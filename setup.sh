#!/bin/bash

# Script de setup para o projeto de Agente de Reparos Residenciais

set -e

echo "🔧 Configurando o CQL AI Agent"
echo "========================================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está disponível. Por favor, instale o Docker Compose."
    exit 1
fi

echo ""
echo "✅ Docker e Docker Compose encontrados"

# Iniciar Ollama
echo ""
echo "🚀 Iniciando container do Ollama..."
docker-compose up -d

echo ""
echo "⏳ Aguardando Ollama inicializar..."
sleep 5

# Verificar se Ollama está rodando
if ! docker ps | grep -q ollama; then
    echo "❌ Ollama não está rodando. Verifique os logs com: docker-compose logs"
    exit 1
fi

echo "✅ Ollama está rodando"

# Baixar modelo
echo ""
echo "📥 Baixando modelo qwen2.5:3b (isso pode demorar alguns minutos)..."
docker exec -it ollama ollama pull qwen2.5:3b

echo ""
echo "✅ Setup completo!"
echo ""
echo "Para executar o agente:"
echo "  uv run agent.py"
echo ""
echo "Para parar o Ollama:"
echo "  docker-compose down"
echo ""
