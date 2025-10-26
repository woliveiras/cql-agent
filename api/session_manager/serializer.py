"""
Serialização customizada para RepairAgent

Este módulo fornece funções para serializar e deserializar objetos RepairAgent,
extraindo apenas o estado essencial e reconstruindo o agente completo.
"""

import json
from typing import Dict, Any
from agents import RepairAgent


def serialize_agent(agent: RepairAgent) -> bytes:
    """
    Serializa um RepairAgent para bytes

    Extrai apenas o estado essencial do agente (histórico, tentativas, estado)
    e serializa como JSON, ignorando objetos não-serializáveis como LLM clients.

    Args:
        agent: Instância do RepairAgent

    Returns:
        bytes: Estado do agente serializado
    """
    # Extrair apenas o estado essencial
    state = {
        "conversation_history": _serialize_messages(agent.conversation_history),
        "current_attempt": agent.current_attempt,
        "state": agent.state.value,
        "max_attempts": agent.max_attempts,
        "use_rag": agent.use_rag,
        "use_web_search": agent.use_web_search,
    }

    # Serializar como JSON
    json_str = json.dumps(state, ensure_ascii=False)
    return json_str.encode('utf-8')


def deserialize_agent(data: bytes) -> RepairAgent:
    """
    Deserializa bytes para um RepairAgent

    Reconstrói o agente com uma nova instância dos clientes LLM, RAG e Web Search,
    e restaura o estado essencial (histórico, tentativas, estado).

    Args:
        data: Estado do agente serializado

    Returns:
        RepairAgent: Instância reconstruída do agente
    """
    from agents.repair_agent.agent import ConversationState

    # Deserializar JSON
    json_str = data.decode('utf-8')
    state = json.loads(json_str)

    # Criar nova instância do agente com as mesmas configurações
    agent = RepairAgent(
        max_attempts=state["max_attempts"],
        use_rag=state["use_rag"],
        use_web_search=state["use_web_search"]
    )

    # Restaurar estado
    agent.conversation_history = _deserialize_messages(state["conversation_history"])
    agent.current_attempt = state["current_attempt"]
    agent.state = ConversationState(state["state"])

    return agent


def _serialize_messages(messages: list) -> list:
    """
    Serializa mensagens do LangChain para dicionários

    Args:
        messages: Lista de mensagens LangChain ou dicts

    Returns:
        list: Lista de dicionários serializáveis
    """
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    serialized = []
    for msg in messages:
        # Se já é um dict, usar diretamente
        if isinstance(msg, dict):
            serialized.append(msg)
        # Se é um objeto Message, extrair campos
        else:
            msg_dict = {
                "content": msg.content,
                "type": msg.__class__.__name__
            }
            serialized.append(msg_dict)
    return serialized


def _deserialize_messages(messages_data: list) -> list:
    """
    Deserializa dicionários de volta para mensagens LangChain

    Args:
        messages_data: Lista de dicionários

    Returns:
        list: Lista de mensagens LangChain
    """
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    type_map = {
        "HumanMessage": HumanMessage,
        "AIMessage": AIMessage,
        "SystemMessage": SystemMessage
    }

    messages = []
    for msg_data in messages_data:
        # Se o dict não tem 'type', presumir que já está no formato correto
        if "type" not in msg_data:
            # Tentar manter como dict se possível
            messages.append(msg_data)
            continue

        msg_class = type_map.get(msg_data["type"])
        if msg_class:
            messages.append(msg_class(content=msg_data["content"]))
    return messages
