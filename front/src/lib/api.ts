import axios from 'axios';
import type { WeatherResponse, ForecastResponse, NewsResponse, NewsParams, User } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для добавления токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const weatherApi = {
  getCurrent: async (city: string): Promise<WeatherResponse> => {
    const { data } = await api.get(`/weather/current`, { params: { city } });
    return data;
  },
  
  getForecast: async (city: string, days: number = 7): Promise<ForecastResponse> => {
    const { data } = await api.get(`/weather/forecast`, { params: { city, days } });
    return data;
  },
};

export const newsApi = {
  getNews: async (params: NewsParams): Promise<NewsResponse> => {
    const { data } = await api.get(`/news`, { params });
    return data;
  },
};

export const userApi = {
  getProfile: async (): Promise<User> => {
    const { data } = await api.get(`/user/profile`);
    return data;
  },
  
  updateProfile: async (updates: Partial<User>): Promise<User> => {
    const { data } = await api.put(`/user/profile`, updates);
    return data;
  },
  
  addFavoriteCity: async (city: string): Promise<User> => {
    const { data } = await api.post(`/user/favorites`, { city });
    return data;
  },
  
  removeFavoriteCity: async (city: string): Promise<User> => {
    const { data } = await api.delete(`/user/favorites/${city}`);
    return data;
  },
};

export const authApi = {
  loginWithTelegram: async (telegramData: any): Promise<{ token: string; user: User }> => {
    const { data } = await api.post(`/auth/telegram`, telegramData);
    return data;
  },
  
  loginWithEmail: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const { data } = await api.post(`/auth/login`, { email, password });
    return data;
  },
  
  register: async (email: string, password: string, username: string): Promise<{ token: string; user: User }> => {
    const { data } = await api.post(`/auth/register`, { email, password, username });
    return data;
  },
};

export default api;
