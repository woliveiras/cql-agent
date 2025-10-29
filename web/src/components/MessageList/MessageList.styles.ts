import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const Container = styled.div<{ theme?: Theme }>`
  flex: 1;
  overflow-y: auto;
  padding: ${(props) => props.theme?.spacing.xl || '2rem'};
  display: flex;
  flex-direction: column;

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${(props) => props.theme?.colors.background.paper || '#F8FAFC'};
  }

  &::-webkit-scrollbar-thumb {
    background: ${(props) => props.theme?.colors.neutral[300] || '#CBD5E1'};
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: ${(props) => props.theme?.colors.neutral[400] || '#94A3B8'};
  }

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.md || '1rem'};
  }
`;

export const MessagesWrapper = styled.div`
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
`;

export const EmptyStateContainer = styled.div<{ theme?: Theme }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: ${(props) => props.theme?.spacing['4xl'] || '6rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  text-align: center;
  padding-bottom: ${(props) => props.theme?.spacing['2xl'] || '3rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding-top: ${(props) => props.theme?.spacing['2xl'] || '3rem'};
  }
`;
