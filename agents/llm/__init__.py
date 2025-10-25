"""
LLM Provider Manager - Gerencia diferentes provedores de LLM (Ollama, OpenAI, Gemini, etc.)
"""

from .config import LLMProvider, EmbeddingProvider, LLMConfig

from .factory import LLMFactory
from .embeddings_factory import EmbeddingsFactory

__all__ = [
    "LLMProvider",
    "EmbeddingProvider",
    "LLMConfig",
    "LLMFactory",
    "EmbeddingsFactory",
]
