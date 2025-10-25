"""
Embeddings Factory - Cria instâncias de embeddings de acordo com o provedor configurado
"""

from typing import Optional
from langchain_core.embeddings import Embeddings

from .config import EmbeddingProvider, LLMConfig


class EmbeddingsFactory:
    """Factory para criar instâncias de embeddings de diferentes provedores"""
    
    @staticmethod
    def create_embeddings(
        provider: Optional[EmbeddingProvider] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Embeddings:
        """
        Cria uma instância de embeddings baseada no provedor especificado
        
        Args:
            provider: Provedor de embeddings (usa EMBEDDING_PROVIDER do ambiente se None)
            model: Nome do modelo de embeddings (usa padrão do provedor se None)
            **kwargs: Argumentos adicionais específicos do provedor
            
        Returns:
            Instância de embeddings do provedor especificado
            
        Raises:
            ValueError: Se provedor não for suportado ou configuração estiver incorreta
            ImportError: Se biblioteca do provedor não estiver instalada
        """
        if provider is None:
            provider = LLMConfig.get_embedding_provider()
        
        if provider == EmbeddingProvider.OLLAMA:
            return EmbeddingsFactory._create_ollama_embeddings(
                model=model or LLMConfig.OLLAMA_EMBEDDING_MODEL,
                **kwargs
            )
        
        elif provider == EmbeddingProvider.OPENAI:
            # Valida API key antes de criar
            if not LLMConfig.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY não configurada. "
                    "Defina a variável de ambiente OPENAI_API_KEY."
                )
            return EmbeddingsFactory._create_openai_embeddings(
                model=model or LLMConfig.OPENAI_EMBEDDING_MODEL,
                **kwargs
            )
        
        elif provider == EmbeddingProvider.GEMINI:
            # Valida API key antes de criar
            if not LLMConfig.GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY não configurada. "
                    "Defina a variável de ambiente GEMINI_API_KEY."
                )
            return EmbeddingsFactory._create_gemini_embeddings(
                model=model or LLMConfig.GEMINI_EMBEDDING_MODEL,
                **kwargs
            )
        
        else:
            raise ValueError(f"Provedor de embeddings não suportado: {provider}")
    
    @staticmethod
    def _create_ollama_embeddings(
        model: str,
        **kwargs
    ) -> Embeddings:
        """Cria instância do OllamaEmbeddings"""
        try:
            from langchain_ollama import OllamaEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-ollama não está instalado. "
                "Instale com: pip install langchain-ollama"
            )
        
        base_url = kwargs.pop("base_url", LLMConfig.OLLAMA_BASE_URL)
        
        return OllamaEmbeddings(
            model=model,
            base_url=base_url,
            **kwargs
        )
    
    @staticmethod
    def _create_openai_embeddings(
        model: str,
        **kwargs
    ) -> Embeddings:
        """Cria instância do OpenAIEmbeddings"""
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-openai não está instalado. "
                "Instale com: pip install langchain-openai"
            )
        
        api_key = kwargs.pop("api_key", LLMConfig.OPENAI_API_KEY)
        base_url = kwargs.pop("base_url", LLMConfig.OPENAI_BASE_URL)
        
        embeddings_kwargs = {
            "model": model,
            "api_key": api_key,
            **kwargs
        }
        
        # Adiciona base_url apenas se configurado
        if base_url:
            embeddings_kwargs["base_url"] = base_url
        
        return OpenAIEmbeddings(**embeddings_kwargs)
    
    @staticmethod
    def _create_gemini_embeddings(
        model: str,
        **kwargs
    ) -> Embeddings:
        """Cria instância do GoogleGenerativeAIEmbeddings"""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-google-genai não está instalado. "
                "Instale com: pip install langchain-google-genai"
            )
        
        api_key = kwargs.pop("google_api_key", LLMConfig.GEMINI_API_KEY)
        
        return GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key,
            **kwargs
        )
