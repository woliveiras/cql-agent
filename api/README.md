# 📘 API REST - Repair Agent

## 🎯 Visão Geral

API Flask RESTful para o Agente de Reparos Residenciais, fornecendo endpoints documentados com Swagger/OpenAPI para integração com OpenWebUI e outros frontends.

## 🏗️ Arquitetura

```
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

```bash
# Modo desenvolvimento
uv run python -m api.app

# Ou com Flask diretamente
uv run flask --app api.app run --debug
```

### 3️⃣ Acessar Documentação

Abra no navegador: http://localhost:5000/docs

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

### Variáveis de Ambiente

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

Acesse http://localhost:5000/docs para:

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
