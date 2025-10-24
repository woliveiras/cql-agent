import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const ButtonContainer = styled.div`
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
`;

interface FeedbackButtonProps {
  variant: 'yes' | 'no';
  theme?: Theme;
}

export const FeedbackButton = styled.button<FeedbackButtonProps>`
  padding: 0.625rem 1.25rem;
  border-radius: ${({ theme }) => (theme as Theme).borderRadius.md};
  border: 2px solid ${({ theme, variant }) => 
    variant === 'yes' ? (theme as Theme).colors.success.main : (theme as Theme).colors.error.main};
  background-color: ${({ theme }) => (theme as Theme).colors.background.paper};
  color: ${({ theme, variant }) => 
    variant === 'yes' ? (theme as Theme).colors.success.main : (theme as Theme).colors.error.main};
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;

  &:hover:not(:disabled) {
    background-color: ${({ theme, variant }) => 
      variant === 'yes' ? (theme as Theme).colors.success.main : (theme as Theme).colors.error.main};
    color: ${({ theme }) => (theme as Theme).colors.background.paper};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px ${({ variant }) => 
      variant === 'yes' 
        ? 'rgba(22, 163, 74, 0.3)' 
        : 'rgba(220, 38, 38, 0.3)'};
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;
