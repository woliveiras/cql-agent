# 🔧 Agente de IA para Reparos Residenciais

Agente de IA especializado em ajudar com pequenos reparos residenciais, construído com LangChain, Ollama e Python.

## 📋 Fase 1 - Agente Básico

Nesta primeira fase, implementamos um agente básico que responde perguntas sobre reparos residenciais usando um modelo LLM local via Ollama.

### ✨ Funcionalidades

- 🤖 Chat interativo para perguntas sobre reparos
- 🏠 Especializado em problemas residenciais
- ⚠️ Alertas de segurança quando necessário
- 💡 Instruções passo a passo
- 🔒 100% local e privado (usando Ollama)
- 🔄 Sistema de tentativas (até 3 tentativas antes de sugerir profissional)
- ✅ Validação de feedback com respostas "sim" ou "não"
- 📝 Histórico de conversação mantido para contexto
- 🎯 Detecção automática de sucesso/falha

## 🚀 Como usar

### 1. Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- UV (gerenciador de pacotes Python)

### 2. Iniciar o Ollama

```bash
# Subir o container do Ollama
docker-compose up -d

# Baixar o modelo (primeira vez)
docker exec -it ollama ollama pull qwen2.5:3b
```

### 3. Instalar dependências

```bash
uv sync
```

### 4. Executar o agente

```bash
# Ativar o ambiente virtual (opcional, uv faz isso automaticamente)
source .venv/bin/activate

# Executar o agente
uv run agent.py
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
│   ├── __init__.py       # Exporta todos os prompts
│   ├── base.py           # Prompt base do sistema
│   ├── states.py         # Prompts por estado
│   ├── messages.py       # Mensagens de resposta
│   └── README.md         # Documentação dos prompts
├── docker-compose.yml    # Configuração do Ollama
├── pyproject.toml        # Dependências do projeto
├── uv.lock              # Lock file das dependências
└── README.md            # Este arquivo
```

## 🔄 Próximas Fases

- **Fase 2**: RAG com base de conhecimento (PDFs)
- **Fase 3**: Integração com DuckDuckGo para busca na internet
- **Fase 4**: API Flask e integração com OpenWebUI

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
