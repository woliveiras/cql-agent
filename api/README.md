# 📘 API REST - Repair Agent

## 🎯 Visão Geral

API Flask RESTful para o Agente de Reparos Residenciais, fornecendo endpoints documentados com Swagger/OpenAPI para integração com OpenWebUI e outros frontends.

## 🏗️ Arquitetura

```text
┌─────────────────┐
│   Frontend      │
│  (OpenWebUI)    │
└────────┬────────┘
         │ HTTP REST
         ▼
┌─────────────────┐
│   Flask API     │
│   + Swagger     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repair Agent   │
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
# Opção 1: Flask development server (com auto-reload)
uv run python -m api.app

# Opção 2: Flask CLI (recomendado para dev)
uv run flask --app api.app run --debug --port 5000

# Opção 3: Gunicorn com reload (mais próximo de produção)
uv run gunicorn --config api/gunicorn.conf.py \
  --reload \
  --log-level debug \
  api.app:app
```

**Características do modo desenvolvimento:**

- ✅ Auto-reload ao modificar código
- ✅ Debug detalhado
- ✅ Stack traces completos
- ⚠️ Single worker (não otimizado para carga)

#### 🚀 Modo Produção

```bash
# Opção 1: Gunicorn com configuração otimizada (RECOMENDADO)
uv run gunicorn --config api/gunicorn.conf.py api.app:app

# Opção 2: Gunicorn com parâmetros personalizados
uv run gunicorn api.app:app \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 30 \
  --access-logfile - \
  --error-logfile -

# Opção 3: Docker (produção completa)
docker-compose up -d api
```

**Características do modo produção:**

- ✅ Múltiplos workers (baseado em CPU)
- ✅ Preload da aplicação (memória otimizada)
- ✅ Graceful restart
- ✅ Health checks automáticos
- ✅ Logging estruturado
- ⚡ Alta performance e concorrência

#### ⚙️ Configuração de Workers

O número de workers é calculado automaticamente:

```text
workers = (CPU cores × 2) + 1
```

Você pode sobrescrever via variável de ambiente:

```bash
# Forçar 8 workers
GUNICORN_WORKERS=8 uv run gunicorn --config api/gunicorn.conf.py api.app:app
```

### 3️⃣ Acessar Documentação

Abra no navegador: <http://localhost:5000/docs>

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

### Gunicorn (Servidor de Produção)

O projeto usa Gunicorn como servidor WSGI para produção. As configurações estão em `api/gunicorn.conf.py`:

#### Principais Configurações

| Configuração | Valor Padrão | Descrição |
|--------------|--------------|-----------|
| `workers` | `(CPU × 2) + 1` | Número de processos worker |
| `worker_class` | `sync` | Tipo de worker (sync para Flask) |
| `timeout` | `30s` | Timeout de requisições |
| `max_requests` | `1000` | Requests antes de reiniciar worker |
| `preload_app` | `true` | Carregar app antes de fazer fork |

#### Variáveis de Ambiente

```bash
# Número de workers (padrão: auto-detect)
GUNICORN_WORKERS=4

# Habilitar reload automático (dev apenas)
GUNICORN_RELOAD=true

# Nível de log
LOG_LEVEL=info  # debug, info, warning, error, critical
```

#### Lifecycle Hooks

O Gunicorn possui hooks configurados para logging detalhado:

- `on_starting`: Servidor iniciando
- `when_ready`: Pronto para aceitar conexões
- `post_fork`: Worker criado
- `worker_exit`: Worker finalizado
- `on_exit`: Servidor desligando

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
FLASK_PORT=5000

# Modo debug
FLASK_ENV=development

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

Para produção, adicione rate limiting:

```bash
uv add flask-limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)
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

Para produção, use Redis:

```bash
uv add redis flask-session
```

```python
from flask_session import Session
import redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
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

Para métricas avançadas, adicione Prometheus:

```bash
uv add prometheus-flask-exporter
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
uv pip list | grep flask
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
