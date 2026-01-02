import React, { useEffect, useState } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { View, ActivityIndicator, Text, StyleSheet, BackHandler } from 'react-native';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { useAuthStore } from '../stores/authStore';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Lista de rotas públicas (não requerem auth)
const PUBLIC_ROUTES = ['auth', 'index'];

/**
 * AUTH GUARD COMPONENT
 * Bloqueia TODAS as rotas privadas se não autenticado
 */
function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const segments = useSegments();
  const navigationState = useRootNavigationState();
  
  const { isAuthenticated, isLoading, isInitialized, initialize } = useAuthStore();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  // Inicializa auth store ao montar
  useEffect(() => {
    console.log('🛡️ AUTH GUARD: Montado');
    initialize().finally(() => {
      setIsCheckingAuth(false);
    });
  }, []);

  // Bloqueia botão voltar em rotas de auth
  useEffect(() => {
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      const inAuthGroup = segments[0] === 'auth';
      const inRoot = segments.length === 0 || segments[0] === 'index';
      
      // Bloqueia voltar se não autenticado ou em telas de auth
      if (!isAuthenticated || inAuthGroup || inRoot) {
        console.log('🛡️ AUTH GUARD: Bloqueando botão voltar');
        return true;
      }
      return false;
    });

    return () => backHandler.remove();
  }, [isAuthenticated, segments]);

  // Redireciona baseado no estado de auth
  useEffect(() => {
    // Espera navegação estar pronta
    if (!navigationState?.key) return;
    
    // Espera inicialização
    if (isCheckingAuth || isLoading || !isInitialized) {
      console.log('🛡️ AUTH GUARD: Aguardando inicialização...');
      return;
    }

    const inAuthGroup = segments[0] === 'auth';
    const inPublicRoute = PUBLIC_ROUTES.includes(segments[0] as string) || segments.length === 0;

    console.log('🛡️ AUTH GUARD: Verificando rota', { 
      segments, 
      isAuthenticated, 
      inAuthGroup, 
      inPublicRoute 
    });

    if (!isAuthenticated) {
      // Não autenticado
      if (!inAuthGroup && !inPublicRoute) {
        // Tentando acessar rota privada - BLOQUEIA
        console.log('🛡️ AUTH GUARD: Bloqueando rota privada, redirecionando para login');
        router.replace('/auth/login');
      }
    } else {
      // Autenticado
      if (inAuthGroup) {
        // Já logado mas em tela de auth - redireciona para home
        console.log('🛡️ AUTH GUARD: Já autenticado, redirecionando para home');
        checkAndRedirect();
      }
    }
  }, [isAuthenticated, segments, navigationState?.key, isCheckingAuth, isLoading, isInitialized]);

  const checkAndRedirect = async () => {
    const hasProfile = await AsyncStorage.getItem('hasCompletedOnboarding');
    if (hasProfile === 'true') {
      router.replace('/(tabs)');
    } else {
      router.replace('/onboarding');
    }
  };

  // Loading state
  if (isCheckingAuth || isLoading || !isInitialized) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Carregando...</Text>
      </View>
    );
  }

  return <>{children}</>;
}

// Inner component that can access theme
function RootStackNavigator() {
  const { colors } = useTheme();
  
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
        animation: 'fade',
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
});
