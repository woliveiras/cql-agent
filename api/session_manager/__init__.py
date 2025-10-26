"""
Gerenciamento de sessões com suporte a Redis e fallback em memória

Este módulo fornece uma camada de abstração para armazenamento de sessões,
suportando tanto Redis (produção) quanto memória (desenvolvimento).
"""

from api.session_manager.base import SessionStore
from api.session_manager.memory_store import MemorySessionStore
from api.session_manager.redis_store import RedisSessionStore
from api.session_manager.manager import SessionManager

__all__ = [
    "SessionStore",
    "MemorySessionStore",
    "RedisSessionStore",
    "SessionManager",
]
