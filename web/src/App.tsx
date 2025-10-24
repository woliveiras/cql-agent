import { Global, ThemeProvider } from '@emotion/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { lightTheme } from './styles/theme';
import { globalStyles } from './styles/global';
import { queryClient } from './lib/queryClient';

import { Layout } from './components/Layout';
import { Welcome } from './pages/Welcome';
import { Chat } from './pages/Chat';
import { Showcase } from './pages/Showcase';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={lightTheme}>
        <Global styles={globalStyles(lightTheme)} />
        <BrowserRouter>
          <Routes>
            <Route
              path="/"
              element={
                <Layout showHeader>
                  <Welcome />
                </Layout>
              }
            />
            <Route
              path="/chat"
              element={
                <Layout showHeader>
                  <Chat />
                </Layout>
              }
            />
            <Route path="/showcase" element={<Showcase />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
