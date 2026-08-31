import os
import uuid
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import UPLOADS_DIR, GEMINI_MODEL, TOP_K
from app.document_processor import DocumentProcessor
from app.vector_store import VectorStoreManager
from app.rag_chain import RAGChainManager


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="RAG Multi-Format Document Application API",
    description="LangChain + ChromaDB + HuggingFace + Gemini RAG Backend API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Initialize Core Services
# ============================================================

doc_processor = DocumentProcessor()

vector_store = VectorStoreManager()

rag_chain = RAGChainManager(
    vector_store_manager=vector_store
)


# ============================================================
# Supported File Extensions
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".csv",
    ".xls",
    ".xlsx"
}


# ============================================================
# Helper Functions
# ============================================================

def get_file_extension(filename: str) -> str:
    """
    Returns the lowercase file extension.
    """

    return os.path.splitext(filename)[1].lower()


def validate_file_extension(filename: str) -> str:
    """
    Validates whether the uploaded file type is supported.
    """

    extension = get_file_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                "Supported formats: "
                ".pdf, .txt, .md, .csv, .xls, .xlsx"
            )
        )

    return extension


# ============================================================
# Request Models
# ============================================================

class QueryRequest(BaseModel):

    question: str

    top_k: Optional[int] = TOP_K

    api_key: Optional[str] = None

    gemini_model: Optional[str] = GEMINI_MODEL

    # --------------------------------------------------------
    # Optional metadata filter
    # --------------------------------------------------------

    metadata_filter: Optional[Dict[str, Any]] = None


# ============================================================
# Health Check
# ============================================================

@app.get("/api/health")
def health_check():

    has_api_key = bool(
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )

    return {
        "status": "online",

        "gemini_api_key_configured": has_api_key,

        "default_gemini_model": GEMINI_MODEL,

        "embedding_model": "all-MiniLM-L6-v2",

        "vector_store": "ChromaDB (Local)",

        "supported_file_types": sorted(
            ALLOWED_EXTENSIONS
        )
    }


# ============================================================
# List Documents
# ============================================================

@app.get("/api/documents")
def list_documents():

    docs = vector_store.list_documents()

    return {
        "documents": docs
    }


# ============================================================
# Upload Document
# ============================================================

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = validate_file_extension(
        file.filename
    )

    # --------------------------------------------------------
    # Generate document ID
    # --------------------------------------------------------

    doc_id = str(uuid.uuid4())

    # --------------------------------------------------------
    # Create safe filename
    # --------------------------------------------------------

    safe_filename = (
        f"{doc_id}_{file.filename}"
    )

    file_path = os.path.join(
        UPLOADS_DIR,
        safe_filename
    )

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    try:

        contents = await file.read()

        if not contents:

            raise ValueError(
                "Uploaded file content is empty."
            )

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(contents)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save uploaded "
                f"document: {str(e)}"
            )
        )

    # --------------------------------------------------------
    # Process document
    # --------------------------------------------------------

    try:

        chunks = doc_processor.process_document(
            file_path=file_path,
            doc_id=doc_id
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text "
                    "from this document."
                )
            )

        # ----------------------------------------------------
        # Store in ChromaDB
        # ----------------------------------------------------

        vector_store.add_documents(
            chunks
        )

        return {

            "message": (
                "Document uploaded and "
                "indexed successfully."
            ),

            "doc_id": doc_id,

            "filename": file.filename,

            "file_type": extension,

            "total_chunks": len(chunks),

            "chunk_size": (
                doc_processor.chunk_size
            ),

            "chunk_overlap": (
                doc_processor.chunk_overlap
            )
        }

    except HTTPException:

        if os.path.exists(file_path):

            os.remove(file_path)

        raise

    except Exception as e:

        if os.path.exists(file_path):

            os.remove(file_path)

        print(
            f"Error processing document upload: "
            f"{str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document processing error: "
                f"{str(e)}"
            )
        )


# ============================================================
# Update Document
# ============================================================

@app.put("/api/documents/{doc_id}")
async def update_document(
    doc_id: str,
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = validate_file_extension(
        file.filename
    )

    # --------------------------------------------------------
    # Create file path
    # --------------------------------------------------------

    safe_filename = (
        f"{doc_id}_{file.filename}"
    )

    file_path = os.path.join(
        UPLOADS_DIR,
        safe_filename
    )

    # --------------------------------------------------------
    # Save new file
    # --------------------------------------------------------

    try:

        contents = await file.read()

        if not contents:

            raise ValueError(
                "Uploaded file content is empty."
            )

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(contents)

        # ----------------------------------------------------
        # Process new document
        # ----------------------------------------------------

        chunks = doc_processor.process_document(
            file_path=file_path,
            doc_id=doc_id
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text "
                    "from updated document."
                )
            )

        # ----------------------------------------------------
        # Replace old chunks
        # ----------------------------------------------------

        vector_store.update_document(
            doc_id=doc_id,
            new_documents=chunks
        )

        return {

            "message": (
                "Document updated and "
                "re-indexed successfully."
            ),

            "doc_id": doc_id,

            "filename": file.filename,

            "file_type": extension,

            "total_chunks": len(chunks)
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"Error updating document: "
            f"{str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Error updating document: "
                f"{str(e)}"
            )
        )


# ============================================================
# Delete Document
# ============================================================

@app.delete("/api/documents/{doc_id}")
def delete_document(
    doc_id: str
):

    success = vector_store.delete_document(
        doc_id=doc_id
    )

    if not success:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document with ID {doc_id} "
                "not found or already deleted."
            )
        )

    return {

        "message": (
            f"Document {doc_id} "
            "deleted successfully."
        ),

        "doc_id": doc_id
    }


# ============================================================
# RAG Query
# ============================================================

@app.post("/api/query")
def query_rag(
    request: QueryRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question string cannot be empty."
        )

    try:

        result = rag_chain.generate_answer(

            question=request.question,

            k=request.top_k or TOP_K,

            custom_api_key=request.api_key,

            custom_model=request.gemini_model,

            # ------------------------------------------------
            # Pass metadata filter to RAG pipeline
            # ------------------------------------------------

            metadata_filter=request.metadata_filter
        )

        return result

    except ValueError as ve:

        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Error processing "
                f"RAG query: {str(e)}"
            )
        )


# ============================================================
# Run Server
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )