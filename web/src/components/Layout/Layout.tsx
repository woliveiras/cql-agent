import { Header } from '../Header';
import type { LayoutProps } from './types';
import { LayoutContainer, MainContent } from './Layout.styles';

export const Layout = ({ children, showHeader = true }: LayoutProps) => {
  return (
    <LayoutContainer>
      {showHeader && <Header />}
      <MainContent>{children}</MainContent>
    </LayoutContainer>
  );
};
