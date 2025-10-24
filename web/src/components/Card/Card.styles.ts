import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';
import type { CardVariant } from './types';

interface StyledCardProps {
  variant: CardVariant;
  padding: 'none' | 'small' | 'medium' | 'large';
  clickable: boolean;
  theme?: Theme;
}

const getVariantStyles = (variant: CardVariant, theme: Theme) => {
  switch (variant) {
    case 'elevated':
      return `
        background: ${theme.colors.background.default};
        border: none;
        box-shadow: ${theme.shadows.md};

        &:hover {
          box-shadow: ${theme.shadows.lg};
        }
      `;
    case 'outlined':
      return `
        background: ${theme.colors.background.default};
        border: 2px solid ${theme.colors.neutral[200]};
        box-shadow: none;

        &:hover {
          border-color: ${theme.colors.neutral[300]};
        }
      `;
    case 'filled':
      return `
        background: ${theme.colors.background.paper};
        border: none;
        box-shadow: none;

        &:hover {
          background: ${theme.colors.background.hover};
        }
      `;
    default:
      return '';
  }
};

const getPaddingStyles = (padding: string, theme: Theme) => {
  switch (padding) {
    case 'none':
      return '0';
    case 'small':
      return theme.spacing.md;
    case 'medium':
      return theme.spacing.lg;
    case 'large':
      return theme.spacing.xl;
    default:
      return theme.spacing.lg;
  }
};

export const StyledCard = styled.div<StyledCardProps>`
  border-radius: ${(props) => props.theme?.borderRadius.lg || '0.75rem'};
  padding: ${(props) => props.theme && getPaddingStyles(props.padding, props.theme)};
  transition: all ${(props) => props.theme?.transitions.normal || '250ms cubic-bezier(0.4, 0, 0.2, 1)'};
  cursor: ${(props) => (props.clickable ? 'pointer' : 'default')};
  
  ${(props) => props.theme && getVariantStyles(props.variant, props.theme)}

  ${(props) =>
    props.clickable &&
    `
    &:active {
      transform: scale(0.98);
    }
  `}
`;
