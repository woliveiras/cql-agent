import { useState } from 'react';
import { Global, ThemeProvider } from '@emotion/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import { Layout } from './components/Layout';
import OfflineIndicator from './components/OfflineIndicator';
import InstallPrompt from './components/InstallPrompt';
import { queryClient } from './lib/queryClient';
import { usePWA } from './hooks/usePWA';
import { Chat } from './pages/Chat';
import { NotFound } from './pages/NotFound';
import { Showcase } from './pages/Showcase';
import { Welcome } from './pages/Welcome';
import { globalStyles } from './styles/global';
import { lightTheme } from './styles/theme';

function App() {
  const pwa = usePWA();
  const [showInstallPrompt, setShowInstallPrompt] = useState(true);

  const handleInstall = async () => {
    const success = await pwa.install();
    if (success) {
      setShowInstallPrompt(false);
    }
    return success;
  };

  const handleDismissInstall = () => {
    setShowInstallPrompt(false);
    // Pode armazenar no localStorage para não mostrar novamente
    localStorage.setItem('installPromptDismissed', 'true');
  };

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={lightTheme}>
          <Global styles={globalStyles(lightTheme)} />

          {/* Indicador de status offline/online */}
          <OfflineIndicator isOnline={pwa.isOnline} queuedMessages={pwa.queuedMessages} />

          {/* Prompt de instalação do PWA */}
          {pwa.canInstall && showInstallPrompt && !localStorage.getItem('installPromptDismissed') && (
            <InstallPrompt onInstall={handleInstall} onDismiss={handleDismissInstall} />
          )}

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
    </ErrorBoundary>
  );
}

export default App;
