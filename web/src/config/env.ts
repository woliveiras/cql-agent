export const env = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:5000',
} as const;
