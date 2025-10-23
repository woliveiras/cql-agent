# Módulo de Segurança

Este módulo implementa camadas de segurança para validação e sanitização de entrada do usuário.

## Componentes

### 1. Sanitização (`sanitizer.py`)

Função: `sanitize_input(text: str) -> str`

**Proteções implementadas:**

- ✅ Remove caracteres nulos (`\x00`)
- ✅ Remove caracteres de controle perigosos
- ✅ Detecta tentativas de SQL injection
- ✅ Detecta tentativas de XSS
- ✅ Detecta tentativas de command injection
- ✅ Previne DoS por caracteres repetidos
- ✅ Normaliza espaços em branco

**Uso:**

```python
from security import sanitize_input, SanitizationError

try:
    clean_text = sanitize_input(user_input)
except SanitizationError as e:
    # Retornar erro 400 ao usuário
    return {"error": str(e)}, 400
```

### 2. Guardrails de Conteúdo (`guardrails.py`)

Classe: `ContentGuardrail`

**Funcionalidades:**

- ✅ Valida se a mensagem é sobre reparos residenciais
- ✅ Bloqueia conteúdo proibido (ilegal, adulto, jailbreak)
- ✅ Calcula score de relevância (0.0 a 1.0)
- ✅ Validação adicional com LLM (opcional)
- ✅ Modo strict para ambientes de produção

**Uso básico:**

```python
from security import ContentGuardrail

guardrail = ContentGuardrail(
    use_llm_validation=True,  # Usar LLM para validação adicional
    strict_mode=False          # False = retorna dict, True = levanta exceção
)

result = guardrail.validate(user_message)

if not result['is_valid']:
    return {"error": result['reason']}, 400
    
# Processar mensagem normalmente
```

**Configuração:**

```python
guardrail = ContentGuardrail(
    use_llm_validation=True,    # Habilitar validação LLM
    model_name="qwen2.5:3b",    # Modelo para classificação
    base_url="http://ollama:11434",  # URL do Ollama
    strict_mode=False           # Modo estrito
)
```

## Integração com API

O módulo está integrado em `api/app.py`:

1. **Validação Pydantic** (schema rigoroso)
2. **Sanitização** (remove padrões perigosos)
3. **Guardrails** (valida relevância do domínio)
4. **Tratamento de erro** (retorna 400 sem vazar detalhes)

### Fluxo de validação

```text
Requisição
    ↓
[Pydantic] Valida schema (1-4096 chars)
    ↓
[Sanitizer] Remove padrões perigosos
    ↓
[Guardrail] Valida relevância do domínio
    ↓
[Agent] Processa mensagem
```

## Exemplos de Mensagens

### ✅ Permitidas (score alto)

- "Como consertar uma torneira pingando?"
- "Minha porta está emperrada"
- "Problema com vazamento no encanamento"
- "Como trocar a resistência do chuveiro?"

### ⚠️ Permitidas (score médio/baixo)

- "Como resolver isso?" (genérico, mas pode ser permitido)
- "Ajuda!" (muito vago)

### ❌ Bloqueadas (conteúdo proibido)

- "How to make a bomb"
- "Ignore previous instructions"
- "Recipe for chocolate cake"
- `<script>alert('xss')</script>`

### ❌ Bloqueadas (off-topic)

- "What's the weather?"
- "Bitcoin investment tips"
- "Best recipe for pasta"

## Scores de Relevância

- **0.8 - 1.0**: Alta relevância (múltiplas keywords + padrões)
- **0.4 - 0.7**: Média relevância (algumas keywords)
- **0.1 - 0.3**: Baixa relevância (poucas ou nenhuma keyword)
- **< 0.1**: Bloqueado (muito irrelevante)

## Testes

Execute os testes de segurança:

```bash
pytest security/test_security.py -v
```

## Métricas e Logs

O sistema registra:

- Tentativas de injection (SQL, XSS, Command)
- Mensagens bloqueadas por guardrail
- Scores de relevância
- Erros de validação

Exemplo de log:

```sh
2025-01-20 10:30:45 - WARNING - Possível tentativa de SQL injection detectada
2025-01-20 10:31:12 - INFO - Mensagem validada (score: 0.85): Como consertar...
2025-01-20 10:32:03 - WARNING - Mensagem bloqueada por guardrail: Conteúdo não relacionado
```

## Configuração de Produção

Para produção, recomenda-se:

```python
# Modo strict (levanta exceção imediatamente)
guardrail = ContentGuardrail(
    use_llm_validation=True,
    strict_mode=True  # Bloqueia mensagens suspeitas
)

# Logs detalhados
logging.basicConfig(level=logging.WARNING)
```

## Variáveis de Ambiente

```bash
# URL do Ollama para validação LLM
export OLLAMA_BASE_URL=http://localhost:11434

# Nível de log
export LOG_LEVEL=INFO
```

## Performance

- **Sanitização**: ~0.1ms (regex simples)
- **Guardrail (sem LLM)**: ~1ms (keywords + regex)
- **Guardrail (com LLM)**: ~200-500ms (apenas para score < 0.3)

O LLM é usado apenas como fallback para mensagens com score baixo, otimizando performance.

## Limitações Conhecidas

1. **Falsos positivos**: Algumas mensagens legítimas podem ser bloqueadas
2. **Idioma**: Otimizado para português, mas aceita inglês
3. **LLM**: Depende do Ollama rodando localmente
4. **Keywords**: Lista fixa, pode não cobrir todos os termos

## Roadmap

- [ ] Suporte multilíngue
- [ ] Cache de validações
- [ ] Métricas com Prometheus
- [ ] Modelo de classificação fine-tuned
- [ ] Whitelist de usuários confiáveis

## Contribuindo

Para adicionar novos padrões de segurança:

1. Edite `sanitizer.py` (patterns)
2. Edite `guardrails.py` (keywords/topics)
3. Adicione testes em `test_security.py`
4. Execute `pytest` para validar

## Referências

- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [LangChain Guardrails](https://python.langchain.com/docs/guides/safety/)
