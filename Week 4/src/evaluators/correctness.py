"""
Correctness Evaluator

Evaluates if the generated answer is correct compared to the reference answer.
"""

from typing_extensions import Annotated, TypedDict
from langchain_ollama import OllamaLLM
from langsmith.schemas import Run, Example
from src.config import Config
import logging
import json

logger = logging.getLogger(__name__)


class CorrectnessGrade(TypedDict):
    """Schema for correctness evaluation results."""
    score: Annotated[int, ..., "Correctness score: 0 (incorrect) or 1 (correct)"]
    reasoning: Annotated[str, ..., "Explanation for the correctness score"]


# Instructions for the correctness evaluator
CORRECTNESS_INSTRUCTIONS = """You are evaluating the correctness of an answer to an EU AI Act compliance question.

Compare the generated answer with the reference answer:
- Score 1 (Correct): The generated answer captures the same key information and meaning as the reference answer, even if worded differently
- Score 0 (Incorrect): The generated answer is wrong, incomplete, or significantly differs from the reference answer

Provide:
1. A score (0 or 1)
2. Clear reasoning explaining your score

Focus on semantic correctness, not exact wording."""


# Initialize the grader LLM (Ollama)
grader_llm = OllamaLLM(
    model=Config.EVALUATOR_MODEL_NAME,
    temperature=Config.EVALUATOR_MODEL_TEMPERATURE,
    base_url=Config.OLLAMA_BASE_URL,
    format="json"
)


def correctness_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluates if the generated answer is correct compared to the reference answer.

    This evaluator:
    1. Takes the generated answer from the RAG system
    2. Compares it to the expected reference answer
    3. Returns a score (0 or 1) and reasoning

    Args:
        run: The execution run containing the generated answer
        example: The test example containing the reference answer

    Returns:
        A dictionary with the score and reasoning
    """
    # Extract the generated answer from the run outputs
    generated_answer = run.outputs.get("answer", "")

    # Extract the reference answer from the example
    reference_answer = example.outputs.get("expected_answer", "")

    if not generated_answer or not reference_answer:
        logger.warning("Missing answer in correctness evaluation")
        return {
            "key": "correctness",
            "score": 0,
            "reason": "Missing generated or reference answer"
        }

    # Grade the answer using the LLM
    prompt = f"""{CORRECTNESS_INSTRUCTIONS}

Reference Answer: {reference_answer}

Generated Answer: {generated_answer}

Respond with JSON only."""

    try:
        response = grader_llm.invoke(prompt)
        grade = json.loads(response)

        logger.info(f"Correctness score: {grade['score']}")

        return {
            "key": "correctness",
            "score": grade["score"],
            "reason": grade["reasoning"]
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse evaluator response: {e}")
        return {
            "key": "correctness",
            "score": 0,
            "reason": f"Evaluation error: {str(e)}"
        }
