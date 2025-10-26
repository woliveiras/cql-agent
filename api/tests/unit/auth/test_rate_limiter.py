"""
Testes para o sistema de rate limiting
"""

import pytest
import time
from api.auth.rate_limiter import RateLimiter, RateLimitExceeded


def test_rate_limiter_memory_backend():
    """Testa rate limiter com backend em memória"""
    limiter = RateLimiter(use_redis=False, default_limit=5, default_window=60)

    assert limiter.backend == 'memory'


def test_check_rate_limit_allows_requests():
    """Testa que requests dentro do limite são permitidas"""
    limiter = RateLimiter(use_redis=False, default_limit=10, default_window=60)

    for i in range(10):
        allowed, retry_after = limiter.check_rate_limit("user1")
        assert allowed is True
        assert retry_after == 0


def test_check_rate_limit_blocks_excess():
    """Testa que requests acima do limite são bloqueadas"""
    limiter = RateLimiter(use_redis=False, default_limit=5, default_window=60)

    # Fazer 5 requests (limite)
    for i in range(5):
        allowed, _ = limiter.check_rate_limit("user1")
        assert allowed is True

    # 6ª request deve ser bloqueada
    allowed, retry_after = limiter.check_rate_limit("user1")
    assert allowed is False
    assert retry_after > 0


def test_check_rate_limit_different_users():
    """Testa que usuários diferentes têm limites independentes"""
    limiter = RateLimiter(use_redis=False, default_limit=3, default_window=60)

    # User1 faz 3 requests
    for i in range(3):
        allowed, _ = limiter.check_rate_limit("user1")
        assert allowed is True

    # User1 bloqueado na 4ª
    allowed, _ = limiter.check_rate_limit("user1")
    assert allowed is False

    # User2 ainda pode fazer requests
    allowed, _ = limiter.check_rate_limit("user2")
    assert allowed is True


def test_check_rate_limit_custom_limit():
    """Testa rate limiting com limite customizado"""
    limiter = RateLimiter(use_redis=False, default_limit=10, default_window=60)

    # Usar limite customizado de 2
    for i in range(2):
        allowed, _ = limiter.check_rate_limit("user1", limit=2)
        assert allowed is True

    # 3ª request bloqueada
    allowed, _ = limiter.check_rate_limit("user1", limit=2)
    assert allowed is False


def test_check_rate_limit_different_namespaces():
    """Testa que namespaces diferentes têm limites independentes"""
    limiter = RateLimiter(use_redis=False, default_limit=2, default_window=60)

    # Namespace "api"
    for i in range(2):
        allowed, _ = limiter.check_rate_limit("user1", namespace="api")
        assert allowed is True

    allowed, _ = limiter.check_rate_limit("user1", namespace="api")
    assert allowed is False

    # Namespace "admin" ainda permite requests
    allowed, _ = limiter.check_rate_limit("user1", namespace="admin")
    assert allowed is True


def test_get_usage():
    """Testa obtenção de informações de uso"""
    limiter = RateLimiter(use_redis=False, default_limit=10, default_window=60)

    # Fazer 3 requests
    for i in range(3):
        limiter.check_rate_limit("user1")

    usage = limiter.get_usage("user1")

    assert usage['requests_made'] == 3
    assert usage['requests_remaining'] == 7
    assert usage['limit'] == 10
    assert usage['window_size'] == 60


def test_reset():
    """Testa reset de contador de rate limit"""
    limiter = RateLimiter(use_redis=False, default_limit=3, default_window=60)

    # Fazer 3 requests (atingir limite)
    for i in range(3):
        limiter.check_rate_limit("user1")

    # Verificar que está bloqueado
    allowed, _ = limiter.check_rate_limit("user1")
    assert allowed is False

    # Resetar
    limiter.reset("user1")

    # Agora deve permitir novamente
    allowed, _ = limiter.check_rate_limit("user1")
    assert allowed is True


def test_sliding_window():
    """Testa sliding window: requests antigas expiram"""
    limiter = RateLimiter(use_redis=False, default_limit=2, default_window=1)  # Janela de 1 segundo

    # Fazer 2 requests (atingir limite)
    limiter.check_rate_limit("user1")
    limiter.check_rate_limit("user1")

    # Verificar que está bloqueado
    allowed, _ = limiter.check_rate_limit("user1")
    assert allowed is False

    # Aguardar janela expirar
    time.sleep(1.1)

    # Agora deve permitir novamente
    allowed, _ = limiter.check_rate_limit("user1")
    assert allowed is True


def test_rate_limit_exceeded_exception():
    """Testa exceção RateLimitExceeded"""
    exception = RateLimitExceeded("Too many requests", retry_after=60)

    assert exception.message == "Too many requests"
    assert exception.retry_after == 60
    assert str(exception) == "Too many requests"


def test_rate_limiter_default_values():
    """Testa valores padrão do rate limiter"""
    limiter = RateLimiter(use_redis=False)

    assert limiter.default_limit == 100
    assert limiter.default_window == 3600
    assert limiter.backend == 'memory'
