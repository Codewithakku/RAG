from typing import List, Dict, Any, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import CHROMA_DB_DIR, TOP_K
from app.embeddings import get_embedding_model


class VectorStoreManager:
    """
    Manages ChromaDB local vector database for:
    - Adding documents
    - Updating documents
    - Deleting documents
    - Listing documents
    - Similarity search
    - Metadata-filtered similarity search
    """

    def __init__(
        self,
        persist_directory: str = CHROMA_DB_DIR,
        collection_name: str = "rag_documents"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_function = None
        self.vector_store = None

    def _ensure_vector_store(self) -> None:
        """
        Lazily initialize embeddings and Chroma collection.
        """

        if self.vector_store is not None:
            return

        self.embedding_function = get_embedding_model()

        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
        )

    def add_documents(
        self,
        documents: List[Document]
    ) -> List[str]:
        """Adds document chunks to ChromaDB store."""

        if not documents:
            return []

        self._ensure_vector_store()

        ids = [
            f"{doc.metadata.get('doc_id')}_{i}"
            for i, doc in enumerate(documents)
        ]

        return self.vector_store.add_documents(
            documents=documents,
            ids=ids
        )

    def delete_document(
        self,
        doc_id: str
    ) -> bool:
        """Deletes all chunks associated with a doc_id."""

        try:

            self._ensure_vector_store()

            collection = self.vector_store._collection

            results = collection.get(
                where={"doc_id": doc_id}
            )

            if results and results.get("ids"):

                ids_to_delete = results["ids"]

                collection.delete(
                    ids=ids_to_delete
                )

                return True

            return False

        except Exception as e:

            print(
                f"Error deleting document {doc_id}: {str(e)}"
            )

            return False

    def update_document(
        self,
        doc_id: str,
        new_documents: List[Document]
    ) -> bool:
        """Replaces existing document chunks."""

        self.delete_document(doc_id)

        self.add_documents(new_documents)

        return True

    def list_documents(
        self
    ) -> List[Dict[str, Any]]:
        """Lists all distinct documents with chunk counts."""

        try:

            self._ensure_vector_store()

            collection = self.vector_store._collection

            results = collection.get(
                include=["metadatas"]
            )

            doc_map: Dict[str, Dict[str, Any]] = {}

            if results and results.get("metadatas"):

                for meta in results["metadatas"]:

                    if meta and "doc_id" in meta:

                        d_id = meta["doc_id"]

                        s_file = meta.get(
                            "source_file",
                            "Unknown"
                        )

                        if d_id not in doc_map:

                            doc_map[d_id] = {
                                "doc_id": d_id,
                                "source_file": s_file,
                                "chunk_count": 0
                            }

                        doc_map[d_id]["chunk_count"] += 1

            return list(doc_map.values())

        except Exception as e:

            print(
                f"Error listing documents: {str(e)}"
            )

            return []

    def similarity_search(
        self,
        query: str,
        k: int = TOP_K,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Performs similarity search with an optional
        metadata filter.

        If metadata_filter is None:
            Search all chunks.

        Example:
            metadata_filter={
                "doc_id": "123"
            }

        This searches only chunks belonging to
        document ID 123.
        """

        self._ensure_vector_store()

        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=metadata_filter
        )