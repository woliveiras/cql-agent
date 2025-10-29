import { useLocation, useNavigate } from 'react-router-dom';
import { useChatStore } from '../../store/chat';
import { Button } from '../Button';
import { HeaderContainer, HeaderContent, Logo, LogoIcon, Nav } from './Header.styles';
import type { HeaderProps } from './types';

export const Header = ({ onNewChat }: HeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const startNewConversation = useChatStore((state) => state.startNewConversation);

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
    } else {
      // Inicia nova conversa e redireciona para home
      startNewConversation();

      // Se já estiver na home, apenas recarrega
      if (location.pathname === '/') {
        window.location.reload();
      } else {
        navigate('/');
      }
    }
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo onClick={handleLogoClick}>
          <LogoIcon>🔧</LogoIcon>
          <span>CQL Assistant</span>
        </Logo>

        <Nav>
          <Button variant="ghost" size="small" onClick={handleNewChat}>
            Nova Consulta
          </Button>
        </Nav>
      </HeaderContent>
    </HeaderContainer>
  );
};
