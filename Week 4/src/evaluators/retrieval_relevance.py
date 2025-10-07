"""
Retrieval Relevance Evaluator

Evaluates if the retrieved documents are relevant to the input question.
"""

from typing_extensions import Annotated, TypedDict
from langchain_ollama import OllamaLLM
from langsmith.schemas import Run, Example
from src.config import Config
import logging
import json

logger = logging.getLogger(__name__)


class RetrievalRelevanceGrade(TypedDict):
    """Schema for retrieval relevance evaluation results."""
    score: Annotated[int, ..., "Retrieval relevance score: 0 (not relevant) or 1 (relevant)"]
    reasoning: Annotated[str, ..., "Explanation for the retrieval relevance score"]


# Instructions for the retrieval relevance evaluator
RETRIEVAL_RELEVANCE_INSTRUCTIONS = """You are evaluating whether retrieved documents from the EU AI Act are relevant to a compliance question.

Assess if the retrieved documents contain information that could help answer the question:
- Score 1 (Relevant): The documents contain information pertinent to answering the question
- Score 0 (Not Relevant): The documents don't contain useful information for answering the question

Provide:
1. A score (0 or 1)
2. Clear reasoning explaining your score

Focus on whether the documents contain information that could help answer the question, even if they don't contain the complete answer."""


# Initialize the grader LLM (Ollama)
retrieval_relevance_llm = OllamaLLM(
    model=Config.EVALUATOR_MODEL_NAME,
    temperature=Config.EVALUATOR_MODEL_TEMPERATURE,
    base_url=Config.OLLAMA_BASE_URL,
    format="json"
)


def retrieval_relevance_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluates if the retrieved documents are relevant to the input question.

    This evaluator:
    1. Takes the user's question
    2. Takes the documents that were retrieved
    3. Checks if the documents contain information useful for answering the question

    This helps diagnose retrieval problems in the RAG pipeline.

    Args:
        run: The execution run containing the retrieved documents
        example: The test example containing the input question

    Returns:
        A dictionary with the score and reasoning
    """
    # Extract the input question
    question = example.inputs.get("question", "")

    # Extract the retrieved documents
    documents = run.outputs.get("documents", [])

    if not question:
        logger.warning("Missing question in retrieval relevance evaluation")
        return {
            "key": "retrieval_relevance",
            "score": 0,
            "reason": "Missing question"
        }

    if not documents:
        logger.warning("No documents in retrieval relevance evaluation")
        return {
            "key": "retrieval_relevance",
            "score": 0,
            "reason": "No documents retrieved"
        }

    # Combine documents into a single context string
    context_parts = []
    for doc in documents:
        if isinstance(doc, str):
            context_parts.append(doc)
        elif hasattr(doc, 'page_content'):
            context_parts.append(doc.page_content)
        elif isinstance(doc, dict):
            context_parts.append(doc.get("content", ""))

    context = "\n\n".join(context_parts)

    # Grade the retrieval relevance using the LLM
    prompt = f"""{RETRIEVAL_RELEVANCE_INSTRUCTIONS}

Question: {question}

Retrieved Documents:
{context}

Respond with JSON only."""

    try:
        response = retrieval_relevance_llm.invoke(prompt)
        grade = json.loads(response)

        logger.info(f"Retrieval relevance score: {grade['score']}")

        return {
            "key": "retrieval_relevance",
            "score": grade["score"],
            "reason": grade["reasoning"]
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse evaluator response: {e}")
        return {
            "key": "retrieval_relevance",
            "score": 0,
            "reason": f"Evaluation error: {str(e)}"
        }
