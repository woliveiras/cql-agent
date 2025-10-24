import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';
import type { ButtonVariant, ButtonSize } from './types';

interface StyledButtonProps {
  variant: ButtonVariant;
  size: ButtonSize;
  fullWidth: boolean;
  theme?: Theme;
}

const getVariantStyles = (variant: ButtonVariant, theme: Theme) => {
  switch (variant) {
    case 'primary':
      return `
        background: ${theme.colors.primary.main};
        color: ${theme.colors.primary.contrast};
        border: 2px solid ${theme.colors.primary.main};

        &:hover:not(:disabled) {
          background: ${theme.colors.primary.dark};
          border-color: ${theme.colors.primary.dark};
        }

        &:active:not(:disabled) {
          background: ${theme.colors.primary.dark};
          transform: translateY(1px);
        }
      `;
    case 'secondary':
      return `
        background: ${theme.colors.secondary.main};
        color: ${theme.colors.secondary.contrast};
        border: 2px solid ${theme.colors.secondary.main};

        &:hover:not(:disabled) {
          background: ${theme.colors.secondary.dark};
          border-color: ${theme.colors.secondary.dark};
        }

        &:active:not(:disabled) {
          background: ${theme.colors.secondary.dark};
          transform: translateY(1px);
        }
      `;
    case 'ghost':
      return `
        background: transparent;
        color: ${theme.colors.text.primary};
        border: 2px solid ${theme.colors.neutral[300]};

        &:hover:not(:disabled) {
          background: ${theme.colors.background.hover};
          border-color: ${theme.colors.neutral[400]};
        }

        &:active:not(:disabled) {
          background: ${theme.colors.neutral[200]};
          transform: translateY(1px);
        }
      `;
    default:
      return '';
  }
};

const getSizeStyles = (size: ButtonSize, theme: Theme) => {
  switch (size) {
    case 'small':
      return `
        padding: ${theme.spacing.sm} ${theme.spacing.md};
        font-size: ${theme.typography.fontSize.sm};
        height: 32px;
      `;
    case 'medium':
      return `
        padding: ${theme.spacing.md} ${theme.spacing.lg};
        font-size: ${theme.typography.fontSize.base};
        height: 40px;
      `;
    case 'large':
      return `
        padding: ${theme.spacing.md} ${theme.spacing.xl};
        font-size: ${theme.typography.fontSize.lg};
        height: 48px;
      `;
    default:
      return '';
  }
};

export const StyledButton = styled.button<StyledButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  font-family: ${(props) => props.theme?.typography.fontFamily.sans || 'sans-serif'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  cursor: pointer;
  transition: all ${(props) => props.theme?.transitions.fast || '150ms cubic-bezier(0.4, 0, 0.2, 1)'};
  outline: none;
  user-select: none;
  width: ${(props) => (props.fullWidth ? '100%' : 'auto')};

  ${(props) => props.theme && getVariantStyles(props.variant, props.theme)}
  ${(props) => props.theme && getSizeStyles(props.size, props.theme)}

  &:focus-visible {
    outline: 2px solid ${(props) => props.theme?.colors.primary.main || '#DC2626'};
    outline-offset: 2px;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export const LoadingSpinner = styled.span<{ theme?: Theme }>`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;
