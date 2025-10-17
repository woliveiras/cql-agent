"""
Mensagens de Resposta - Templates para respostas do agente
"""

SUCCESS_MESSAGE = """🎉 Que ótimo que deu certo! Fico feliz em ter ajudado!

Se precisar de ajuda com outro reparo, é só me chamar. Boa sorte e até a próxima! 👋"""


def get_max_attempts_message(max_attempts: int) -> str:
    """
    Retorna a mensagem quando o máximo de tentativas é atingido
    
    Args:
        max_attempts: Número máximo de tentativas
        
    Returns:
        Mensagem formatada
    """
    return f"""Entendo sua frustração. Já tentamos {max_attempts} abordagens diferentes e o problema persiste.

Neste ponto, recomendo que você procure um profissional qualificado. Alguns problemas podem ser mais complexos do que parecem e podem necessitar:
- Ferramentas especializadas
- Conhecimento técnico avançado
- Inspeção presencial para diagnóstico correto

Você fez um bom esforço tentando resolver sozinho! Se tiver outro problema no futuro, estarei aqui para ajudar. 🔧"""


AMBIGUOUS_FEEDBACK_MESSAGE = """⚠️ Não entendi sua resposta. 

O problema foi resolvido? Por favor, responda apenas com 'sim' ou 'não'."""
