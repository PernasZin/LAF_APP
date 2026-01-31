import React, { useEffect } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { useAuthStore } from '../stores/authStore';
import { useSubscriptionStore } from '../stores/subscriptionStore';
import { config } from '../config';

const BACKEND_URL = config.BACKEND_URL;

/**
 * ROOT AUTH GUARD
 * SINGLE SOURCE OF TRUTH: AuthStore + SubscriptionStore
 * 
 * LOGIC:
 * 1. If on index (root) → allow (language selection)
 * 2. if (!isAuthenticated) → /auth/login
 * 3. else if (!profileCompleted) → /onboarding
 * 4. else → Verifica status premium no backend
 * 5. else if (subscriptionExpired) → /paywall (assinatura expirou após período de graça)
 * 6. else if (!hasSeenPaywall && !isPremium) → /paywall
 * 7. else → /(tabs) - usuário premium vai direto para o app
 */
function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const segments = useSegments();
  const navigationState = useRootNavigationState();
  
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const userId = useAuthStore((s) => s.userId);
  const profileCompleted = useAuthStore((s) => s.profileCompleted);
  const isInitialized = useAuthStore((s) => s.isInitialized);
  const initialize = useAuthStore((s) => s.initialize);

  const hasSeenPaywall = useSubscriptionStore((s) => s.hasSeenPaywall);
  const isPremium = useSubscriptionStore((s) => s.isPremium);
  const checkSubscriptionStatus = useSubscriptionStore((s) => s.checkSubscriptionStatus);
  const setHasSeenPaywall = useSubscriptionStore((s) => s.setHasSeenPaywall);
  const initializeSubscription = useSubscriptionStore((s) => s.initialize);
  const syncWithBackend = useSubscriptionStore((s) => s.syncWithBackend);
  const activateSubscription = useSubscriptionStore((s) => s.activateSubscription);

  // Initialize once
  useEffect(() => {
    initialize();
    initializeSubscription();
  }, []);

  // Sincronizar com backend quando o usuário está autenticado
  useEffect(() => {
    const checkPremiumStatus = async () => {
      if (isAuthenticated && userId && profileCompleted) {
        try {
          console.log('🔄 Verificando status premium no backend para:', userId);
          const response = await fetch(`${BACKEND_URL}/api/user/premium/${userId}`);
          
          if (response.ok) {
            const data = await response.json();
            console.log('📦 Status premium do backend:', data);
            
            if (data.is_premium) {
              // Usuário já tem assinatura ativa - ativar localmente
              const planType = data.current_plan || 'monthly';
              activateSubscription(planType);
              setHasSeenPaywall(true);
              console.log('✅ Usuário é premium! Ativando assinatura local.');
            }
          }
        } catch (error) {
          console.error('❌ Erro ao verificar status premium:', error);
        }
      }
    };

    checkPremiumStatus();
  }, [isAuthenticated, userId, profileCompleted]);

  // Redirect based on auth state
  useEffect(() => {
    if (!navigationState?.key || !isInitialized) return;

    const currentSegment = segments[0];
    const inAuth = currentSegment === 'auth';
    const inOnboarding = currentSegment === 'onboarding';
    const inPaywall = currentSegment === 'paywall';
    const inTabs = currentSegment === '(tabs)';
    const inLegal = currentSegment === 'legal';
    const inSettings = currentSegment === 'settings';
    const inSubscription = currentSegment === 'subscription';
    const isRootIndex = segments.length === 0 || currentSegment === 'index';

    // Verificar status da assinatura
    const subscriptionStatus = checkSubscriptionStatus();
    const subscriptionExpired = subscriptionStatus === 'expired';
    
    console.log('🛡️ GUARD:', { 
      isAuthenticated, 
      profileCompleted, 
      hasSeenPaywall, 
      isPremium: isPremium(), 
      subscriptionStatus,
      subscriptionExpired,
      segments: currentSegment, 
      isRootIndex 
    });

    // ALLOW index screen to handle language selection first
    if (isRootIndex) {
      console.log('🛡️ → Allowing index screen');
      return;
    }

    // ALLOW legal pages (terms, privacy) without authentication
    if (inLegal) {
      console.log('🛡️ → Allowing legal page');
      return;
    }

    // NOT authenticated → go to login
    if (!isAuthenticated) {
      if (!inAuth) {
        console.log('🛡️ → /auth/login');
        router.replace('/auth/login');
      }
      return;
    }

    // ============ NOVO FLUXO: PREMIUM OBRIGATÓRIO ============
    // Authenticated but NOT premium → MUST go to paywall (cannot skip)
    if (!isPremium()) {
      if (!inPaywall) {
        console.log('🛡️ → /paywall (premium obrigatório)');
        router.replace('/paywall');
      }
      return;
    }

    // Premium but NO profile → go to onboarding
    if (!profileCompleted) {
      if (!inOnboarding) {
        console.log('🛡️ → /onboarding (premium, criar perfil)');
        router.replace('/onboarding');
      }
      return;
    }

    // ALLOW settings and subscription pages for premium users with profile
    if (inSettings || inSubscription) {
      console.log('🛡️ → Allowing settings/subscription page');
      return;
    }

    // Premium WITH profile → go to tabs
    if (inAuth || inOnboarding || inPaywall) {
      console.log('🛡️ → /(tabs) - premium com perfil');
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, profileCompleted, isInitialized, hasSeenPaywall, segments, navigationState?.key]);

  if (!isInitialized) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#10B981" />
      </View>
    );
  }

  return <>{children}</>;
}

function RootStack() {
  const { colors } = useTheme();
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="auth" />
      <Stack.Screen name="onboarding" />
      <Stack.Screen name="paywall" />
      <Stack.Screen name="(tabs)" />
      <Stack.Screen name="settings" />
      <Stack.Screen name="legal" />
    </Stack>
  );
}

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthGuard>
          <RootStack />
        </AuthGuard>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
});
