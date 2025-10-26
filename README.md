# 🔧 Agente de IA para Reparos Residenciais

Agente de IA especializado em ajudar com pequenos reparos residenciais, construído com LangChain e Python. Suporta múltiplos provedores de LLM: Ollama (local), OpenAI, Google Gemini e Anthropic.

[![on_push_to_main](https://github.com/woliveiras/cql-agent/actions/workflows/on_push_to_main.yml/badge.svg)](https://github.com/woliveiras/cql-agent/actions/workflows/on_push_to_main.yml)

## ✨ Funcionalidades

- 🤖 Chat interativo para perguntas sobre reparos
- 🏠 Especializado em problemas residenciais
- ⚠️ Alertas de segurança quando necessário
- 💡 Instruções passo a passo
- 🎯 **Múltiplos provedores de LLM suportados:**
  - 🔒 **Ollama** - 100% local e privado (padrão)
  - 🌐 **OpenAI** - GPT-4, GPT-3.5-turbo, etc
  - ✨ **Google Gemini** - Gemini 1.5 Flash/Pro
  - 🧠 **Anthropic** - Claude 3.5 Sonnet
- 🔄 Sistema de tentativas (até 3 tentativas antes de sugerir profissional)
- ✅ Validação de feedback com respostas "sim" ou "não"
- 📝 Histórico de conversação mantido para contexto
- 🎯 Detecção automática de sucesso/falha
- 📚 Base de conhecimento a partir de PDFs
- 🔍 Busca semântica em documentos
- 💾 Armazenamento vetorial com ChromaDB
- 🎯 Respostas baseadas em manuais específicos
- ⚡ Embeddings com múltiplos provedores
- 🌐 Busca web com DuckDuckGo
- 🔄 Fallback automático: RAG → Web → LLM
- 🇧🇷 Resultados em português (região br-pt)
- 🌐 API REST com FastAPI
- 📖 Documentação Swagger e ReDoc automáticas
- 🔌 Pipe Function para OpenWebUI
- 🐳 Docker Compose para deploy completo
- 🔄 Gerenciamento de sessões
- 🎨 Interface web moderna
- 🔒 Privacidade mantida (DuckDuckGo não rastreia)
- 🛡️ Segurança reforçada com sanitização e guardrails
- ✅ Validação rigorosa de entrada (Pydantic nativo)
- 🚫 Proteção contra injection (SQL, XSS, Command)
- 🎯 Guardrails de conteúdo (apenas reparos residenciais)
- ⚡ Performance otimizada (async/await)

## 🏗️ Arquitetura

O projeto é dividido em três componentes principais:

1. **Backend (Python + FastAPI)**: API REST com agente de IA, RAG e ferramentas
2. **Frontend (React + TypeScript)**: Interface web moderna para interação
3. **Ollama (Docker)**: Servidor LLM local para processamento

```text
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend   │─────▶│   Ollama    │
│  React/Vite │ HTTP │ FastAPI/LLM │ HTTP │  LLM Local  │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ├──▶ ChromaDB (RAG)
                            └──▶ DuckDuckGo (Web Search)
```

## 🚀 Como usar

### 1. Pré-requisitos

**Backend:**

- Python 3.12+
- UV (gerenciador de pacotes Python)
- Docker e Docker Compose

**Frontend (Opcional):**

- Node.js 18+ ou 20+
- pnpm 10+

### 2. Configurar Provedor de LLM

Copie o arquivo de exemplo e configure seu provedor:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e escolha seu provedor:

#### Opção A: Ollama (Local - Gratuito) ⭐ Padrão

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

Depois, inicie o Ollama:

Se estiver usando o Ollama diretamente em seu S.O., lembre-se de executar o app.

Em seguida, baixe os modelos através do terminal:

```bash
# Baixar os modelos (primeira vez)
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Se estiver usando via Docker, execute:

```bash
# Subir o container do Ollama
docker-compose up -d

# Baixar os modelos (primeira vez)
docker exec -it ollama ollama pull qwen2.5:3b
docker exec -it ollama ollama pull nomic-embed-text
```

#### Opção B: OpenAI

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...  # Sua chave da API OpenAI
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Obtenha sua chave em: <https://platform.openai.com/api-keys>

**Para instalar o suporte OpenAI:**

```bash
uv sync --extra openai
```

#### Opção C: Google Gemini

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=...  # Sua chave da API Gemini
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001
```

Obtenha sua chave em: <https://makersuite.google.com/app/apikey>

**Para instalar o suporte Gemini:**

```bash
uv sync --extra google
```

#### Opção D: Anthropic (Claude)

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...  # Sua chave da API Anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Para embeddings, use um dos outros provedores:
EMBEDDING_PROVIDER=openai  # ou ollama
```

Obtenha sua chave em: <https://console.anthropic.com/settings/keys>

**Para instalar o suporte Anthropic:**

```bash
uv sync --extra anthropic
```

#### Instalar Todos os Provedores

```bash
uv sync --extra all-providers
```

### 3. Configurar RAG

```bash
# 1. Adicionar PDFs na pasta pdfs/
# Coloque manuais sobre reparos residenciais

# 2. Processar PDFs e criar base de conhecimento
uv run scripts/setup_rag.py

# Isso irá criar o banco vetorial em chroma_db/
```

### 3. Instalar dependências

```bash
uv sync
```

### 4. Executar o agente

#### Opção 1: CLI (Linha de Comando)

```bash
# Ativar o ambiente virtual (opcional, uv faz isso automaticamente)
source .venv/bin/activate

# Executar o agente
uv run agent.py
```

#### Opção 2: API REST (FastAPI)

```bash
# Desenvolvimento (com auto-reload)
uv run uvicorn api.app:app --host 0.0.0.0 --port 5000 --reload

# Produção (com múltiplos workers)
uv run uvicorn api.app:app --host 0.0.0.0 --port 5000 --workers 4

# Acessar documentação Swagger
# http://localhost:5000/docs

# Acessar documentação ReDoc
# http://localhost:5000/redoc

# Testar API (script automatizado)
./test_api.sh

# Ou testar manualmente
uv run python test_api.py
```

> 📚 **Guia completo:** Veja [GUIA_DEPLOY.md](docs/GUIA_DEPLOY.md) para mais opções de execução

#### Opção 3: Frontend Web (React)

```bash
# Navegar para a pasta do frontend
cd web

# Instalar dependências (primeira vez)
pnpm install

# Iniciar servidor de desenvolvimento
pnpm dev

# Acessar interface web
# http://localhost:5173
```

> 💡 **Nota:** O frontend requer que a API REST esteja rodando na porta 5000

#### Opção 4: Docker Compose (Deploy Completo)

```bash
# Iniciar todos os serviços (Ollama + API + OpenWebUI)
docker-compose up -d

# Acessar OpenWebUI
# http://localhost:8080
```

Em ambiente local, você pode usar a Pipe Function integrada ao OpenWebUI e desabilitar a autenticação para facilitar os testes.

Para desabilitar autenticação, edite o arquivo `docker-compose.yml` e defina:

```yaml
  - WEBUI_AUTH=false
```

Os detalhes de uso de Pipe Function estão na documentação: [Integração com OpenWebUI](docs/INTEGRACAO_OPENWEBUI.md)

## 💬 Exemplo de uso

Exemplo de interação com o agente via CLI:

```bash
============================================================
🔧 CQL AI Agent - Assistente de Reparos Residenciais
============================================================

Inicializando o agente...


✅ Agente inicializado com sucesso!

💡 Dica: O agente tentará ajudá-lo até 3 vezes antes de sugerir um profissional

📝 Comandos: 'sair' para encerrar | 'novo' para um novo problema

👤 Você: Como posso consertar uma torneira que está pingando?

🤖 Agente: Para consertar uma torneira pingando, siga estes passos:

1. **Feche o registro de água** da torneira
2. Abra a torneira para liberar pressão restante
3. Remova o cabo da torneira
4. Desatarraxe a peça de vedação
5. Substitua o anel de borracha (O-ring) ou a válvula
6. Remonte tudo na ordem inversa
7. Abra o registro novamente

⚠️ **Segurança**: Se não se sentir confortável, chame um encanador!

O problema foi resolvido? Responda com 'sim' ou 'não'.

👤 Você: 
```

## 🛠️ Tecnologias Utilizadas

**Backend:**

- **Python** - Linguagem de programação
- **UV** - Gerenciador de pacotes e ambientes virtuais
- **LangChain** - Framework para construção de aplicações com LLMs
- **Múltiplos provedores LLM:**
  - **LangChain-Ollama** - Modelos locais com Ollama
  - **LangChain-OpenAI** - GPT-4, GPT-3.5-turbo (opcional)
  - **LangChain-Google-GenAI** - Gemini 1.5 Flash/Pro (opcional)
  - **LangChain-Anthropic** - Claude 3.5 Sonnet (opcional)
- **Pydantic** - Validação de dados
- **Docker** - Containerização
- **FastAPI** - Framework web moderno para API REST
- **Uvicorn** - Servidor ASGI de alta performance
- **ChromaDB** - Banco de dados vetorial para RAG
- **DuckDuckGo** - Busca web gratuita e privada

**Frontend:**

- **React** - Biblioteca para interfaces de usuário
- **TypeScript** - JavaScript tipado
- **Vite** - Build tool moderna
- **EmotionCSS** - Styling CSS-in-JS
- **Zustand** - State management
- **React Query** - Data fetching e cache
- **React Router** - Roteamento
- **Vitest** - Framework de testes
- **Biome.js** - Linting e formatação

## 💡 Boas Práticas do Código

Este projeto segue boas práticas de desenvolvimento:

- ✅ **Código limpo**: Comentários apenas onde agregam valor real
- ✅ **Type hints**: Tipagem estática com Pydantic
- ✅ **Documentação**: Docstrings significativas em funções principais
- ✅ **Modularização**: Código organizado em módulos (prompts, rag, tools, api, llm)
- ✅ **Factory Pattern**: Abstração de provedores LLM através de factories
- ✅ **Validação**: Validação de entrada/saída com Pydantic
- ✅ **Logging**: Sistema de logs estruturado
- ✅ **Testes automatizados**: Suíte completa com 136+ testes (unit + integration)
- ✅ **Coverage**: Cobertura de código com pytest-cov
- ✅ **CI/CD**: GitHub Actions com testes automáticos
- ✅ **Containerização**: Deploy completo com Docker Compose

## 🔌 Provedores de LLM Suportados

O projeto suporta múltiplos provedores através de uma camada de abstração:

### Arquitetura de Provedores

```text
┌──────────────────────────────────────────────┐
│           RepairAgent / VectorStore          │
└──────────────────┬───────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │   LLMFactory /     │
         │ EmbeddingsFactory  │
         └─────────┬──────────┘
                   │
     ┌─────────────┼─────────────┬─────────────┐
     ▼             ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Ollama  │  │ OpenAI  │  │ Gemini  │  │Anthropic│
│ (Local) │  │   API   │  │   API   │  │   API   │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### Comparação de Provedores

| Provedor | Custo | Privacidade | Velocidade | Qualidade | Embeddings |
|----------|-------|-------------|------------|-----------|------------|
| **Ollama** | 🟢 Gratuito | 🟢 100% Local | 🟡 Média | 🟢 Boa | ✅ Sim |
| **OpenAI** | 🔴 Pago | 🔴 Cloud | 🟢 Rápida | 🟢 Excelente | ✅ Sim |
| **Gemini** | 🟡 Free Tier | 🔴 Cloud | 🟢 Rápida | 🟢 Excelente | ✅ Sim |
| **Anthropic** | 🔴 Pago | 🔴 Cloud | 🟢 Rápida | 🟢 Excelente | ❌ Não* |

*\* Anthropic não possui embeddings próprios. Use outro provedor para embeddings.*

### Configuração via Variáveis de Ambiente

Toda a configuração é feita através do arquivo `.env`:

```bash
# Escolher provedor principal
LLM_PROVIDER=ollama  # ou openai, gemini, anthropic

# Embeddings podem usar provedor diferente
EMBEDDING_PROVIDER=ollama  # ou openai, gemini

# Configurações específicas do provedor escolhido
OLLAMA_MODEL=qwen2.5:3b
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-1.5-flash
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Custos Estimados (APIs Pagas)

**OpenAI (Novembro 2024):**

- GPT-4o-mini: ~$0.15/$0.60 por 1M tokens (input/output)
- text-embedding-3-small: ~$0.02 por 1M tokens

**Google Gemini:**

- Gemini 1.5 Flash: Gratuito até 15 req/min
- Acima: ~$0.35/$1.05 por 1M tokens

**Anthropic:**

- Claude 3.5 Sonnet: ~$3/$15 por 1M tokens

💡 **Dica:** Para uso pessoal/experimental, Ollama (gratuito) ou Gemini Free Tier são ótimas opções!

## 📁 Estrutura do Projeto

```text
cql-agent/
├── agents/                    # 🤖 Agentes de IA
│   ├── llm/                   # 🔌 Gerenciamento de provedores LLM
│   │   ├── __init__.py        # Enums e configurações
│   │   ├── factory.py         # Factory para criar LLMs
│   │   └── embeddings_factory.py  # Factory para embeddings
│   ├── repair_agent/          # Agente principal de reparos
│   │   ├── __init__.py
│   │   ├── agent.py           # Código principal do agente
│   │   └── prompts/           # Módulo de prompts organizados
│   │       ├── __init__.py
│   │       ├── base.py        # Prompts base do sistema
│   │       ├── states.py      # Estados da conversação
│   │       ├── messages.py    # Templates de mensagens
│   │       └── README.md
│   ├── rag/                   # 📚 Módulo RAG (Retrieval-Augmented Generation)
│   │   ├── __init__.py
│   │   ├── loader.py          # Carrega e processa PDFs
│   │   ├── vectorstore.py     # Gerencia ChromaDB
│   │   ├── retriever.py       # Busca documentos semânticos
│   │   └── pdfs/              # PDFs de exemplo
│   └── tools/                 # 🔧 Ferramentas do agente
│       ├── __init__.py
│       └── web_search.py      # Busca web (DuckDuckGo)
├── api/                       # 🌐 API REST
│   ├── __init__.py
│   ├── app.py                 # FastAPI + Swagger automático
│   ├── gunicorn.conf.py       # Configuração Gunicorn (produção)
│   ├── README.md
│   ├── security/              # 🛡️ Módulo de segurança
│   │   ├── __init__.py
│   │   ├── sanitizer.py       # Sanitização de entrada
│   │   ├── guardrails.py      # Validação de conteúdo com SpaCy
│   │   ├── ner_repair.py      # Named Entity Recognition
│   │   ├── context_analyzer.py  # Análise de contexto sintático
│   │   ├── intention_analyzer.py  # Análise de intenção comunicativa
│   │   └── README.md          # Documentação de segurança
│   └── tests/                 # 🧪 Testes automatizados
│       ├── conftest.py        # Fixtures compartilhadas
│       ├── unit/              # Testes unitários
│       │   └── security/      # Testes de segurança
│       ├── integration/       # Testes de integração
│       └── README.md          # Documentação de testes
├── web/                       # 🎨 Frontend React
│   ├── src/
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── containers/        # Componentes agregadores
│   │   ├── pages/             # Páginas da aplicação
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API clients
│   │   ├── store/             # Zustand stores
│   │   ├── styles/            # Theme e estilos globais
│   │   └── test/              # Setup de testes
│   ├── public/                # Arquivos estáticos
│   ├── package.json
│   ├── vite.config.ts
│   ├── biome.json             # Configuração Biome.js
│   └── README.md              # Documentação do frontend
├── openwebui/                 # 🔌 Integração OpenWebUI
│   └── pipe.py                # Pipe Function
├── scripts/                   # 📜 Scripts auxiliares
│   └── setup_rag.py           # Processa PDFs e cria base
├── docs/                      # 📖 Documentação detalhada
│   ├── GUIA_DEPLOY.md         # Deploy e execução (dev + prod)
│   ├── GUIA_SWAGGER.md        # Documentação Swagger
│   ├── INTEGRACAO_OPENWEBUI.md  # Integração com OpenWebUI
│   └── QUICK_START_RAG.md     # Guia rápido RAG
├── pdfs/                      # 📄 PDFs de conhecimento (adicionar aqui)
│   └── README.md
├── chroma_db/                 # 💾 Base vetorial (gerado automaticamente)
│   └── chroma.sqlite3
├── docker-compose.yml         # 🐳 Deploy completo (Ollama + API)
├── Dockerfile                 # 🐳 Docker para API
├── setup.sh                   # 🚀 Script de setup inicial
├── test_api.sh                # 🧪 Script de testes da API
├── test_security.sh           # 🛡️ Script de testes de segurança
├── pyproject.toml             # 📦 Dependências Python
└── README.md                  # 📘 Este arquivo
```

## 🛡️ Segurança

O projeto implementa múltiplas camadas de segurança:

### 1. Validação de Schema (Pydantic)

- Mensagens: 1-4096 caracteres
- Session ID: alfanumérico com _ e -
- Validação rigorosa de tipos

### 2. Sanitização de Entrada

- Remove caracteres nulos (`\x00`)
- Detecta SQL injection
- Detecta XSS (Cross-Site Scripting)
- Detecta command injection
- Previne DoS por repetição

### 3. Guardrails de Conteúdo

- Valida se mensagem é sobre reparos residenciais
- Bloqueia conteúdo proibido (ilegal, adulto, jailbreak)
- Score de relevância (0.0 a 1.0)
- Validação adicional com LLM

### 4. Tratamento de Erros

- Retorna 400 Bad Request para entrada inválida
- Não vaza detalhes internos
- Logs detalhados para auditoria

### Testes Automatizados

O projeto possui uma suíte completa de testes organizados por tipo:

```bash
# Executar todos os testes
pytest

# Testes unitários (136 testes)
pytest api/tests/unit/ -v

# Testes de integração (API deve estar rodando)
pytest api/tests/integration/ -v

# Testes com cobertura
pytest --cov=api --cov=agents --cov-report=html

# Ver relatório de cobertura
open htmlcov/index.html
```

**Estrutura de testes:**
- **Unit**: Testes de componentes isolados (sanitização, NER, análise de contexto, etc.)
- **Integration**: Testes de fluxos completos da API e segurança

Veja [api/tests/README.md](api/tests/README.md) para documentação completa.

## 🐛 Troubleshooting

### Erro de conexão com Ollama

```bash
❌ Erro: Connection refused
```

**Solução**: Certifique-se que o Ollama está rodando:

```bash
docker-compose ps
docker-compose up -d
```

### Modelo não encontrado

```bash
❌ Erro: model 'qwen2.5:3b' not found
```

**Solução**: Baixe o modelo:

```bash
docker exec -it ollama ollama pull qwen2.5:3b
```

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
