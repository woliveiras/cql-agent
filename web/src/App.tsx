import { Global, ThemeProvider } from '@emotion/react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { lightTheme } from './styles/theme';
import { globalStyles } from './styles/global';

import { Showcase } from './pages/Showcase';

function App() {
  return (
    <ThemeProvider theme={lightTheme}>
      <Global styles={globalStyles(lightTheme)} />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/showcase" replace />} />
          <Route path="/showcase" element={<Showcase />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
