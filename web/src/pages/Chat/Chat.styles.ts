import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
`;

export const ChatContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

export const ErrorBanner = styled.div<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  background-color: ${(props) => props.theme?.colors.error.light || '#EF4444'};
  color: #FFFFFF;
  text-align: center;
  font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
`;

export const CloseButton = styled.button<{ theme?: Theme }>`
  background: none;
  border: none;
  color: #FFFFFF;
  cursor: pointer;
  padding: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  font-size: 1.25rem;
  line-height: 1;
  opacity: 0.8;
  transition: opacity ${(props) => props.theme?.transitions.fast || '0.15s'};

  &:hover {
    opacity: 1;
  }
`;
