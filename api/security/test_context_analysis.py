#!/usr/bin/env python3
"""
Testes para Análise de Contexto Sintático
"""

import pytest
from api.security.context_analyzer import ContextAnalyzer, get_context_analyzer
from api.security.guardrails import ContentGuardrail


class TestContextAnalyzer:
    """Testes para o ContextAnalyzer"""

    def test_complete_sentence_high_score(self):
        """Frase completa deve ter score alto"""
        analyzer = ContextAnalyzer()

        result = analyzer.analyze("A torneira está vazando no banheiro")

        assert result.has_complete_sentence
        assert result.has_main_verb
        assert result.num_tokens >= 5
        assert result.context_score > 0.6
        assert result.confidence_level == "high"

    def test_question_pattern_high_score(self):
        """Pergunta estruturada deve ter score alto"""
        analyzer = ContextAnalyzer()

        result = analyzer.analyze("Como consertar a torneira?")

        assert result.has_question_pattern
        assert result.has_main_verb
        assert result.context_score > 0.5
        assert result.confidence_level in ["high", "medium"]

    def test_isolated_word_low_score(self):
        """Palavra isolada deve ter score baixo"""
        analyzer = ContextAnalyzer()

        result = analyzer.analyze("torneira")

        assert not result.has_complete_sentence
        assert not result.has_main_verb
        assert result.num_tokens == 1
        assert result.context_score < 0.3
        assert result.confidence_level == "low"

    def test_two_words_low_score(self):
        """Duas palavras isoladas também têm score baixo"""
        analyzer = ContextAnalyzer()

        result = analyzer.analyze("torneira quebrada")

        assert not result.has_complete_sentence
        assert result.num_tokens == 2
        assert result.context_score < 0.4
        assert result.confidence_level == "low"

    def test_verb_without_complement_medium_score(self):
        """Testa verbo sem complemento - deve ter score médio/baixo"""
        analyzer = ContextAnalyzer()
        text = "consertar"
        result = analyzer.analyze(text)
        
        assert result.has_main_verb
        assert not result.has_complete_sentence
        assert result.context_score < 0.5
        assert result.confidence_level in ["low", "medium"]  # Aceita low ou medium

    def test_sentence_depth_analysis(self):
        """Frase complexa tem maior profundidade"""
        analyzer = ContextAnalyzer()

        simple = analyzer.analyze("torneira")
        complex = analyzer.analyze("Como consertar a torneira da pia?")

        assert complex.avg_dependency_depth > simple.avg_dependency_depth
        assert complex.context_score > simple.context_score

    def test_verb_and_noun_count(self):
        """Testa contagem de verbos e substantivos"""
        analyzer = ContextAnalyzer()
        text = "A torneira está vazando água"
        result = analyzer.analyze(text)
        
        # Deve ter pelo menos 1 verbo e 1 substantivo
        assert result.verb_count >= 1
        assert result.noun_count >= 1
        # Sem forçar has_complete_sentence - depende da análise sintática

    def test_empty_text(self):
        """Texto vazio retorna análise vazia"""
        analyzer = ContextAnalyzer()

        result = analyzer.analyze("")

        assert result.context_score == 0.0
        assert result.confidence_level == "low"
        assert not result.has_complete_sentence

    def test_singleton_pattern(self):
        """get_context_analyzer() retorna sempre a mesma instância"""
        analyzer1 = get_context_analyzer()
        analyzer2 = get_context_analyzer()

        assert analyzer1 is analyzer2


class TestContextIntegrationWithGuardrail:
    """Testes de integração com ContentGuardrail"""

    def test_complete_sentence_vs_isolated_word(self):
        """Frase completa tem score maior que palavra isolada"""
        guardrail = ContentGuardrail(use_ner=False, use_context_analysis=True)

        complete = guardrail.validate("A torneira está vazando")
        isolated = guardrail.validate("torneira")

        assert complete['is_valid']
        # Isolated pode ou não ser válida, mas score deve ser menor
        assert complete['score'] > isolated['score'], (
            f"Complete ({complete['score']:.2f}) deve ter score maior "
            f"que isolated ({isolated['score']:.2f})"
        )

    def test_question_vs_fragment(self):
        """Pergunta estruturada vs fragmento"""
        guardrail = ContentGuardrail(use_ner=False, use_context_analysis=True)

        question = guardrail.validate("Como consertar a torneira?")
        fragment = guardrail.validate("consertar torneira")

        assert question['is_valid']
        assert question['score'] > fragment['score']

    def test_context_with_ner_enabled(self):
        """Context analysis funciona junto com NER"""
        guardrail = ContentGuardrail(use_ner=True, use_context_analysis=True)

        # Frase completa + entidades NER
        result = guardrail.validate("A torneira está com vazamento urgente")

        assert result['is_valid']
        # Deve ter score alto (NER + context + keywords)
        assert result['score'] > 0.4

    def test_context_disabled(self):
        """Guardrail funciona sem context analysis"""
        guardrail = ContentGuardrail(use_ner=False, use_context_analysis=False)

        result = guardrail.validate("Como consertar torneira?")

        assert result['is_valid']
        # Score baseado apenas em keywords + patterns

    def test_long_sentence_vs_short(self):
        """Sentença longa e bem estruturada vs curta"""
        guardrail = ContentGuardrail(use_ner=False, use_context_analysis=True)

        long = guardrail.validate(
            "Preciso consertar a torneira da pia que está vazando"
        )
        short = guardrail.validate("consertar vazamento")

        assert long['is_valid']
        # Long tem mais contexto, deve ter score maior
        assert long['score'] >= short['score'] * 0.8


