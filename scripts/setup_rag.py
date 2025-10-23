#!/usr/bin/env python
"""
Script de Setup RAG - Processa PDFs e cria base de conhecimento
"""

from agents.rag.vectorstore import VectorStoreManager
from agents.rag.loader import PDFLoader
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Processa PDFs e cria vector store"""

    print("=" * 60)
    print("🔧 Setup RAG - Base de Conhecimento")
    print("=" * 60)

    # Configurações
    pdf_directory = "./agents/rag/pdfs"
    chroma_directory = "./chroma_db"

    # Verificar se há PDFs
    pdf_path = Path(pdf_directory)
    if not pdf_path.exists():
        print(f"\n❌ Diretório '{pdf_directory}' não encontrado!")
        print("   Crie o diretório e adicione PDFs sobre reparos residenciais.")
        return

    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        print(f"\n⚠️  Nenhum PDF encontrado em '{pdf_directory}'")
        print("   Adicione PDFs sobre reparos residenciais para criar a base de conhecimento.")
        return

    try:
        # 1. Carregar e processar PDFs
        print("\n📚 Processando PDFs...")
        print("-" * 60)

        loader = PDFLoader(
            chunk_size=500,
            chunk_overlap=50
        )

        documents = loader.process_directory(pdf_directory)

        if not documents:
            print("\n❌ Nenhum documento foi extraído dos PDFs")
            return

        # 2. Criar vector store
        print("\n" + "-" * 60)
        print("💾 Criando base de conhecimento...")

        vectorstore_manager = VectorStoreManager(
            persist_directory=chroma_directory,
            collection_name="repair_docs",
            embedding_model="nomic-embed-text"
        )

        vectorstore_manager.create_vectorstore(documents)

        # 3. Testar busca
        print("\n" + "-" * 60)
        print("🧪 Testando busca...")

        test_query = "Como fazer reparo"
        results = vectorstore_manager.similarity_search(test_query, k=2)

        print(f"\n   Query: '{test_query}'")
        print(f"   Resultados: {len(results)} documentos encontrados")

        if results:
            print("\n   Exemplo do primeiro resultado:")
            print(f"   {results[0].page_content[:150]}...")

        # 4. Sucesso
        print("\n" + "=" * 60)
        print("✅ Base de conhecimento criada com sucesso!")
        print("=" * 60)
        print(f"\n📁 Vector store: {chroma_directory}")
        print(f"📄 Total de chunks: {len(documents)}")
        print(f"📚 PDFs processados: {len(pdf_files)}")
        print("\n💡 Agora você pode executar: uv run agents/repair_agent/agent.py")

    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
