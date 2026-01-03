import React, { useEffect } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { useAuthStore } from '../stores/authStore';

/**
 * ROOT AUTH GUARD
 * SINGLE SOURCE OF TRUTH: AuthStore
 * 
 * LOGIC:
 * if (!isAuthenticated) → /auth/login
 * else if (!profileCompleted) → /onboarding
 * else → /(tabs)
 */
function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const segments = useSegments();
  const navigationState = useRootNavigationState();
  
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const profileCompleted = useAuthStore((s) => s.profileCompleted);
  const isInitialized = useAuthStore((s) => s.isInitialized);
  const initialize = useAuthStore((s) => s.initialize);

  // Initialize once
  useEffect(() => {
    initialize();
  }, []);

  // Redirect based on auth state
  useEffect(() => {
    if (!navigationState?.key || !isInitialized) return;

    const inAuth = segments[0] === 'auth';
    const inOnboarding = segments[0] === 'onboarding';
    const inTabs = segments[0] === '(tabs)';

    console.log('🛡️ GUARD:', { isAuthenticated, profileCompleted, segments: segments[0] });

    // NOT authenticated → go to login
    if (!isAuthenticated) {
      if (!inAuth) {
        console.log('🛡️ → /auth/login');
        router.replace('/auth/login');
      }
      return;
    }

    // Authenticated but NO profile → go to onboarding
    if (!profileCompleted) {
      if (!inOnboarding) {
        console.log('🛡️ → /onboarding');
        router.replace('/onboarding');
      }
      return;
    }

    // Authenticated WITH profile → go to tabs
    if (inAuth || inOnboarding || segments.length === 0) {
      console.log('🛡️ → /(tabs)');
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, profileCompleted, isInitialized, segments, navigationState?.key]);

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
          <RootStack />
        </AuthGuard>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
});
