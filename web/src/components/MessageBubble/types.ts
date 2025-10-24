export type MessageRole = 'user' | 'assistant';

export interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  timestamp?: Date;
  isStreaming?: boolean;
  showFeedback?: boolean;
  onFeedback?: (feedback: 'sim' | 'não') => void;
  feedbackDisabled?: boolean;
}
