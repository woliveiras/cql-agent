/**
 * Configuração de variáveis de ambiente
 * Validação e tipagem segura
 */

const isProd = import.meta.env.PROD;
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Validação de segurança em produção
if (isProd) {
  // Forçar HTTPS em produção
  if (!apiUrl.startsWith('https://')) {
    throw new Error(
      '⚠️ ERRO DE SEGURANÇA: API URL deve usar HTTPS em produção!\n' +
      `URL atual: ${apiUrl}\n` +
      'Configure VITE_API_URL corretamente no .env.production'
    );
  }

  // Validar que não está usando localhost/127.0.0.1 em produção
  if (apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1')) {
    throw new Error(
      '⚠️ ERRO: Não use localhost em produção!\n' +
      'Configure VITE_API_URL com o domínio real no .env.production'
    );
  }

  console.info('✅ Validação de segurança: OK');
}

export const env = {
  apiUrl,
  isProd,
  isDev: import.meta.env.DEV,
} as const;
