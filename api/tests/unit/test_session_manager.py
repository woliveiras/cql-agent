"""
Testes para o módulo de gerenciamento de sessões
"""

import pytest
from api.session_manager import (
    MemorySessionStore,
    RedisSessionStore,
    SessionManager
)
from agents import RepairAgent


class TestMemorySessionStore:
    """Testes para armazenamento em memória"""

    def test_set_and_get(self):
        """Testa armazenamento e recuperação"""
        store = MemorySessionStore()
        agent = RepairAgent(use_rag=False, use_web_search=False)

        store.set("test-session", agent)
        retrieved = store.get("test-session")

        assert retrieved is not None
        assert retrieved.state == agent.state

    def test_get_nonexistent(self):
        """Testa recuperação de sessão inexistente"""
        store = MemorySessionStore()
        retrieved = store.get("nonexistent")

        assert retrieved is None

    def test_delete(self):
        """Testa remoção de sessão"""
        store = MemorySessionStore()
        agent = RepairAgent(use_rag=False, use_web_search=False)

        store.set("test-session", agent)
        assert store.exists("test-session")

        result = store.delete("test-session")
        assert result is True
        assert not store.exists("test-session")

    def test_delete_nonexistent(self):
        """Testa remoção de sessão inexistente"""
        store = MemorySessionStore()
        result = store.delete("nonexistent")
        assert result is False

    def test_exists(self):
        """Testa verificação de existência"""
        store = MemorySessionStore()
        agent = RepairAgent(use_rag=False, use_web_search=False)

        assert not store.exists("test-session")

        store.set("test-session", agent)
        assert store.exists("test-session")

    def test_list_sessions(self):
        """Testa listagem de sessões"""
        store = MemorySessionStore()

        # Vazio no início
        assert len(store.list_sessions()) == 0

        # Adicionar sessões
        store.set("session-1", RepairAgent(use_rag=False, use_web_search=False))
        store.set("session-2", RepairAgent(use_rag=False, use_web_search=False))

        sessions = store.list_sessions()
        assert len(sessions) == 2
        assert "session-1" in sessions
        assert "session-2" in sessions

    def test_get_ttl(self):
        """Testa obtenção de TTL (sempre None em memória)"""
        store = MemorySessionStore()
        agent = RepairAgent(use_rag=False, use_web_search=False)

        store.set("test-session", agent, ttl=60)
        ttl = store.get_ttl("test-session")

        # Memória não suporta TTL
        assert ttl is None

    def test_get_ttl_nonexistent(self):
        """Testa TTL de sessão inexistente"""
        store = MemorySessionStore()
        ttl = store.get_ttl("nonexistent")
        assert ttl == 0

    def test_agent_state_persistence(self):
        """Testa que o estado do agente é preservado"""
        store = MemorySessionStore()
        agent = RepairAgent(use_rag=False, use_web_search=False)

        # Modificar estado do agente
        agent.current_attempt = 2

        store.set("test-session", agent)
        retrieved = store.get("test-session")

        assert retrieved.current_attempt == 2


