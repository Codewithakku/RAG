import os
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    UnstructuredExcelLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentProcessor:
    """
    Handles loading different document types and splitting them
    into chunks.

    Supported formats:
        PDF   -> PyPDFLoader
        TXT   -> TextLoader
        MD    -> UnstructuredMarkdownLoader
        CSV   -> CSVLoader
        XLS   -> UnstructuredExcelLoader
        XLSX  -> UnstructuredExcelLoader
    """

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    # ============================================================
    # PDF Loader
    # ============================================================

    def load_pdf(self, file_path: str) -> List[Document]:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found at: {file_path}"
            )

        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            if documents and any(
                doc.page_content.strip()
                for doc in documents
            ):
                return documents

        except Exception as e:

            print(
                f"PyPDFLoader warning: {str(e)}. "
                "Trying direct pypdf fallback."
            )

        # PDF fallback

        try:

            from pypdf import PdfReader

            reader = PdfReader(file_path)

            documents = []

            for page_num, page in enumerate(reader.pages):

                text = page.extract_text() or ""

                if text.strip():

                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": file_path,
                                "page": page_num
                            }
                        )
                    )

            return documents

        except Exception as fallback_err:

            raise ValueError(
                f"Failed to parse PDF document: "
                f"{str(fallback_err)}"
            )

    # ============================================================
    # TXT Loader
    # ============================================================

    def load_txt(self, file_path: str) -> List[Document]:

        loader = TextLoader(
            file_path,
            encoding="utf-8"
        )

        return loader.load()

    # ============================================================
    # Markdown Loader
    # ============================================================

    def load_md(self, file_path: str) -> List[Document]:

        loader = UnstructuredMarkdownLoader(
            file_path
        )

        return loader.load()

    # ============================================================
    # CSV Loader
    # ============================================================

    def load_csv(self, file_path: str) -> List[Document]:

        loader = CSVLoader(
            file_path=file_path,
            encoding="utf-8"
        )

        return loader.load()

    # ============================================================
    # Excel Loader
    # ============================================================

    def load_excel(self, file_path: str) -> List[Document]:

        loader = UnstructuredExcelLoader(
            file_path,
            mode="elements"
        )

        return loader.load()

    # ============================================================
    # Generic Document Loader
    # ============================================================

    def load_document(self, file_path: str) -> List[Document]:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Document not found at: {file_path}"
            )

        extension = os.path.splitext(file_path)[1].lower()

        # PDF
        if extension == ".pdf":
            return self.load_pdf(file_path)

        # TXT
        elif extension == ".txt":
            return self.load_txt(file_path)

        # Markdown
        elif extension == ".md":
            return self.load_md(file_path)

        # CSV
        elif extension == ".csv":
            return self.load_csv(file_path)

        # Excel
        elif extension in [".xls", ".xlsx"]:
            return self.load_excel(file_path)

        # Unsupported
        else:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                "Supported formats are: "
                ".pdf, .txt, .md, .csv, .xls, .xlsx"
            )

    # ============================================================
    # Process Document
    # ============================================================

    def process_document(
        self,
        file_path: str,
        doc_id: str
    ) -> List[Document]:

        # Load document according to extension
        raw_docs = self.load_document(file_path)

        file_name = os.path.basename(file_path)

        # Empty document
        if not raw_docs:
            return []

        # Chunking
        chunks = self.text_splitter.split_documents(
            raw_docs
        )

        # Add metadata
        for idx, chunk in enumerate(chunks):

            chunk.metadata["doc_id"] = doc_id

            chunk.metadata["source_file"] = file_name

            chunk.metadata["chunk_index"] = idx

            chunk.metadata["file_type"] = (
                os.path.splitext(file_name)[1].lower()
            )

        return chunks