# Trabalho Passo a Passo

Inicializando Projeto CQL Agent

Instalação do UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Criando o projeto CQL Agent:

```bash
uv init --no-readme --no-pin-python
```

`uv init`: Cria a estrutura básica de um projeto Python gerenciado pelo UV, incluindo:

- Um arquivo `pyproject.toml` (configuração do projeto)
- Um arquivo `main.py` (script de exemplo)
- `--no-readme`: Não cria um arquivo README.md automaticamente
- `--no-pin-python`: Não fixa/especifica uma versão exata do Python no projeto (não cria o arquivo `.python-version`)

Adicionando as dependências necessárias:

```bash
uv add langchain langchain-ollama pydantic
```

Inicizalizando o Ollama:

```bash
docker-compose up -d
```

Baixando o modelo:

```bash
docker exec -it ollama ollama pull qwen2.5:3b
```

Executando o agente:

```bash
uv run agent.py
```

Adicionando dependências para RAG com ChromaDB e manipulação de PDFs:

```bash
uv add langchain-chroma chromadb pypdf langchain-community
```

Tornando o script de setup RAG executável:

```bash
chmod +x scripts/setup_rag.py
```
