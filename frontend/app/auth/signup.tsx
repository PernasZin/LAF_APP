/**
 * LAF Premium Signup Screen
 * ==========================
 * Com seletor de idioma - InputField fora do componente
 */

import React, { useState, useCallback } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ScrollView, Alert, Keyboard, Modal
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
import { Mail, Lock, Eye, EyeOff, UserPlus, ArrowLeft, Sparkles, Globe, Check } from 'lucide-react-native';

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

export default function SignupScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const setLanguage = useSettingsStore((state) => state.setLanguage);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const t = translations[language]?.auth || translations['pt-BR'].auth;

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showLangModal, setShowLangModal] = useState(false);

  const buttonScale = useSharedValue(1);

  const animatedButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const handleSignup = async () => {
    Keyboard.dismiss();

    if (!email || !password || !confirmPassword) {
      Alert.alert(
        language === 'en-US' ? 'Required fields' : 'Campos obrigatórios', 
        language === 'en-US' ? 'Please fill all fields.' : 'Por favor, preencha todos os campos.'
      );
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Erro', language === 'en-US' ? 'Passwords do not match.' : 'As senhas não coincidem.');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Erro', language === 'en-US' ? 'Password must be at least 6 characters.' : 'A senha deve ter pelo menos 6 caracteres.');
      return;
    }

    buttonScale.value = withSpring(0.95, animations.spring.snappy);
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data = await response.json();

      if (response.ok && data.user_id) {
        await AsyncStorage.setItem('userId', data.user_id);
        await AsyncStorage.setItem('userEmail', email.trim().toLowerCase());
        await AsyncStorage.setItem('token', data.access_token || '');
        await AsyncStorage.setItem('profileCompleted', 'false');
        
        // ✅ Atualiza AuthStore - o AuthGuard vai redirecionar automaticamente para /onboarding
        // NÃO fazer router.replace() aqui para evitar duplicação de tela!
        await useAuthStore.getState().login(
          data.user_id, 
          data.access_token || '', 
          false
        );
        
        // O AuthGuard vai detectar que profileCompleted=false e redirecionar para /onboarding
      } else {
        Alert.alert('Erro', data.detail || data.message || (language === 'en-US' ? 'Could not create account' : 'Não foi possível criar a conta'));
      }
    } catch (error) {
      Alert.alert('Erro', language === 'en-US' ? 'Could not connect to server' : 'Não foi possível conectar ao servidor');
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
            {/* Header */}
            <Animated.View entering={FadeInDown.springify()} style={styles.headerRow}>
              <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                <ArrowLeft size={24} color={theme.text} />
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.langButton, { backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)' }]}
                onPress={() => setShowLangModal(true)}
              >
                <Globe size={16} color={theme.text} />
                <Text style={[styles.langButtonText, { color: theme.text }]}>
                  {LANGUAGES.find(l => l.code === language)?.flag}
                </Text>
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
              <Text style={[styles.brandTitle, { color: theme.text }]}>{t.createAccount}</Text>
              <Text style={[styles.brandSubtitle, { color: theme.textSecondary }]}>
                {language === 'en-US' ? 'Start your fitness journey now' : language === 'es-ES' ? 'Comienza tu viaje fitness ahora' : 'Comece sua jornada fitness agora'}
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
              {/* Email */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>{t.email}</Text>
                <View style={[styles.inputContainer, { backgroundColor: theme.input.background, borderColor: theme.input.border }]}>
                  <Mail size={20} color={theme.textTertiary} />
                  <TextInput
                    style={[styles.input, { color: theme.text }]}
                    placeholder={language === 'en-US' ? 'your@email.com' : 'seu@email.com'}
                    placeholderTextColor={theme.input.placeholder}
                    value={email}
                    onChangeText={setEmail}
                    autoCapitalize="none"
                    keyboardType="email-address"
                    autoCorrect={false}
                  />
                </View>
              </View>

              {/* Password */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>{t.password}</Text>
                <View style={[styles.inputContainer, { backgroundColor: theme.input.background, borderColor: theme.input.border }]}>
                  <Lock size={20} color={theme.textTertiary} />
                  <TextInput
                    style={[styles.input, { color: theme.text }]}
                    placeholder="••••••••"
                    placeholderTextColor={theme.input.placeholder}
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry={!showPassword}
                    autoCorrect={false}
                  />
                  <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                    {showPassword ? <EyeOff size={20} color={theme.textTertiary} /> : <Eye size={20} color={theme.textTertiary} />}
                  </TouchableOpacity>
                </View>
              </View>

              {/* Confirm Password */}
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>
                  {language === 'en-US' ? 'Confirm Password' : language === 'es-ES' ? 'Confirmar Contraseña' : 'Confirmar Senha'}
                </Text>
                <View style={[styles.inputContainer, { backgroundColor: theme.input.background, borderColor: theme.input.border }]}>
                  <Lock size={20} color={theme.textTertiary} />
                  <TextInput
                    style={[styles.input, { color: theme.text }]}
                    placeholder="••••••••"
                    placeholderTextColor={theme.input.placeholder}
                    value={confirmPassword}
                    onChangeText={setConfirmPassword}
                    secureTextEntry={!showPassword}
                    autoCorrect={false}
                  />
                </View>
              </View>

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
                      {isLoading ? (language === 'en-US' ? 'Creating...' : 'Criando...') : t.createAccount}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>

              {/* Terms and Privacy */}
              <View style={styles.termsContainer}>
                <Text style={[styles.termsText, { color: theme.textTertiary }]}>
                  {language === 'en-US' 
                    ? 'By clicking Create Account, you agree to our ' 
                    : language === 'es-ES'
                    ? 'Al hacer clic en Crear Cuenta, aceptas nuestros '
                    : 'Ao clicar em Criar Conta, você concorda com nossos '}
                  <Text 
                    style={[styles.termsLink, { color: premiumColors.primary }]}
                    onPress={() => router.push('/legal/terms')}
                  >
                    {language === 'en-US' ? 'Terms' : language === 'es-ES' ? 'Términos' : 'Termos'}
                  </Text>
                  {language === 'en-US' ? ' and ' : language === 'es-ES' ? ' y ' : ' e '}
                  <Text 
                    style={[styles.termsLink, { color: premiumColors.primary }]}
                    onPress={() => router.push('/legal/privacy')}
                  >
                    {language === 'en-US' ? 'Privacy Policy' : language === 'es-ES' ? 'Política de Privacidad' : 'Política de Privacidade'}
                  </Text>
                  .
                </Text>
              </View>
            </Animated.View>

            {/* Login Link */}
            <Animated.View entering={FadeInUp.delay(400).springify()} style={styles.loginSection}>
              <Text style={[styles.loginText, { color: theme.textSecondary }]}>
                {t.hasAccount}
              </Text>
              <TouchableOpacity onPress={() => router.push('/auth/login')}>
                <Text style={[styles.loginLink, { color: premiumColors.primary }]}>
                  {t.login}
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
  scrollContent: { flexGrow: 1, padding: spacing.xl },

  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  langButton: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderRadius: radius.full },
  langButtonText: { fontSize: 16 },

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

  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  modalContent: { width: '80%', borderRadius: radius.xl, padding: spacing.lg },
  modalTitle: { fontSize: 18, fontWeight: '700', marginBottom: spacing.lg, textAlign: 'center' },
  langOption: { flexDirection: 'row', alignItems: 'center', paddingVertical: spacing.md, borderBottomWidth: 1, gap: spacing.md },
  langFlag: { fontSize: 24 },
  langLabel: { flex: 1, fontSize: 16, fontWeight: '600' },

  termsContainer: { marginTop: spacing.lg, paddingHorizontal: spacing.sm },
  termsText: { fontSize: 12, textAlign: 'center', lineHeight: 18 },
  termsLink: { fontWeight: '600' },
});
