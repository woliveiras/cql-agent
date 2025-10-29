import { Component, type ErrorInfo, type ReactNode } from 'react';
import {
  ErrorContainer,
  ErrorContent,
  ErrorTitle,
  ErrorMessage,
  ErrorDetails,
  ReloadButton,
  HomeButton,
  ButtonGroup,
} from './ErrorBoundary.styles';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // In production, you could send this to an error tracking service
    // Example: Sentry.captureException(error, { extra: errorInfo });

    this.setState({
      error,
      errorInfo,
    });
  }

  handleReload = (): void => {
    window.location.reload();
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorContainer>
          <ErrorContent>
            <ErrorTitle>Ops! Algo deu errado</ErrorTitle>
            <ErrorMessage>
              Desculpe, ocorreu um erro inesperado. Nossa equipe foi notificada e
              estamos trabalhando para resolver o problema.
            </ErrorMessage>

            {import.meta.env.DEV && this.state.error && (
              <ErrorDetails>
                <summary>Detalhes do erro (apenas em desenvolvimento)</summary>
                <pre>
                  <strong>Erro:</strong> {this.state.error.toString()}
                  {'\n\n'}
                  <strong>Stack trace:</strong>
                  {'\n'}
                  {this.state.error.stack}
                  {'\n\n'}
                  {this.state.errorInfo && (
                    <>
                      <strong>Component stack:</strong>
                      {'\n'}
                      {this.state.errorInfo.componentStack}
                    </>
                  )}
                </pre>
              </ErrorDetails>
            )}

            <ButtonGroup>
              <ReloadButton onClick={this.handleReload}>
                Recarregar página
              </ReloadButton>
              <HomeButton onClick={this.handleGoHome}>
                Voltar ao início
              </HomeButton>
            </ButtonGroup>
          </ErrorContent>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
