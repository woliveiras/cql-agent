import { useState } from 'react';
import {
  Container,
  Content,
  Icon,
  Title,
  Description,
  ButtonGroup,
  InstallButton,
  DismissButton,
} from './InstallPrompt.styles';

interface InstallPromptProps {
  onInstall: () => Promise<boolean>;
  onDismiss: () => void;
}

export function InstallPrompt({ onInstall, onDismiss }: InstallPromptProps) {
  const [installing, setInstalling] = useState(false);

  const handleInstall = async () => {
    setInstalling(true);
    try {
      const success = await onInstall();
      if (success) {
        // Prompt será fechado automaticamente
      } else {
        setInstalling(false);
      }
    } catch (error) {
      console.error('Erro ao instalar:', error);
      setInstalling(false);
    }
  };

  return (
    <Container>
      <Content>
        <Icon>📱</Icon>
        <div>
          <Title>Instalar Vicente</Title>
          <Description>
            Instale o app para acesso rápido e use mesmo sem internet!
          </Description>
        </div>
      </Content>

      <ButtonGroup>
        <InstallButton onClick={handleInstall} disabled={installing}>
          {installing ? 'Instalando...' : 'Instalar'}
        </InstallButton>
        <DismissButton onClick={onDismiss} disabled={installing}>
          Agora não
        </DismissButton>
      </ButtonGroup>
    </Container>
  );
}

export default InstallPrompt;
