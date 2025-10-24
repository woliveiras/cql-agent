import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@emotion/react';
import { lightTheme } from '../../styles/theme';
import { MessageBubble } from './MessageBubble';

const renderWithTheme = (component: React.ReactElement) => {
  return render(<ThemeProvider theme={lightTheme}>{component}</ThemeProvider>);
};

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    renderWithTheme(
      <MessageBubble role="user" content="Minha torneira está vazando" />
    );
    expect(screen.getByText('Minha torneira está vazando')).toBeDefined();
  });

  it('renders assistant message correctly', () => {
    renderWithTheme(
      <MessageBubble role="assistant" content="Vou ajudar você com isso!" />
    );
    expect(screen.getByText('Vou ajudar você com isso!')).toBeDefined();
  });

  it('displays timestamp when provided', () => {
    const timestamp = new Date('2025-10-24T10:30:00');
    renderWithTheme(
      <MessageBubble
        role="user"
        content="Test message"
        timestamp={timestamp}
      />
    );
    expect(screen.getByText('10:30')).toBeDefined();
  });

  it('shows streaming cursor when isStreaming is true', () => {
    const { container } = renderWithTheme(
      <MessageBubble role="assistant" content="Digitando" isStreaming={true} />
    );
    expect(container.querySelector('span[class*="StreamingCursor"]')).toBeTruthy();
  });

  it('does not show streaming cursor when isStreaming is false', () => {
    const { container } = renderWithTheme(
      <MessageBubble role="assistant" content="Mensagem completa" isStreaming={false} />
    );
    expect(container.querySelector('span[class*="StreamingCursor"]')).toBeFalsy();
  });

  it('renders user avatar for user messages', () => {
    const { container } = renderWithTheme(
      <MessageBubble role="user" content="Test" />
    );
    // Avatar component renders with specific structure
    expect(container.querySelector('[class*="Avatar"]')).toBeTruthy();
  });

  it('renders assistant avatar for assistant messages', () => {
    const { container } = renderWithTheme(
      <MessageBubble role="assistant" content="Test" />
    );
    expect(container.querySelector('[class*="Avatar"]')).toBeTruthy();
  });
});
