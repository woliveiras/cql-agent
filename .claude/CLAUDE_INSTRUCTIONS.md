# Instruções para Claude Code - CQL Agent

## Visão Geral

**Stack**: Python 3.12 (FastAPI, LangChain, ChromaDB) + React 19 (TypeScript, Vite, Zustand)
**Gerenciadores**: UV (Python), pnpm (Node.js)
**LLM**: Multi-provider (Ollama/OpenAI/Gemini/Claude) via Factory Pattern
**Idioma**: Português (pt-BR) - prompts, docs, keywords

## Convenções de Código

### Python

- **Nomenclatura**: `snake_case` (funções/vars), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constantes)
- **Estilo**: Max 120 chars, complexidade ≤ 10, type hints obrigatórias, Pydantic models para schemas
- **Linting**: Flake8 (E9, F63, F7, F82) + Pylint (score ≥ 8.0)
- **Testes**: `test_*.py` colocated, pytest + pytest-asyncio

### TypeScript/React

- **Nomenclatura**: `camelCase` (funções/vars), `PascalCase` (componentes/types)
- **Estilo**: Max 100 chars, 2 espaços, aspas simples, semicolons always (Biome)
- **Estrutura**: `Component.tsx` + `Component.styles.ts` + `Component.test.tsx` + `index.ts`
- **State**: Zustand (global), TanStack Query (server), useState (local)
- **Testes**: Vitest + happy-dom + Testing Library

### Commits

- Você NUNCA deve commitar código

## Áreas Críticas

1. **`api/security/`**
   - NUNCA relaxe validações sem discussão
   - Teste: `uv run pytest api/security/ -v`

2. **`agents/llm/`**
   - Mudanças afetam TODOS os fluxos LLM
   - Valide: `uv run scripts/demo_llm_providers.py`

3. **`agents/rag/`**
   - Após mudanças: `rm -rf chroma_db/ && uv run scripts/setup_rag.py`

4. **`.env`**
   - NUNCA commite valores sensíveis
   - Mantenha `.env.example` atualizado

5. **`api/app.py`** (ALTA) - Endpoints com validação de segurança
   - Pydantic models obrigatórios
   - Teste: `uv run pytest api/test_api.py -v`

## Outputs e Documentação

- **Outputs Claude**: `.claude-outputs/` (já no `.gitignore`)
- **Docs**: `docs/` (apenas quando solicitado, formato Markdown, pt-BR)
- NÃO CRIE NENHUMA documentação adicional sem aprovação prévia

## Particularidades Importantes

- **Idioma pt-BR**: Prompts, keywords, docs, NER (SpaCy `pt_core_news_sm`)
- **UV obrigatório**: Backend (`uv sync`, extras: `--extra openai/google/anthropic/all-providers`)
- **pnpm obrigatório**: Frontend (não usar npm/yarn)
- **Ollama padrão**: LLM local gratuito (requer download manual de modelos)
- **ChromaDB**: Não commitar `chroma_db/` (gerado por `scripts/setup_rag.py`)
- **Segurança**: Pipeline de 6 camadas (Pydantic → Sanitization → Guardrails → Intention → Context → NER)
- **RAG Fallback**: RAG → Web Search (DuckDuckGo) → LLM
- **State Machine**: `NEW_PROBLEM → WAITING_FEEDBACK → RESOLVED | MAX_ATTEMPTS`

---

**Repo**: https://github.com/woliveiras/cql-agent
**Docs**: [README](README.md) | [LLM Providers](docs/LLM_PROVIDERS.md) | [RAG](docs/QUICK_START_RAG.md) | [Deploy](docs/GUIA_DEPLOY.md)