class TestSessionManager:
    """Testes para o gerenciador de sessões"""

    def test_init_with_memory(self):
        """Testa inicialização com MemoryStore"""
        manager = SessionManager(use_redis=False)
        assert isinstance(manager.store, MemorySessionStore)

    def test_get_or_create_agent_creates_new(self):
        """Testa criação de novo agente"""
        manager = SessionManager(use_redis=False)

        agent = manager.get_or_create_agent(
            "new-session",
            use_rag=False,
            use_web_search=False
        )

        assert agent is not None
        assert manager.store.exists("new-session")

    def test_get_or_create_agent_returns_existing(self):
        """Testa recuperação de agente existente"""
        manager = SessionManager(use_redis=False)

        # Criar primeiro agente
        agent1 = manager.get_or_create_agent(
            "existing-session",
            use_rag=False,
            use_web_search=False
        )
        agent1.current_attempt = 3

        # Atualizar
        manager.update_agent("existing-session", agent1)

        # Recuperar novamente
        agent2 = manager.get_or_create_agent(
            "existing-session",
            use_rag=False,
            use_web_search=False
        )

        assert agent2.current_attempt == 3

    def test_update_agent(self):
        """Testa atualização de agente"""
        manager = SessionManager(use_redis=False)

        agent = manager.get_or_create_agent(
            "test-session",
            use_rag=False,
            use_web_search=False
        )

        # Modificar e atualizar
        agent.current_attempt = 5
        manager.update_agent("test-session", agent)

        # Verificar persistência
        retrieved = manager.store.get("test-session")
        assert retrieved.current_attempt == 5

    def test_delete_session(self):
        """Testa remoção de sessão"""
        manager = SessionManager(use_redis=False)

        manager.get_or_create_agent(
            "test-session",
            use_rag=False,
            use_web_search=False
        )

        assert manager.store.exists("test-session")

        result = manager.delete_session("test-session")
        assert result is True
        assert not manager.store.exists("test-session")

    def test_list_sessions(self):
        """Testa listagem de sessões"""
        manager = SessionManager(use_redis=False)

        # Criar algumas sessões
        manager.get_or_create_agent("session-1", use_rag=False, use_web_search=False)
        manager.get_or_create_agent("session-2", use_rag=False, use_web_search=False)

        sessions = manager.list_sessions()

        assert len(sessions) == 2
        assert all('session_id' in s for s in sessions)
        assert all('state' in s for s in sessions)
        assert all('current_attempt' in s for s in sessions)
        assert all('ttl' in s for s in sessions)

    def test_list_sessions_empty(self):
        """Testa listagem de sessões quando vazio"""
        manager = SessionManager(use_redis=False)
        sessions = manager.list_sessions()
        assert len(sessions) == 0


@pytest.mark.integration
class TestRedisSessionStore:
    """
    Testes de integração para Redis

    Requer Redis rodando em localhost:6379
    Pula automaticamente se Redis não estiver disponível
    """

    @pytest.fixture
    def redis_store(self):
        """Fixture que cria um RedisStore para testes"""
        try:
            store = RedisSessionStore(
                host="localhost",
                port=6379,
                db=15,  # Usar DB separado para testes
                key_prefix="test:session:"
            )
            yield store

            # Cleanup: remover todas as sessões de teste
            for session_id in store.list_sessions():
                store.delete(session_id)

        except Exception as e:
            pytest.skip(f"Redis não disponível: {e}")

    def test_set_and_get(self, redis_store):
        """Testa armazenamento e recuperação no Redis"""
        agent = RepairAgent(use_rag=False, use_web_search=False)

        redis_store.set("test-session", agent, ttl=60)
        retrieved = redis_store.get("test-session")

        assert retrieved is not None
        assert retrieved.state.value == agent.state.value

    def test_ttl(self, redis_store):
        """Testa TTL no Redis"""
        agent = RepairAgent(use_rag=False, use_web_search=False)

        redis_store.set("test-session", agent, ttl=60)
        ttl = redis_store.get_ttl("test-session")

        assert ttl is not None
        assert ttl <= 60
        assert ttl > 0

    def test_delete(self, redis_store):
        """Testa remoção no Redis"""
        agent = RepairAgent(use_rag=False, use_web_search=False)

        redis_store.set("test-session", agent)
        assert redis_store.exists("test-session")

        result = redis_store.delete("test-session")
        assert result is True
        assert not redis_store.exists("test-session")

    def test_list_sessions(self, redis_store):
        """Testa listagem no Redis"""
        agent1 = RepairAgent(use_rag=False, use_web_search=False)
        agent2 = RepairAgent(use_rag=False, use_web_search=False)

        redis_store.set("session-1", agent1)
        redis_store.set("session-2", agent2)

        sessions = redis_store.list_sessions()
        assert len(sessions) >= 2  # >= porque pode ter outras sessões
        assert "session-1" in sessions
        assert "session-2" in sessions

    def test_agent_serialization(self, redis_store):
        """Testa serialização completa do agente"""
        agent = RepairAgent(use_rag=False, use_web_search=False)
        agent.current_attempt = 3
        agent.conversation_history.append({"role": "user", "content": "test"})

        redis_store.set("test-session", agent)
        retrieved = redis_store.get("test-session")

        assert retrieved.current_attempt == 3
        assert len(retrieved.conversation_history) == 1
