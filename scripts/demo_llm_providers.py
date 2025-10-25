#!/usr/bin/env python
"""
Exemplo de uso da camada de provedores LLM
Demonstra como usar diferentes provedores de forma transparente
"""

import os
import sys
from pathlib import Path

# Adicionar path raiz ao sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.llm import LLMFactory, EmbeddingsFactory, LLMProvider, LLMConfig


def exemplo_basico():
    """Exemplo básico: usar provedor configurado em .env"""
    print("=" * 60)
    print("📌 Exemplo 1: Provedor Padrão (.env)")
    print("=" * 60)
    
    # Lê provedor do .env
    provider = LLMConfig.get_provider()
    print(f"\n✅ Provedor configurado: {provider.value}")
    
    # Cria LLM automaticamente
    llm = LLMFactory.create_llm()
    print(f"✅ LLM criado: {type(llm).__name__}")
    
    # Teste simples
    response = llm.invoke("Diga 'Olá' em uma palavra")
    print(f"✅ Resposta: {response.content}")


def exemplo_especifico():
    """Exemplo: especificar provedor manualmente"""
    print("\n" + "=" * 60)
    print("📌 Exemplo 2: Provedor Específico")
    print("=" * 60)
    
    # Forçar uso de Ollama (se disponível)
    try:
        llm = LLMFactory.create_llm(
            provider=LLMProvider.OLLAMA,
            model="qwen2.5:3b",
            temperature=0.5,
            max_tokens=50
        )
        print(f"\n✅ Ollama LLM criado: {type(llm).__name__}")
        print(f"   Modelo: qwen2.5:3b")
        print(f"   Temperature: 0.5")
        
    except Exception as e:
        print(f"\n⚠️  Ollama não disponível: {e}")


def exemplo_embeddings():
    """Exemplo: criar embeddings"""
    print("\n" + "=" * 60)
    print("📌 Exemplo 3: Embeddings")
    print("=" * 60)
    
    embedding_provider = LLMConfig.get_embedding_provider()
    print(f"\n✅ Provedor de embeddings: {embedding_provider.value}")
    
    # Cria embeddings
    embeddings = EmbeddingsFactory.create_embeddings()
    print(f"✅ Embeddings criadas: {type(embeddings).__name__}")
    
    # Teste
    text = "Como consertar uma torneira"
    vector = embeddings.embed_query(text)
    print(f"✅ Embedding gerado: {len(vector)} dimensões")
    print(f"   Primeiros valores: {vector[:5]}")


def exemplo_hibrido():
    """Exemplo: usar provedores diferentes para LLM e embeddings"""
    print("\n" + "=" * 60)
    print("📌 Exemplo 4: Configuração Híbrida")
    print("=" * 60)
    
    llm_provider = LLMConfig.get_provider()
    emb_provider = LLMConfig.get_embedding_provider()
    
    print(f"\n✅ LLM Provider: {llm_provider.value}")
    print(f"✅ Embedding Provider: {emb_provider.value}")
    
    if llm_provider != emb_provider:
        print("\n💡 Você está usando provedores diferentes!")
        print("   Isso é útil para:")
        print("   - LLM comercial (ex: OpenAI) + Embeddings locais (Ollama)")
        print("   - LLM local (Ollama) + Embeddings comerciais (OpenAI)")


def exemplo_validacao():
    """Exemplo: validação de configuração"""
    print("\n" + "=" * 60)
    print("📌 Exemplo 5: Validação de Configuração")
    print("=" * 60)
    
    provider = LLMConfig.get_provider()
    
    try:
        LLMConfig.validate_config()
        print(f"\n✅ Configuração de {provider.value} está válida!")
        
        # Mostra configurações relevantes
        if provider == LLMProvider.OLLAMA:
            print(f"   Base URL: {LLMConfig.OLLAMA_BASE_URL}")
            print(f"   Modelo: {LLMConfig.OLLAMA_MODEL}")
        elif provider == LLMProvider.OPENAI:
            print(f"   Modelo: {LLMConfig.OPENAI_MODEL}")
            print(f"   API Key: {'✅ Configurada' if LLMConfig.OPENAI_API_KEY else '❌ Faltando'}")
        elif provider == LLMProvider.GEMINI:
            print(f"   Modelo: {LLMConfig.GEMINI_MODEL}")
            print(f"   API Key: {'✅ Configurada' if LLMConfig.GEMINI_API_KEY else '❌ Faltando'}")
        elif provider == LLMProvider.ANTHROPIC:
            print(f"   Modelo: {LLMConfig.ANTHROPIC_MODEL}")
            print(f"   API Key: {'✅ Configurada' if LLMConfig.ANTHROPIC_API_KEY else '❌ Faltando'}")
            
    except ValueError as e:
        print(f"\n❌ Configuração inválida: {e}")


def main():
    """Executa todos os exemplos"""
    print("\n🔧 CQL Agent - Exemplos de Provedores LLM\n")
    
    try:
        exemplo_basico()
        exemplo_especifico()
        exemplo_embeddings()
        exemplo_hibrido()
        exemplo_validacao()
        
        print("\n" + "=" * 60)
        print("✅ Todos os exemplos executados com sucesso!")
        print("=" * 60)
        print("\n💡 Dica: Edite o arquivo .env para testar outros provedores")
        print("   Veja: docs/LLM_PROVIDERS.md para mais informações\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
