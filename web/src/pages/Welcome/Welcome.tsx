import styled from '@emotion/styled';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '@emotion/react';
import type { Theme } from '../../styles/types';
import { Button } from '../../components/Button';
import { Textarea } from '../../components/Input';
import { Card } from '../../components/Card';

const Container = styled.div<{ theme?: Theme }>`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${(props) => props.theme?.spacing.xl || '2rem'};
  max-width: 800px;
  margin: 0 auto;
  width: 100%;

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    padding: ${(props) => props.theme?.spacing.lg || '1.5rem'};
  }
`;

const Hero = styled.div<{ theme?: Theme }>`
  text-align: center;
  margin-bottom: ${(props) => props.theme?.spacing['3xl'] || '4rem'};
`;

const Title = styled.h1<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize['4xl'] || '2.25rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.bold || 700};
  color: ${(props) => props.theme?.colors.text.primary || '#0F172A'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};
  line-height: ${(props) => props.theme?.typography.lineHeight.tight || 1.25};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    font-size: ${(props) => props.theme?.typography.fontSize['3xl'] || '1.875rem'};
  }
`;

const Subtitle = styled.p<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.lg || '1.125rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  margin-bottom: ${(props) => props.theme?.spacing.sm || '0.5rem'};
`;

const AssistantName = styled.span<{ theme?: Theme }>`
  color: ${(props) => props.theme?.colors.primary.main || '#DC2626'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.semibold || 600};
`;

const FreeNotice = styled.p<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
  color: ${(props) => props.theme?.colors.text.disabled || '#94A3B8'};
  margin-top: ${(props) => props.theme?.spacing.md || '1rem'};
`;

const InputSection = styled.div<{ theme?: Theme }>`
  width: 100%;
  margin-bottom: ${(props) => props.theme?.spacing['2xl'] || '3rem'};
`;

const SuggestionsTitle = styled.h3<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.base || '1rem'};
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
  margin-bottom: ${(props) => props.theme?.spacing.md || '1rem'};
  text-align: center;
`;

const SuggestionsGrid = styled.div<{ theme?: Theme }>`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${(props) => props.theme?.spacing.md || '1rem'};
  margin-bottom: ${(props) => props.theme?.spacing.xl || '2rem'};

  @media (max-width: ${(props) => props.theme?.breakpoints.mobile || '640px'}) {
    grid-template-columns: 1fr;
  }
`;

const SuggestionCard = styled(Card)`
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
  }
`;

const SuggestionTitle = styled.div<{ theme?: Theme }>`
  font-weight: ${(props) => props.theme?.typography.fontWeight.medium || 500};
  margin-bottom: ${(props) => props.theme?.spacing.xs || '0.25rem'};
`;

const SuggestionText = styled.div<{ theme?: Theme }>`
  font-size: ${(props) => props.theme?.typography.fontSize.sm || '0.875rem'};
  color: ${(props) => props.theme?.colors.text.secondary || '#475569'};
`;

const suggestions = [
  { title: '💧 Torneira pingando', text: 'Como consertar uma torneira que está vazando?' },
  { title: '💡 Lâmpada queimada', text: 'Como trocar uma lâmpada com segurança?' },
  { title: '🚪 Porta rangendo', text: 'O que fazer quando uma porta está rangendo?' },
  { title: '🔌 Tomada não funciona', text: 'Tomada não está funcionando, o que verificar?' },
];

export function Welcome() {
  const theme = useTheme() as Theme;
  const navigate = useNavigate();
  const [message, setMessage] = useState('');

  const handleStart = () => {
    if (message.trim()) {
      // TODO: Navegar para página de chat com a mensagem
      console.log('Iniciando chat com:', message);
      navigate('/chat');
    }
  };

  const handleSuggestionClick = (suggestionText: string) => {
    setMessage(suggestionText);
  };

  return (
    <Container>
      <Hero>
        <Title>
          Olá, sou o <AssistantName>Vicente</AssistantName>
        </Title>
        <Subtitle>Seu assistente de IA para reparos residenciais</Subtitle>
        <FreeNotice>✨ Gratuito e sem necessidade de login</FreeNotice>
      </Hero>

      <InputSection>
        <Textarea
          fullWidth
          placeholder="Me conte sobre seu problema..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
        />
        <div style={{ marginTop: theme.spacing.md, textAlign: 'center' }}>
          <Button onClick={handleStart} disabled={!message.trim()} size="large">
            Começar Consulta
          </Button>
        </div>
      </InputSection>

      <div style={{ width: '100%' }}>
        <SuggestionsTitle>Ou escolha uma sugestão:</SuggestionsTitle>
        <SuggestionsGrid>
          {suggestions.map((suggestion) => (
            <SuggestionCard
              key={suggestion.title}
              variant="outlined"
              padding="medium"
              clickable
              onClick={() => handleSuggestionClick(suggestion.text)}
            >
              <SuggestionTitle>{suggestion.title}</SuggestionTitle>
              <SuggestionText>{suggestion.text}</SuggestionText>
            </SuggestionCard>
          ))}
        </SuggestionsGrid>
      </div>
    </Container>
  );
}

export default Welcome;
