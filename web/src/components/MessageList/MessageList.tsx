import { useEffect, useRef } from 'react';
import { MessageBubble } from '../MessageBubble';
import { ThinkingIndicator } from '../ThinkingIndicator';
import {
  Container,
  EmptyStateContainer,
  MessagesWrapper,
} from './MessageList.styles';
import type { MessageListProps } from './types';

export function MessageList({
  messages,
  isLoading = false,
  emptyState,
  onFeedback,
  feedbackDisabled = false,
}: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

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
            showFeedback={message.needsFeedback}
            onFeedback={onFeedback ? (feedback) => onFeedback(message.id, feedback) : undefined}
            feedbackDisabled={feedbackDisabled}
          />
        ))}

        {isLoading && <ThinkingIndicator />}

        <div ref={messagesEndRef} />
      </MessagesWrapper>
    </Container>
  );
}
