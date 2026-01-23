/**
 * Subscription Store - Gerenciamento de Assinatura
 * ================================================
 * Controla estado de trial e assinatura premium
 * Integrado com IAP (In-App Purchases)
 * 
 * LÓGICA DE CANCELAMENTO:
 * - Quando cancelada, a assinatura continua válida até o fim do período pago
 * - Após o período + 3 dias de graça, o app é bloqueado
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configurações da assinatura
export const SUBSCRIPTION_CONFIG = {
  TRIAL_DAYS: 7, // 7 dias de free trial
  GRACE_PERIOD_DAYS: 3, // Dias de graça após expiração
  MONTHLY_PRICE: 29.90, // R$ 29,90/mês
  ANNUAL_PRICE: 199.90, // R$ 199,90/ano
  ANNUAL_MONTHLY_PRICE: 16.66, // R$ 199,90/12 = ~R$ 16,66/mês
  ANNUAL_DISCOUNT: 44, // 44% de desconto no plano anual
  CURRENCY: 'BRL',
  PRODUCT_IDS: {
    MONTHLY: 'com.laf.subscription.monthly',
    ANNUAL: 'com.laf.subscription.annual',
  },
};

export type SubscriptionStatus = 'none' | 'trial' | 'active' | 'cancelled' | 'expired' | 'grace_period';

interface SubscriptionState {
  status: SubscriptionStatus;
  trialStartDate: string | null;
  trialEndDate: string | null;
  subscriptionStartDate: string | null;
  subscriptionEndDate: string | null;
  cancelledAt: string | null; // Data em que foi cancelada
  planType: 'monthly' | 'annual' | null;
  hasSeenPaywall: boolean;
  isInitialized: boolean;

  // Actions
  initialize: () => Promise<void>;
  startTrial: () => Promise<void>;
  activateSubscription: (planType: 'monthly' | 'annual', endDate?: string) => Promise<void>;
  cancelSubscription: () => Promise<void>;
  setHasSeenPaywall: (seen: boolean) => void;
  setPremiumStatus: (isPremium: boolean) => void;
  checkSubscriptionStatus: () => SubscriptionStatus;
  getRemainingTrialDays: () => number;
  getRemainingDays: () => number;
  isPremium: () => boolean;
  isInGracePeriod: () => boolean;
  reset: () => void;
  syncWithBackend: (userId: string, backendUrl: string) => Promise<void>;
}

const initialState = {
  status: 'none' as SubscriptionStatus,
  trialStartDate: null,
  trialEndDate: null,
  subscriptionStartDate: null,
  subscriptionEndDate: null,
  cancelledAt: null,
  planType: null as 'monthly' | 'annual' | null,
  hasSeenPaywall: false,
  isInitialized: false,
};

export const useSubscriptionStore = create<SubscriptionState>()(
  persist(
    (set, get) => ({
      ...initialState,

      initialize: async () => {
        const state = get();
        if (state.isInitialized) return;

        // Verifica e atualiza o status baseado nas datas
        const newStatus = get().checkSubscriptionStatus();
        set({ status: newStatus, isInitialized: true });
      },

      startTrial: async () => {
        const now = new Date();
        const trialEnd = new Date(now);
        trialEnd.setDate(trialEnd.getDate() + SUBSCRIPTION_CONFIG.TRIAL_DAYS);

        set({
          status: 'trial',
          trialStartDate: now.toISOString(),
          trialEndDate: trialEnd.toISOString(),
        });

        console.log('🎉 Trial started:', {
          start: now.toISOString(),
          end: trialEnd.toISOString(),
        });
      },

      activateSubscription: async (planType: 'monthly' | 'annual', endDate?: string) => {
        const now = new Date();
        let subEnd: Date;
        
        if (endDate) {
          subEnd = new Date(endDate);
        } else {
          subEnd = new Date(now);
          if (planType === 'monthly') {
            subEnd.setMonth(subEnd.getMonth() + 1);
          } else {
            subEnd.setFullYear(subEnd.getFullYear() + 1);
          }
        }

        set({
          status: 'active',
          subscriptionStartDate: now.toISOString(),
          subscriptionEndDate: subEnd.toISOString(),
          cancelledAt: null,
          planType,
          hasSeenPaywall: true,
        });

        console.log('✅ Subscription activated:', {
          planType,
          start: now.toISOString(),
          end: subEnd.toISOString(),
        });
      },

      cancelSubscription: async () => {
        const now = new Date();
        set({ 
          status: 'cancelled',
          cancelledAt: now.toISOString(),
        });
        console.log('❌ Subscription cancelled at:', now.toISOString());
      },

      setHasSeenPaywall: (seen: boolean) => {
        set({ hasSeenPaywall: seen });
      },

      setPremiumStatus: (isPremium: boolean) => {
        if (isPremium) {
          // Ativar premium - se não tem data de término, define 1 mês
          const state = get();
          if (!state.subscriptionEndDate) {
            const now = new Date();
            const subEnd = new Date(now);
            subEnd.setMonth(subEnd.getMonth() + 1);
            
            set({
              status: 'active',
              subscriptionStartDate: now.toISOString(),
              subscriptionEndDate: subEnd.toISOString(),
              cancelledAt: null,
              hasSeenPaywall: true,
            });
          } else {
            set({ 
              status: 'active',
              cancelledAt: null,
              hasSeenPaywall: true,
            });
          }
        } else {
          // Remover premium
          set({ 
            status: 'expired',
            hasSeenPaywall: false,
          });
        }
      },

      checkSubscriptionStatus: (): SubscriptionStatus => {
        const state = get();
        const now = new Date();

        // Verifica assinatura
        if (state.subscriptionEndDate) {
          const subEnd = new Date(state.subscriptionEndDate);
          const gracePeriodEnd = new Date(subEnd);
          gracePeriodEnd.setDate(gracePeriodEnd.getDate() + SUBSCRIPTION_CONFIG.GRACE_PERIOD_DAYS);

          // Assinatura ativa (não expirou)
          if (now < subEnd) {
            // Se foi cancelada mas ainda está no período pago
            if (state.cancelledAt) {
              return 'cancelled'; // Mostra como cancelada mas ainda funciona
            }
            return 'active';
          }
          
          // Dentro do período de graça (3 dias após expiração)
          if (now < gracePeriodEnd) {
            return 'grace_period';
          }
          
          // Expirou completamente (passou os 3 dias de graça)
          return 'expired';
        }

        // Verifica trial
        if (state.trialEndDate) {
          const trialEnd = new Date(state.trialEndDate);
          if (now < trialEnd) {
            return 'trial';
          }
          return 'expired';
        }

        return state.status || 'none';
      },

      getRemainingTrialDays: (): number => {
        const state = get();
        if (!state.trialEndDate) return 0;

        const now = new Date();
        const trialEnd = new Date(state.trialEndDate);
        const diffTime = trialEnd.getTime() - now.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        return Math.max(0, diffDays);
      },

      getRemainingDays: (): number => {
        const state = get();
        const now = new Date();
        
        // Verifica assinatura
        if (state.subscriptionEndDate) {
          const subEnd = new Date(state.subscriptionEndDate);
          const gracePeriodEnd = new Date(subEnd);
          gracePeriodEnd.setDate(gracePeriodEnd.getDate() + SUBSCRIPTION_CONFIG.GRACE_PERIOD_DAYS);
          
          const diffTime = gracePeriodEnd.getTime() - now.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          return Math.max(0, diffDays);
        }
        
        // Verifica trial
        if (state.trialEndDate) {
          const trialEnd = new Date(state.trialEndDate);
          const diffTime = trialEnd.getTime() - now.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          return Math.max(0, diffDays);
        }
        
        return 0;
      },

      isPremium: (): boolean => {
        const status = get().checkSubscriptionStatus();
        // Premium se está em trial, ativo, cancelado (mas ainda no período) ou período de graça
        return status === 'trial' || status === 'active' || status === 'cancelled' || status === 'grace_period';
      },

      isInGracePeriod: (): boolean => {
        const status = get().checkSubscriptionStatus();
        return status === 'grace_period';
      },

      reset: () => {
        set(initialState);
      },

      syncWithBackend: async (userId: string, backendUrl: string) => {
        try {
          const response = await fetch(`${backendUrl}/api/user/premium/${userId}`);
          if (response.ok) {
            const data = await response.json();
            
            if (data.is_premium) {
              set({
                status: data.subscription_status === 'cancelled' ? 'cancelled' : 'active',
                subscriptionEndDate: data.subscription_end_date || null,
                cancelledAt: data.cancelled_at || null,
                hasSeenPaywall: true,
              });
            } else {
              // Verifica se expirou
              const currentStatus = get().checkSubscriptionStatus();
              if (currentStatus === 'expired') {
                set({ 
                  status: 'expired',
                  hasSeenPaywall: false,
                });
              }
            }
          }
        } catch (error) {
          console.error('Failed to sync subscription with backend:', error);
        }
      },
    }),
    {
      name: 'laf-subscription',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        status: state.status,
        trialStartDate: state.trialStartDate,
        trialEndDate: state.trialEndDate,
        subscriptionStartDate: state.subscriptionStartDate,
        subscriptionEndDate: state.subscriptionEndDate,
        cancelledAt: state.cancelledAt,
        planType: state.planType,
        hasSeenPaywall: state.hasSeenPaywall,
      }),
    }
  )
);