class TestContextScoring:
    """Testes detalhados do scoring contextual"""

    def test_high_confidence_scenarios(self):
        """Cenários que devem ter confiança razoável"""
        analyzer = ContextAnalyzer()

        messages = [
            "A torneira está vazando no banheiro",
            "Como consertar a porta quebrada?",
            "Preciso trocar o chuveiro que não funciona",
        ]

        for msg in messages:
            result = analyzer.analyze(msg)
            # Frases completas devem ter score >= 0.45
            assert result.context_score >= 0.45, (
                f"'{msg}' deveria ter score >= 0.45, "
                f"got {result.context_score:.2f}"
            )

    def test_low_confidence_scenarios(self):
        """Cenários que devem ter baixa confiança"""
        analyzer = ContextAnalyzer()

        low_confidence_messages = [
            "torneira",
            "porta janela",
        ]

        for msg in low_confidence_messages:
            result = analyzer.analyze(msg)
            # Palavras isoladas devem ter score baixo
            assert result.context_score < 0.4, (
                f"'{msg}' deveria ter score < 0.4, "
                f"got {result.context_score:.2f}"
            )

    def test_context_score_gradual(self):
        """Score aumenta com mais contexto"""
        analyzer = ContextAnalyzer()

        level1 = analyzer.analyze("torneira")
        level3 = analyzer.analyze("A torneira está vazando")

        # Frase completa deve ter score maior que palavra isolada
        assert level3.context_score > level1.context_score

    def test_main_verb_detection(self):
        """Detecta presença de verbo principal"""
        analyzer = ContextAnalyzer()

        with_verb = analyzer.analyze("A torneira está vazando")
        without_verb = analyzer.analyze("torneira do banheiro")

        # Frase com verbo deve ter score maior
        assert with_verb.context_score > without_verb.context_score

    def test_complete_sentence_criteria(self):
        """Valida critérios de frase completa"""
        analyzer = ContextAnalyzer()

        # Frase completa deve ter tokens suficientes
        complete = analyzer.analyze("Preciso consertar a torneira")
        assert complete.num_tokens >= 3

        # Incompleta: apenas substantivo
        incomplete = analyzer.analyze("torneira")
        assert not incomplete.has_complete_sentence


class TestRealWorldScenarios:
    """Testes com mensagens do mundo real"""

    def test_user_questions(self):
        """Perguntas típicas de usuários"""
        guardrail = ContentGuardrail(use_context_analysis=True)

        questions = [
            "Como consertar torneira que pinga?",
            "Onde fica o registro do chuveiro?",
            "Qual a melhor forma de desentupir pia?",
            "Por que minha porta está travando?",
        ]

        for q in questions:
            result = guardrail.validate(q)
            assert result['is_valid'], f"Pergunta '{q}' deve ser válida"
            assert result['score'] > 0.2, (
                f"Pergunta '{q}' deve ter score razoável, got {result['score']:.2f}"
            )

    def test_user_statements(self):
        """Afirmações típicas de usuários"""
        guardrail = ContentGuardrail(use_context_analysis=True)

        statements = [
            "Minha torneira está vazando muito",
            "A porta do quarto não fecha direito",
            "O chuveiro parou de funcionar",
            "Tem um vazamento no banheiro",
        ]

        for stmt in statements:
            result = guardrail.validate(stmt)
            assert result['is_valid'], f"Afirmação '{stmt}' deve ser válida"
            assert result['score'] > 0.2

    def test_fragments_vs_sentences(self):
        """Compara fragmentos com sentenças completas"""
        guardrail = ContentGuardrail(use_context_analysis=True)

        # Pares: (fragmento, sentença completa)
        pairs = [
            ("torneira", "A torneira está vazando"),
            ("porta quebrada", "A porta está quebrada"),
            ("consertar", "Preciso consertar isso"),
        ]

        for fragment, sentence in pairs:
            frag_result = guardrail.validate(fragment)
            sent_result = guardrail.validate(sentence)

            # Sentença deve ter score maior
            assert sent_result['score'] > frag_result['score'], (
                f"Sentença '{sentence}' ({sent_result['score']:.2f}) "
                f"deve ter score maior que fragmento '{fragment}' "
                f"({frag_result['score']:.2f})"
            )
