import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';

interface AppState {
  user: User | null;
  token: string | null;
  theme: 'light' | 'dark' | 'system';
  currentCity: string;
  
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setCurrentCity: (city: string) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      theme: 'system',
      currentCity: 'Москва',
      
      setUser: (user) => set({ user }),
      setToken: (token) => {
        if (token) {
          localStorage.setItem('token', token);
        } else {
          localStorage.removeItem('token');
        }
        set({ token });
      },
      setTheme: (theme) => set({ theme }),
      setCurrentCity: (city) => set({ currentCity: city }),
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null });
      },
    }),
    {
      name: 'weathernews-storage',
    }
  )
);
