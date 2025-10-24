import { Avatar } from '../Avatar';
import type { MessageBubbleProps } from './types';
import {
  MessageContainer,
  MessageContent,
  MessageBubbleStyled,
  MessageTime,
  StreamingCursor,
} from './MessageBubble.styles';

export function MessageBubble({
  role,
  content,
  timestamp,
  isStreaming = false,
}: MessageBubbleProps) {

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <MessageContainer role={role}>
      {role === 'assistant' && <Avatar variant="assistant" size="small" />}
      
      <MessageContent>
        <MessageBubbleStyled role={role}>
          {content}
          {isStreaming && <StreamingCursor />}
        </MessageBubbleStyled>
        
        {timestamp && (
          <MessageTime role={role}>
            {formatTime(timestamp)}
          </MessageTime>
        )}
      </MessageContent>

      {role === 'user' && <Avatar variant="user" size="small" />}
    </MessageContainer>
  );
}
