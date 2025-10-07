"""
Evaluator modules for RAG system assessment.

This package contains specialized evaluators for multi-dimensional assessment:
- Correctness: Answer vs reference answer
- Relevance: Answer vs question
- Groundedness: Answer vs retrieved documents
- Retrieval Relevance: Documents vs question
"""

from src.evaluators.correctness import correctness_evaluator
from src.evaluators.relevance import relevance_evaluator
from src.evaluators.groundedness import groundedness_evaluator
from src.evaluators.retrieval_relevance import retrieval_relevance_evaluator

__all__ = [
    "correctness_evaluator",
    "relevance_evaluator",
    "groundedness_evaluator",
    "retrieval_relevance_evaluator"
]
