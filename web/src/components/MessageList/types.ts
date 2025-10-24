import type { ReactNode } from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  needsFeedback?: boolean;
}

export interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  emptyState?: ReactNode;
  onFeedback?: (messageId: string, feedback: 'sim' | 'não') => void;
  feedbackDisabled?: boolean;
}
