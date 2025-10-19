"""
Configuração do Gunicorn para Repair Agent API
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "repair-agent-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (desabilitado por padrão, configurar se necessário)
keyfile = None
certfile = None

# Reload
reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"
reload_engine = "auto"

# Preload app (melhora performance)
preload_app = True

# Lifecycle hooks
def on_starting(server):
    """Executado quando o Gunicorn inicia"""
    server.log.info("🚀 Gunicorn starting...")

def when_ready(server):
    """Executado quando o servidor está pronto para aceitar conexões"""
    server.log.info("✅ Gunicorn ready. Workers: %s", workers)

def on_reload(server):
    """Executado quando o servidor recarrega"""
    server.log.info("🔄 Gunicorn reloading...")

def worker_int(worker):
    """Executado quando o worker recebe SIGINT ou SIGQUIT"""
    worker.log.info("⚠️ Worker received INT or QUIT signal")

def worker_abort(worker):
    """Executado quando o worker recebe SIGABRT"""
    worker.log.info("❌ Worker received SIGABRT signal")

def pre_fork(server, worker):
    """Executado antes de fazer fork de um worker"""
    pass

def post_fork(server, worker):
    """Executado após fazer fork de um worker"""
    server.log.info("👷 Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Executado após inicialização do worker"""
    worker.log.info("🔧 Worker initialized")

def worker_exit(server, worker):
    """Executado quando um worker termina"""
    server.log.info("👋 Worker exiting (pid: %s)", worker.pid)

def child_exit(server, worker):
    """Executado quando um worker filho termina"""
    pass

def on_exit(server):
    """Executado quando o Gunicorn termina"""
    server.log.info("🛑 Gunicorn shutting down...")
