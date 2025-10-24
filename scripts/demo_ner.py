#!/usr/bin/env python3
"""
Demonstração do NER (Named Entity Recognition) para reparos residenciais
"""

from api.security.ner_repair import RepairNER
from api.security.guardrails import ContentGuardrail

# Exemplos reais de mensagens
mensagens = [
    "A torneira da pia está vazando",
    "Preciso consertar a porta do quarto",
    "O chuveiro está quebrado e precisa trocar",
    "Como funciona o sistema solar?",  # Off-topic
    "Vazameto no banhero",  # Com typos (NER não pega, mas fuzzy sim)
]

print("=" * 80)
print("🔍 DEMONSTRAÇÃO DO NER (Named Entity Recognition)")
print("=" * 80)

ner = RepairNER()

for msg in mensagens:
    print(f"\n📝 Mensagem: \"{msg}\"")
    print("-" * 80)
    
    summary = ner.get_entity_summary(msg)
    
    if summary["entities"]:
        for entity_type, entities in summary["entities"].items():
            print(f"  ✓ {entity_type}: {entities}")
        
        print(f"\n  📊 Score NER: {summary['score']:.2f}")
        print(f"  🔧 Contexto de reparo: {'SIM ✅' if summary['has_repair_context'] else 'NÃO ❌'}")
        print(f"  🎯 Categoria principal: {summary['primary_category']}")
    else:
        print("  ❌ Nenhuma entidade encontrada")
        print(f"  📊 Score NER: {summary['score']:.2f}")

print("\n" + "=" * 80)
print("🛡️ VALIDAÇÃO COM GUARDRAIL (NER + FUZZY MATCHING)")
print("=" * 80)

guardrail = ContentGuardrail(use_ner=True)

for msg in mensagens:
    print(f"\n📝 Mensagem: \"{msg}\"")
    print("-" * 80)
    
    result = guardrail.validate(msg)
    
    if result['is_valid']:
        print(f"  ✅ VÁLIDA - Score: {result['score']:.2f}")
        if result.get('corrections'):
            print(f"  🔄 Correções fuzzy: {result['corrections']}")
    else:
        print(f"  ❌ INVÁLIDA - {result['reason']}")

print("\n" + "=" * 80)
