import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { sessionManager } from '../../lib/sessionManager';
import type { ChatStore } from './types';

export const useChatStore = create<ChatStore>()(
  devtools(
    (set) => ({
      // State - Inicializa com sessionId do localStorage ou cria novo
      messages: [],
      sessionId: sessionManager.getOrCreateSessionId(),
      isLoading: false,
      error: null,
      waitingFeedback: false,

      // Actions
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      setMessages: (messages) => set({ messages }),

      updateMessage: (id, updates) =>
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
          ),
        })),

      setSessionId: (sessionId) => {
        sessionManager.setSessionId(sessionId);
        set({ sessionId });
      },

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      clearChat: () =>
        set({
          messages: [],
          error: null,
        }),

      clearError: () => set({ error: null }),

      setWaitingFeedback: (waiting) => set({ waitingFeedback: waiting }),

      startNewConversation: () => {
        const newSessionId = sessionManager.createNewSession();
        set({
          messages: [],
          sessionId: newSessionId,
          error: null,
          isLoading: false,
          waitingFeedback: false,
        });
      },
    }),
    { name: 'chat-store' }
  )
);
