import { useEffect, useState } from 'react';
import { Avatar } from '../Avatar';
import {
  AnimatedDots,
  ThinkingBubble,
  ThinkingContainer,
  ThinkingContent,
  ThinkingText,
} from './ThinkingIndicator.styles';

const thinkingMessages = [
  'Consultando',
  'Pensando',
  'Refletindo',
  'Buscando',
  'Analisando',
  'Processando',
];

export function ThinkingIndicator() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % thinkingMessages.length);
    }, 2000); // Troca de mensagem a cada 2 segundos

    return () => clearInterval(interval);
  }, []);

  return (
    <ThinkingContainer>
      <Avatar variant="assistant" size="small" />
      <ThinkingContent>
        <ThinkingBubble>
          <ThinkingText>{thinkingMessages[messageIndex]}</ThinkingText>
          <AnimatedDots />
        </ThinkingBubble>
      </ThinkingContent>
    </ThinkingContainer>
  );
}
