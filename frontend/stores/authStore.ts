/**
 * Auth Store - Gerenciamento de Autenticação
 * CRÍTICO: Controla estado de sessão e logout completo
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Lista COMPLETA de chaves a limpar no logout
const AUTH_STORAGE_KEYS = [
  'userId',
  'user',
  'userProfile',
  'authToken',
  'accessToken',
  'refreshToken',
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
  isLoading: boolean;
  isHydrated: boolean;
  
  // Actions
  setAuthenticated: (authenticated: boolean, userId?: string | null) => void;
  setUserId: (userId: string | null) => void;
  setHydrated: (hydrated: boolean) => void;
  logout: () => Promise<void>;
  validateSession: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      userId: null,
      isLoading: false,
      isHydrated: false,
      
      setAuthenticated: (authenticated: boolean, userId?: string | null) => {
        set({ 
          isAuthenticated: authenticated, 
          userId: userId !== undefined ? userId : get().userId 
        });
      },
      
      setUserId: (userId: string | null) => {
        set({ userId, isAuthenticated: !!userId });
      },
      
      setHydrated: (hydrated: boolean) => {
        set({ isHydrated: hydrated });
      },
      
      /**
       * LOGOUT COMPLETO
       * Remove TODOS os dados de sessão
       */
      logout: async () => {
        console.log('🔐 LOGOUT: Iniciando limpeza completa...');
        
        try {
          // 1. Reset estado Zustand IMEDIATAMENTE
          set({
            isAuthenticated: false,
            userId: null,
            isLoading: false,
          });
          console.log('✅ Estado Zustand resetado');
          
          // 2. Remove chaves específicas
          await AsyncStorage.multiRemove(AUTH_STORAGE_KEYS);
          console.log('✅ Chaves de autenticação removidas');
          
          // 3. Remove TODAS as chaves (belt and suspenders)
          const allKeys = await AsyncStorage.getAllKeys();
          if (allKeys.length > 0) {
            await AsyncStorage.multiRemove(allKeys);
            console.log(`✅ Todas as ${allKeys.length} chaves removidas`);
          }
          
          // 4. Confirma limpeza
          const remainingKeys = await AsyncStorage.getAllKeys();
          if (remainingKeys.length > 0) {
            console.warn('⚠️ Chaves restantes após logout:', remainingKeys);
            // Força remoção uma a uma
            for (const key of remainingKeys) {
              await AsyncStorage.removeItem(key);
            }
          }
          
          console.log('🔐 LOGOUT: Completo!');
        } catch (error) {
          console.error('❌ Erro no logout:', error);
          // Mesmo com erro, garante estado resetado
          set({
            isAuthenticated: false,
            userId: null,
          });
          throw error;
        }
      },
      
      /**
       * VALIDAÇÃO DE SESSÃO
       * Verifica se usuário ainda tem sessão válida
       */
      validateSession: async () => {
        try {
          const userId = await AsyncStorage.getItem('userId');
          const hasCompleted = await AsyncStorage.getItem('hasCompletedOnboarding');
          
          const isValid = !!(userId && hasCompleted === 'true');
          
          set({
            isAuthenticated: isValid,
            userId: isValid ? userId : null,
          });
          
          console.log('🔐 Sessão validada:', { isValid, userId: isValid ? userId : null });
          
          return isValid;
        } catch (error) {
          console.error('❌ Erro ao validar sessão:', error);
          // Se erro, considera não autenticado
          set({
            isAuthenticated: false,
            userId: null,
          });
          return false;
        }
      },
    }),
    {
      name: 'laf-auth',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        userId: state.userId,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setHydrated(true);
        }
      },
    }
  )
);
