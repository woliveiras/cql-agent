"""
Web Search Tool - Busca informações na internet usando DuckDuckGo
"""

from typing import List, Dict, Optional
from duckduckgo_search import DDGS


class WebSearchTool:
    """Ferramenta de busca web usando DuckDuckGo"""
    
    def __init__(
        self,
        max_results: int = 3,
        region: str = "br-pt",
        safesearch: str = "moderate"
    ):
        """
        Inicializa a ferramenta de busca web
        
        Args:
            max_results: Número máximo de resultados a retornar
            region: Região da busca (br-pt para Brasil/Português)
            safesearch: Nível de filtro (on, moderate, off)
        """
        self.max_results = max_results
        self.region = region
        self.safesearch = safesearch
    
    def search(self, query: str) -> Optional[str]:
        """
        Realiza busca web e retorna resultados formatados
        
        Args:
            query: Termo de busca
            
        Returns:
            Resultados formatados ou None se houver erro
        """
        try:
            # Adiciona contexto de reparos domésticos à query
            enhanced_query = f"{query} reparos domésticos manutenção"
            
            # Busca usando DuckDuckGo
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    enhanced_query,
                    region=self.region,
                    safesearch=self.safesearch,
                    max_results=self.max_results
                ))
            
            if not results:
                return None
            
            # Formata resultados
            return self._format_results(results)
            
        except Exception as e:
            print(f"⚠️  Erro na busca web: {e}")
            return None
    
    def _format_results(self, results: List[Dict]) -> str:
        """
        Formata resultados da busca para inclusão no prompt
        
        Args:
            results: Lista de resultados do DuckDuckGo
            
        Returns:
            Resultados formatados
        """
        formatted_parts = []
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Sem título')
            body = result.get('body', 'Sem descrição')
            url = result.get('href', '')
            
            formatted_parts.append(
                f"[Resultado {i}] {title}\n{body}\nFonte: {url}"
            )
        
        return "\n\n".join(formatted_parts)
    
    def search_with_fallback(
        self,
        query: str,
        alternative_queries: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Tenta buscar com query original e fallback para alternativas
        
        Args:
            query: Query principal
            alternative_queries: Queries alternativas caso primeira falhe
            
        Returns:
            Primeiros resultados encontrados ou None
        """
        # Tenta query principal
        results = self.search(query)
        if results:
            return results
        
        # Tenta queries alternativas
        if alternative_queries:
            for alt_query in alternative_queries:
                results = self.search(alt_query)
                if results:
                    return results
        
        return None


def format_search_context(web_results: Optional[str]) -> str:
    """
    Formata contexto de busca web para o prompt
    
    Args:
        web_results: Resultados da busca web
        
    Returns:
        Contexto formatado
    """
    if not web_results:
        return ""
    
    return f"\n\n## 🌐 Informações da Internet:\n{web_results}\n"
