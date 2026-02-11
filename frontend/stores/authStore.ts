/**
 * Auth Store - SINGLE SOURCE OF TRUTH
 * Controla: isAuthenticated, userId, token, profileCompleted
 */
import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  token: string | null;
  profileCompleted: boolean;
  isInitialized: boolean;
  
  initialize: () => Promise<void>;
  login: (userId: string, token: string, profileCompleted: boolean) => Promise<void>;
  setProfileCompleted: (completed: boolean) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  userId: null,
  token: null,
  profileCompleted: false,
  isInitialized: false,
  
  initialize: async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      const userId = await AsyncStorage.getItem('userId');
      const profileCompleted = await AsyncStorage.getItem('profileCompleted');
      
      if (token && userId) {
        set({ 
          isAuthenticated: true, 
          userId, 
          token,
          profileCompleted: profileCompleted === 'true',
          isInitialized: true 
        });
      } else {
        set({ 
          isAuthenticated: false, 
          userId: null, 
          token: null,
          profileCompleted: false,
          isInitialized: true 
        });
      }
    } catch (error) {
      set({ isAuthenticated: false, userId: null, token: null, profileCompleted: false, isInitialized: true });
    }
  },
  
  login: async (userId: string, token: string, profileCompleted: boolean) => {
    // IMPORTANTE: Limpar cache de perfil antigo antes de salvar novo login
    // Isso evita que dados de outro usuário ou dados desatualizados apareçam
    await AsyncStorage.removeItem('userProfile');
    
    await AsyncStorage.setItem('token', token);
    await AsyncStorage.setItem('userId', userId);
    await AsyncStorage.setItem('profileCompleted', profileCompleted ? 'true' : 'false');
    set({ isAuthenticated: true, userId, token, profileCompleted });
  },
  
  setProfileCompleted: async (completed: boolean) => {
    await AsyncStorage.setItem('profileCompleted', completed ? 'true' : 'false');
    set({ profileCompleted: completed });
  },
  
  logout: async () => {
    // Limpa AsyncStorage PRIMEIRO
    try {
      await AsyncStorage.clear();
    } catch (error) {
      console.error('Error clearing AsyncStorage:', error);
    }
    // Depois atualiza o estado
    set({ isAuthenticated: false, userId: null, token: null, profileCompleted: false, isInitialized: true });
  },
}));
