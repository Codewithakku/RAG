import os
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import CHROMA_DB_DIR, TOP_K
from app.embeddings import get_embedding_model

class VectorStoreManager:
    """Manages ChromaDB local vector database for adding, updating, deleting, listing, and retrieving documents."""

    def __init__(self, persist_directory: str = CHROMA_DB_DIR, collection_name: str = "rag_documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_function = get_embedding_model()
        
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Adds document chunks to ChromaDB store."""
        if not documents:
            return []
        ids = [f"{doc.metadata.get('doc_id')}_{i}" for i, doc in enumerate(documents)]
        return self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_document(self, doc_id: str) -> bool:
        """Deletes all chunks associated with a doc_id from ChromaDB."""
        try:
            # Query collection directly to get chunk IDs matching doc_id
            collection = self.vector_store._collection
            results = collection.get(where={"doc_id": doc_id})
            
            if results and results.get("ids"):
                ids_to_delete = results["ids"]
                collection.delete(ids=ids_to_delete)
                return True
            return False
        except Exception as e:
            print(f"Error deleting document {doc_id}: {str(e)}")
            return False

    def update_document(self, doc_id: str, new_documents: List[Document]) -> bool:
        """Updates a document by removing its existing chunks and adding the new chunks."""
        # 1. Delete old chunks if exist
        self.delete_document(doc_id)
        # 2. Add new chunks
        self.add_documents(new_documents)
        return True

    def list_documents(self) -> List[Dict[str, Any]]:
        """Lists all distinct documents stored in ChromaDB along with chunk counts."""
        try:
            collection = self.vector_store._collection
            results = collection.get(include=["metadatas"])
            
            doc_map: Dict[str, Dict[str, Any]] = {}
            if results and results.get("metadatas"):
                for meta in results["metadatas"]:
                    if meta and "doc_id" in meta:
                        d_id = meta["doc_id"]
                        s_file = meta.get("source_file", "Unknown")
                        if d_id not in doc_map:
                            doc_map[d_id] = {
                                "doc_id": d_id,
                                "source_file": s_file,
                                "chunk_count": 0
                            }
                        doc_map[d_id]["chunk_count"] += 1
                        
            return list(doc_map.values())
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []

    def similarity_search(self, query: str, k: int = TOP_K) -> List[Document]:
        """Performs similarity search against ChromaDB and returns top k relevant chunks."""
        return self.vector_store.similarity_search(query=query, k=k)
