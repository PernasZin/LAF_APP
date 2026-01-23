/**
 * Paywall Screen - Tela de Assinatura Premium
 * ============================================
 * Mostra benefícios e opção de iniciar trial/assinar
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Platform,
  Alert,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import Animated, { FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, withSpring, withSequence } from 'react-native-reanimated';
import {
  Crown,
  Check,
  Sparkles,
  Utensils,
  Dumbbell,
  TrendingUp,
  RefreshCw,
  Shield,
  X,
  Zap,
} from 'lucide-react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { useSettingsStore } from '../stores/settingsStore';
import { useSubscriptionStore, SUBSCRIPTION_CONFIG } from '../stores/subscriptionStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../theme/premium';
import { SupportedLanguage, translations } from '../i18n/translations';
import { config } from '../config';

const BACKEND_URL = config.BACKEND_URL;

const FEATURES = [
  { icon: Utensils, key: 'personalizedDiet' },
  { icon: Dumbbell, key: 'customWorkouts' },
  { icon: TrendingUp, key: 'progressTracking' },
  { icon: RefreshCw, key: 'autoAdjustments' },
  { icon: Shield, key: 'unlimitedAccess' },
  { icon: Zap, key: 'prioritySupport' },
];

const getTranslations = (lang: SupportedLanguage) => {
  const t = {
    'pt-BR': {
      title: 'Desbloqueie Todo o Potencial',
      subtitle: 'Transforme seu corpo com planos personalizados de dieta e treino',
      trialBadge: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} dias grátis`,
      startTrial: 'Iniciar Período Grátis',
      thenPrice: `Depois R$ ${SUBSCRIPTION_CONFIG.MONTHLY_PRICE.toFixed(2)}/mês`,
      cancelAnytime: 'Cancele quando quiser',
      features: {
        personalizedDiet: 'Dieta 100% personalizada',
        customWorkouts: 'Treinos adaptados ao seu nível',
        progressTracking: 'Acompanhamento de progresso',
        autoAdjustments: 'Ajustes automáticos de dieta',
        unlimitedAccess: 'Acesso ilimitado a tudo',
        prioritySupport: 'Suporte prioritário',
      },
      restorePurchase: 'Restaurar compra',
      termsNotice: 'Ao continuar, você concorda com os Termos de Uso e Política de Privacidade',
      processing: 'Processando...',
      skipForNow: 'Pular por enquanto',
    },
    'en-US': {
      title: 'Unlock Your Full Potential',
      subtitle: 'Transform your body with personalized diet and workout plans',
      trialBadge: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} days free`,
      startTrial: 'Start Free Trial',
      thenPrice: `Then $${(SUBSCRIPTION_CONFIG.MONTHLY_PRICE / 5).toFixed(2)}/month`,
      cancelAnytime: 'Cancel anytime',
      features: {
        personalizedDiet: '100% personalized diet',
        customWorkouts: 'Workouts adapted to your level',
        progressTracking: 'Progress tracking',
        autoAdjustments: 'Automatic diet adjustments',
        unlimitedAccess: 'Unlimited access to everything',
        prioritySupport: 'Priority support',
      },
      restorePurchase: 'Restore purchase',
      termsNotice: 'By continuing, you agree to the Terms of Use and Privacy Policy',
      processing: 'Processing...',
      skipForNow: 'Skip for now',
    },
    'es-ES': {
      title: 'Desbloquea Todo Tu Potencial',
      subtitle: 'Transforma tu cuerpo con planes personalizados de dieta y entrenamiento',
      trialBadge: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} días gratis`,
      startTrial: 'Iniciar Período Gratis',
      thenPrice: `Luego €${(SUBSCRIPTION_CONFIG.MONTHLY_PRICE / 6).toFixed(2)}/mes`,
      cancelAnytime: 'Cancela cuando quieras',
      features: {
        personalizedDiet: 'Dieta 100% personalizada',
        customWorkouts: 'Entrenamientos adaptados a tu nivel',
        progressTracking: 'Seguimiento de progreso',
        autoAdjustments: 'Ajustes automáticos de dieta',
        unlimitedAccess: 'Acceso ilimitado a todo',
        prioritySupport: 'Soporte prioritario',
      },
      restorePurchase: 'Restaurar compra',
      termsNotice: 'Al continuar, aceptas los Términos de Uso y la Política de Privacidad',
      processing: 'Procesando...',
      skipForNow: 'Saltar por ahora',
    },
  };
  return t[lang] || t['pt-BR'];
};

export default function PaywallScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const t = getTranslations(language);

  const { startTrial, setHasSeenPaywall, isPremium } = useSubscriptionStore();
  const [isLoading, setIsLoading] = useState(false);

  const buttonScale = useSharedValue(1);
  const crownRotation = useSharedValue(0);

  useEffect(() => {
    // Animação da coroa
    crownRotation.value = withSequence(
      withSpring(-5),
      withSpring(5),
      withSpring(0)
    );
  }, []);

  const animatedButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const animatedCrownStyle = useAnimatedStyle(() => ({
    transform: [{ rotate: `${crownRotation.value}deg` }],
  }));

  const handleStartTrial = async () => {
    setIsLoading(true);
    buttonScale.value = withSpring(0.95);

    try {
      // TODO: Integrar com IAP real aqui
      // Por enquanto, inicia trial simulado
      await startTrial();
      setHasSeenPaywall(true);

      // Pequeno delay para UX
      await new Promise(resolve => setTimeout(resolve, 800));

      // Navega para as tabs principais
      router.replace('/(tabs)');
    } catch (error) {
      console.error('Error starting trial:', error);
      Alert.alert(
        'Erro',
        'Não foi possível iniciar o período grátis. Tente novamente.'
      );
    } finally {
      setIsLoading(false);
      buttonScale.value = withSpring(1);
    }
  };

  const handleRestorePurchase = async () => {
    // TODO: Implementar restauração de compra com IAP
    Alert.alert(
      language === 'en-US' ? 'Restore Purchase' : 'Restaurar Compra',
      language === 'en-US'
        ? 'Purchase restoration will be available when the app is published to the stores.'
        : 'A restauração de compra estará disponível quando o app for publicado nas lojas.'
    );
  };

  const handleSkip = () => {
    setHasSeenPaywall(true);
    router.replace('/(tabs)');
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Gradient Background */}
      <LinearGradient
        colors={isDark
          ? ['rgba(234, 179, 8, 0.15)', 'transparent', 'rgba(16, 185, 129, 0.1)']
          : ['rgba(234, 179, 8, 0.2)', 'transparent', 'rgba(16, 185, 129, 0.15)']
        }
        locations={[0, 0.4, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        {/* Skip Button */}
        <TouchableOpacity
          style={styles.skipButton}
          onPress={handleSkip}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <X size={24} color={theme.textTertiary} />
        </TouchableOpacity>

        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Crown Icon */}
          <Animated.View entering={FadeInDown.springify()} style={styles.iconContainer}>
            <Animated.View style={animatedCrownStyle}>
              <LinearGradient
                colors={['#F59E0B', '#EAB308', '#CA8A04']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.crownBg}
              >
                <Crown size={40} color="#FFF" strokeWidth={2} />
              </LinearGradient>
            </Animated.View>
          </Animated.View>

          {/* Title */}
          <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.titleContainer}>
            <Text style={[styles.title, { color: theme.text }]}>{t.title}</Text>
            <Text style={[styles.subtitle, { color: theme.textSecondary }]}>{t.subtitle}</Text>
          </Animated.View>

          {/* Trial Badge */}
          <Animated.View entering={FadeInDown.delay(200).springify()} style={styles.badgeContainer}>
            <LinearGradient
              colors={['#10B981', '#059669']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.trialBadge}
            >
              <Sparkles size={16} color="#FFF" />
              <Text style={styles.trialBadgeText}>{t.trialBadge}</Text>
            </LinearGradient>
          </Animated.View>

          {/* Features Card */}
          <Animated.View
            entering={FadeInUp.delay(300).springify()}
            style={[
              styles.featuresCard,
              {
                backgroundColor: isDark ? 'rgba(30, 41, 59, 0.8)' : 'rgba(255, 255, 255, 0.9)',
                borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(0, 0, 0, 0.05)',
              },
            ]}
          >
            {FEATURES.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Animated.View
                  key={feature.key}
                  entering={FadeInUp.delay(400 + index * 50).springify()}
                  style={styles.featureRow}
                >
                  <View style={[styles.featureIconBg, { backgroundColor: premiumColors.primary + '20' }]}>
                    <Icon size={18} color={premiumColors.primary} />
                  </View>
                  <Text style={[styles.featureText, { color: theme.text }]}>
                    {t.features[feature.key as keyof typeof t.features]}
                  </Text>
                  <Check size={18} color="#10B981" />
                </Animated.View>
              );
            })}
          </Animated.View>

          {/* CTA Button */}
          <Animated.View
            entering={FadeInUp.delay(700).springify()}
            style={[styles.ctaContainer, animatedButtonStyle]}
          >
            <TouchableOpacity
              onPress={handleStartTrial}
              disabled={isLoading}
              activeOpacity={0.9}
            >
              <LinearGradient
                colors={isLoading
                  ? ['#9CA3AF', '#6B7280']
                  : ['#F59E0B', '#EAB308', '#CA8A04']
                }
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.ctaButton}
              >
                {isLoading ? (
                  <ActivityIndicator color="#FFF" />
                ) : (
                  <>
                    <Crown size={22} color="#FFF" />
                    <Text style={styles.ctaButtonText}>{t.startTrial}</Text>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>

            <Text style={[styles.priceText, { color: theme.textSecondary }]}>
              {t.thenPrice}
            </Text>
            <Text style={[styles.cancelText, { color: theme.textTertiary }]}>
              {t.cancelAnytime}
            </Text>
          </Animated.View>

          {/* Restore Purchase */}
          <Animated.View entering={FadeInUp.delay(800).springify()} style={styles.restoreContainer}>
            <TouchableOpacity onPress={handleRestorePurchase}>
              <Text style={[styles.restoreText, { color: premiumColors.primary }]}>
                {t.restorePurchase}
              </Text>
            </TouchableOpacity>
          </Animated.View>

          {/* Terms Notice */}
          <Animated.View entering={FadeInUp.delay(900).springify()} style={styles.termsContainer}>
            <Text style={[styles.termsText, { color: theme.textTertiary }]}>
              {t.termsNotice}
            </Text>
          </Animated.View>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.xl,
  },
  skipButton: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 60 : 20,
    right: spacing.lg,
    zIndex: 10,
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    alignItems: 'center',
    marginTop: spacing.xl * 2,
    marginBottom: spacing.lg,
  },
  crownBg: {
    width: 88,
    height: 88,
    borderRadius: 44,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#F59E0B',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 12,
  },
  titleContainer: {
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    textAlign: 'center',
    letterSpacing: -0.5,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: spacing.md,
  },
  badgeContainer: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  trialBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: radius.full,
  },
  trialBadgeText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: '700',
  },
  featuresCard: {
    borderRadius: radius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    marginBottom: spacing.xl,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    gap: spacing.md,
  },
  featureIconBg: {
    width: 36,
    height: 36,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  featureText: {
    flex: 1,
    fontSize: 15,
    fontWeight: '500',
  },
  ctaContainer: {
    marginBottom: spacing.lg,
  },
  ctaButton: {
    height: 58,
    borderRadius: radius.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    shadowColor: '#F59E0B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  ctaButtonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '700',
  },
  priceText: {
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    marginTop: spacing.md,
  },
  cancelText: {
    fontSize: 13,
    textAlign: 'center',
    marginTop: spacing.xs,
  },
  restoreContainer: {
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  restoreText: {
    fontSize: 14,
    fontWeight: '600',
  },
  termsContainer: {
    paddingHorizontal: spacing.lg,
  },
  termsText: {
    fontSize: 11,
    textAlign: 'center',
    lineHeight: 16,
  },
});
