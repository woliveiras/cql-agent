# Autenticação Anônima e Rate Limiting

Sistema híbrido de autenticação e rate limiting sem necessidade de login, implementado para proteger a API contra abuso mantendo uma experiência de usuário fluida.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Como Funciona](#como-funciona)
- [Configuração](#configuração)
- [Uso no Frontend](#uso-no-frontend)
- [Endpoints Protegidos](#endpoints-protegidos)
- [Rate Limiting](#rate-limiting)
- [Exemplos Práticos](#exemplos-práticos)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

Este sistema implementa autenticação **100% transparente para o usuário**, sem necessidade de criar conta ou fazer login. Combina:

1. **Fingerprinting** - Identifica usuários por IP + User-Agent
2. **JWT Anônimo** - Gera tokens temporários automaticamente
3. **Rate Limiting** - Limita número de requests por período
4. **Quotas Flexíveis** - Permite configurar limites diferentes

### Características

✅ **Sem login** - Usuário nunca vê tela de autenticação
✅ **Transparente** - Funciona automaticamente em background
✅ **Escalável** - Suporte a Redis para distribuição
✅ **Seguro** - Protege contra abuso e DDoS
✅ **Configurável** - Ative/desative via `.env`

---

## Como Funciona

### Fluxo Completo

```
1ª REQUEST DO USUÁRIO:
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│  Middleware  │─────▶│   Backend   │
│  (Browser)  │      │  Auth+Rate   │      │     API     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─ Gera fingerprint (IP + User-Agent)
                            ├─ Verifica rate limit
                            ├─ Cria token JWT anônimo
                            └─ Adiciona token no header de resposta

2ª REQUEST (mesma sessão):
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│  Middleware  │─────▶│   Backend   │
│  (Token no  │      │  Valida JWT  │      │     API     │
│   header)   │      │  + Rate Lim. │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
```

### Componentes

#### 1. **Fingerprinting** (`api/auth/fingerprint.py`)

Gera uma "impressão digital" única do cliente:

```python
fingerprint = SHA256(IP + User-Agent + Accept-Language)
```

**Exemplo:**
```
IP: 192.168.1.100
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X)
Accept-Language: pt-BR,pt;q=0.9

Fingerprint: a7b3c9d2e5f8...  (hash SHA256)
```

#### 2. **JWT Anônimo** (`api/auth/jwt_handler.py`)

Gera tokens JWT temporários com informações do usuário:

```json
{
  "user_id": "anon_xYz123ABC",
  "fingerprint": "a7b3c9d2e5f8...",
  "issued_at": "2024-10-26T10:00:00Z",
  "expires_at": "2024-10-27T10:00:00Z",
  "quota_limit": 100,
  "quota_used": 15
}
```

#### 3. **Rate Limiter** (`api/auth/rate_limiter.py`)

Controla número de requests por período:

- **Backend Redis**: Escalável, distribuído
- **Backend Memória**: Simples, desenvolvimento local
- **Algoritmo**: Sliding Window Log

#### 4. **Middleware** (`api/auth/middleware.py`)

Integra tudo de forma transparente na FastAPI.

---

## Configuração

### 1. Variáveis de Ambiente

Edite o arquivo `.env`:

```bash
# ============================================================================
# AUTENTICAÇÃO E RATE LIMITING
# ============================================================================

# Habilitar sistema de autenticação anônima (true/false)
AUTH_ENABLED=true

# Habilitar rate limiting (true/false)
RATE_LIMIT_ENABLED=true

# Limite de requests por janela de tempo
RATE_LIMIT=100

# Janela de tempo em segundos (3600 = 1 hora)
RATE_WINDOW=3600

# Chave secreta para JWT (gere uma forte!)
# Exemplo: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=sua_chave_secreta_aqui

# Expiração de tokens em horas
JWT_EXPIRATION_HOURS=24

# Redis (opcional, para produção)
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
```

### 2. Gerar Chave Secreta

**IMPORTANTE:** Em produção, use uma chave forte!

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado e cole em `JWT_SECRET_KEY=...`

### 3. Instalar Dependências

```bash
uv sync
```

### 4. Iniciar API

```bash
uv run uvicorn api.app:app --host 0.0.0.0 --port 5000 --reload
```

Você verá no log:

```
INFO: Middleware de autenticação ativado
      rate_limit_enabled=True
      rate_limit=100
      rate_window=3600
      use_redis=False
```

---

## Uso no Frontend

### JavaScript/TypeScript

```typescript
// api.ts
const API_URL = 'http://localhost:5000';

// Armazenar token no localStorage
let anonymousToken: string | null = localStorage.getItem('anonymous_token');

async function sendMessage(message: string) {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Adicionar token se existir
  if (anonymousToken) {
    headers['Authorization'] = `Bearer ${anonymousToken}`;
  }

  const response = await fetch(`${API_URL}/api/v1/chat/message`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ message })
  });

  // Salvar novo token se fornecido
  const newToken = response.headers.get('X-Anonymous-Token');
  if (newToken) {
    anonymousToken = newToken;
    localStorage.setItem('anonymous_token', newToken);
  }

  // Verificar informações de rate limit
  const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining');
  console.log(`Requests restantes: ${rateLimitRemaining}`);

  // Tratar rate limit excedido
  if (response.status === 429) {
    const data = await response.json();
    const retryAfter = data.retry_after;
    throw new Error(`Rate limit excedido. Tente em ${retryAfter}s`);
  }

  return response.json();
}

// Uso
try {
  const result = await sendMessage('Como consertar torneira?');
  console.log(result.response);
} catch (error) {
  console.error(error);
}
```

### React com Custom Hook

```typescript
// useApi.ts
import { useState, useEffect } from 'react';

export function useApi() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('anonymous_token')
  );

  useEffect(() => {
    if (token) {
      localStorage.setItem('anonymous_token', token);
    }
  }, [token]);

  async function sendMessage(message: string) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch('/api/v1/chat/message', {
      method: 'POST',
      headers,
      body: JSON.stringify({ message })
    });

    const newToken = response.headers.get('X-Anonymous-Token');
    if (newToken) {
      setToken(newToken);
    }

    if (response.status === 429) {
      const data = await response.json();
      throw new Error(`Rate limit: tente em ${data.retry_after}s`);
    }

    return response.json();
  }

  return { sendMessage, token };
}

// Componente
function ChatComponent() {
  const { sendMessage } = useApi();
  const [message, setMessage] = useState('');

  async function handleSubmit() {
    try {
      const result = await sendMessage(message);
      console.log(result.response);
    } catch (error) {
      alert(error.message);
    }
  }

  return (
    <div>
      <input value={message} onChange={e => setMessage(e.target.value)} />
      <button onClick={handleSubmit}>Enviar</button>
    </div>
  );
}
```

---

## Endpoints Protegidos

### Endpoints COM Rate Limiting

Todos os endpoints exceto os listados abaixo:

- `POST /api/v1/chat/message` ✅
- `DELETE /api/v1/chat/reset/{session_id}` ✅
- `GET /api/v1/chat/sessions` ✅

### Endpoints SEM Rate Limiting

Estes endpoints são excluídos:

- `GET /health` - Health check
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc
- `GET /` - Rota raiz

---

## Rate Limiting

### Headers de Resposta

Toda resposta inclui headers informativos:

```http
HTTP/1.1 200 OK
X-Anonymous-Token: eyJhbGciOiJIUzI1NiIs...
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 3600
```

### Response quando Limite Excedido

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 300

{
  "error": "Rate limit excedido",
  "details": "Você fez muitas requisições. Tente novamente em 300 segundos.",
  "retry_after": 300
}
```

### Configurações Recomendadas

#### Desenvolvimento
```bash
RATE_LIMIT=1000
RATE_WINDOW=3600  # 1 hora
```

#### Produção (API Pública)
```bash
RATE_LIMIT=100
RATE_WINDOW=3600  # 1 hora
```

#### Produção (API Restrita)
```bash
RATE_LIMIT=10
RATE_WINDOW=60  # 1 minuto
```

---

## Exemplos Práticos

### Exemplo 1: Teste com cURL

```bash
# 1ª request - recebe token
curl -X POST http://localhost:5000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Como consertar torneira?"}' \
  -v | grep -i "x-anonymous-token"

# Copiar token do header X-Anonymous-Token

# 2ª request - usa token
curl -X POST http://localhost:5000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"message": "E se não funcionar?"}' \
  -v
```

### Exemplo 2: Verificar Rate Limit

```bash
# Ver quantos requests restam
curl -X POST http://localhost:5000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "teste"}' \
  -v 2>&1 | grep "X-RateLimit"

# Saída:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 95
# X-RateLimit-Reset: 3600
```

### Exemplo 3: Testar Bloqueio

```bash
# Fazer muitos requests rapidamente
for i in {1..105}; do
  curl -X POST http://localhost:5000/api/v1/chat/message \
    -H "Content-Type: application/json" \
    -d '{"message": "teste '$i'"}' \
    -s | jq '.error' 2>/dev/null
done

# Após 100 requests, verá:
# "Rate limit excedido"
```

---

## Troubleshooting

### Problema: Token não está sendo salvo

**Solução:** Verifique se está lendo o header `X-Anonymous-Token` e salvando no localStorage:

```javascript
const token = response.headers.get('X-Anonymous-Token');
if (token) {
  localStorage.setItem('anonymous_token', token);
}
```

### Problema: Rate limit muito restritivo

**Solução 1:** Aumentar limite no `.env`:
```bash
RATE_LIMIT=500
```

**Solução 2:** Aumentar janela de tempo:
```bash
RATE_WINDOW=7200  # 2 horas
```

**Solução 3:** Desabilitar temporariamente:
```bash
RATE_LIMIT_ENABLED=false
```

### Problema: Erro "Connection refused" no Redis

**Solução:** Usar backend em memória:
```bash
USE_REDIS=false
```

### Problema: Token expirou

**Comportamento normal:** Tokens expiram após `JWT_EXPIRATION_HOURS`. O middleware gera automaticamente um novo token.

**Verificar:** Se o frontend está salvando o novo token:
```javascript
const newToken = response.headers.get('X-Anonymous-Token');
if (newToken) {
  setToken(newToken); // Atualizar estado
}
```

### Problema: CORS bloqueando headers

**Solução:** Verificar se CORS permite ler headers customizados:

```python
# api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Anonymous-Token", "X-RateLimit-*"]  # ← Adicionar
)
```

### Problema: Desabilitar para testes

**Solução:** Desabilitar completamente:
```bash
AUTH_ENABLED=false
```

---

## Testes

### Executar Testes Unitários

```bash
# Todos os testes de autenticação
pytest api/tests/unit/auth/ -v

# Teste específico
pytest api/tests/unit/auth/test_jwt_handler.py -v

# Com cobertura
pytest api/tests/unit/auth/ --cov=api.auth --cov-report=html
```

### Testes Implementados

- ✅ **test_fingerprint.py** - 10 testes de fingerprinting
- ✅ **test_jwt_handler.py** - 15 testes de JWT
- ✅ **test_rate_limiter.py** - 12 testes de rate limiting

---

## Segurança

### Boas Práticas

1. **Gere chave JWT forte:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use Redis em produção:**
   ```bash
   USE_REDIS=true
   ```

3. **Configure HTTPS:**
   - Tokens só devem ser transmitidos via HTTPS

4. **Monitore rate limit:**
   - Ajuste limites baseado em uso real

5. **Rotação de chaves:**
   - Troque `JWT_SECRET_KEY` periodicamente

### Limitações

⚠️ **Fingerprinting não é 100% único:**
- Usuários atrás do mesmo proxy/NAT terão fingerprints similares
- Solução: Tokens JWT garantem unicidade

⚠️ **Tokens podem ser compartilhados:**
- Se usuário copiar token, outro pode usar
- Mitigação: Validar fingerprint no token

⚠️ **Rate limit por memória não persiste:**
- Restart da API reseta contadores
- Solução: Use Redis

---

## Referências

- [JWT.io](https://jwt.io/) - Especificação JWT
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JSON Web Token
- [IETF Rate Limiting](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers) - Headers de rate limit
- [FastAPI Middleware](https://fastapi.tiangolo.com/advanced/middleware/) - Documentação FastAPI

---

## Suporte

Encontrou problemas? Abra uma issue no GitHub ou consulte:

- [README.md](../README.md) - Documentação principal
- [GUIA_DEPLOY.md](GUIA_DEPLOY.md) - Deploy em produção
- [GitHub Issues](https://github.com/woliveiras/cql-agent/issues)
