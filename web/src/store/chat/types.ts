import type { Message } from '../../components/MessageList';

export interface ChatState {
  messages: Message[];
  sessionId: string;
  isLoading: boolean;
  error: string | null;
  waitingFeedback: boolean;
}

export interface ChatActions {
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  setSessionId: (id: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
  clearError: () => void;
  startNewConversation: () => void;
  setWaitingFeedback: (waiting: boolean) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
}

export type ChatStore = ChatState & ChatActions;
