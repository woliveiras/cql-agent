import type { HTMLAttributes } from 'react';

export type AvatarSize = 'small' | 'medium' | 'large';
export type AvatarVariant = 'user' | 'assistant';

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  size?: AvatarSize;
  variant?: AvatarVariant;
  name?: string;
  src?: string;
  alt?: string;
}
