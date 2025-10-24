import type { InputProps, TextareaProps } from './types';
import { InputWrapper, Label, StyledInput, StyledTextarea, HelperText } from './Input.styles';

export const Input = ({ label, error, helperText, fullWidth = false, id, ...rest }: InputProps) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  const hasError = Boolean(error);

  return (
    <InputWrapper fullWidth={fullWidth}>
      {label && <Label htmlFor={inputId}>{label}</Label>}
      <StyledInput id={inputId} hasError={hasError} aria-invalid={hasError} {...rest} />
      {(error || helperText) && (
        <HelperText isError={hasError}>{error || helperText}</HelperText>
      )}
    </InputWrapper>
  );
};

export const Textarea = ({
  label,
  error,
  helperText,
  fullWidth = false,
  id,
  rows = 4,
  ...rest
}: TextareaProps) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  const hasError = Boolean(error);

  return (
    <InputWrapper fullWidth={fullWidth}>
      {label && <Label htmlFor={textareaId}>{label}</Label>}
      <StyledTextarea
        id={textareaId}
        hasError={hasError}
        aria-invalid={hasError}
        rows={rows}
        {...rest}
      />
      {(error || helperText) && (
        <HelperText isError={hasError}>{error || helperText}</HelperText>
      )}
    </InputWrapper>
  );
};
