"""API para o Agente de Reparos Residenciais"""

from .app import app

__all__ = ['app']

# Configurações de segurança exportadas para referência
SECURITY_CONFIG = {
    'max_message_length': 4096,
    'min_message_length': 1,
    'session_id_pattern': r'^[a-zA-Z0-9_-]+$',
    'max_session_id_length': 128,
    'content_guardrail_enabled': True,
    'sanitization_enabled': True
}
