import axios, { type AxiosError } from 'axios';
import { env } from '../config/env';
import type { ApiError } from './types';

export const api = axios.create({
  baseURL: env.apiUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Adicionar headers customizados se necessário
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string | { error?: string; details?: string } }>) => {
    let errorMessage = 'Erro desconhecido';
    
    if (error.response?.data) {
      const data = error.response.data;
      
      // Backend pode retornar detail como string ou objeto
      if (typeof data.detail === 'string') {
        errorMessage = data.detail;
      } else if (typeof data.detail === 'object' && data.detail) {
        errorMessage = data.detail.error || data.detail.details || JSON.stringify(data.detail);
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    const apiError: ApiError = {
      detail: errorMessage,
      status: error.response?.status || 500,
    };
    
    // Log para debug
    console.error('API Error:', {
      status: apiError.status,
      detail: apiError.detail,
      url: error.config?.url,
      method: error.config?.method,
      data: error.config?.data,
    });
    
    return Promise.reject(apiError);
  }
);
