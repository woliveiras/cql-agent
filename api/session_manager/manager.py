"""
Gerenciador de sessões com fallback automático
"""

import os
from typing import Dict, Any, List

from agents import RepairAgent
from api.logging_config import get_logger
from api.session_manager.base import SessionStore
from api.session_manager.memory_store import MemorySessionStore
from api.session_manager.redis_store import RedisSessionStore

logger = get_logger(__name__, component="session")


class SessionManager:
    """
    Gerenciador de sessões com fallback automático

    Tenta usar Redis primeiro, faz fallback para memória se Redis falhar.

    Attributes:
        store: SessionStore sendo usado (Redis ou Memory)

    Examples:
        >>> manager = SessionManager(use_redis=True)
        >>> agent = manager.get_or_create_agent("session-123")
        >>> # ... usar agent ...
        >>> manager.update_agent("session-123", agent)
    """

    def __init__(self, use_redis: bool = True):
        """
        Inicializa o gerenciador de sessões

        Args:
            use_redis: Se True, tenta usar Redis (pode fazer fallback para memória)
        """
        self.store: SessionStore

        if use_redis:
            try:
                # Tentar usar Redis
                redis_url = os.getenv("REDIS_URL")

                if redis_url:
                    self.store = RedisSessionStore(redis_url=redis_url)
                else:
                    # Configuração manual
                    self.store = RedisSessionStore(
                        host=os.getenv("REDIS_HOST", "localhost"),
                        port=int(os.getenv("REDIS_PORT", "6379")),
                        db=int(os.getenv("REDIS_DB", "0")),
                        password=os.getenv("REDIS_PASSWORD"),
                        key_prefix=os.getenv("REDIS_KEY_PREFIX", "cql:session:"),
                        default_ttl=int(os.getenv("SESSION_TTL", "3600"))
                    )

                logger.info("SessionManager usando RedisSessionStore")

            except Exception as e:
                logger.warning(
                    f"Falha ao conectar ao Redis, usando MemorySessionStore: {e}"
                )
                self.store = MemorySessionStore()
        else:
            self.store = MemorySessionStore()
            logger.info("SessionManager usando MemorySessionStore")

    def get_or_create_agent(
        self,
        session_id: str,
        use_rag: bool = True,
        use_web_search: bool = True
    ) -> RepairAgent:
        """
        Obtém ou cria um agente para a sessão

        Args:
            session_id: ID da sessão
            use_rag: Habilitar RAG
            use_web_search: Habilitar busca web

        Returns:
            RepairAgent da sessão (novo ou existente)
        """
        # Tentar recuperar sessão existente
        agent = self.store.get(session_id)

        if agent is None:
            # Criar novo agente
            logger.info(
                "Criando novo agente",
                extra={
                    "session_id": session_id,
                    "use_rag": use_rag,
                    "use_web_search": use_web_search,
                    "event_type": "agent_created"
                }
            )

            agent = RepairAgent(
                use_rag=use_rag,
                use_web_search=use_web_search
            )

            # Armazenar no store
            self.store.set(session_id, agent)

        return agent

    def update_agent(self, session_id: str, agent: RepairAgent) -> None:
        """
        Atualiza o estado de um agente

        IMPORTANTE: Deve ser chamado após cada interação para persistir mudanças

        Args:
            session_id: ID da sessão
            agent: Agente atualizado
        """
        self.store.set(session_id, agent)

    def delete_session(self, session_id: str) -> bool:
        """
        Remove uma sessão

        Args:
            session_id: ID da sessão

        Returns:
            True se removido, False se não existia
        """
        return self.store.delete(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Lista todas as sessões ativas com informações

        Returns:
            Lista de dicionários com info das sessões
            Cada dict contém: session_id, state, current_attempt, ttl
        """
        session_ids = self.store.list_sessions()
        sessions = []

        for sid in session_ids:
            agent = self.store.get(sid)
            if agent:
                ttl = self.store.get_ttl(sid)
                sessions.append({
                    "session_id": sid,
                    "state": agent.state.value,
                    "current_attempt": agent.current_attempt,
                    "ttl": ttl
                })

        return sessions
