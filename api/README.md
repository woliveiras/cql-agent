# 📘 API REST - CQL Assistant

## 🎯 Visão Geral

API FastAPI moderna para o Agente de Reparos Residenciais, fornecendo endpoints documentados automaticamente com Swagger UI e ReDoc para integração com OpenWebUI e outros frontends.

## 🏗️ Arquitetura

```text
┌─────────────────┐
│   Frontend      │
│  (OpenWebUI)    │
└────────┬────────┘
         │ HTTP REST
         ▼
┌─────────────────┐
│  FastAPI        │
│ Swagger + ReDoc │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CQL Assistant  │
│  RAG + Web      │
└────────┬────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐  ┌─────────┐
│ Ollama │  │ChromaDB │
└────────┘  └─────────┘
```

## 🚀 Inicio Rápido

### 1️⃣ Instalar Dependências

```bash
uv sync
```

### 2️⃣ Iniciar a API

#### 🔧 Modo Desenvolvimento

```bash
# Opção 1: Uvicorn development server (RECOMENDADO)
uv run uvicorn api.app:app --reload --host 0.0.0.0 --port 5000

# Opção 2: Uvicorn com logs verbosos
uv run uvicorn api.app:app --reload --log-level debug --port 5000

# Opção 3: Uvicorn com múltiplos workers (teste de produção)
uv run uvicorn api.app:app --reload --workers 2 --host 0.0.0.0 --port 5000
```

**Características do modo desenvolvimento:**

- ✅ Auto-reload ao modificar código
- ✅ Suporte async/await nativo
- ✅ Logs coloridos e detalhados
- ✅ Performance otimizada
- ⚠️ Single worker por padrão (usar --workers para mais)

#### 🚀 Modo Produção

```bash
# Opção 1: Uvicorn com múltiplos workers (RECOMENDADO)
uv run uvicorn api.app:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 4 \
  --log-level info

# Opção 2: Uvicorn com Gunicorn (máxima performance)
uv run gunicorn api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --timeout 30 \
  --access-logfile - \
  --error-logfile -

# Opção 3: Docker (produção completa)
docker-compose up -d api
```

**Características do modo produção:**

- ✅ Múltiplos workers (baseado em CPU)
- ✅ Async/await para alta concorrência
- ✅ Graceful restart
- ✅ Health checks automáticos
- ✅ Logging estruturado
- ⚡ Performance superior com ASGI

#### ⚙️ Configuração de Workers

O número de workers é calculado automaticamente:

```text
workers = (CPU cores × 2) + 1
```

Você pode sobrescrever via linha de comando:

```bash
# Forçar 8 workers
uv run uvicorn api.app:app --workers 8 --host 0.0.0.0 --port 5000
```

### 3️⃣ Acessar Documentação

**Swagger UI (Interativa):**  
<http://localhost:5000/docs>

**ReDoc (Somente Leitura):**  
<http://localhost:5000/redoc>

## 📡 Endpoints

### `POST /api/v1/chat/message`

Envia uma mensagem para o agente.

**Request:**

```json
{
  "message": "Como consertar uma torneira pingando?",
  "session_id": "user-123",
  "use_rag": true,
  "use_web_search": true
}
```

**Response:**

```json
{
  "response": "Para consertar uma torneira pingando...",
  "session_id": "user-123",
  "state": "new_problem",
  "metadata": {
    "rag_enabled": true,
    "web_search_enabled": true,
    "current_attempt": 1,
    "max_attempts": 3
  },
  "timestamp": "2025-10-18T10:30:00Z"
}
```

### `DELETE /api/v1/chat/reset/{session_id}`

Reseta o estado de uma sessão.

**Response:**

```json
{
  "message": "Sessão user-123 resetada com sucesso"
}
```

### `GET /api/v1/chat/sessions`

Lista todas as sessões ativas.

**Response:**

```json
{
  "sessions": [
    {
      "session_id": "user-123",
      "state": "waiting_feedback",
      "current_attempt": 2
    }
  ],
  "total": 1
}
```

### `GET /health`

Health check da API.

**Response:**

```json
{
  "status": "healthy",
  "service": "repair-agent-api",
  "version": "1.0.0",
  "timestamp": "2025-10-18T10:30:00Z"
}
```

## 🔧 Configuração

### Uvicorn (Servidor ASGI)

O projeto usa Uvicorn como servidor ASGI para produção. Para configuração avançada, use Gunicorn como process manager com workers Uvicorn.

#### Principais Configurações

| Configuração | Valor Padrão | Descrição |
|--------------|--------------|-----------|
| `workers` | `1` | Número de processos worker |
| `host` | `127.0.0.1` | Host para bind |
| `port` | `8000` | Porta do servidor |
| `timeout-keep-alive` | `5s` | Timeout de keep-alive |
| `reload` | `false` | Auto-reload (dev apenas) |

#### Linha de Comando

```bash
# Múltiplos workers
uv run uvicorn api.app:app --workers 4 --host 0.0.0.0 --port 5000

# Com Gunicorn (process manager)
uv run gunicorn api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000
```

#### Variáveis de Ambiente

```bash
# Porta do servidor
PORT=5000

# Nível de log
LOG_LEVEL=info  # debug, info, warning, error, critical
```

#### Health Checks

A API possui health check configurado:

