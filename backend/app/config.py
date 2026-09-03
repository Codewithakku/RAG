import os
from dotenv import load_dotenv


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# Base Directory
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# ChromaDB Configuration
# ============================================================

CHROMA_DB_DIR = os.getenv(
    "CHROMA_DB_DIR",
    os.path.join(BASE_DIR, "chroma_db")
)


# ============================================================
# Upload Directory
# ============================================================

UPLOADS_DIR = os.getenv(
    "UPLOADS_DIR",
    os.path.join(BASE_DIR, "uploads")
)


# ============================================================
# Document Chunking Configuration
# ============================================================

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", 500)
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", 50)
)


# ============================================================
# Embedding Model Configuration
# ============================================================

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)


# ============================================================
# Retrieval Configuration
# ============================================================

TOP_K = int(
    os.getenv("TOP_K", 3)
)


# ============================================================
# Indexing Strategy Configuration
# ============================================================

# If total chunks are below this value,
# HNSW will be selected.

HNSW_MAX_CHUNKS = int(
    os.getenv("HNSW_MAX_CHUNKS", 5000)
)


# Index strategy names

HNSW_INDEX = "HNSW"
IVF_INDEX = "IVF"


# ============================================================
# Google Gemini Configuration
# ============================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-1.5-flash"
)


# ============================================================
# Create Required Directories
# ============================================================

os.makedirs(
    CHROMA_DB_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOADS_DIR,
    exist_ok=True
)