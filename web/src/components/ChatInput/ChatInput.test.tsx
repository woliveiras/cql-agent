import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@emotion/react';
import { lightTheme } from '../../styles/theme';
import { ChatInput } from './ChatInput';

const renderWithTheme = (component: React.ReactElement) => {
  return render(<ThemeProvider theme={lightTheme}>{component}</ThemeProvider>);
};

describe('ChatInput', () => {
  it('renders with placeholder', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput
        value=""
        onChange={onChange}
        onSend={onSend}
        placeholder="Digite aqui..."
      />
    );
    
    expect(screen.getByPlaceholderText('Digite aqui...')).toBeDefined();
  });

  it('calls onChange when typing', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="" onChange={onChange} onSend={onSend} />
    );
    
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    
    expect(onChange).toHaveBeenCalledWith('Test message');
  });

  it('calls onSend when clicking send button', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="Test message" onChange={onChange} onSend={onSend} />
    );
    
    const sendButton = screen.getByLabelText('Enviar mensagem');
    fireEvent.click(sendButton);
    
    expect(onSend).toHaveBeenCalled();
  });

  it('calls onSend when pressing Enter', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="Test message" onChange={onChange} onSend={onSend} />
    );
    
    const textarea = screen.getByRole('textbox');
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });
    
    expect(onSend).toHaveBeenCalled();
  });

  it('does not send on Shift+Enter', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="Test message" onChange={onChange} onSend={onSend} />
    );
    
    const textarea = screen.getByRole('textbox');
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });
    
    expect(onSend).not.toHaveBeenCalled();
  });

  it('disables send when value is empty', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="" onChange={onChange} onSend={onSend} />
    );
    
    const sendButton = screen.getByLabelText('Enviar mensagem');
    expect(sendButton.hasAttribute('disabled')).toBe(true);
  });

  it('disables input when disabled prop is true', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="" onChange={onChange} onSend={onSend} disabled={true} />
    );
    
    const textarea = screen.getByRole('textbox');
    expect(textarea.hasAttribute('disabled')).toBe(true);
  });

  it('shows character counter', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="Test" onChange={onChange} onSend={onSend} maxLength={100} />
    );
    
    expect(screen.getByText('4/100')).toBeDefined();
  });

  it('does not send when value is only whitespace', () => {
    const onChange = vi.fn();
    const onSend = vi.fn();
    
    renderWithTheme(
      <ChatInput value="   " onChange={onChange} onSend={onSend} />
    );
    
    const sendButton = screen.getByLabelText('Enviar mensagem');
    fireEvent.click(sendButton);
    
    expect(onSend).not.toHaveBeenCalled();
  });
});
