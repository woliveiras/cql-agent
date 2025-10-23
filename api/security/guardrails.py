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
        
        # Tentativas de jailbreak
        r"ignore\s+(previous|all)\s+(instructions|prompts)",
        r"you\s+are\s+now",
        r"forget\s+(everything|all|your)",
        r"new\s+(role|character|personality)",
        r"disregard\s+(previous|all)",
        
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
        # 1. Verifica conteúdo proibido
        is_valid, reason = self._check_prohibited_content(message)
        if not is_valid:
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": 0.0}
        
        # 2. Calcula relevância
        relevance_score = self._check_repair_relevance(message)
        
        # 3. Decisão final
        # Em modo strict, exige score mínimo de 0.2
        # Em modo normal, exige score mínimo de 0.1
        min_score = 0.2 if self.strict_mode else 0.1
        
        if relevance_score < min_score:
            reason = "Mensagem não parece estar relacionada a reparos residenciais"
            if self.strict_mode:
                raise ContentGuardrailError(reason)
            return {"is_valid": False, "reason": reason, "score": relevance_score}
        
        return {"is_valid": True, "reason": None, "score": relevance_score}
