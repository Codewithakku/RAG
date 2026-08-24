import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.document_processor import DocumentProcessor
from app.vector_store import VectorStoreManager

def run_test():
    sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_rag_guide.pdf")
    if not os.path.exists(sample_path):
        print(f"Sample PDF not found at {sample_path}")
        return

    print("=== 1. Testing Document Processor on PDF ===")
    dp = DocumentProcessor()
    chunks = dp.process_pdf(file_path=sample_path, doc_id="test-doc-id-1")
    print(f"Successfully processed PDF into {len(chunks)} chunks.")
    if chunks:
        print(f"Chunk 0 content snippet:\n{chunks[0].page_content[:150]}...")
        print(f"Chunk 0 metadata: {chunks[0].metadata}")

    print("\n=== 2. Testing ChromaDB Vector Store Insertion ===")
    vstore = VectorStoreManager(persist_directory="./test_chroma_db", collection_name="test_uploads")
    vstore.add_documents(chunks)
    
    docs_list = vstore.list_documents()
    print(f"ChromaDB Indexed Documents: {docs_list}")

    results = vstore.similarity_search(query="What is the chunk size?", k=3)
    print(f"\n=== 3. Similarity Search Retrieved {len(results)} chunks ===")
    for i, res in enumerate(results):
        print(f"Result {i+1}: Page {res.metadata.get('page', 0)+1} -> '{res.page_content[:100]}...'")

    # Clean up test collection
    vstore.delete_document("test-doc-id-1")
    print("\n=== Test Completed Successfully! ===")

if __name__ == "__main__":
    run_test()
