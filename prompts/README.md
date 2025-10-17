# Prompts do CQL AI Agent

Este diretório contém todos os prompts utilizados pelo agente de reparos residenciais, organizados por categoria.

## 📁 Estrutura

```text
prompts/
├── __init__.py       # Exporta todos os prompts
├── base.py           # Prompt base do sistema
├── states.py         # Prompts por estado da conversação
├── messages.py       # Mensagens de resposta
└── README.md         # Este arquivo
```

## 📝 Arquivos

### `base.py`

Contém o prompt base do sistema que define a personalidade e comportamento geral do agente.

**Exports:**

- `BASE_SYSTEM_PROMPT` - Prompt principal que define o agente como especialista em reparos

### `states.py`

Contém prompts específicos para cada estado da conversação.

**Exports:**

- `NEW_PROBLEM_PROMPT` - Instruções para quando um novo problema é apresentado
- `get_waiting_feedback_prompt()` - Prompt dinâmico para tentativas subsequentes
- `get_max_attempts_prompt()` - Prompt quando o limite de tentativas é atingido

### `messages.py`

Contém mensagens prontas que o agente retorna ao usuário.

**Exports:**

- `SUCCESS_MESSAGE` - Mensagem de celebração quando problema é resolvido
- `get_max_attempts_message()` - Mensagem quando sugere procurar profissional
- `AMBIGUOUS_FEEDBACK_MESSAGE` - Mensagem quando resposta do usuário é ambígua

## 🔧 Como Usar

### Importar todos os prompts

```python
from prompts import (
    BASE_SYSTEM_PROMPT,
    NEW_PROBLEM_PROMPT,
    get_waiting_feedback_prompt,
    SUCCESS_MESSAGE
)
```

### Exemplo de uso

```python
# Prompt base
prompt = BASE_SYSTEM_PROMPT

# Adicionar prompt de novo problema
prompt += NEW_PROBLEM_PROMPT

# Ou usar função dinâmica
feedback_prompt = get_waiting_feedback_prompt(current_attempt=2, max_attempts=3)
```

## ✏️ Modificando Prompts

Para modificar o comportamento do agente, edite os arquivos correspondentes:

- **Personalidade geral**: `base.py`
- **Perguntas ao usuário**: `states.py`
- **Mensagens de resposta**: `messages.py`

## 🎯 Boas Práticas

1. **Mantenha prompts concisos**: Modelos processam melhor instruções claras
2. **Use formatação**: Strings multilinha (""") para legibilidade
3. **Documente mudanças**: Comente o motivo de alterações importantes
4. **Teste alterações**: Sempre teste o agente após modificar prompts

## 📚 Referências

- [Guia de Prompt Engineering - OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)
- [LangChain Prompts](https://python.langchain.com/docs/modules/model_io/prompts/)
- [Ollama Prompt Engineering](https://github.com/ollama/ollama/blob/main/docs/modelfile.md#system)
