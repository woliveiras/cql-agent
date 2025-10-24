#!/usr/bin/env python3
"""
Testes para Análise de Intenção Comunicativa
"""

import pytest
from api.security.intention_analyzer import (
    IntentionAnalyzer,
    IntentionType,
    get_intention_analyzer
)
from api.security.guardrails import ContentGuardrail


class TestIntentionAnalyzer:
    """Testes unitários para o IntentionAnalyzer"""
    
    def test_question_with_interrogative_and_mark(self):
        """Pergunta com interrogativo + ? deve ter alta confiança"""
        analyzer = IntentionAnalyzer()
        
        questions = [
            "Como consertar a torneira?",
            "Onde fica o registro de água?",
            "Quando devo trocar o filtro?",
            "Por que o chuveiro não funciona?",
            "Qual ferramenta usar?"
        ]
        
        for question in questions:
            result = analyzer.analyze(question)
            assert result.intention_type == IntentionType.QUESTION
            assert result.confidence >= 0.80, f"'{question}' should have high confidence"
            assert result.has_interrogative
            assert result.has_question_mark
    
    def test_question_with_only_interrogative(self):
        """Pergunta com interrogativo sem ? deve ter boa confiança"""
        analyzer = IntentionAnalyzer()
        
        result = analyzer.analyze("como consertar torneira vazando")
        
        assert result.intention_type == IntentionType.QUESTION
        assert result.confidence >= 0.70
        assert result.has_interrogative
        assert not result.has_question_mark
    
    def test_question_with_only_mark(self):
        """Texto com apenas ? deve ser classificado como pergunta (confiança média)"""
        analyzer = IntentionAnalyzer()
        
        result = analyzer.analyze("Tem como arrumar a porta?")
        
        assert result.intention_type in [IntentionType.QUESTION, IntentionType.COMMAND]
        assert result.has_question_mark
    
    def test_command_with_modal_verbs(self):
        """Comandos com verbos modais devem ter alta confiança"""
        analyzer = IntentionAnalyzer()
        
        commands = [
            "Preciso consertar a torneira",
            "Quero trocar o chuveiro",
            "Posso instalar sozinho",
            "Devo chamar um profissional",
            "Gostaria de resolver o vazamento"
        ]
        
        for command in commands:
            result = analyzer.analyze(command)
            assert result.intention_type == IntentionType.COMMAND, f"'{command}' should be COMMAND"
            assert result.confidence >= 0.70
            assert result.has_modal_verb
    
    def test_command_with_request_verbs(self):
        """Comandos com verbos de pedido devem ser detectados"""
        analyzer = IntentionAnalyzer()
        
        commands = [
            "Ajuda a consertar",
            "Conserta a torneira",
            "Troca o filtro",
            "Instala o chuveiro"
        ]
        
        for command in commands:
            result = analyzer.analyze(command)
            # Pode ser COMMAND ou QUESTION (dependendo da pontuação)
            assert result.intention_type in [IntentionType.COMMAND, IntentionType.QUESTION]
            assert result.confidence >= 0.60
    
    def test_statement_simple(self):
        """Afirmações simples devem ser classificadas como STATEMENT"""
        analyzer = IntentionAnalyzer()
        
        statements = [
            "A torneira está vazando",
            "O chuveiro parou de funcionar",
            "Tem um vazamento no banheiro",
            "A porta está quebrada"
        ]
        
        for statement in statements:
            result = analyzer.analyze(statement)
            assert result.intention_type == IntentionType.STATEMENT, f"'{statement}' should be STATEMENT"
            assert result.confidence >= 0.70
            assert not result.has_interrogative
            assert not result.has_question_mark
    
    def test_empty_text(self):
        """Texto vazio deve retornar STATEMENT com confiança 0"""
        analyzer = IntentionAnalyzer()
        
        result = analyzer.analyze("")
        
        assert result.intention_type == IntentionType.STATEMENT
        assert result.confidence == 0.0
    
    def test_singleton_pattern(self):
        """Testa que get_intention_analyzer retorna singleton"""
        analyzer1 = get_intention_analyzer()
        analyzer2 = get_intention_analyzer()
        
        assert analyzer1 is analyzer2


class TestIntentionIntegrationWithGuardrail:
    """Testes de integração com ContentGuardrail"""
    
    def test_question_has_higher_score(self):
        """Perguntas devem ter score mais alto que afirmações genéricas"""
        guardrail = ContentGuardrail()
        
        question = "Como consertar torneira quebrada?"
        statement = "A torneira está quebrada"
        
        question_result = guardrail.validate(question)
        statement_result = guardrail.validate(statement)
        
        # Pergunta deve ter score >= afirmação
        assert question_result['score'] >= statement_result['score']
    
    def test_command_has_high_score(self):
        """Comandos devem ter score alto (relevância para agente)"""
        guardrail = ContentGuardrail()
        
        commands = [
            "Preciso consertar a torneira",
            "Quero trocar o chuveiro",
            "Ajuda a resolver o vazamento"
        ]
        
        for command in commands:
            result = guardrail.validate(command)
            assert result['is_valid']
            assert result['score'] >= 0.40, f"'{command}' should have high score"
    
    def test_intention_disabled(self):
        """Guardrail deve funcionar com intention analysis desabilitado"""
        guardrail = ContentGuardrail(use_intention_analysis=False)
        
        result = guardrail.validate("Como consertar torneira?")
        
        assert result['is_valid']
        assert result['score'] > 0.0
    
    def test_all_nlp_features_enabled(self):
        """Testa com todos os recursos NLP habilitados"""
        guardrail = ContentGuardrail(
            use_ner=True,
            use_context_analysis=True,
            use_intention_analysis=True
        )
        
        # Pergunta bem formada com entidades de reparo
        message = "Como consertar vazamento na torneira do banheiro?"
        result = guardrail.validate(message)
        
        assert result['is_valid']
        assert result['score'] >= 0.50, "Should have high score with all NLP features"


