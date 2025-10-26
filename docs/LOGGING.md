# Logging Estruturado - CQL Agent

O CQL Agent utiliza um sistema de logging estruturado baseado em JSON para facilitar monitoramento, debugging e análise de logs em produção.

## Características

- ✅ **Logs estruturados em JSON** para produção
- ✅ **Logs legíveis** para desenvolvimento
- ✅ **Contexto adicional** automático (session_id, request_id, component, etc.)
- ✅ **Diferentes níveis de log** por ambiente
- ✅ **Rastreamento de performance** com duration_ms
- ✅ **Integração fácil** com ferramentas de observabilidade

## Configuração

### Variáveis de Ambiente

Configure o logging através do arquivo `.env`:

```bash
# Ambiente (development, production)
ENVIRONMENT=development

# Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Formato JSON (true para produção, false para desenvolvimento)
JSON_LOGS=false

# Arquivo de log opcional
LOG_FILE=./logs/app.log
```

### Modo Desenvolvimento

Logs legíveis para humanos:

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
JSON_LOGS=false
```

**Exemplo de saída:**

```
2025-10-26 09:16:31 - api.app - INFO - Processando mensagem
2025-10-26 09:16:32 - api.security - WARNING - Sanitização falhou
```

### Modo Produção

Logs estruturados em JSON:

```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
JSON_LOGS=true
```

**Exemplo de saída:**

```json
{
  "timestamp": "2025-10-26T09:16:31",
  "level": "INFO",
  "logger": "api.app",
  "message": "Processando mensagem",
  "component": "api",
  "session_id": "session-123",
  "event_type": "message_processing",
  "message_length": 45,
  "use_rag": true,
  "duration_ms": 150,
  "module": "app",
  "function": "send_message",
  "line": 280
}
```

## Uso no Código

### Configuração Inicial

```python
from api.logging_config import setup_logging

# Configurar logging (uma vez, no início da aplicação)
setup_logging(
    level="INFO",
    json_logs=True,  # ou False para desenvolvimento
    log_file="./logs/app.log"  # opcional
)
```

### Criar Logger

```python
from api.logging_config import get_logger

# Criar logger com componente
logger = get_logger(__name__, component="api")
```

### Logging Simples

```python
# Log simples
logger.info("Operação concluída")

# Log com contexto
logger.info(
    "Processando request",
    extra={
        "session_id": "123",
        "user_id": "user-456",
        "duration_ms": 150
    }
)
```

### Logging com Contexto (Context Manager)

Use `LogContext` para adicionar contexto temporário a todos os logs:

```python
from api.logging_config import LogContext

with LogContext(session_id="123", request_id="abc"):
    logger.info("Iniciando processamento")  # Terá session_id e request_id
    # ... operações ...
    logger.info("Finalizando processamento")  # Também terá session_id e request_id
```

### Logging de Erros

```python
try:
    # ... código ...
except Exception as e:
    logger.error(
        "Erro ao processar request",
        extra={
            "session_id": session_id,
            "error_type": type(e).__name__,
            "error": str(e)
        },
        exc_info=True  # Inclui stack trace
    )
```

## Campos Padrão

Todo log inclui automaticamente:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `timestamp` | ISO 8601 timestamp | `2025-10-26T09:16:31` |
| `level` | Nível do log | `INFO`, `ERROR`, etc. |
| `logger` | Nome do logger | `api.app` |
| `message` | Mensagem do log | `Processando mensagem` |
| `module` | Módulo Python | `app` |
| `function` | Função que gerou o log | `send_message` |
| `line` | Linha do código | `280` |

## Campos de Contexto

Campos adicionais que podem ser incluídos via `extra={}`:

### Identificação

- `session_id`: ID da sessão do usuário
- `request_id`: ID único da requisição
- `user_id`: ID do usuário
- `component`: Componente da aplicação (api, agent, rag, security)

### Eventos

- `event_type`: Tipo de evento (request, response, error, agent_created, etc.)

### Performance

- `duration_ms`: Duração em milissegundos
- `message_length`: Tamanho da mensagem

### Aplicação Específica

- `use_rag`: Se RAG foi usado
- `use_web_search`: Se web search foi usado
- `relevance_score`: Score de relevância (0-1)
- `state`: Estado do agente
- `current_attempt`: Tentativa atual

### Erros

- `error`: Mensagem de erro
- `error_type`: Tipo da exceção

## Exemplos Práticos

### 1. API Request/Response

```python
start_time = time.time()

with LogContext(session_id=request.session_id, event_type="api_request"):
    logger.info(
        "Request recebido",
        extra={
            "method": "POST",
            "endpoint": "/api/v1/chat/message",
            "message_length": len(request.message)
        }
    )

    # Processar request
    response = process_request(request)

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "Request processado",
        extra={
            "duration_ms": duration_ms,
            "status": "success"
        }
    )
