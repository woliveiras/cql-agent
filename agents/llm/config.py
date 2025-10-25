"""
Configurações e Enums para LLM Providers
"""

from enum import Enum
from typing import Optional
import os


class LLMProvider(str, Enum):
    """Provedores de LLM suportados"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class EmbeddingProvider(str, Enum):
    """Provedores de embeddings suportados"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMConfig:
    """Configuração centralizada para LLM providers"""
    
    @staticmethod
    def get_provider() -> LLMProvider:
        """Retorna o provedor configurado via variável de ambiente"""
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        try:
            return LLMProvider(provider)
        except ValueError:
            raise ValueError(
                f"Provedor '{provider}' não suportado. "
                f"Use um dos seguintes: {', '.join([p.value for p in LLMProvider])}"
            )
    
    @staticmethod
    def get_embedding_provider() -> EmbeddingProvider:
        """Retorna o provedor de embeddings configurado"""
        provider = os.getenv("EMBEDDING_PROVIDER", os.getenv("LLM_PROVIDER", "ollama")).lower()
        try:
            return EmbeddingProvider(provider)
        except ValueError:
            raise ValueError(
                f"Provedor de embeddings '{provider}' não suportado. "
                f"Use um dos seguintes: {', '.join([p.value for p in EmbeddingProvider])}"
            )
    
    # Configurações Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # Configurações OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # Para compatibilidade com APIs alternativas
    
    # Configurações Google Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    
    # Configurações Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Configurações gerais de LLM
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
    
    @classmethod
    def validate_config(cls, provider: Optional[LLMProvider] = None) -> None:
        """
        Valida se as configurações necessárias estão presentes
        
        Args:
            provider: Provedor específico para validar, ou None para validar o configurado
            
        Raises:
            ValueError: Se configurações obrigatórias estiverem faltando
        """
        if provider is None:
            provider = cls.get_provider()
        
        if provider == LLMProvider.OPENAI and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY não configurada. "
                "Defina a variável de ambiente OPENAI_API_KEY com sua chave da API OpenAI."
            )
        
        if provider == LLMProvider.GEMINI and not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Defina a variável de ambiente GEMINI_API_KEY com sua chave da API Google."
            )
        
        if provider == LLMProvider.ANTHROPIC and not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY não configurada. "
                "Defina a variável de ambiente ANTHROPIC_API_KEY com sua chave da API Anthropic."
            )
