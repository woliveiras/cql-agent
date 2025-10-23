"""
Guardrails de conteúdo para validar a intenção do prompt
Verifica se a mensagem está relacionada ao domínio do agente (reparos residenciais)
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Pattern

logger = logging.getLogger(__name__)


class ContentGuardrailError(Exception):
    """Exceção levantada quando o conteúdo viola os guardrails"""
    pass


class ContentGuardrail:
    """
    Guardrail de conteúdo que valida se a mensagem é apropriada
    para o domínio de reparos residenciais
    """
    
    # Palavras-chave relacionadas a reparos residenciais
    REPAIR_KEYWORDS = [
        # Estruturas
        "torneira", "pia", "cano", "encanamento", "vazamento", "tubulação",
        "chuveiro", "registro", "válvula", "sifão", "ralo", "esgoto",
        "porta", "janela", "fechadura", "dobradiça", "maçaneta", "trinco",
        "parede", "reboco", "massa", "pintura", "tinta", "rachadura", "fissura",
        "teto", "telhado", "telha", "calha", "goteira", "infiltração",
        "piso", "azulejo", "cerâmica", "rejunte", "ladrilho",
        
        # Elétrica
        "tomada", "interruptor", "luz", "lâmpada", "fiação", "disjuntor",
        "fusível", "eletricidade", "elétrico", "curto", "voltagem",
        
        # Móveis e objetos
        "gaveta", "armário", "prateleira", "móvel", "estante",
        
        # Ações
        "consertar", "reparar", "arrumar", "corrigir", "instalar", "trocar",
        "substituir", "fixar", "ajustar", "vedar", "calafetar", "desentupir",
        "limpar", "manutenção", "resolver", "problema", "quebrado", "defeito",
        
        # Geral
        "casa", "residencial", "doméstico", "lar", "apartamento",
        "reparo", "manutenção", "diy", "faça você mesmo"
    ]
    
    # Padrões de perguntas legítimas (serão compilados no __init__)
    QUESTION_PATTERNS_RAW = [
        r"\bcomo\s+(consertar|reparar|arrumar|resolver|instalar|trocar|fixar)",
        r"\bpor\s+que\s+(está|ta|ficou).+(quebrado|vazando|pingando|travando)",
        r"\bo\s+que\s+fazer\s+(quando|se|com)",
        r"\bpreciso\s+(consertar|reparar|arrumar|ajuda|resolver)",
        r"\btenho\s+(um\s+)?problema\s+(com|na|no)",
        r"\bestá\s+(quebrado|vazando|pingando|travando|entupido)",
        r"\b(dicas|tutorial|passo\s+a\s+passo|instruções)\s+(para|de)"
    ]
    
    # Tópicos proibidos (off-topic claro) (serão compilados no __init__)
    PROHIBITED_TOPICS_RAW = [
        # Conteúdo ilegal
        r"\b(bomb|weapon|gun|explosive|drug|hack|crack|pirat|steal|illegal)\b",
        
        # Conteúdo adulto/ofensivo
        r"\b(porn|xxx|sex|nude|naked|adult\s+content)\b",
        
        # Tentativas de jailbreak básicas
        r"ignore\s+(previous|all|above)\s+(instructions?|prompts?|commands?|rules?)",
        r"you\s+are\s+now\s+(a|an|acting|pretending)",
        r"forget\s+(everything|all|your|the)\s*(you|instructions?|rules?)?",
        r"new\s+(role|character|personality|identity|system)",
        r"disregard\s+(previous|all|above|the)\s*(instructions?|rules?)?",
        
        # Prompt injection avançada - comandos de sistema
        r"<\|.*?\|>",  # Tokens especiais do sistema
        r"\[SYSTEM\]|\[INST\]|\[/INST\]",  # Tags de instrução
        r"###\s*(System|Instruction|User|Assistant)",  # Markdown de sistema
        r"<start_of_turn>|<end_of_turn>",  # Delimitadores de turno
        
        # Tentativas de role manipulation
        r"(act|behave|pretend|play|roleplay)\s+(as|like)\s+(a|an)",
        r"from\s+now\s+on",
        r"switch\s+to\s+(mode|role|character)",
        r"override\s+(your|the)\s+(instructions?|rules?|programming)",
        
        # Tentativas de extrair informações do sistema
        r"(show|display|print|reveal|tell)\s+(me\s+)?(your|the)\s+(prompt|instructions?|system|rules?)",
        r"what\s+(are|is)\s+your\s+(instructions?|prompt|rules?|system\s+message)",
        r"repeat\s+(your|the)\s+(prompt|instructions?|system)",
        
        # Encoding attacks (base64, hex, etc)
        r"base64|decode|encode|hex|ascii|unicode|\\x[0-9a-f]{2}",
        r"eval\(|exec\(|system\(|shell\(",  # Code execution
        
        # Tentativas de bypass com separadores
        r"---+\s*(ignore|new|system|instruction)",
        r"\*\*\*+\s*(ignore|new|system|instruction)",
        r"===+\s*(ignore|new|system|instruction)",
        
        # Payload injection
        r";\s*(drop|delete|insert|update|select)\s+",  # SQL injection patterns
        r"\$\{|\{\{.*?\}\}",  # Template injection
        
        # Multi-language jailbreaking
        r"traduza|traduzir|translate|翻译",  # Bypass via translation
        
        # Tópicos completamente fora do escopo
        r"\b(crypto|bitcoin|invest|stock|trade|forex)\b",
        r"\b(recipe|cooking|food|meal)\b",
        r"\b(medical|doctor|disease|medication|surgery)\b",
        r"\b(legal|lawyer|lawsuit|court)\b"
    ]
    
    def __init__(
        self,
        strict_mode: bool = False
    ):
        """
        Inicializa o guardrail
        
        Args:
            strict_mode: Se True, aplica validação mais rigorosa
        """
        self.strict_mode = strict_mode
        
        # Pré-compila todos os patterns regex para melhor performance
        self.question_patterns: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.QUESTION_PATTERNS_RAW
        ]
        
        self.prohibited_patterns: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.PROHIBITED_TOPICS_RAW
        ]
        
        logger.info(
            f"ContentGuardrail initialized: strict_mode={strict_mode}, "
            f"question_patterns={len(self.question_patterns)}, "
            f"prohibited_patterns={len(self.prohibited_patterns)}"
        )
    
    def _detect_prompt_injection(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta tentativas sofisticadas de prompt injection
        
        Analisa:
        - Delimitadores suspeitos (---, ***, ===, ||)
        - Caracteres especiais em excesso (>, <, {, }, [, ])
        - Padrões de encoding (base64-like, hex)
        - Tokens especiais do sistema
        - Comandos imperativos suspeitos
        
        Returns:
            (is_safe, reason)
        """
        # 1. Verifica excesso de delimitadores suspeitos
        delimiter_count = sum([
            message.count('---'),
            message.count('***'),
            message.count('==='),
            message.count('|||'),
            message.count('###')
        ])
        if delimiter_count >= 2:
            logger.warning(f"Excesso de delimitadores detectado: {delimiter_count}")
            return False, "Padrão suspeito de delimitadores detectado"
        
        # 2. Verifica excesso de caracteres especiais (possível payload)
        special_chars = '<>{}[]$|\\`'
        special_count = sum(1 for char in message if char in special_chars)
        if special_count > len(message) * 0.1:  # Mais de 10% são caracteres especiais
            logger.warning(f"Excesso de caracteres especiais: {special_count}/{len(message)}")
            return False, "Excesso de caracteres especiais detectado"
        
        # 3. Detecta sequências que parecem base64 longas
        # Base64 tem padrão: letras, números, +, /, = no final
        base64_pattern = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
        if base64_pattern.search(message):
            logger.warning("Possível payload base64 detectado")
            return False, "Sequência codificada suspeita detectada"
        
        # 4. Detecta múltiplas quebras de linha (tentativa de injeção multi-linha)
        if message.count('\n') > 5:
            logger.warning(f"Excesso de quebras de linha: {message.count(chr(10))}")
            return False, "Formato de mensagem suspeito"
        
        # 5. Detecta comandos imperativos em sequência
        imperative_words = ['ignore', 'forget', 'disregard', 'override', 'bypass', 
                           'skip', 'disable', 'remove', 'delete', 'change', 'modify']
        imperative_count = sum(1 for word in imperative_words if word in message.lower())
        if imperative_count >= 3:
            logger.warning(f"Múltiplos comandos imperativos: {imperative_count}")
            return False, "Múltiplos comandos de manipulação detectados"
        
        # 6. Detecta tentativas de fechar/abrir contextos
        context_markers = ['</system>', '<system>', '[/INST]', '[INST]', 
                          '<|endoftext|>', '<|im_end|>', '<|im_start|>']
        if any(marker in message for marker in context_markers):
            logger.warning("Marcadores de contexto do sistema detectados")
            return False, "Tentativa de manipulação de contexto detectada"
        
        return True, None
    
    def _check_prohibited_content(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se a mensagem contém conteúdo proibido usando patterns pré-compilados
        
        Returns:
            (is_valid, reason)
        """
        for pattern in self.prohibited_patterns:
            if pattern.search(message):
                logger.warning(f"Conteúdo proibido detectado: {pattern.pattern}")
                return False, "Conteúdo inapropriado ou fora do escopo"
        
        return True, None
    
    def _check_repair_relevance(self, message: str) -> float:
        """
        Calcula score de relevância para reparos residenciais usando patterns pré-compilados
        
        Returns:
            Score de 0.0 a 1.0
        """
        message_lower = message.lower()
        
        # Conta keywords encontradas
        keyword_count = sum(1 for keyword in self.REPAIR_KEYWORDS if keyword in message_lower)
        
        # Verifica padrões de pergunta usando patterns compilados
        pattern_matches = sum(1 for pattern in self.question_patterns if pattern.search(message))
        
        # Calcula score
        keyword_score = min(keyword_count / 3, 1.0)  # Normaliza em 3 keywords
        pattern_score = min(pattern_matches / 2, 1.0)  # Normaliza em 2 padrões
        
        # Média ponderada
        final_score = (keyword_score * 0.7) + (pattern_score * 0.3)
        
        logger.debug(f"Relevance score: {final_score:.2f} (keywords: {keyword_count}, patterns: {pattern_matches})")
        
        return final_score
    
    def validate(self, message: str) -> Dict[str, any]:
        """
        Valida se a mensagem é apropriada para o agente
        
        Args:
            message: Mensagem a ser validada
            
        Returns:
            Dict com:
                - is_valid: bool
                - reason: str (se inválido)
                - score: float (score de relevância)
                
        Raises:
            ContentGuardrailError: Se a validação falhar em modo strict
        """
        # 1. Detecta prompt injection avançada
        is_safe, reason = self._detect_prompt_injection(message)
        if not is_safe:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}
        
        # 2. Verifica conteúdo proibido via patterns
        is_valid, reason = self._check_prohibited_content(message)
        if not is_valid:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}
        
        # 3. Calcula relevância
        relevance_score = self._check_repair_relevance(message)
        
        # 4. Decisão final
        # Em modo strict, exige score mínimo de 0.2
        # Em modo normal, exige score mínimo de 0.1
        min_score = 0.2 if self.strict_mode else 0.1
        
        if relevance_score < min_score:
            reason = "Mensagem não parece estar relacionada a reparos residenciais"
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": relevance_score}
        
        return {"is_valid": True, "reason": None, "score": relevance_score}
