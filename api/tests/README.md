# Test Suite - CQL Agent

Esta pasta contém todos os testes automatizados do CQL Agent, organizados por tipo e escopo.

## Estrutura de Diretórios

```
api/tests/
├── unit/              # Testes unitários (componentes isolados)
│   └── security/      # Testes de módulos de segurança
│       ├── test_sanitizer.py           # Sanitização de entrada
│       ├── test_ner.py                 # Named Entity Recognition
│       ├── test_context_analysis.py    # Análise de contexto
│       ├── test_intention_analysis.py  # Análise de intenção
│       └── test_weighted_keywords.py   # Sistema de pesos
├── integration/       # Testes de integração (múltiplos componentes)
│   ├── test_api.py            # Endpoints da API
│   ├── test_api_security.py   # Fluxo de segurança da API
│   └── test_security_flow.py  # Fluxo completo de segurança
├── conftest.py        # Fixtures compartilhadas
└── README.md          # Este arquivo
```

## Tipos de Testes

### Unit Tests (api/tests/unit/)

Testes de componentes isolados, sem dependências externas:

- **Sanitização** (`test_sanitizer.py`): Validação de entrada, detecção de SQL injection, XSS, command injection
- **NER** (`test_ner.py`): Extração de entidades (ferramentas, problemas, ações, cômodos)
- **Context Analysis** (`test_context_analysis.py`): Análise sintática e estrutural de mensagens
- **Intention Analysis** (`test_intention_analysis.py`): Classificação de intenção (pergunta, comando, afirmação)
- **Weighted Keywords** (`test_weighted_keywords.py`): Sistema de pesos para keywords de reparo

### Integration Tests (api/tests/integration/)

Testes de fluxos completos envolvendo múltiplos componentes:

- **API** (`test_api.py`): Testes de endpoints REST
- **API Security** (`test_api_security.py`): Validação do pipeline de segurança
- **Security Flow** (`test_security_flow.py`): Fluxo end-to-end de segurança

## Como Executar os Testes

### Executar todos os testes

```bash
pytest
```

### Executar apenas testes unitários

```bash
pytest api/tests/unit/
```

### Executar apenas testes de integração

```bash
pytest api/tests/integration/
```

### Executar testes de um módulo específico

```bash
# Testes de sanitização
pytest api/tests/unit/security/test_sanitizer.py

# Testes de NER
pytest api/tests/unit/security/test_ner.py

# Testes de API
pytest api/tests/integration/test_api.py
```

### Executar com cobertura de código

```bash
# Cobertura completa
pytest --cov

# Cobertura com relatório HTML
pytest --cov --cov-report=html

# Ver relatório
open htmlcov/index.html
```

### Executar testes por marcadores

```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Excluir testes lentos
pytest -m "not slow"
```

### Modo verboso com detalhes

```bash
pytest -vv
```

### Executar testes com saída detalhada

```bash
pytest -vv --tb=long
```

## Fixtures Disponíveis (conftest.py)

O arquivo `conftest.py` fornece fixtures compartilhadas para facilitar os testes:

### Guardrails

- `guardrail`: ContentGuardrail padrão
- `strict_guardrail`: ContentGuardrail em modo strict
- `guardrail_no_ner`: ContentGuardrail sem NER
- `guardrail_with_all_features`: ContentGuardrail com todos os recursos NLP

### Analisadores

- `repair_ner`: Instância do RepairNER
- `context_analyzer`: Instância do ContextAnalyzer
- `intention_analyzer`: Instância do IntentionAnalyzer

### Dados de Teste

- `valid_repair_messages`: Lista de mensagens válidas
- `invalid_messages`: Lista de mensagens inválidas (fora do escopo)
- `malicious_inputs`: Lista de inputs maliciosos para testes de segurança

### Exemplo de Uso

```python
def test_with_fixture(guardrail, valid_repair_messages):
    """Testa guardrail com mensagens válidas"""
    for msg in valid_repair_messages:
        result = guardrail.validate(msg)
        assert result['is_valid']
```

## Requisitos

Os testes requerem as seguintes dependências (já incluídas no pyproject.toml):

- `pytest>=8.0.0`
- `pytest-cov>=4.1.0`
- `pytest-asyncio>=0.21.0`
- `httpx>=0.27.0` (para testes de API)

## Configuração

A configuração do pytest está em `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=api",
    "--cov=agents",
    "--cov-report=html",
    "--cov-report=term-missing",
]
```

## Boas Práticas

1. **Isolamento**: Testes unitários não devem ter dependências externas
2. **Nomes descritivos**: Use nomes que descrevem o comportamento testado
3. **Arrange-Act-Assert**: Organize os testes em três seções claras
4. **Fixtures**: Reutilize fixtures do conftest.py quando possível
5. **Marcadores**: Use `@pytest.mark.integration` ou `@pytest.mark.unit`
6. **Documentação**: Adicione docstrings explicando o que cada teste valida

## Adicionando Novos Testes

### Teste Unitário

1. Crie o arquivo em `tests/unit/<modulo>/test_<nome>.py`
2. Importe as fixtures necessárias
3. Use `@pytest.mark.unit` se quiser marcar explicitamente
4. Execute: `pytest tests/unit/<modulo>/test_<nome>.py`

### Teste de Integração

1. Crie o arquivo em `tests/integration/test_<nome>.py`
2. Use `@pytest.mark.integration`
3. Execute: `pytest tests/integration/test_<nome>.py`

## Troubleshooting

### Erro de importação

Se encontrar erros de importação, certifique-se de estar executando os testes do diretório raiz do projeto:

```bash
cd /path/to/cql-agent
pytest
```

### Modelo spaCy não encontrado

Instale o modelo português:

```bash
python -m spacy download pt_core_news_sm
```

### Testes lentos

Para pular testes lentos:

```bash
pytest -m "not slow"
```
