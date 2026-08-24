import os
import sys

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.document_processor import DocumentProcessor
from app.embeddings import get_embedding_model
from app.vector_store import VectorStoreManager
from app.rag_chain import RAGChainManager, RAG_PROMPT_TEMPLATE
from langchain_core.documents import Document

def test_pipeline():
    print("=== 1. Testing Document Processor (Chunk size 500, overlap 50) ===")
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    print(f"Chunk size: {processor.chunk_size}, Chunk overlap: {processor.chunk_overlap}")

    sample_doc = Document(
        page_content="LangChain is a framework for developing applications powered by large language models (LLMs). Retrieval-Augmented Generation (RAG) is a technique for enhancing LLM responses with external data sources like PDF files. ChromaDB stores high-dimensional embeddings for fast vector similarity search.",
        metadata={"source_file": "test_sample.pdf", "page": 0}
    )
    chunks = processor.text_splitter.split_documents([sample_doc])
    for idx, c in enumerate(chunks):
        c.metadata["doc_id"] = "test-doc-123"
        c.metadata["source_file"] = "test_sample.pdf"
        c.metadata["chunk_index"] = idx

    print(f"Total chunks created: {len(chunks)}")
    print(f"Sample Chunk 0 len: {len(chunks[0].page_content)}")
    assert len(chunks[0].page_content) <= 500, "Chunk size exceeds 500 limit!"

    print("\n=== 2. Testing Hugging Face Embeddings (all-MiniLM-L6-v2) ===")
    embeddings = get_embedding_model()
    test_vec = embeddings.embed_query("Testing similarity search embedding model.")
    print(f"Embedding dimension: {len(test_vec)}")
    assert len(test_vec) == 384, f"Expected 384 dimensions for all-MiniLM-L6-v2, got {len(test_vec)}"

    print("\n=== 3. Testing ChromaDB Vector Store Operations ===")
    vstore = VectorStoreManager(persist_directory="./test_chroma_db", collection_name="test_collection")
    
    # Add documents
    added_ids = vstore.add_documents(chunks)
    print(f"Added {len(added_ids)} chunk embeddings to ChromaDB.")

    # Similarity Search (Top K = 3)
    results = vstore.similarity_search("What is RAG?", k=3)
    print(f"Similarity search retrieved {len(results)} chunks.")
    assert len(results) > 0, "No chunks retrieved!"
    print(f"Top 1 match content snippet: '{results[0].page_content[:100]}...'")

    # List documents
    doc_list = vstore.list_documents()
    print(f"Indexed documents in ChromaDB: {doc_list}")

    # Delete document
    deleted = vstore.delete_document("test-doc-123")
    print(f"Document deletion status: {deleted}")

    doc_list_after = vstore.list_documents()
    print(f"Indexed documents after deletion: {doc_list_after}")
    assert len(doc_list_after) == 0, "Document chunks were not properly deleted from ChromaDB!"

    print("\n=== 4. Testing RAG Prompt Template ===")
    print("Prompt Template:")
    print(RAG_PROMPT_TEMPLATE)

    print("\n✅ All core RAG pipeline unit tests passed successfully!")

if __name__ == "__main__":
    test_pipeline()
