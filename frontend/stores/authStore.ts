/**
 * Auth Store - Gerenciamento de Autenticação
 * CRÍTICO: Controla estado de sessão e logout completo
 * 
 * IMPORTANTE: NÃO usa persist para evitar reidratação após logout
 */
import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Lista COMPLETA de chaves a limpar no logout
const ALL_STORAGE_KEYS = [
  'userId',
  'user',
  'userProfile',
  'authToken',
  'accessToken',
  'refreshToken',
  'userEmail',
  'hasCompletedOnboarding',
  'dietPlan',
  'workoutPlan',
  'profileImage',
  'notificationsEnabled',
  'laf-settings',
  'laf-auth',
  'profile',
  'settings',
  'onboardingCompleted',
  'dietData',
];

interface AuthState {
  // Estado
  isAuthenticated: boolean;
  userId: string | null;
  accessToken: string | null;
  isLoading: boolean;
  isInitialized: boolean;
  
  // Actions
  initialize: () => Promise<void>;
  setAuthenticated: (authenticated: boolean, userId?: string | null, token?: string | null) => void;
  logout: () => Promise<void>;
  checkAuth: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // Estado inicial: NÃO autenticado
  isAuthenticated: false,
  userId: null,
  accessToken: null,
  isLoading: true,
  isInitialized: false,
  
  /**
   * INICIALIZAÇÃO
   * Chamado UMA VEZ no app root para verificar auth
   */
  initialize: async () => {
    console.log('🔐 AUTH: Inicializando...');
    
    try {
      const token = await AsyncStorage.getItem('accessToken');
      const userId = await AsyncStorage.getItem('userId');
      
      if (!token || !userId) {
        console.log('🔐 AUTH: Sem token/userId, não autenticado');
        set({ 
          isAuthenticated: false, 
          userId: null, 
          accessToken: null,
          isLoading: false,
          isInitialized: true 
        });
        return;
      }
      
      // Valida token no backend
      const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
      try {
        const response = await fetch(`${BACKEND_URL}/api/auth/validate`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          console.log('🔐 AUTH: Token válido, usuário autenticado');
          set({ 
            isAuthenticated: true, 
            userId, 
            accessToken: token,
            isLoading: false,
            isInitialized: true 
          });
        } else {
          console.log('🔐 AUTH: Token inválido, limpando...');
          // Token inválido - limpa tudo
          await AsyncStorage.multiRemove(ALL_STORAGE_KEYS);
          set({ 
            isAuthenticated: false, 
            userId: null, 
            accessToken: null,
            isLoading: false,
            isInitialized: true 
          });
        }
      } catch (networkError) {
        // Erro de rede - considera autenticado se tem token local
        console.log('🔐 AUTH: Erro de rede, usando token local');
        set({ 
          isAuthenticated: true, 
          userId, 
          accessToken: token,
          isLoading: false,
          isInitialized: true 
        });
      }
    } catch (error) {
      console.error('🔐 AUTH: Erro na inicialização:', error);
      set({ 
        isAuthenticated: false, 
        userId: null, 
        accessToken: null,
        isLoading: false,
        isInitialized: true 
      });
    }
  },
  
  /**
   * SET AUTHENTICATED
   * Usado após login/signup
   */
  setAuthenticated: (authenticated: boolean, userId?: string | null, token?: string | null) => {
    set({ 
      isAuthenticated: authenticated, 
      userId: userId ?? null,
      accessToken: token ?? null,
    });
  },
  
  /**
   * LOGOUT COMPLETO - HARD RESET
   * Remove TODOS os dados de sessão
   */
  logout: async () => {
    console.log('🔐 LOGOUT: Iniciando HARD RESET...');
    
    // 1. PRIMEIRO: Reset estado Zustand IMEDIATAMENTE
    set({
      isAuthenticated: false,
      userId: null,
      accessToken: null,
      isLoading: false,
    });
    console.log('✅ Estado Zustand resetado');
    
    try {
      // 2. Remove chaves específicas
      await AsyncStorage.multiRemove(ALL_STORAGE_KEYS);
      console.log('✅ Chaves específicas removidas');
      
      // 3. Remove TODAS as chaves restantes
      const allKeys = await AsyncStorage.getAllKeys();
      if (allKeys.length > 0) {
        await AsyncStorage.multiRemove(allKeys);
        console.log(`✅ ${allKeys.length} chaves adicionais removidas`);
      }
      
      // 4. Limpa completamente o AsyncStorage
      await AsyncStorage.clear();
      console.log('✅ AsyncStorage.clear() executado');
      
      // 5. Verifica se realmente limpou
      const remainingKeys = await AsyncStorage.getAllKeys();
      console.log('🔐 LOGOUT: Chaves restantes:', remainingKeys.length);
      
      if (remainingKeys.length > 0) {
        console.warn('⚠️ Ainda há chaves:', remainingKeys);
        // Força remoção individual
        for (const key of remainingKeys) {
          await AsyncStorage.removeItem(key);
        }
      }
      
      console.log('🔐 LOGOUT: COMPLETO!');
    } catch (error) {
      console.error('❌ Erro no logout:', error);
      // Mesmo com erro, estado já foi resetado
    }
  },
  
  /**
   * CHECK AUTH
   * Verifica se ainda está autenticado
   */
  checkAuth: async () => {
    const token = await AsyncStorage.getItem('accessToken');
    const userId = await AsyncStorage.getItem('userId');
    
    const isAuth = !!(token && userId);
    
    if (!isAuth) {
      set({
        isAuthenticated: false,
        userId: null,
        accessToken: null,
      });
    }
    
    return isAuth;
  },
}));
