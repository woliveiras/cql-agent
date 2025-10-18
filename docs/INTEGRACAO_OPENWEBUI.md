# 🔗 Integração OpenWebUI + API Flask

Este documento explica como integrar o web server Flask com o OpenWebUI usando Pipe Functions.

## 📋 Índice

- [Como Funciona](#como-funciona)
- [Configuração Inicial](#configuração-inicial)
- [Usando a Pipe Function](#usando-a-pipe-function)
- [Modelos Disponíveis](#modelos-disponíveis)
- [Configurações Avançadas](#configurações-avançadas)
- [Troubleshooting](#troubleshooting)

---

## 🔄 Como Funciona

A integração usa o padrão **Pipe Function** do OpenWebUI:

```text
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌─────────┐
│  OpenWebUI  │─────▶│ Pipe Function│─────▶│  Flask API  │─────▶│ Ollama  │
│  (Frontend) │      │  (pipe.py)   │      │ (port 5000) │      │(LLM)    │
└─────────────┘      └──────────────┘      └─────────────┘      └─────────┘
     ▲                                             │
     │                                             │
     └─────────────────────────────────────────────┘
                    Resposta formatada
```

### Fluxo de Dados

1. **Usuário** envia mensagem no OpenWebUI
2. **OpenWebUI** encaminha para a Pipe Function (`pipe.py`)
3. **Pipe Function** faz requisição HTTP POST para Flask API
4. **Flask API** processa com RepairAgent (RAG + Web Search + LLM)
5. **Flask API** retorna resposta em JSON
6. **Pipe Function** formata e retorna para OpenWebUI
7. **OpenWebUI** exibe para o usuário

---

## ⚙️ Configuração Inicial

### 1. Verificar Docker Compose

Certifique-se que o `docker-compose.yml` está configurado corretamente:

```yaml
services:
  api:
    # ... outras configurações
    networks:
      - repair-network
    ports:
      - "5000:5000"

  openwebui:
    # ... outras configurações
    networks:
      - repair-network
    depends_on:
      - api
    volumes:
      - ./openwebui/pipe.py:/app/backend/pipes/repair_agent_pipe.py:ro
```

**Pontos importantes:**

- ✅ Ambos os serviços na mesma network (`repair-network`)
- ✅ OpenWebUI depende da API (`depends_on`)
- ✅ Volume bind da Pipe Function montado corretamente

### 2. Iniciar os Serviços

```bash
docker compose up -d
```

Verificar se tudo está rodando:

```bash
docker compose ps
```

Você deve ver:

- ✅ `repair-agent-ollama` (UP)
- ✅ `repair-agent-api` (UP)
- ✅ `repair-agent-openwebui` (UP, healthy)

### 3. Testar Conectividade

Teste se o OpenWebUI consegue acessar a API:

```bash
# Do container do OpenWebUI, tentar acessar a API
docker exec repair-agent-openwebui curl -s http://api:5000/health
```

Se retornar JSON com `"status": "healthy"`, está funcionando! ✅

---

## 🚀 Usando a Pipe Function

### 1. Acessar OpenWebUI

Abra no navegador: **<http://localhost:8080>**

### 2. Carregar a Pipe Function

1. No OpenWebUI na barra lateral esquerda, parte inferior, clique no seu nome de usuário ou "user"
2. Clique em **Admin Panel** 
3. Vá em **Functions**
4. Clique en **+ Create New Function**
5. Copie o conteúdo de `openwebui/pipe.py` para a nova Pipe Function.

### 3. Ativar a Function

1. Encontre **"Repair Agent"** na lista
2. Clique no toggle para **ATIVAR** ✅
3. A function agora está disponível para uso

### 4. Configurar (Opcional)

Clique em **⚙️ Configure** na Pipe Function para ajustar:

- **API_BASE_URL**: URL da API (padrão: `http://api:5000/api/v1`)
- **USE_RAG**: Habilitar RAG por padrão
- **USE_WEB_SEARCH**: Habilitar busca web por padrão
- **SESSION_PREFIX**: Prefixo das sessões (padrão: `openwebui`)
- **TIMEOUT**: Timeout em segundos (padrão: 30)

---

## 🎯 Modelos Disponíveis

A Pipe Function expõe **3 modelos virtuais**:

### 1. **Repair Agent (RAG + Web Search)** 🔍🌐

- **ID**: `repair-agent-rag-web`
- **Recursos**: RAG + Busca Web + LLM
- **Melhor para**: Perguntas complexas que precisam de documentação + informações atualizadas

**Exemplo:**

```sh
👤 Como consertar uma torneira que está pingando?

🤖 [Busca nos PDFs] → [Busca na Web] → [Resposta completa com contexto]
```

### 2. **Repair Agent (RAG Only)** 📚

- **ID**: `repair-agent-rag-only`
- **Recursos**: Apenas RAG + LLM (sem internet)
- **Melhor para**: Perguntas que estão nos PDFs de documentação

**Exemplo:**

```sh
👤 Quais ferramentas preciso para trocar um disjuntor?

🤖 [Busca apenas nos PDFs] → [Resposta baseada na documentação]
```

### 3. **Repair Agent (Base LLM)** 🧠

- **ID**: `repair-agent-base`
- **Recursos**: Apenas LLM (sem RAG, sem Web)
- **Melhor para**: Conversação geral, perguntas simples

**Exemplo:**

```sh
👤 O que significa disjuntor?

🤖 [Resposta direto do modelo LLM]
```

---

## 🔧 Configurações Avançadas

### Modificar a Pipe Function

Edite `openwebui/pipe.py` e reinicie o OpenWebUI:

```bash
# Editar arquivo
nano openwebui/pipe.py

# Reiniciar OpenWebUI
docker compose restart openwebui
```

### Variáveis de Ambiente

Você pode adicionar variáveis de ambiente no `docker-compose.yml`:

```yaml
openwebui:
  environment:
    - REPAIR_API_URL=http://api:5000/api/v1
```

E usar no `pipe.py`:

```python
import os

class Valves(BaseModel):
    API_BASE_URL: str = os.getenv("REPAIR_API_URL", "http://api:5000/api/v1")
```

### Debug Mode

Para ativar informações de debug nas respostas:

1. Edite `pipe.py`
2. Na função `pipe()`, mude:

```python
if body.get("debug", False):  # ← Mude para True
    footer = f"\n\n---\n*Estado: {state} | RAG: {use_rag} | Web: {use_web_search}*"
    agent_response += footer
```

Para:

```python
if True:  # Sempre mostrar debug
    footer = f"\n\n---\n*Estado: {state} | RAG: {use_rag} | Web: {use_web_search}*"
    agent_response += footer
```

### Customizar Modelos

Adicione mais modelos editando `get_models()` em `pipe.py`:

```python
def get_models(self) -> List[dict]:
    return [
        # ... modelos existentes
        {
            "id": "repair-agent-custom",
            "name": "Repair Agent (Custom Mode)"
        }
    ]
```

---

## 🐛 Troubleshooting

### Problema 1: Pipe Function não aparece no OpenWebUI

**Sintomas:**

- Lista de Functions vazia
- "Repair Agent" não aparece

**Soluções:**

1. **Verificar volume montado:**

```bash
docker exec repair-agent-openwebui ls -la /app/backend/pipes/
# Deve mostrar: repair_agent_pipe.py
```

2. **Verificar logs:**

```bash
docker logs repair-agent-openwebui | grep -i pipe
docker logs repair-agent-openwebui | grep -i error
```

3. **Reiniciar OpenWebUI:**

```bash
docker compose restart openwebui
```

4. **Verificar permissões:**

```bash
chmod 644 openwebui/pipe.py
```

---

### Problema 2: Erro de conexão com a API

**Sintomas:**

- Mensagem: "❌ Não foi possível conectar à API"
- Timeout ao enviar mensagem

**Soluções:**

1. **Testar conectividade:**

```bash
docker exec repair-agent-openwebui curl -s http://api:5000/health
```

2. **Verificar se API está rodando:**

```bash
docker compose ps api
docker logs repair-agent-api
```

3. **Verificar URL na Pipe:**

- Abrir OpenWebUI → Settings → Functions → Repair Agent → Configure
- Confirmar `API_BASE_URL = http://api:5000/api/v1`
- **NÃO usar `localhost`** (use o nome do serviço Docker: `api`)

4. **Verificar network:**

```bash
docker network inspect cql-agent_repair-network
# Verificar se ambos containers estão na mesma rede
```

---

### Problema 3: Respostas lentas ou timeout

**Sintomas:**

- Demora muito para responder
- Timeout após 30 segundos

**Soluções:**

1. **Aumentar timeout na Pipe Function:**

```python
class Valves(BaseModel):
    TIMEOUT: int = 60  # ← Aumentar de 30 para 60
```

2. **Verificar recursos do Ollama:**

```bash
docker stats repair-agent-ollama
# Verificar CPU e memória
```

3. **Usar modelo menor:**

- Trocar de `qwen2.5:3b` para `qwen2.5:1.5b`
- Editar `agent.py`:

```python
model_name: str = "qwen2.5:1.5b"
```

---

### Problema 4: RAG não funciona

**Sintomas:**

- Mensagem: "⚠️ RAG não disponível"
- Não encontra informações nos PDFs

**Soluções:**

1. **Verificar ChromaDB:**

```bash
# Verificar se pasta existe e tem permissão
ls -la ./chroma_db/
docker exec repair-agent-api ls -la /app/chroma_db/
```

2. **Recarregar documentos:**

```bash
# Parar API
docker compose stop api

# Apagar ChromaDB (cuidado!)
rm -rf ./chroma_db/*

# Recarregar
docker compose up -d api
docker logs -f repair-agent-api
# Aguardar mensagem: "✅ Vector store carregado"
```

3. **Verificar PDFs:**

```bash
ls -la ./pdfs/
# Deve ter arquivos .pdf
```

---

### Problema 5: Web Search não funciona

**Sintomas:**

- Não busca na internet
- Erro ao fazer busca web

**Soluções:**

1. **Verificar logs:**

```bash
docker logs repair-agent-api | grep -i "web\|duckduckgo"
```

2. **Testar DuckDuckGo:**

```bash
docker exec repair-agent-api python3 -c "
from tools.web_search import search_web
print(search_web('test'))
"
```

3. **Verificar se está habilitado:**

- No OpenWebUI, use o modelo **"Repair Agent (RAG + Web Search)"**
- Ou configure `USE_WEB_SEARCH = True` nas Valves

---

## 📊 Monitoramento

### Logs em Tempo Real

```bash
# Todos os serviços
docker compose logs -f

# Apenas API
docker compose logs -f api

# Apenas OpenWebUI
docker compose logs -f openwebui
```

### Verificar Saúde dos Serviços

```bash
# Health check da API
curl http://localhost:5000/health | jq

# Status dos containers
docker compose ps

# Uso de recursos
docker stats
```

### Ver Sessões Ativas

```bash
# Listar sessões via API
curl http://localhost:5000/api/v1/chat/sessions | jq
```

---

## 🎓 Exemplos de Uso

### Exemplo 1: Pergunta com RAG + Web

```
Modelo: Repair Agent (RAG + Web Search)

👤 Como consertar uma torneira que está pingando?

🤖 Resposta:
Para consertar uma torneira que está pingando, siga estes passos:

1. **Feche o registro de água**
   - Localize o registro sob a pia
   - Gire no sentido horário até fechar completamente

2. **Identifique o tipo de torneira**
   - Torneira de compressão: tem duas alças
   - Torneira monocomando: tem uma única alavanca

... [resposta completa baseada nos PDFs + web]
```

### Exemplo 2: Pergunta apenas com documentação

```
Modelo: Repair Agent (RAG Only)

👤 Quais ferramentas preciso para trocar um disjuntor?

🤖 Resposta baseada nos manuais:
- Chave de fenda isolada
- Alicate
- Multímetro (para testar tensão)
... [informações dos PDFs]
```

### Exemplo 3: Conversa casual

```
Modelo: Repair Agent (Base LLM)

👤 Oi, tudo bem?

🤖 Olá! Tudo ótimo! Como posso ajudá-lo com reparos residenciais hoje?
```

---

## 🔐 Segurança

### Autenticação (Produção)

Para produção, habilite autenticação no OpenWebUI:

```yaml
openwebui:
  environment:
    - WEBUI_AUTH=true  # ← Mudar de false para true
```

### Rate Limiting

Adicione rate limiting na API Flask:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Forwarded-For', request.remote_addr)
)

@api.route('/chat/message')
@limiter.limit("10 per minute")
def chat():
    # ...
```

---

## 📚 Referências

- [OpenWebUI Pipelines Documentation](https://docs.openwebui.com/pipelines/)
- [Flask-RESTX Documentation](https://flask-restx.readthedocs.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

## 🎯 Próximos Passos

1. ✅ **Pipe Function funcionando** - Você está aqui!
2. 🔄 **Testar no OpenWebUI** - Use os 3 modelos
3. 📝 **Customizar respostas** - Edite os prompts
4. 🚀 **Deploy em produção** - Configure autenticação e HTTPS
5. 📊 **Monitoramento** - Adicione métricas e logs

---

**Criado em**: Outubro 2025  
**Projeto**: CQL Agent - Repair Agent com RAG e Web Search  
**Stack**: Flask + OpenWebUI + LangChain + Ollama + ChromaDB
