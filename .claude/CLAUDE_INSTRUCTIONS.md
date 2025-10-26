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
**Formato**: `<type>: <description>` (inglês, imperativo, max 72 chars)
**Tipos**: `feat`, `fix`, `refac`, `chore`, `docs`, `test`, `perf`, `style`

## Áreas Críticas (SEMPRE testar após modificações)

1. **`api/security/`** (ALTA) - 7 componentes, 4600+ linhas, 136 testes
   - NUNCA relaxe validações sem discussão
   - Teste: `uv run pytest api/security/ -v`

2. **`agents/llm/`** (MÉDIA-ALTA) - Factory Pattern multi-provider
   - Mudanças afetam TODOS os fluxos LLM
   - Valide: `uv run scripts/demo_llm_providers.py`

3. **`agents/rag/`** (MÉDIA) - ChromaDB + embeddings
   - Após mudanças: `rm -rf chroma_db/ && uv run scripts/setup_rag.py`

4. **`.env`** (ALTA) - 80+ variáveis
   - NUNCA commite valores sensíveis
   - Mantenha `.env.example` atualizado

5. **`api/app.py`** (ALTA) - Endpoints com validação de segurança
   - Pydantic models obrigatórios
   - Teste: `uv run pytest api/test_api.py -v`

## Outputs e Documentação

- **Outputs Claude**: `.claude-outputs/` (já no `.gitignore`)
- **Docs**: `docs/` (apenas quando solicitado, formato Markdown, pt-BR)

## Particularidades Importantes

- **Idioma pt-BR**: Prompts, keywords, docs, NER (SpaCy `pt_core_news_sm`)
- **UV obrigatório**: Backend (`uv sync`, extras: `--extra openai/google/anthropic/all-providers`)
- **pnpm obrigatório**: Frontend (não usar npm/yarn)
- **Ollama padrão**: LLM local gratuito (requer download manual de modelos)
- **ChromaDB**: Não commitar `chroma_db/` (gerado por `scripts/setup_rag.py`)
- **Segurança**: Pipeline de 6 camadas (Pydantic → Sanitization → Guardrails → Intention → Context → NER)
- **RAG Fallback**: RAG → Web Search (DuckDuckGo) → LLM
- **State Machine**: `NEW_PROBLEM → WAITING_FEEDBACK → RESOLVED | MAX_ATTEMPTS`

## Checklist Pré-Commit

**Python**:
- [ ] Type hints + docstrings
- [ ] `uv run flake8 .` (sem erros críticos)
- [ ] `uv run pylint **/*.py --fail-under=8.0`
- [ ] `uv run pytest -v` (todos passam)
- [ ] Sem `print()` debug (use `logging`)

**TypeScript**:
- [ ] Tipos explícitos (evitar `any`)
- [ ] `pnpm lint` (passa)
- [ ] `pnpm build` (compila)
- [ ] `pnpm test` (passa)
- [ ] Sem `console.log` debug

**Git**:
- [ ] Commit: `<type>: <description>` (inglês, imperativo)
- [ ] Sem `.env`, `chroma_db/`, binários > 1MB
- [ ] Branch atualizada: `git pull --rebase origin main`

**Pré-PR**:
- [ ] Pipeline completo executado (backend + frontend)
- [ ] Coverage mantido/aumentado
- [ ] `.env.example` atualizado (se novas vars)
- [ ] Testado com Ollama (mínimo)

## Comandos Principais

### Backend (Python)
```bash
# Setup
uv sync                                # Deps base
uv sync --extra all-providers          # Com todos LLM providers

# Dev
uv run uvicorn api.app:app --reload    # API dev server
uv run scripts/setup_rag.py            # Processar PDFs → ChromaDB

# Testes
uv run pytest -v                       # Todos
uv run pytest api/security/ -v         # Segurança
uv run pytest --cov=api                # Com coverage

# Qualidade
uv run flake8 .                        # Lint
uv run pylint **/*.py --fail-under=8.0 # Análise
uv run pip-audit --desc                # Security scan
```

### Frontend (TypeScript)
```bash
# Setup (na pasta web/)
pnpm install

# Dev
pnpm dev                               # Dev server :5173
pnpm build                             # Build + typecheck

# Testes
pnpm test                              # Unit tests
pnpm test:coverage                     # Com coverage

# Qualidade
pnpm lint                              # Biome lint
pnpm audit --audit-level=moderate      # Security scan
```

### Docker
```bash
# Stack completo
docker-compose up -d                                    # Subir
docker exec -it ollama ollama pull qwen2.5:3b           # Baixar modelo LLM
docker exec -it ollama ollama pull nomic-embed-text     # Baixar modelo embedding
docker exec -it api uv run scripts/setup_rag.py         # Processar RAG
curl http://localhost:5000/health                       # Check API
# Acessar: http://localhost:5000/docs (Swagger) | http://localhost:8080 (OpenWebUI)
```

## Estrutura Crítica

```
cql-agent/
├── agents/
│   ├── llm/                    # Factory Pattern multi-provider
│   ├── repair_agent/           # State Machine + prompts
│   ├── rag/                    # ChromaDB + retrieval
│   └── tools/                  # Web search (DuckDuckGo)
├── api/
│   ├── app.py                  # FastAPI endpoints
│   └── security/               # 7 camadas validação (4600+ linhas, 136 testes)
├── web/src/
│   ├── components/             # UI reutilizáveis
│   ├── pages/                  # Welcome, Chat, Showcase
│   ├── services/               # API client (axios)
│   └── store/                  # Zustand + TanStack Query
├── scripts/                    # Demos e setup_rag.py
├── docs/                       # Guias (LLM, RAG, Deploy, OpenWebUI)
├── .env.example                # Template vars (80 linhas)
└── chroma_db/                  # Vector DB (gerado, não commitar)
```

---

**Repo**: https://github.com/woliveiras/cql-agent
**Docs**: [README](README.md) | [LLM Providers](docs/LLM_PROVIDERS.md) | [RAG](docs/QUICK_START_RAG.md) | [Deploy](docs/GUIA_DEPLOY.md)
