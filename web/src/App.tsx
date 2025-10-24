import { Global, ThemeProvider } from '@emotion/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { lightTheme } from './styles/theme';
import { globalStyles } from './styles/global';

import { Layout } from './components/Layout';
import { Welcome } from './pages/Welcome';
import { Showcase } from './pages/Showcase';

function App() {
  return (
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
                <div>Chat Page (TODO)</div>
              </Layout>
            }
          />
          <Route path="/showcase" element={<Showcase />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
