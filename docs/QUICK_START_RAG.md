# 🚀 Quick Start - RAG

## Configuração Rápida do RAG

### 1. Baixar modelo de embeddings

```bash
docker exec -it ollama ollama pull nomic-embed-text
```

### 2. Adicionar PDFs

Coloque PDFs sobre reparos residenciais na pasta `pdfs/`:

```bash
pdfs/
├── manual_eletrica.pdf
├── manual_hidraulica.pdf
└── guia_reparos.pdf
```

### 3. Processar PDFs

```bash
uv run scripts/setup_rag.py
```

### 4. Testar

```bash
uv run agent.py
```

## ✅ Checklist

- [ ] Ollama rodando (`docker-compose up -d`)
- [ ] Modelo qwen2.5:3b instalado
- [ ] Modelo nomic-embed-text instalado
- [ ] PDFs na pasta `pdfs/`
- [ ] Base criada (`chroma_db/` existe)
- [ ] Agente testado

## 🔄 Atualizar base

Para adicionar novos PDFs:

1. Adicione os PDFs em `pdfs/`
2. Execute novamente: `uv run scripts/setup_rag.py`

## 🧪 Testar busca

```bash
# O agente agora busca automaticamente nos PDFs
# quando você faz uma pergunta sobre reparos
```

## ⚠️ Troubleshooting

### Erro: "modelo nomic-embed-text não encontrado"

```bash
docker exec -it ollama ollama pull nomic-embed-text
```

### Erro: "Nenhum PDF encontrado"

Adicione PDFs na pasta `pdfs/`

### Erro: "ChromaDB connection"

Verifique se há espaço em disco suficiente
