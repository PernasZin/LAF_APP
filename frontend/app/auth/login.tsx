/**
 * LAF Premium Login Screen
 * ========================
 * Glassmorphism + Gradientes + Animações
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, 
  KeyboardAvoidingView, Platform, ScrollView, Alert, Keyboard
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { 
  FadeInDown, FadeInUp, useSharedValue, 
  useAnimatedStyle, withSpring 
} from 'react-native-reanimated';
import { Mail, Lock, Eye, EyeOff, LogIn, UserPlus, Sparkles } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing, animations } from '../../theme/premium';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function LoginScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  
  const buttonScale = useSharedValue(1);
  
  const animatedButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const handleLogin = async () => {
    Keyboard.dismiss();
    
    if (!email || !password) {
      Alert.alert('Campos obrigatórios', 'Por favor, preencha email e senha.');
      return;
    }

    buttonScale.value = withSpring(0.95, animations.spring.snappy);
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });

      const data = await response.json();

      if (response.ok && data.user_id) {
        await AsyncStorage.setItem('userId', data.user_id);
        await AsyncStorage.setItem('userEmail', email.trim().toLowerCase());
        
        if (data.has_profile) {
          router.replace('/(tabs)');
        } else {
          router.replace('/onboarding');
        }
      } else {
        Alert.alert('Erro', data.message || 'Email ou senha incorretos');
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setIsLoading(false);
      buttonScale.value = withSpring(1, animations.spring.gentle);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Background Gradient */}
      <LinearGradient
        colors={isDark 
          ? ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.08)']
          : ['rgba(16, 185, 129, 0.12)', 'transparent', 'rgba(59, 130, 246, 0.12)']
        }
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />
      
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView 
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {/* Logo/Brand Section */}
            <Animated.View entering={FadeInDown.springify()} style={styles.brandSection}>
              <View style={styles.logoContainer}>
                <LinearGradient
                  colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.logoGradient}
                >
                  <Sparkles size={36} color="#FFF" strokeWidth={2} />
                </LinearGradient>
              </View>
              <Text style={[styles.brandTitle, { color: theme.text }]}>LAF</Text>
              <Text style={[styles.brandSubtitle, { color: theme.textSecondary }]}>
                Seu assistente de nutrição inteligente
              </Text>
            </Animated.View>

            {/* Form Card */}
            <Animated.View 
              entering={FadeInUp.delay(200).springify()} 
              style={[styles.formCard, { 
                backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.85)',
                borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
              }]}
            >
              <Text style={[styles.formTitle, { color: theme.text }]}>Entrar</Text>
              <Text style={[styles.formSubtitle, { color: theme.textSecondary }]}>
                Bem-vindo de volta! Entre para continuar.
              </Text>

              {/* Email Input */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>Email</Text>
                <View style={[
                  styles.inputContainer,
                  { 
                    backgroundColor: theme.input.background,
                    borderColor: emailFocused ? premiumColors.primary : theme.input.border,
                  }
                ]}>
                  <Mail size={20} color={emailFocused ? premiumColors.primary : theme.textTertiary} />
                  <TextInput
                    style={[styles.input, { color: theme.text }]}
                    placeholder="seu@email.com"
                    placeholderTextColor={theme.input.placeholder}
                    value={email}
                    onChangeText={setEmail}
                    onFocus={() => setEmailFocused(true)}
                    onBlur={() => setEmailFocused(false)}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoComplete="email"
                  />
                </View>
              </View>

              {/* Password Input */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>Senha</Text>
                <View style={[
                  styles.inputContainer,
                  { 
                    backgroundColor: theme.input.background,
                    borderColor: passwordFocused ? premiumColors.primary : theme.input.border,
                  }
                ]}>
                  <Lock size={20} color={passwordFocused ? premiumColors.primary : theme.textTertiary} />
                  <TextInput
                    style={[styles.input, { color: theme.text }]}
                    placeholder="••••••••"
                    placeholderTextColor={theme.input.placeholder}
                    value={password}
                    onChangeText={setPassword}
                    onFocus={() => setPasswordFocused(true)}
                    onBlur={() => setPasswordFocused(false)}
                    secureTextEntry={!showPassword}
                    autoComplete="password"
                  />
                  <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                    {showPassword 
                      ? <EyeOff size={20} color={theme.textTertiary} />
                      : <Eye size={20} color={theme.textTertiary} />
                    }
                  </TouchableOpacity>
                </View>
              </View>

              {/* Login Button */}
              <Animated.View style={[styles.buttonContainer, animatedButtonStyle]}>
                <TouchableOpacity 
                  onPress={handleLogin} 
                  disabled={isLoading}
                  activeOpacity={0.9}
                >
                  <LinearGradient
                    colors={isLoading 
                      ? ['#9CA3AF', '#6B7280']
                      : [premiumColors.gradient.start, premiumColors.gradient.middle, premiumColors.gradient.end]
                    }
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.loginButton}
                  >
                    <LogIn size={20} color="#FFF" />
                    <Text style={styles.loginButtonText}>
                      {isLoading ? 'Entrando...' : 'Entrar'}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            </Animated.View>

            {/* Sign Up Link */}
            <Animated.View entering={FadeInUp.delay(400).springify()} style={styles.signUpSection}>
              <Text style={[styles.signUpText, { color: theme.textSecondary }]}>
                Não tem uma conta?
              </Text>
              <TouchableOpacity 
                onPress={() => router.push('/auth/signup')}
                style={styles.signUpButton}
              >
                <UserPlus size={18} color={premiumColors.primary} />
                <Text style={[styles.signUpLink, { color: premiumColors.primary }]}>
                  Criar conta
                </Text>
              </TouchableOpacity>
            </Animated.View>
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  keyboardView: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.xl,
  },
  
  // Brand Section
  brandSection: {
    alignItems: 'center',
    marginBottom: spacing['2xl'],
  },
  logoContainer: {
    marginBottom: spacing.lg,
  },
  logoGradient: {
    width: 80,
    height: 80,
    borderRadius: radius['2xl'],
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: premiumColors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 12,
  },
  brandTitle: {
    fontSize: 42,
    fontWeight: '800',
    letterSpacing: -1.5,
  },
  brandSubtitle: {
    fontSize: 15,
    marginTop: spacing.xs,
    fontWeight: '500',
  },
  
  // Form Card
  formCard: {
    borderRadius: radius['2xl'],
    padding: spacing.xl,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 12,
  },
  formTitle: {
    fontSize: 26,
    fontWeight: '700',
    letterSpacing: -0.5,
    marginBottom: spacing.xs,
  },
  formSubtitle: {
    fontSize: 14,
    marginBottom: spacing.xl,
  },
  
  // Input
  inputGroup: {
    marginBottom: spacing.lg,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: '600',
    marginBottom: spacing.sm,
    letterSpacing: 0.3,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 56,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    paddingHorizontal: spacing.base,
    gap: spacing.md,
  },
  input: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
  },
  
  // Button
  buttonContainer: {
    marginTop: spacing.md,
  },
  loginButton: {
    height: 56,
    borderRadius: radius.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    shadowColor: premiumColors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  loginButtonText: {
    color: '#FFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  
  // Sign Up
  signUpSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.xl,
    gap: spacing.sm,
  },
  signUpText: {
    fontSize: 15,
  },
  signUpButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  signUpLink: {
    fontSize: 15,
    fontWeight: '700',
  },
});
