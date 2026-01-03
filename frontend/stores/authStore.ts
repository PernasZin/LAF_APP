/**
 * Auth Store - Gerenciamento de Autenticação
 * CRÍTICO: Controla estado de sessão e logout completo
 * 
 * SOLUÇÃO: Estado em memória SEM persistência automática
 * O logout limpa TUDO e força estado false
 */
import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Flag global para bloquear re-autenticação após logout
let LOGOUT_IN_PROGRESS = false;
let LOGOUT_COMPLETED = false;

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  accessToken: string | null;
  isLoading: boolean;
  isInitialized: boolean;
  
  initialize: () => Promise<void>;
  setAuth: (userId: string, token: string) => Promise<void>;
  logout: () => Promise<void>;
  forceLogout: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isAuthenticated: false,
  userId: null,
  accessToken: null,
  isLoading: true,
  isInitialized: false,
  
  /**
   * INICIALIZAÇÃO - Chamada UMA VEZ ao abrir app
   */
  initialize: async () => {
    // Se logout foi completado, não re-autentica
    if (LOGOUT_COMPLETED) {
      console.log('🔐 AUTH: Logout recente, mantendo deslogado');
      set({ 
        isAuthenticated: false, 
        userId: null, 
        accessToken: null,
        isLoading: false,
        isInitialized: true 
      });
      return;
    }

    console.log('🔐 AUTH: Inicializando...');
    
    try {
      const token = await AsyncStorage.getItem('accessToken');
      const userId = await AsyncStorage.getItem('userId');
      
      console.log('🔐 AUTH: Dados encontrados:', { hasToken: !!token, hasUserId: !!userId });
      
      if (!token || !userId) {
        set({ 
          isAuthenticated: false, 
          userId: null, 
          accessToken: null,
          isLoading: false,
          isInitialized: true 
        });
        return;
      }
      
      // Token existe - considera autenticado
      set({ 
        isAuthenticated: true, 
        userId, 
        accessToken: token,
        isLoading: false,
        isInitialized: true 
      });
      
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
   * SET AUTH - Após login/signup bem sucedido
   */
  setAuth: async (userId: string, token: string) => {
    LOGOUT_COMPLETED = false; // Reset flag de logout
    
    await AsyncStorage.setItem('accessToken', token);
    await AsyncStorage.setItem('userId', userId);
    
    set({ 
      isAuthenticated: true, 
      userId, 
      accessToken: token,
    });
    
    console.log('🔐 AUTH: Autenticado:', userId);
  },
  
  /**
   * LOGOUT - HARD RESET COMPLETO
   */
  logout: async () => {
    if (LOGOUT_IN_PROGRESS) {
      console.log('🔐 LOGOUT: Já em progresso, ignorando...');
      return;
    }
    
    LOGOUT_IN_PROGRESS = true;
    console.log('🔐 LOGOUT: ========== INICIANDO HARD RESET ==========');
    
    // 1. PRIMEIRO: Reset estado IMEDIATO
    set({
      isAuthenticated: false,
      userId: null,
      accessToken: null,
      isLoading: false,
    });
    console.log('🔐 LOGOUT: Estado Zustand resetado');
    
    try {
      // 2. Lista todas as chaves
      const allKeys = await AsyncStorage.getAllKeys();
      console.log('🔐 LOGOUT: Chaves encontradas:', allKeys.length, allKeys);
      
      // 3. Remove todas as chaves
      if (allKeys.length > 0) {
        await AsyncStorage.multiRemove(allKeys);
        console.log('🔐 LOGOUT: multiRemove executado');
      }
      
      // 4. Clear completo
      await AsyncStorage.clear();
      console.log('🔐 LOGOUT: clear() executado');
      
      // 5. Verifica se limpou
      const remaining = await AsyncStorage.getAllKeys();
      console.log('🔐 LOGOUT: Chaves restantes:', remaining.length);
      
      // 6. Se ainda tem chaves, remove uma a uma
      if (remaining.length > 0) {
        for (const key of remaining) {
          try {
            await AsyncStorage.removeItem(key);
          } catch (e) {
            console.warn('🔐 LOGOUT: Erro ao remover', key);
          }
        }
      }
      
      // 7. Marca logout como completo
      LOGOUT_COMPLETED = true;
      
      console.log('🔐 LOGOUT: ========== COMPLETO ==========');
      
    } catch (error) {
      console.error('🔐 LOGOUT: Erro:', error);
      LOGOUT_COMPLETED = true; // Mesmo com erro, marca como completo
    } finally {
      LOGOUT_IN_PROGRESS = false;
    }
  },
  
  /**
   * FORCE LOGOUT - Logout síncrono imediato
   */
  forceLogout: () => {
    LOGOUT_COMPLETED = true;
    set({
      isAuthenticated: false,
      userId: null,
      accessToken: null,
      isLoading: false,
    });
  },
}));

// Reset flag quando módulo é carregado
LOGOUT_COMPLETED = false;
