"""
Agente de IA para Reparos Residenciais
Agente com RAG e busca web que responde perguntas sobre reparos residenciais 
usando modelos locais, base de conhecimento em PDFs e busca na internet
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
import os

from .prompts import (
    BASE_SYSTEM_PROMPT,
    NEW_PROBLEM_PROMPT,
    get_waiting_feedback_prompt,
    get_max_attempts_prompt,
    SUCCESS_MESSAGE,
    get_max_attempts_message,
    AMBIGUOUS_FEEDBACK_MESSAGE
)

from agents.rag import VectorStoreManager, DocumentRetriever
from agents.tools import WebSearchTool


class ConversationState(Enum):
    """Estados da conversação"""
    NEW_PROBLEM = "new_problem"
    WAITING_FEEDBACK = "waiting_feedback"
    RESOLVED = "resolved"
    MAX_ATTEMPTS = "max_attempts"


class RepairAgent:
    """Agente especializado em reparos residenciais com RAG, busca web e acompanhamento de tentativas"""
    
    def __init__(
        self,
        model_name: str = "qwen2.5:3b",
        temperature: float = 0.3,
        num_predict: int = 500,
        base_url: Optional[str] = None,
        max_attempts: int = 3,
        use_rag: bool = True,
        use_web_search: bool = True,
        chroma_db_path: str = "./chroma_db"
    ):
        """
        Inicializa o agente de reparos residenciais
        
        Args:
            model_name: Nome do modelo Ollama a ser usado
            temperature: Controla a criatividade das respostas (0.0 a 1.0)
            num_predict: Limita tokens de resposta
            base_url: URL do servidor Ollama, usa OLLAMA_BASE_URL ou localhost:11434 por padrão
            max_attempts: Número máximo de tentativas antes de sugerir profissional
            use_rag: Se True, usa RAG para buscar documentos relevantes
            use_web_search: Se True, usa busca web quando RAG não encontra informações
            chroma_db_path: Caminho para o banco de dados ChromaDB
        """
        # Usa variável de ambiente se base_url não foi especificado
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            num_predict=num_predict,
            base_url=base_url
        )
        
        self.max_attempts = max_attempts
        self.conversation_history: List = []
        self.current_attempt = 0
        self.state = ConversationState.NEW_PROBLEM
        self.use_rag = use_rag
        self.use_web_search = use_web_search
        
        # Inicializa RAG se disponível
        self.retriever: Optional[DocumentRetriever] = None
        if use_rag and os.path.exists(chroma_db_path):
            try:
                vectorstore_manager = VectorStoreManager(
                    persist_directory=chroma_db_path,
                    ollama_base_url=base_url
                )
                # Carrega o vectorstore existente
                vectorstore = vectorstore_manager.load_vectorstore()
                if vectorstore is None:
                    raise ValueError("Não foi possível carregar o vector store")
                
                self.retriever = DocumentRetriever(
                    vectorstore_manager=vectorstore_manager,
                    k=3,
                    relevance_threshold=0.8
                )
                print("✅ RAG inicializado com sucesso!")
            except Exception as e:
                print(f"⚠️  RAG não disponível: {e}")
                self.retriever = None
        elif use_rag:
            print(f"⚠️  Base de conhecimento não encontrada em {chroma_db_path}")
            print("   Execute: uv run scripts/setup_rag.py")
        
        # Inicializa Web Search se habilitado
        self.web_search: Optional[WebSearchTool] = None
        if use_web_search:
            try:
                self.web_search = WebSearchTool(max_results=3, region="br-pt")
                print("✅ Busca web inicializada com sucesso!")
            except Exception as e:
                print(f"⚠️  Busca web não disponível: {e}")
                self.web_search = None
    
    def _get_system_prompt(
        self, 
        rag_context: Optional[str] = None,
        web_context: Optional[str] = None
    ) -> str:
        """
        Retorna o prompt de sistema apropriado baseado no estado
        
        Args:
            rag_context: Contexto da base de conhecimento (PDFs)
            web_context: Contexto da busca web (internet)
        """
        prompt = BASE_SYSTEM_PROMPT
        
        # Adiciona contexto do RAG se disponível
        if rag_context:
            prompt += f"\n\n## 📚 Informações da Base de Conhecimento (PDFs):\n{rag_context}\n"
            prompt += "\nUse essas informações dos manuais para fornecer uma resposta precisa.\n"
        
        # Adiciona contexto da web se disponível
        if web_context:
            prompt += f"\n\n## 🌐 Informações da Internet:\n{web_context}\n"
            prompt += "\nUse essas informações atualizadas da internet como referência adicional.\n"
        
        if self.state == ConversationState.NEW_PROBLEM:
            prompt += NEW_PROBLEM_PROMPT
        
        elif self.state == ConversationState.WAITING_FEEDBACK:
            if self.current_attempt < self.max_attempts:
                prompt += get_waiting_feedback_prompt(self.current_attempt, self.max_attempts)
            else:
                prompt += get_max_attempts_prompt(self.max_attempts)
        
        return prompt
    
    def _is_positive_feedback(self, message: str) -> bool:
        """Detecta se a mensagem do usuário indica sucesso"""
        message_lower = message.lower().strip()
        
        # Primeiro verificar se há negação na mensagem
        has_negation = any(neg in message_lower for neg in ['não', 'nao', 'nope', 'no'])
        
        # Se há negação, não é positivo
        if has_negation:
            return False
        
        # Respostas diretas positivas
        if message_lower in ['sim', 's', 'yes', 'y', 'ok']:
            return True
        
        # Frases positivas (somente se não houver negação)
        positive_phrases = [
            'funcionou', 'deu certo', 'consegui', 'resolveu', 'resolvido',
            'obrigado', 'valeu', 'sucesso', 'está funcionando', 'perfeito',
            'ótimo', 'excelente'
        ]
        return any(phrase in message_lower for phrase in positive_phrases)
    
    def _is_negative_feedback(self, message: str) -> bool:
        """Detecta se a mensagem do usuário indica falha"""
        message_lower = message.lower().strip()
        
        # Respostas diretas
        if message_lower in ['não', 'nao', 'n', 'no']:
            return True
        
        # Frases negativas
        negative_phrases = [
            'não funcionou', 'não deu', 'não consegui', 'ainda não',
            'continua', 'não resolveu', 'problema persiste', 'não está',
            'ainda está', 'persiste'
        ]
        return any(phrase in message_lower for phrase in negative_phrases)
    
    def chat(self, user_message: str) -> str:
        """
        Processa uma mensagem do usuário e retorna a resposta do agente
        
        Args:
            user_message: Pergunta ou solicitação do usuário
            
        Returns:
            Resposta do agente
        """
        # Se chegou ao máximo de tentativas ou problema resolvido,
        # verificar se é uma nova pergunta ("não" é um feedback)
        if self.state in [ConversationState.MAX_ATTEMPTS, ConversationState.RESOLVED]:
            # Se não é feedback simples (sim/não), considerar como nova pergunta
            if not (self._is_positive_feedback(user_message) or self._is_negative_feedback(user_message)):
                # Reset para novo problema
                self.reset()
                # Continua processamento normal abaixo
        
        # Atualiza o estado baseado no feedback
        if self.state == ConversationState.WAITING_FEEDBACK:
            if self._is_positive_feedback(user_message):
                self.state = ConversationState.RESOLVED
                return SUCCESS_MESSAGE
            
            elif self._is_negative_feedback(user_message):
                self.current_attempt += 1
                if self.current_attempt >= self.max_attempts:
                    self.state = ConversationState.MAX_ATTEMPTS
                # Se ainda há tentativas, marcar que precisa de nova solução
                else:
                    # Estado continua WAITING_FEEDBACK mas precisamos de nova resposta
                    pass
            else:
                # Feedback ambíguo - pede clarificação
                return AMBIGUOUS_FEEDBACK_MESSAGE
        
        # Se chegou ao máximo de tentativas (e não resetou acima)
        if self.state == ConversationState.MAX_ATTEMPTS:
            return get_max_attempts_message(self.max_attempts)
        
        # Mostra mensagem de processamento
        print("🤖 Agente: Processando...", end="\r", flush=True)
        
        # 1. Busca contexto relevante no RAG (apenas para novas perguntas)
        rag_context = None
        web_context = None
        
        if self.retriever and self.state == ConversationState.NEW_PROBLEM:
            try:
                rag_context, has_relevant = self.retriever.retrieve_and_format(user_message)
                if has_relevant:
                    print("\n📚 Encontrei informações!\n")
            except Exception as e:
                print(f"⚠️  Erro ao buscar documentos: {e}")
                rag_context = None
        
        # 2. Se RAG não encontrou nada, busca na web (fallback)
        if not rag_context and self.web_search and self.state == ConversationState.NEW_PROBLEM:
            try:
                print("🌐 Buscando informações na internet...\n")
                web_context = self.web_search.search(user_message)
                if web_context:
                    print("✅ Encontrei informações atualizadas na internet!\n")
                else:
                    print("⚠️  Nenhuma informação relevante encontrada na web.\n")
            except Exception as e:
                print(f"⚠️  Erro na busca web: {e}")
                web_context = None
        
        # Adiciona mensagem do usuário ao histórico
        self.conversation_history.append(HumanMessage(content=user_message))
        
        # Prepara as mensagens para o LLM
        messages = [
            SystemMessage(content=self._get_system_prompt(
                rag_context=rag_context,
                web_context=web_context
            )),
            *self.conversation_history
        ]
        
        # Obtém resposta do modelo
        response = self.llm.invoke(messages)
        
        # Adiciona resposta ao histórico
        self.conversation_history.append(AIMessage(content=response.content))
        
        response_text = response.content
        
        # Atualiza estado para aguardar feedback após primeira resposta
        if self.state == ConversationState.NEW_PROBLEM:
            self.state = ConversationState.WAITING_FEEDBACK
            self.current_attempt = 1
            
            # Garantir que a pergunta de feedback está sempre presente
            feedback_question = "\n\nO problema foi resolvido? Responda com 'sim' ou 'não'."
            
            # Se a resposta não termina com a pergunta, adicionar
            if not response_text.rstrip().endswith(("'sim' ou 'não'.", "'sim' ou 'não'?", "sim' ou 'não'.")):
                response_text += feedback_question
        
        # Para tentativas subsequentes (WAITING_FEEDBACK), também garantir a pergunta
        elif self.state == ConversationState.WAITING_FEEDBACK and self.current_attempt < self.max_attempts:
            feedback_question = "\n\nEssa solução funcionou? Responda com 'sim' ou 'não'."
            
            # Se a resposta não termina com a pergunta, adicionar
            if not response_text.rstrip().endswith(("'sim' ou 'não'.", "'sim' ou 'não'?", "sim' ou 'não'.")):
                response_text += feedback_question
        
        return response_text
    
    def reset(self):
        """Reinicia o agente para um novo problema"""
        self.conversation_history = []
        self.current_attempt = 0
        self.state = ConversationState.NEW_PROBLEM


class RepairQuery(BaseModel):
    """Modelo para validação de consultas de reparo"""
    question: str = Field(..., description="Pergunta sobre reparo residencial")
    urgency: Optional[str] = Field(None, description="Nível de urgência: baixa, média, alta")
    location: Optional[str] = Field(None, description="Local do problema (ex: cozinha, banheiro)")


def main():
    """Função principal para interação via linha de comando"""
    print("=" * 60)
    print("🔧 CQL AI Agent - Assistente de Reparos Residenciais")
    print("=" * 60)
    print("\nInicializando o agente...")
    
    try:
        agent = RepairAgent(max_attempts=3, use_rag=True, use_web_search=True)
        print("\n✅ Agente inicializado com sucesso!")
        
        # Mostra status do RAG
        if agent.retriever:
            print("📚 RAG ativo - usando base de conhecimento em PDFs")
        else:
            print("⚠️  RAG desativado")
        
        # Mostra status da busca web
        if agent.web_search:
            print("🌐 Busca web ativa - usando DuckDuckGo como fallback")
        else:
            print("⚠️  Busca web desativada")
        
        print("\n💡 O agente busca primeiro nos PDFs, depois na internet se necessário")
        print("💡 Tentará ajudá-lo até 3 vezes antes de sugerir um profissional")
        print("\n📝 Comandos: 'sair' para encerrar | 'novo' para um novo problema\n")
        
        while True:
            user_input = input("\n👤 Você: ").strip()
            
            if not user_input:
                continue
            
            # Comandos especiais
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Até logo! Boa sorte com seus reparos!")
                break
            
            if user_input.lower() in ['novo', 'new', 'reiniciar', 'reset']:
                agent.reset()
                print("\n🔄 Agente reiniciado! Pronto para um novo problema.")
                continue
            
            # Processar mensagem
            response = agent.chat(user_input)
            print("🤖 Agente:", response)
            
            # Se o problema foi resolvido, oferecer reiniciar
            if agent.state == ConversationState.RESOLVED or agent.state == ConversationState.MAX_ATTEMPTS:
                print("\n💬 Digite 'novo' para relatar outro problema ou 'sair' para encerrar.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n⚠️  Certifique-se de que o Ollama está rodando:")
        print("   docker-compose up -d")
        print("   docker exec -it ollama ollama pull qwen2.5:3b")
        print("   docker exec -it ollama ollama pull nomic-embed-text")


if __name__ == "__main__":
    main()
