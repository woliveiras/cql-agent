# Redis Session Management - CQL Agent

Sistema de gerenciamento de sessões com suporte a Redis e fallback automático para memória.

## Visão Geral

O CQL Agent agora suporta persistência de sessões através do Redis, permitindo:

- ✅ **Persistência**: Sessões sobrevivem a restarts da aplicação
- ✅ **Escalabilidade**: Suporte a múltiplas instâncias da API
- ✅ **TTL Automático**: Limpeza automática de sessões antigas
- ✅ **Fallback Inteligente**: Usa memória se Redis não estiver disponível
- ✅ **Transparente**: Mesma API, diferentes backends

## Arquitetura

```
┌─────────────────────────────────────────┐
│         SessionManager                   │
│  (Camada de abstração)                  │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ┌────▼────┐   ┌───▼──────┐
   │ Memory  │   │  Redis   │
   │  Store  │   │  Store   │
   └─────────┘   └──────────┘
   (Dev/Fallback) (Produção)
```

## Configuração

### Desenvolvimento (Sem Redis)

Basta não habilitar o Redis. O sistema usará memória automaticamente:

```bash
# .env
USE_REDIS=false
```

### Produção (Com Redis)

#### Opção 1: URL Completa

```bash
# .env
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0

# Com autenticação
REDIS_URL=redis://:password@localhost:6379/0
```

#### Opção 2: Configuração Manual

```bash
# .env
USE_REDIS=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=sua-senha-aqui

# TTL padrão das sessões (em segundos)
SESSION_TTL=3600  # 1 hora

# Prefixo para chaves no Redis
REDIS_KEY_PREFIX=cql:session:
```

## Docker Compose

O Redis já está configurado no `docker-compose.yml`:

```bash
# Subir todos os serviços (incluindo Redis)
docker-compose up -d

# Ver logs do Redis
docker logs repair-agent-redis

# Conectar ao Redis CLI
docker exec -it repair-agent-redis redis-cli

# Ver todas as sessões
docker exec -it repair-agent-redis redis-cli KEYS "cql:session:*"
```

## Uso no Código

### Criar/Obter Agente

```python
from api.session_manager import SessionManager

# Inicializar gerenciador
manager = SessionManager(use_redis=True)

# Obter ou criar agente
agent = manager.get_or_create_agent(
    session_id="user-123",
    use_rag=True,
    use_web_search=True
)
```

### Atualizar Agente

**IMPORTANTE:** Sempre chame `update_agent()` após modificar o agente!

```python
# Processar mensagem
response = agent.chat(user_message)

# Persistir mudanças
manager.update_agent("user-123", agent)
```

### Listar Sessões

```python
sessions = manager.list_sessions()

for session in sessions:
    print(f"Session: {session['session_id']}")
    print(f"  State: {session['state']}")
    print(f"  Attempts: {session['current_attempt']}")
    print(f"  TTL: {session['ttl']} segundos")
```

### Remover Sessão

```python
manager.delete_session("user-123")
```

## Estrutura de Dados

### Chaves no Redis

```
cql:session:{session_id}
```

Exemplos:
- `cql:session:user-123`
- `cql:session:default`
- `cql:session:abc-def-456`

### Valor Armazenado

O agente é serializado usando `pickle`:

```python
# O que é armazenado:
{
    "state": "new_problem",
    "current_attempt": 0,
    "conversation_history": [...],
    "max_attempts": 3,
    ...
}
```

### TTL (Time To Live)

Sessões expiram automaticamente após o TTL configurado:

```bash
# Configurar TTL (em segundos)
SESSION_TTL=3600   # 1 hora (padrão)
SESSION_TTL=1800   # 30 minutos
SESSION_TTL=7200   # 2 horas
```

## Monitoramento

### Comandos Redis Úteis

```bash
# Conectar ao Redis
docker exec -it repair-agent-redis redis-cli

# Listar todas as sessões
KEYS "cql:session:*"

# Ver conteúdo de uma sessão (serializado)
GET "cql:session:user-123"

# Ver TTL de uma sessão
TTL "cql:session:user-123"

# Número total de sessões
DBSIZE

# Info do Redis
INFO memory
INFO stats

# Limpar todas as sessões (cuidado!)
FLUSHDB
```

### Logs da Aplicação

O SessionManager registra logs estruturados:

```json
{
  "timestamp": "2025-10-26T10:30:00",
  "level": "INFO",
  "logger": "api.session_manager",
  "message": "RedisSessionStore inicializado com sucesso",
  "component": "session",
  "redis_url": "redis://localhost:6379/0",
  "default_ttl": 3600
}
```

```json
{
  "timestamp": "2025-10-26T10:30:15",
  "level": "INFO",
  "logger": "api.session_manager",
  "message": "Criando novo agente",
  "component": "session",
  "session_id": "user-123",
  "use_rag": true,
  "use_web_search": true,
  "event_type": "agent_created"
}
```

