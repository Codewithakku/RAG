import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from sentence_transformers import CrossEncoder

from app.config import GEMINI_MODEL
from app.vector_store import VectorStoreManager


# ============================================================
# Re-ranking Configuration
# ============================================================

INITIAL_RETRIEVAL_K = 10

RERANK_K = 3

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


# ============================================================
# Allowed Gemini Models
# ============================================================

ALLOWED_GEMINI_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]


# ============================================================
# Professional Hybrid RAG Prompt Template
# ============================================================

RAG_PROMPT_TEMPLATE = """
You are a helpful AI assistant. Answer clearly, accurately, and concisely.

Source rules:
- PDF question → use {context} only; never guess. If unavailable, reply exactly: "I cannot find the answer in the provided documents context."
- General question → use general knowledge.
- Date/time → use {current_date}, {current_time}.
- Weather → use {weather_context}.
- Greeting → respond naturally.

Date: {current_date}
Time: {current_time}

Weather:
{weather_context}

PDF Context:
{context}

Question:
{question}
"""


class RAGChainManager:
    """
    Manages the complete RAG question-answering pipeline.

    Pipeline:

        Question
            ↓
        Metadata Filter (optional)
            ↓
        ChromaDB Similarity Search
            ↓
        Retrieve 10 candidate chunks
            ↓
        Cross-Encoder Re-ranking
            ↓
        Select best 3 chunks
            ↓
        Gemini LLM
            ↓
        Final Answer
    """

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model_name: str = GEMINI_MODEL,
        api_key: str = None
    ):

        self.vector_store_manager = vector_store_manager

        self.model_name = model_name

        self.api_key = (
            api_key
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        self.prompt = ChatPromptTemplate.from_template(
            RAG_PROMPT_TEMPLATE
        )

        self.output_parser = StrOutputParser()

        self.reranker = CrossEncoder(
            RERANKER_MODEL
        )

    # ========================================================
    # Create Gemini LLM
    # ========================================================

    def _get_llm(
        self,
        custom_api_key: str = None,
        custom_model: str = None
    ) -> ChatGoogleGenerativeAI:

        key = custom_api_key or self.api_key

        model = custom_model or self.model_name

        if not key:

            raise ValueError(
                "Google Gemini API Key is missing. "
                "Please enter your API key in Settings "
                "or set GOOGLE_API_KEY environment variable."
            )

        if model not in ALLOWED_GEMINI_MODELS:

            raise ValueError(
                f"Unsupported Gemini model: '{model}'. "
                f"Allowed models are: "
                f"{', '.join(ALLOWED_GEMINI_MODELS)}"
            )

        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=key,
            max_output_tokens=1024
        )

    # ========================================================
    # Re-rank Documents
    # ========================================================

    def _rerank_documents(
        self,
        question: str,
        documents: List[Document],
        top_k: int = RERANK_K
    ) -> List[Dict[str, Any]]:

        if not documents:
            return []

        top_k = min(
            top_k,
            len(documents)
        )

        pairs = [
            [question, document.page_content]
            for document in documents
        ]

        scores = self.reranker.predict(
            pairs
        )

        scored_documents = [
            {
                "document": document,
                "score": float(score)
            }
            for document, score in zip(
                documents,
                scores
            )
        ]

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored_documents[:top_k]

    # ========================================================
    # Generate Answer
    # ========================================================

    def generate_answer(
        self,
        question: str,
        k: int = RERANK_K,
        custom_api_key: str = None,
        custom_model: str = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        # ====================================================
        # 1. Initial Retrieval
        # ====================================================

        retrieved_docs: List[Document] = (
            self.vector_store_manager.similarity_search(
                query=question,
                k=INITIAL_RETRIEVAL_K,
                metadata_filter=metadata_filter
            )
        )

        # ====================================================
        # 2. Re-ranking
        # ====================================================

        reranked_results = self._rerank_documents(
            question=question,
            documents=retrieved_docs,
            top_k=k
        )

        # ====================================================
        # 3. Extract Final Documents
        # ====================================================

        docs = [
            result["document"]
            for result in reranked_results
        ]

        # ====================================================
        # 4. Format PDF Context
        # ====================================================

        context_snippets = []

        sources = []

        for result in reranked_results:

            doc = result["document"]

            rerank_score = result["score"]

            source_file = doc.metadata.get(
                "source_file",
                "Unknown PDF"
            )

            page_num = doc.metadata.get(
                "page",
                0
            ) + 1

            doc_id = doc.metadata.get(
                "doc_id",
                ""
            )

            content = doc.page_content.strip()

            snippet = (
                f"[Source: {source_file}, Page {page_num}]\n"
                f"{content}"
            )

            context_snippets.append(
                snippet
            )

            sources.append({
                "source_file": source_file,
                "page": page_num,
                "doc_id": doc_id,
                "content": content,
                "rerank_score": rerank_score
            })

        # ====================================================
        # 5. Create Formatted Context
        # ====================================================

        if context_snippets:

            formatted_context = "\n\n---\n\n".join(
                context_snippets
            )

        else:

            formatted_context = (
                "No relevant PDF context was retrieved."
            )

        # ====================================================
        # 6. Current Date and Time
        # ====================================================

        now = datetime.now()

        current_date = now.strftime(
            "%B %d, %Y"
        )

        current_time = now.strftime(
            "%I:%M %p"
        )

        # ====================================================
        # 7. Weather
        # ====================================================

        weather_context = (
            "No live weather information is currently available."
        )

        # ====================================================
        # 8. Gemini
        # ====================================================

        try:

            llm = self._get_llm(
                custom_api_key=custom_api_key,
                custom_model=custom_model
            )

            chain = (
                self.prompt
                | llm
                | self.output_parser
            )

            response_text = chain.invoke({
                "context": formatted_context,
                "question": question,
                "current_date": current_date,
                "current_time": current_time,
                "weather_context": weather_context
            })

        except Exception as e:

            response_text = (
                f"Error communicating with Gemini LLM: {str(e)}"
            )

        # ====================================================
        # 9. Return Final Response
        # ====================================================

        return {
            "answer": response_text,
            "sources": sources,
            "context_used": formatted_context
        }