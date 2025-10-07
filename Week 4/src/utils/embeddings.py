"""
Embeddings and Vector Store Module

Manages document embeddings and vector storage for semantic search.
"""

from typing import List, Optional
from langchain.schema import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from src.config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """
    Manages document embeddings and vector storage.

    This class handles:
    - Creating embeddings using Ollama
    - Storing embeddings in a vector database
    - Providing semantic search capabilities
    """

    def __init__(
        self,
        model_name: str = Config.EMBEDDINGS_MODEL_NAME,
        retrieval_k: int = Config.RETRIEVAL_K
    ):
        """
        Initialize the embeddings manager.

        Args:
            model_name: Name of the Ollama embeddings model
            retrieval_k: Number of documents to retrieve in searches
        """
        self.model_name = model_name
        self.retrieval_k = retrieval_k

        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=Config.OLLAMA_BASE_URL
        )

        # Vector store will be initialized when documents are added
        self.vectorstore: Optional[InMemoryVectorStore] = None
        self.retriever: Optional[VectorStoreRetriever] = None

        logger.info(f"EmbeddingsManager initialized with model={model_name}, k={retrieval_k}")

    def create_vectorstore(self, documents: List[Document]) -> InMemoryVectorStore:
        """
        Creates a vector store from documents.

        This method:
        1. Generates embeddings for all documents
        2. Stores them in an in-memory vector database
        3. Enables fast semantic similarity search

        Args:
            documents: List of Document chunks to embed

        Returns:
            InMemoryVectorStore containing the embedded documents
        """
        if not documents:
            raise ValueError("Cannot create vectorstore from empty document list")

        logger.info(f"Creating vectorstore from {len(documents)} documents")

        # Create vector store with embeddings
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=documents,
            embedding=self.embeddings
        )

        logger.info("✓ Vectorstore created successfully")

        return self.vectorstore

    def get_retriever(self) -> VectorStoreRetriever:
        """
        Gets or creates a retriever for semantic search.

        Returns:
            VectorStoreRetriever configured for semantic search

        Raises:
            RuntimeError: If vectorstore hasn't been created yet
        """
        if self.vectorstore is None:
            raise RuntimeError(
                "Vectorstore not initialized. Call create_vectorstore() first."
            )

        if self.retriever is None:
            # Create retriever that returns top k most relevant documents
            self.retriever = self.vectorstore.as_retriever(k=self.retrieval_k)
            logger.info(f"✓ Retriever created with k={self.retrieval_k}")

        return self.retriever

    def search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Performs semantic search on the document collection.

        Args:
            query: Search query
            k: Number of results to return (uses default if None)

        Returns:
            List of most relevant Documents
        """
        if self.vectorstore is None:
            raise RuntimeError("Vectorstore not initialized")

        k = k or self.retrieval_k

        logger.info(f"Searching for: '{query[:50]}...'")

        # Perform similarity search
        results = self.vectorstore.similarity_search(query, k=k)

        logger.info(f"✓ Found {len(results)} relevant documents")

        return results

    def get_stats(self) -> dict:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with vector store statistics
        """
        if self.vectorstore is None:
            return {"status": "not_initialized"}

        # Note: InMemoryVectorStore doesn't expose document count directly
        # This is a limitation we acknowledge
        return {
            "status": "initialized",
            "model": self.model_name,
            "retrieval_k": self.retrieval_k
        }


def create_embeddings_from_documents(
    documents: List[Document]
) -> tuple[InMemoryVectorStore, VectorStoreRetriever]:
    """
    Convenience function to create embeddings and retriever from documents.

    Args:
        documents: List of Document chunks

    Returns:
        Tuple of (vectorstore, retriever)
    """
    manager = EmbeddingsManager()
    vectorstore = manager.create_vectorstore(documents)
    retriever = manager.get_retriever()

    return vectorstore, retriever
