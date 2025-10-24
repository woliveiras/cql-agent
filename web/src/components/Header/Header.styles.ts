import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const HeaderContainer = styled.header<{ theme?: Theme }>`
  position: sticky;
  top: 0;
  z-index: 100;
  background: ${(props) => props.theme?.colors.background.default || '#FFFFFF'};
  border-bottom: 1px solid ${(props) => props.theme?.colors.neutral[200] || '#E2E8F0'};
  padding: ${(props) => props.theme?.spacing.md || '1rem'} ${(props) => props.theme?.spacing.lg || '1.5rem'};
`;

export const HeaderContent = styled.div<{ theme?: Theme }>`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: ${(props) => props.theme?.spacing.lg || '1.5rem'};
`;

export const Logo = styled.div<{ theme?: Theme }>`
  display: flex;
  align-items: center;
  gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  font-size: ${(props) => props.theme?.typography.fontSize.xl || '1.25rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.bold || 700};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  text-decoration: none;
  cursor: pointer;
  user-select: none;

  &:hover {
    color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  }
`;

export const LogoIcon = styled.span<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['2xl'] || '1.5rem'};
`;

export const Nav = styled.nav<{ theme?: Theme }>`
  display: flex;
  align-items: center;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    gap: ${(props) => props.theme?.spacing.sm || '0.5rem'};
  }
`;
