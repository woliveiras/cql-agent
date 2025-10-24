# 🔧 Agente de IA para Reparos Residenciais

Agente de IA especializado em ajudar com pequenos reparos residenciais, construído com LangChain, Ollama e Python.

[![on_push_to_main](https://github.com/woliveiras/cql-agent/actions/workflows/on_push_to_main.yml/badge.svg)](https://github.com/woliveiras/cql-agent/actions/workflows/on_push_to_main.yml)

## ✨ Funcionalidades

- 🤖 Chat interativo para perguntas sobre reparos
- 🏠 Especializado em problemas residenciais
- ⚠️ Alertas de segurança quando necessário
- 💡 Instruções passo a passo
- 🔒 100% local e privado (usando Ollama)
- 🔄 Sistema de tentativas (até 3 tentativas antes de sugerir profissional)
- ✅ Validação de feedback com respostas "sim" ou "não"
- 📝 Histórico de conversação mantido para contexto
- 🎯 Detecção automática de sucesso/falha
- 📚 Base de conhecimento a partir de PDFs
- 🔍 Busca semântica em documentos
- 💾 Armazenamento vetorial com ChromaDB
- 🎯 Respostas baseadas em manuais específicos
- ⚡ Embeddings locais com Ollama
- 🌐 Busca web com DuckDuckGo
- 🔄 Fallback automático: RAG → Web → LLM
- 🆓 Completamente gratuito (sem API keys)
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

## 🚀 Como usar

### 1. Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- UV (gerenciador de pacotes Python)

### 2. Iniciar o Ollama

```bash
# Subir o container do Ollama
docker-compose up -d

# Baixar os modelos (primeira vez)
docker exec -it ollama ollama pull qwen2.5:3b
docker exec -it ollama ollama pull nomic-embed-text
```

### 2.5. Configurar RAG (Opcional, mas recomendado)

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

#### Opção 3: Docker Compose (Deploy Completo)

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

- **Python** - Linguagem de programação
- **UV** - Gerenciador de pacotes e ambientes virtuais
- **LangChain** - Framework para construção de aplicações com LLMs
- **LangChain-Ollama** - Integração do LangChain com Ollama
- **Pydantic** - Validação de dados
- **Ollama** - Execução local de modelos LLM
- **Docker** - Containerização do Ollama
- **FastAPI** - Framework web moderno para API REST
- **Uvicorn** - Servidor ASGI de alta performance
- **ChromaDB** - Banco de dados vetorial para RAG
- **DuckDuckGo** - Busca web gratuita e privada

## 💡 Boas Práticas do Código

Este projeto segue boas práticas de desenvolvimento:

- ✅ **Código limpo**: Comentários apenas onde agregam valor real
- ✅ **Type hints**: Tipagem estática com Pydantic
- ✅ **Documentação**: Docstrings significativas em funções principais
- ✅ **Modularização**: Código organizado em módulos (prompts, rag, tools, api)
- ✅ **Validação**: Validação de entrada/saída com Pydantic
- ✅ **Logging**: Sistema de logs estruturado
- ✅ **Containerização**: Deploy completo com Docker Compose

## 📁 Estrutura do Projeto

```text
cql-agent/
├── agents/                    # 🤖 Agentes de IA
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
│   ├── test_api.py            # Testes da API
│   ├── README.md
│   └── security/              # 🛡️ Módulo de segurança
│       ├── __init__.py
│       ├── sanitizer.py       # Sanitização de entrada
│       ├── guardrails.py      # Validação de conteúdo com SpaCy
│       ├── test_security.py   # Testes unitários
│       ├── test_api_security.py  # Testes de integração
│       └── README.md          # Documentação de segurança
├── openwebui/                 # 🎨 Integração OpenWebUI
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

### Testes de Segurança

```bash
# Testes unitários
pytest security/test_security.py -v

# Testes de integração (API deve estar rodando)
python security/test_api_security.py
```

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
