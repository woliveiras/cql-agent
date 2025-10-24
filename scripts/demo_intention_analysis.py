#!/usr/bin/env python3
"""
Demonstração: Análise de Intenção Comunicativa
==============================================

Classifica a intenção de mensagens em:
- QUESTION: Perguntas (busca informação)
- COMMAND: Comandos/Pedidos (solicita ação)
- STATEMENT: Afirmações (declara fato)
"""

from api.security.intention_analyzer import IntentionAnalyzer, IntentionType
from api.security.guardrails import ContentGuardrail


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def analyze_intention(analyzer: IntentionAnalyzer, text: str):
    """Analyze and display intention results"""
    result = analyzer.analyze(text)
    
    # Tipo emoji
    type_emoji = {
        IntentionType.QUESTION: "❓",
        IntentionType.COMMAND: "⚡",
        IntentionType.STATEMENT: "💬"
    }
    emoji = type_emoji.get(result.intention_type, "⚪")
    
    # Confiança
    conf_emoji = "🟢" if result.confidence >= 0.80 else "🟡" if result.confidence >= 0.60 else "🔴"
    
    print(f"\n{emoji} \"{text}\"")
    print(f"   └─ Tipo: {result.intention_type.value.upper()}")
    print(f"   └─ {conf_emoji} Confiança: {result.confidence:.2f}")
    
    # Features detectados
    features = []
    if result.has_interrogative:
        features.append(f"✓ Interrogativo ({', '.join(result.features.get('interrogatives_found', []))})")
    if result.has_modal_verb:
        features.append(f"✓ Verbo modal ({', '.join(result.features.get('modal_verbs_found', [])[:2])})")
    if result.has_question_mark:
        features.append("✓ Pontuação de pergunta (?)")
    if result.features.get('request_verbs_found'):
        features.append(f"✓ Verbo de pedido ({', '.join(result.features.get('request_verbs_found', [])[:2])})")
    
    if features:
        print(f"   └─ Features: {' | '.join(features)}")


def compare_with_guardrail():
    """Compare intention impact on guardrail scoring"""
    print_header("Integração com Guardrail")
    
    guardrail_with = ContentGuardrail(use_intention_analysis=True)
    guardrail_without = ContentGuardrail(use_intention_analysis=False)
    
    messages = [
        ("❓ PERGUNTA", "Como consertar torneira quebrada?"),
        ("⚡ COMANDO", "Preciso trocar o chuveiro urgente"),
        ("💬 AFIRMAÇÃO", "A porta está quebrada")
    ]
    
    for label, msg in messages:
        print(f"\n{label}: \"{msg}\"")
        
        with_result = guardrail_with.validate(msg)
        without_result = guardrail_without.validate(msg)
        
        print(f"   Com análise de intenção:    Score {with_result['score']:.2f} "
              f"({'✓ válido' if with_result['is_valid'] else '✗ inválido'})")
        print(f"   Sem análise de intenção:    Score {without_result['score']:.2f} "
              f"({'✓ válido' if without_result['is_valid'] else '✗ inválido'})")
        
        diff = with_result['score'] - without_result['score']
        if diff > 0:
            print(f"   📈 Ganho: +{diff:.2f} pontos com análise de intenção")
        elif diff < 0:
            print(f"   📉 Perda: {diff:.2f} pontos")


def main():
    """Run all demonstrations"""
    analyzer = IntentionAnalyzer()
    
    # 1. Perguntas
    print_header("1. Perguntas (QUESTION) - Busca por Informação")
    questions = [
        "Como consertar a torneira?",
        "Onde fica o registro de água?",
        "Quando devo trocar o filtro?",
        "Por que o chuveiro não funciona?",
        "Qual ferramenta usar para isso?"
    ]
    for q in questions:
        analyze_intention(analyzer, q)
    
    # 2. Comandos/Pedidos
    print_header("2. Comandos (COMMAND) - Solicitação de Ação")
    commands = [
        "Preciso consertar a torneira urgente",
        "Quero trocar o chuveiro",
        "Posso fazer isso sozinho?",
        "Gostaria de aprender a instalar",
        "Ajuda a resolver o vazamento"
    ]
    for c in commands:
        analyze_intention(analyzer, c)
    
    # 3. Afirmações
    print_header("3. Afirmações (STATEMENT) - Declaração de Fato")
    statements = [
        "A torneira está vazando",
        "O chuveiro parou de funcionar",
        "Tem um vazamento no banheiro",
        "A porta não fecha direito",
        "O registro está travado"
    ]
    for s in statements:
        analyze_intention(analyzer, s)
    
    # 4. Comparação de tipos
    print_header("4. Comparação: Mesmo Tema, Intenções Diferentes")
    
    examples = [
        ("❓ Pergunta", "Como consertar a torneira?"),
        ("⚡ Comando", "Preciso consertar a torneira"),
        ("💬 Afirmação", "A torneira está quebrada")
    ]
    
    print("\n📊 Observe como a intenção muda o score:\n")
    for label, text in examples:
        result = analyzer.analyze(text)
        bar = "█" * int(result.confidence * 50)
        print(f"{label:15} | {text:35} | {bar} {result.confidence:.2f}")
    
    # 5. Integração com guardrail
    compare_with_guardrail()
    
    # Summary
    print_header("Resumo")
    print("""
✨ Análise de Intenção Comunicativa:

📋 Classifica mensagens em 3 tipos:
   ❓ QUESTION  - Perguntas (busca informação)
   ⚡ COMMAND   - Comandos/Pedidos (solicita ação)
   💬 STATEMENT - Afirmações (declara fato)

🔍 Detecta features linguísticas:
   • Pronomes interrogativos (como, quando, onde, por que)
   • Verbos modais (preciso, quero, posso, devo)
   • Verbos de pedido (ajudar, consertar, trocar, instalar)
   • Modo verbal (imperativo, indicativo, subjuntivo)
   • Pontuação (?, !)

📊 Impacto no Guardrail:
   • Perguntas:   Score alto (busca por informação = relevante)
   • Comandos:    Score muito alto (pedido direto = altamente relevante)
   • Afirmações:  Score médio (contexto, mas menos acionável)

🎯 Benefícios:
   • Prioriza perguntas e comandos sobre afirmações genéricas
   • Melhora detecção de mensagens acionáveis
   • Reduz falsos positivos de afirmações fora de contexto
   • Scoring mais inteligente baseado em intenção comunicativa
    """)


if __name__ == "__main__":
    main()