```

### 2. Criação de Agente

```python
logger.info(
    "Criando novo agente",
    extra={
        "session_id": session_id,
        "use_rag": use_rag,
        "use_web_search": use_web_search,
        "event_type": "agent_created"
    }
)
```

### 3. Sanitização de Entrada

```python
try:
    sanitized = sanitize_input(message)
except SanitizationError as e:
    logger.warning(
        "Sanitização falhou",
        extra={
            "session_id": session_id,
            "error": str(e),
            "event_type": "sanitization_failed"
        }
    )
```

### 4. Performance Tracking

```python
start_time = time.time()

# ... operação ...

duration_ms = int((time.time() - start_time) * 1000)
logger.info(
    "Operação concluída",
    extra={
        "operation": "rag_search",
        "duration_ms": duration_ms,
        "results_count": len(results)
    }
)
```

## Integração com Ferramentas

### 1. Elasticsearch + Kibana

Logs JSON podem ser facilmente ingeridos pelo Elasticsearch:

```bash
# Exemplo de pipeline Filebeat
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/cql-agent/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "cql-agent-%{+yyyy.MM.dd}"
```

### 2. Grafana Loki

```yaml
# promtail-config.yaml
scrape_configs:
  - job_name: cql-agent
    static_configs:
      - targets:
          - localhost
        labels:
          job: cql-agent
          __path__: /var/log/cql-agent/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            timestamp: timestamp
            message: message
```

### 3. DataDog

```python
import logging
from pythonjsonlogger import jsonlogger

# Logs JSON são automaticamente parseados pelo DataDog
# Adicione tags para facilitar filtragem:
logger.info("Event", extra={
    "dd.trace_id": trace_id,
    "dd.span_id": span_id,
    "service": "cql-agent",
    "env": "production"
})
```

## Queries de Exemplo

### Elasticsearch/Kibana

```json
// Encontrar erros em uma sessão específica
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" }},
        { "match": { "session_id": "session-123" }}
      ]
    }
  }
}

// Requisições lentas (> 1 segundo)
{
  "query": {
    "range": {
      "duration_ms": { "gte": 1000 }
    }
  }
}
```

### Grafana Loki

```logql
# Todos os erros
{job="cql-agent"} | json | level="ERROR"

# Duração média por endpoint
avg_over_time({job="cql-agent"} | json | unwrap duration_ms [5m])

# Eventos de criação de agente
{job="cql-agent"} | json | event_type="agent_created"
```

## Boas Práticas

### ✅ Fazer

1. **Use níveis apropriados:**
   - `DEBUG`: Informação detalhada para debugging
   - `INFO`: Eventos importantes (request, response, criação de recursos)
   - `WARNING`: Situações inesperadas mas recuperáveis
   - `ERROR`: Erros que precisam atenção
   - `CRITICAL`: Falhas graves do sistema

2. **Adicione contexto relevante:**
   ```python
   logger.info("Operação", extra={"session_id": "123", "duration_ms": 150})
   ```

3. **Use event_type consistentes:**
   ```python
   event_type="request", "response", "error", "agent_created", etc.
   ```

4. **Inclua métricas de performance:**
   ```python
   extra={"duration_ms": duration}
   ```

5. **Log erros com stack trace:**
   ```python
   logger.error("Erro", exc_info=True)
   ```

### ❌ Evitar

1. **Não logue informações sensíveis:**
   ```python
   # ❌ NÃO FAÇA ISSO
   logger.info("Login", extra={"password": password})

   # ✅ FAÇA ISSO
   logger.info("Login", extra={"user_id": user_id})
   ```

2. **Não use f-strings para mensagens:**
   ```python
   # ❌ Ruim (sempre avaliado)
   logger.debug(f"Valor: {expensive_operation()}")

   # ✅ Melhor
   logger.debug("Valor: %s", expensive_operation())
   ```

3. **Não logue em loops sem controle:**
   ```python
   # ❌ Pode gerar milhares de logs
   for item in large_list:
       logger.debug(f"Processando {item}")

   # ✅ Melhor
   logger.debug(f"Processando {len(large_list)} items")
   ```

## Troubleshooting

### Logs não aparecem

Verifique o nível de log:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Campos extras não aparecem em JSON

Certifique-se de usar `extra={}`:

```python
logger.info("Message", extra={"field": "value"})
```

### Performance

Logs em JSON têm overhead mínimo. Para otimizar:

1. Use nível `INFO` em produção
2. Evite logs em loops críticos
3. Use sampling para high-volume events

## Referências

- [python-json-logger](https://github.com/madzak/python-json-logger)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [12-Factor App: Logs](https://12factor.net/logs)
