# 📚 PDFs de Reparos Residenciais

Esta pasta deve conter PDFs sobre reparos residenciais para alimentar a base de conhecimento do agente.

## 📝 O que adicionar aqui

Coloque PDFs com informações sobre:

- ⚡ **Reparos elétricos**: Troca de tomadas, interruptores, fusíveis
- 🚰 **Reparos hidráulicos**: Torneiras, canos, vazamentos
- 🪟 **Reparos gerais**: Portas, janelas, fechaduras
- 🔧 **Manutenção**: Pintura, vedação, pequenos consertos
- 🏠 **Segurança**: Precauções e equipamentos de proteção

## 🎯 Formatos aceitos

- ✅ `.pdf` - Único formato suportado

## 💡 Onde encontrar PDFs

### Fontes gratuitas e legais

1. **Manuais de fabricantes**:
   - Sites de marcas de ferramentas e materiais
   - Documentação técnica de produtos

2. **Guias governamentais**:
   - Manuais de segurança residencial
   - Guias de manutenção predial

3. **Conteúdo educacional**:
   - Tutoriais do SENAI, SEBRAE
   - Guias de universidades técnicas

4. **Creative Commons**:
   - Archive.org
   - Google Scholar (artigos abertos)

## ⚙️ Após adicionar PDFs

Execute o script de setup para processar os documentos:

```bash
uv run scripts/setup_rag.py
```

Este comando irá:

1. Ler todos os PDFs desta pasta
2. Dividir em chunks
3. Criar embeddings
4. Armazenar no ChromaDB

## 📊 Estrutura esperada

```text
pdfs/
├── manual_eletrica.pdf
├── manual_hidraulica.pdf
├── guia_seguranca.pdf
└── ...
```

## ⚠️ Importante

- **Direitos autorais**: Apenas use PDFs que você tenha permissão
- **Qualidade**: PDFs com texto (não apenas imagens escaneadas)
- **Idioma**: Preferencialmente em português
- **Tamanho**: Cada PDF será dividido em chunks de ~500 caracteres

## 🔄 Atualizar base de conhecimento

Para adicionar novos PDFs:

1. Coloque os novos arquivos aqui
2. Execute novamente: `uv run scripts/setup_rag.py`
3. O sistema recriará a base com todos os PDFs

---

**Status atual**: 📁 Pasta vazia - Adicione PDFs para começar!
