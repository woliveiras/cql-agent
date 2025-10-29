import styled from '@emotion/styled';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/Button';
import type { Theme } from '../../styles/types';

const Container = styled.div<{ theme?: Theme }>`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${(props) => props.theme?.spacing.xl || '2rem'};
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
  text-align: center;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.lg || '1.5rem'};
  }
`;

const IconWrapper = styled.div<{ theme?: Theme }>`
  font-size: 8rem;
  margin-bottom: 2rem;
  animation: swing 2s ease-in-out infinite;

  @keyframes swing {
    0%, 100% {
      transform: rotate(-5deg);
    }
    50% {
      transform: rotate(5deg);
    }
  }

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    font-size: 6rem;
  }
`;

const ErrorCode = styled.h1<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['4xl'] || '3.75rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.bold || 700};
  color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};
  line-height: ${(props) => props.theme?.typography.lineHeight.tight || 1.25};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    font-size: ${(props) => props.theme?.typography.fontSize['4xl'] || '2.25rem'};
  }
`;

const Title = styled.h2<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['2xl'] || '1.5rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    font-size: ${(props) => props.theme?.typography.fontSize.xl || '1.25rem'};
  }
`;

const Description = styled.p<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  margin-bottom: ${(props) => props.theme?.spacing['2xl'] || '3rem'};
  line-height: ${(props) => props.theme?.typography.lineHeight.relaxed || 1.625};
`;

const ButtonGroup = styled.div<{ theme?: Theme }>`
  display: flex;
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  flex-wrap: wrap;
  justify-content: center;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    flex-direction: column;
    width: 100%;
  }
`;

export function NotFound() {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/');
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <Container>
      <IconWrapper>🔧</IconWrapper>
      <ErrorCode>404</ErrorCode>
      <Title>Ops! Página não encontrada</Title>
      <Description>
        Parece que esta página precisa de um reparo... ou simplesmente não existe!
        <br />
        Que tal voltar para a página inicial e começar uma nova consulta?
      </Description>
      <ButtonGroup>
        <Button onClick={handleGoHome} size="large">
          🏠 Ir para Home
        </Button>
        <Button onClick={handleGoBack} variant="secondary" size="large">
          ← Voltar
        </Button>
      </ButtonGroup>
    </Container>
  );
}

export default NotFound;
