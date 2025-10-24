import type { ReactNode } from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  emptyState?: ReactNode;
}
