import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';
import type { AvatarSize, AvatarVariant } from './types';

interface StyledAvatarProps {
  size: AvatarSize;
  variant: AvatarVariant;
  hasImage: boolean;
  theme?: Theme;
}

const getSizeStyles = (size: AvatarSize) => {
  switch (size) {
    case 'small':
      return `
        width: 32px;
        height: 32px;
        font-size: 0.875rem;
      `;
    case 'medium':
      return `
        width: 40px;
        height: 40px;
        font-size: 1rem;
      `;
    case 'large':
      return `
        width: 56px;
        height: 56px;
        font-size: 1.25rem;
      `;
    default:
      return '';
  }
};

const getVariantStyles = (variant: AvatarVariant, theme: Theme) => {
  switch (variant) {
    case 'user':
      return `
        background: ${theme.colors.primary.main};
        color: ${theme.colors.primary.contrast};
      `;
    case 'assistant':
      return `
        background: ${theme.colors.secondary.main};
        color: ${theme.colors.secondary.contrast};
      `;
    default:
      return '';
  }
};

export const StyledAvatar = styled.div<StyledAvatarProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: ${(props) => props.theme?.borderRadius.full || '9999px'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
  user-select: none;
  flex-shrink: 0;
  overflow: hidden;
  
  ${(props) => getSizeStyles(props.size)}
  ${(props) => props.theme && !props.hasImage && getVariantStyles(props.variant, props.theme)}
`;

export const AvatarImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

export const AvatarIcon = styled.svg`
  width: 60%;
  height: 60%;
`;
