# 🧪 Testando a API do Repair Agent

## 🌐 Documentação Interativa

A API usa **FastAPI**, que gera documentação OpenAPI 3.0 automaticamente a partir do código Python. Você tem duas opções de interface:

### 📘 Swagger UI (Interativa)

Interface oficial do OpenAPI para testar endpoints:

```sh
http://localhost:5000/docs
```

**Recursos:**

- ✅ Testar endpoints diretamente no navegador
- ✅ Ver esquemas de request/response
- ✅ Autenticação integrada
- ✅ Exemplos de código

### 📗 ReDoc (Somente Leitura)

Documentação alternativa mais limpa e organizada:

```sh
http://localhost:5000/redoc
```

**Recursos:**

- ✅ Design limpo e responsivo
- ✅ Navegação por tags
- ✅ Exemplos de código
- ✅ Melhor para leitura e compartilhamento

---

## 🧪 Testando no Swagger UI

### 1. Acessar Swagger

Abra no navegador:

```sh
http://localhost:5000/docs
```

### 2. Testar Endpoints no Swagger

#### Teste 1: Health Check

1. Clique em `GET /health`
2. Clique em "Try it out"
3. Clique em "Execute"
4. Veja a resposta:

```json
{
  "status": "healthy",
  "service": "repair-agent-api",
  "version": "1.0.0",
  "timestamp": "2025-10-18T..."
}
```

#### Teste 2: Enviar Mensagem

1. Clique em `POST /api/v1/chat/message`
2. Clique em "Try it out"
3. Cole este JSON no campo "Request body":

    ```json
    {
      "message": "Como consertar uma torneira pingando?",
      "session_id": "swagger-test-001",
      "use_rag": true,
      "use_web_search": false
    }
    ```

4. Clique em "Execute"
5. Aguarde (pode demorar ~5-10 segundos)
6. Veja a resposta com instruções do agente!

#### Teste 3: Listar Sessões

1. Clique em `GET /api/v1/chat/sessions`
2. Clique em "Try it out"
3. Clique em "Execute"
4. Veja lista de sessões ativas

#### Teste 4: Resetar Sessão

1. Clique em `DELETE /api/v1/chat/reset/{session_id}`
2. Clique em "Try it out"
3. Digite `swagger-test-001` no campo session_id
4. Clique em "Execute"
5. Veja confirmação de reset

---

## 📮 Postman

### 1. Importar Collection

Crie uma nova Collection chamada "Repair Agent API"

### 2. Request 1: Health Check

**Método**: GET  
**URL**: `http://localhost:5000/health`  
**Headers**: (nenhum necessário)

**Resposta esperada**:

```json
{
  "status": "healthy",
  "service": "repair-agent-api",
  "version": "1.0.0",
  "timestamp": "2025-10-18T07:30:00.000000Z"
}
```

### 3. Request 2: Enviar Mensagem

**Método**: POST  
**URL**: `http://localhost:5000/api/v1/chat/message`  
**Headers**:

```text
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "message": "Como consertar uma torneira pingando?",
  "session_id": "postman-test-001",
  "use_rag": true,
  "use_web_search": false
}
```

**Resposta esperada**:

```json
{
  "response": "Para consertar uma torneira pingando, siga estes passos:\n\n1. Desligue o registro...",
  "session_id": "postman-test-001",
  "state": "waiting_feedback",
  "metadata": {
    "rag_enabled": true,
    "web_search_enabled": false,
    "current_attempt": 1,
    "max_attempts": 3
  },
  "timestamp": "2025-10-18T07:30:00.000000Z"
}
```

### 4. Request 3: Continuar Conversa

**Método**: POST  
**URL**: `http://localhost:5000/api/v1/chat/message`  
**Headers**:

```text
Content-Type: application/json
```

**Body** (raw JSON):

```json
{
  "message": "Sim, funcionou!",
  "session_id": "postman-test-001"
}
```

**Resposta esperada**:

```json
{
  "response": "Ótimo! Fico feliz que tenha conseguido...",
  "session_id": "postman-test-001",
  "state": "resolved",
  "metadata": {...},
  "timestamp": "..."
}
```

### 5. Request 4: Listar Sessões

**Método**: GET  
**URL**: `http://localhost:5000/api/v1/chat/sessions`  
**Headers**: (nenhum necessário)

**Resposta esperada**:

```json
{
  "sessions": [
    {
      "session_id": "postman-test-001",
      "state": "resolved",
      "current_attempt": 1
    }
  ],
  "total": 1
}
```

### 6. Request 5: Resetar Sessão

**Método**: DELETE  
**URL**: `http://localhost:5000/api/v1/chat/reset/postman-test-001`  
**Headers**: (nenhum necessário)

