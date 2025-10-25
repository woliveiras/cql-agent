"""
LLM Factory - Cria instâncias de LLM de acordo com o provedor configurado
"""

from typing import Optional
from langchain_core.language_models import BaseChatModel

from .config import LLMProvider, LLMConfig


class LLMFactory:
    """Factory para criar instâncias de LLM de diferentes provedores"""
    
    @staticmethod
    def create_llm(
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        Cria uma instância de LLM baseada no provedor especificado
        
        Args:
            provider: Provedor de LLM (usa LLM_PROVIDER do ambiente se None)
            model: Nome do modelo (usa padrão do provedor se None)
            temperature: Temperatura do modelo (usa LLM_TEMPERATURE se None)
            max_tokens: Máximo de tokens (usa LLM_MAX_TOKENS se None)
            **kwargs: Argumentos adicionais específicos do provedor
            
        Returns:
            Instância do chat model do provedor especificado
            
        Raises:
            ValueError: Se provedor não for suportado ou configuração estiver incorreta
            ImportError: Se biblioteca do provedor não estiver instalada
        """
        if provider is None:
            provider = LLMConfig.get_provider()
        
        # Valida configuração antes de criar
        LLMConfig.validate_config(provider)
        
        # Usa valores padrão se não especificado
        temperature = temperature if temperature is not None else LLMConfig.LLM_TEMPERATURE
        max_tokens = max_tokens if max_tokens is not None else LLMConfig.LLM_MAX_TOKENS
        
        if provider == LLMProvider.OLLAMA:
            return LLMFactory._create_ollama_llm(
                model=model or LLMConfig.OLLAMA_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == LLMProvider.OPENAI:
            return LLMFactory._create_openai_llm(
                model=model or LLMConfig.OPENAI_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == LLMProvider.GEMINI:
            return LLMFactory._create_gemini_llm(
                model=model or LLMConfig.GEMINI_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == LLMProvider.ANTHROPIC:
            return LLMFactory._create_anthropic_llm(
                model=model or LLMConfig.ANTHROPIC_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        else:
            raise ValueError(f"Provedor não suportado: {provider}")
    
    @staticmethod
    def _create_ollama_llm(
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> BaseChatModel:
        """Cria instância do ChatOllama"""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError(
                "langchain-ollama não está instalado. "
                "Instale com: pip install langchain-ollama"
            )
        
        base_url = kwargs.pop("base_url", LLMConfig.OLLAMA_BASE_URL)
        
        return ChatOllama(
            model=model,
            temperature=temperature,
            num_predict=max_tokens,
            base_url=base_url,
            **kwargs
        )
    
    @staticmethod
    def _create_openai_llm(
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> BaseChatModel:
        """Cria instância do ChatOpenAI"""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai não está instalado. "
                "Instale com: pip install langchain-openai"
            )
        
        api_key = kwargs.pop("api_key", LLMConfig.OPENAI_API_KEY)
        base_url = kwargs.pop("base_url", LLMConfig.OPENAI_BASE_URL)
        
        llm_kwargs = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "api_key": api_key,
            **kwargs
        }
        
        # Adiciona base_url apenas se configurado (para compatibilidade com APIs alternativas)
        if base_url:
            llm_kwargs["base_url"] = base_url
        
        return ChatOpenAI(**llm_kwargs)
    
    @staticmethod
    def _create_gemini_llm(
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> BaseChatModel:
        """Cria instância do ChatGoogleGenerativeAI"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "langchain-google-genai não está instalado. "
                "Instale com: pip install langchain-google-genai"
            )
        
        api_key = kwargs.pop("google_api_key", LLMConfig.GEMINI_API_KEY)
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def _create_anthropic_llm(
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> BaseChatModel:
        """Cria instância do ChatAnthropic"""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError(
                "langchain-anthropic não está instalado. "
                "Instale com: pip install langchain-anthropic"
            )
        
        api_key = kwargs.pop("anthropic_api_key", LLMConfig.ANTHROPIC_API_KEY)
        
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            anthropic_api_key=api_key,
            **kwargs
        )
