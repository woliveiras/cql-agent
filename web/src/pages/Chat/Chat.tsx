import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { MessageList, type Message } from '../../components/MessageList';
import { ChatInput } from '../../components/ChatInput';
import { useChatStore } from '../../store/chat';
import { useSendMessage } from '../../hooks/useSendMessage';
import type { ApiError } from '../../services';
import {
  ChatContainer,
  ChatContent,
  ErrorBanner,
  CloseButton,
} from './Chat.styles';

export function Chat() {
  const location = useLocation();
  const initialMessage = location.state?.initialMessage as string | undefined;
  const hasInitialized = useRef(false);
  
  const [inputValue, setInputValue] = useState('');
  
  const {
    messages,
    sessionId,
    isLoading,
    error,
    addMessage,
    setLoading,
    setError,
    clearError,
  } = useChatStore();

  const sendMessageMutation = useSendMessage();

  // Enviar mensagem inicial se vier da página Welcome
  useEffect(() => {
    if (initialMessage && messages.length === 0 && !hasInitialized.current) {
      hasInitialized.current = true;
      handleSend(initialMessage);
    }
  }, [initialMessage, messages.length]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || inputValue.trim();
    if (!textToSend) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setInputValue('');
    setLoading(true);
    clearError();

    try {
      const response = await sendMessageMutation.mutateAsync({
        message: textToSend,
        session_id: sessionId, // Sempre envia o sessionId
        use_rag: true,
        use_web_search: true,
      });

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      addMessage(assistantMessage);
    } catch (err) {
      const apiError = err as ApiError;
      setError(
        apiError.detail || 'Não foi possível enviar sua mensagem. Por favor, tente novamente.'
      );
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => {
    clearError();
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
