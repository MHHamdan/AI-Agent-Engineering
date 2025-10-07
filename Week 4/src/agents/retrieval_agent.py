"""
Retrieval Agent

Specialized agent for finding and retrieving relevant documents from the EU AI Act.
This agent implements the retrieval component of the A2A protocol.
"""

from typing import Dict, Any, List
from langchain.schema import Document
from langchain_core.vectorstores import VectorStoreRetriever
from src.agents.base_agent import BaseAgent
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)


class RetrievalAgent(BaseAgent):
    """
    Specialized agent for document retrieval.

    In the A2A protocol, this agent:
    - Receives questions from the coordinator
    - Performs semantic search on the document corpus
    - Returns relevant document chunks
    - Provides retrieval quality metrics
    """

    def __init__(self, retriever: VectorStoreRetriever):
        """
        Initialize the retrieval agent.

        Args:
            retriever: Configured vector store retriever
        """
        super().__init__(
            name="RetrievalAgent",
            description="Specialized in finding relevant EU AI Act documents using semantic search"
        )
        self.retriever = retriever

    @traceable(name="retrieval_agent_process")
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a retrieval request.

        Args:
            inputs: Dictionary with 'question' key

        Returns:
            Dictionary with 'documents' and 'metadata' keys
        """
        question = inputs.get("question", "")

        if not question:
            logger.warning("Empty question received")
            return {"documents": [], "metadata": {"status": "error", "reason": "empty_question"}}

        logger.info(f"[{self.name}] Processing question: {question[:100]}...")

        # Perform semantic search
        documents = self.retriever.invoke(question)

        # Prepare metadata about the retrieval
        metadata = {
            "status": "success",
            "num_documents": len(documents),
            "agent": self.name,
            "query_length": len(question)
        }

        logger.info(f"[{self.name}] Retrieved {len(documents)} documents")

        return {
            "documents": documents,
            "metadata": metadata,
            "agent_name": self.name
        }

    def get_document_summaries(self, documents: List[Document]) -> List[str]:
        """
        Get brief summaries of retrieved documents.

        Args:
            documents: List of retrieved documents

        Returns:
            List of summary strings
        """
        summaries = []
        for i, doc in enumerate(documents, 1):
            page = doc.metadata.get('page', 'N/A')
            preview = doc.page_content[:100]
            summaries.append(f"Doc {i} (Page {page}): {preview}...")

        return summaries
