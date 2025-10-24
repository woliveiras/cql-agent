import type { HTMLAttributes, ReactNode } from 'react';

export type CardVariant = 'elevated' | 'outlined' | 'filled';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: 'none' | 'small' | 'medium' | 'large';
  clickable?: boolean;
  children: ReactNode;
}
