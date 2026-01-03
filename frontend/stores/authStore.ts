/**
 * Auth Store - VERSÃO SIMPLIFICADA
 * SEM persistência automática - estado em memória apenas
 */
import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  accessToken: string | null;
  isInitialized: boolean;
  
  initialize: () => Promise<void>;
  login: (userId: string, token: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isAuthenticated: false,
  userId: null,
  accessToken: null,
  isInitialized: false,
  
  initialize: async () => {
    try {
      const token = await AsyncStorage.getItem('accessToken');
      const userId = await AsyncStorage.getItem('userId');
      
      if (token && userId) {
        set({ isAuthenticated: true, userId, accessToken: token, isInitialized: true });
      } else {
        set({ isAuthenticated: false, userId: null, accessToken: null, isInitialized: true });
      }
    } catch (error) {
      set({ isAuthenticated: false, userId: null, accessToken: null, isInitialized: true });
    }
  },
  
  login: async (userId: string, token: string) => {
    await AsyncStorage.setItem('accessToken', token);
    await AsyncStorage.setItem('userId', userId);
    set({ isAuthenticated: true, userId, accessToken: token });
  },
  
  logout: async () => {
    // 1. Reset state FIRST
    set({ isAuthenticated: false, userId: null, accessToken: null });
    
    // 2. Clear ALL storage
    try {
      await AsyncStorage.clear();
    } catch (e) {
      console.error('Logout storage error:', e);
    }
  },
}));
