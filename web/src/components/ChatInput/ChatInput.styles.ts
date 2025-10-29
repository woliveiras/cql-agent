import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const Container = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  padding: ${(props) => props.theme?.spacing.lg || '1.5rem'};
  background-color: ${(props) => props.theme?.colors.background.default || '#FFFFFF'};
  border-top: 1px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};
  align-items: flex-end;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.md || '1rem'};
    gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  }
`;

export const InputWrapper = styled.div`
  flex: 1;
  position: relative;
`;

export const StyledTextarea = styled.textarea<{ theme?: Theme }>`
  width: 100%;
  min-height: 120px;
  max-height: 240px;
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  border: 1px solid ${(props) => props.theme?.colors.neutral[300] || '#CBD5E1'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  font-family: inherit;
  line-height: ${(props) => props.theme?.typography.lineHeight.normal || 1.5};
  resize: none;
  outline: none;
  overflow-y: auto;
  transition: border-color ${(props) => props.theme?.transitions.fast || '0.15s'};

  /* Remove scrollbar */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  
  &::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Opera */
  }

  &:focus {
    border-color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  }

  &:disabled {
    background-color: ${(props) => props.theme?.colors.background.hover || '#F1F5F9'};
    cursor: not-allowed;
    color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  }

  &::placeholder {
    color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  }
`;

export const CharCounter = styled.span<{ isLimit: boolean; theme?: Theme }>`
  position: absolute;
  bottom: ${(props) => props.theme?.spacing.xs || "1.25rem"};
  right: ${(props) => props.theme?.spacing.sm || "1.5rem"};
  font-size: ${(props) => props.theme?.typography.fontSize.xs || "0.75rem"};
  color: ${(props) =>
    props.isLimit
      ? props.theme?.colors.error.main || "#DC2626"
      : props.theme?.colors.text.disabled || "#94A3B8"};
  pointer-events: none;
`;

export const SendButton = styled.button<{ theme?: Theme }>`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  background-color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  color: #FFFFFF;
  border: none;
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  font-size: ${(props) => props.theme?.typography.fontSize.xl || '1.25rem'};
  cursor: pointer;
  transition: all ${(props) => props.theme?.transitions.fast || '0.15s'};

  &:hover:not(:disabled) {
    background-color: ${(props) => props.theme?.colors.primary.dark || '#B91C1C'};
    transform: translateY(-1px);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    background-color: ${(props) => props.theme?.colors.neutral[300] || '#CBD5E1'};
    cursor: not-allowed;
    transform: none;
  }

  &:focus-visible {
    outline: 2px solid ${(props) => props.theme?.colors.primary.light || '#EF4444'};
    outline-offset: 2px;
  }
`;

export const Disclaimer = styled.p<{ theme?: Theme }>`
  margin-top: ${(props) => props.theme?.spacing.sm || "0.5rem"};
  margin-bottom: ${(props) => props.theme?.spacing.sm || "0.5rem"};
  padding: 0 ${(props) => props.theme?.spacing.md || "1rem"};
  font-size: ${(props) => props.theme?.typography.fontSize.xs || "0.75rem"};
  color: ${(props) => props.theme?.colors.text.disabled || "#94A3B8"};
  text-align: center;
  line-height: ${(props) =>
    props.theme?.typography.lineHeight.relaxed || 1.625};
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || "640px"}) {
    font-size: 0.625rem;
    padding: 0 ${(props) => props.theme?.spacing.sm || "0.5rem"};
  }
`;
