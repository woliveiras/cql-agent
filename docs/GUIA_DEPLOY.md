# 🚀 Guia de Deploy e Execução

Este guia explica como executar a API em diferentes ambientes.

## 📋 Índice

- [Desenvolvimento](#-desenvolvimento)
- [Produção Local](#-produção-local)
- [Produção Docker](#-produção-docker)
- [Configurações Avançadas](#-configurações-avançadas)
- [Monitoramento](#-monitoramento)

---

## 🔧 Desenvolvimento

### Modo 1: Uvicorn Development Server (Recomendado)

**Ideal para:** Desenvolvimento ativo com hot reload

```bash
# Iniciar servidor de desenvolvimento
uv run uvicorn api.app:app --reload --host 0.0.0.0 --port 5000

# ✅ Auto-reload habilitado
# ✅ Async/await nativo
# ✅ Performance otimizada
# ✅ Logs coloridos e detalhados
```

### Modo 2: Uvicorn com Log Debug

**Ideal para:** Debugging detalhado

```bash
# Iniciar com logs verbosos
uv run uvicorn api.app:app --reload --log-level debug --port 5000

# Com variáveis de ambiente
PYTHONPATH=. uv run uvicorn api.app:app --reload
```

**Recursos:**

- ✅ Auto-reload ao salvar arquivos
- ✅ Stack traces detalhados
- ✅ Suporte async/await
- ✅ Ideal para TDD

### Modo 3: Uvicorn com Múltiplos Workers (Teste de Produção)

**Ideal para:** Testar em ambiente similar a produção

```bash
# Uvicorn com múltiplos workers
uv run uvicorn api.app:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 2 \
  --log-level info
```

**Recursos:**

- ✅ Múltiplos workers
- ✅ Logs estruturados
- ⚡ Mais próximo de produção

---

## 🚀 Produção Local

### Modo 1: Uvicorn Production (Recomendado)

**Ideal para:** Produção local, testes de carga

```bash
# Iniciar com múltiplos workers
uv run uvicorn api.app:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 4 \
  --log-level info

# Workers são calculados automaticamente: (CPU cores × 2) + 1
# Logs vão para stdout/stderr
```

**Customizar workers:**

```bash
# Forçar 4 workers
uv run uvicorn api.app:app --workers 4 --host 0.0.0.0 --port 5000

# Forçar 8 workers com log warning
uv run uvicorn api.app:app --workers 8 --log-level warning --host 0.0.0.0 --port 5000
```

### Modo 2: Uvicorn com Gunicorn (Máxima Performance)

**Ideal para:** Alta concorrência e performance

```bash
# Usando Gunicorn como process manager com Uvicorn workers
uv run gunicorn api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --timeout 30 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### Verificar Status

```bash
# Health check
curl http://localhost:5000/health

# Verificar workers (outro terminal)
ps aux | grep uvicorn

# Testar carga (requer wrk ou ab)
wrk -t4 -c100 -d30s http://localhost:5000/health
```

---

## 🐳 Produção Docker

### Deploy Completo (Docker Compose)

**Ideal para:** Produção completa (Ollama + API + OpenWebUI)

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Logs da API
docker-compose logs -f api

# Verificar health
docker inspect --format='{{.State.Health.Status}}' repair-agent-api

# Parar serviços
docker-compose down
```

### Build e Run Manual

**Ideal para:** Deploy customizado

```bash
# Build da imagem
docker build -f Dockerfile.api -t repair-agent-api:latest .

# Run com variáveis de ambiente
docker run -d \
  --name repair-agent-api \
  -p 5000:5000 \
  -e UVICORN_WORKERS=4 \
  -e LOG_LEVEL=info \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v $(pwd)/chroma_db:/app/chroma_db:ro \
  -v $(pwd)/pdfs:/app/pdfs:ro \
  repair-agent-api:latest

# Verificar logs
docker logs -f repair-agent-api

# Health check
docker exec repair-agent-api curl -f http://localhost:5000/health
```

### Escalar Workers

```bash
# No docker-compose.yml, adicionar:
services:
  api:
    environment:
      - UVICORN_WORKERS=8  # Customizar

# Ou via linha de comando para testes
docker run -e UVICORN_WORKERS=8 ...
```

---

## ⚙️ Configurações Avançadas

### Uvicorn com Systemd (Linux)

**Ideal para:** Servidores Linux dedicados

```bash
# Criar arquivo /etc/systemd/system/repair-agent-api.service
sudo nano /etc/systemd/system/repair-agent-api.service
```

```ini
[Unit]
Description=Repair Agent API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/repair-agent
Environment="PATH=/opt/repair-agent/.venv/bin"
ExecStart=/opt/repair-agent/.venv/bin/uvicorn \
  api.app:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 4 \
  --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable repair-agent-api
sudo systemctl start repair-agent-api

# Verificar status
sudo systemctl status repair-agent-api

# Logs
sudo journalctl -u repair-agent-api -f
```

### Nginx Reverse Proxy

**Ideal para:** Produção com múltiplas aplicações

```nginx
# /etc/nginx/sites-available/repair-agent-api
upstream repair_api {
    server localhost:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name api.repair-agent.com;

    location / {
        proxy_pass http://repair_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /health {
        proxy_pass http://repair_api/health;
        access_log off;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/repair-agent-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Configuração com SSL (Let's Encrypt)

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d api.repair-agent.com

# Renovar automaticamente (crontab)
0 0 * * * certbot renew --quiet
```

---

## 📊 Monitoramento

### Health Checks

```bash
# Verificar se API está saudável
curl -f http://localhost:5000/health || echo "Unhealthy"

# Com timeout
timeout 5 curl -f http://localhost:5000/health

# Loop contínuo (monitoramento)
watch -n 5 'curl -s http://localhost:5000/health | jq'
```

### Logs

```bash
# Desenvolvimento (Uvicorn)
# Logs vão automaticamente para console com cores

# Produção (Uvicorn)
# Logs vão para stdout/stderr por padrão

# Docker
docker-compose logs -f api
docker logs -f repair-agent-api

# Filtrar erros
docker logs repair-agent-api 2>&1 | grep ERROR

# Últimas 100 linhas
docker logs --tail 100 repair-agent-api
```

### Métricas de Performance

```bash
# Processos e memória
ps aux | grep uvicorn

# CPU e RAM (htop)
htop -p $(pgrep -f uvicorn)

# Requests por segundo (com wrk)
wrk -t4 -c100 -d30s --latency http://localhost:5000/health

# Apache Bench
ab -n 1000 -c 10 http://localhost:5000/health
```

### Alertas com Healthcheck

**Script de monitoramento simples:**

```bash
#!/bin/bash
# monitor.sh

while true; do
    if ! curl -sf http://localhost:5000/health > /dev/null; then
        echo "$(date): API is DOWN!" | tee -a /var/log/repair-api-monitor.log
        # Enviar alerta (email, Slack, etc)
    fi
    sleep 60
done
```

---

## 🔄 Graceful Restart

### Uvicorn

```bash
# HUP: Reload workers (zero downtime)
kill -HUP <master_pid>

# TERM: Graceful shutdown (espera requisições terminarem)
kill -TERM <master_pid>

# Docker
docker kill -s HUP repair-agent-api

# Docker Compose
docker-compose kill -s HUP api
```

### Systemd

```bash
# Reload (zero downtime)
sudo systemctl reload repair-agent-api

# Restart
sudo systemctl restart repair-agent-api
```

---

## 🐛 Troubleshooting

### API não inicia

```bash
# Verificar porta ocupada
lsof -i :5000

# Verificar dependências
uv pip list | grep -E 'fastapi|uvicorn'

# Verificar Ollama
curl http://localhost:11434/api/tags
```

### Workers morrem constantemente

```bash
# Aumentar timeout
uv run uvicorn api.app:app --timeout-keep-alive 60 --workers 4

# Verificar logs
docker logs repair-agent-api
```

### Performance ruim

```bash
# Aumentar workers
uv run uvicorn api.app:app --workers 8

# Verificar CPU
htop

# Verificar memória
free -h
```

### Logs não aparecem

```bash
# Forçar unbuffered output
PYTHONUNBUFFERED=1 uv run uvicorn api.app:app

# Docker
docker run -e PYTHONUNBUFFERED=1 ...
```
