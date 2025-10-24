import { useEffect, useRef } from 'react';
import { MessageBubble } from '../MessageBubble';
import { Avatar } from '../Avatar';
import { LoadingIndicator } from '../LoadingIndicator';
import type { MessageListProps } from './types';
import {
  Container,
  MessagesWrapper,
  EmptyStateContainer,
  LoadingContainer,
} from './MessageList.styles';

export function MessageList({
  messages,
  isLoading = false,
  emptyState,
}: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <Container ref={containerRef}>
        <EmptyStateContainer>
          {emptyState || (
            <>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>💬</div>
              <p>Nenhuma mensagem ainda.</p>
              <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                Comece uma conversa digitando abaixo.
              </p>
            </>
          )}
        </EmptyStateContainer>
      </Container>
    );
  }

  return (
    <Container ref={containerRef}>
      <MessagesWrapper>
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
            isStreaming={message.isStreaming}
          />
        ))}

        {isLoading && (
          <LoadingContainer>
            <Avatar variant="assistant" size="small" />
            <LoadingIndicator />
          </LoadingContainer>
        )}

        <div ref={messagesEndRef} />
      </MessagesWrapper>
    </Container>
  );
}
