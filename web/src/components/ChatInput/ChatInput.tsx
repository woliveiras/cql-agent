import { type KeyboardEvent, useEffect, useRef } from 'react';
import {
  CharCounter,
  Container,
  Disclaimer,
  InputWrapper,
  SendButton,
  StyledTextarea,
} from './ChatInput.styles';
import type { ChatInputProps } from './types';

export function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = 'Digite sua mensagem...',
  maxLength = 500,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = '120px';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 240)}px`;
    }
  }, []);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSend();
      }
    }
  };

  const handleSendClick = () => {
    if (value.trim() && !disabled) {
      onSend();
    }
  };

  const isAtLimit = value.length >= maxLength;
  const canSend = value.trim().length > 0 && !disabled;

  return (
    <>
      <Container>
        <InputWrapper>
          <StyledTextarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            maxLength={maxLength}
            rows={1}
          />
          {maxLength && (
            <CharCounter isLimit={isAtLimit}>
              {value.length}/{maxLength}
            </CharCounter>
          )}
        </InputWrapper>

        <SendButton
          onClick={handleSendClick}
          disabled={!canSend}
          type="button"
          aria-label="Enviar mensagem"
        >
          ↑
        </SendButton>
      </Container>
      <Disclaimer>
        Vicente é um assistente virtual e pode não entender todos os problemas. Em caso de emergência, contate um profissional.
      </Disclaimer>
    </>
  );
}
