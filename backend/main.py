import os
import uuid
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import UPLOADS_DIR, GEMINI_MODEL, TOP_K
from app.document_processor import DocumentProcessor
from app.vector_store import VectorStoreManager
from app.rag_chain import RAGChainManager

app = FastAPI(
    title="RAG PDF Application API",
    description="LangChain + ChromaDB + HuggingFace + Gemini RAG Backend API",
    version="1.0.0"
)

# Enable CORS for React Frontend (vite default http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
doc_processor = DocumentProcessor()
vector_store = VectorStoreManager()
rag_chain = RAGChainManager(vector_store_manager=vector_store)

# Request Models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = TOP_K
    api_key: Optional[str] = None
    gemini_model: Optional[str] = GEMINI_MODEL

@app.get("/api/health")
def health_check():
    """Health check endpoint and API key status."""
    has_api_key = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    return {
        "status": "online",
        "gemini_api_key_configured": has_api_key,
        "default_gemini_model": GEMINI_MODEL,
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_store": "ChromaDB (Local)"
    }

@app.get("/api/documents")
def list_documents():
    """Returns list of indexed PDF documents in ChromaDB vector store."""
    docs = vector_store.list_documents()
    return {"documents": docs}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF document, extracts text using PyPDFLoader, chunks with RecursiveCharacterTextSplitter (500/50), embeds and stores in ChromaDB."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)

    # Save file to uploads directory safely using await file.read()
    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise ValueError("Uploaded file content is empty.")

        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded PDF: {str(e)}")

    # Process and chunk PDF
    try:
        chunks = doc_processor.process_pdf(file_path=file_path, doc_id=doc_id)
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract text from this PDF file.")

        # Store in ChromaDB
        vector_store.add_documents(chunks)

        return {
            "message": "Document uploaded and indexed successfully.",
            "doc_id": doc_id,
            "filename": file.filename,
            "total_chunks": len(chunks),
            "chunk_size": doc_processor.chunk_size,
            "chunk_overlap": doc_processor.chunk_overlap
        }
    except Exception as e:
        # Clean up file on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Error processing PDF upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF Error: {str(e)}")

# put : update document
@app.put("/api/documents/{doc_id}")
async def update_document(doc_id: str, file: UploadFile = File(...)):
    """Updates an existing document by re-processing new PDF and replacing chunks in ChromaDB."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    safe_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)

    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise ValueError("Uploaded file content is empty.")

        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        chunks = doc_processor.process_pdf(file_path=file_path, doc_id=doc_id)
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract text from updated PDF file.")

        success = vector_store.update_document(doc_id=doc_id, new_documents=chunks)

        return {
            "message": "Document updated and re-indexed successfully.",
            "doc_id": doc_id,
            "filename": file.filename,
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    """Deletes document chunks from ChromaDB vector database."""
    success = vector_store.delete_document(doc_id=doc_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found or already deleted.")
    return {"message": f"Document {doc_id} deleted successfully.", "doc_id": doc_id}

@app.post("/api/query")
def query_rag(request: QueryRequest):
    """Retrieves top K (default 3) relevant chunks from ChromaDB and answers using Google Gemini LLM."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question string cannot be empty.")

    try:
        result = rag_chain.generate_answer(
            question=request.question,
            k=request.top_k or TOP_K,
            custom_api_key=request.api_key,
            custom_model=request.gemini_model
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RAG query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
