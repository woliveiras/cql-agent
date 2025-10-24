import { useMutation } from '@tanstack/react-query';
import { chatService } from '../services';
import type { ChatMessageRequest, ChatMessageResponse } from '../services';

export function useSendMessage() {
  return useMutation<ChatMessageResponse, Error, ChatMessageRequest>({
    mutationFn: (data) => chatService.sendMessage(data),
  });
}
