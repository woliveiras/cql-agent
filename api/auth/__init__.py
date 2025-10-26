"""
Módulo de autenticação e rate limiting para a API.
Suporta autenticação híbrida: fingerprinting + tokens JWT.
Inclui middleware para integração com FastAPI.
"""

from .fingerprint import generate_fingerprint
from .jwt_handler import JWTHandler, AnonymousToken
from .rate_limiter import RateLimiter, RateLimitExceeded
from .middleware import AuthMiddleware, get_current_user

__all__ = [
    'generate_fingerprint',
    'JWTHandler',
    'AnonymousToken',
    'RateLimiter',
    'RateLimitExceeded',
    'AuthMiddleware',
    'get_current_user',
]
