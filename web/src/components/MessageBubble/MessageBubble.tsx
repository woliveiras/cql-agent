import { Avatar } from '../Avatar';
import { FeedbackButtons } from '../FeedbackButtons';
import {
  MessageBubbleStyled,
  MessageContainer,
  MessageContent,
  MessageTime,
  StreamingCursor,
} from './MessageBubble.styles';
import type { MessageBubbleProps } from './types';

export function MessageBubble({
  role,
  content,
  timestamp,
  isStreaming = false,
  showFeedback = false,
  onFeedback,
  feedbackDisabled = false,
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

        {showFeedback && onFeedback && role === 'assistant' && (
          <FeedbackButtons onFeedback={onFeedback} disabled={feedbackDisabled} />
        )}

        {timestamp && <MessageTime role={role}>{formatTime(timestamp)}</MessageTime>}
      </MessageContent>

      {role === 'user' && <Avatar variant="user" size="small" />}
    </MessageContainer>
  );
}
