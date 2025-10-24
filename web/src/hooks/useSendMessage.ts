import { useMutation } from '@tanstack/react-query';
import type { ApiError, ChatMessageRequest, ChatMessageResponse } from '../services';
import { chatService } from '../services';

export function useSendMessage() {
  return useMutation<ChatMessageResponse, ApiError, ChatMessageRequest>({
    mutationFn: (data) => chatService.sendMessage(data),
  });
}
