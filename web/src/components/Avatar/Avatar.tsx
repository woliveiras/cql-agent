import type { AvatarProps } from './types';
import { StyledAvatar, AvatarImage, AvatarIcon } from './Avatar.styles';

const getInitials = (name: string): string => {
  const parts = name.trim().split(' ');
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
};

// Ícone de usuário (pessoa)
const UserIcon = () => (
  <AvatarIcon viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </AvatarIcon>
);

// Ícone de assistente (ferramenta/chave inglesa)
const AssistantIcon = () => (
  <AvatarIcon viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
  </AvatarIcon>
);

export const Avatar = ({
  size = 'medium',
  variant = 'user',
  name,
  src,
  alt,
  ...rest
}: AvatarProps) => {
  const hasImage = Boolean(src);

  return (
    <StyledAvatar size={size} variant={variant} hasImage={hasImage} {...rest}>
      {src ? (
        <AvatarImage src={src} alt={alt || name || `${variant} avatar`} />
      ) : name ? (
        getInitials(name)
      ) : variant === 'assistant' ? (
        <AssistantIcon />
      ) : (
        <UserIcon />
      )}
    </StyledAvatar>
  );
};
