# 🔐 Módulo de Autenticação

Módulo de autenticação anônima e rate limiting para FastAPI, sem necessidade de login.

## 📁 Estrutura

```
api/auth/
├── __init__.py           # Exports públicos
├── fingerprint.py        # Sistema de fingerprinting
├── jwt_handler.py        # Geração e validação de JWT
├── rate_limiter.py       # Rate limiting com Redis/Memory
├── middleware.py         # Middleware FastAPI
└── README.md            # Esta documentação
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Request                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   AuthMiddleware      │
         │  (middleware.py)      │
         └───────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │Finger- │  │  JWT   │  │ Rate   │
    │print   │  │Handler │  │Limiter │
    └────────┘  └────────┘  └────────┘
         │           │           │
         └───────────┼───────────┘
                     ▼
         ┌───────────────────────┐
         │     Backend API       │
         └───────────────────────┘
```

## 📦 Componentes

### 1. `fingerprint.py`

**Função:** Gera impressão digital única do cliente

**Principais funções:**
- `generate_fingerprint(request)` - Gera hash SHA256 do fingerprint
- `get_client_info(request)` - Extrai informações detalhadas
- `_get_real_ip(request)` - Obtém IP real (considera proxies)

**Exemplo:**
```python
from api.auth import generate_fingerprint

fingerprint = generate_fingerprint(request)
# Output: "a7b3c9d2e5f8..."
```

**Algoritmo:**
```
fingerprint = SHA256(IP + User-Agent + Accept-Language)
```

### 2. `jwt_handler.py`

**Função:** Gerencia tokens JWT anônimos

**Classes principais:**
- `AnonymousToken` - Dataclass representando token
- `JWTHandler` - Handler para criar/validar tokens

**Principais métodos:**
- `create_token(fingerprint)` - Cria novo token
- `verify_token(token)` - Valida e decodifica token
- `refresh_token(old_token, new_quota)` - Renova token

**Exemplo:**
```python
from api.auth import JWTHandler

handler = JWTHandler(secret_key="your_secret")

# Criar token
token = handler.create_token(fingerprint="abc123")

# Validar token
decoded = handler.verify_token(token)
print(decoded.user_id)  # "anon_xyz..."
```

**Payload do Token:**
```json
{
  "user_id": "anon_xyz123",
  "fingerprint": "a7b3c9d2...",
  "iat": 1698765432,
  "exp": 1698851832,
  "quota_limit": 100,
  "quota_used": 15,
  "type": "anonymous"
}
```

### 3. `rate_limiter.py`

**Função:** Controla taxa de requests

**Classe principal:**
- `RateLimiter` - Gerencia rate limiting

**Backends suportados:**
- **Redis** - Distribuído, escalável (produção)
- **Memory** - Em memória, simples (desenvolvimento)

**Principais métodos:**
- `check_rate_limit(identifier, limit, window)` - Verifica limite
- `get_usage(identifier)` - Retorna estatísticas de uso
- `reset(identifier)` - Reseta contador

**Exemplo:**
```python
from api.auth import RateLimiter

limiter = RateLimiter(use_redis=True, default_limit=100)

# Verificar limite
allowed, retry_after = limiter.check_rate_limit("user_123")

if not allowed:
    print(f"Rate limit excedido. Tente em {retry_after}s")

# Ver uso
usage = limiter.get_usage("user_123")
print(f"Usado: {usage['requests_made']}/{usage['limit']}")
```

**Algoritmo:** Sliding Window Log

### 4. `middleware.py`

**Função:** Integra tudo de forma transparente

**Classes principais:**
- `AuthMiddleware` - Middleware FastAPI
- `get_current_user` - Dependency injection

**Fluxo do Middleware:**
```
1. Extrair token JWT do header Authorization (se existir)
2. Validar token
3. Se token inválido/ausente, gerar fingerprint
4. Verificar rate limiting
5. Gerar novo token se necessário
6. Adicionar informações ao request.state
7. Processar request
8. Adicionar headers de resposta (token, rate limit)
```

**Exemplo:**
```python
from api.auth import AuthMiddleware

app.add_middleware(
    AuthMiddleware,
    enabled=True,
    rate_limit_enabled=True,
    rate_limit=100,
    rate_window=3600,
    use_redis=False
)
```

**Dependency Injection:**
```python
from fastapi import Depends
from api.auth import get_current_user

@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"user_id": user["user_id"]}
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Ativar autenticação
AUTH_ENABLED=true

# Ativar rate limiting
RATE_LIMIT_ENABLED=true

# Limites
RATE_LIMIT=100
RATE_WINDOW=3600

# JWT
JWT_SECRET_KEY=your_secret_key_here
JWT_EXPIRATION_HOURS=24

# Redis (opcional)
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
```

