import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@emotion/react';
import { lightTheme } from '../../styles/theme';
import { Input, Textarea } from './Input';

describe('Input', () => {
  const renderInput = (props = {}) => {
    return render(
      <ThemeProvider theme={lightTheme}>
        <Input {...props} />
      </ThemeProvider>
    );
  };

  it('should render input', () => {
    renderInput();
    expect(screen.getByRole('textbox')).toBeDefined();
  });

  it('should render with label', () => {
    renderInput({ label: 'Nome', id: 'name' });
    expect(screen.getByLabelText('Nome')).toBeDefined();
  });

  it('should render with placeholder', () => {
    renderInput({ placeholder: 'Digite seu nome' });
    expect(screen.getByPlaceholderText('Digite seu nome')).toBeDefined();
  });

  it('should render with error message', () => {
    renderInput({ error: 'Campo obrigatório' });
    expect(screen.getByText('Campo obrigatório')).toBeDefined();
  });

  it('should render with helper text', () => {
    renderInput({ helperText: 'Mínimo 3 caracteres' });
    expect(screen.getByText('Mínimo 3 caracteres')).toBeDefined();
  });

  it('should be disabled when disabled prop is true', () => {
    renderInput({ disabled: true });
    const input = screen.getByRole('textbox');
    expect(input.hasAttribute('disabled')).toBe(true);
  });

  it('should have aria-invalid when has error', () => {
    renderInput({ error: 'Erro' });
    const input = screen.getByRole('textbox');
    expect(input.getAttribute('aria-invalid')).toBe('true');
  });
});

describe('Textarea', () => {
  const renderTextarea = (props = {}) => {
    return render(
      <ThemeProvider theme={lightTheme}>
        <Textarea {...props} />
      </ThemeProvider>
    );
  };

  it('should render textarea', () => {
    renderTextarea();
    expect(screen.getByRole('textbox')).toBeDefined();
  });

  it('should render with label', () => {
    renderTextarea({ label: 'Mensagem', id: 'message' });
    expect(screen.getByLabelText('Mensagem')).toBeDefined();
  });

  it('should render with error message', () => {
    renderTextarea({ error: 'Campo obrigatório' });
    expect(screen.getByText('Campo obrigatório')).toBeDefined();
  });

  it('should render with custom rows', () => {
    renderTextarea({ rows: 10 });
    const textarea = screen.getByRole('textbox');
    expect(textarea.getAttribute('rows')).toBe('10');
  });
});
