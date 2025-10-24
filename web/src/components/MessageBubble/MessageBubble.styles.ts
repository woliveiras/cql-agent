import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';
import type { MessageRole } from './types';

export const MessageContainer = styled.div<{ role: MessageRole; theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  align-items: flex-start;
  justify-content: ${(props) => (props.role === 'user' ? 'flex-end' : 'flex-start')};
  margin-bottom: ${(props) => props.theme?.spacing.lg || '1.5rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  }
`;

export const MessageContent = styled.div<{ theme?: Theme }>`
  display: flex;
  flex-direction: column;
  gap: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  max-width: 70%;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    max-width: 85%;
  }
`;

export const MessageBubbleStyled = styled.div<{ role: MessageRole; theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  background-color: ${(props) =>
    props.role === 'user'
      ? props.theme?.colors.primary.main || '#DC2626'
      : props.theme?.colors.background.paper || '#F8FAFC'};
  color: ${(props) =>
    props.role === 'user'
      ? '#FFFFFF'
      : props.theme?.colors.text.primary || '#0F172A'};
  line-height: ${(props) => props.theme?.typography.lineHeight.relaxed || 1.625};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  word-wrap: break-word;
  white-space: pre-wrap;

  ${(props) =>
    props.role === 'assistant' &&
    `
    border: 1px solid ${props.theme?.colors.neutral[200] || '#E2E8F0'};
  `}

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.sm || '0.5rem'} ${(props) => props.theme?.spacing.md || '1rem'};
  }
`;

export const MessageTime = styled.span<{ role: MessageRole; theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.xs || '0.75rem'};
  color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  align-self: ${(props) => (props.role === 'user' ? 'flex-end' : 'flex-start')};
`;

export const StreamingCursor = styled.span<{ theme?: Theme }>`
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: currentColor;
  margin-left: 2px;
  animation: blink 1s infinite;

  @keyframes blink {
    0%,
    49% {
      opacity: 1;
    }
    50%,
    100% {
      opacity: 0;
    }
  }
`;