### Inicialização na API

```python
# api/app.py
from api.auth import AuthMiddleware

auth_enabled = os.getenv("AUTH_ENABLED", "true").lower() == "true"

if auth_enabled:
    app.add_middleware(
        AuthMiddleware,
        enabled=True,
        rate_limit_enabled=True,
        rate_limit=100,
        rate_window=3600,
        use_redis=False,
        excluded_paths=["/health", "/docs"]
    )
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes do módulo
pytest api/tests/unit/auth/ -v

# Teste específico
pytest api/tests/unit/auth/test_jwt_handler.py -v

# Com cobertura
pytest api/tests/unit/auth/ --cov=api.auth --cov-report=html
```

### Cobertura Atual

- **test_fingerprint.py**: 10 testes, 100% cobertura
- **test_jwt_handler.py**: 14 testes, 96% cobertura
- **test_rate_limiter.py**: 11 testes, 58% cobertura (Redis não testado)

## 🔒 Segurança

### Boas Práticas Implementadas

✅ **Chave secreta forte** - Gerada automaticamente se não fornecida
✅ **Tokens expiram** - Configurável via `JWT_EXPIRATION_HOURS`
✅ **Fingerprint no token** - Validação de consistência
✅ **SHA256** - Hash criptograficamente seguro
✅ **Sliding window** - Algoritmo justo de rate limiting
✅ **Fail-open** - Em caso de erro, permite request (não bloqueia serviço)

### Limitações Conhecidas

⚠️ **Fingerprint não é 100% único** - Usuários atrás do mesmo proxy podem ter fingerprints similares
⚠️ **Tokens podem ser compartilhados** - Se usuário copiar token, outro pode usar
⚠️ **Rate limit em memória não persiste** - Restart da API reseta contadores

### Mitigações

✅ Validação de fingerprint no token
✅ Tokens expiram periodicamente
✅ Use Redis em produção para persistência

## 📊 Performance

### Benchmarks (aproximados)

| Operação | Tempo | Backend |
|----------|-------|---------|
| `generate_fingerprint()` | ~0.1ms | N/A |
| `create_token()` | ~1ms | N/A |
| `verify_token()` | ~1ms | N/A |
| `check_rate_limit()` | ~0.5ms | Memory |
| `check_rate_limit()` | ~2ms | Redis |

### Overhead do Middleware

- **Sem rate limiting**: ~1-2ms por request
- **Com rate limiting (memory)**: ~2-3ms por request
- **Com rate limiting (Redis)**: ~3-5ms por request

## 🔄 Fluxo Completo

### 1ª Request (Novo Usuário)

```
1. Request chega sem token
   ↓
2. Middleware gera fingerprint
   ↓
3. Cria token JWT com fingerprint
   ↓
4. Verifica rate limit (0/100)
   ↓
5. Processa request
   ↓
6. Retorna response + token no header
```

### 2ª Request (Usuário Existente)

```
1. Request chega com token no header
   ↓
2. Middleware valida token
   ↓
3. Extrai user_id do token
   ↓
4. Verifica rate limit (1/100)
   ↓
5. Processa request
   ↓
6. Retorna response + headers de rate limit
```

### Request com Rate Limit Excedido

```
1. Request chega com token
   ↓
2. Middleware valida token
   ↓
3. Verifica rate limit (100/100) ❌
   ↓
4. Retorna 429 Too Many Requests
   ↓
5. Header Retry-After: 300
```

## 🛠️ Desenvolvimento

### Adicionar Novo Backend de Rate Limiting

1. Edite `rate_limiter.py`
2. Adicione método `_check_<backend>()`
3. Atualize `__init__()` para detectar novo backend
4. Adicione testes em `test_rate_limiter.py`

### Customizar Payload do Token

1. Edite `jwt_handler.py`
2. Modifique `create_token()` para adicionar campos
3. Modifique `verify_token()` para ler novos campos
4. Atualize `AnonymousToken` dataclass

### Adicionar Novo Header de Resposta

1. Edite `middleware.py`
2. Modifique método `dispatch()`
3. Adicione header antes de `return response`

## 📚 Referências

- [RFC 7519 - JWT](https://tools.ietf.org/html/rfc7519)
- [IETF Rate Limiting Headers](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers)
- [FastAPI Middleware](https://fastapi.tiangolo.com/advanced/middleware/)
- [Redis Commands](https://redis.io/commands/)

## 🆘 Suporte

Problemas ou dúvidas:
- [Documentação completa](../../docs/AUTH_RATE_LIMITING.md)
- [Quick Start](../../QUICK_START_AUTH.md)
- [GitHub Issues](https://github.com/woliveiras/cql-agent/issues)
