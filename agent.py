"""
Agente de IA para Reparos Residenciais
Agente básico que responde perguntas sobre reparos residenciais usando modelos locais
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

from prompts import (
    BASE_SYSTEM_PROMPT,
    NEW_PROBLEM_PROMPT,
    get_waiting_feedback_prompt,
    get_max_attempts_prompt,
    SUCCESS_MESSAGE,
    get_max_attempts_message,
    AMBIGUOUS_FEEDBACK_MESSAGE
)


class ConversationState(Enum):
    """Estados da conversação"""
    NEW_PROBLEM = "new_problem"
    WAITING_FEEDBACK = "waiting_feedback"
    RESOLVED = "resolved"
    MAX_ATTEMPTS = "max_attempts"


class RepairAgent:
    """Agente especializado em reparos residenciais com acompanhamento de tentativas"""
    
    def __init__(
        self,
        model_name: str = "qwen2.5:3b",
        temperature: float = 0.3,
        num_predict: int = 500,
        base_url: str = "http://localhost:11434",
        max_attempts: int = 3
    ):
        """
        Inicializa o agente de reparos residenciais
        
        Args:
            model_name: Nome do modelo Ollama a ser usado
            temperature: Controla a criatividade das respostas (0.0 a 1.0)
            num_predict: Limita tokens de resposta
            base_url: URL do servidor Ollama, localhost:11434 por padrão
            max_attempts: Número máximo de tentativas antes de sugerir profissional
        """
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
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema apropriado baseado no estado"""
        prompt = BASE_SYSTEM_PROMPT
        
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
        
        # Respostas diretas
        if message_lower in ['sim', 's', 'yes', 'y']:
            return True
        
        # Frases positivas
        positive_phrases = [
            'funcionou', 'deu certo', 'consegui', 'resolveu', 'resolvido',
            'obrigado', 'valeu', 'sucesso', 'está funcionando'
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
        # Atualiza o estado baseado no feedback
        if self.state == ConversationState.WAITING_FEEDBACK:
            if self._is_positive_feedback(user_message):
                self.state = ConversationState.RESOLVED
                return SUCCESS_MESSAGE
            
            elif self._is_negative_feedback(user_message):
                self.current_attempt += 1
                if self.current_attempt >= self.max_attempts:
                    self.state = ConversationState.MAX_ATTEMPTS
            else:
                # Feedback ambíguo - pede clarificação
                return AMBIGUOUS_FEEDBACK_MESSAGE
        
        # Se chegou ao máximo de tentativas
        if self.state == ConversationState.MAX_ATTEMPTS:
            return get_max_attempts_message(self.max_attempts)
        
        # Adiciona mensagem do usuário ao histórico
        self.conversation_history.append(HumanMessage(content=user_message))
        
        # Prepara as mensagens para o LLM
        messages = [
            SystemMessage(content=self._get_system_prompt()),
            *self.conversation_history
        ]
        
        # Obtém resposta do modelo
        response = self.llm.invoke(messages)
        
        # Adiciona resposta ao histórico
        self.conversation_history.append(AIMessage(content=response.content))
        
        # Atualiza estado para aguardar feedback após primeira resposta
        if self.state == ConversationState.NEW_PROBLEM:
            self.state = ConversationState.WAITING_FEEDBACK
            self.current_attempt = 1
        
        return response.content
    
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
        agent = RepairAgent(max_attempts=3)
        print("\n\n✅ Agente inicializado com sucesso!")
        print("\n💡 Dica: O agente tentará ajudá-lo até 3 vezes antes de sugerir um profissional")
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
            print("\n🤖 Agente: Processando...", end="\r")
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


if __name__ == "__main__":
    main()
