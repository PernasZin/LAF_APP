import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, Pressable, ActivityIndicator, Platform, BackHandler } from 'react-native';
import { useRouter, Redirect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '../stores/authStore';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function WelcomeScreen() {
  const router = useRouter();
  const [isNavigating, setIsNavigating] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [destination, setDestination] = useState<'login' | 'tabs' | 'onboarding' | null>(null);
  const checkDone = useRef(false);
  
  // Auth store
  const { isAuthenticated, validateSession } = useAuthStore();

  useEffect(() => {
    // Prevent double execution
    if (checkDone.current) return;
    checkDone.current = true;
    
    // Safety timeout - never show loading forever
    const safetyTimeout = setTimeout(() => {
      console.log('⏰ Safety timeout - forcing welcome screen');
      setIsChecking(false);
    }, 3000);

    checkAndNavigate().finally(() => {
      clearTimeout(safetyTimeout);
    });
    
    return () => clearTimeout(safetyTimeout);
  }, []);

  // Bloqueia botão voltar na tela de welcome
  useEffect(() => {
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      // Sempre bloqueia voltar na tela inicial
      return true;
    });

    return () => backHandler.remove();
  }, []);

  const checkAndNavigate = async () => {
    try {
      console.log('🏠 Starting auth check...');
      
      // 1. Verifica se tem token
      const token = await AsyncStorage.getItem('accessToken');
      const userId = await AsyncStorage.getItem('userId');
      const hasCompleted = await AsyncStorage.getItem('hasCompletedOnboarding');
      
      console.log('🏠 Auth check:', { hasToken: !!token, userId: !!userId, hasCompleted });
      
      if (!token) {
        // Sem token = vai para login
        console.log('❌ Sem token, indo para login');
        setDestination('login');
        return;
      }
      
      // 2. Valida token no backend
      try {
        const response = await fetch(`${BACKEND_URL}/api/auth/validate`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
          // Token inválido = limpa tudo e vai para login
          console.log('❌ Token inválido, limpando e indo para login');
          await AsyncStorage.multiRemove(['accessToken', 'userId', 'userEmail', 'hasCompletedOnboarding']);
          useAuthStore.setState({ isAuthenticated: false, userId: null });
          setDestination('login');
          return;
        }
        
        const data = await response.json();
        console.log('✅ Token válido:', data);
        
        // Atualiza auth store
        useAuthStore.setState({ isAuthenticated: true, userId: data.user_id });
        
        // 3. Decide destino baseado no estado do perfil
        if (data.has_profile && hasCompleted === 'true') {
          console.log('✅ Usuário com perfil, indo para tabs');
          setDestination('tabs');
        } else {
          console.log('⚠️ Usuário sem perfil, indo para onboarding');
          setDestination('onboarding');
        }
        
      } catch (error) {
        console.error('❌ Erro ao validar token:', error);
        // Erro de rede = assume token válido se tem perfil local
        if (hasCompleted === 'true' && userId) {
          setDestination('tabs');
        } else if (userId) {
          setDestination('onboarding');
        } else {
          setDestination('login');
        }
      }
      
    } catch (error) {
      console.error('❌ Check error:', error);
      setDestination('login');
    } finally {
      console.log('✅ Check complete');
      setIsChecking(false);
    }
  };

  // Redirect based on destination
  if (destination === 'tabs') {
    return <Redirect href="/(tabs)" />;
  }
  
  if (destination === 'onboarding') {
    return <Redirect href="/onboarding" />;
  }
  
  if (destination === 'login') {
    return <Redirect href="/auth/login" />;
  }

  // Loading state
  if (isChecking) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <View style={styles.logoContainer}>
            <Ionicons name="fitness" size={60} color="#10B981" />
          </View>
          <Text style={styles.loadingTitle}>LAF</Text>
          <ActivityIndicator size="large" color="#10B981" style={{ marginTop: 24 }} />
        </View>
      </SafeAreaView>
    );
  }

  // Fallback: Welcome screen (não deveria chegar aqui normalmente)
  const handleGetStarted = () => {
    if (isNavigating) return;
    setIsNavigating(true);
    router.push('/auth/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Logo */}
        <View style={styles.logoSection}>
          <View style={styles.logoContainer}>
            <Ionicons name="fitness" size={80} color="#10B981" />
          </View>
          <Text style={styles.title}>LAF</Text>
          <Text style={styles.subtitle}>Dieta • Treino • Resultados</Text>
        </View>

        {/* Features */}
        <View style={styles.features}>
          <View style={styles.featureItem}>
            <Ionicons name="restaurant" size={24} color="#10B981" />
            <Text style={styles.featureText}>Dieta personalizada com IA</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="barbell" size={24} color="#10B981" />
            <Text style={styles.featureText}>Treinos sob medida</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="analytics" size={24} color="#10B981" />
            <Text style={styles.featureText}>Acompanhe seu progresso</Text>
          </View>
        </View>

        {/* CTA */}
        <Pressable
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
            isNavigating && styles.buttonDisabled,
          ]}
          onPress={handleGetStarted}
          disabled={isNavigating}
        >
          {isNavigating ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Começar</Text>
          )}
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#10B981',
    marginTop: 16,
    letterSpacing: 2,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'space-between',
  },
  logoSection: {
    alignItems: 'center',
    marginTop: 60,
  },
  logoContainer: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#F0FDF4',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 48,
    fontWeight: '700',
    color: '#10B981',
    letterSpacing: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 8,
    letterSpacing: 1,
  },
  features: {
    marginVertical: 40,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0FDF4',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#374151',
    marginLeft: 16,
    fontWeight: '500',
  },
  button: {
    backgroundColor: '#10B981',
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  buttonPressed: {
    backgroundColor: '#059669',
    transform: [{ scale: 0.98 }],
  },
  buttonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
});