**Resposta esperada**:

```json
{
  "message": "Sessão postman-test-001 resetada com sucesso"
}
```

---

## 🔥 Cenários de Teste Avançados

### Teste com RAG + Web Search

```json
{
  "message": "Como instalar energia solar em casa?",
  "session_id": "advanced-test-001",
  "use_rag": true,
  "use_web_search": true
}
```

Este teste irá:

1. Buscar na base de conhecimento (RAG)
2. Se não encontrar, buscar na web
3. Retornar resposta combinada

### Teste Apenas Web Search

```json
{
  "message": "Qual a previsão do tempo para hoje?",
  "session_id": "web-only-test",
  "use_rag": false,
  "use_web_search": true
}
```

### Teste Apenas LLM Base

```json
{
  "message": "Como consertar uma torneira?",
  "session_id": "llm-only-test",
  "use_rag": false,
  "use_web_search": false
}
```

---

## 🎯 Fluxo Completo de Teste

### Cenário: Usuário com Problema

1. **Nova Conversa** - Usuário reporta problema

   ```json
   {
     "message": "Minha torneira está pingando",
     "session_id": "flow-test-001"
   }
   ```

   **Estado esperado**: `waiting_feedback`

2. **Feedback Negativo** - Primeira tentativa falhou

   ```json
   {
     "message": "Não funcionou",
     "session_id": "flow-test-001"
   }
   ```

   **Estado esperado**: `waiting_feedback` (tentativa 2)

3. **Feedback Positivo** - Problema resolvido

   ```json
   {
     "message": "Agora funcionou!",
     "session_id": "flow-test-001"
   }
   ```

   **Estado esperado**: `resolved`

4. **Novo Problema** - Usuário tem outro problema

   ```json
   {
     "message": "Agora o chuveiro não esquenta",
     "session_id": "flow-test-001"
   }
   ```

   **Estado esperado**: `new_problem`

---

## 📊 Validação de Respostas

### Status Codes

| Code | Situação |
|------|----------|
| 200 | ✅ Sucesso |
| 400 | ❌ Dados inválidos (verifica JSON) |
| 404 | ❌ Sessão não encontrada |
| 500 | ❌ Erro no servidor (verifica logs) |

### Verificar Metadados

Na resposta, sempre verifique:

```json
{
  "metadata": {
    "rag_enabled": true,        // RAG está ativo?
    "web_search_enabled": false, // Web search está ativo?
    "current_attempt": 1,        // Quantas tentativas?
    "max_attempts": 3            // Limite de tentativas
  }
}
```

---

## 🐛 Troubleshooting

### Erro: Connection Refused

```bash
# Verificar se API está rodando
docker compose ps

# Ver logs
docker compose logs api
```

### Erro: 400 Bad Request

Verifique o JSON:

- Campos obrigatórios: `message`, `session_id`
- `message` deve ter entre 1-2000 caracteres
- JSON deve estar bem formatado

### Resposta Demora Muito

- RAG pode levar 5-10 segundos (primeira vez)
- Web search adiciona 2-5 segundos
- LLM base responde em 2-3 segundos

---

## 💡 Dicas

### Postman

1. **Salve os Requests**: Crie uma Collection
2. **Use Variáveis**: `{{base_url}}` = `http://localhost:5000`
3. **Testes Automáticos**: Adicione scripts de validação
4. **Ambientes**: Dev, Staging, Production

### Swagger

1. **Mais Rápido**: Interface integrada
2. **Documentação**: Vê schemas automaticamente
3. **Validação**: Valida antes de enviar
4. **Download**: Baixe spec OpenAPI

---

## 📝 Collection Postman (Exportar)

Cole este JSON no Postman (Import > Raw text):

```json
{
  "info": {
    "name": "Repair Agent API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Send Message",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"Como consertar uma torneira pingando?\",\n  \"session_id\": \"postman-test-001\",\n  \"use_rag\": true,\n  \"use_web_search\": false\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/v1/chat/message",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "v1", "chat", "message"]
        }
      }
    },
    {
      "name": "List Sessions",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5000/api/v1/chat/sessions",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "v1", "chat", "sessions"]
        }
      }
    },
    {
      "name": "Reset Session",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "http://localhost:5000/api/v1/chat/reset/postman-test-001",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "v1", "chat", "reset", "postman-test-001"]
        }
      }
    }
  ]
}
```

---

## 🎉 Pronto para Testar

1. **Swagger**: <http://localhost:5000/docs> (Mais fácil!)
2. **Postman**: Importe a collection acima
3. **cURL**: Use os exemplos do `test_api.py`

Boa sorte com os testes! 🚀
