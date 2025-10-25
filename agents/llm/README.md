# 🔌 Módulo LLM - Gerenciamento de Provedores

Este módulo implementa uma camada de abstração para gerenciar diferentes provedores de LLM (Large Language Models) e embeddings.

## 📋 Visão Geral

O módulo `agents/llm` permite que o CQL Agent suporte múltiplos provedores de forma transparente, usando o **Factory Pattern**.

### Provedores Suportados

- **Ollama** - Modelos locais (padrão)
- **OpenAI** - GPT-4, GPT-3.5-turbo, etc
- **Google Gemini** - Gemini 1.5 Flash/Pro
- **Anthropic** - Claude 3.5 Sonnet

## 🏗️ Arquitetura

### Componentes

```text
agents/llm/
├── __init__.py              # Exports principais + enums + configuração
├── factory.py               # LLMFactory - cria chat models
└── embeddings_factory.py    # EmbeddingsFactory - cria embeddings
```

### Factory Pattern

```python
# Uso básico
from agents.llm import LLMFactory, EmbeddingsFactory

# Cria LLM baseado em variável de ambiente
llm = LLMFactory.create_llm()

# Cria embeddings
embeddings = EmbeddingsFactory.create_embeddings()
```

### Fluxo de Criação

```text
┌─────────────────────┐
│  Client Code        │
│  (RepairAgent, etc) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LLMFactory /       │
│  EmbeddingsFactory  │
└──────────┬──────────┘
           │
           ├─ Lê LLM_PROVIDER / EMBEDDING_PROVIDER
           ├─ Valida configuração
           └─ Instancia provedor correto
           │
           ▼
┌─────────────────────┐
│  Chat Model /       │
│  Embeddings         │
└─────────────────────┘
```

## 📦 Componentes Detalhados

### 1. `__init__.py`

**Exports:**

- `LLMProvider` - Enum com provedores de LLM
- `EmbeddingProvider` - Enum com provedores de embeddings
- `LLMConfig` - Classe de configuração estática
- `LLMFactory` - Factory para criar LLMs
- `EmbeddingsFactory` - Factory para criar embeddings

**Exemplo:**

```python
from agents.llm import LLMProvider, LLMConfig

# Obter provedor configurado
provider = LLMConfig.get_provider()

# Validar configuração
LLMConfig.validate_config()

# Acessar configurações
print(LLMConfig.OLLAMA_MODEL)
print(LLMConfig.OPENAI_API_KEY)
```

### 2. `factory.py` - LLMFactory

**Responsabilidades:**

- Criar instâncias de chat models
- Validar configuração antes de criar
- Fornecer mensagens de erro úteis

**Métodos:**

```python
class LLMFactory:
    @staticmethod
    def create_llm(
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseChatModel:
        """Cria LLM do provedor especificado"""
```

**Exemplo:**

```python
from agents.llm import LLMFactory, LLMProvider

# Usar provedor do .env
llm = LLMFactory.create_llm()

# Forçar provedor específico
llm = LLMFactory.create_llm(
    provider=LLMProvider.OPENAI,
    model="gpt-4o-mini",
    temperature=0.7
)
```

### 3. `embeddings_factory.py` - EmbeddingsFactory

**Responsabilidades:**

- Criar instâncias de embeddings
- Suportar provedores diferentes do LLM principal
- Validar API keys

**Métodos:**

```python
class EmbeddingsFactory:
    @staticmethod
    def create_embeddings(
        provider: Optional[EmbeddingProvider] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Embeddings:
        """Cria embeddings do provedor especificado"""
```

**Exemplo:**

```python
from agents.llm import EmbeddingsFactory, EmbeddingProvider

# Usar provedor do .env
embeddings = EmbeddingsFactory.create_embeddings()

# Forçar provedor específico
embeddings = EmbeddingsFactory.create_embeddings(
    provider=EmbeddingProvider.OPENAI,
    model="text-embedding-3-small"
)
```

## ⚙️ Configuração

### Variáveis de Ambiente

Todas as configurações são lidas do arquivo `.env`:

```bash
# Provedor principal
LLM_PROVIDER=ollama  # ollama, openai, gemini, anthropic

# Provedor de embeddings (opcional, usa LLM_PROVIDER se não especificado)
EMBEDDING_PROVIDER=ollama

# Configurações gerais
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=500

# Configurações específicas de cada provedor
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Classe LLMConfig

```python
class LLMConfig:
    """Configuração centralizada para LLM providers"""
    
    @staticmethod
    def get_provider() -> LLMProvider:
        """Retorna provedor de LLM configurado"""
    
    @staticmethod
    def get_embedding_provider() -> EmbeddingProvider:
        """Retorna provedor de embeddings configurado"""
    
    @classmethod
    def validate_config(cls, provider: Optional[LLMProvider] = None) -> None:
        """Valida se configuração está completa"""
        
    # Atributos de classe com todas as configurações
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    # ... etc
```

## 🔄 Integração com Código Existente

```python
from agents.llm import LLMFactory, EmbeddingsFactory

# Cria automaticamente com base em .env
llm = LLMFactory.create_llm()
embeddings = EmbeddingsFactory.create_embeddings()
```

## 🧪 Testes

### Testar Provedor

```bash
# Executar script de demonstração
uv run scripts/demo_llm_providers.py
```

### Testar Manualmente

```python
from agents.llm import LLMFactory, LLMConfig

# Validar configuração
try:
    LLMConfig.validate_config()
    print("✅ Configuração válida")
except ValueError as e:
    print(f"❌ Erro: {e}")

# Criar e testar LLM
llm = LLMFactory.create_llm()
response = llm.invoke("Olá!")
print(response.content)
```

## 🚀 Adicionar Novo Provedor

Para adicionar suporte a um novo provedor (ex: Cohere, HuggingFace):

1. **Adicionar enum em `__init__.py`:**

   ```python
   class LLMProvider(str, Enum):
       # ... existentes ...
       COHERE = "cohere"
   ```

2. **Adicionar configurações em `LLMConfig`:**

   ```python
   COHERE_API_KEY = os.getenv("COHERE_API_KEY")
   COHERE_MODEL = os.getenv("COHERE_MODEL", "command")
   ```

3. **Adicionar método em `factory.py`:**

   ```python
   @staticmethod
   def _create_cohere_llm(...) -> BaseChatModel:
       from langchain_cohere import ChatCohere
       return ChatCohere(...)
   ```

4. **Adicionar caso no `create_llm()`:**

   ```python
   elif provider == LLMProvider.COHERE:
       return LLMFactory._create_cohere_llm(...)
   ```

5. **Adicionar dependência em `pyproject.toml`:**

   ```toml
   [project.optional-dependencies]
   cohere = ["langchain-cohere>=0.1.0"]
   ```

## 📚 Referências

- [LangChain - Model I/O](https://python.langchain.com/docs/modules/model_io/)
- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)
- [Guia Completo de Provedores](../../docs/LLM_PROVIDERS.md)
