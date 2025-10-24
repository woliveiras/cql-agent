import { useMutation } from '@tanstack/react-query';
import { chatService } from '../services';
import type { ChatMessageRequest, ChatMessageResponse, ApiError } from '../services';

export function useSendMessage() {
  return useMutation<ChatMessageResponse, ApiError, ChatMessageRequest>({
    mutationFn: (data) => chatService.sendMessage(data),
  });
}
