/**
 * Subscription Store - Gerenciamento de Assinatura
 * ================================================
 * Controla estado de trial e assinatura premium
 * Preparado para integração com IAP (In-App Purchases)
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configurações da assinatura
export const SUBSCRIPTION_CONFIG = {
  TRIAL_DAYS: 7,
  MONTHLY_PRICE: 29.90,
  CURRENCY: 'BRL',
  // IDs dos produtos nas lojas (configurar depois)
  PRODUCT_IDS: {
    IOS: 'com.laf.premium.monthly',
    ANDROID: 'laf_premium_monthly',
  },
};

export type SubscriptionStatus = 'none' | 'trial' | 'active' | 'expired' | 'cancelled';

interface SubscriptionState {
  status: SubscriptionStatus;
  trialStartDate: string | null;
  trialEndDate: string | null;
  subscriptionStartDate: string | null;
  subscriptionEndDate: string | null;
  hasSeenPaywall: boolean;
  isInitialized: boolean;

  // Actions
  initialize: () => Promise<void>;
  startTrial: () => Promise<void>;
  activateSubscription: (endDate?: string) => Promise<void>;
  cancelSubscription: () => Promise<void>;
  setHasSeenPaywall: (seen: boolean) => void;
  checkSubscriptionStatus: () => SubscriptionStatus;
  getRemainingTrialDays: () => number;
  isPremium: () => boolean;
  reset: () => void;
}

const initialState = {
  status: 'none' as SubscriptionStatus,
  trialStartDate: null,
  trialEndDate: null,
  subscriptionStartDate: null,
  subscriptionEndDate: null,
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

      activateSubscription: async (endDate?: string) => {
        const now = new Date();
        const subEnd = endDate ? new Date(endDate) : new Date(now);
        if (!endDate) {
          subEnd.setMonth(subEnd.getMonth() + 1); // 1 mês padrão
        }

        set({
          status: 'active',
          subscriptionStartDate: now.toISOString(),
          subscriptionEndDate: subEnd.toISOString(),
        });

        console.log('✅ Subscription activated:', {
          start: now.toISOString(),
          end: subEnd.toISOString(),
        });
      },

      cancelSubscription: async () => {
        set({ status: 'cancelled' });
      },

      setHasSeenPaywall: (seen: boolean) => {
        set({ hasSeenPaywall: seen });
      },

      checkSubscriptionStatus: (): SubscriptionStatus => {
        const state = get();
        const now = new Date();

        // Verifica assinatura ativa
        if (state.subscriptionEndDate) {
          const subEnd = new Date(state.subscriptionEndDate);
          if (now < subEnd) {
            return 'active';
          } else if (state.status === 'active') {
            return 'expired';
          }
        }

        // Verifica trial
        if (state.trialEndDate) {
          const trialEnd = new Date(state.trialEndDate);
          if (now < trialEnd) {
            return 'trial';
          } else if (state.status === 'trial') {
            return 'expired';
          }
        }

        return state.status;
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

      isPremium: (): boolean => {
        const status = get().checkSubscriptionStatus();
        return status === 'trial' || status === 'active';
      },

      reset: () => {
        set(initialState);
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
        hasSeenPaywall: state.hasSeenPaywall,
      }),
    }
  )
);
