"""
Testes para o sistema de fingerprinting
"""

import pytest
from fastapi import Request
from api.auth.fingerprint import generate_fingerprint, get_client_info, _get_real_ip


class MockClient:
    """Mock de request.client"""
    def __init__(self, host: str):
        self.host = host


class MockRequest:
    """Mock de FastAPI Request"""
    def __init__(self, headers: dict, client_host: str = "192.168.1.1"):
        self.headers = headers
        self.client = MockClient(client_host)


def test_generate_fingerprint_basic():
    """Testa geração de fingerprint básico"""
    request = MockRequest(
        headers={
            'user-agent': 'Mozilla/5.0',
            'accept-language': 'pt-BR,pt;q=0.9'
        }
    )

    fingerprint = generate_fingerprint(request)

    assert isinstance(fingerprint, str)
    assert len(fingerprint) == 64  # SHA256 hex = 64 caracteres


def test_generate_fingerprint_consistency():
    """Testa que o mesmo request gera o mesmo fingerprint"""
    request1 = MockRequest(
        headers={
            'user-agent': 'Mozilla/5.0',
            'accept-language': 'pt-BR'
        }
    )
    request2 = MockRequest(
        headers={
            'user-agent': 'Mozilla/5.0',
            'accept-language': 'pt-BR'
        }
    )

    fp1 = generate_fingerprint(request1)
    fp2 = generate_fingerprint(request2)

    assert fp1 == fp2


def test_generate_fingerprint_different_user_agent():
    """Testa que user-agents diferentes geram fingerprints diferentes"""
    request1 = MockRequest(
        headers={
            'user-agent': 'Mozilla/5.0',
            'accept-language': 'pt-BR'
        }
    )
    request2 = MockRequest(
        headers={
            'user-agent': 'Chrome/90.0',
            'accept-language': 'pt-BR'
        }
    )

    fp1 = generate_fingerprint(request1)
    fp2 = generate_fingerprint(request2)

    assert fp1 != fp2


def test_generate_fingerprint_different_ip():
    """Testa que IPs diferentes geram fingerprints diferentes"""
    request1 = MockRequest(
        headers={'user-agent': 'Mozilla/5.0'},
        client_host="192.168.1.1"
    )
    request2 = MockRequest(
        headers={'user-agent': 'Mozilla/5.0'},
        client_host="192.168.1.2"
    )

    fp1 = generate_fingerprint(request1)
    fp2 = generate_fingerprint(request2)

    assert fp1 != fp2


def test_get_real_ip_direct():
    """Testa obtenção de IP direto"""
    request = MockRequest(
        headers={},
        client_host="192.168.1.100"
    )

    ip = _get_real_ip(request)
    assert ip == "192.168.1.100"


def test_get_real_ip_x_forwarded_for():
    """Testa obtenção de IP via X-Forwarded-For"""
    request = MockRequest(
        headers={'x-forwarded-for': '203.0.113.1, 198.51.100.1'},
        client_host="192.168.1.1"
    )

    ip = _get_real_ip(request)
    assert ip == "203.0.113.1"  # Primeiro IP da lista


def test_get_real_ip_x_real_ip():
    """Testa obtenção de IP via X-Real-IP"""
    request = MockRequest(
        headers={'x-real-ip': '203.0.113.5'},
        client_host="192.168.1.1"
    )

    ip = _get_real_ip(request)
    assert ip == "203.0.113.5"


def test_get_real_ip_priority():
    """Testa prioridade: X-Forwarded-For > X-Real-IP > client.host"""
    request = MockRequest(
        headers={
            'x-forwarded-for': '203.0.113.1',
            'x-real-ip': '203.0.113.2'
        },
        client_host="192.168.1.1"
    )

    ip = _get_real_ip(request)
    assert ip == "203.0.113.1"  # X-Forwarded-For tem prioridade


def test_get_client_info():
    """Testa extração de informações do cliente"""
    request = MockRequest(
        headers={
            'user-agent': 'Mozilla/5.0',
            'accept-language': 'pt-BR',
            'referer': 'https://example.com'
        }
    )

    info = get_client_info(request)

    assert 'ip' in info
    assert 'user_agent' in info
    assert 'accept_language' in info
    assert 'referer' in info
    assert 'fingerprint' in info
    assert info['user_agent'] == 'Mozilla/5.0'
    assert info['accept_language'] == 'pt-BR'
    assert info['referer'] == 'https://example.com'


def test_get_client_info_missing_headers():
    """Testa extração de info com headers faltando"""
    request = MockRequest(headers={})

    info = get_client_info(request)

    assert info['user_agent'] == 'unknown'
    assert info['accept_language'] == 'unknown'
    assert info['referer'] == 'unknown'
