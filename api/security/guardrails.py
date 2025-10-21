"""
Guardrails de conteúdo para validar a intenção do prompt
Verifica se a mensagem está relacionada ao domínio do agente (reparos residenciais)
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

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
    
    # Padrões de perguntas legítimas
    QUESTION_PATTERNS = [
        r"\bcomo\s+(consertar|reparar|arrumar|resolver|instalar|trocar|fixar)",
        r"\bpor\s+que\s+(está|ta|ficou).+(quebrado|vazando|pingando|travando)",
        r"\bo\s+que\s+fazer\s+(quando|se|com)",
        r"\bpreciso\s+(consertar|reparar|arrumar|ajuda|resolver)",
        r"\btenho\s+(um\s+)?problema\s+(com|na|no)",
        r"\bestá\s+(quebrado|vazando|pingando|travando|entupido)",
        r"\b(dicas|tutorial|passo\s+a\s+passo|instruções)\s+(para|de)"
    ]
    
    # Tópicos proibidos (off-topic claro)
    PROHIBITED_TOPICS = [
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
        use_llm_validation: bool = True,
        model_name: str = "qwen2.5:3b",
        base_url: Optional[str] = None,
        strict_mode: bool = False
    ):
        """
        Inicializa o guardrail
        
        Args:
            use_llm_validation: Se True, usa LLM para validação adicional
            model_name: Nome do modelo para validação LLM
            base_url: URL base do Ollama
            strict_mode: Se True, aplica validação mais rigorosa
        """
        self.use_llm_validation = use_llm_validation
        self.strict_mode = strict_mode
        
        if use_llm_validation:
            self.llm = ChatOllama(
                model=model_name,
                temperature=0.0,  # Deterministico para classificação
                num_predict=50,   # Resposta curta
                base_url=base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            )
        else:
            self.llm = None
    
    def _check_prohibited_content(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se a mensagem contém conteúdo proibido
        
        Returns:
            (is_valid, reason)
        """
        message_lower = message.lower()
        
        for pattern in self.PROHIBITED_TOPICS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.warning(f"Conteúdo proibido detectado: {pattern}")
                return False, "Conteúdo inapropriado ou fora do escopo"
        
        return True, None
    
    def _check_repair_relevance(self, message: str) -> float:
        """
        Calcula score de relevância para reparos residenciais
        
        Returns:
            Score de 0.0 a 1.0
        """
        message_lower = message.lower()
        
        # Conta keywords encontradas
        keyword_count = sum(1 for keyword in self.REPAIR_KEYWORDS if keyword in message_lower)
        
        # Verifica padrões de pergunta
        pattern_matches = sum(1 for pattern in self.QUESTION_PATTERNS 
                            if re.search(pattern, message_lower, re.IGNORECASE))
        
        # Calcula score
        keyword_score = min(keyword_count / 3, 1.0)  # Normaliza em 3 keywords
        pattern_score = min(pattern_matches / 2, 1.0)  # Normaliza em 2 padrões
        
        # Média ponderada
        final_score = (keyword_score * 0.7) + (pattern_score * 0.3)
        
        logger.debug(f"Relevance score: {final_score:.2f} (keywords: {keyword_count}, patterns: {pattern_matches})")
        
        return final_score
    
    def _llm_validate(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Usa LLM para validar se a mensagem é sobre reparos residenciais
        
        Returns:
            (is_valid, reason)
        """
        if not self.llm:
            return True, None
        
        try:
            validation_prompt = SystemMessage(content="""Você é um classificador de mensagens.
Sua tarefa é determinar se uma mensagem é relacionada a REPAROS RESIDENCIAIS (consertos em casa, manutenção doméstica, DIY).

Responda APENAS com:
- "SIM" se a mensagem for sobre reparos/manutenção residencial
- "NAO" se for sobre outro assunto

Exemplos:
- "Como consertar torneira?" → SIM
- "Receita de bolo" → NAO
- "Problema com porta emperrada" → SIM
- "Previsão do tempo" → NAO""")
            
            user_message = HumanMessage(content=f"Mensagem: {message}\n\nClassificação:")
            
            response = self.llm.invoke([validation_prompt, user_message])
            classification = response.content.strip().upper()
            
            logger.debug(f"LLM classification: {classification}")
            
            if "NAO" in classification or "NÃO" in classification:
                return False, "Mensagem não relacionada a reparos residenciais"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Erro na validação LLM: {e}")
            # Em caso de erro, permite a mensagem (fail-open)
            return True, None
    
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
        
        # 3. Validação LLM (se habilitada)
        if self.use_llm_validation and relevance_score < 0.3:
            # Só usa LLM se o score de keywords for baixo
            is_valid, reason = self._llm_validate(message)
            if not is_valid:
                if self.strict_mode:
                    raise ContentGuardrailError(reason)
                return {"is_valid": False, "reason": reason, "score": relevance_score}
        
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


# Importação para evitar erro circular
import os
