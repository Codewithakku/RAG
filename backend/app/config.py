import os
from dotenv import load_dotenv

# Load .env file if available
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ChromaDB storage directory
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", os.path.join(BASE_DIR, "chroma_db"))

# Upload storage directory
UPLOADS_DIR = os.getenv("UPLOADS_DIR", os.path.join(BASE_DIR, "uploads"))

# Document Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Retrieval Top K
TOP_K = int(os.getenv("TOP_K", 3))

# Google Gemini Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Ensure required directories exist
os.makedirs(CHROMA_DB_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
