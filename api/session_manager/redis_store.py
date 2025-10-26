"""
Armazenamento de sessões em Redis
"""

from typing import Optional, List

from agents import RepairAgent
from api.logging_config import get_logger
from api.session_manager.base import SessionStore
from api.session_manager.serializer import serialize_agent, deserialize_agent

logger = get_logger(__name__, component="session")


class RedisSessionStore(SessionStore):
    """
    Armazenamento de sessões em Redis

    Usado para produção. Suporta:
    - Persistência entre restarts
    - TTL automático
    - Escalabilidade horizontal
    - Clustering

    A serialização é feita via JSON, extraindo apenas o estado essencial do agente
    (histórico de conversação, tentativas, estado atual) e reconstruindo o agente
    completo na deserialização. Isso evita problemas com pickle de objetos não-serializáveis
    como thread locks e clientes HTTP.

    Attributes:
        client: Cliente Redis
        key_prefix: Prefixo para todas as chaves Redis
        default_ttl: TTL padrão em segundos
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "cql:session:",
        default_ttl: int = 3600
    ):
        """
        Inicializa conexão com Redis

        Args:
            redis_url: URL completa do Redis (ex: redis://localhost:6379/0)
            host: Host do Redis
            port: Porta do Redis
            db: Número do database Redis
            password: Senha do Redis (opcional)
            key_prefix: Prefixo para todas as chaves
            default_ttl: TTL padrão em segundos (padrão: 1 hora)

        Raises:
            ImportError: Se redis não estiver instalado
            ConnectionError: Se não conseguir conectar ao Redis
        """
        try:
            import redis
            from redis.exceptions import ConnectionError, TimeoutError
        except ImportError:
            raise ImportError(
                "Redis não está instalado. Instale com: uv sync"
            )

        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

        # Conectar ao Redis
        if redis_url:
            self.client = redis.from_url(
                redis_url,
                decode_responses=False,  # Manteremos bytes para serialização
                socket_connect_timeout=5,
                socket_timeout=5
            )
        else:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )

        # Testar conexão
        try:
            self.client.ping()
            logger.info(
                "RedisSessionStore inicializado com sucesso",
                extra={
                    "redis_url": redis_url or f"{host}:{port}/{db}",
                    "default_ttl": default_ttl
                }
            )
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            raise

    def _make_key(self, session_id: str) -> str:
        """
        Cria a chave Redis com prefixo

        Args:
            session_id: ID da sessão

        Returns:
            Chave completa com prefixo
        """
        return f"{self.key_prefix}{session_id}"

    def get(self, session_id: str) -> Optional[RepairAgent]:
        """
        Recupera sessão do Redis

        Args:
            session_id: ID da sessão

        Returns:
            RepairAgent ou None se não encontrado
        """
        try:
            key = self._make_key(session_id)
            data = self.client.get(key)

            if data is None:
                return None

            # Deserializar o agente
            agent = deserialize_agent(data)

            logger.debug(
                "Sessão recuperada do Redis",
                extra={"session_id": session_id}
            )

            return agent

        except Exception as e:
            logger.error(
                "Erro ao recuperar sessão do Redis",
                extra={
                    "session_id": session_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            return None

    def set(
        self,
        session_id: str,
        agent: RepairAgent,
        ttl: Optional[int] = None
    ) -> None:
        """
        Armazena sessão no Redis com TTL

        Args:
            session_id: ID da sessão
            agent: Instância do RepairAgent
            ttl: Time-to-live em segundos (usa default_ttl se None)

        Raises:
            Exception: Se falhar ao armazenar
        """
        try:
            key = self._make_key(session_id)

            # Serializar o agente
            data = serialize_agent(agent)

            # Usar TTL fornecido ou padrão
            ttl_seconds = ttl or self.default_ttl

            # Armazenar com TTL
            self.client.setex(key, ttl_seconds, data)

            logger.debug(
                "Sessão armazenada no Redis",
                extra={
                    "session_id": session_id,
                    "ttl": ttl_seconds
                }
            )

        except Exception as e:
            logger.error(
                "Erro ao armazenar sessão no Redis",
                extra={
                    "session_id": session_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            raise

    def delete(self, session_id: str) -> bool:
        """
        Remove sessão do Redis

        Args:
            session_id: ID da sessão

        Returns:
            True se removido, False caso contrário
        """
        try:
            key = self._make_key(session_id)
            result = self.client.delete(key)

            logger.debug(
                "Sessão removida do Redis",
                extra={"session_id": session_id, "deleted": result > 0}
            )

            return result > 0

        except Exception as e:
            logger.error(
                "Erro ao remover sessão do Redis",
                extra={
                    "session_id": session_id,
                    "error": str(e)
                },
                exc_info=True
            )
            return False

    def exists(self, session_id: str) -> bool:
        """
        Verifica se sessão existe no Redis

        Args:
            session_id: ID da sessão

        Returns:
            True se existe, False caso contrário
        """
        try:
            key = self._make_key(session_id)
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Erro ao verificar existência: {e}")
            return False

    def list_sessions(self) -> List[str]:
        """
        Lista todos os IDs de sessões ativas

        Returns:
            Lista de session IDs (sem o prefixo)
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.client.keys(pattern)

            # Remover prefixo dos IDs
            prefix_len = len(self.key_prefix)
            session_ids = [
                key.decode('utf-8')[prefix_len:]
                for key in keys
            ]

            return session_ids

        except Exception as e:
            logger.error(f"Erro ao listar sessões: {e}")
            return []

    def get_ttl(self, session_id: str) -> Optional[int]:
        """
        Retorna TTL restante em segundos

        Args:
            session_id: ID da sessão

        Returns:
            Segundos restantes, 0 se expirado, None se sem TTL
        """
        try:
            key = self._make_key(session_id)
            ttl = self.client.ttl(key)

            # -2 = chave não existe
            # -1 = chave sem TTL
            # >= 0 = TTL em segundos

            if ttl == -2:
                return 0
            elif ttl == -1:
                return None
            else:
                return ttl

        except Exception as e:
            logger.error(f"Erro ao obter TTL: {e}")
            return None
