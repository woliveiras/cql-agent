import type { ButtonProps } from './types';
import { StyledButton, LoadingSpinner } from './Button.styles';

export const Button = ({
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  loading = false,
  disabled,
  children,
  ...rest
}: ButtonProps) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <LoadingSpinner />}
      {children}
    </StyledButton>
  );
};