```bash
# Endpoint
GET /health

# Resposta
{
  "status": "healthy",
  "service": "repair-agent-api",
  "version": "1.0.0",
  "timestamp": "2025-10-19T10:30:00Z"
}

# Docker health check (configurado no Dockerfile)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3
```

O health check verifica automaticamente:

- ✅ API está respondendo
- ✅ Processo está ativo
- ✅ Porta está acessível

**Monitorar health check:**

```bash
# Docker
docker inspect --format='{{.State.Health.Status}}' repair-agent-api

# Curl manual
curl -f http://localhost:5000/health || echo "API unhealthy"

# Com timeout
timeout 5 curl -f http://localhost:5000/health
```

### Variáveis de Ambiente da Aplicação

```bash
# URL do Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Porta da API
PORT=5000

# Nível de log
LOG_LEVEL=info

# Caminho do ChromaDB
CHROMA_DB_PATH=./chroma_db
```

### Configuração em `agent.py`

A API usa as mesmas configurações do agente:

```python
agent = RepairAgent(
    model_name="qwen2.5:3b",
    temperature=0.3,
    use_rag=True,
    use_web_search=True,
    chroma_db_path="./chroma_db"
)
```

## 📚 Documentação Interativa

### Swagger UI

Acesse <http://localhost:5000/docs> para:

- ✅ Ver todos os endpoints disponíveis
- ✅ Testar requisições diretamente no navegador
- ✅ Ver schemas de request/response
- ✅ Baixar especificação OpenAPI

### Exemplo de Uso

```bash
# Testar endpoint de chat
curl -X POST http://localhost:5000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Como consertar uma torneira?",
    "session_id": "test-123"
  }'
```

## 🔐 Segurança

### CORS

CORS está habilitado para permitir requisições de qualquer origem em desenvolvimento. **Em produção, configure origens específicas:**

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://seu-frontend.com"]
    }
})
```

### Rate Limiting

Para produção, adicione rate limiting com Slowapi:

```bash
uv add slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/chat/message")
@limiter.limit("100/hour")
async def chat_message(request: Request):
    ...
```

## 🐳 Docker

### Build

```bash
docker build -f Dockerfile.api -t repair-agent-api .
```

### Run

```bash
docker run -p 5000:5000 \
  -v $(pwd)/chroma_db:/app/chroma_db:ro \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  repair-agent-api
```

## 🧪 Testes

### Teste Automatizado Completo

```bash
# Script de teste completo (recomendado)
./test_api.sh

# Com URL customizada
API_URL=http://localhost:8000 ./test_api.sh
```

O script testa:

- ✅ Health check
- ✅ Documentação Swagger
- ✅ Endpoint de chat
- ✅ Listagem de sessões
- ✅ Reset de sessão
- ⚡ Performance (10 requisições)

### Teste Manual

```bash
# Health check
curl http://localhost:5000/health

# Enviar mensagem
curl -X POST http://localhost:5000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá!", "session_id": "test"}'

# Listar sessões
curl http://localhost:5000/api/v1/chat/sessions

# Resetar sessão
curl -X DELETE http://localhost:5000/api/v1/chat/reset/test
```

### Teste Automatizado

```python
import requests

# Configurar
BASE_URL = "http://localhost:5000/api/v1"

# Enviar mensagem
response = requests.post(
    f"{BASE_URL}/chat/message",
    json={
        "message": "Como consertar torneira?",
        "session_id": "test-123"
    }
)

print(response.json())
```

## 🔄 Gerenciamento de Sessões

### Em Memória (Desenvolvimento)

Por padrão, sessões são armazenadas em memória (dicionário Python). Isso é adequado para desenvolvimento mas **não é recomendado para produção**.

### Redis (Produção)

Para produção, use Redis com aioredis:

```bash
uv add aioredis
```

```python
import aioredis
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.redis = await aioredis.from_url("redis://localhost:6379")

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()
```

## 📊 Monitoramento

### Logs

A API usa logging do Python:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Logs incluem:

- Requisições recebidas
- Erros de processamento
- Criação/reset de sessões

### Métricas

Para métricas avançadas, adicione Prometheus com starlette-prometheus:

```bash
uv add starlette-prometheus
```

## 🚦 Status Codes

| Code | Significado |
|------|-------------|
| 200 | Sucesso |
| 400 | Requisição inválida (validação falhou) |
| 404 | Recurso não encontrado (sessão não existe) |
| 500 | Erro interno do servidor |

## 🔗 Integração com OpenWebUI

Veja `openwebui/pipe.py` para integração completa com OpenWebUI.

## 📖 Próximos Passos

1. Testar API standalone
2. Integrar com OpenWebUI
3. Deploy com Docker Compose
4. Configurar monitoramento

📚 **Guias Detalhados:**

- [Guia Completo de Deploy](../docs/GUIA_DEPLOY.md) - Desenvolvimento, produção e monitoramento
- [Integração com OpenWebUI](../docs/INTEGRACAO_OPENWEBUI.md)
- [Quick Start RAG](../docs/QUICK_START_RAG.md)

## 🆘 Troubleshooting

### API não inicia

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Verificar dependências
uv pip list | grep fastapi
```

### Erro 500 ao enviar mensagem

- Verificar logs da API
- Confirmar que ChromaDB está acessível
- Testar agente diretamente (sem API)

### Sessões não persistem

- Em desenvolvimento, sessões são em memória
- Reiniciar a API limpa todas as sessões
- Use Redis para persistência

## 📝 Licença

Este projeto segue a mesma licença do projeto principal.
