import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const Container = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  align-items: center;
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
`;

export const Dot = styled.div<{ delay: number; theme?: Theme }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  animation: bounce 1.4s infinite ease-in-out;
  animation-delay: ${(props) => props.delay}s;

  @keyframes bounce {
    0%,
    80%,
    100% {
      transform: scale(0);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;
