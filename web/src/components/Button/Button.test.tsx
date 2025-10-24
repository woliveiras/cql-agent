import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@emotion/react';
import { lightTheme } from '../../styles/theme';
import { Button } from './Button';

describe('Button', () => {
  const renderButton = (props = {}) => {
    return render(
      <ThemeProvider theme={lightTheme}>
        <Button {...props}>Click me</Button>
      </ThemeProvider>
    );
  };

  it('should render button with text', () => {
    renderButton();
    expect(screen.getByRole('button', { name: /click me/i })).toBeDefined();
  });

  it('should render primary variant by default', () => {
    renderButton();
    const button = screen.getByRole('button');
    expect(button).toBeDefined();
  });

  it('should render secondary variant', () => {
    renderButton({ variant: 'secondary' });
    const button = screen.getByRole('button');
    expect(button).toBeDefined();
  });

  it('should render ghost variant', () => {
    renderButton({ variant: 'ghost' });
    const button = screen.getByRole('button');
    expect(button).toBeDefined();
  });

  it('should be disabled when disabled prop is true', () => {
    renderButton({ disabled: true });
    const button = screen.getByRole('button');
    expect(button.hasAttribute('disabled')).toBe(true);
  });

  it('should be disabled when loading is true', () => {
    renderButton({ loading: true });
    const button = screen.getByRole('button');
    expect(button.hasAttribute('disabled')).toBe(true);
  });

  it('should render loading spinner when loading', () => {
    const { container } = renderButton({ loading: true });
    const spinner = container.querySelector('span');
    expect(spinner).toBeDefined();
  });
});
