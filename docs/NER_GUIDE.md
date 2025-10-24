# 🧠 NER (Named Entity Recognition) para Reparos Residenciais

## 📖 Visão Geral

O módulo NER identifica e extrai entidades relacionadas a reparos residenciais em mensagens dos usuários, fornecendo uma análise contextual inteligente para validação de conteúdo.

## 🎯 Funcionalidades

### Entidades Reconhecidas

O sistema identifica **5 categorias** de entidades:

1. **FERRAMENTA** (peso 2.0) 🔧
   - Objetos a serem reparados: torneira, porta, tomada, janela, etc.
   - ~50+ termos mapeados

2. **PROBLEMA** (peso 2.0) ⚠️
   - Defeitos e problemas: vazamento, quebrado, entupido, trincado, etc.
   - ~40+ termos mapeados

3. **ACAO** (peso 1.5) 🛠️
   - Verbos de reparo: consertar, trocar, arrumar, instalar, etc.
   - ~25+ termos mapeados

4. **COMODO** (peso 1.0) 🏠
   - Cômodos da casa: banheiro, cozinha, sala, quarto, etc.
   - ~15+ termos mapeados

5. **MATERIAL** (peso 1.0) 🧱
   - Materiais de construção: cano, fio, parafuso, tinta, etc.
   - ~20+ termos mapeados

**Total: 151 termos** no vocabulário de reparos

## 🔍 Como Funciona

### 1. Extração de Entidades

Usa `spaCy PhraseMatcher` para identificação rápida de padrões:

```python
from api.security.ner_repair import RepairNER

ner = RepairNER()
entities = ner.extract_entities("A torneira está vazando no banheiro")

# Resultado:
# {
#   "FERRAMENTA": ["torneira"],
#   "PROBLEMA": ["vazando"],
#   "COMODO": ["banheiro"]
# }
```

### 2. Score Ponderado

Calcula score de 0.0 a 1.0 baseado na importância das entidades:

```python
score = ner.calculate_weighted_score(entities)
# Score: 0.75 (FERRAMENTA + PROBLEMA são mais importantes)
```

**Fórmula:**

- Score máximo ideal = 8.0 (2 FERRAMENTAs × 2.0 + 2 PROBLEMAs × 2.0)
- Score normalizado = soma_ponderada / 8.0

### 3. Resumo Completo

```python
summary = ner.get_entity_summary("Preciso consertar a porta do quarto")

# {
#   "entities": {
#     "FERRAMENTA": ["porta"],
#     "ACAO": ["consertar"],
#     "COMODO": ["quarto"]
#   },
#   "score": 0.56,
#   "has_repair_context": True,  # FERRAMENTA + ACAO
#   "primary_category": "FERRAMENTA",
#   "entity_count": 3
# }
```

## 🛡️ Integração com Guardrails

O NER é integrado como **estratégia primária** no `ContentGuardrail`:

### Estratégia Multi-camadas

```python
from api.security.guardrails import ContentGuardrail

# NER habilitado (padrão)
guardrail = ContentGuardrail(use_ner=True)
result = guardrail.validate("Vazameto no banhero")  # Typos!

# ✅ Válida - Score: 0.17
# 🔄 Correções fuzzy: {'vazameto': 'vazamento'}
```

**Scoring Inteligente:**

1. **Se NER encontra contexto de reparo** (FERRAMENTA+PROBLEMA ou ACAO+FERRAMENTA):
   - 70% NER + 20% fuzzy keywords + 10% patterns

2. **Se NER não encontra contexto claro**:
   - 50% fuzzy keywords + 30% NER + 20% patterns

3. **Sem NER (use_ner=False)**:
   - 70% fuzzy keywords + 30% patterns

## 📊 Exemplos Práticos

### ✅ Mensagens Válidas

```python
ner = RepairNER()

# Alta relevância (FERRAMENTA + PROBLEMA)
summary = ner.get_entity_summary("A torneira está vazando")
# Score: 0.75, has_repair_context: True

# Média relevância (FERRAMENTA + ACAO)
summary = ner.get_entity_summary("Preciso consertar a porta")
# Score: 0.56, has_repair_context: True

# Com typos (NER não pega, mas fuzzy matching sim)
result = guardrail.validate("Tornera pingando")
# ✅ VÁLIDA - Correção: tornera → torneira
```

### ❌ Mensagens Inválidas

```python
# Off-topic (score = 0.0)
summary = ner.get_entity_summary("Como funciona o sistema solar?")
# Score: 0.0, has_repair_context: False

result = guardrail.validate("Como funciona o sistema solar?")
# ❌ INVÁLIDA - Mensagem não relacionada a reparos
```

## 🚀 Performance

### Lazy Loading

O modelo spaCy é carregado **apenas quando necessário**:

```python
guardrail = ContentGuardrail(use_ner=True)
# ← NER NÃO é carregado aqui

result = guardrail.validate("mensagem")
# ← NER é carregado AGORA (primeira validação)
```

### Singleton Pattern

Uma única instância do NER é compartilhada:

```python
from api.security.ner_repair import get_repair_ner

ner1 = get_repair_ner()
ner2 = get_repair_ner()

assert ner1 is ner2  # ✅ Mesma instância
```

## 🧪 Testes

Suite completa com **20 testes**:

```bash
# Testes NER
pytest api/security/test_ner.py -v

# Testes de integração
pytest api/security/test_ner.py::TestNERIntegrationWithGuardrail -v

# Todos os testes de segurança
pytest api/security/ -v
```

### Cobertura

- ✅ Extração de todas as 5 categorias de entidades
- ✅ Score ponderado (alto/baixo)
- ✅ Resumo de entidades e contexto de reparo
- ✅ Case insensitive
- ✅ Entidades compostas
- ✅ Singleton pattern
- ✅ Integração com guardrails
- ✅ Exemplos do mundo real

## 📈 Melhorias Futuras

- [ ] Expandir vocabulário com sinônimos regionais
- [ ] Suporte a entidades compostas ("torneira da pia")
- [ ] Detecção de negações ("não está vazando")
- [ ] Análise de sentimento (urgência)
- [ ] Cache de análises frequentes

## 🔧 Configuração

### Requisitos

```bash
pip install spacy rapidfuzz
python -m spacy download pt_core_news_sm
```

### Uso Básico

```python
from api.security.ner_repair import RepairNER
from api.security.guardrails import ContentGuardrail

# Apenas NER
ner = RepairNER()
summary = ner.get_entity_summary("mensagem")

# Validação completa (NER + fuzzy + patterns)
guardrail = ContentGuardrail(use_ner=True)
result = guardrail.validate("mensagem")
```

### Desabilitando NER

```python
# Usa apenas fuzzy matching + patterns
guardrail = ContentGuardrail(use_ner=False)
```

## 📚 Arquitetura

```text
api/security/
├── ner_repair.py         # 270 linhas - Core NER
├── guardrails.py         # Integração NER + validação
├── test_ner.py           # 250 linhas - 20 testes
└── test_security.py      # 56 testes (incluindo fuzzy)
```

## 🎓 Recursos

- [spaCy PhraseMatcher](https://spacy.io/api/phrasematcher)
- [NER Concepts](https://en.wikipedia.org/wiki/Named-entity_recognition)
- [Fuzzy Matching (rapidfuzz)](https://github.com/maxbachmann/rapidfuzz)

---

**Status:** ✅ Implementado e testado (76 testes passando)  
**Última atualização:** 2024-01-24
