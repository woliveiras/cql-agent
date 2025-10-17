"""
Módulo de Prompts - Centraliza todos os prompts do agente
"""

from .base import BASE_SYSTEM_PROMPT
from .states import (
    NEW_PROBLEM_PROMPT,
    get_waiting_feedback_prompt,
    get_max_attempts_prompt
)
from .messages import (
    SUCCESS_MESSAGE,
    get_max_attempts_message,
    AMBIGUOUS_FEEDBACK_MESSAGE
)

__all__ = [
    'BASE_SYSTEM_PROMPT',
    'NEW_PROBLEM_PROMPT',
    'get_waiting_feedback_prompt',
    'get_max_attempts_prompt',
    'SUCCESS_MESSAGE',
    'get_max_attempts_message',
    'AMBIGUOUS_FEEDBACK_MESSAGE'
]
