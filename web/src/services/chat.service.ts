import { api } from './api';
import type { ChatMessageRequest, ChatMessageResponse } from './types';

export const chatService = {
  /**
   * Envia uma mensagem para o chat
   */
  async sendMessage(data: ChatMessageRequest): Promise<ChatMessageResponse> {
    const response = await api.post<ChatMessageResponse>('/api/v1/chat/message', data);
    return response.data;
  },

  /**
   * Reseta uma sessão específica
   */
  async resetSession(sessionId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/api/v1/chat/reset/${sessionId}`);
    return response.data;
  },

  /**
   * Health check da API
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get<{ status: string }>('/health');
    return response.data;
  },
};
