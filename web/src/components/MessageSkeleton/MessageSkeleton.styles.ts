import { keyframes } from '@emotion/react';
import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

const shimmer = keyframes`
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
`;

export const SkeletonContainer = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: ${(props) => props.theme?.spacing.lg || '1.5rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  }
`;

export const SkeletonAvatar = styled.div<{ theme?: Theme }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(
    to right,
    ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'} 0%,
    ${(props) => props.theme?.colors.neutral[100] || '#F1F5F9'} 20%,
    ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'} 40%,
    ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'} 100%
  );
  background-size: 800px 104px;
  animation: ${shimmer} 1.5s infinite linear;
  flex-shrink: 0;
`;

export const SkeletonContent = styled.div<{ theme?: Theme }>`
  display: flex;
  flex-direction: column;
  gap: ${(props) => props.theme?.spacing.xs || '0.25rem'};
  max-width: 70%;
  flex: 1;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    max-width: 85%;
  }
`;

export const SkeletonBubble = styled.div<{ theme?: Theme }>`
  padding: ${(props) => props.theme?.spacing.md || '1rem'};
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  background-color: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  border: 1px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};
  min-height: 80px;
  display: flex;
  flex-direction: column;
  gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.sm || '0.5rem'} ${(props) => props.theme?.spacing.md || '1rem'};
    min-height: 60px;
  }
`;

export const SkeletonLine = styled.div<{ width?: string; theme?: Theme }>`
  height: 14px;
  width: ${(props) => props.width || '100%'};
  border-radius: ${(props) => props.theme?.borderRadius.sm || '0.25rem'};
  background: linear-gradient(
    to right,
    ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'} 0%,
    ${(props) => props.theme?.colors.neutral[100] || '#F1F5F9'} 20%,
    ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'} 40%,
    ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'} 100%
  );
  background-size: 800px 104px;
  animation: ${shimmer} 1.5s infinite linear;
`;
