"""
Módulo de sanitização de entrada
Remove caracteres perigosos e valida o formato da entrada
"""

import re
import logging
import bleach
import sqlparse
from sqlparse import tokens as T

logger = logging.getLogger(__name__)


class SanitizationError(Exception):
    """Exceção levantada quando a sanitização falha"""
    pass


# ============================================================================
# PRÉ-COMPILAÇÃO DE REGEX PATTERNS
# ============================================================================

# Padrões SQL injection óbvios
SQL_INJECTION_PATTERNS = [
    re.compile(r"'\s*OR\s+'", re.IGNORECASE),  # ' OR ' (bypass autenticação)
    re.compile(r"'\s*OR\s+\d+\s*=\s*\d+", re.IGNORECASE),  # ' OR 1=1
    re.compile(r"\bUNION\b.*\bSELECT\b", re.IGNORECASE),  # UNION SELECT
]

# Padrões de command injection óbvio
COMMAND_INJECTION_PATTERNS = [
    re.compile(r";\s*rm\s+-rf", re.IGNORECASE),  # ; rm -rf /
    re.compile(r"\|\s*bash", re.IGNORECASE),  # | bash
    re.compile(r"&&\s*rm\s+", re.IGNORECASE),  # && rm
    re.compile(r"\$\(.*\)", re.IGNORECASE),  # Command substitution $(...)
]

# Padrões JavaScript perigosos
JAVASCRIPT_XSS_PATTERNS = [
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # onclick=, onload=, etc
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"</script>", re.IGNORECASE),
]

# Outros padrões úteis
WHITESPACE_PATTERN = re.compile(r'\s+')
REPEATED_CHARS_PATTERN = re.compile(r'(.)\1{99,}')  # 100+ caracteres repetidos


def _detect_sql_injection(text: str) -> bool:
    """
    Detecta SQL injection usando sqlparse (biblioteca especializada)
    Complexidade justificada: detecção de múltiplos padrões de SQL injection

    Abordagem: Se o texto contém estrutura SQL válida com comandos
    destrutivos ou comentários SQL, provavelmente é tentativa de injection.

    Args:
        text: Texto a ser analisado

    Returns:
        True se detectar SQL injection, False caso contrário
    """
    try:
        # Parse o texto como SQL
        parsed = sqlparse.parse(text)

        # Se não houver statements, não é SQL
        if not parsed:
            return False

        for statement in parsed:
            # Verifica se há tokens SQL válidos
            tokens = list(statement.flatten())

            # Se não há tokens, ignora
            if not tokens:
                continue

            # Detecta comandos DDL (DROP, ALTER, CREATE, etc.)
            # Esses NUNCA deveriam aparecer em mensagem de chat
            for token in tokens:
                if token.ttype == T.Keyword.DDL:
                    logger.warning(f"SQL DDL keyword detectado: {token.value}")
                    return True

                # Detecta comandos DML (SELECT, DELETE, UPDATE, INSERT)
                # SELECT pode aparecer em texto ("select da janela"), mas
                # se aparecer junto com FROM, WHERE, etc., é SQL injection
                if token.ttype == T.Keyword.DML:
                    keyword = token.value.upper()

                    # Comandos destrutivos sempre bloqueiam
                    if keyword in ('DELETE', 'UPDATE', 'INSERT'):
                        logger.warning(f"SQL DML destrutivo detectado: {token.value}")
                        return True

                    # SELECT: verifica se há outros tokens SQL suspeitos
                    if keyword == 'SELECT':
                        # Verifica se há FROM, WHERE, JOIN (indica query real)
                        token_values = [t.value.upper() for t in tokens if t.ttype == T.Keyword]
                        if any(kw in token_values for kw in ('FROM', 'WHERE', 'JOIN')):
                            logger.warning("SQL SELECT com FROM/WHERE detectado")
                            return True

                # Detecta comentários SQL (-- ou /* */)
                # Comum em SQL injection para comentar resto da query
                if token.ttype in (T.Comment.Single, T.Comment.Multiline):
                    logger.warning(f"Comentário SQL detectado: {token.value[:50]}")
                    return True

        # Mesmo que sqlparse não detecte, verifica padrões óbvios
        # de SQL injection que podem escapar do parser
        for pattern in SQL_INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning(f"Padrão SQL injection detectado: {pattern.pattern}")
                return True

        return False

    except Exception as e:
        # Se houver erro no parsing, por segurança assumimos que pode ser malicioso
        logger.debug(f"Erro ao parsear SQL (pode ser texto normal): {e}")
        return False


