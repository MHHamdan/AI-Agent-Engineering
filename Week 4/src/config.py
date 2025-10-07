"""
Configuration Module

Centralized configuration management for the EU AI Act RAG system.
Provides type-safe configuration with validation and environment variable loading.
Implements singleton pattern for consistent configuration access across modules.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """
    Application configuration container with type-safe settings.

    Manages all system configuration including:
    - Model selection and hyperparameters
    - Document processing parameters
    - Retrieval configuration
    - External service endpoints
    - Performance and timeout settings

    All settings are class-level constants for memory efficiency and thread safety.
    Environment variables override defaults where applicable.
    """

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    MODELS_DIR = PROJECT_ROOT / "models"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Create directories if they don't exist
    DATA_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # Document paths
    EU_AI_ACT_PDF = PROJECT_ROOT / "eu_ai_act.pdf"

    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # LangSmith Configuration (Optional Observability)
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "AI-Act-RAG-System")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

    # Model Configuration
    # qwen2.5:14b provides superior instruction following and context retention
    RAG_MODEL_NAME: str = "qwen2.5:14b"
    RAG_MODEL_TEMPERATURE: float = 0.0  # Deterministic output for consistency

    # Evaluator Model Configuration
    EVALUATOR_MODEL_NAME: str = "qwen2.5:14b"
    EVALUATOR_MODEL_TEMPERATURE: float = 0.0  # Zero temperature for reproducible evaluation

    # Embedding Model Configuration
    EMBEDDINGS_MODEL_NAME: str = "mxbai-embed-large"  # Optimized for semantic similarity

    # Document Processing Configuration
    CHUNK_SIZE: int = 2000  # Character count per chunk, balances context vs granularity
    CHUNK_OVERLAP: int = 400  # Overlap prevents context loss at boundaries

    # Retrieval Configuration
    RETRIEVAL_K: int = 6  # Number of top-k documents to retrieve per query

    # Dataset Configuration
    DATASET_NAME: str = "eu-ai-act-rag-evaluation"
    EXPERIMENT_PREFIX: str = "eu-ai-act-rag"

    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = 5  # Maximum reasoning steps before timeout
    AGENT_TIMEOUT: int = 120  # Timeout in seconds for agent execution

    @classmethod
    def validate(cls) -> bool:
        """
        Validates configuration and verifies runtime dependencies.

        Performs health checks on:
        - Ollama service availability
        - Required file existence
        - Model availability

        Returns:
            bool: True if all validations pass

        Raises:
            ValueError: If Ollama service is unreachable
            FileNotFoundError: If required files are missing
        """
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=2)
            if response.status_code != 200:
                raise ValueError(f"Ollama service returned status {response.status_code}")
        except Exception as e:
            raise ValueError(
                f"Failed to connect to Ollama at {cls.OLLAMA_BASE_URL}. "
                f"Ensure Ollama service is running and accessible. "
                f"Error: {str(e)}"
            )

        if not cls.EU_AI_ACT_PDF.exists():
            raise FileNotFoundError(
                f"Required document not found: {cls.EU_AI_ACT_PDF}. "
                f"Ensure eu_ai_act.pdf exists in project root."
            )

        return True

    @classmethod
    def get_langsmith_env(cls) -> dict:
        """
        Constructs LangSmith environment variable dictionary.

        Returns:
            dict: Environment variables for LangSmith integration
        """
        return {
            "LANGSMITH_TRACING": str(cls.LANGSMITH_TRACING).lower(),
            "LANGSMITH_API_KEY": cls.LANGSMITH_API_KEY,
            "LANGSMITH_PROJECT": cls.LANGSMITH_PROJECT,
            "LANGSMITH_ENDPOINT": cls.LANGSMITH_ENDPOINT
        }

    @classmethod
    def setup_environment(cls):
        """
        Initializes runtime environment with configuration values.

        Conditionally sets environment variables based on feature flags.
        Idempotent - safe to call multiple times.
        """
        if cls.LANGSMITH_TRACING:
            for key, value in cls.get_langsmith_env().items():
                os.environ[key] = value


# Initialize environment on module import
Config.setup_environment()
