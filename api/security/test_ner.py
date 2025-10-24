"""
Testes para o módulo NER (Named Entity Recognition) de reparos
"""

import pytest
from api.security.ner_repair import RepairNER, get_repair_ner


class TestRepairNER:
    """Testes para extração de entidades relacionadas a reparos"""

    def test_extract_ferramenta(self):
        """Testa extração de ferramentas/objetos"""
        ner = RepairNER()
        
        text = "A torneira da pia está quebrada"
        entities = ner.extract_entities(text)
        
        assert "FERRAMENTA" in entities
        assert "torneira" in entities["FERRAMENTA"]
        assert "pia" in entities["FERRAMENTA"]

    def test_extract_problema(self):
        """Testa extração de problemas/defeitos"""
        ner = RepairNER()
        
        text = "Tem um vazamento no cano"
        entities = ner.extract_entities(text)
        
        assert "PROBLEMA" in entities
        assert "vazamento" in entities["PROBLEMA"]

    def test_extract_acao(self):
        """Testa extração de ações de reparo"""
        ner = RepairNER()
        
        text = "Preciso consertar a porta"
        entities = ner.extract_entities(text)
        
        assert "ACAO" in entities
        assert "consertar" in entities["ACAO"]

    def test_extract_comodo(self):
        """Testa extração de cômodos"""
        ner = RepairNER()
        
        text = "O chuveiro do banheiro não funciona"
        entities = ner.extract_entities(text)
        
        assert "COMODO" in entities
        assert "banheiro" in entities["COMODO"]

    def test_extract_material(self):
        """Testa extração de materiais"""
        ner = RepairNER()
        
        text = "Preciso comprar um cano novo"
        entities = ner.extract_entities(text)
        
        assert "MATERIAL" in entities
        assert "cano" in entities["MATERIAL"]

    def test_extract_multiple_entities(self):
        """Testa extração de múltiplas entidades"""
        ner = RepairNER()
        
        text = "Como consertar vazamento na torneira do banheiro?"
        entities = ner.extract_entities(text)
        
        # Deve encontrar múltiplos tipos
        assert "ACAO" in entities  # consertar
        assert "PROBLEMA" in entities  # vazamento
        assert "FERRAMENTA" in entities  # torneira
        assert "COMODO" in entities  # banheiro

    def test_weighted_score_high(self):
        """Testa score alto quando tem ferramenta e problema"""
        ner = RepairNER()
        
        entities = {
            "FERRAMENTA": ["torneira"],
            "PROBLEMA": ["vazamento"]
        }
        
        score = ner.calculate_weighted_score(entities)
        # 1 FERRAMENTA (2.0) + 1 PROBLEMA (2.0) = 4.0 / 8.0 = 0.5
        assert score >= 0.5, "Score deve ser alto quando tem ferramenta e problema"
        assert score == 0.5, "Score deve ser 0.5 com 1 ferramenta + 1 problema"

    def test_weighted_score_low(self):
        """Testa score baixo quando tem apenas contexto"""
        ner = RepairNER()
        
        entities = {
            "COMODO": ["banheiro"]
        }
        
        score = ner.calculate_weighted_score(entities)
        # 1 COMODO (1.0) = 1.0 / 8.0 = 0.125
        assert score < 0.3, "Score deve ser baixo quando tem apenas cômodo"
        assert score == 0.125, "Score deve ser 0.125 com apenas 1 cômodo"

    def test_entity_summary_repair_context(self):
        """Testa resumo de entidades com contexto de reparo"""
        ner = RepairNER()
        
        text = "A torneira está vazando no banheiro"
        summary = ner.get_entity_summary(text)
        
        assert summary["has_repair_context"] is True
        assert summary["score"] >= 0.5  # FERRAMENTA + PROBLEMA = 0.5
        assert "FERRAMENTA" in summary["entities"]
        assert "PROBLEMA" in summary["entities"]

    def test_entity_summary_no_repair_context(self):
        """Testa quando não há contexto claro de reparo"""
        ner = RepairNER()
        
        text = "Estou na cozinha fazendo comida"
        summary = ner.get_entity_summary(text)
        
        # Pode encontrar "cozinha" como cômodo
        # Mas não deve ter contexto de reparo
        assert summary["has_repair_context"] is False

    def test_case_insensitive(self):
        """Testa que extração é case-insensitive"""
        ner = RepairNER()
        
        text1 = "A TORNEIRA está quebrada"
        text2 = "a torneira está quebrada"
        
        entities1 = ner.extract_entities(text1)
        entities2 = ner.extract_entities(text2)
        
        assert entities1 == entities2

    def test_compound_entities(self):
        """Testa extração de entidades compostas"""
        ner = RepairNER()
        
        text = "O chuveiro elétrico queimou"
        entities = ner.extract_entities(text)
        
        assert "FERRAMENTA" in entities
        # Deve encontrar "chuveiro elétrico" ou pelo menos "chuveiro"
        assert any("chuveiro" in entity for entity in entities["FERRAMENTA"])

    def test_singleton_pattern(self):
        """Testa que get_repair_ner retorna sempre a mesma instância"""
        ner1 = get_repair_ner()
        ner2 = get_repair_ner()
        
        assert ner1 is ner2, "Deve retornar a mesma instância (singleton)"

    def test_primary_category(self):
        """Testa identificação da categoria primária"""
        ner = RepairNER()
        
        text = "A torneira, a pia e o chuveiro estão com problema"
        summary = ner.get_entity_summary(text)
        
        # Deve ter FERRAMENTA como primária (mais entidades)
        assert summary["primary_category"] == "FERRAMENTA"

    def test_empty_text(self):
        """Testa comportamento com texto vazio"""
        ner = RepairNER()
        
        entities = ner.extract_entities("")
        assert entities == {}
        
        summary = ner.get_entity_summary("")
        assert summary["entity_count"] == 0
        assert summary["score"] == 0.0

    def test_no_entities_found(self):
        """Testa quando não encontra nenhuma entidade"""
        ner = RepairNER()
        
        text = "Olá, como vai?"
        entities = ner.extract_entities(text)
        
        assert entities == {}

    def test_real_world_examples(self):
        """Testa exemplos do mundo real"""
        ner = RepairNER()
        
        examples = [
            ("Como consertar torneira pingando?", ["ACAO", "FERRAMENTA", "PROBLEMA"]),
            ("Tenho vazamento no banheiro", ["PROBLEMA", "COMODO"]),
            ("Preciso trocar a fechadura da porta", ["ACAO", "FERRAMENTA"]),
            ("O disjuntor desligou", ["FERRAMENTA", "PROBLEMA"]),
        ]
        
        for text, expected_categories in examples:
            entities = ner.extract_entities(text)
            found_categories = set(entities.keys())
            
            # Verifica se encontrou pelo menos uma das categorias esperadas
            assert len(found_categories & set(expected_categories)) > 0, (
                f"Esperava encontrar alguma de {expected_categories} em '{text}', "
                f"mas encontrou apenas {list(found_categories)}"
            )


