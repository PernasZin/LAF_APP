/**
 * LAF Premium Signup Screen
 * ==========================
 * Glassmorphism + Gradientes + Animações
 */

import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ScrollView, Alert, Keyboard
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
import { Mail, Lock, Eye, EyeOff, UserPlus, ArrowLeft, User, Sparkles } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing, animations } from '../../theme/premium';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Input Field Component - OUTSIDE main component to prevent re-renders
const InputField = ({ 
  icon: Icon, 
  label, 
  value, 
  onChangeText, 
  placeholder, 
  secureTextEntry, 
  field, 
  showToggle,
  showPassword,
  setShowPassword,
  focusedField,
  setFocusedField,
  theme,
  isDark
}: any) => (
  <View style={inputStyles.inputGroup}>
    <Text style={[inputStyles.inputLabel, { color: theme.textSecondary }]}>{label}</Text>
    <View style={[
      inputStyles.inputContainer,
      {
        backgroundColor: theme.input.background,
        borderColor: focusedField === field ? premiumColors.primary : theme.input.border,
      }
    ]}>
      <Icon size={20} color={focusedField === field ? premiumColors.primary : theme.textTertiary} />
      <TextInput
        style={[inputStyles.input, { color: theme.text }]}
        placeholder={placeholder}
        placeholderTextColor={theme.input.placeholder}
        value={value}
        onChangeText={onChangeText}
        onFocus={() => setFocusedField(field)}
        onBlur={() => setFocusedField(null)}
        secureTextEntry={secureTextEntry && !showPassword}
        autoCapitalize={field === 'email' ? 'none' : field === 'name' ? 'words' : 'none'}
        keyboardType={field === 'email' ? 'email-address' : 'default'}
        autoCorrect={false}
      />
      {showToggle && (
        <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
          {showPassword ? <EyeOff size={20} color={theme.textTertiary} /> : <Eye size={20} color={theme.textTertiary} />}
        </TouchableOpacity>
      )}
    </View>
  </View>
);

const inputStyles = StyleSheet.create({
  inputGroup: { marginBottom: spacing.lg },
  inputLabel: { fontSize: 13, fontWeight: '600', marginBottom: spacing.sm, letterSpacing: 0.3 },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 56,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    paddingHorizontal: spacing.base,
    gap: spacing.md,
  },
  input: { flex: 1, fontSize: 16, fontWeight: '500' },
});

export default function SignupScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const buttonScale = useSharedValue(1);

  const animatedButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const handleSignup = async () => {
    Keyboard.dismiss();

    if (!name || !email || !password || !confirmPassword) {
      Alert.alert('Campos obrigatórios', 'Por favor, preencha todos os campos.');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Erro', 'As senhas não coincidem.');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Erro', 'A senha deve ter pelo menos 6 caracteres.');
      return;
    }

    buttonScale.value = withSpring(0.95, animations.spring.snappy);
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data = await response.json();

      if (response.ok && data.user_id) {
        await AsyncStorage.setItem('userId', data.user_id);
        await AsyncStorage.setItem('userEmail', email.trim().toLowerCase());
        router.replace('/onboarding');
      } else {
        Alert.alert('Erro', data.message || 'Não foi possível criar a conta');
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setIsLoading(false);
      buttonScale.value = withSpring(1, animations.spring.gentle);
    }
  };

  // InputField component is defined at the top of the file

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
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
            {/* Back Button */}
            <Animated.View entering={FadeInDown.springify()}>
              <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                <ArrowLeft size={24} color={theme.text} />
              </TouchableOpacity>
            </Animated.View>

            {/* Logo/Brand Section */}
            <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.brandSection}>
              <View style={styles.logoContainer}>
                <LinearGradient
                  colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.logoGradient}
                >
                  <Sparkles size={32} color="#FFF" strokeWidth={2} />
                </LinearGradient>
              </View>
              <Text style={[styles.brandTitle, { color: theme.text }]}>Criar Conta</Text>
              <Text style={[styles.brandSubtitle, { color: theme.textSecondary }]}>
                Comece sua jornada fitness agora
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
              <InputField
                icon={User}
                label="Nome"
                value={name}
                onChangeText={setName}
                placeholder="Seu nome"
                field="name"
              />

              <InputField
                icon={Mail}
                label="Email"
                value={email}
                onChangeText={setEmail}
                placeholder="seu@email.com"
                field="email"
              />

              <InputField
                icon={Lock}
                label="Senha"
                value={password}
                onChangeText={setPassword}
                placeholder="••••••••"
                secureTextEntry
                field="password"
                showToggle
              />

              <InputField
                icon={Lock}
                label="Confirmar Senha"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                placeholder="••••••••"
                secureTextEntry
                field="confirmPassword"
              />

              {/* Signup Button */}
              <Animated.View style={[styles.buttonContainer, animatedButtonStyle]}>
                <TouchableOpacity onPress={handleSignup} disabled={isLoading} activeOpacity={0.9}>
                  <LinearGradient
                    colors={isLoading
                      ? ['#9CA3AF', '#6B7280']
                      : [premiumColors.gradient.start, premiumColors.gradient.middle, premiumColors.gradient.end]
                    }
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.signupButton}
                  >
                    <UserPlus size={20} color="#FFF" />
                    <Text style={styles.signupButtonText}>
                      {isLoading ? 'Criando...' : 'Criar Conta'}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            </Animated.View>

            {/* Login Link */}
            <Animated.View entering={FadeInUp.delay(400).springify()} style={styles.loginSection}>
              <Text style={[styles.loginText, { color: theme.textSecondary }]}>
                Já tem uma conta?
              </Text>
              <TouchableOpacity onPress={() => router.push('/auth/login')}>
                <Text style={[styles.loginLink, { color: premiumColors.primary }]}>
                  Entrar
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
  scrollContent: { flexGrow: 1, padding: spacing.xl },

  backButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },

  brandSection: { alignItems: 'center', marginBottom: spacing.xl },
  logoContainer: { marginBottom: spacing.md },
  logoGradient: {
    width: 72,
    height: 72,
    borderRadius: radius.xl,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: premiumColors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 12,
  },
  brandTitle: { fontSize: 32, fontWeight: '800', letterSpacing: -1 },
  brandSubtitle: { fontSize: 15, marginTop: spacing.xs },

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

  inputGroup: { marginBottom: spacing.lg },
  inputLabel: { fontSize: 13, fontWeight: '600', marginBottom: spacing.sm, letterSpacing: 0.3 },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 56,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    paddingHorizontal: spacing.base,
    gap: spacing.md,
  },
  input: { flex: 1, fontSize: 16, fontWeight: '500' },

  buttonContainer: { marginTop: spacing.md },
  signupButton: {
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
  signupButtonText: { color: '#FFF', fontSize: 17, fontWeight: '700', letterSpacing: -0.3 },

  loginSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.xl,
    gap: spacing.sm,
  },
  loginText: { fontSize: 15 },
  loginLink: { fontSize: 15, fontWeight: '700' },
});
