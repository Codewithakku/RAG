import os
from typing import List, Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from app.config import GEMINI_MODEL, TOP_K
from app.vector_store import VectorStoreManager

# Simple RAG Prompt Template
RAG_PROMPT_TEMPLATE = """You are a helpful, precise AI assistant answering user questions based ONLY on the provided context retrieved from PDF documents.

Context:
{context}

Question:
{question}

Instructions:
- Answer the question thoroughly and accurately using ONLY the information provided in the Context above.
- If the answer cannot be found in the provided context, state clearly: "I cannot find the answer in the provided documents context."
- Do not make up facts or rely on external knowledge outside the provided context.

Answer:"""

class RAGChainManager:
    """Manages Gemini LLM initialization and RAG question-answering pipeline."""

    def __init__(self, vector_store_manager: VectorStoreManager, model_name: str = GEMINI_MODEL, api_key: str = None):
        self.vector_store_manager = vector_store_manager
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        self.output_parser = StrOutputParser()

    def _get_llm(self, custom_api_key: str = None, custom_model: str = None) -> ChatGoogleGenerativeAI:
        key = custom_api_key or self.api_key
        model = custom_model or self.model_name

        # Map deprecated/legacy model names to a stable default.
        if model in ["gemini-pro", "models/gemini-pro", "gemini-2.0-flash", "models/gemini-2.0-flash", "gemini-3.6-flash", "models/gemini-3.6-flash"]:
            model = "gemini-1.5-flash"
        
        if not key:
            raise ValueError("Google Gemini API Key is missing. Please click Settings to enter your API key or set GOOGLE_API_KEY env variable.")
        
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=key,
            temperature=0.2,
            max_output_tokens=1024
        )

    def generate_answer(self, question: str, k: int = TOP_K, custom_api_key: str = None, custom_model: str = None) -> Dict[str, Any]:
        """Retrieves top-k context chunks from ChromaDB, constructs prompt, invokes Gemini, and returns response with source citations."""
        # 1. Retrieve relevant chunks
        docs: List[Document] = self.vector_store_manager.similarity_search(query=question, k=k)
        
        if not docs:
            return {
                "answer": "No relevant documents found in the database. Please upload a PDF first.",
                "sources": [],
                "context_used": ""
            }

        # 2. Format context string
        context_snippets = []
        sources = []
        for i, doc in enumerate(docs):
            source_file = doc.metadata.get("source_file", "Unknown PDF")
            page_num = doc.metadata.get("page", 0) + 1
            doc_id = doc.metadata.get("doc_id", "")
            
            snippet = f"[Source: {source_file}, Page {page_num}]\n{doc.page_content.strip()}"
            context_snippets.append(snippet)
            
            sources.append({
                "source_file": source_file,
                "page": page_num,
                "doc_id": doc_id,
                "content": doc.page_content.strip()
            })

        formatted_context = "\n\n---\n\n".join(context_snippets)

        # 3. Build & execute chain
        llm = self._get_llm(custom_api_key=custom_api_key, custom_model=custom_model)
        chain = self.prompt | llm | self.output_parser
        
        try:
            response_text = chain.invoke({
                "context": formatted_context,
                "question": question
            })
        except Exception as e:
            response_text = f"Error communicating with Gemini LLM: {str(e)}"

        return {
            "answer": response_text,
            "sources": sources,
            "context_used": formatted_context
        }
