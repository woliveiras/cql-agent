# Dockerfile para a API
FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema e uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copiar arquivos de dependências
COPY pyproject.toml ./

# Instalar dependências usando uv
RUN uv pip install --system --no-cache -r pyproject.toml

# Copiar código da aplicação
COPY agents/ ./agents/
COPY api/ ./api/

# Criar diretórios necessários
RUN mkdir -p /app/chroma_db /app/pdfs

# Expor porta
EXPOSE 5000

ENV PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=4 \
    LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
