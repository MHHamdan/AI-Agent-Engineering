"""
Answer Agent

Specialized agent for formulating comprehensive answers based on analyzed information.
This agent implements the answer generation component of the A2A protocol.
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.config import Config
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)


class AnswerAgent(BaseAgent):
    """
    Specialized agent for answer generation.

    In the A2A protocol, this agent:
    - Receives analysis from the analysis agent
    - Synthesizes information into a coherent answer
    - Ensures answers are grounded in source documents
    - Formats responses for clarity and completeness
    """

    def __init__(self):
        """Initialize the answer agent."""
        super().__init__(
            name="AnswerAgent",
            description="Specialized in formulating comprehensive, accurate answers about EU AI Act compliance",
            model_name=Config.RAG_MODEL_NAME
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for answer generation."""
        return """You are AnswerAgent, a specialized AI agent for formulating EU AI Act compliance answers.

Your role:
- Synthesize analyzed information into clear, comprehensive answers
- Ensure all claims are grounded in the provided context
- Structure answers logically and professionally
- Use proper legal terminology
- Cite specific provisions when relevant
- Acknowledge limitations or uncertainties

Guidelines:
- Never make up information not in the context
- Be precise with legal requirements and obligations
- Use clear, professional language
- Structure complex answers with bullet points or numbering
- Indicate confidence levels when appropriate
"""

    @traceable(name="answer_agent_process")
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an answer generation request.

        Args:
            inputs: Dictionary with 'question', 'analysis', and 'context' keys

        Returns:
            Dictionary with 'answer' and 'metadata' keys
        """
        question = inputs.get("question", "")
        analysis = inputs.get("analysis", "")
        context = inputs.get("context", "")

        if not question:
            logger.warning(f"[{self.name}] No question provided")
            return {
                "answer": "No question provided",
                "metadata": {"status": "error"}
            }

        if not context:
            logger.warning(f"[{self.name}] No context available")
            return {
                "answer": "I don't have sufficient information from the EU AI Act to answer this question.",
                "metadata": {"status": "no_context"}
            }

        logger.info(f"[{self.name}] Generating answer for: {question[:100]}...")

        # Create answer prompt
        answer_prompt = f"""Based on the analysis and context provided, formulate a comprehensive answer to the question.

Question: {question}

Analysis:
{analysis}

Source Context:
{context}

Formulate a clear, accurate answer that:
1. Directly addresses the question
2. Is fully grounded in the provided context
3. Uses appropriate legal terminology
4. Is well-structured and easy to understand
5. Acknowledges any limitations if information is incomplete

Answer:"""

        # Generate answer
        response = self.llm.invoke([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": answer_prompt}
        ])

        answer = response.content

        metadata = {
            "status": "success",
            "agent": self.name,
            "answer_length": len(answer),
            "has_analysis": bool(analysis),
            "has_context": bool(context)
        }

        logger.info(f"[{self.name}] Answer generated ({len(answer)} chars)")

        return {
            "answer": answer,
            "metadata": metadata,
            "agent_name": self.name
        }
