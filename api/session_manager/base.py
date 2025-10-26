"""
Interface abstrata para armazenamento de sessões
"""

from typing import Optional, List
from abc import ABC, abstractmethod

from agents import RepairAgent


class SessionStore(ABC):
    """Interface abstrata para armazenamento de sessões"""

    @abstractmethod
    def get(self, session_id: str) -> Optional[RepairAgent]:
        """
        Recupera uma sessão pelo ID

        Args:
            session_id: ID da sessão

        Returns:
            RepairAgent ou None se não encontrado
        """
        pass

    @abstractmethod
    def set(self, session_id: str, agent: RepairAgent, ttl: Optional[int] = None) -> None:
        """
        Armazena uma sessão com TTL opcional

        Args:
            session_id: ID da sessão
            agent: Instância do RepairAgent
            ttl: Time-to-live em segundos (opcional)
        """
        pass

    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """
        Remove uma sessão

        Args:
            session_id: ID da sessão

        Returns:
            True se removido, False se não existia
        """
        pass

    @abstractmethod
    def exists(self, session_id: str) -> bool:
        """
        Verifica se uma sessão existe

        Args:
            session_id: ID da sessão

        Returns:
            True se existe, False caso contrário
        """
        pass

    @abstractmethod
    def list_sessions(self) -> List[str]:
        """
        Lista todos os IDs de sessões ativas

        Returns:
            Lista de session IDs
        """
        pass

    @abstractmethod
    def get_ttl(self, session_id: str) -> Optional[int]:
        """
        Retorna o TTL restante de uma sessão

        Args:
            session_id: ID da sessão

        Returns:
            Segundos restantes, 0 se expirado, None se sem TTL
        """
        pass
