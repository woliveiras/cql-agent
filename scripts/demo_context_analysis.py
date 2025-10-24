#!/usr/bin/env python3
"""
Demonstração: Análise de Contexto Sintático
============================================

Compara como o sistema diferencia:
- Frases completas (alta confiança)
- Perguntas estruturadas (média/alta confiança)
- Palavras isoladas (baixa confiança)
"""

from api.security.context_analyzer import ContextAnalyzer
from api.security.guardrails import ContentGuardrail


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def analyze_text(analyzer: ContextAnalyzer, text: str):
    """Analyze and display detailed results"""
    result = analyzer.analyze(text)
    
    print(f"\n📝 Texto: \"{text}\"")
    print(f"   └─ Tokens: {result.num_tokens}")
    print(f"   └─ Verbos: {result.verb_count} | Substantivos: {result.noun_count}")
    print(f"   └─ Profundidade sintática: {result.avg_dependency_depth:.2f}")
    
    # Características estruturais
    features = []
    if result.has_complete_sentence:
        features.append("✓ Frase completa")
    if result.has_main_verb:
        features.append("✓ Verbo principal")
    if result.has_question_pattern:
        features.append("✓ Padrão de pergunta")
    
    if features:
        print(f"   └─ Estrutura: {' | '.join(features)}")
    else:
        print(f"   └─ Estrutura: ⚠️  Fragmento/palavra isolada")
    
    # Score e confiança
    confidence_emoji = {
        "high": "🟢",
        "medium": "🟡", 
        "low": "🔴"
    }
    emoji = confidence_emoji.get(result.confidence_level, "⚪")
    
    print(f"\n   {emoji} Score de contexto: {result.context_score:.2f}")
    print(f"   {emoji} Confiança: {result.confidence_level.upper()}")


def compare_with_guardrail():
    """Compare context impact on guardrail scoring"""
    print_header("Integração com Guardrail")
    
    guardrail_with_context = ContentGuardrail(
        use_ner=False, 
        use_context_analysis=True
    )
    
    guardrail_without_context = ContentGuardrail(
        use_ner=False,
        use_context_analysis=False
    )
    
    messages = [
        "A torneira está vazando no banheiro",
        "torneira",
        "Como consertar torneira quebrada?"
    ]
    
    for msg in messages:
        print(f"\n📨 Mensagem: \"{msg}\"")
        
        with_ctx = guardrail_with_context.validate(msg)
        without_ctx = guardrail_without_context.validate(msg)
        
        print(f"   Com análise de contexto:    Score {with_ctx['score']:.2f} "
              f"({'✓ válido' if with_ctx['is_valid'] else '✗ inválido'})")
        print(f"   Sem análise de contexto:    Score {without_ctx['score']:.2f} "
              f"({'✓ válido' if without_ctx['is_valid'] else '✗ inválido'})")
        
        diff = with_ctx['score'] - without_ctx['score']
        if diff > 0:
            print(f"   📈 Ganho: +{diff:.2f} pontos com análise de contexto")
        elif diff < 0:
            print(f"   📉 Perda: {diff:.2f} pontos (fragmento identificado)")


def main():
    """Run all demonstrations"""
    analyzer = ContextAnalyzer()
    
    # 1. Frases completas
    print_header("1. Frases Completas (Alta Confiança)")
    complete_sentences = [
        "A torneira está vazando no banheiro",
        "Preciso consertar a porta que não fecha",
        "O chuveiro parou de funcionar hoje"
    ]
    for text in complete_sentences:
        analyze_text(analyzer, text)
    
    # 2. Perguntas estruturadas
    print_header("2. Perguntas Estruturadas (Média/Alta Confiança)")
    questions = [
        "Como consertar torneira quebrada?",
        "Onde fica o registro de água?",
        "Quando devo trocar o filtro?"
    ]
    for text in questions:
        analyze_text(analyzer, text)
    
    # 3. Palavras isoladas
    print_header("3. Palavras Isoladas (Baixa Confiança)")
    isolated_words = [
        "torneira",
        "vazamento",
        "consertar"
    ]
    for text in isolated_words:
        analyze_text(analyzer, text)
    
    # 4. Fragmentos vs sentenças
    print_header("4. Progressão: Fragmento → Frase Completa")
    progression = [
        "torneira",
        "torneira vazando",
        "A torneira está vazando",
        "A torneira está vazando no banheiro"
    ]
    print("\n📊 Observe como o score aumenta com mais contexto:\n")
    for i, text in enumerate(progression, 1):
        result = analyzer.analyze(text)
        bar = "█" * int(result.context_score * 50)
        print(f"{i}. {text:45} | {bar} {result.context_score:.2f}")
    
    # 5. Integração com guardrail
    compare_with_guardrail()
    
    # Summary
    print_header("Resumo")
    print("""
✨ Análise de Contexto Sintático:

✓ Detecta frases completas vs fragmentos
✓ Identifica padrões de perguntas (como, quando, onde)
✓ Analisa estrutura sintática (verbos, objetos, profundidade)
✓ Calcula score de confiança (0.0 - 1.0)
✓ Melhora validação de mensagens relevantes

📊 Impacto no Guardrail:
  • Frases completas: Score +20-30% maior
  • Palavras isoladas: Score permanece baixo (correto)
  • Perguntas válidas: Detectadas mesmo sem keywords específicas
    """)


if __name__ == "__main__":
    main()
