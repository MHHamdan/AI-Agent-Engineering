"""
Groundedness Evaluator

Evaluates if the generated answer is grounded in the retrieved documents.
"""

from typing_extensions import Annotated, TypedDict
from langchain_ollama import OllamaLLM
from langsmith.schemas import Run, Example
from src.config import Config
import logging
import json

logger = logging.getLogger(__name__)


class GroundedGrade(TypedDict):
    """Schema for groundedness evaluation results."""
    score: Annotated[int, ..., "Groundedness score: 0 (not grounded) or 1 (grounded)"]
    reasoning: Annotated[str, ..., "Explanation for the groundedness score"]


# Instructions for the groundedness evaluator
GROUNDED_INSTRUCTIONS = """You are evaluating whether an answer is grounded in (supported by) the retrieved documents from the EU AI Act.

Check if all claims in the answer are supported by the retrieved documents:
- Score 1 (Grounded): All statements in the answer are supported by or can be inferred from the retrieved documents
- Score 0 (Not Grounded): The answer contains information not found in the retrieved documents, or makes unsupported claims

Provide:
1. A score (0 or 1)
2. Clear reasoning explaining your score

Be strict: the answer should only contain information from the retrieved documents."""


# Initialize the grader LLM (Ollama)
grounded_llm = OllamaLLM(
    model=Config.EVALUATOR_MODEL_NAME,
    temperature=Config.EVALUATOR_MODEL_TEMPERATURE,
    base_url=Config.OLLAMA_BASE_URL,
    format="json"
)


def groundedness_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluates if the generated answer is grounded in the retrieved documents.

    This evaluator:
    1. Takes the documents that were retrieved from the EU AI Act
    2. Takes the generated answer
    3. Checks if every claim in the answer is supported by the documents

    This prevents hallucination and ensures factual accuracy.

    Args:
        run: The execution run containing the answer and retrieved documents
        example: The test example (not used here but required by interface)

    Returns:
        A dictionary with the score and reasoning
    """
    # Extract the generated answer
    generated_answer = run.outputs.get("answer", "")

    # Extract the retrieved documents
    documents = run.outputs.get("documents", [])

    if not generated_answer:
        logger.warning("Missing answer in groundedness evaluation")
        return {
            "key": "groundedness",
            "score": 0,
            "reason": "Missing generated answer"
        }

    if not documents:
        logger.warning("No documents in groundedness evaluation")
        return {
            "key": "groundedness",
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

    # Grade the groundedness using the LLM
    prompt = f"""{GROUNDED_INSTRUCTIONS}

Retrieved Documents:
{context}

Generated Answer: {generated_answer}

Respond with JSON only."""

    try:
        response = grounded_llm.invoke(prompt)
        grade = json.loads(response)

        logger.info(f"Groundedness score: {grade['score']}")

        return {
            "key": "groundedness",
            "score": grade["score"],
            "reason": grade["reasoning"]
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse evaluator response: {e}")
        return {
            "key": "groundedness",
            "score": 0,
            "reason": f"Evaluation error: {str(e)}"
        }
