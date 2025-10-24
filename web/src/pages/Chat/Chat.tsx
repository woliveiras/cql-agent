import { useState } from 'react';
import { MessageList, type Message } from '../../components/MessageList';
import { ChatInput } from '../../components/ChatInput';
import {
  ChatContainer,
  ChatContent,
  ErrorBanner,
  CloseButton,
} from './Chat.styles';

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Integrar com a API real
      // Simulação de resposta
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content:
          'Olá! Sou o Vicente, seu assistente de reparos. Esta é uma resposta simulada. Em breve vou me conectar com a API real para ajudar você com seus problemas domésticos! 🔧',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(
        'Não foi possível enviar sua mensagem. Por favor, tente novamente.'
      );
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  return (
    <ChatContainer>
      {error && (
        <ErrorBanner>
          <span>⚠️ {error}</span>
          <CloseButton onClick={handleCloseError}>×</CloseButton>
        </ErrorBanner>
      )}

      <ChatContent>
        <MessageList
          messages={messages}
          isLoading={isLoading}
          emptyState={
            <>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔧</div>
              <h2>Olá! Sou o Vicente</h2>
              <p style={{ marginTop: '0.5rem' }}>
                Seu assistente de IA para reparos residenciais
              </p>
              <p
                style={{
                  fontSize: '0.875rem',
                  marginTop: '1rem',
                  opacity: 0.7,
                }}
              >
                Me conte sobre seu problema e vou ajudar você a resolvê-lo!
              </p>
            </>
          }
        />

        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          disabled={isLoading}
          placeholder="Descreva seu problema de reparo..."
          maxLength={500}
        />
      </ChatContent>
    </ChatContainer>
  );
}

export default Chat;
