#!/usr/bin/env python3
"""
Intention Analyzer - Classificação de Intenção de Mensagens
===========================================================

Classifica a intenção comunicativa de mensagens em:
- QUESTION: Perguntas (busca por informação)
- COMMAND: Comandos/Pedidos (solicitação de ação)
- STATEMENT: Afirmações (declaração de fato)

Usa análise linguística para detectar:
- Pronomes interrogativos (como, quando, onde, por que)
- Verbos modais (posso, preciso, quero, deve)
- Modo verbal (imperativo, subjuntivo)
- Pontuação (?, !)
- Estrutura sintática

Author: William Oliveira
Date: 2025-10-24
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import spacy

logger = logging.getLogger(__name__)


class IntentionType(Enum):
    """Tipos de intenção comunicativa"""
    QUESTION = "question"        # Pergunta - busca informação
    COMMAND = "command"          # Comando/Pedido - solicita ação
    STATEMENT = "statement"      # Afirmação - declara fato


@dataclass
class IntentionAnalysis:
    """Resultado da análise de intenção"""
    intention_type: IntentionType
    confidence: float  # 0.0 - 1.0
    has_interrogative: bool
    has_modal_verb: bool
    has_imperative: bool
    has_question_mark: bool
    verb_mood: Optional[str]  # indicativo, imperativo, subjuntivo
    features: Dict[str, any]


class IntentionAnalyzer:
    """
    Analisa a intenção comunicativa de mensagens
    
    Classifica mensagens em:
    - QUESTION: "Como consertar torneira?", "Onde fica o registro?"
    - COMMAND: "Preciso consertar a porta", "Quero trocar o chuveiro"
    - STATEMENT: "A torneira está vazando", "O chuveiro parou"
    
    Examples:
        >>> analyzer = IntentionAnalyzer()
        >>> result = analyzer.analyze("Como consertar a torneira?")
        >>> result.intention_type
        IntentionType.QUESTION
        >>> result.confidence
        0.95
    """
    
    # Pronomes e advérbios interrogativos
    INTERROGATIVES = {
        'como', 'quando', 'onde', 'por que', 'porque', 'qual', 'quais',
        'quem', 'quanto', 'quantos', 'o que', 'que'
    }
    
    # Verbos modais que indicam comando/pedido
    MODAL_VERBS = {
        'preciso', 'precisar', 'precisa',
        'quero', 'querer', 'quer',
        'posso', 'poder', 'pode',
        'devo', 'dever', 'deve',
        'consigo', 'conseguir', 'consegue',
        'gostaria', 'gostar', 'gosta',
        'poderia', 'deveria', 'quereria'
    }
    
    # Verbos de solicitação/pedido
    REQUEST_VERBS = {
        'ajudar', 'ajuda', 'ajude',
        'fazer', 'faça', 'faz',
        'consertar', 'conserte', 'conserta',
        'trocar', 'troque', 'troca',
        'instalar', 'instale', 'instala',
        'resolver', 'resolva', 'resolve',
        'arrumar', 'arrume', 'arruma'
    }
    
    def __init__(self):
        """Inicializa o analisador de intenção"""
        self._nlp = None
        
    @property
    def nlp(self):
        """Lazy loading do modelo spaCy"""
        if self._nlp is None:
            self._nlp = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy carregado para análise de intenção")
        return self._nlp
    
    def analyze(self, text: str) -> IntentionAnalysis:
        """
        Analisa a intenção comunicativa do texto
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            IntentionAnalysis com tipo, confiança e features detectados
        """
        if not text or not text.strip():
            return IntentionAnalysis(
                intention_type=IntentionType.STATEMENT,
                confidence=0.0,
                has_interrogative=False,
                has_modal_verb=False,
                has_imperative=False,
                has_question_mark=False,
                verb_mood=None,
                features={}
            )
        
        text = text.strip()
        doc = self.nlp(text.lower())
        
        # Detecta features linguísticas
        has_interrogative = self._has_interrogative(text)
        has_modal_verb = self._has_modal_verb(text)
        has_imperative = self._has_imperative(doc)
        has_question_mark = text.endswith('?')
        verb_mood = self._detect_verb_mood(doc)
        
        features = {
            'interrogatives_found': self._find_interrogatives(text),
            'modal_verbs_found': self._find_modal_verbs(text),
            'request_verbs_found': self._find_request_verbs(text),
            'num_verbs': len([token for token in doc if token.pos_ == "VERB"]),
            'ends_with_question': has_question_mark,
            'ends_with_exclamation': text.endswith('!')
        }
        
        # Classifica intenção
        intention_type, confidence = self._classify_intention(
            has_interrogative=has_interrogative,
            has_modal_verb=has_modal_verb,
            has_imperative=has_imperative,
            has_question_mark=has_question_mark,
            verb_mood=verb_mood,
            features=features
        )
        
        return IntentionAnalysis(
            intention_type=intention_type,
            confidence=confidence,
            has_interrogative=has_interrogative,
            has_modal_verb=has_modal_verb,
            has_imperative=has_imperative,
            has_question_mark=has_question_mark,
            verb_mood=verb_mood,
            features=features
        )
    
    def _has_interrogative(self, text: str) -> bool:
        """Verifica se tem pronome/advérbio interrogativo"""
        text_lower = text.lower()
        
        # Verifica interrogativos no início (mais comum em perguntas)
        words = text_lower.split()
        if words and words[0] in self.INTERROGATIVES:
            return True
        
        # Verifica interrogativos como palavras completas (não parte de outra palavra)
        # Evita falsos positivos como "quebrada" contendo "que"
        import re
        for interr in self.INTERROGATIVES:
            # Usa word boundary para match exato
            pattern = r'\b' + re.escape(interr) + r'\b'
            if re.search(pattern, text_lower):
                # Verifica se é realmente interrogativo e não parte de outra construção
                # "o que" ou "que" isolado = interrogativo
                # "que" em "quebrada", "quero" = não interrogativo
                if interr == 'que':
                    # "que" só é interrogativo se:
                    # 1. Está no início: "que ferramenta?"
                    # 2. Vem após "o": "o que fazer?"
                    # 3. Está isolado com espaços: "qual que é?"
                    if re.search(r'(^que\b|\bo\s+que\b|\bqual\s+que\b)', text_lower):
                        return True
                else:
                    return True
        
        return False
    
    def _has_modal_verb(self, text: str) -> bool:
        """Verifica se tem verbo modal (pedido/comando)"""
        text_lower = text.lower()
        return any(modal in text_lower for modal in self.MODAL_VERBS)
    
    def _has_imperative(self, doc) -> bool:
        """Verifica se tem verbo no imperativo"""
        for token in doc:
            if token.pos_ == "VERB" and token.morph.get("Mood"):
                if "Imp" in token.morph.get("Mood"):
                    return True
        return False
    
    def _detect_verb_mood(self, doc) -> Optional[str]:
        """Detecta o modo verbal predominante"""
        moods = []
        for token in doc:
            if token.pos_ == "VERB":
                mood = token.morph.get("Mood")
                if mood:
                    moods.extend(mood)
        
        if not moods:
            return None
        
        # Retorna o mood mais comum
        mood_map = {
            "Ind": "indicativo",
            "Imp": "imperativo",
            "Sub": "subjuntivo",
            "Cnd": "condicional"
        }
        
        most_common = max(set(moods), key=moods.count) if moods else None
        return mood_map.get(most_common, most_common)
    
    def _find_interrogatives(self, text: str) -> List[str]:
        """Encontra interrogativos presentes no texto"""
        text_lower = text.lower()
        return [interr for interr in self.INTERROGATIVES if interr in text_lower]
    
    def _find_modal_verbs(self, text: str) -> List[str]:
        """Encontra verbos modais presentes no texto"""
        text_lower = text.lower()
        return [modal for modal in self.MODAL_VERBS if modal in text_lower]
    
    def _find_request_verbs(self, text: str) -> List[str]:
        """Encontra verbos de pedido presentes no texto"""
        text_lower = text.lower()
        return [verb for verb in self.REQUEST_VERBS if verb in text_lower]
    
    def _classify_intention(
        self,
        has_interrogative: bool,
        has_modal_verb: bool,
        has_imperative: bool,
        has_question_mark: bool,
        verb_mood: Optional[str],
        features: Dict
    ) -> tuple[IntentionType, float]:
        """
        Classifica a intenção com base nas features detectadas
        
        Regras de classificação:
        1. QUESTION (alta prioridade):
           - Tem interrogativo + ? = 0.95
           - Tem interrogativo sem ? = 0.80
           - Tem apenas ? no final = 0.60
        
        2. COMMAND (média-alta prioridade):
           - Tem modal + verbo de pedido = 0.90
           - Tem modal = 0.75
           - Tem imperativo = 0.85
           - Tem verbo de pedido = 0.65
        
        3. STATEMENT (fallback):
           - Nenhuma das anteriores = 0.70
           - Afirmação simples = 0.80
        
        Returns:
            (intention_type, confidence)
        """
        # QUESTION - mais específico primeiro
        if has_interrogative and has_question_mark:
            return IntentionType.QUESTION, 0.95
        
        if has_interrogative:
            return IntentionType.QUESTION, 0.80
        
        if has_question_mark:
            # ? pode ser usado em comandos educados: "Pode consertar?"
            if has_modal_verb or features.get('modal_verbs_found'):
                return IntentionType.COMMAND, 0.75
            return IntentionType.QUESTION, 0.60
        
        # COMMAND - pedidos e comandos
        modal_verbs = features.get('modal_verbs_found', [])
        request_verbs = features.get('request_verbs_found', [])
        
        if has_imperative:
            return IntentionType.COMMAND, 0.85
        
        if modal_verbs and request_verbs:
            return IntentionType.COMMAND, 0.90
        
        if has_modal_verb or modal_verbs:
            return IntentionType.COMMAND, 0.75
        
        if request_verbs:
            return IntentionType.COMMAND, 0.65
        
        if verb_mood == "imperativo":
            return IntentionType.COMMAND, 0.80
        
        # STATEMENT - fallback
        # Afirmações com verbos indicativos
        if verb_mood == "indicativo" or features.get('num_verbs', 0) > 0:
            return IntentionType.STATEMENT, 0.80
        
        # Fallback genérico
        return IntentionType.STATEMENT, 0.70


# Singleton instance
_intention_analyzer_instance = None


def get_intention_analyzer() -> IntentionAnalyzer:
    """
    Retorna instância singleton do IntentionAnalyzer
    
    Returns:
        IntentionAnalyzer instance
    """
    global _intention_analyzer_instance
    if _intention_analyzer_instance is None:
        _intention_analyzer_instance = IntentionAnalyzer()
    return _intention_analyzer_instance
