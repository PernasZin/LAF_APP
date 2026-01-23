import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Redirect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import { Globe, Check, Sparkles } from 'lucide-react-native';

import { useAuthStore } from '../stores/authStore';
import { useSettingsStore, LanguagePreference } from '../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../theme/premium';
import { translations, SupportedLanguage } from '../i18n/translations';

const LANGUAGES = [
  { code: 'pt-BR' as LanguagePreference, label: 'Português (Brasil)', flag: '🇧🇷' },
  { code: 'en-US' as LanguagePreference, label: 'English (US)', flag: '🇺🇸' },
  { code: 'es-ES' as LanguagePreference, label: 'Español', flag: '🇪🇸' },
];

type ScreenState = 'loading' | 'language_select' | 'redirect';

/**
 * Tela inicial - Seleção de Idioma + Redireciona baseado no estado de auth
 */
export default function IndexScreen() {
  const { isAuthenticated, isInitialized } = useAuthStore();
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const language = useSettingsStore((state) => state.language);
  const setLanguage = useSettingsStore((state) => state.setLanguage);
  
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  // Get translations for selected language
  const t = translations[selectedLang as SupportedLanguage] || translations['pt-BR'];
  
  const [screenState, setScreenState] = useState<ScreenState>('loading');
  const [destination, setDestination] = useState<'login' | 'tabs' | 'onboarding' | null>(null);
  const [selectedLang, setSelectedLang] = useState<LanguagePreference>(language);

  // Initial check on mount
  useEffect(() => {
    const init = async () => {
      try {
        const hasSelectedLang = await AsyncStorage.getItem('hasSelectedLanguage');
        console.log('hasSelectedLanguage check:', hasSelectedLang);
        
        if (hasSelectedLang !== 'true') {
          // First time user - show language selector
          setScreenState('language_select');
        } else {
          // Returning user - go to redirect flow
          setScreenState('redirect');
        }
      } catch (error) {
        console.log('Error in init:', error);
        // Show language selector on error
        setScreenState('language_select');
      }
    };
    
    init();
  }, []);

  // Handle redirect logic after language is selected
  useEffect(() => {
    if (screenState !== 'redirect') return;
    if (!isInitialized) return;
    
    const checkDestination = async () => {
      if (!isAuthenticated) {
        setDestination('login');
        return;
      }

      const hasProfile = await AsyncStorage.getItem('hasCompletedOnboarding');
      if (hasProfile === 'true') {
        setDestination('tabs');
      } else {
        setDestination('onboarding');
      }
    };
    
    checkDestination();
  }, [screenState, isAuthenticated, isInitialized]);

  const handleLanguageSelect = (langCode: LanguagePreference) => {
    setSelectedLang(langCode);
  };

  const handleContinue = async () => {
    setLanguage(selectedLang);
    await AsyncStorage.setItem('hasSelectedLanguage', 'true');
    setScreenState('redirect');
  };

  // ============ LANGUAGE SELECTOR SCREEN ============
  if (screenState === 'language_select') {
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
          {/* Logo Section */}
          <Animated.View entering={FadeInDown.springify()} style={styles.logoSection}>
            <View style={styles.logoContainer}>
              <LinearGradient
                colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.logoGradient}
              >
                <Sparkles size={40} color="#FFF" strokeWidth={2} />
              </LinearGradient>
            </View>
            <Text style={[styles.brandTitle, { color: theme.text }]}>LAF</Text>
            <Text style={[styles.brandSubtitle, { color: theme.textSecondary }]}>
              {t.languageSelect?.yourAssistant || 'Seu assistente de nutrição'}
            </Text>
          </Animated.View>

          {/* Language Selection */}
          <Animated.View entering={FadeInUp.delay(200).springify()} style={styles.languageSection}>
            <View style={[styles.languageIconContainer, { backgroundColor: `${premiumColors.primary}15` }]}>
              <Globe size={28} color={premiumColors.primary} />
            </View>
            <Text style={[styles.languageTitle, { color: theme.text }]}>
              {t.languageSelect?.title || 'Escolha seu idioma'}
            </Text>
            <Text style={[styles.languageSubtitle, { color: theme.textSecondary }]}>
              {t.languageSelect?.subtitle || 'Select your language / Selecciona tu idioma'}
            </Text>

            {/* Language Options */}
            <View style={styles.languageOptions}>
              {LANGUAGES.map((lang, index) => {
                const isSelected = selectedLang === lang.code;
                return (
                  <Animated.View 
                    key={lang.code}
                    entering={FadeInUp.delay(300 + index * 100).springify()}
                  >
                    <TouchableOpacity
                      style={[
                        styles.languageOption,
                        {
                          backgroundColor: isSelected 
                            ? isDark ? 'rgba(16, 185, 129, 0.15)' : 'rgba(16, 185, 129, 0.1)'
                            : isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
                          borderColor: isSelected 
                            ? premiumColors.primary 
                            : isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)',
                        }
                      ]}
                      onPress={() => handleLanguageSelect(lang.code)}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.languageFlag}>{lang.flag}</Text>
                      <Text style={[styles.languageLabel, { color: theme.text }]}>
                        {lang.label}
                      </Text>
                      {isSelected && (
                        <View style={styles.checkContainer}>
                          <Check size={20} color={premiumColors.primary} strokeWidth={3} />
                        </View>
                      )}
                    </TouchableOpacity>
                  </Animated.View>
                );
              })}
            </View>

            {/* Continue Button */}
            <Animated.View entering={FadeInUp.delay(600).springify()} style={styles.continueContainer}>
              <TouchableOpacity 
                onPress={handleContinue} 
                activeOpacity={0.7}
                style={[styles.continueButton, { backgroundColor: premiumColors.primary }]}
              >
                <Text style={styles.continueButtonText}>Continuar</Text>
              </TouchableOpacity>
            </Animated.View>
          </Animated.View>
        </SafeAreaView>
      </View>
    );
  }

  // ============ REDIRECT LOGIC ============
  if (destination === 'login') {
    return <Redirect href="/auth/login" />;
  }
  
  if (destination === 'tabs') {
    return <Redirect href="/(tabs)" />;
  }
  
  if (destination === 'onboarding') {
    return <Redirect href="/onboarding" />;
  }

  // ============ LOADING STATE ============
  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark 
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']
        }
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />
      <SafeAreaView style={styles.loadingContainer}>
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
        <ActivityIndicator size="large" color={premiumColors.primary} style={{ marginTop: 24 }} />
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
    justifyContent: 'center',
    padding: spacing.xl,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Logo Section
  logoSection: {
    alignItems: 'center',
    marginBottom: spacing['3xl'],
  },
  logoContainer: {
    marginBottom: spacing.lg,
  },
  logoGradient: {
    width: 88,
    height: 88,
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
    fontSize: 48,
    fontWeight: '800',
    letterSpacing: -2,
  },
  brandSubtitle: {
    fontSize: 16,
    marginTop: spacing.xs,
    fontWeight: '500',
  },
  
  // Language Section
  languageSection: {
    alignItems: 'center',
  },
  languageIconContainer: {
    width: 56,
    height: 56,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.base,
  },
  languageTitle: {
    fontSize: 24,
    fontWeight: '700',
    letterSpacing: -0.5,
    marginBottom: spacing.xs,
  },
  languageSubtitle: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  
  // Language Options
  languageOptions: {
    width: '100%',
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  languageOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.base,
    borderRadius: radius.xl,
    borderWidth: 2,
    gap: spacing.md,
  },
  languageFlag: {
    fontSize: 28,
  },
  languageLabel: {
    flex: 1,
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: -0.3,
  },
  checkContainer: {
    width: 28,
    height: 28,
    borderRadius: radius.full,
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  
  // Continue Button
  continueContainer: {
    width: '100%',
  },
  continueButton: {
    height: 56,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: premiumColors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  continueButtonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
});
