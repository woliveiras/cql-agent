import { Header } from '../Header';
import { LayoutContainer, MainContent } from './Layout.styles';
import type { LayoutProps } from './types';

export const Layout = ({ children, showHeader = true }: LayoutProps) => {
  return (
    <LayoutContainer>
      {showHeader && <Header />}
      <MainContent>{children}</MainContent>
    </LayoutContainer>
  );
};
