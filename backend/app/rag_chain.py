import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from app.config import GEMINI_MODEL
from app.vector_store import VectorStoreManager


# ============================================================
# Top-K Retrieval Configuration
# ============================================================

TOP_K = 3


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
- Document question → use {context} only; never guess. If unavailable, reply exactly: "I cannot find the answer in the provided documents context."
- General question → use general knowledge.
- Date/time → use {current_date}, {current_time}.
- Weather → use {weather_context}.
- Greeting → respond naturally.

Date: {current_date}
Time: {current_time}

Weather:
{weather_context}

Document Context:
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
        Metadata Filter (optional, incl. file_type)
            ↓
        ChromaDB Similarity Search
            ↓
        Top-K Documents
            ↓
        Gemini LLM
            ↓
        Final Answer (+ index strategy + performance timings)
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
    # Generate Answer
    # ========================================================

    def generate_answer(
        self,
        question: str,
        k: int = TOP_K,
        custom_api_key: str = None,
        custom_model: str = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:

        timings = {}

        total_start = time.perf_counter()

        # ====================================================
        # 0. Merge file_type into metadata filter
        # ====================================================

        combined_filter = (
            dict(metadata_filter)
            if metadata_filter
            else {}
        )

        if file_type:
            combined_filter["file_type"] = file_type

        combined_filter = combined_filter or None

        # ====================================================
        # 0.5 Capture index strategy for this query
        # ====================================================

        strategy_start = time.perf_counter()

        strategy_info = (
            self.vector_store_manager
            .get_index_strategy()
        )

        timings["index_strategy_check_sec"] = round(
            time.perf_counter() - strategy_start,
            4
        )

        # ====================================================
        # 1. Top-K Similarity Retrieval
        # ====================================================

        retrieval_start = time.perf_counter()

        retrieved_docs: List[Document] = (
            self.vector_store_manager.similarity_search(
                query=question,
                k=k,
                metadata_filter=combined_filter
            )
        )

        timings["retrieval_sec"] = round(
            time.perf_counter() - retrieval_start,
            4
        )

        # ====================================================
        # 2. Use Retrieved Top-K Documents Directly
        # ====================================================

        docs = retrieved_docs

        # ====================================================
        # 3. Format Context
        # ====================================================

        context_snippets = []

        sources = []

        for doc in docs:

            source_file = doc.metadata.get(
                "source_file",
                "Unknown source"
            )

            doc_file_type = doc.metadata.get(
                "file_type",
                ""
            )

            doc_id = doc.metadata.get(
                "doc_id",
                ""
            )

            content = doc.page_content.strip()

            if "page" in doc.metadata:

                location_tag = (
                    f"Page {doc.metadata['page'] + 1}"
                )

            else:

                location_tag = (
                    f"Chunk "
                    f"{doc.metadata.get('chunk_index', '?')}"
                )

            snippet = (
                f"[Source: {source_file} "
                f"({doc_file_type}), "
                f"{location_tag}]\n"
                f"{content}"
            )

            context_snippets.append(
                snippet
            )

            sources.append({
                "source_file": source_file,
                "file_type": doc_file_type,
                "location": location_tag,
                "doc_id": doc_id,
                "content": content
            })

        # ====================================================
        # 4. Create Formatted Context
        # ====================================================

        if context_snippets:

            formatted_context = (
                "\n\n---\n\n".join(
                    context_snippets
                )
            )

        else:

            formatted_context = (
                "No relevant document context was retrieved."
            )

        # ====================================================
        # 5. Current Date and Time
        # ====================================================

        now = datetime.now()

        current_date = now.strftime(
            "%B %d, %Y"
        )

        current_time = now.strftime(
            "%I:%M %p"
        )

        # ====================================================
        # 6. Weather
        # ====================================================

        weather_context = (
            "No live weather information is currently available."
        )

        # ====================================================
        # 7. Gemini
        # ====================================================

        gemini_start = time.perf_counter()

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
                f"Error communicating with Gemini LLM: "
                f"{str(e)}"
            )

        timings["gemini_sec"] = round(
            time.perf_counter() - gemini_start,
            4
        )

        # ====================================================
        # 8. Total Time
        # ====================================================

        timings["total_sec"] = round(
            time.perf_counter() - total_start,
            4
        )

        # ====================================================
        # 9. Return Final Response
        # ====================================================

        return {
            "answer": response_text,
            "sources": sources,
            "context_used": formatted_context,
            "index_strategy": strategy_info,
            "performance": timings
        }