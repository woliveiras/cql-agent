import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import type { Theme } from '../../styles/types';

const dots = keyframes`
  0%, 20% {
    content: '';
  }
  40% {
    content: '.';
  }
  60% {
    content: '..';
  }
  80%, 100% {
    content: '...';
  }
`;

export const ThinkingContainer = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: ${(props) => props.theme?.spacing.lg || '1.5rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  }
`;

export const ThinkingContent = styled.div<{ theme?: Theme }>`
  display: flex;
  flex-direction: column;
  gap: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  max-width: 70%;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    max-width: 85%;
  }
`;

export const ThinkingBubble = styled.div<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  background-color: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  border: 1px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 2px;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.sm || '0.5rem'} ${(props) => props.theme?.spacing.md || '1rem'};
  }
`;

export const ThinkingText = styled.span`
  display: inline-block;
`;

export const AnimatedDots = styled.span`
  display: inline-block;
  min-width: 1.5em;
  text-align: left;

  &::after {
    content: '';
    animation: ${dots} 1.5s infinite;
  }
`;
