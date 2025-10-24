import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

interface InputWrapperProps {
  fullWidth: boolean;
  theme?: Theme;
}

interface StyledInputProps {
  hasError: boolean;
  theme?: Theme;
}

export const InputWrapper = styled.div<InputWrapperProps>`
  display: flex;
  flex-direction: column;
  gap: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  width: ${(props) => (props.fullWidth ? '100%' : 'auto')};
`;

export const Label = styled.label<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
`;

export const StyledInput = styled.input<StyledInputProps>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  font-family: ${(props) => props.theme?.typography.fontFamily.sans || 'sans-serif'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  background: ${(props) => props.theme?.colors.background.default || '#FFFFFF'};
  border: 2px solid
    ${(props) => {
      if (props.hasError) return props.theme?.colors.error.main || '#DC2626';
      return props.theme?.colors.neutral[300] || '#CBD5E1';
    }};
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  outline: none;
  transition: all ${(props) => props.theme?.transitions.fast || '150ms cubic-bezier(0.4, 0, 0.2, 1)'};
  width: 100%;

  &::placeholder {
    color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  }

  &:hover:not(:disabled) {
    border-color: ${(props) => {
      if (props.hasError) return props.theme?.colors.error.main || '#DC2626';
      return props.theme?.colors.neutral[400] || '#94A3B8';
    }};
  }

  &:focus {
    border-color: ${(props) => {
      if (props.hasError) return props.theme?.colors.error.main || '#DC2626';
      return props.theme?.colors.primary.main || '#DC2626';
    }};
    box-shadow: 0 0 0 3px
      ${(props) => {
        if (props.hasError) return 'rgba(220, 38, 38, 0.1)';
        return 'rgba(220, 38, 38, 0.1)';
      }};
  }

  &:disabled {
    background: ${(props) => props.theme?.colors.neutral[100] || '#F1F5F9'};
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

export const StyledTextarea = styled.textarea<StyledInputProps>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  font-family: ${(props) => props.theme?.typography.fontFamily.sans || 'sans-serif'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  background: ${(props) => props.theme?.colors.background.default || '#FFFFFF'};
  border: 2px solid
    ${(props) => {
      if (props.hasError) return props.theme?.colors.error.main || '#DC2626';
      return props.theme?.colors.neutral[300] || '#CBD5E1';
    }};
  border-radius: ${(props) => props.theme?.borderRadius.md || '0.5rem'};
  outline: none;
  transition: all ${(props) => props.theme?.transitions.fast || '150ms cubic-bezier(0.4, 0, 0.2, 1)'};
  width: 100%;
  resize: vertical;
  min-height: 80px;
  line-height: ${(props) => props.theme?.typography.lineHeight.normal || 1.5};

  &::placeholder {
    color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  }

  &:hover:not(:disabled) {
    border-color: ${(props) => {
      if (props.hasError) return props.theme?.colors.error.main || '#DC2626';
      return props.theme?.colors.neutral[400] || '#94A3B8';
    }};
  }

  &:focus {
    border-color: ${(props) => {
      if (props.hasError) return props.theme?.colors.error.main || '#DC2626';
      return props.theme?.colors.primary.main || '#DC2626';
    }};
    box-shadow: 0 0 0 3px
      ${(props) => {
        if (props.hasError) return 'rgba(220, 38, 38, 0.1)';
        return 'rgba(220, 38, 38, 0.1)';
      }};
  }

  &:disabled {
    background: ${(props) => props.theme?.colors.neutral[100] || '#F1F5F9'};
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

export const HelperText = styled.span<{ isError?: boolean; theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.xs || '0.75rem'};
  color: ${(props) => {
    if (props.isError) return props.theme?.colors.error.main || '#DC2626';
    return props.theme?.colors.text.secondary || '#475569';
  }};
`;
