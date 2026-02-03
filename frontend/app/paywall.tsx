/**
 * Paywall Screen - Tela de Assinatura Premium
 * ============================================
 * Mostra benefícios e opção de iniciar trial/assinar
 * 
 * Usa APENAS In-App Purchase (IAP) para iOS e Android (App Store / Google Play)
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Pressable,
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
import { iapService, IAP_PRODUCTS } from '../services/IAPService';

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
      trialInfo: `Experimente ${SUBSCRIPTION_CONFIG.TRIAL_DAYS} dias grátis, depois pagamento recorrente`,
      startTrial: 'Iniciar Período Grátis',
      thenPrice: `Depois R$ ${SUBSCRIPTION_CONFIG.MONTHLY_PRICE.toFixed(2)}/mês`,
      cancelAnytime: 'Cancele quando quiser. Sem compromisso.',
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
      monthly: 'Mensal',
      annual: 'Anual',
      perMonth: 'por mês',
      perYear: 'por ano',
      trialThenRecurring: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} dias grátis, depois recorrente`,
    },
    'en-US': {
      title: 'Unlock Your Full Potential',
      subtitle: 'Transform your body with personalized diet and workout plans',
      trialBadge: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} days free`,
      trialInfo: `Try ${SUBSCRIPTION_CONFIG.TRIAL_DAYS} days free, then recurring payment`,
      startTrial: 'Start Free Trial',
      thenPrice: `Then $${(SUBSCRIPTION_CONFIG.MONTHLY_PRICE / 5).toFixed(2)}/month`,
      cancelAnytime: 'Cancel anytime. No commitment.',
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
      monthly: 'Monthly',
      annual: 'Annual',
      perMonth: 'per month',
      perYear: 'per year',
      trialThenRecurring: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} days free, then recurring`,
    },
    'es-ES': {
      title: 'Desbloquea Todo Tu Potencial',
      subtitle: 'Transforma tu cuerpo con planes personalizados de dieta y entrenamiento',
      trialBadge: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} días gratis`,
      trialInfo: `Prueba ${SUBSCRIPTION_CONFIG.TRIAL_DAYS} días gratis, después pago recurrente`,
      startTrial: 'Iniciar Período Gratis',
      thenPrice: `Luego €${(SUBSCRIPTION_CONFIG.MONTHLY_PRICE / 6).toFixed(2)}/mes`,
      cancelAnytime: 'Cancela cuando quieras. Sin compromiso.',
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
      monthly: 'Mensual',
      annual: 'Anual',
      perMonth: 'por mes',
      perYear: 'por año',
      trialThenRecurring: `${SUBSCRIPTION_CONFIG.TRIAL_DAYS} días gratis, después recurrente`,
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

  const { startTrial, setHasSeenPaywall, isPremium, setPremiumStatus, activateSubscription } = useSubscriptionStore();
  const [isLoading, setIsLoading] = useState(false);
  const [iapInitialized, setIapInitialized] = useState(false);

  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'annual'>('monthly');

  const buttonScale = useSharedValue(1);
  const crownRotation = useSharedValue(0);

  // Inicializar IAP no mobile
  useEffect(() => {
    const initIAP = async () => {
      if (Platform.OS !== 'web') {
        try {
          const initialized = await iapService.initialize();
          setIapInitialized(initialized);
          
          if (initialized) {
            // Buscar produtos
            await iapService.getProducts();
            
            // Configurar listener de compras bem-sucedidas
            iapService.onPurchase(async (purchase) => {
              console.log('🎉 Purchase completed:', purchase.productId);
              
              // Determinar tipo de plano baseado no productId
              const isAnnual = purchase.productId.includes('annual');
              const planType = isAnnual ? 'annual' : 'monthly';
              
              // Ativar assinatura com data de expiração correta
              activateSubscription(planType);
              setHasSeenPaywall(true);
              
              // Salvar no backend (para sincronização)
              try {
                const userId = await AsyncStorage.getItem('userId');
                if (userId) {
                  await fetch(`${BACKEND_URL}/api/user/premium`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      user_id: userId,
                      product_id: purchase.productId,
                      transaction_id: purchase.transactionId,
                      receipt: purchase.transactionReceipt,
                      platform: Platform.OS,
                      plan_type: planType,
                    }),
                  });
                }
              } catch (error) {
                console.error('Failed to sync purchase with backend:', error);
              }
              
              // Redirecionar para o app
              router.replace('/(tabs)');
            });
          }
        } catch (error) {
          console.error('Failed to initialize IAP:', error);
        }
      }
    };

    initIAP();

    // Cleanup
    return () => {
      if (Platform.OS !== 'web') {
        iapService.disconnect();
      }
    };
  }, []);

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

  /**
   * Handler para assinatura - APENAS Apple/Google In-App Purchase
   */
  const handleSubscribe = async () => {
    console.log('🔵 handleSubscribe called! selectedPlan:', selectedPlan);
    console.log('🔵 Platform:', Platform.OS);
    
    setIsLoading(true);
    buttonScale.value = withSpring(0.95);

    try {
      const userId = await AsyncStorage.getItem('userId');
      console.log('🔵 userId from AsyncStorage:', userId);
      
      if (!userId) {
        Alert.alert('Erro', 'Faça login primeiro para assinar.');
        setIsLoading(false);
        router.replace('/auth/login');
        return;
      }

      // Verificar se estamos em ambiente de produção (não Expo Go)
      if (Platform.OS === 'web') {
        // Na web, mostrar mensagem informando que assinatura é apenas via app
        Alert.alert(
          'Assinatura via App',
          'As assinaturas estão disponíveis apenas através do aplicativo iOS ou Android. Por favor, baixe o app na App Store ou Google Play para assinar.',
          [{ text: 'OK' }]
        );
        setIsLoading(false);
        return;
      }

      // Inicializar IAP se necessário
      if (!iapInitialized) {
        console.log('🛒 Initializing IAP...');
        const initialized = await iapService.initialize();
        if (!initialized) {
          Alert.alert(
            'Erro',
            'Não foi possível conectar à loja. Verifique sua conexão e tente novamente.',
            [{ text: 'OK' }]
          );
          setIsLoading(false);
          return;
        }
        setIapInitialized(true);
      }

      // Usar In-App Purchase
      console.log('🛒 Using In-App Purchase (IAP)');
      
      const productId = selectedPlan === 'monthly' 
        ? IAP_PRODUCTS.MONTHLY 
        : IAP_PRODUCTS.ANNUAL;
      
      console.log('🛒 Purchasing product:', productId);
      
      const success = await iapService.purchaseProduct(productId!);
      
      if (!success) {
        Alert.alert(
          'Erro',
          'Não foi possível iniciar a compra. Tente novamente.'
        );
      }
      // O listener de compras vai cuidar do resto (atualizar premium e redirecionar)
      
    } catch (error) {
      console.error('❌ Error in purchase:', error);
      Alert.alert(
        'Erro',
        'Não foi possível iniciar o pagamento. Tente novamente.'
      );
    } finally {
      setIsLoading(false);
      buttonScale.value = withSpring(1);
    }
  };

  const handleStartTrial = async () => {
    // Para manter compatibilidade, o trial agora inicia a assinatura
    await handleSubscribe();
  };

  const handleRestorePurchase = async () => {
    if (Platform.OS === 'web') {
      Alert.alert(
        language === 'en-US' ? 'Restore Purchase' : 'Restaurar Compra',
        language === 'en-US'
          ? 'Purchase restoration is only available on mobile devices.'
          : 'A restauração de compra está disponível apenas em dispositivos móveis.'
      );
      return;
    }

    setIsLoading(true);
    
    try {
      if (!iapInitialized) {
        await iapService.initialize();
      }

      const purchases = await iapService.restorePurchases();
      
      if (purchases.length > 0) {
        // Usuário tem compras anteriores
        setPremiumStatus(true);
        setHasSeenPaywall(true);
        
        Alert.alert(
          language === 'en-US' ? 'Success!' : 'Sucesso!',
          language === 'en-US'
            ? 'Your purchase has been restored.'
            : 'Sua compra foi restaurada.',
          [
            {
              text: 'OK',
              onPress: () => router.replace('/(tabs)'),
            },
          ]
        );
      } else {
        Alert.alert(
          language === 'en-US' ? 'No Purchases Found' : 'Nenhuma Compra Encontrada',
          language === 'en-US'
            ? 'We could not find any previous purchases associated with your account.'
            : 'Não encontramos nenhuma compra anterior associada à sua conta.'
        );
      }
    } catch (error) {
      console.error('❌ Error restoring purchases:', error);
      Alert.alert(
        'Erro',
        language === 'en-US'
          ? 'Failed to restore purchases. Please try again.'
          : 'Falha ao restaurar compras. Tente novamente.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Premium é obrigatório - não há opção de pular
  // handleSkip removido intencionalmente

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

          {/* Plan Selection */}
          <Animated.View entering={FadeInUp.delay(650).springify()} style={styles.planContainer}>
            <Pressable
              onPress={() => setSelectedPlan('monthly')}
              style={[
                styles.planOption,
                {
                  backgroundColor: selectedPlan === 'monthly' 
                    ? (isDark ? 'rgba(234, 179, 8, 0.2)' : 'rgba(234, 179, 8, 0.15)')
                    : (isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)'),
                  borderColor: selectedPlan === 'monthly' ? '#EAB308' : (isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(0, 0, 0, 0.1)'),
                  borderWidth: selectedPlan === 'monthly' ? 2 : 1,
                }
              ]}
            >
              <View style={styles.planHeader}>
                <Text style={[styles.planTitle, { color: theme.text }]}>{t.monthly}</Text>
                {selectedPlan === 'monthly' && <Check size={20} color="#EAB308" />}
              </View>
              <Text style={[styles.planPrice, { color: theme.text }]}>R$ {SUBSCRIPTION_CONFIG.MONTHLY_PRICE.toFixed(2).replace('.', ',')}</Text>
              <Text style={[styles.planPeriod, { color: theme.textSecondary }]}>{t.perMonth}</Text>
              <Text style={[styles.trialText, { color: '#10B981' }]}>{t.trialThenRecurring}</Text>
            </Pressable>
            
            <Pressable
              onPress={() => setSelectedPlan('annual')}
              style={[
                styles.planOption,
                {
                  backgroundColor: selectedPlan === 'annual' 
                    ? (isDark ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.15)')
                    : (isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)'),
                  borderColor: selectedPlan === 'annual' ? '#10B981' : (isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(0, 0, 0, 0.1)'),
                  borderWidth: selectedPlan === 'annual' ? 2 : 1,
                }
              ]}
            >
              <View style={styles.saveBadge}>
                <Text style={styles.saveBadgeText}>-{SUBSCRIPTION_CONFIG.ANNUAL_DISCOUNT}%</Text>
              </View>
              <View style={styles.planHeader}>
                <Text style={[styles.planTitle, { color: theme.text }]}>{t.annual}</Text>
                {selectedPlan === 'annual' && <Check size={20} color="#10B981" />}
              </View>
              <Text style={[styles.planPrice, { color: theme.text }]}>R$ {SUBSCRIPTION_CONFIG.ANNUAL_PRICE.toFixed(2).replace('.', ',')}</Text>
              <Text style={[styles.planPeriod, { color: theme.textSecondary }]}>{t.perYear} (R$ {SUBSCRIPTION_CONFIG.ANNUAL_MONTHLY_PRICE.toFixed(2).replace('.', ',')}/mês)</Text>
              <Text style={[styles.trialText, { color: '#10B981' }]}>{t.trialThenRecurring}</Text>
            </Pressable>
          </Animated.View>

          {/* CTA Button */}
          <Animated.View
            entering={FadeInUp.delay(700).springify()}
            style={styles.ctaContainer}
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
              <TouchableOpacity
                onPress={() => {
                  console.log('🟢 Button pressed!');
                  handleSubscribe();
                }}
                disabled={isLoading}
                activeOpacity={0.8}
                style={styles.ctaButtonInner}
              >
                {isLoading ? (
                  <ActivityIndicator color="#FFF" />
                ) : (
                  <>
                    <Crown size={22} color="#FFF" />
                    <Text style={styles.ctaButtonText}>
                      {selectedPlan === 'monthly' ? t.startTrial : t.startTrial}
                    </Text>
                  </>
                )}
              </TouchableOpacity>
            </LinearGradient>

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
              Ao assinar, você concorda com os{' '}
              <Text 
                style={[styles.termsLink, { color: premiumColors.primary }]}
                onPress={() => Linking.openURL('https://www.apple.com/legal/internet-services/itunes/dev/stdeula/')}
              >
                Termos de Uso (EULA)
              </Text>
              {' '}e{' '}
              <Text 
                style={[styles.termsLink, { color: premiumColors.primary }]}
                onPress={() => router.push('/settings/privacy')}
              >
                Política de Privacidade
              </Text>
            </Text>
            <Text style={[styles.termsText, { color: theme.textTertiary, marginTop: 8 }]}>
              A assinatura é renovada automaticamente e pode ser gerenciada ou cancelada a qualquer momento nas configurações da sua conta Apple.
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
    shadowColor: '#F59E0B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  ctaButtonInner: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  ctaButtonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '700',
  },
  ctaButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
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
  // Plan Selection Styles
  planContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  planOption: {
    flex: 1,
    padding: spacing.md,
    borderRadius: radius.lg,
    position: 'relative',
    overflow: 'hidden',
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  planTitle: {
    fontSize: 16,
    fontWeight: '700',
  },
  planPrice: {
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 2,
  },
  planPeriod: {
    fontSize: 12,
    fontWeight: '500',
  },
  trialText: {
    fontSize: 11,
    fontWeight: '600',
    marginTop: 4,
  },
  saveBadge: {
    position: 'absolute',
    top: -2,
    right: -2,
    backgroundColor: '#10B981',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderBottomLeftRadius: radius.md,
    borderTopRightRadius: radius.lg,
  },
  saveBadgeText: {
    color: '#FFF',
    fontSize: 11,
    fontWeight: '800',
  },
  termsLink: {
    textDecorationLine: 'underline',
    fontWeight: '600',
  },
});
