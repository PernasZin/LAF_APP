/**
 * LAF Premium Login Screen
 * ========================
 * Com seletor de idioma
 */

import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, 
  KeyboardAvoidingView, Platform, ScrollView, Alert, Keyboard, Modal
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
import { Mail, Lock, Eye, EyeOff, LogIn, UserPlus, Sparkles, Globe, Check } from 'lucide-react-native';

import { useSettingsStore, LanguagePreference } from '../../stores/settingsStore';
import { useAuthStore } from '../../stores/authStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing, animations } from '../../theme/premium';
import { translations, SupportedLanguage } from '../../i18n/translations';

import { config } from '../../config';
const BACKEND_URL = config.BACKEND_URL;

const LANGUAGES = [
  { code: 'pt-BR' as LanguagePreference, label: 'Português', flag: '🇧🇷' },
  { code: 'en-US' as LanguagePreference, label: 'English', flag: '🇺🇸' },
  { code: 'es-ES' as LanguagePreference, label: 'Español', flag: '🇪🇸' },
];

export default function LoginScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const setLanguage = useSettingsStore((state) => state.setLanguage);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const t = translations[language]?.auth || translations['pt-BR'].auth;
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [showLangModal, setShowLangModal] = useState(false);
  
  const buttonScale = useSharedValue(1);
  
  const animatedButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const handleLogin = async () => {
    Keyboard.dismiss();
    
    if (!email || !password) {
      Alert.alert(t.email, language === 'en-US' ? 'Please fill email and password.' : language === 'es-ES' ? 'Por favor, complete email y contraseña.' : 'Por favor, preencha email e senha.');
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
        // Salvar dados
        await AsyncStorage.setItem('userId', data.user_id);
        await AsyncStorage.setItem('userEmail', email.trim().toLowerCase());
        await AsyncStorage.setItem('token', data.access_token || '');
        
        // Verifica se tem perfil (backend retorna profile_completed)
        const hasProfile = data.profile_completed || data.has_profile || false;
        
        await AsyncStorage.setItem('profileCompleted', hasProfile ? 'true' : 'false');
        if (hasProfile) {
          await AsyncStorage.setItem('hasCompletedOnboarding', 'true');
        }
        
        // ✅ Atualiza AuthStore - o AuthGuard vai redirecionar automaticamente
        // NÃO fazer router.replace() aqui para evitar duplicação de tela!
        await useAuthStore.getState().login(
          data.user_id, 
          data.access_token || '', 
          hasProfile
        );
        
        // O AuthGuard detecta a mudança de estado e redireciona:
        // - Se hasProfile=true → /(tabs)
        // - Se hasProfile=false → /onboarding
      } else {
        Alert.alert('Erro', data.detail || data.message || (language === 'en-US' ? 'Invalid email or password' : language === 'es-ES' ? 'Email o contraseña incorrectos' : 'Email ou senha incorretos'));
      }
    } catch (error) {
      Alert.alert('Erro', language === 'en-US' ? 'Could not connect to server' : language === 'es-ES' ? 'No se pudo conectar al servidor' : 'Não foi possível conectar ao servidor');
    } finally {
      setIsLoading(false);
      buttonScale.value = withSpring(1, animations.spring.gentle);
    }
  };

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
            {/* Language Button */}
            <Animated.View entering={FadeInDown.springify()} style={styles.langButtonContainer}>
              <TouchableOpacity 
                style={[styles.langButton, { backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)' }]}
                onPress={() => setShowLangModal(true)}
              >
                <Globe size={18} color={theme.text} />
                <Text style={[styles.langButtonText, { color: theme.text }]}>
                  {LANGUAGES.find(l => l.code === language)?.flag} {LANGUAGES.find(l => l.code === language)?.label}
                </Text>
              </TouchableOpacity>
            </Animated.View>

            {/* Logo Section */}
            <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.logoSection}>
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
              <Text style={[styles.appName, { color: theme.text }]}>LAF</Text>
              <Text style={[styles.tagline, { color: theme.textSecondary }]}>
                {language === 'en-US' ? 'Your fitness journey starts here' : language === 'es-ES' ? 'Tu viaje fitness comienza aquí' : 'Sua jornada fitness começa aqui'}
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
              {/* Email Input */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>{t.email}</Text>
                <View style={[
                  styles.inputContainer,
                  { 
                    backgroundColor: theme.input.background,
                    borderColor: emailFocused ? premiumColors.primary : theme.input.border 
                  }
                ]}>
                  <Mail size={20} color={emailFocused ? premiumColors.primary : theme.textTertiary} />
                  <TextInput
                    style={[styles.input, { color: theme.text }]}
                    placeholder={language === 'en-US' ? 'your@email.com' : 'seu@email.com'}
                    placeholderTextColor={theme.input.placeholder}
                    value={email}
                    onChangeText={setEmail}
                    onFocus={() => setEmailFocused(true)}
                    onBlur={() => setEmailFocused(false)}
                    autoCapitalize="none"
                    keyboardType="email-address"
                    autoCorrect={false}
                  />
                </View>
              </View>

              {/* Password Input */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>{t.password}</Text>
                <View style={[
                  styles.inputContainer,
                  { 
                    backgroundColor: theme.input.background,
                    borderColor: passwordFocused ? premiumColors.primary : theme.input.border 
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
                    autoCorrect={false}
                  />
                  <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                    {showPassword ? (
                      <EyeOff size={20} color={theme.textTertiary} />
                    ) : (
                      <Eye size={20} color={theme.textTertiary} />
                    )}
                  </TouchableOpacity>
                </View>
              </View>

              {/* Login Button */}
              <Animated.View style={[styles.buttonContainer, animatedButtonStyle]}>
                <TouchableOpacity onPress={handleLogin} disabled={isLoading} activeOpacity={0.9}>
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
                      {isLoading ? (language === 'en-US' ? 'Entering...' : language === 'es-ES' ? 'Entrando...' : 'Entrando...') : t.enterAccount}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            </Animated.View>

            {/* Signup Link */}
            <Animated.View entering={FadeInUp.delay(400).springify()} style={styles.signupSection}>
              <Text style={[styles.signupText, { color: theme.textSecondary }]}>
                {t.noAccount}
              </Text>
              <TouchableOpacity onPress={() => router.push('/auth/signup')}>
                <Text style={[styles.signupLink, { color: premiumColors.primary }]}>
                  {t.createAccount}
                </Text>
              </TouchableOpacity>
            </Animated.View>
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>

      {/* Language Modal */}
      <Modal visible={showLangModal} transparent animationType="fade">
        <TouchableOpacity 
          style={[styles.modalOverlay, { backgroundColor: theme.overlay }]}
          activeOpacity={1}
          onPress={() => setShowLangModal(false)}
        >
          <View style={[styles.modalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            <Text style={[styles.modalTitle, { color: theme.text }]}>
              {language === 'en-US' ? 'Select Language' : language === 'es-ES' ? 'Seleccionar Idioma' : 'Selecionar Idioma'}
            </Text>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[styles.langOption, { borderBottomColor: theme.border }]}
                onPress={() => {
                  setLanguage(lang.code);
                  setShowLangModal(false);
                }}
              >
                <Text style={styles.langFlag}>{lang.flag}</Text>
                <Text style={[styles.langLabel, { color: theme.text }]}>{lang.label}</Text>
                {language === lang.code && <Check size={20} color={premiumColors.primary} />}
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  keyboardView: { flex: 1 },
  scrollContent: { flexGrow: 1, padding: spacing.xl, justifyContent: 'center' },

  langButtonContainer: { position: 'absolute', top: 0, right: 0 },
  langButton: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.full },
  langButtonText: { fontSize: 13, fontWeight: '600' },

  logoSection: { alignItems: 'center', marginBottom: spacing['2xl'] },
  logoContainer: { marginBottom: spacing.md },
  logoGradient: {
    width: 80,
    height: 80,
    borderRadius: radius.xl,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: premiumColors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 12,
  },
  appName: { fontSize: 42, fontWeight: '900', letterSpacing: -2 },
  tagline: { fontSize: 15, marginTop: spacing.xs, textAlign: 'center' },

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
  loginButtonText: { color: '#FFF', fontSize: 17, fontWeight: '700', letterSpacing: -0.3 },

  signupSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.xl,
    gap: spacing.sm,
  },
  signupText: { fontSize: 15 },
  signupLink: { fontSize: 15, fontWeight: '700' },

  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  modalContent: { width: '80%', borderRadius: radius.xl, padding: spacing.lg },
  modalTitle: { fontSize: 18, fontWeight: '700', marginBottom: spacing.lg, textAlign: 'center' },
  langOption: { flexDirection: 'row', alignItems: 'center', paddingVertical: spacing.md, borderBottomWidth: 1, gap: spacing.md },
  langFlag: { fontSize: 24 },
  langLabel: { flex: 1, fontSize: 16, fontWeight: '600' },
});
