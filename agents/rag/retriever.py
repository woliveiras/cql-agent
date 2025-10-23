"""
Document Retriever - Recupera documentos relevantes do vector store
"""

from typing import List, Tuple
from langchain_core.documents import Document
from .vectorstore import VectorStoreManager


class DocumentRetriever:
    """Recupera documentos relevantes para queries"""

    def __init__(
        self,
        vectorstore_manager: VectorStoreManager,
        k: int = 3,
        relevance_threshold: float = 0.8
    ):
        """
        Inicializa o retriever

        Args:
            vectorstore_manager: Gerenciador do vector store
            k: Número de documentos a recuperar
            relevance_threshold: Threshold máximo de distância (menor = mais similar)
                               Valores recomendados:
                               - 0.5: Muito similar (restritivo)
                               - 0.8: Similar (balanceado)
                               - 1.0: Relativamente similar (permissivo)
        """
        self.vectorstore_manager = vectorstore_manager
        self.k = k
        self.relevance_threshold = relevance_threshold

    def retrieve(self, query: str) -> Tuple[List[Document], bool]:
        """
        Recupera documentos relevantes para a query

        Args:
            query: Pergunta do usuário

        Returns:
            Tupla (documentos, encontrou_relevantes)
        """
        try:
            docs = self.vectorstore_manager.similarity_search(
                query=query,
                k=self.k,
                score_threshold=self.relevance_threshold
            )

            has_relevant = len(docs) > 0
            return docs, has_relevant

        except Exception as e:
            print(f"⚠️  Erro ao buscar documentos: {e}")
            return [], False

    def format_context(self, documents: List[Document]) -> str:
        """
        Formata documentos em um contexto para o prompt

        Args:
            documents: Lista de documentos recuperados

        Returns:
            Contexto formatado
        """
        if not documents:
            return ""

        context_parts = []

        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source_file', 'desconhecido')
            page = doc.metadata.get('page', 'N/A')
            content = doc.page_content.strip()

            context_parts.append(
                f"[Documento {i} - {source} (página {page})]\n{content}"
            )

        return "\n\n---\n\n".join(context_parts)

    def retrieve_and_format(self, query: str) -> Tuple[str, bool]:
        """
        Recupera documentos e formata em contexto

        Args:
            query: Pergunta do usuário

        Returns:
            Tupla (contexto_formatado, encontrou_relevantes)
        """
        docs, has_relevant = self.retrieve(query)

        if has_relevant:
            context = self.format_context(docs)
            return context, True

        return "", False