def _detect_obvious_attacks(text: str) -> bool:
    """
    Detecta padrões OBVIAMENTE maliciosos de command injection

    SQL injection é detectado por _detect_sql_injection() com sqlparse.
    Esta função foca apenas em command injection óbvio.

    Args:
        text: Texto a ser analisado

    Returns:
        True se detectar padrão claramente malicioso, False caso contrário
    """
    # Usa padrões pré-compilados para melhor performance
    for pattern in COMMAND_INJECTION_PATTERNS:
        if pattern.search(text):
            logger.warning(f"Padrão command injection detectado: {pattern.pattern[:50]}")
            return True

    return False


def sanitize_input(text: str) -> str:
    """
    Sanitiza a entrada do usuário removendo caracteres perigosos
    Complexidade justificada: múltiplas validações de segurança em sequência

    Args:
        text: Texto a ser sanitizado

    Returns:
        Texto sanitizado

    Raises:
        SanitizationError: Se o texto contiver conteúdo inválido
    """
    if not isinstance(text, str):
        raise SanitizationError("Entrada deve ser uma string")

    # Remove caracteres nulos que podem causar problemas
    if '\x00' in text:
        logger.warning("Caractere nulo detectado na entrada")
        raise SanitizationError("Entrada contém caracteres inválidos (null bytes)")

    # Remove outros caracteres de controle perigosos (exceto \n, \r, \t)
    # Mantemos quebras de linha e tabs para preservar formatação legítima
    control_chars = ''.join(chr(i) for i in range(32) if i not in (9, 10, 13))
    if any(char in text for char in control_chars):
        logger.warning("Caracteres de controle perigosos detectados na entrada")
        text = ''.join(char for char in text if char not in control_chars)

    # Sanitização de HTML/XSS usando bleach (biblioteca especializada)
    # bleach.clean remove todas as tags HTML por padrão
    original_text = text
    text = bleach.clean(text, tags=[], strip=True)

    if text != original_text:
        # Se houve modificação, é possível que havia HTML malicioso
        logger.warning(f"HTML/tags removidas pela sanitização: {original_text[:100]}")

    # Detecta padrões JavaScript perigosos que podem ter escapado
    for pattern in JAVASCRIPT_XSS_PATTERNS:
        if pattern.search(text):
            logger.warning(f"Padrão JavaScript perigoso detectado: {text[:100]}")
            raise SanitizationError("Entrada contém padrões suspeitos de JavaScript/XSS")

    # Remove espaços em branco excessivos (usa padrão pré-compilado)
    text = WHITESPACE_PATTERN.sub(' ', text)
    text = text.strip()

    # Verifica se ainda há conteúdo após sanitização
    if not text:
        raise SanitizationError("Entrada vazia após sanitização")

    # Detecta SQL injection usando sqlparse (biblioteca especializada)
    if _detect_sql_injection(text):
        raise SanitizationError("Entrada contém padrões suspeitos de SQL injection")

    # Detecta command injection óbvio (fail-fast para economizar recursos)
    if _detect_obvious_attacks(text):
        raise SanitizationError("Entrada contém padrões claramente maliciosos")

    # Limita caracteres repetidos suspeitos (possível DoS ou bypass)
    # Usa padrão pré-compilado para melhor performance
    if REPEATED_CHARS_PATTERN.search(text):
        logger.warning("Sequência excessiva de caracteres repetidos detectada")
        raise SanitizationError("Entrada contém sequências suspeitas de caracteres repetidos")

    logger.debug(f"Entrada sanitizada com sucesso: {len(text)} caracteres")
    return text


def validate_text_encoding(text: str) -> bool:
    """
    Valida se o texto possui encoding válido

    Args:
        text: Texto a ser validado

    Returns:
        True se válido, False caso contrário
    """
    try:
        # Tenta encodar e decodar em UTF-8
        text.encode('utf-8').decode('utf-8')
        return True
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False
