#!/usr/bin/env python3
"""
EU AI Act RAG Evaluation System - Main Entry Point

This script provides a command-line interface for running the RAG evaluation system
with A2A (Agent-to-Agent) protocol.

Usage:
    python main.py --mode [evaluate|test|setup]
    python main.py --help
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluation_pipeline import EvaluationPipeline
from src.config import Config
from src.utils.dataset import DatasetManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="EU AI Act RAG Evaluation System with A2A Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full evaluation
  python main.py --mode evaluate

  # Test with a single question
  python main.py --mode test --question "What are prohibited AI practices?"

  # Setup dataset only
  python main.py --mode setup

  # Run with custom dataset
  python main.py --mode evaluate --dataset my-custom-dataset
        """
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["evaluate", "test", "setup"],
        default="evaluate",
        help="Operation mode: evaluate (full eval), test (single question), setup (dataset only)"
    )

    parser.add_argument(
        "--question",
        type=str,
        help="Question to test (only for test mode)"
    )

    parser.add_argument(
        "--dataset",
        type=str,
        help="Dataset name to use (default: from config)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print header
    print_header()

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()
        logger.info("Configuration validated")

        # Update dataset name if provided
        if args.dataset:
            Config.DATASET_NAME = args.dataset
            logger.info(f"Using dataset: {args.dataset}")

        # Execute based on mode
        if args.mode == "setup":
            run_setup()

        elif args.mode == "test":
            run_test(args.question)

        elif args.mode == "evaluate":
            run_evaluation()

    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"\nError: {str(e)}", exc_info=args.verbose)
        sys.exit(1)


def print_header():
    """Print application header."""
    print("\n" + "=" * 80)
    print("  EU AI Act RAG Evaluation System")
    print("  Agent-to-Agent Protocol Implementation")
    print("=" * 80 + "\n")


def run_setup():
    """Setup mode - Initialize dataset only."""
    logger.info("Mode: SETUP - Dataset initialization")
    print("\nSetting up evaluation dataset...\n")

    dataset_manager = DatasetManager()
    dataset_manager.create_dataset()

    stats = dataset_manager.get_dataset_stats()

    print("\nDataset setup complete!")
    print(f"  Name: {stats['dataset_name']}")
    print(f"  Examples: {stats['total_examples']}")
    print(f"  Categories: {stats['categories']}")
    print("\n")


def run_test(question: str = None):
    """Test mode - Run with a single question."""
    logger.info("Mode: TEST - Single question")

    if not question:
        # Use default test question
        question = "What are the prohibited AI practices under the EU AI Act?"
        print(f"\nNo question provided, using default:")
        print(f"   '{question}'\n")

    print(f"\nTesting with question:")
    print(f"   {question}\n")

    # Initialize pipeline
    pipeline = EvaluationPipeline()

    # Setup RAG system
    print("Setting up RAG system with Agent-to-Agent protocol...\n")
    pipeline.setup_rag_system()

    # Test question
    print("\nProcessing through Agent-to-Agent protocol...\n")
    result = pipeline.test_single_question(question)

    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"\nQuestion:")
    print(f"   {question}")

    print(f"\nAnswer:")
    print(f"   {result['answer']}\n")

    print(f"Retrieved Documents: {len(result['documents'])}")

    print(f"\nAgent Workflow:")
    for trace in result.get('agent_trace', []):
        print(f"   {trace['agent']}: {trace['action']}")

    print(f"\nProtocol: {result['metadata']['protocol']}")
    print(f"Agents Involved: {result['metadata']['agents_involved']}")
    print("\n")


def run_evaluation():
    """Evaluate mode - Run full evaluation pipeline."""
    logger.info("Mode: EVALUATE - Full evaluation")

    print("\nRunning comprehensive evaluation with Agent-to-Agent protocol...\n")

    # Initialize pipeline
    pipeline = EvaluationPipeline()

    # Setup RAG system
    print("Step 1: Setting up RAG system...\n")
    pipeline.setup_rag_system()

    # Run evaluation
    print("\nStep 2: Running evaluation on all test cases...\n")
    results = pipeline.run_evaluation()

    # Display summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    print(f"\nExperiment: {results['experiment_name']}")
    print(f"Evaluators: Correctness, Relevance, Groundedness, Retrieval Relevance")
    print(f"Protocol: Agent-to-Agent")

    print(f"\nView detailed results:")
    print(f"   https://smith.langchain.com")

    print(f"\nNext steps:")
    print(f"   1. Review scores in LangSmith dashboard")
    print(f"   2. Analyze agent traces for insights")
    print(f"   3. Identify areas for improvement")
    print(f"   4. Iterate on agent prompts and configurations")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
