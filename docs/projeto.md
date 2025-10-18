# Desafio: Criar um AI Agent para reparos residenciais

Eu quero criar um AI Agent para ajudar o usuário a fazer pequenos reparos em sua casa quando algo aparecer

Eu quero ir por partes

Primeiro quero um agente básico que somente responde ao usuário com base em seu modelo

Na segunda fase quero um esquema onde vou utilizar RAG pra criar uma base de conhecimentos para este agente com alguns PDFs sobre reparos residenciais

Na terceira fase, quero conectar este agente com a internet através de uma Tool gratuita, como o DuckDuckGo, para responder perguntas sobre reparos residenciais que estejam fora de sua base de conhecimento

Na quarta fase, quero criar uma função Pipe para que possamos utilizar este agente no OpenWebUI

As tecnologias utilizadas devem ser:

- Python, PyDantic, UV
- LangChain
- Ollama
- LLM local (Ollama) via Docker
- ChromaDB via Docker
- RAG (Recuperação Augmentada por Geração)
- Ferramenta de busca gratuita (DuckDuckGo)
- PDFs como base de conhecimento
- Flask para criar uma API para ser usada com o OpenWebUI
- OpenWebUI via Docker
- Docker para containerização
- Modelo: qwen2.5:3b
