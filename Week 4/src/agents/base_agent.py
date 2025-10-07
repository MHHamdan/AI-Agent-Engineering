"""
Base Agent Module

Defines the base class for all agents in the A2A protocol.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the system.

    Agents in the A2A protocol are specialized components that:
    - Have specific roles and responsibilities
    - Can communicate with other agents
    - Maintain state during conversations
    - Provide structured outputs
    """

    def __init__(
        self,
        name: str,
        description: str,
        model_name: str = Config.RAG_MODEL_NAME,
        temperature: float = Config.RAG_MODEL_TEMPERATURE
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique name for this agent
            description: Description of the agent's role
            model_name: LLM model to use
            temperature: Temperature for response generation
        """
        self.name = name
        self.description = description
        self.model_name = model_name
        self.temperature = temperature

        # Initialize the LLM for this agent (Ollama)
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=Config.OLLAMA_BASE_URL
        )

        logger.info(f"Initialized {self.name} agent")

    @abstractmethod
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process inputs and return outputs.

        This method must be implemented by all agent subclasses.

        Args:
            inputs: Dictionary of input data

        Returns:
            Dictionary of output data
        """
        pass

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        return f"""You are {self.name}, a specialized AI agent.

Role: {self.description}

Your responsibilities:
- Focus on your specific area of expertise
- Provide accurate, well-structured information
- Communicate clearly with other agents in the system
- Base your responses on factual information
"""

    def __str__(self) -> str:
        return f"{self.name} ({self.description})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
