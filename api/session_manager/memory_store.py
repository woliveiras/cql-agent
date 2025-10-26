"""
Armazenamento de sessões em memória
"""

from typing import Optional, Dict, List

from agents import RepairAgent
from api.logging_config import get_logger
from api.session_manager.base import SessionStore

logger = get_logger(__name__, component="session")


class MemorySessionStore(SessionStore):
    """
    Armazenamento de sessões em memória

    Usado para desenvolvimento e como fallback.
    Não persiste entre restarts.

    Attributes:
        _store: Dicionário interno para armazenar sessões
    """

    def __init__(self):
        """Inicializa o store em memória"""
        self._store: Dict[str, RepairAgent] = {}
        logger.info("MemorySessionStore inicializado")

    def get(self, session_id: str) -> Optional[RepairAgent]:
        """Recupera sessão da memória"""
        return self._store.get(session_id)

    def set(self, session_id: str, agent: RepairAgent, ttl: Optional[int] = None) -> None:
        """Armazena sessão em memória (TTL ignorado)"""
        self._store[session_id] = agent
        logger.debug(
            "Sessão armazenada em memória",
            extra={"session_id": session_id}
        )

    def delete(self, session_id: str) -> bool:
        """Remove sessão da memória"""
        if session_id in self._store:
            del self._store[session_id]
            logger.debug(
                "Sessão removida da memória",
                extra={"session_id": session_id}
            )
            return True
        return False

    def exists(self, session_id: str) -> bool:
        """Verifica existência em memória"""
        return session_id in self._store

    def list_sessions(self) -> List[str]:
        """Lista todas as sessões em memória"""
        return list(self._store.keys())

    def get_ttl(self, session_id: str) -> Optional[int]:
        """
        Memória não suporta TTL

        Returns:
            None se existe (sem TTL), 0 se não existe
        """
        return None if self.exists(session_id) else 0
