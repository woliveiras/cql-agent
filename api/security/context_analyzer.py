#!/usr/bin/env python3
"""
Análise de Contexto Sintático para Validação de Mensagens

Usa spaCy para analisar a estrutura sintática das mensagens e diferenciar:
- Frases completas e bem estruturadas (alta confiança)
- Palavras isoladas ou fragmentos (baixa confiança)

Técnicas:
- Dependency parsing: analisa relações sintáticas
- POS tagging: identifica classes gramaticais
- Sentence structure: verifica completude da frase
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContextAnalysis:
    """Resultado da análise de contexto"""
    has_complete_sentence: bool  # Tem frase completa com verbo + objeto
    has_main_verb: bool  # Tem verbo principal
    has_question_pattern: bool  # É uma pergunta estruturada
    num_tokens: int  # Quantidade de tokens
    num_sentences: int  # Quantidade de sentenças
    verb_count: int  # Quantidade de verbos
    noun_count: int  # Quantidade de substantivos
    avg_dependency_depth: float  # Profundidade média da árvore sintática
    context_score: float  # Score de contexto (0.0-1.0)
    confidence_level: str  # "high", "medium", "low"


class ContextAnalyzer:
    """
    Analisador de contexto sintático usando spaCy

    Avalia a qualidade do contexto da mensagem baseado em:
    1. Completude sintática (verbo + objeto + complementos)
    2. Estrutura de pergunta (WH-words + verbo)
    3. Complexidade sintática (profundidade de dependências)
    4. Densidade de conteúdo (substantivos vs função)
    """

    def __init__(self):
        """Inicializa o analisador (lazy loading do spaCy)"""
        self._nlp = None
        self._initialized = False

    @property
    def nlp(self):
        """Lazy loading do modelo spaCy"""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("pt_core_news_sm")
                logger.info("Modelo spaCy carregado para análise de contexto")
                self._initialized = True
            except Exception as e:
                logger.error(f"Erro ao carregar spaCy: {e}")
                raise
        return self._nlp

    def analyze(self, text: str) -> ContextAnalysis:
        """
        Analisa o contexto sintático da mensagem

        Args:
            text: Texto a ser analisado

        Returns:
            ContextAnalysis com métricas detalhadas
        """
        if not text or not text.strip():
            return self._empty_analysis()

        doc = self.nlp(text.lower())

        # Métricas básicas
        num_tokens = len([t for t in doc if not t.is_punct and not t.is_space])
        num_sentences = len(list(doc.sents))

        # Contagem de classes gramaticais
        verbs = [t for t in doc if t.pos_ == "VERB"]
        nouns = [t for t in doc if t.pos_ in ["NOUN", "PROPN"]]
        verb_count = len(verbs)
        noun_count = len(nouns)

        # Análise de completude
        has_main_verb = self._has_main_verb(doc)
        has_complete_sentence = self._has_complete_sentence(doc)
        has_question_pattern = self._has_question_pattern(doc)

        # Profundidade sintática
        avg_depth = self._calculate_dependency_depth(doc)

        # Calcula score de contexto
        context_score = self._calculate_context_score(
            num_tokens=num_tokens,
            has_main_verb=has_main_verb,
            has_complete_sentence=has_complete_sentence,
            has_question_pattern=has_question_pattern,
            verb_count=verb_count,
            noun_count=noun_count,
            avg_depth=avg_depth
        )

        # Define nível de confiança
        if context_score >= 0.7:
            confidence = "high"
        elif context_score >= 0.4:
            confidence = "medium"
        else:
            confidence = "low"

        logger.debug(
            f"Context analysis: tokens={num_tokens}, verbs={verb_count}, "
            f"nouns={noun_count}, complete={has_complete_sentence}, "
            f"score={context_score:.2f}"
        )

        return ContextAnalysis(
            has_complete_sentence=has_complete_sentence,
            has_main_verb=has_main_verb,
            has_question_pattern=has_question_pattern,
            num_tokens=num_tokens,
            num_sentences=num_sentences,
            verb_count=verb_count,
            noun_count=noun_count,
            avg_dependency_depth=avg_depth,
            context_score=context_score,
            confidence_level=confidence
        )

    def _empty_analysis(self) -> ContextAnalysis:
        """Retorna análise vazia para textos inválidos"""
        return ContextAnalysis(
            has_complete_sentence=False,
            has_main_verb=False,
            has_question_pattern=False,
            num_tokens=0,
            num_sentences=0,
            verb_count=0,
            noun_count=0,
            avg_dependency_depth=0.0,
            context_score=0.0,
            confidence_level="low"
        )

    def _has_main_verb(self, doc) -> bool:
        """
        Verifica se há um verbo principal (ROOT)

        Exemplo:
        - "A torneira está vazando" → True (está = ROOT)
        - "torneira vazamento" → False (sem verbo)
        """
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                return True
        return False

    def _has_complete_sentence(self, doc) -> bool:
        """
        Verifica se há uma frase completa (verbo + objeto/complemento)

        Critérios:
        - Tem verbo principal (ROOT)
        - Tem pelo menos um objeto direto, complemento ou sujeito
        - Pelo menos 3 tokens significativos

        Exemplos:
        - "Como consertar torneira" → True (verbo + objeto)
        - "A torneira está vazando" → True (sujeito + verbo + complemento)
        - "torneira" → False (apenas substantivo)
        - "consertar" → False (apenas verbo)
        """
        # Precisa ter verbo principal
        if not self._has_main_verb(doc):
            return False

        # Precisa ter mínimo de tokens
        tokens = [t for t in doc if not t.is_punct and not t.is_space]
        if len(tokens) < 3:
            return False

        # Procura por dependências que indicam frase completa
        complete_deps = ["obj", "dobj", "iobj", "nsubj", "nsubjpass", "ccomp", "xcomp"]

        for token in doc:
            if token.dep_ in complete_deps:
                return True

        return False

    def _has_question_pattern(self, doc) -> bool:
        """
        Detecta padrão de pergunta estruturada

        Padrões:
        - WH-words: como, quando, onde, porque, qual, quem
        - Ponto de interrogação
        - Verbo no início (inversão)

        Exemplos:
        - "Como consertar torneira?" → True
        - "Onde está o vazamento?" → True
        - "torneira quebrada" → False
        """
        text = doc.text.lower()

        # WH-words em português
        wh_words = ["como", "quando", "onde", "porque", "por que", "qual", "quem", "quanto"]
        has_wh = any(wh in text for wh in wh_words)

        # Ponto de interrogação
        has_question_mark = "?" in text

        # Verbo no início ou logo após WH-word
        has_verb_pattern = False
        tokens = [t for t in doc if not t.is_punct and not t.is_space]
        if len(tokens) >= 2:
            # Verbo é um dos 2 primeiros tokens
            has_verb_pattern = any(t.pos_ == "VERB" for t in tokens[:2])

        return (has_wh or has_question_mark) and has_verb_pattern

    def _calculate_dependency_depth(self, doc) -> float:
        """
        Calcula profundidade média da árvore de dependências

        Maior profundidade = frase mais complexa/estruturada
        Menor profundidade = palavras isoladas

        Exemplos:
        - "Como consertar a torneira da pia?" → profundidade ~2-3
        - "torneira" → profundidade 0
        """
        if not doc:
            return 0.0

        depths = []
        for token in doc:
            depth = 0
            current = token
            # Sobe na árvore até a raiz
            while current.head != current:
                depth += 1
                current = current.head
            depths.append(depth)

        return sum(depths) / len(depths) if depths else 0.0

    def _calculate_context_score(
        self,
        num_tokens: int,
        has_main_verb: bool,
        has_complete_sentence: bool,
        has_question_pattern: bool,
        verb_count: int,
        noun_count: int,
        avg_depth: float
    ) -> float:
        """
        Calcula score de contexto baseado em múltiplos fatores

        Score de 0.0 a 1.0:
        - 1.0: Frase completa, bem estruturada, clara
        - 0.5: Estrutura parcial, contexto médio
        - 0.0: Palavras isoladas, sem contexto

        Fatores:
        - Completude sintática (40%)
        - Quantidade de tokens (20%)
        - Densidade de conteúdo (20%)
        - Profundidade sintática (20%)
        """
        score = 0.0

        # Fator 1: Completude sintática (40%)
        if has_complete_sentence:
            score += 0.4
        elif has_main_verb:
            score += 0.2
        elif has_question_pattern:
            score += 0.3

        # Fator 2: Quantidade de tokens (20%)
        # 1-2 tokens = 0.0, 3-4 = 0.1, 5+ = 0.2
        if num_tokens >= 5:
            score += 0.2
        elif num_tokens >= 3:
            score += 0.1

        # Fator 3: Densidade de conteúdo (20%)
        # Proporção de substantivos e verbos
        content_words = verb_count + noun_count
        if num_tokens > 0:
            density = content_words / num_tokens
            score += min(density * 0.2, 0.2)

        # Fator 4: Profundidade sintática (20%)
        # Profundidade > 1.5 indica estrutura complexa
        if avg_depth >= 2.0:
            score += 0.2
        elif avg_depth >= 1.0:
            score += 0.1

        return min(score, 1.0)


# Singleton global (lazy initialization)
_context_analyzer_instance = None


def get_context_analyzer() -> ContextAnalyzer:
    """
    Retorna instância singleton do ContextAnalyzer

    Garante que apenas uma instância do modelo spaCy é carregada
    """
    global _context_analyzer_instance
    if _context_analyzer_instance is None:
        _context_analyzer_instance = ContextAnalyzer()
    return _context_analyzer_instance
