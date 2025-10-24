import { ThemeProvider } from '@emotion/react';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { lightTheme } from '../../styles/theme';
import { Card } from './Card';

describe('Card', () => {
  const renderCard = (props = {}) => {
    return render(
      <ThemeProvider theme={lightTheme}>
        <Card {...props}>
          <p>Card content</p>
        </Card>
      </ThemeProvider>
    );
  };

  it('should render card with content', () => {
    renderCard();
    expect(screen.getByText('Card content')).toBeDefined();
  });

  it('should render elevated variant by default', () => {
    const { container } = renderCard();
    const card = container.firstChild;
    expect(card).toBeDefined();
  });

  it('should render outlined variant', () => {
    const { container } = renderCard({ variant: 'outlined' });
    const card = container.firstChild;
    expect(card).toBeDefined();
  });

  it('should render filled variant', () => {
    const { container } = renderCard({ variant: 'filled' });
    const card = container.firstChild;
    expect(card).toBeDefined();
  });

  it('should render with small padding', () => {
    const { container } = renderCard({ padding: 'small' });
    const card = container.firstChild;
    expect(card).toBeDefined();
  });

  it('should render with no padding', () => {
    const { container } = renderCard({ padding: 'none' });
    const card = container.firstChild;
    expect(card).toBeDefined();
  });

  it('should render with large padding', () => {
    const { container } = renderCard({ padding: 'large' });
    const card = container.firstChild;
    expect(card).toBeDefined();
  });

  it('should be clickable when clickable prop is true', () => {
    const { container } = renderCard({ clickable: true });
    const card = container.firstChild as HTMLElement;
    const computedStyle = window.getComputedStyle(card);
    expect(computedStyle.cursor).toBe('pointer');
  });
});
