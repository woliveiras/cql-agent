#!/bin/bash

# Script para testar a API em modo desenvolvimento e produção

set -e

echo "🧪 Teste da API Repair Agent"
echo "========================================================="

API_URL="${API_URL:-http://localhost:5000}"
TIMEOUT=5

run_with_timeout() {
    local timeout=$1
    shift
    
    # No macOS, usar perl para simular timeout
    if [[ "$OSTYPE" == "darwin"* ]]; then
        perl -e "alarm $timeout; exec @ARGV" "$@" 2>/dev/null
    else
        timeout "$timeout" "$@"
    fi
}

# Função para verificar se a API está rodando
check_api() {
    echo ""
    echo "🔍 Verificando se API está acessível..."
    
    if run_with_timeout $TIMEOUT curl -sf "$API_URL/health" > /dev/null 2>&1; then
        echo "✅ API está rodando e saudável!"
        curl -s "$API_URL/health" | python3 -m json.tool
        return 0
    else
        echo "❌ API não está acessível em $API_URL"
        return 1
    fi
}

# Função para testar endpoints
test_endpoints() {
    echo ""
    echo "📡 Testando endpoints..."
    
    # Test 1: Health Check
    echo ""
    echo "Test 1: Health Check"
    if curl -sf "$API_URL/health" > /dev/null; then
        echo "✅ Health check passou"
    else
        echo "❌ Health check falhou"
        return 1
    fi
    
    # Test 2: Swagger Docs
    echo ""
    echo "Test 2: Swagger Documentation"
    if curl -sf "$API_URL/docs" > /dev/null; then
        echo "✅ Swagger docs acessível"
    else
        echo "❌ Swagger docs inacessível"
        return 1
    fi
    
    # Test 3: Send Message
    echo ""
    echo "Test 3: Send Chat Message"
    RESPONSE=$(curl -sf -X POST "$API_URL/api/v1/chat/message" \
        -H "Content-Type: application/json" \
        -d '{
            "message": "Como consertar uma torneira?",
            "session_id": "test-session"
        }' || echo "")
    
    if [ -n "$RESPONSE" ]; then
        echo "✅ Chat endpoint passou"
        echo "$RESPONSE" | python3 -m json.tool | head -15
    else
        echo "❌ Chat endpoint falhou"
        return 1
    fi
    
    # Test 4: List Sessions
    echo ""
    echo "Test 4: List Sessions"
    SESSIONS=$(curl -sf "$API_URL/api/v1/chat/sessions" || echo "")
    
    if [ -n "$SESSIONS" ]; then
        echo "✅ Sessions endpoint passou"
        echo "$SESSIONS" | python3 -m json.tool
    else
        echo "❌ Sessions endpoint falhou"
        return 1
    fi
    
    # Test 5: Reset Session
    echo ""
    echo "Test 5: Reset Session"
    if curl -sf -X DELETE "$API_URL/api/v1/chat/reset/test-session" > /dev/null; then
        echo "✅ Reset endpoint passou"
    else
        echo "❌ Reset endpoint falhou"
        return 1
    fi
}

# Função para testar performance
test_performance() {
    echo ""
    echo "⚡ Teste de Performance (10 requisições)"
    
    echo ""
    echo "Enviando 10 requisições ao /health..."
    
    TOTAL_TIME=0
    SUCCESS_COUNT=0
    
    for i in {1..10}; do
        if [[ "$OSTYPE" == "darwin"* ]]; then
            START=$(perl -MTime::HiRes=time -e 'printf "%.0f\n", time * 1000')
        else
            START=$(date +%s%3N)
        fi
        
        if curl -sf "$API_URL/health" > /dev/null 2>&1; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                END=$(perl -MTime::HiRes=time -e 'printf "%.0f\n", time * 1000')
            else
                END=$(date +%s%3N)
            fi
            DURATION=$(($END - $START))
            TOTAL_TIME=$(($TOTAL_TIME + $DURATION))
            SUCCESS_COUNT=$(($SUCCESS_COUNT + 1))
            echo "  Request $i: ${DURATION}ms"
        else
            echo "  Request $i: FAILED"
        fi
    done
    
    if [ $SUCCESS_COUNT -gt 0 ]; then
        AVG_TIME=$(($TOTAL_TIME / $SUCCESS_COUNT))
        echo ""
        echo "📊 Resultado:"
        echo "  - Sucesso: $SUCCESS_COUNT/10"
        echo "  - Tempo médio: ${AVG_TIME}ms"
        
        if [ $AVG_TIME -lt 100 ]; then
            echo "  - Performance: 🔥 Excelente"
        elif [ $AVG_TIME -lt 500 ]; then
            echo "  - Performance: ✅ Boa"
        else
            echo "  - Performance: ⚠️ Aceitável"
        fi
    fi
}

main() {
    echo ""
    echo "Testando: $API_URL"
    echo ""
    
    # Verificar se API está rodando
    if ! check_api; then
        echo ""
        echo "❌ Testes abortados: API não está rodando"
        echo ""
        echo "Para iniciar a API:"
        echo "  Desenvolvimento: uv run flask --app api.app run --debug"
        echo "  Produção: uv run gunicorn --config api/gunicorn.conf.py api.app:app"
        echo "  Docker: docker-compose up -d"
        exit 1
    fi
    
    # Testar endpoints
    if test_endpoints; then
        echo ""
        echo "✅ Todos os testes de endpoints passaram!"
    else
        echo ""
        echo "❌ Alguns testes falharam"
        exit 1
    fi
    
    # Testar performance
    test_performance
    
    echo ""
    echo "========================================================="
    echo "✅ Testes concluídos com sucesso!"
    echo ""
    echo "🌐 Acesse a documentação: $API_URL/docs"
    echo ""
}

# Executar
main
