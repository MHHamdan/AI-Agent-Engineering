"""
Relevance Evaluator

Evaluates if the generated answer is relevant to the input question.
"""

from typing_extensions import Annotated, TypedDict
from langchain_ollama import OllamaLLM
from langsmith.schemas import Run, Example
from src.config import Config
import logging
import json

logger = logging.getLogger(__name__)


class RelevanceGrade(TypedDict):
    """Schema for relevance evaluation results."""
    score: Annotated[int, ..., "Relevance score: 0 (not relevant) or 1 (relevant)"]
    reasoning: Annotated[str, ..., "Explanation for the relevance score"]


# Instructions for the relevance evaluator
RELEVANCE_INSTRUCTIONS = """You are evaluating whether an answer is relevant to an EU AI Act compliance question.

Assess if the generated answer directly addresses the question asked:
- Score 1 (Relevant): The answer directly addresses the question and provides pertinent information
- Score 0 (Not Relevant): The answer is off-topic, doesn't address the question, or provides unrelated information

Provide:
1. A score (0 or 1)
2. Clear reasoning explaining your score

Focus on whether the answer addresses what was actually asked."""


# Initialize the grader LLM (Ollama)
relevance_llm = OllamaLLM(
    model=Config.EVALUATOR_MODEL_NAME,
    temperature=Config.EVALUATOR_MODEL_TEMPERATURE,
    base_url=Config.OLLAMA_BASE_URL,
    format="json"
)


def relevance_evaluator(run: Run, example: Example) -> dict:
    """
    Evaluates if the generated answer is relevant to the input question.

    This evaluator:
    1. Takes the user's question
    2. Takes the generated answer
    3. Determines if the answer actually addresses the question

    Args:
        run: The execution run containing the generated answer
        example: The test example containing the input question

    Returns:
        A dictionary with the score and reasoning
    """
    # Extract the input question
    question = example.inputs.get("question", "")

    # Extract the generated answer
    generated_answer = run.outputs.get("answer", "")

    if not question or not generated_answer:
        logger.warning("Missing question or answer in relevance evaluation")
        return {
            "key": "relevance",
            "score": 0,
            "reason": "Missing question or generated answer"
        }

    # Grade the relevance using the LLM
    prompt = f"""{RELEVANCE_INSTRUCTIONS}

Question: {question}

Generated Answer: {generated_answer}

Respond with JSON only."""

    try:
        response = relevance_llm.invoke(prompt)
        grade = json.loads(response)

        logger.info(f"Relevance score: {grade['score']}")

        return {
            "key": "relevance",
            "score": grade["score"],
            "reason": grade["reasoning"]
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse evaluator response: {e}")
        return {
            "key": "relevance",
            "score": 0,
            "reason": f"Evaluation error: {str(e)}"
        }
