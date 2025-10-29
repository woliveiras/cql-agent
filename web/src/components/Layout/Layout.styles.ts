import styled from '@emotion/styled';
import type { Theme } from '../../styles/types';

export const LayoutContainer = styled.div<{ theme?: Theme }>`
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: ${(props) => props.theme?.colors.background.default || '#FFFFFF'};
`;

export const MainContent = styled.main<{ theme?: Theme }>`
  flex: 1;
  display: flex;
  flex-direction: column;
`;
