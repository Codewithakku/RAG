# load , text extract , nd chunking
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    """Handles loading PDF documents and splitting them into chunks using PyPDFLoader and RecursiveCharacterTextSplitter."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """Loads pages from a PDF file using PyPDFLoader with fallback to pypdf PdfReader."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported.")

        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            if documents and any(doc.page_content.strip() for doc in documents):
                return documents
        except Exception as e:
            print(f"PyPDFLoader warning: {str(e)}. Attempting direct pypdf fallback extraction.")

        # Fallback to direct pypdf PdfReader extraction
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            documents = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": file_path, "page": page_num}
                    ))
            return documents
        except Exception as fallback_err:
            raise ValueError(f"Failed to parse PDF document: {str(fallback_err)}")

    def process_pdf(self, file_path: str, doc_id: str) -> List[Document]:
        """Loads a PDF file and splits it into chunks, adding metadata like doc_id and filename."""
        raw_docs = self.load_pdf(file_path)
        file_name = os.path.basename(file_path)
        
        if not raw_docs:
            return []

        chunks = self.text_splitter.split_documents(raw_docs)
        
        # Enrich metadata for each chunk
        for idx, chunk in enumerate(chunks):
            chunk.metadata["doc_id"] = doc_id
            chunk.metadata["source_file"] = file_name
            chunk.metadata["chunk_index"] = idx
            
        return chunks
