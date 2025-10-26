"""
Sistema de rate limiting com suporte a Redis e memória
Implementa múltiplas estratégias de limitação
"""

import os
import time
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import threading

from api.logging_config import get_logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Configurar logger
logger = get_logger(__name__, component="rate_limiter")


class RateLimitExceeded(Exception):
    """Exceção lançada quando o rate limit é excedido"""

    def __init__(self, message: str, retry_after: int):
        """
        Args:
            message: Mensagem de erro
            retry_after: Tempo em segundos até poder tentar novamente
        """
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


class RateLimiter:
    """
    Sistema de rate limiting com suporte a múltiplos backends (Redis ou memória)

    Estratégias de limitação:
    - Por IP/fingerprint
    - Por token de usuário
    - Global (toda a API)
    - Por endpoint

    Example:
        >>> limiter = RateLimiter(use_redis=True)
        >>> allowed, retry_after = limiter.check_rate_limit("user_123", limit=100, window=3600)
        >>> if not allowed:
        ...     raise RateLimitExceeded("Too many requests", retry_after)
    """

    def __init__(
        self,
        use_redis: bool = False,
        redis_url: Optional[str] = None,
        default_limit: int = 100,
        default_window: int = 3600
    ):
        """
        Inicializa o rate limiter

        Args:
            use_redis: Se True, usa Redis como backend (requer redis-py instalado)
            redis_url: URL de conexão do Redis (ex: redis://localhost:6379/0)
            default_limit: Limite padrão de requests por janela
            default_window: Janela de tempo padrão em segundos (3600 = 1 hora)
        """
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.default_limit = default_limit
        self.default_window = default_window

        # Backend de armazenamento
        if self.use_redis:
            redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Testar conexão
                self.redis_client.ping()
                self.backend = 'redis'
                logger.info("Rate limiter usando Redis como backend", extra={"redis_url": redis_url})
            except Exception as e:
                logger.warning(
                    "Falha ao conectar no Redis, usando memória como fallback",
                    extra={
                        "error": str(e),
                        "redis_url": redis_url,
                        "event_type": "redis_connection_failed"
                    }
                )
                self.use_redis = False
                self.backend = 'memory'
                self._init_memory_storage()
        else:
            self.backend = 'memory'
            self._init_memory_storage()

    def _init_memory_storage(self):
        """Inicializa armazenamento em memória"""
        self.memory_storage: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def check_rate_limit(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        namespace: str = "default"
    ) -> Tuple[bool, int]:
        """
        Verifica se o rate limit foi excedido

        Args:
            identifier: Identificador único (user_id, fingerprint, IP, etc)
            limit: Limite de requests (usa default_limit se None)
            window: Janela de tempo em segundos (usa default_window se None)
            namespace: Namespace para separar diferentes tipos de limite

        Returns:
            Tupla (permitido, retry_after)
            - permitido: True se dentro do limite, False se excedido
            - retry_after: Segundos até poder tentar novamente (0 se permitido)

        Example:
            >>> limiter = RateLimiter()
            >>> allowed, retry = limiter.check_rate_limit("user_123", limit=10, window=60)
            >>> if not allowed:
            ...     print(f"Tente novamente em {retry} segundos")
        """
        limit = limit or self.default_limit
        window = window or self.default_window

        if self.use_redis:
            return self._check_redis(identifier, limit, window, namespace)
        else:
            return self._check_memory(identifier, limit, window, namespace)

    def _check_redis(
        self,
        identifier: str,
        limit: int,
        window: int,
        namespace: str
    ) -> Tuple[bool, int]:
        """
        Verifica rate limit usando Redis (Sliding Window Log algorithm)

        Args:
            identifier: Identificador único
            limit: Limite de requests
            window: Janela de tempo em segundos
            namespace: Namespace

        Returns:
            Tupla (permitido, retry_after)
        """
        key = f"ratelimit:{namespace}:{identifier}"
        now = time.time()
        window_start = now - window

        try:
            # Pipeline para operações atômicas
            pipe = self.redis_client.pipeline()

            # 1. Remover requests antigos fora da janela
            pipe.zremrangebyscore(key, 0, window_start)

            # 2. Contar requests na janela atual
            pipe.zcard(key)

            # 3. Adicionar request atual
            pipe.zadd(key, {str(now): now})

            # 4. Definir expiração da chave
            pipe.expire(key, window)

            # Executar pipeline
            results = pipe.execute()
            current_count = results[1]

            # Verificar se excedeu o limite
            if current_count >= limit:
                # Calcular tempo até a próxima janela
                oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_request:
                    oldest_time = oldest_request[0][1]
                    retry_after = int(window - (now - oldest_time)) + 1
                else:
                    retry_after = window

                return False, retry_after

            return True, 0

        except Exception as e:
            logger.warning(
                "Erro no rate limiter Redis, permitindo request (fail-open)",
                extra={
                    "error": str(e),
                    "identifier": identifier,
                    "namespace": namespace,
                    "event_type": "rate_limiter_error"
                }
            )
            # Em caso de erro, permitir o request (fail-open)
            return True, 0

    def _check_memory(
        self,
        identifier: str,
        limit: int,
        window: int,
        namespace: str
    ) -> Tuple[bool, int]:
        """
        Verifica rate limit usando memória

        Args:
            identifier: Identificador único
            limit: Limite de requests
            window: Janela de tempo em segundos
            namespace: Namespace

        Returns:
            Tupla (permitido, retry_after)
        """
        key = f"{namespace}:{identifier}"
        now = time.time()
        window_start = now - window

        with self.lock:
            # Obter lista de timestamps
            timestamps = self.memory_storage[key]

            # Remover timestamps antigos
            timestamps = [ts for ts in timestamps if ts > window_start]
            self.memory_storage[key] = timestamps

            # Verificar se excedeu o limite
            if len(timestamps) >= limit:
                # Calcular tempo até a próxima janela
                oldest_time = min(timestamps)
                retry_after = int(window - (now - oldest_time)) + 1
                return False, retry_after

            # Adicionar timestamp atual
            timestamps.append(now)

            return True, 0

    def get_usage(
        self,
        identifier: str,
        window: Optional[int] = None,
        namespace: str = "default"
    ) -> Dict[str, int]:
        """
        Obtém informações de uso atual

        Args:
            identifier: Identificador único
            window: Janela de tempo em segundos
            namespace: Namespace

        Returns:
            Dicionário com informações de uso:
            - requests_made: Número de requests feitos na janela
            - requests_remaining: Número de requests restantes
            - window_size: Tamanho da janela em segundos

        Example:
            >>> limiter = RateLimiter()
            >>> usage = limiter.get_usage("user_123")
            >>> print(f"Usado: {usage['requests_made']}/{usage['requests_remaining']}")
        """
        window = window or self.default_window
        limit = self.default_limit
        key = f"{namespace}:{identifier}"
        now = time.time()
        window_start = now - window

        if self.use_redis:
            try:
                redis_key = f"ratelimit:{key}"
                # Remover antigos e contar
                self.redis_client.zremrangebyscore(redis_key, 0, window_start)
                requests_made = self.redis_client.zcard(redis_key)
            except Exception:
                requests_made = 0
        else:
            with self.lock:
                timestamps = self.memory_storage.get(key, [])
                timestamps = [ts for ts in timestamps if ts > window_start]
                requests_made = len(timestamps)

        return {
            'requests_made': requests_made,
            'requests_remaining': max(0, limit - requests_made),
            'window_size': window,
            'limit': limit
        }

    def reset(self, identifier: str, namespace: str = "default"):
        """
        Reseta o contador de rate limit para um identificador

        Args:
            identifier: Identificador único
            namespace: Namespace

        Example:
            >>> limiter = RateLimiter()
            >>> limiter.reset("user_123")
        """
        key = f"{namespace}:{identifier}"

        if self.use_redis:
            try:
                redis_key = f"ratelimit:{key}"
                self.redis_client.delete(redis_key)
            except Exception as e:
                logger.warning(
                    "Erro ao resetar rate limit no Redis",
                    extra={
                        "error": str(e),
                        "identifier": identifier,
                        "namespace": namespace,
                        "event_type": "rate_limiter_reset_error"
                    }
                )
        else:
            with self.lock:
                if key in self.memory_storage:
                    del self.memory_storage[key]
