"""
Tests for configuration module.
"""

import pytest
from src.config import Config


def test_config_attributes_exist():
    """Test that all required config attributes exist."""
    assert hasattr(Config, 'OLLAMA_BASE_URL')
    assert hasattr(Config, 'LANGSMITH_API_KEY')
    assert hasattr(Config, 'RAG_MODEL_NAME')
    assert hasattr(Config, 'EVALUATOR_MODEL_NAME')
    assert hasattr(Config, 'EMBEDDINGS_MODEL_NAME')


def test_config_paths_exist():
    """Test that config paths are properly set."""
    assert Config.PROJECT_ROOT.exists()
    assert Config.DATA_DIR.exists()
    assert Config.MODELS_DIR.exists()
    assert Config.LOGS_DIR.exists()


def test_config_chunk_settings():
    """Test that chunk settings are reasonable."""
    assert Config.CHUNK_SIZE > 0
    assert Config.CHUNK_OVERLAP >= 0
    assert Config.CHUNK_OVERLAP < Config.CHUNK_SIZE


def test_config_retrieval_settings():
    """Test retrieval configuration."""
    assert Config.RETRIEVAL_K > 0
    assert isinstance(Config.RETRIEVAL_K, int)
