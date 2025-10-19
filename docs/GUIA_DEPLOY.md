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

### Modo 1: Flask Development Server (Mais simples)

**Ideal para:** Testes rápidos, debugging

```bash
# Iniciar servidor de desenvolvimento
uv run python -m api.app

# ✅ Auto-reload habilitado
# ✅ Debug mode ativo
# ✅ Stack traces detalhados
# ⚠️ Single-threaded (não usar em produção)
```

### Modo 2: Flask CLI (Recomendado para dev)

**Ideal para:** Desenvolvimento ativo com debugging

```bash
# Iniciar com Flask CLI
uv run flask --app api.app run --debug --port 5000

# Com host customizado
uv run flask --app api.app run --debug --host 0.0.0.0

# Com variáveis de ambiente
FLASK_ENV=development uv run flask --app api.app run --debug
```

**Recursos:**

- ✅ Auto-reload ao salvar arquivos
- ✅ Debugger interativo no navegador
- ✅ Variáveis de ambiente automáticas
- ✅ Ideal para TDD

### Modo 3: Gunicorn com Reload

**Ideal para:** Testar em ambiente similar a produção

```bash
# Gunicorn com reload
uv run gunicorn --config api/gunicorn.conf.py \
  --reload \
  --log-level debug \
  --workers 2 \
  api.app:app
```

**Recursos:**

- ✅ Auto-reload
- ✅ Múltiplos workers
- ✅ Logs detalhados
- ⚡ Mais próximo de produção

---

## 🚀 Produção Local

### Modo 1: Gunicorn com Configuração (Recomendado)

**Ideal para:** Produção local, testes de carga

```bash
# Iniciar com configuração padrão
uv run gunicorn --config api/gunicorn.conf.py api.app:app

# Workers são calculados automaticamente: (CPU cores × 2) + 1
# Logs vão para stdout/stderr
# Health checks habilitados
```

**Customizar workers:**

```bash
# Forçar 4 workers
GUNICORN_WORKERS=4 uv run gunicorn --config api/gunicorn.conf.py api.app:app

# Forçar 8 workers com log warning
GUNICORN_WORKERS=8 LOG_LEVEL=warning \
  uv run gunicorn --config api/gunicorn.conf.py api.app:app
```

### Modo 2: Gunicorn Inline (Sem config)

**Ideal para:** Testes rápidos de produção

```bash
# Configuração inline
uv run gunicorn api.app:app \
  --workers 4 \
  --worker-class sync \
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
ps aux | grep gunicorn

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
  -e GUNICORN_WORKERS=4 \
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
      - GUNICORN_WORKERS=8  # Customizar

# Ou via linha de comando para testes
docker run -e GUNICORN_WORKERS=8 ...
```

---

## ⚙️ Configurações Avançadas

### Gunicorn com Systemd (Linux)

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
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/repair-agent
Environment="PATH=/opt/repair-agent/.venv/bin"
ExecStart=/opt/repair-agent/.venv/bin/gunicorn \
  --config /opt/repair-agent/api/gunicorn.conf.py \
  api.app:app
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
# Desenvolvimento (Flask)
# Logs vão automaticamente para console

# Produção (Gunicorn)
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
ps aux | grep gunicorn

# CPU e RAM (htop)
htop -p $(pgrep -f gunicorn)

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

### Gunicorn

```bash
# HUP: Reload configuração e código (zero downtime)
kill -HUP <master_pid>

# TERM: Graceful shutdown (espera requisições terminarem)
kill -TERM <master_pid>

# QUIT: Graceful shutdown com timeout
kill -QUIT <master_pid>

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
uv pip list | grep -E 'flask|gunicorn'

# Verificar Ollama
curl http://localhost:11434/api/tags
```

### Workers morrem constantemente

```bash
# Aumentar timeout
GUNICORN_TIMEOUT=60 uv run gunicorn ...

# Ou editar api/gunicorn.conf.py:
timeout = 60
```

### Performance ruim

```bash
# Aumentar workers
GUNICORN_WORKERS=8 uv run gunicorn ...

# Verificar CPU
htop

# Verificar memória
free -h
```

### Logs não aparecem

```bash
# Forçar unbuffered output
PYTHONUNBUFFERED=1 uv run gunicorn ...

# Docker
docker run -e PYTHONUNBUFFERED=1 ...
```
