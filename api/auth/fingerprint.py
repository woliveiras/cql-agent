"""
Sistema de fingerprinting para identificação de clientes sem login
Gera uma impressão digital única baseada em características do request
"""

import hashlib
from typing import Optional
from fastapi import Request


def generate_fingerprint(request: Request) -> str:
    """
    Gera uma impressão digital única do cliente baseada em:
    - Endereço IP (com suporte a proxy/load balancer)
    - User-Agent
    - Accept-Language

    Args:
        request: Request do FastAPI

    Returns:
        Hash SHA256 da impressão digital (64 caracteres)

    Example:
        >>> fingerprint = generate_fingerprint(request)
        >>> print(fingerprint)
        'a1b2c3d4e5f6...'
    """
    # Obter IP real (considerando proxies)
    ip = _get_real_ip(request)

    # Obter User-Agent
    user_agent = request.headers.get('user-agent', 'unknown')

    # Obter idioma preferido (adiciona mais entropia)
    accept_language = request.headers.get('accept-language', 'unknown')

    # Combinar dados
    fingerprint_data = f"{ip}:{user_agent}:{accept_language}"

    # Gerar hash SHA256
    fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()

    return fingerprint_hash


def _get_real_ip(request: Request) -> str:
    """
    Obtém o IP real do cliente, considerando proxies e load balancers

    Ordem de prioridade:
    1. X-Forwarded-For (primeiro IP da lista)
    2. X-Real-IP
    3. request.client.host (IP direto)

    Args:
        request: Request do FastAPI

    Returns:
        Endereço IP do cliente
    """
    # Verificar X-Forwarded-For (comum em load balancers)
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        # Pegar o primeiro IP (cliente original)
        ip = x_forwarded_for.split(',')[0].strip()
        return ip

    # Verificar X-Real-IP (comum em nginx)
    x_real_ip = request.headers.get('x-real-ip')
    if x_real_ip:
        return x_real_ip.strip()

    # Fallback: IP direto da conexão
    if request.client and request.client.host:
        return request.client.host

    return 'unknown'


def get_client_info(request: Request) -> dict:
    """
    Extrai informações detalhadas do cliente para logging/debugging

    Args:
        request: Request do FastAPI

    Returns:
        Dicionário com informações do cliente

    Example:
        >>> info = get_client_info(request)
        >>> print(info['ip'])
        '192.168.1.1'
    """
    return {
        'ip': _get_real_ip(request),
        'user_agent': request.headers.get('user-agent', 'unknown'),
        'accept_language': request.headers.get('accept-language', 'unknown'),
        'referer': request.headers.get('referer', 'unknown'),
        'fingerprint': generate_fingerprint(request),
    }
