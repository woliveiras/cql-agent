#!/usr/bin/env python3
"""
Script de teste da API REST
Valida todos os endpoints e funcionalidades
"""

import requests
import time
import sys

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v1"


def print_test(name, success, details=""):
    """Imprime resultado do teste"""
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")


# ============================================================================
# Helper functions
# ============================================================================

def check_health():
    """Verifica endpoint de health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        data = response.json()
        print_test("Health Check", success, f"Status: {data.get('status')}")
        return success
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False


def check_swagger():
    """Verifica se documentação Swagger está disponível"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        success = response.status_code == 200
        print_test("Swagger Documentation", success, f"{BASE_URL}/docs")
        return success
    except Exception as e:
        print_test("Swagger Documentation", False, str(e))
        return False


def send_chat_message():
    """Envia mensagem ao agente"""
    try:
        payload = {
            "message": "Como consertar uma torneira pingando?",
            "session_id": "test-session-001",
            "use_rag": True,
            "use_web_search": False  # Desabilitar web para teste mais rápido
        }

        print("\n📨 Enviando mensagem para API...")
        response = requests.post(
            f"{API_BASE}/chat/message",
            json=payload,
            timeout=60
        )

        success = response.status_code == 200

        if success:
            data = response.json()
            print_test("Chat Message", True, f"Sessão: {data.get('session_id')}")
            print("\n💬 Resposta do agente:")
            print(f"   {data.get('response', '')[:200]}...")
            print("\n📊 Metadados:")
            print(f"   Estado: {data.get('state')}")
            print(f"   RAG: {data.get('metadata', {}).get('rag_enabled')}")
            return True, data.get('session_id')
        else:
            print_test("Chat Message", False, f"Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None

    except Exception as e:
        print_test("Chat Message", False, str(e))
        return False, None


def list_sessions():
    """Lista sessões ativas"""
    try:
        response = requests.get(f"{API_BASE}/chat/sessions", timeout=5)
        success = response.status_code == 200

        if success:
            data = response.json()
            total = data.get('total', 0)
            print_test("List Sessions", True, f"Total de sessões: {total}")
            return success
        else:
            print_test("List Sessions", False, f"Status: {response.status_code}")
            return False

    except Exception as e:
        print_test("List Sessions", False, str(e))
        return False


def reset_session(session_id):
    """Reseta uma sessão específica (helper function)"""
    try:
        response = requests.delete(
            f"{API_BASE}/chat/reset/{session_id}",
            timeout=5
        )
        success = response.status_code == 200
        print_test(f"Reset Session ({session_id})", success)
        return success
    except Exception as e:
        print_test(f"Reset Session ({session_id})", False, str(e))
        return False


def main():
    """Executa todos os testes"""
    print("=" * 70)
    print("🧪 TESTE DA API REST - CQL Assistant")
    print("=" * 70)

    # Aguardar API iniciar
    print("\n⏳ Verificando se API está disponível...")
    time.sleep(1)

    print("\n" + "=" * 70)
    print("📡 TESTES DE ENDPOINTS")
    print("=" * 70 + "\n")

    # Testes básicos
    results = []

    results.append(("Health Check", check_health()))
    results.append(("Swagger Docs", check_swagger()))

    # Teste de chat (mais demorado)
    print("\n" + "=" * 70)
    print("💬 TESTE DE CONVERSAÇÃO")
    print("=" * 70)

    chat_success, session_id = send_chat_message()
    results.append(("Chat Message", chat_success))

    # Testes de gerenciamento
    print("\n" + "=" * 70)
    print("🔧 TESTES DE GERENCIAMENTO")
    print("=" * 70 + "\n")

    results.append(("List Sessions", list_sessions()))

    if session_id:
        results.append(("Reset Session", reset_session(session_id)))

    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70 + "\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    print(f"\n{'=' * 70}")
    print(f"Resultado: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 Todos os testes passaram!")
        print("=" * 70)
        return 0
    else:
        print("⚠️  Alguns testes falharam")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
