import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Pressable, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function WelcomeScreen() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isNavigating, setIsNavigating] = useState(false);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      const hasCompleted = await AsyncStorage.getItem('hasCompletedOnboarding');
      const userId = await AsyncStorage.getItem('userId');
      
      console.log('🏠 Welcome: Checking status', { hasCompleted, userId });
      
      if (hasCompleted === 'true' && userId) {
        console.log('✅ Redirecting to home');
        router.replace('/(tabs)');
        return;
      }
    } catch (error) {
      console.error('Error checking status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartPress = () => {
    console.log('🚀 Button pressed - navigating to onboarding');
    setIsNavigating(true);
    
    // Use setTimeout to ensure state update is visible
    setTimeout(() => {
      try {
        router.push('/onboarding');
      } catch (error) {
        console.error('Navigation error:', error);
        setIsNavigating(false);
      }
    }, 100);
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#10B981" />
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