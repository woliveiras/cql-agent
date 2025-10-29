import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const Container = styled.div<{ theme?: Theme }>`
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: ${({ theme }) => theme?.colors.background.paper || '#f8fafc'};
  border-top: 2px solid ${({ theme }) => theme?.colors.primary.main || '#dc2626'};
  padding: ${({ theme }) => theme?.spacing.lg || '1.5rem'};
  box-shadow: ${({ theme }) => theme?.shadows.xl || '0 -4px 20px rgba(0, 0, 0, 0.1)'};
  z-index: 999;
  animation: slideUp 0.3s ease-out;

  @keyframes slideUp {
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @media (max-width: ${({ theme }) => theme?.breakpoints.mobile || '640px'}) {
    padding: ${({ theme }) => theme?.spacing.md || '1rem'};
  }
`;

export const Content = styled.div<{ theme?: Theme }>`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme?.spacing.md || '1rem'};
  margin-bottom: ${({ theme }) => theme?.spacing.md || '1rem'};
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: ${({ theme }) => theme?.breakpoints.mobile || '640px'}) {
    gap: ${({ theme }) => theme?.spacing.sm || '0.5rem'};
  }
`;

export const Icon = styled.div<{ theme?: Theme }>`
  font-size: 2.5rem;
  flex-shrink: 0;

  @media (max-width: ${({ theme }) => theme?.breakpoints.mobile || '640px'}) {
    font-size: 2rem;
  }
`;

export const Title = styled.h3<{ theme?: Theme }>`
  font-size: ${({ theme }) => theme?.typography.fontSize.lg || '1.125rem'};
  font-weight: ${({ theme }) => theme?.typography.fontWeight.semibold || 600};
  color: ${({ theme }) => theme?.colors.text.primary || '#0f172a'};
  margin: 0 0 0.25rem 0;
`;

export const Description = styled.p<{ theme?: Theme }>`
  font-size: ${({ theme }) => theme?.typography.fontSize.sm || '0.875rem'};
  color: ${({ theme }) => theme?.colors.text.secondary || '#475569'};
  margin: 0;
`;

export const ButtonGroup = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${({ theme }) => theme?.spacing.md || '1rem'};
  max-width: 900px;
  margin: 0 auto;

  @media (max-width: ${({ theme }) => theme?.breakpoints.mobile || '640px'}) {
    flex-direction: column;
    gap: ${({ theme }) => theme?.spacing.sm || '0.5rem'};
  }
`;

const Button = styled.button<{ theme?: Theme }>`
  flex: 1;
  padding: ${({ theme }) => theme?.spacing.md || '1rem'};
  font-size: ${({ theme }) => theme?.typography.fontSize.base || '1rem'};
  font-weight: ${({ theme }) => theme?.typography.fontWeight.semibold || 600};
  border-radius: ${({ theme }) => theme?.borderRadius.md || '0.5rem'};
  border: none;
  cursor: pointer;
  transition: ${({ theme }) => theme?.transitions.fast || '150ms cubic-bezier(0.4, 0, 0.2, 1)'};

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:not(:disabled):hover {
    transform: translateY(-2px);
  }

  &:not(:disabled):active {
    transform: translateY(0);
  }
`;

export const InstallButton = styled(Button)<{ theme?: Theme }>`
  background: ${({ theme }) => theme?.colors.primary.main || '#dc2626'};
  color: ${({ theme }) => theme?.colors.primary.contrast || '#ffffff'};

  &:not(:disabled):hover {
    background: ${({ theme }) => theme?.colors.primary.dark || '#b91c1c'};
  }
`;

export const DismissButton = styled(Button)<{ theme?: Theme }>`
  background: transparent;
  color: ${({ theme }) => theme?.colors.text.secondary || '#475569'};
  border: 1px solid ${({ theme }) => theme?.colors.neutral[200] || '#e2e8f0'};

  &:not(:disabled):hover {
    background: ${({ theme }) => theme?.colors.background.hover || '#f1f5f9'};
    border-color: ${({ theme }) => theme?.colors.neutral[300] || '#cbd5e1'};
  }
`;
