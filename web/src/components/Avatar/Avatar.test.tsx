import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@emotion/react';
import { lightTheme } from '../../styles/theme';
import { Avatar } from './Avatar';

describe('Avatar', () => {
  const renderAvatar = (props = {}) => {
    return render(
      <ThemeProvider theme={lightTheme}>
        <Avatar {...props} />
      </ThemeProvider>
    );
  };

  it('should render avatar', () => {
    const { container } = renderAvatar();
    expect(container.firstChild).toBeDefined();
  });

  it('should render with initials from name', () => {
    renderAvatar({ name: 'John Doe' });
    expect(screen.getByText('JD')).toBeDefined();
  });

  it('should render single initial for single word name', () => {
    renderAvatar({ name: 'John' });
    expect(screen.getByText('J')).toBeDefined();
  });

  it('should render user icon when no name or image', () => {
    const { container } = renderAvatar({ variant: 'user' });
    const svg = container.querySelector('svg');
    expect(svg).toBeDefined();
  });

  it('should render assistant icon when variant is assistant', () => {
    const { container } = renderAvatar({ variant: 'assistant' });
    const svg = container.querySelector('svg');
    expect(svg).toBeDefined();
  });

  it('should render image when src is provided', () => {
    renderAvatar({ src: 'https://example.com/avatar.jpg', alt: 'User avatar' });
    const img = screen.getByAltText('User avatar');
    expect(img).toBeDefined();
    expect(img.getAttribute('src')).toBe('https://example.com/avatar.jpg');
  });

  it('should render small size', () => {
    const { container } = renderAvatar({ size: 'small', name: 'Test' });
    expect(container.firstChild).toBeDefined();
  });

  it('should render large size', () => {
    const { container } = renderAvatar({ size: 'large', name: 'Test' });
    expect(container.firstChild).toBeDefined();
  });

  it('should use default alt text when not provided', () => {
    renderAvatar({ src: 'https://example.com/avatar.jpg', variant: 'user' });
    const img = screen.getByAltText('user avatar');
    expect(img).toBeDefined();
  });
});
