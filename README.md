# 🔧 Agente de IA para Reparos Residenciais

Agente de IA especializado em ajudar com pequenos reparos residenciais, construído com LangChain, Ollama e Python.

## 📋 Fases do Projeto

### Fase 1 - Agente Básico ✅

Agente básico que responde perguntas usando modelo LLM local.

### Fase 2 - RAG ✅

Sistema de recuperação de informações de PDFs com ChromaDB.

### Fase 3 - Web Search ✅

Busca web com DuckDuckGo como fallback quando RAG não encontra informações.

### Fase 4 - OpenWebUI + API REST ✅

Interface web via OpenWebUI com API Flask documentada (Swagger).

### ✨ Funcionalidades

#### Fase 1 (Agente Básico)

- 🤖 Chat interativo para perguntas sobre reparos
- 🏠 Especializado em problemas residenciais
- ⚠️ Alertas de segurança quando necessário
- 💡 Instruções passo a passo
- 🔒 100% local e privado (usando Ollama)
- 🔄 Sistema de tentativas (até 3 tentativas antes de sugerir profissional)
- ✅ Validação de feedback com respostas "sim" ou "não"
- 📝 Histórico de conversação mantido para contexto
- 🎯 Detecção automática de sucesso/falha

#### Fase 2 (RAG)

- 📚 Base de conhecimento a partir de PDFs
- 🔍 Busca semântica em documentos
- 💾 Armazenamento vetorial com ChromaDB
- 🎯 Respostas baseadas em manuais específicos
- ⚡ Embeddings locais com Ollama

#### Fase 3 (Web Search)

- 🌐 Busca web com DuckDuckGo
- 🔄 Fallback automático: RAG → Web → LLM
- 🆓 Completamente gratuito (sem API keys)
- 🇧🇷 Resultados em português (região br-pt)

#### Fase 4 (API + OpenWebUI)

- 🌐 API REST com Flask
- 📖 Documentação Swagger automática
- 🔌 Pipe Function para OpenWebUI
- 🐳 Docker Compose para deploy completo
- 🔄 Gerenciamento de sessões
- 🎨 Interface web moderna
- 🔒 Privacidade mantida (DuckDuckGo não rastreia)

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

### 2.5. Configurar RAG (Opcional - Fase 2)

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

#### Opção 2: API REST (Fase 4)

```bash
# Iniciar API Flask
uv run python -m api.app

# Acessar documentação Swagger
# http://localhost:5000/docs

# Testar API
uv run python test_api.py
```

#### Opção 3: Docker Compose (Deploy Completo)

```bash
# Iniciar todos os serviços (Ollama + API + OpenWebUI)
docker-compose up -d

# Acessar OpenWebUI
# http://localhost:8080
```

## 💬 Exemplo de uso

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

## 📁 Estrutura do Projeto

```text
cql-agent/
├── agent.py              # Código principal do agente
├── prompts/              # Módulo de prompts organizados
│   ├── __init__.py
│   ├── base.py
│   ├── states.py
│   ├── messages.py
│   └── README.md
├── rag/                  # Módulo RAG
│   ├── __init__.py
│   ├── loader.py         # Carrega e processa PDFs
│   ├── vectorstore.py    # Gerencia ChromaDB
│   └── retriever.py      # Busca documentos
├── tools/                # Ferramentas do agente
│   ├── __init__.py
│   └── web_search.py     # Busca web (DuckDuckGo)
├── api/                  # API REST (Fase 4)
│   ├── __init__.py
│   └── app.py            # Flask API + Swagger
├── openwebui/            # Integração OpenWebUI
│   └── pipe.py           # Pipe Function
├── scripts/              # Scripts auxiliares
│   └── setup_rag.py      # Processa PDFs e cria base
├── docs/                 # Documentação detalhada
│   ├── FASE_2_COMPLETA.md
│   ├── FASE_3_COMPLETA.md
│   ├── FASE_4_COMPLETA.md
│   └── README_API.md
├── pdfs/                 # PDFs de conhecimento (adicionar aqui)
│   └── README.md
├── chroma_db/            # Base vetorial (gerado automaticamente)
├── docker-compose.yml    # Deploy completo (Ollama + API + OpenWebUI)
├── Dockerfile.api        # Docker para API
├── test_api.py           # Testes da API
├── pyproject.toml        # Dependências
└── README.md             # Este arquivo
```

## 🔄 Status do Projeto

- ✅ **Fase 1**: Agente básico (Concluída)
- ✅ **Fase 2**: RAG com base de conhecimento (Concluída)
- ✅ **Fase 3**: Busca web com DuckDuckGo (Concluída)
- ✅ **Fase 4**: API REST + OpenWebUI (Concluída)

## 📚 Documentação Adicional

- [API REST](docs/README_API.md) - Guia completo da API Flask
- [Fase 2 - RAG](docs/FASE_2_COMPLETA.md) - Implementação do RAG
- [Fase 3 - Web Search](docs/FASE_3_COMPLETA.md) - Busca web
- [Fase 4 - OpenWebUI](docs/FASE_4_COMPLETA.md) - API + Interface web

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
