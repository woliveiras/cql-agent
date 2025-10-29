"""
Prompts de Estado - Instruções específicas para cada estado da conversação
"""

NEW_PROBLEM_PROMPT = """

INSTRUÇÕES IMPORTANTES:
- NUNCA sugira chamar um profissional na primeira tentativa
- SEMPRE forneça uma solução prática e detalhada
- Ao final da solução, pergunte: "O problema foi resolvido?"
"""


def get_waiting_feedback_prompt(current_attempt: int, max_attempts: int) -> str:
    """
    Retorna o prompt para quando o agente está aguardando feedback

    Args:
        current_attempt: Tentativa atual
        max_attempts: Número máximo de tentativas

    Returns:
        Prompt formatado
    """
    return f"""\n\nO usuário tentou a solução anterior mas não funcionou (tentativa {current_attempt}/{max_attempts}).
Forneça uma NOVA abordagem diferente ou dicas adicionais.
Seja encorajador e termine perguntando:

"Essa solução funcionou? Responda com 'sim' ou 'não'." """


def get_max_attempts_prompt(max_attempts: int) -> str:
    """
    Retorna o prompt para quando o máximo de tentativas foi atingido

    Args:
        max_attempts: Número máximo de tentativas

    Returns:
        Prompt formatado
    """
    return f"""\n\nO usuário já tentou {max_attempts} vezes sem sucesso.
Agradeça o esforço e sugira educadamente buscar um profissional qualificado.
Explique que alguns problemas podem ser mais complexos e necessitam equipamento ou experiência especializada."""
