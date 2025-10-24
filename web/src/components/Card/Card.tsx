import type { CardProps } from './types';
import { StyledCard } from './Card.styles';

export const Card = ({
  variant = 'elevated',
  padding = 'medium',
  clickable = false,
  children,
  ...rest
}: CardProps) => {
  return (
    <StyledCard variant={variant} padding={padding} clickable={clickable} {...rest}>
      {children}
    </StyledCard>
  );
};
