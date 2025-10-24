#!/usr/bin/env python3
"""
Demonstração do Sistema de Pesos para Keywords
"""

from api.security.guardrails import ContentGuardrail

print("=" * 80)
print("⚖️  DEMONSTRAÇÃO: SISTEMA DE PESOS PARA KEYWORDS")
print("=" * 80)

guardrail = ContentGuardrail(use_ner=False)  # Sem NER para focar nos pesos

mensagens = [
    # URGENTES (peso 3.0)
    ("🚨 URGENTE", "Socorro! Vazamento de gás urgente!"),
    ("🔥 EMERGÊNCIA", "Emergência: curto circuito com fogo!"),
    
    # CRÍTICOS (peso 2.0)
    ("⚠️  CRÍTICO", "Torneira quebrada e entupida"),
    ("💧 PROBLEMA", "Tem infiltração na parede"),
    
    # IMPORTANTES (peso 1.5)
    ("🔧 AÇÃO", "Preciso consertar e reparar a porta"),
    ("🛠️  MANUTENÇÃO", "Quero trocar o registro"),
    
    # CONTEXTUAIS (peso 1.0)
    ("🏠 CONTEXTO", "Tenho uma casa com porta e janela"),
    
    # OFF-TOPIC (sem keywords)
    ("❌ OFF-TOPIC", "Como funciona o sistema solar?"),
]

for categoria, msg in mensagens:
    print(f"\n{categoria}")
    print(f"  📝 \"{msg}\"")
    print("-" * 80)
    
    result = guardrail.validate(msg)
    
    if result['is_valid']:
        score = result['score']
        # Classifica o score
        if score > 0.3:
            nivel = "🟢 ALTO"
        elif score > 0.15:
            nivel = "🟡 MÉDIO"
        else:
            nivel = "🔵 BAIXO"
        
        print(f"  ✅ VÁLIDA - Score: {score:.2f} {nivel}")
    else:
        print(f"  ❌ INVÁLIDA - {result['reason']}")

print("\n" + "=" * 80)
print("📊 COMPARAÇÃO DE SCORES")
print("=" * 80)

comparacoes = [
    ("vazamento urgente", "porta quebrada", "Keywords urgentes vs críticas"),
    ("consertar reparar", "casa sala", "Keywords importantes vs contextuais"),
    ("vazamento gás fogo", "porta janela sala", "Múltiplas urgentes vs contextuais"),
]

for msg1, msg2, desc in comparacoes:
    result1 = guardrail.validate(msg1)
    result2 = guardrail.validate(msg2)
    
    print(f"\n📌 {desc}")
    print(f"  ➜ \"{msg1}\" → Score: {result1['score']:.2f}")
    print(f"  ➜ \"{msg2}\" → Score: {result2['score']:.2f}")
    
    if result1['score'] > result2['score']:
        diff = result1['score'] - result2['score']
        print(f"  ✓ Primeira tem score {diff:.2f} MAIOR")
    else:
        diff = result2['score'] - result1['score']
        print(f"  ✓ Segunda tem score {diff:.2f} MAIOR")

print("\n" + "=" * 80)
print("💡 SISTEMA DE PESOS")
print("=" * 80)
print("""
📊 Categorias de Pesos:

  🚨 URGENTES (peso 3.0):
     vazamento, urgente, emergência, fogo, gás, curto, choque, perigo
     → Situações de alto risco que requerem atenção imediata

  ⚠️  CRÍTICOS (peso 2.0):
     quebrado, entupido, infiltração, goteira, rachadura, defeito
     → Problemas graves que precisam atenção rápida

  🔧 IMPORTANTES (peso 1.5):
     consertar, reparar, trocar, instalar, problema, manutenção
     → Ações e problemas comuns de reparo

  🏠 CONTEXTUAIS (peso 1.0):
     Todos os outros termos (casa, porta, sala, etc.)
     → Termos descritivos e de localização

🎯 Impacto:
  • 1 keyword urgente ≈ 3 keywords contextuais
  • Permite priorizar mensagens de emergência
  • Score normalizado de 0.0 a 1.0
  • Integra com NER e fuzzy matching
""")
print("=" * 80)
