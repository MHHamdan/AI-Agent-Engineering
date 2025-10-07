"""
Analysis Agent

Specialized agent for analyzing retrieved documents and extracting relevant information.
This agent implements the analysis component of the A2A protocol.
"""

from typing import Dict, Any, List
from langchain.schema import Document
from src.agents.base_agent import BaseAgent
from src.config import Config
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):
    """
    Specialized agent for document analysis.

    In the A2A protocol, this agent:
    - Receives documents from the retrieval agent
    - Analyzes content for relevance to the question
    - Extracts key information and insights
    - Provides structured analysis to the answer agent
    """

    def __init__(self):
        """Initialize the analysis agent."""
        super().__init__(
            name="AnalysisAgent",
            description="Specialized in analyzing EU AI Act documents and extracting relevant information",
            model_name=Config.RAG_MODEL_NAME
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for analysis."""
        return """You are AnalysisAgent, a specialized AI agent for analyzing EU AI Act documents.

Your role:
- Analyze retrieved documents for relevance to questions
- Extract key facts, requirements, and regulations
- Identify important legal provisions and obligations
- Summarize complex regulatory language
- Provide structured analysis for answer generation

Guidelines:
- Focus on factual information only
- Preserve legal accuracy and terminology
- Highlight contradictions or ambiguities
- Note confidence levels for extracted information
"""

    @traceable(name="analysis_agent_process")
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an analysis request.

        Args:
            inputs: Dictionary with 'question' and 'documents' keys

        Returns:
            Dictionary with 'analysis', 'key_points', and 'metadata' keys
        """
        question = inputs.get("question", "")
        documents = inputs.get("documents", [])

        if not documents:
            logger.warning(f"[{self.name}] No documents to analyze")
            return {
                "analysis": "No documents available for analysis",
                "key_points": [],
                "metadata": {"status": "no_documents"}
            }

        logger.info(f"[{self.name}] Analyzing {len(documents)} documents")

        # Combine document content
        context = self._prepare_context(documents)

        # Analyze the content
        analysis_prompt = f"""Analyze the following EU AI Act documents in relation to this question:

Question: {question}

Documents:
{context}

Provide:
1. Overall relevance assessment
2. Key facts and requirements extracted
3. Important legal provisions identified
4. Any ambiguities or edge cases

Be concise but thorough."""

        # Get analysis from LLM
        response = self.llm.invoke([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": analysis_prompt}
        ])

        analysis = response.content

        # Extract key points
        key_points = self._extract_key_points(analysis)

        metadata = {
            "status": "success",
            "num_documents_analyzed": len(documents),
            "agent": self.name
        }

        logger.info(f"[{self.name}] Analysis complete")

        return {
            "analysis": analysis,
            "key_points": key_points,
            "context": context,
            "metadata": metadata,
            "agent_name": self.name
        }

    def _prepare_context(self, documents: List[Document]) -> str:
        """
        Prepare document context for analysis.

        Args:
            documents: List of documents

        Returns:
            Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            page = doc.metadata.get('page', 'N/A')
            context_parts.append(f"[Document {i}, Page {page}]\n{doc.page_content}")

        return "\n\n".join(context_parts)

    def _extract_key_points(self, analysis: str) -> List[str]:
        """
        Extract key points from analysis text.

        Args:
            analysis: Analysis text

        Returns:
            List of key points
        """
        # Simple extraction based on numbered lists or bullet points
        # In production, this could use more sophisticated NLP
        lines = analysis.split('\n')
        key_points = []

        for line in lines:
            line = line.strip()
            # Look for numbered items or bullet points
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                key_points.append(line)

        return key_points[:5]  # Return top 5 key points
