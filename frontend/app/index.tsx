import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Redirect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/authStore';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Tela inicial - Redireciona baseado no estado de auth
 * O AUTH GUARD no _layout.tsx já protege as rotas
 * Esta tela apenas decide para onde ir
 */
export default function IndexScreen() {
  const { isAuthenticated, isInitialized, isLoading } = useAuthStore();
  const [destination, setDestination] = React.useState<'login' | 'tabs' | 'onboarding' | null>(null);

  React.useEffect(() => {
    checkDestination();
  }, [isAuthenticated, isInitialized]);

  const checkDestination = async () => {
    // Aguarda inicialização
    if (!isInitialized || isLoading) return;

    if (!isAuthenticated) {
      // Não autenticado -> Login
      setDestination('login');
      return;
    }

    // Autenticado -> verifica se tem perfil
    const hasProfile = await AsyncStorage.getItem('hasCompletedOnboarding');
    if (hasProfile === 'true') {
      setDestination('tabs');
    } else {
      setDestination('onboarding');
    }
  };

  // Redirect based on destination
  if (destination === 'login') {
    return <Redirect href="/auth/login" />;
  }
  
  if (destination === 'tabs') {
    return <Redirect href="/(tabs)" />;
  }
  
  if (destination === 'onboarding') {
    return <Redirect href="/onboarding" />;
  }

  // Loading state
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Ionicons name="fitness" size={60} color="#10B981" />
        </View>
        <Text style={styles.title}>LAF</Text>
        <ActivityIndicator size="large" color="#10B981" style={{ marginTop: 24 }} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#F0FDF4',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 36,
    fontWeight: '700',
    color: '#10B981',
    letterSpacing: 2,
  },
});
