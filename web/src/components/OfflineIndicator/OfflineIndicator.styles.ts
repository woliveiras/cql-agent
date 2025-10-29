import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const Container = styled.div<{ $isOnline: boolean; theme?: Theme }>`
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  background: ${({ $isOnline, theme }) =>
    $isOnline
      ? theme?.colors.success.main || '#16a34a'
      : theme?.colors.warning.main || '#ea580c'};
  color: white;
  padding: ${({ theme }) => theme?.spacing.md || '1rem'};
  border-radius: ${({ theme }) => theme?.borderRadius.md || '0.5rem'};
  box-shadow: ${({ theme }) => theme?.shadows.lg || '0 10px 15px rgba(0, 0, 0, 0.1)'};
  min-width: 200px;
  animation: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @media (max-width: ${({ theme }) => theme?.breakpoints.mobile || '640px'}) {
    top: auto;
    bottom: 5rem;
    right: 0.5rem;
    left: 0.5rem;
    min-width: auto;
  }
`;

export const Status = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

export const Icon = styled.span`
  font-size: 1.25rem;
  animation: pulse 2s ease-in-out infinite;

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
`;

export const Text = styled.span`
  font-weight: 600;
  font-size: 0.875rem;
`;

export const QueueInfo = styled.div`
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 0.75rem;
  opacity: 0.9;
`;
