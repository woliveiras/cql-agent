"""
Vector Store Manager - Gerencia o ChromaDB e embeddings
"""

from pathlib import Path
from typing import List, Optional
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


class VectorStoreManager:
    """Gerencia o armazenamento vetorial com ChromaDB"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "repair_docs",
        embedding_model: str = "nomic-embed-text",
        ollama_base_url: str = "http://localhost:11434"
    ):
        """
        Inicializa o gerenciador de vector store
        
        Args:
            persist_directory: Diretório para persistir o banco
            collection_name: Nome da coleção no ChromaDB
            embedding_model: Modelo de embeddings do Ollama
            ollama_base_url: URL do servidor Ollama
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Inicializar embeddings
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_base_url
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
        score_threshold: float = 0.0
    ) -> List[Document]:
        """
        Busca documentos similares à query
        
        Args:
            query: Texto da busca
            k: Número de documentos a retornar
            score_threshold: Threshold mínimo de similaridade
            
        Returns:
            Lista de documentos mais similares
        """
        if self.vectorstore is None:
            raise ValueError("Vector store não inicializado")
        
        # Buscar com scores
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # Filtrar por threshold
        filtered_docs = [
            doc for doc, score in docs_with_scores
            if score >= score_threshold
        ]
        
        return filtered_docs
    
    def delete_collection(self):
        """Remove a coleção do vector store"""
        if self.vectorstore is not None:
            self.vectorstore.delete_collection()
            print(f"🗑️  Coleção '{self.collection_name}' removida")
