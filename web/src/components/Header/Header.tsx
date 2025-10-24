import { useNavigate } from 'react-router-dom';
import { Button } from '../Button';
import type { HeaderProps } from './types';
import { HeaderContainer, HeaderContent, Logo, LogoIcon, Nav } from './Header.styles';

export const Header = ({ onNewChat }: HeaderProps) => {
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
    } else {
      navigate('/');
    }
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo onClick={handleLogoClick}>
          <LogoIcon>🔧</LogoIcon>
          <span>RepairChat</span>
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
