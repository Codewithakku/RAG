from langchain_huggingface import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL_NAME

def get_embedding_model(model_name: str = EMBEDDING_MODEL_NAME) -> HuggingFaceEmbeddings:
    """Initializes and returns the HuggingFaceEmbeddings instance for all-MiniLM-L6-v2."""
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings
