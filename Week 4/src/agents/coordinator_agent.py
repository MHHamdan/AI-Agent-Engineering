"""
Coordinator Agent

Orchestrates the A2A (Agent-to-Agent) protocol by coordinating multiple specialized agents.
This is the main entry point for the multi-agent RAG system.
"""

from typing import Dict, Any, List
from langchain.schema import Document
from src.agents.base_agent import BaseAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.answer_agent import AnswerAgent
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that orchestrates the A2A protocol.

    This agent:
    - Receives user questions
    - Coordinates communication between specialized agents
    - Implements the A2A protocol workflow:
      1. Retrieval Agent → Find relevant documents
      2. Analysis Agent → Analyze documents
      3. Answer Agent → Generate final answer
    - Tracks agent interactions and performance
    """

    def __init__(
        self,
        retrieval_agent: RetrievalAgent,
        analysis_agent: AnalysisAgent,
        answer_agent: AnswerAgent
    ):
        """
        Initialize the coordinator agent.

        Args:
            retrieval_agent: Agent for document retrieval
            analysis_agent: Agent for document analysis
            answer_agent: Agent for answer generation
        """
        super().__init__(
            name="CoordinatorAgent",
            description="Orchestrates multi-agent collaboration using A2A protocol"
        )

        self.retrieval_agent = retrieval_agent
        self.analysis_agent = analysis_agent
        self.answer_agent = answer_agent

        self.agent_chain = [
            self.retrieval_agent,
            self.analysis_agent,
            self.answer_agent
        ]

        logger.info(f"[{self.name}] Initialized with {len(self.agent_chain)} specialized agents")

    @traceable(name="coordinator_agent_process")
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a question using the A2A protocol.

        This implements the full agent-to-agent workflow:
        1. Coordinator receives question
        2. Retrieval agent finds relevant documents
        3. Analysis agent analyzes the documents
        4. Answer agent generates the final answer
        5. Coordinator returns complete results

        Args:
            inputs: Dictionary with 'question' key

        Returns:
            Dictionary with 'answer', 'documents', and 'agent_trace' keys
        """
        question = inputs.get("question", "")

        if not question:
            logger.error(f"[{self.name}] No question provided")
            return {"error": "No question provided"}

        logger.info(f"[{self.name}] Starting A2A protocol for question: {question[:100]}...")

        # Track agent interactions
        agent_trace = []

        # STEP 1: Retrieval Agent - Find relevant documents
        logger.info(f"[{self.name}] → Delegating to {self.retrieval_agent.name}")
        retrieval_result = self.retrieval_agent.process({"question": question})
        agent_trace.append({
            "agent": self.retrieval_agent.name,
            "action": "document_retrieval",
            "metadata": retrieval_result.get("metadata", {})
        })

        documents = retrieval_result.get("documents", [])
        if not documents:
            logger.warning(f"[{self.name}] No documents retrieved")
            return {
                "answer": "I couldn't find relevant information in the EU AI Act to answer this question.",
                "documents": [],
                "agent_trace": agent_trace
            }

        # STEP 2: Analysis Agent - Analyze documents
        logger.info(f"[{self.name}] → Delegating to {self.analysis_agent.name}")
        analysis_result = self.analysis_agent.process({
            "question": question,
            "documents": documents
        })
        agent_trace.append({
            "agent": self.analysis_agent.name,
            "action": "document_analysis",
            "metadata": analysis_result.get("metadata", {})
        })

        # STEP 3: Answer Agent - Generate final answer
        logger.info(f"[{self.name}] → Delegating to {self.answer_agent.name}")
        answer_result = self.answer_agent.process({
            "question": question,
            "analysis": analysis_result.get("analysis", ""),
            "context": analysis_result.get("context", "")
        })
        agent_trace.append({
            "agent": self.answer_agent.name,
            "action": "answer_generation",
            "metadata": answer_result.get("metadata", {})
        })

        answer = answer_result.get("answer", "")

        logger.info(f"[{self.name}] A2A protocol complete")

        # Return comprehensive results
        return {
            "answer": answer,
            "documents": documents,
            "analysis": analysis_result.get("analysis", ""),
            "key_points": analysis_result.get("key_points", []),
            "agent_trace": agent_trace,
            "metadata": {
                "coordinator": self.name,
                "agents_involved": len(agent_trace),
                "protocol": "A2A"
            }
        }

    def get_agent_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all agents in the system.

        Returns:
            Dictionary with agent information
        """
        return {
            "coordinator": {
                "name": self.name,
                "description": self.description
            },
            "specialized_agents": [
                {
                    "name": agent.name,
                    "description": agent.description,
                    "role": agent.__class__.__name__
                }
                for agent in self.agent_chain
            ]
        }

    @traceable(name="coordinator_a2a_workflow")
    def process_with_trace(self, question: str) -> Dict[str, Any]:
        """
        Process a question with detailed tracing for evaluation.

        This method is specifically designed for evaluation purposes,
        providing detailed information about the A2A protocol execution.

        Args:
            question: The compliance question

        Returns:
            Dictionary with answer, documents, and detailed trace
        """
        result = self.process({"question": question})

        # Add additional tracing information
        result["workflow"] = {
            "step_1": "Retrieval Agent → Found documents",
            "step_2": "Analysis Agent → Analyzed content",
            "step_3": "Answer Agent → Generated answer",
            "protocol": "A2A (Agent-to-Agent)",
            "total_agents": len(self.agent_chain)
        }

        return result