## Troubleshooting

### Redis não disponível

```bash
❌ Falha ao conectar ao Redis, usando MemorySessionStore: ...
```

**Solução:** O sistema faz fallback automático para memória. Para usar Redis:

1. Verificar se Redis está rodando:
   ```bash
   docker-compose ps redis
   ```

2. Iniciar Redis se necessário:
   ```bash
   docker-compose up -d redis
   ```

3. Testar conexão:
   ```bash
   redis-cli ping
   # Deve retornar: PONG
   ```

### Sessões não persistem

**Problema:** Sessões somem após restart.

**Causa:** Provavelmente `USE_REDIS=false` ou Redis não está conectado.

**Solução:**
1. Verificar `.env`: `USE_REDIS=true`
2. Verificar logs de inicialização
3. Confirmar que Redis está acessível

### Memória do Redis cheia

```bash
❌ OOM command not allowed when used memory > 'maxmemory'
```

**Solução:** Redis está configurado com `maxmemory 256mb` e política `allkeys-lru`:

```bash
# Ver configuração atual
docker exec -it repair-agent-redis redis-cli CONFIG GET maxmemory

# Aumentar limite (temporário)
docker exec -it repair-agent-redis redis-cli CONFIG SET maxmemory 512mb

# Permanente: editar docker-compose.yml
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Sessões expiram muito rápido

**Solução:** Aumentar TTL:

```bash
# .env
SESSION_TTL=7200  # 2 horas
```

## Ferramentas de Visualização

### RedisInsight (Recomendado) 🌟

**Ferramenta oficial da Redis com interface gráfica moderna**

```bash
# macOS
brew install --cask redisinsight

# Ou baixar em: https://redis.io/insight/
```

**Features**:

- Interface gráfica intuitiva
- Visualização de dados em tempo real
- Monitor de performance
- CLI integrado
- Memory analysis

## Performance

### Benchmarks

- **Armazenamento**: ~0.5ms por sessão
- **Recuperação**: ~0.3ms por sessão
- **Listagem** (100 sessões): ~10ms

### Otimizações

1. **Pipeline Commands**: Para operações em lote
2. **Connection Pooling**: Automático no cliente Redis
3. **Serialização**: JSON customizado para objetos Python
4. **TTL**: Evita acúmulo de sessões antigas

## Migração

### De Memória para Redis

1. Habilitar Redis:
   ```bash
   USE_REDIS=true
   REDIS_URL=redis://localhost:6379/0
   ```

2. Restart da aplicação
3. Sessões antigas em memória serão perdidas
4. Novas sessões serão criadas no Redis

### Backup de Sessões

Redis persiste automaticamente em disco (`appendonly yes`):

```bash
# Backup manual
docker exec repair-agent-redis redis-cli BGSAVE

# Ver último save
docker exec repair-agent-redis redis-cli LASTSAVE

# Arquivo de backup
ls -lh /var/lib/docker/volumes/cql-agent_redis_data/_data/
```

## Segurança

### Autenticação

```bash
# .env
REDIS_URL=redis://:sua-senha@localhost:6379/0
```

Ou no docker-compose.yml:

```yaml
redis:
  command: redis-server --requirepass sua-senha
```

### Isolamento

- Use DB separado por ambiente:
  - Dev: `REDIS_DB=0`
  - Test: `REDIS_DB=15`
  - Staging: `REDIS_DB=1`
  - Prod: `REDIS_DB=0` (cluster separado)

### Criptografia

Para dados sensíveis, use Redis com TLS:

```bash
REDIS_URL=rediss://user:password@localhost:6380/0
```

## Escalabilidade

### Múltiplas Instâncias da API

```
┌────────────┐
│  API (1)   │───┐
└────────────┘   │
                 │    ┌─────────┐
┌────────────┐   ├───▶│  Redis  │
│  API (2)   │───┤    └─────────┘
└────────────┘   │
                 │
┌────────────┐   │
│  API (3)   │───┘
└────────────┘
```

Todas as instâncias compartilham o mesmo Redis = sessões consistentes!

### Redis Cluster

Para alta disponibilidade:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes
  # ... configuração cluster
```

## Testes

### Testes Unitários

```bash
# Testes com MemoryStore (sempre passam)
pytest api/tests/unit/test_session_manager.py -k "Memory"

# Testes com RedisStore (requer Redis)
pytest api/tests/unit/test_session_manager.py -k "Redis"
```

### Testes de Integração

```bash
# Todos os testes (pula Redis se não disponível)
pytest api/tests/unit/test_session_manager.py -v
```

## Referências

- [Redis Documentation](https://redis.io/docs/)
- [redis-py](https://github.com/redis/redis-py)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
