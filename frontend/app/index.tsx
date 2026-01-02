import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, Pressable, ActivityIndicator, Platform, BackHandler } from 'react-native';
import { useRouter, Redirect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '../stores/authStore';

export default function WelcomeScreen() {
  const router = useRouter();
  const [isNavigating, setIsNavigating] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [shouldRedirectToTabs, setShouldRedirectToTabs] = useState(false);
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
      // Se não está autenticado, bloqueia voltar
      if (!isAuthenticated) {
        return true; // Bloqueia
      }
      return false; // Permite
    });

    return () => backHandler.remove();
  }, [isAuthenticated]);

  const checkAndNavigate = async () => {
    try {
      console.log('🏠 Starting welcome check...');
      
      // Usa AuthStore para validar sessão
      const isValid = await validateSession();
      
      console.log('🏠 Session validation result:', { isValid, platform: Platform.OS });
      
      if (isValid) {
        console.log('✅ User has valid session, setting redirect flag...');
        setShouldRedirectToTabs(true);
      } else {
        console.log('❌ No valid session, showing welcome screen');
      }
    } catch (error) {
      console.error('❌ Check error:', error);
      // Se erro, não redireciona - mostra tela de boas-vindas
    } finally {
      console.log('✅ Check complete, hiding loading...');
      setIsChecking(false);
    }
  };

  // Handle redirect using Redirect component (works better on web)
  if (shouldRedirectToTabs && !isChecking) {
    console.log('🚀 Redirecting to tabs via Redirect component...');
    return <Redirect href="/(tabs)" />;
  }

  const handleStartPress = () => {
    if (isNavigating) return;
    
    console.log('🚀 Starting onboarding...');
    setIsNavigating(true);
    
    router.push('/onboarding');
  };

  // Brief loading state
  if (isChecking) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingLogo}>LAF</Text>
          <ActivityIndicator size="large" color="#10B981" style={{ marginTop: 20 }} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Logo/Icon */}
        <View style={styles.iconContainer}>
          <Ionicons name="fitness" size={100} color="#10B981" />
        </View>

        {/* Title */}
        <Text style={styles.title}>LAF</Text>
        <Text style={styles.subtitle}>Seu Treinador Pessoal Inteligente</Text>

        {/* Features */}
        <View style={styles.featuresContainer}>
          <FeatureItem 
            icon="nutrition" 
            text="Dieta personalizada com IA"
          />
          <FeatureItem 
            icon="barbell" 
            text="Treinos sob medida para você"
          />
          <FeatureItem 
            icon="trending-up" 
            text="Acompanhe seu progresso"
          />
        </View>

        {/* CTA Button - Using Pressable for better cross-platform support */}
        <Pressable 
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
            isNavigating && styles.buttonDisabled,
          ]}
          onPress={handleStartPress}
          disabled={isNavigating}
        >
          {isNavigating ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <>
              <Text style={styles.buttonText}>Começar Agora</Text>
              <Ionicons name="arrow-forward" size={20} color="#fff" />
            </>
          )}
        </Pressable>

        <Text style={styles.footerText}>
          Planos personalizados para seus objetivos
        </Text>
      </View>
    </SafeAreaView>
  );
}

function FeatureItem({ icon, text }: { icon: any; text: string }) {
  return (
    <View style={styles.featureItem}>
      <View style={styles.featureIcon}>
        <Ionicons name={icon} size={24} color="#10B981" />
      </View>
      <Text style={styles.featureText}>{text}</Text>
    </View>
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
  loadingLogo: {
    fontSize: 48,
    fontWeight: '700',
    color: '#10B981',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
    justifyContent: 'space-between',
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 48,
    fontWeight: '700',
    color: '#10B981',
    textAlign: 'center',
    letterSpacing: 2,
  },
  subtitle: {
    fontSize: 18,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 48,
  },
  featuresContainer: {
    gap: 24,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  featureIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F0FDF4',
    alignItems: 'center',
    justifyContent: 'center',
  },
  featureText: {
    flex: 1,
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
  },
  button: {
    backgroundColor: '#10B981',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 32,
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
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
    fontWeight: '600',
  },
  footerText: {
    textAlign: 'center',
    color: '#9CA3AF',
    fontSize: 14,
    marginTop: 16,
  },
});