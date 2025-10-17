"""
PDF Loader - Carrega e processa PDFs para o sistema RAG
"""

from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class PDFLoader:
    """Carrega e processa arquivos PDF"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        Inicializa o loader de PDFs
        
        Args:
            chunk_size: Tamanho de cada chunk em caracteres
            chunk_overlap: Sobreposição entre chunks
            separators: Lista de separadores para dividir o texto
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len
        )
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Carrega um único arquivo PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Lista de documentos extraídos do PDF
        """
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Adicionar metadados
        for doc in documents:
            doc.metadata['source_file'] = Path(pdf_path).name
        
        return documents
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """
        Carrega todos os PDFs de um diretório
        
        Args:
            directory_path: Caminho para o diretório com PDFs
            
        Returns:
            Lista de todos os documentos carregados
        """
        pdf_dir = Path(directory_path)
        all_documents = []
        
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory_path}")
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"Nenhum PDF encontrado em: {directory_path}")
        
        print(f"📄 Encontrados {len(pdf_files)} PDFs")
        
        for pdf_file in pdf_files:
            print(f"   Carregando: {pdf_file.name}")
            try:
                documents = self.load_pdf(str(pdf_file))
                all_documents.extend(documents)
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar {pdf_file.name}: {e}")
        
        return all_documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide documentos em chunks menores
        
        Args:
            documents: Lista de documentos a dividir
            
        Returns:
            Lista de documentos divididos em chunks
        """
        chunks = self.text_splitter.split_documents(documents)
        print(f"📝 {len(documents)} documentos divididos em {len(chunks)} chunks")
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Document]:
        """
        Processa todos os PDFs de um diretório (load + split)
        
        Args:
            directory_path: Caminho para o diretório
            
        Returns:
            Lista de chunks prontos para embedding
        """
        documents = self.load_directory(directory_path)
        chunks = self.split_documents(documents)
        return chunks
