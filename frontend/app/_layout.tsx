import React, { useEffect, useState } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { useAuthStore } from '../stores/authStore';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * AUTH GUARD - Reage a mudanças no estado de auth
 */
function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const segments = useSegments();
  const navigationState = useRootNavigationState();
  
  // Subscreve ao estado do AuthStore
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  const initialize = useAuthStore((state) => state.initialize);

  // Inicializa UMA vez
  useEffect(() => {
    console.log('🛡️ AUTH GUARD: Inicializando...');
    initialize();
  }, []);

  // Redireciona baseado no estado - reage a mudanças em isAuthenticated
  useEffect(() => {
    // Espera navegação e auth estarem prontos
    if (!navigationState?.key || !isInitialized) {
      console.log('🛡️ AUTH GUARD: Aguardando...', { navReady: !!navigationState?.key, authReady: isInitialized });
      return;
    }

    const inAuthGroup = segments[0] === 'auth';
    const inTabs = segments[0] === '(tabs)';
    const inOnboarding = segments[0] === 'onboarding';
    const inIndex = segments.length === 0 || segments[0] === 'index';

    console.log('🛡️ AUTH GUARD: Verificando', { 
      isAuthenticated, 
      segments: segments.join('/'), 
      inAuthGroup, 
      inTabs,
      inOnboarding 
    });

    // Não autenticado tentando acessar área protegida
    if (!isAuthenticated && (inTabs || inOnboarding)) {
      console.log('🛡️ AUTH GUARD: Bloqueando acesso, redirecionando para login');
      router.replace('/auth/login');
      return;
    }

    // Autenticado na área de auth ou index - redireciona para app
    if (isAuthenticated && (inAuthGroup || inIndex)) {
      console.log('🛡️ AUTH GUARD: Autenticado, verificando perfil...');
      AsyncStorage.getItem('hasCompletedOnboarding').then(hasProfile => {
        console.log('🛡️ AUTH GUARD: hasProfile:', hasProfile);
        if (hasProfile === 'true') {
          console.log('🛡️ AUTH GUARD: Redirecionando para tabs');
          router.replace('/(tabs)');
        } else {
          console.log('🛡️ AUTH GUARD: Redirecionando para onboarding');
          router.replace('/onboarding');
        }
      });
    }
  }, [isAuthenticated, isInitialized, segments, navigationState?.key]);

  // Loading enquanto não inicializa
  if (!isInitialized) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#10B981" />
      </View>
    );
  }

  return <>{children}</>;
}

function RootStackNavigator() {
  const { colors } = useTheme();
  
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen name="index" />
      <Stack.Screen name="auth" />
      <Stack.Screen name="onboarding" />
      <Stack.Screen name="(tabs)" />
      <Stack.Screen name="settings" />
    </Stack>
  );
}

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthGuard>
          <RootStackNavigator />
        </AuthGuard>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});
