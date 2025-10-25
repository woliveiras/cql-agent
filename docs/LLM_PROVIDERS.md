# 🔌 Guia de Provedores LLM

Este documento explica como configurar e usar diferentes provedores de LLM (Large Language Models) no CQL Agent.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Provedores Suportados](#provedores-suportados)
  - [Ollama (Local)](#ollama-local)
  - [OpenAI](#openai)
  - [Google Gemini](#google-gemini)
  - [Anthropic (Claude)](#anthropic-claude)
- [Configuração](#configuração)
- [Migração entre Provedores](#migração-entre-provedores)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O CQL Agent foi projetado para ser **agnóstico de provedor**, permitindo que você escolha o LLM que melhor se adequa às suas necessidades:

- **Privacidade**: Use Ollama para processamento 100% local
- **Qualidade**: Use OpenAI/Gemini/Claude para respostas de alta qualidade
- **Custo**: Use Ollama (gratuito) ou Gemini Free Tier
- **Flexibilidade**: Misture provedores (ex: Ollama para LLM, OpenAI para embeddings)

## 🏗️ Arquitetura

### Factory Pattern

O projeto usa o **Factory Pattern** para abstrair a criação de LLMs:

```python
from agents.llm import LLMFactory, EmbeddingsFactory

# Cria LLM baseado em variável de ambiente LLM_PROVIDER
llm = LLMFactory.create_llm()

# Cria embeddings baseado em EMBEDDING_PROVIDER
embeddings = EmbeddingsFactory.create_embeddings()
```

### Componentes Principais

```text
agents/llm/
├── __init__.py              # LLMProvider, EmbeddingProvider, LLMConfig
├── factory.py               # LLMFactory (cria chat models)
└── embeddings_factory.py    # EmbeddingsFactory (cria embeddings)
```

### Fluxo de Configuração

1. **Leitura de variáveis de ambiente** (`.env`)
2. **Validação de configuração** (chaves API, modelos)
3. **Instanciação do provedor** (via factory)
4. **Uso transparente** (mesmo código para todos os provedores)

## 🔌 Provedores Suportados

### Ollama (Local)

**✅ Vantagens:**

- 100% gratuito
- 100% privado (dados não saem da sua máquina)
- Sem necessidade de API keys
- Funciona offline
- Vários modelos disponíveis

**❌ Desvantagens:**

- Requer recursos computacionais (RAM, GPU opcional)
- Velocidade depende do hardware
- Qualidade pode ser inferior a modelos comerciais

**📦 Instalação:**

```bash
# Já incluído nas dependências padrão
uv sync

# Iniciar Ollama via Docker
docker-compose up -d ollama

# Baixar modelos
docker exec -it ollama ollama pull qwen2.5:3b
docker exec -it ollama ollama pull nomic-embed-text
```

**⚙️ Configuração (.env):**

```bash
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

**🎯 Modelos Recomendados:**

| Modelo | Tamanho | RAM Necessária | Uso |
|--------|---------|----------------|-----|
| `qwen2.5:3b` | 3B | 4GB | Padrão, rápido |
| `qwen2.5:7b` | 7B | 8GB | Melhor qualidade |
| `llama3.2:3b` | 3B | 4GB | Alternativa |
| `mistral:7b` | 7B | 8GB | Boa qualidade |
| `nomic-embed-text` | - | 1GB | Embeddings |

### OpenAI

**✅ Vantagens:**

- Alta qualidade de respostas
- Velocidade rápida
- API confiável e estável
- Bons embeddings

**❌ Desvantagens:**

- Pago (custo por token)
- Dados enviados para servidores da OpenAI
- Requer API key

**📦 Instalação:**

```bash
# Instalar dependência opcional
uv sync --extra openai
```

**🔑 Obter API Key:**

1. Acesse: <https://platform.openai.com/api-keys>
2. Crie uma nova chave (ou use existente)
3. Copie e guarde em local seguro

**⚙️ Configuração (.env):**

```bash
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai

OPENAI_API_KEY=sk-proj-...  # Sua chave aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Opcional: custom base URL (para APIs compatíveis)
# OPENAI_BASE_URL=https://api.openai.com/v1
```

**🎯 Modelos Recomendados:**

| Modelo | Custo (1M tokens) | Velocidade | Uso |
|--------|-------------------|------------|-----|
| `gpt-4o-mini` | $0.15 / $0.60 | Rápido | ⭐ Padrão |
| `gpt-4o` | $2.50 / $10.00 | Médio | Alta qualidade |
| `gpt-3.5-turbo` | $0.50 / $1.50 | Muito rápido | Econômico |
| `text-embedding-3-small` | $0.02 | Rápido | Embeddings |
| `text-embedding-3-large` | $0.13 | Rápido | Embeddings HD |

**💰 Estimativa de Custo:**

Para um chat típico de reparo residencial:

- Mensagem média: ~500 tokens (input + output)
- 100 conversas: ~50,000 tokens
- Custo estimado com GPT-4o-mini: **~$0.04**

### Google Gemini

**✅ Vantagens:**

- Free tier generoso (15 requisições/minuto)
- Alta qualidade de respostas
- Velocidade rápida
- Ótimos embeddings

**❌ Desvantagens:**

- Dados enviados para servidores do Google
- Limite de requisições no free tier
- API menos madura que OpenAI

**📦 Instalação:**

```bash
# Instalar dependência opcional
uv sync --extra google
```

**🔑 Obter API Key:**

1. Acesse: <https://makersuite.google.com/app/apikey>
2. Crie uma nova chave (ou use existente)
3. Copie e guarde em local seguro

**⚙️ Configuração (.env):**

```bash
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini

GEMINI_API_KEY=AIza...  # Sua chave aqui
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001
```

**🎯 Modelos Recomendados:**

| Modelo | Custo | Free Tier | Uso |
|--------|-------|-----------|-----|
| `gemini-1.5-flash` | $0.35/$1.05 | ✅ 15 req/min | ⭐ Padrão |
| `gemini-1.5-pro` | $3.50/$10.50 | ✅ 2 req/min | Alta qualidade |
| `models/embedding-001` | Gratuito | ✅ Sim | Embeddings |

### Anthropic (Claude)

**✅ Vantagens:**

- Altíssima qualidade de respostas
- Excelente para raciocínio complexo
- Contexto longo (200k tokens)
- Seguro e confiável

**❌ Desvantagens:**

- Mais caro que OpenAI
- Não possui embeddings próprios
- Requer API key paga

**📦 Instalação:**

```bash
# Instalar dependência opcional
uv sync --extra anthropic

# Como Anthropic não tem embeddings, instale também outro provedor
uv sync --extra anthropic --extra openai
```

**🔑 Obter API Key:**

1. Acesse: <https://console.anthropic.com/settings/keys>
2. Crie uma nova chave
3. Copie e guarde em local seguro

**⚙️ Configuração (.env):**

```bash
LLM_PROVIDER=anthropic
EMBEDDING_PROVIDER=openai  # Ou ollama/gemini

ANTHROPIC_API_KEY=sk-ant-...  # Sua chave aqui
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Configure também o provedor de embeddings
OPENAI_API_KEY=sk-proj-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**🎯 Modelos Recomendados:**

| Modelo | Custo (1M tokens) | Contexto | Uso |
|--------|-------------------|----------|-----|
| `claude-3-5-sonnet-20241022` | $3.00 / $15.00 | 200k | ⭐ Padrão |
| `claude-3-5-haiku-20241022` | $0.80 / $4.00 | 200k | Econômico |
| `claude-3-opus-20240229` | $15.00 / $75.00 | 200k | Máxima qualidade |

## ⚙️ Configuração

### Arquivo .env Completo

```bash
# ============================================================
# PROVEDOR PRINCIPAL
# ============================================================
LLM_PROVIDER=ollama  # ollama, openai, gemini, anthropic

# Provedor de embeddings (pode ser diferente do LLM)
EMBEDDING_PROVIDER=ollama

# Configurações gerais
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=500

# ============================================================
# OLLAMA
# ============================================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# ============================================================
# OPENAI
# ============================================================
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ============================================================
# GOOGLE GEMINI
# ============================================================
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001

# ============================================================
# ANTHROPIC
# ============================================================
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Validação de Configuração

O sistema valida automaticamente:

```python
from agents.llm import LLMConfig

# Valida provedor atual
LLMConfig.validate_config()

# Valida provedor específico
LLMConfig.validate_config(provider=LLMProvider.OPENAI)
```

## 🔄 Migração entre Provedores

### Cenário 1: Desenvolvimento Local → Produção Cloud

**Desenvolvimento (Ollama):**

```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
```

**Produção (OpenAI):**

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### Cenário 2: Provedor Híbrido

Use LLM comercial + embeddings locais:

```bash
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=ollama

OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Checklist de Migração

Caso você mude de provedor, siga este checklist:

- [ ] Instalar dependências do novo provedor (`uv sync --extra <provider>`)
- [ ] Obter API key (se necessário)
- [ ] Atualizar `.env` com novas configurações
- [ ] Testar com `uv run python api/app.py` ou CLI
- [ ] Recriar RAG se mudar provedor de embeddings (`uv run scripts/setup_rag.py`)
- [ ] Validar custos (se API paga)

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY não configurada"

**Solução:** Configure a variável no `.env`:

```bash
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

### Erro: "Import langchain_openai could not be resolved"

**Solução:** Instale a dependência opcional:

```bash
uv sync --extra openai
```

### Erro: "Ollama connection refused"

**Solução:** Certifique-se que o Ollama está rodando:

```bash
docker-compose up -d ollama
docker ps | grep ollama
```

### Erro: "Rate limit exceeded" (Gemini)

**Solução:** Você ultrapassou o free tier (15 req/min). Espere 1 minuto ou:

```bash
# Adicione delays entre requisições
LLM_TEMPERATURE=0.3  # Menor = mais consistente
```

### Erro: "Vector store incompatível" após mudar embedding provider

**Solução:** Recrie o banco vetorial:

```bash
# Backup (opcional)
mv chroma_db chroma_db.bak

# Recriar com novo provedor
uv run scripts/setup_rag.py
```

### Performance Lenta com Ollama

**Soluções:**

1. Use modelo menor: `qwen2.5:3b` ao invés de `7b`
2. Se tiver GPU NVIDIA, configure CUDA:

   ```bash
   docker-compose down
   # Edite docker-compose.yml para usar GPU
   docker-compose up -d
   ```

3. Reduza `num_predict`:

   ```bash
   LLM_MAX_TOKENS=300  # Ao invés de 500
   ```

## 📚 Recursos Adicionais

- [LangChain Docs](https://python.langchain.com/docs/integrations/llms/)
- [Ollama Library](https://ollama.com/library)
- [OpenAI Platform](https://platform.openai.com/docs)
- [Google AI Studio](https://ai.google.dev/)
- [Anthropic Docs](https://docs.anthropic.com/)
