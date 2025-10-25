"""
Vector Store Manager - Gerencia o banco vetorial ChromaDB
"""

from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma

from agents.llm import EmbeddingsFactory


class VectorStoreManager:
    """Gerencia o armazenamento vetorial com ChromaDB"""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "repair_docs",
        embedding_model: Optional[str] = None
    ):
        """
        Inicializa o gerenciador de vector store

        Args:
            persist_directory: Diretório para persistir o banco
            collection_name: Nome da coleção no ChromaDB
            embedding_model: Modelo de embeddings (usa padrão do provedor se None)
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.embeddings = EmbeddingsFactory.create_embeddings(
            model=embedding_model
        )

        self.vectorstore: Optional[Chroma] = None

    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        Cria um novo vector store a partir de documentos

        Args:
            documents: Lista de documentos para indexar

        Returns:
            Vector store criado
        """
        print(f"\n🔄 Criando vector store com {len(documents)} documentos...")

        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )

        print(f"✅ Vector store criado em: {self.persist_directory}")
        return self.vectorstore

    def load_vectorstore(self) -> Optional[Chroma]:
        """
        Carrega um vector store existente

        Returns:
            Vector store carregado ou None se não existir
        """
        persist_path = Path(self.persist_directory)

        if not persist_path.exists():
            print(f"⚠️  Vector store não encontrado em: {self.persist_directory}")
            return None

        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            print(f"✅ Vector store carregado de: {self.persist_directory}")
            return self.vectorstore
        except Exception as e:
            print(f"❌ Erro ao carregar vector store: {e}")
            return None

    def get_or_create_vectorstore(self, documents: Optional[List[Document]] = None) -> Chroma:
        """
        Carrega vector store existente ou cria um novo

        Args:
            documents: Documentos para criar novo store (se necessário)

        Returns:
            Vector store
        """
        # Tentar carregar existente
        vectorstore = self.load_vectorstore()

        if vectorstore is None:
            if documents is None:
                raise ValueError("Vector store não existe e nenhum documento foi fornecido")

            # Criar novo
            vectorstore = self.create_vectorstore(documents)

        return vectorstore

    def add_documents(self, documents: List[Document]):
        """
        Adiciona novos documentos ao vector store existente

        Args:
            documents: Documentos para adicionar
        """
        if self.vectorstore is None:
            raise ValueError("Vector store não inicializado. Use create_vectorstore() primeiro.")

        print(f"➕ Adicionando {len(documents)} documentos ao vector store...")
        self.vectorstore.add_documents(documents)
        print("✅ Documentos adicionados")

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        score_threshold: float = 1.0
    ) -> List[Document]:
        """
        Busca documentos similares à query

        Args:
            query: Texto da busca
            k: Número de documentos a retornar
            score_threshold: Threshold máximo de distância (menor = mais similar)
                           ChromaDB retorna distâncias, então usamos <=
                           Valores típicos: 0.3 (muito similar) a 1.0 (similar)

        Returns:
            Lista de documentos mais similares
        """
        if self.vectorstore is None:
            raise ValueError("Vector store não inicializado")

        # Buscar com scores
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)

        # Filtrar por threshold (ChromaDB usa distância: menor = mais similar)
        filtered_docs = [
            doc for doc, score in docs_with_scores
            if score <= score_threshold
        ]

        return filtered_docs

    def delete_collection(self):
        """Remove a coleção do vector store"""
        if self.vectorstore is not None:
            self.vectorstore.delete_collection()
            print(f"🗑️  Coleção '{self.collection_name}' removida")