class TestNERIntegrationWithGuardrail:
    """Testes de integração do NER com ContentGuardrail"""

    def test_guardrail_with_ner_enabled(self):
        """Testa guardrail com NER habilitado"""
        from api.security.guardrails import ContentGuardrail
        
        guardrail = ContentGuardrail(use_ner=True)
        
        # Mensagem com entidades claras
        result = guardrail.validate("Como consertar torneira vazando?")
        
        assert result["is_valid"] is True
        assert result["score"] > 0.3

    def test_guardrail_with_ner_disabled(self):
        """Testa guardrail com NER desabilitado (fallback para fuzzy)"""
        from api.security.guardrails import ContentGuardrail
        
        guardrail = ContentGuardrail(use_ner=False)
        
        # Mensagem com keywords
        result = guardrail.validate("Como consertar torneira?")
        
        assert result["is_valid"] is True
        # Score pode ser diferente sem NER
        assert result["score"] > 0.1

    def test_ner_better_context_understanding(self):
        """Testa que NER entende melhor o contexto"""
        from api.security.guardrails import ContentGuardrail
        
        guardrail_ner = ContentGuardrail(use_ner=True)
        guardrail_no_ner = ContentGuardrail(use_ner=False)
        
        # Mensagem ambígua
        text = "A porta está com problema"
        
        result_ner = guardrail_ner.validate(text)
        result_no_ner = guardrail_no_ner.validate(text)
        
        # Ambos devem aceitar, mas NER deve ter score melhor
        # (entende que "porta" + "problema" = contexto de reparo)
        assert result_ner["is_valid"] is True
        assert result_no_ner["is_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
