import { Global, ThemeProvider } from '@emotion/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { queryClient } from './lib/queryClient';
import { Chat } from './pages/Chat';
import { NotFound } from './pages/NotFound';
import { Showcase } from './pages/Showcase';
import { Welcome } from './pages/Welcome';
import { globalStyles } from './styles/global';
import { lightTheme } from './styles/theme';

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
            <Route
              path="*"
              element={
                <Layout showHeader>
                  <NotFound />
                </Layout>
              }
            />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
