from typing import List, Dict, Any, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import (
    CHROMA_DB_DIR,
    TOP_K,
    HNSW_MAX_CHUNKS,
    HNSW_INDEX,
    IVF_INDEX,
)

from app.embeddings import get_embedding_model


class VectorStoreManager:
    """
    Manages ChromaDB local vector database.

    Responsibilities:
    - Add documents
    - Update documents
    - Delete documents
    - List documents
    - Metadata filtering
    - Similarity search
    - Rule-based index strategy selection

    Index strategy rule:

        chunks < HNSW_MAX_CHUNKS
                    ↓
                  HNSW

        chunks >= HNSW_MAX_CHUNKS
                    ↓
                   IVF

    Important:
    ChromaDB currently uses HNSW internally.
    Therefore IVF is currently selected as a strategy
    decision only and is not executed by ChromaDB.
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

    # ========================================================
    # Initialize Vector Store
    # ========================================================

    def _ensure_vector_store(self) -> None:
        """
        Lazily initializes embedding model and ChromaDB.
        """

        if self.vector_store is not None:
            return

        self.embedding_function = get_embedding_model()

        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
        )

    # ========================================================
    # Get Total Chunk Count
    # ========================================================

    def get_total_chunks(self) -> int:
        """
        Returns the total number of chunks
        currently stored in ChromaDB.
        """

        self._ensure_vector_store()

        collection = self.vector_store._collection

        return collection.count()

    # ========================================================
    # Select Index Strategy
    # ========================================================

    def get_index_strategy(self) -> Dict[str, Any]:
        """
        Selects indexing strategy based on total
        number of chunks.

        Rule:

            < HNSW_MAX_CHUNKS chunks  → HNSW
            >= HNSW_MAX_CHUNKS chunks → IVF

        (Threshold value comes from HNSW_MAX_CHUNKS in config.py,
        currently set to 1000. Configurable via .env)
        """

        total_chunks = self.get_total_chunks()

        if total_chunks < HNSW_MAX_CHUNKS:

            strategy = HNSW_INDEX

            reason = (
                f"Dataset contains {total_chunks} chunks, "
                f"which is below the HNSW threshold "
                f"of {HNSW_MAX_CHUNKS}."
            )

        else:

            strategy = IVF_INDEX

            reason = (
                f"Dataset contains {total_chunks} chunks, "
                f"which reached/exceeded the HNSW threshold "
                f"of {HNSW_MAX_CHUNKS}."
            )

        return {
            "index_strategy": strategy,
            "total_chunks": total_chunks,
            "threshold": HNSW_MAX_CHUNKS,
            "reason": reason,
        }

    # ========================================================
    # Add Documents
    # ========================================================

    def add_documents(
        self,
        documents: List[Document]
    ) -> List[str]:
        """
        Adds document chunks to ChromaDB.
        """

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

    # ========================================================
    # Delete Document
    # ========================================================

    def delete_document(
        self,
        doc_id: str
    ) -> bool:
        """
        Deletes all chunks belonging to a document.
        """

        try:

            self._ensure_vector_store()

            collection = self.vector_store._collection

            results = collection.get(
                where={
                    "doc_id": doc_id
                }
            )

            if results and results.get("ids"):

                collection.delete(
                    ids=results["ids"]
                )

                return True

            return False

        except Exception as e:

            print(
                f"Error deleting document "
                f"{doc_id}: {str(e)}"
            )

            return False

    # ========================================================
    # Update Document
    # ========================================================

    def update_document(
        self,
        doc_id: str,
        new_documents: List[Document]
    ) -> bool:
        """
        Replaces an existing document.
        """

        self.delete_document(doc_id)

        self.add_documents(
            new_documents
        )

        return True

    # ========================================================
    # List Documents
    # ========================================================

    def list_documents(
        self
    ) -> List[Dict[str, Any]]:
        """
        Lists all distinct documents with chunk counts.
        """

        try:

            self._ensure_vector_store()

            collection = self.vector_store._collection

            results = collection.get(
                include=["metadatas"]
            )

            doc_map: Dict[
                str,
                Dict[str, Any]
            ] = {}

            if results and results.get(
                "metadatas"
            ):

                for meta in results["metadatas"]:

                    if not meta:
                        continue

                    if "doc_id" not in meta:
                        continue

                    doc_id = meta["doc_id"]

                    source_file = meta.get(
                        "source_file",
                        "Unknown"
                    )

                    if doc_id not in doc_map:

                        doc_map[doc_id] = {
                            "doc_id": doc_id,
                            "source_file": source_file,
                            "chunk_count": 0
                        }

                    doc_map[
                        doc_id
                    ]["chunk_count"] += 1

            return list(
                doc_map.values()
            )

        except Exception as e:

            print(
                f"Error listing documents: "
                f"{str(e)}"
            )

            return []

    # ========================================================
    # Similarity Search
    # ========================================================

    def similarity_search(
        self,
        query: str,
        k: int = TOP_K,
        metadata_filter: Optional[
            Dict[str, Any]
        ] = None
    ) -> List[Document]:
        """
        Performs similarity search with optional
        metadata filtering.

        Metadata example:

            {
                "doc_id": "123"
            }

        or:

            {
                "file_type": ".csv"
            }
        """

        self._ensure_vector_store()

        # ----------------------------------------------------
        # Select indexing strategy
        # ----------------------------------------------------

        strategy_info = (
            self.get_index_strategy()
        )

        strategy = strategy_info[
            "index_strategy"
        ]

        # ----------------------------------------------------
        # Current ChromaDB limitation
        # ----------------------------------------------------

        if strategy == IVF_INDEX:

            print(
                "INFO: Rule selected IVF, "
                "but current ChromaDB collection "
                "uses HNSW internally. "
                "Continuing with ChromaDB search."
            )

        # ----------------------------------------------------
        # Metadata filtered search
        # ----------------------------------------------------

        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=metadata_filter
        )