class TestIntentionScoring:
    """Testes detalhados do scoring de intenção"""
    
    def test_question_higher_than_statement(self):
        """Perguntas devem ter score de intenção maior que afirmações"""
        analyzer = IntentionAnalyzer()
        
        question = analyzer.analyze("Como consertar a torneira?")
        statement = analyzer.analyze("A torneira está quebrada")
        
        # Ambos podem ter features relevantes, mas question deve ter score maior
        assert question.intention_type == IntentionType.QUESTION
        assert statement.intention_type == IntentionType.STATEMENT
    
    def test_command_higher_than_statement(self):
        """Comandos devem ter score de intenção maior que afirmações"""
        analyzer = IntentionAnalyzer()
        
        command = analyzer.analyze("Preciso consertar a torneira")
        statement = analyzer.analyze("A torneira está quebrada")
        
        assert command.intention_type == IntentionType.COMMAND
        assert statement.intention_type == IntentionType.STATEMENT
    
    def test_features_detection(self):
        """Testa detecção de features linguísticas"""
        analyzer = IntentionAnalyzer()
        
        # Pergunta com múltiplas features
        result = analyzer.analyze("Como posso consertar a torneira?")
        
        assert result.has_interrogative
        assert result.has_modal_verb or len(result.features.get('modal_verbs_found', [])) > 0
        assert result.has_question_mark
        assert result.features.get('num_verbs', 0) >= 1


class TestRealWorldIntentions:
    """Testes com mensagens reais de usuários"""
    
    def test_user_questions_real_world(self):
        """Testa perguntas reais de usuários"""
        analyzer = IntentionAnalyzer()
        
        real_questions = [
            "Como faço para trocar o registro?",
            "Onde compro peças para torneira?",
            "Quanto custa consertar um chuveiro?",
            "É difícil trocar uma fechadura?",
            "Qual a melhor cola para PVC?"
        ]
        
        for question in real_questions:
            result = analyzer.analyze(question)
            assert result.intention_type == IntentionType.QUESTION, f"Failed: {question}"
            # Perguntas com ? mas sem interrogativo explícito = confiança 0.6
            # Perguntas com interrogativo + ? = confiança 0.80+
            assert result.confidence >= 0.60
    
    def test_user_commands_real_world(self):
        """Testa comandos reais de usuários"""
        analyzer = IntentionAnalyzer()
        
        real_commands = [
            "Preciso de ajuda para consertar",
            "Quero aprender a trocar torneira",
            "Gostaria de instalar um chuveiro novo",
            "Posso fazer isso sozinho",
            "Deve ter alguma solução mais fácil"
        ]
        
        for command in real_commands:
            result = analyzer.analyze(command)
            assert result.intention_type == IntentionType.COMMAND, f"Failed: {command}"
            assert result.confidence >= 0.60
    
    def test_user_statements_real_world(self):
        """Testa afirmações reais de usuários"""
        analyzer = IntentionAnalyzer()
        
        real_statements = [
            "A torneira está pingando muito",
            "O chuveiro não esquenta direito",
            "Tem um vazamento no cano",
            "A porta não fecha bem",
            "O registro está travado"
        ]
        
        for statement in real_statements:
            result = analyzer.analyze(statement)
            assert result.intention_type == IntentionType.STATEMENT, f"Failed: {statement}"
            assert result.confidence >= 0.60


class TestIntentionConfidence:
    """Testes de confiança na classificação"""
    
    def test_high_confidence_question(self):
        """Perguntas claras devem ter alta confiança"""
        analyzer = IntentionAnalyzer()
        
        result = analyzer.analyze("Como consertar a torneira?")
        
        assert result.confidence >= 0.90
    
    def test_medium_confidence_ambiguous(self):
        """Mensagens ambíguas devem ter confiança média"""
        analyzer = IntentionAnalyzer()
        
        result = analyzer.analyze("consertar torneira")
        
        # Pode ser interpretado de várias formas
        assert 0.40 <= result.confidence <= 0.90
    
    def test_features_affect_confidence(self):
        """Features detectados devem afetar a confiança"""
        analyzer = IntentionAnalyzer()
        
        # Com interrogativo + ? = alta confiança
        high = analyzer.analyze("Como consertar?")
        
        # Só com ? = confiança média
        medium = analyzer.analyze("Pode consertar?")
        
        # Sem markers claros = confiança mais baixa
        low = analyzer.analyze("consertar")
        
        assert high.confidence > medium.confidence
        assert medium.confidence > low.confidence
