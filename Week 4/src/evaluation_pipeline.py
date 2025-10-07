"""
Evaluation Pipeline

Orchestrates the complete evaluation workflow for the RAG system with A2A protocol.
"""

from typing import Dict, Any
from langsmith import traceable
from langsmith.evaluation import evaluate
from src.config import Config
from src.utils.document_processor import load_eu_ai_act
from src.utils.embeddings import create_embeddings_from_documents
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.answer_agent import AnswerAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.evaluators import (
    correctness_evaluator,
    relevance_evaluator,
    groundedness_evaluator,
    retrieval_relevance_evaluator
)
from src.utils.dataset import DatasetManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """
    Complete evaluation pipeline for the RAG system.

    This class orchestrates:
    1. Document processing and embedding
    2. A2A agent initialization
    3. Dataset management
    4. Evaluation execution
    5. Results analysis
    """

    def __init__(self):
        """Initialize the evaluation pipeline."""
        logger.info("=" * 80)
        logger.info("Initializing Evaluation Pipeline with A2A Protocol")
        logger.info("=" * 80)

        # Validate configuration
        Config.validate()

        # Initialize components
        self.coordinator = None
        self.dataset_manager = None
        self.vectorstore = None
        self.retriever = None

        logger.info("Configuration validated")

    def setup_rag_system(self):
        """
        Sets up the complete RAG system with A2A protocol.

        This includes:
        - Loading and processing the EU AI Act PDF
        - Creating embeddings and vector store
        - Initializing all agents
        - Setting up the coordinator
        """
        logger.info("\n[SETUP] Initializing RAG System Components")
        logger.info("-" * 80)

        # Step 1: Load and process documents
        logger.info("[1/4] Loading EU AI Act document...")
        documents = load_eu_ai_act()
        logger.info(f"Loaded and processed {len(documents)} document chunks")

        # Step 2: Create embeddings and vector store
        logger.info("[2/4] Creating embeddings and vector store...")
        self.vectorstore, self.retriever = create_embeddings_from_documents(documents)
        logger.info("Vector store initialized")

        # Step 3: Initialize A2A agents
        logger.info("[3/4] Initializing A2A Protocol agents...")

        # Create specialized agents
        retrieval_agent = RetrievalAgent(self.retriever)
        analysis_agent = AnalysisAgent()
        answer_agent = AnswerAgent()

        # Create coordinator
        self.coordinator = CoordinatorAgent(
            retrieval_agent=retrieval_agent,
            analysis_agent=analysis_agent,
            answer_agent=answer_agent
        )

        logger.info("Agent-to-Agent Protocol agents initialized:")
        for agent_info in self.coordinator.get_agent_summary()["specialized_agents"]:
            logger.info(f"  - {agent_info['name']}: {agent_info['description']}")

        # Step 4: Initialize dataset
        logger.info("[4/4] Setting up evaluation dataset...")
        self.dataset_manager = DatasetManager()
        self.dataset_manager.create_dataset()
        logger.info("Evaluation dataset ready")

        logger.info("\nRAG System Setup Complete!")
        logger.info("=" * 80)

    @traceable(name="rag_target_function")
    def target_function(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Target function for evaluation.

        This wraps the A2A coordinator for systematic evaluation.

        Args:
            inputs: Dictionary with 'question' key

        Returns:
            Dictionary with 'answer', 'documents', and metadata
        """
        if self.coordinator is None:
            raise RuntimeError("RAG system not set up. Call setup_rag_system() first.")

        question = inputs.get("question", "")

        # Process through A2A protocol
        result = self.coordinator.process_with_trace(question)

        return result

    def run_evaluation(self) -> Dict[str, Any]:
        """
        Runs the complete evaluation pipeline.

        Returns:
            Dictionary with evaluation results
        """
        if self.coordinator is None:
            raise RuntimeError("RAG system not set up. Call setup_rag_system() first.")

        logger.info("\n[EVALUATION] Running Comprehensive Evaluation")
        logger.info("=" * 80)

        logger.info("Evaluators:")
        logger.info("  1. Correctness - Comparing answers with references")
        logger.info("  2. Relevance - Checking answer-question alignment")
        logger.info("  3. Groundedness - Verifying document support")
        logger.info("  4. Retrieval Relevance - Assessing retrieval quality")
        logger.info("-" * 80)

        # Run evaluation
        results = evaluate(
            self.target_function,
            data=Config.DATASET_NAME,
            evaluators=[
                correctness_evaluator,
                relevance_evaluator,
                groundedness_evaluator,
                retrieval_relevance_evaluator
            ],
            experiment_prefix=Config.EXPERIMENT_PREFIX,
            description="Comprehensive RAG evaluation with A2A protocol for EU AI Act compliance",
            max_concurrency=2  # Limit concurrency to avoid rate limits
        )

        logger.info("\nEvaluation Complete!")
        logger.info("=" * 80)
        logger.info(f"Experiment: {results['experiment_name']}")
        logger.info(f"View results: https://smith.langchain.com")
        logger.info("=" * 80)

        return results

    def test_single_question(self, question: str) -> Dict[str, Any]:
        """
        Test the system with a single question.

        Args:
            question: The compliance question

        Returns:
            Complete result with answer, documents, and trace
        """
        if self.coordinator is None:
            raise RuntimeError("RAG system not set up. Call setup_rag_system() first.")

        logger.info(f"\n[TEST] Processing question:")
        logger.info(f"Q: {question}")
        logger.info("-" * 80)

        result = self.target_function({"question": question})

        logger.info(f"\nAnswer: {result['answer'][:200]}...")
        logger.info(f"Documents retrieved: {len(result['documents'])}")
        logger.info(f"Agents involved: {result['metadata']['agents_involved']}")

        return result


def run_complete_pipeline():
    """
    Runs the complete evaluation pipeline from start to finish.

    This is the main entry point for running evaluations.
    """
    # Create pipeline
    pipeline = EvaluationPipeline()

    # Setup RAG system
    pipeline.setup_rag_system()

    # Test with a single question first
    test_question = "What are the prohibited AI practices under the EU AI Act?"
    pipeline.test_single_question(test_question)

    # Run full evaluation
    results = pipeline.run_evaluation()

    return results
