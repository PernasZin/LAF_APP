/**
 * LAF Premium Onboarding Screen
 * ==============================
 * Glassmorphism + Gradientes + Animações
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown, FadeInRight, FadeOutLeft } from 'react-native-reanimated';
import { ArrowLeft, ArrowRight, Check, User, Activity, Target, Utensils, Heart, Sparkles } from 'lucide-react-native';

import BasicInfoStep from './steps/BasicInfoStep';
import PhysicalDataStep from './steps/PhysicalDataStep';
import TrainingLevelStep from './steps/TrainingLevelStep';
import GoalStep from './steps/GoalStep';
import MealConfigStep from './steps/MealConfigStep';
import FoodPreferencesStep from './steps/FoodPreferencesStep';

import { useAuthStore } from '../../stores/authStore';
import { useSettingsStore, LanguagePreference } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { translations, SupportedLanguage } from '../../i18n/translations';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const STEP_ICONS = [User, Activity, Target, Target, Utensils, Heart];

export default function OnboardingScreen() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Theme
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  // Auth store
  const userId = useAuthStore((s) => s.userId);
  const setProfileCompleted = useAuthStore((s) => s.setProfileCompleted);
  
  // Language
  const language = useSettingsStore((s) => s.language) as SupportedLanguage;
  const t = translations[language]?.onboarding || translations['pt-BR'].onboarding;
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    sex: '',
    height: '',
    weight: '',
    training_level: '',
    weekly_training_frequency: '',
    available_time_per_session: '',
    goal: '',
    meal_count: 5,
    meal_times: ['07:00', '10:00', '13:00', '16:00', '20:00'],
    dietary_restrictions: [] as string[],
    food_preferences: [] as string[],
    injury_history: [] as string[],
  });

  const steps = [
    { title: t.steps.basicInfo, component: BasicInfoStep },
    { title: t.steps.physicalData, component: PhysicalDataStep },
    { title: t.steps.trainingLevel, component: TrainingLevelStep },
    { title: t.steps.yourGoal, component: GoalStep },
    { title: 'Refeições', component: MealConfigStep },
    { title: t.steps.preferences, component: FoodPreferencesStep },
  ];

  const updateFormData = (data: any) => {
    setFormData({ ...formData, ...data });
  };

  const showAlert = (title: string, message: string) => {
    if (Platform.OS === 'web') {
      window.alert(`${title}\n\n${message}`);
    } else {
      Alert.alert(title, message);
    }
  };

  const validateCurrentStep = () => {
    switch (currentStep) {
      case 0:
        if (!formData.name || !formData.age || !formData.sex) {
          showAlert('Campos obrigatórios', 'Preencha nome, idade e sexo');
          return false;
        }
        break;
      case 1:
        if (!formData.height || !formData.weight) {
          showAlert('Campos obrigatórios', 'Preencha altura e peso');
          return false;
        }
        break;
      case 2:
        if (!formData.training_level) {
          showAlert('Campo obrigatório', 'Selecione seu nível de treino');
          return false;
        }
        break;
      case 3:
        if (!formData.goal) {
          showAlert('Campo obrigatório', 'Selecione seu objetivo');
          return false;
        }
        break;
      case 5:
        // 🚫 VALIDAÇÃO DE ALIMENTOS MÍNIMOS
        // Regras: 2 proteínas, 2 carboidratos, 1 gordura, 1 fruta
        const selectedFoods = formData.food_preferences || [];
        
        // Categorias de alimentos (keys)
        const PROTEIN_KEYS = ['frango', 'patinho', 'carne_moida', 'ovos', 'tilapia', 'atum', 'salmao', 'peru', 'cottage', 'whey_protein', 'iogurte_zero', 'claras'];
        const CARB_KEYS = ['arroz_branco', 'arroz_integral', 'batata_doce', 'macarrao', 'aveia', 'pao_integral', 'pao', 'tapioca', 'feijao', 'lentilha', 'cuscuz'];
        const FAT_KEYS = ['azeite', 'castanhas', 'amendoas', 'nozes', 'pasta_amendoim', 'abacate', 'chia'];
        const FRUIT_KEYS = ['banana', 'maca', 'laranja', 'morango', 'mamao', 'melancia', 'uva', 'pera', 'manga', 'abacaxi', 'kiwi'];
        
        const proteinCount = selectedFoods.filter((f: string) => PROTEIN_KEYS.includes(f)).length;
        const carbCount = selectedFoods.filter((f: string) => CARB_KEYS.includes(f)).length;
        const fatCount = selectedFoods.filter((f: string) => FAT_KEYS.includes(f)).length;
        const fruitCount = selectedFoods.filter((f: string) => FRUIT_KEYS.includes(f)).length;
        
        const missing: string[] = [];
        if (proteinCount < 2) missing.push(`• ${2 - proteinCount} PROTEÍNA(S) (ex: frango, carne, ovos, whey)`);
        if (carbCount < 2) missing.push(`• ${2 - carbCount} CARBOIDRATO(S) (ex: arroz, aveia, pão, batata)`);
        if (fatCount < 1) missing.push(`• 1 GORDURA (ex: azeite, pasta de amendoim, castanhas)`);
        if (fruitCount < 1) missing.push(`• 1 FRUTA (ex: banana, maçã, morango)`);
        
        if (missing.length > 0) {
          const message = `Para garantir que a IA consiga montar uma dieta completa para você, é necessário selecionar no mínimo:\n\n• 2 PROTEÍNAS\n• 2 CARBOIDRATOS\n• 1 GORDURA\n• 1 FRUTA\n\nFalta adicionar:\n${missing.join('\n')}\n\nAdicione os alimentos que faltam e tente novamente.`;
          showAlert('Seleção insuficiente', message);
          return false;
        }
        break;
    }
    return true;
  };

  const handleNext = () => {
    if (!validateCurrentStep()) return;
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const profileData = {
        id: userId,
        name: formData.name,
        age: parseInt(formData.age) || 25,
        sex: formData.sex,
        height: parseInt(formData.height) || 170,
        weight: parseFloat(formData.weight) || 70,
        goal: formData.goal || 'manutencao',
        training_level: formData.training_level || 'iniciante',
        weekly_training_frequency: parseInt(formData.weekly_training_frequency) || 3,
        available_time_per_session: parseInt(formData.available_time_per_session) || 60,
        dietary_restrictions: formData.dietary_restrictions,
        food_preferences: formData.food_preferences,
        injury_history: formData.injury_history,
        meal_count: formData.meal_count,
        meal_times: formData.meal_times,
      };

      const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        await AsyncStorage.setItem('hasCompletedOnboarding', 'true');
        await AsyncStorage.setItem('profileCompleted', 'true');
        await setProfileCompleted(true);
        router.replace('/(tabs)');
      } else {
        const error = await response.json();
        showAlert('Erro', error.detail || 'Não foi possível salvar o perfil');
      }
    } catch (error) {
      console.error('Submit error:', error);
      showAlert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setLoading(false);
    }
  };

  const StepComponent = steps[currentStep].component;
  const StepIcon = STEP_ICONS[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark 
          ? ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']
          : ['rgba(16, 185, 129, 0.1)', 'transparent', 'rgba(59, 130, 246, 0.08)']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />
      
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <View style={styles.headerTop}>
              {currentStep > 0 ? (
                <TouchableOpacity onPress={handleBack} style={styles.backButton}>
                  <ArrowLeft size={24} color={theme.text} />
                </TouchableOpacity>
              ) : (
                <View style={styles.backButton} />
              )}
              
              <View style={[styles.stepBadge, { backgroundColor: `${premiumColors.primary}20` }]}>
                <StepIcon size={18} color={premiumColors.primary} />
                <Text style={[styles.stepBadgeText, { color: premiumColors.primary }]}>
                  {currentStep + 1}/{steps.length}
                </Text>
              </View>
              
              <View style={styles.backButton} />
            </View>
            
            {/* Progress Bar */}
            <View style={[styles.progressContainer, { backgroundColor: theme.border }]}>
              <LinearGradient
                colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={[styles.progressBar, { width: `${progress}%` }]}
              />
            </View>
            
            <Text style={[styles.stepTitle, { color: theme.text }]}>
              {steps[currentStep].title}
            </Text>
          </Animated.View>

          {/* Content */}
          <ScrollView 
            style={styles.content}
            contentContainerStyle={styles.contentContainer}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            <StepComponent
              formData={formData}
              updateFormData={updateFormData}
              theme={theme}
              isDark={isDark}
            />
          </ScrollView>

          {/* Footer */}
          <Animated.View entering={FadeInDown.delay(200).springify()} style={styles.footer}>
            <TouchableOpacity
              onPress={handleNext}
              disabled={loading}
              activeOpacity={0.9}
            >
              <LinearGradient
                colors={[premiumColors.gradient.start, premiumColors.gradient.middle, premiumColors.gradient.end]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.nextButton}
              >
                {loading ? (
                  <ActivityIndicator color="#FFF" />
                ) : (
                  <>
                    <Text style={styles.nextButtonText}>
                      {currentStep === steps.length - 1 ? 'Finalizar' : 'Continuar'}
                    </Text>
                    {currentStep === steps.length - 1 ? (
                      <Check size={20} color="#FFF" strokeWidth={3} />
                    ) : (
                      <ArrowRight size={20} color="#FFF" strokeWidth={2.5} />
                    )}
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  keyboardView: { flex: 1 },
  
  header: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.md,
    paddingBottom: spacing.lg,
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  backButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.full,
    gap: spacing.xs,
  },
  stepBadgeText: {
    fontSize: 14,
    fontWeight: '700',
  },
  progressContainer: {
    height: 6,
    borderRadius: radius.full,
    marginBottom: spacing.lg,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    borderRadius: radius.full,
  },
  stepTitle: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -0.5,
    textAlign: 'center',
  },
  
  content: { flex: 1 },
  contentContainer: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing['2xl'],
  },
  
  footer: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.xl,
    paddingTop: spacing.md,
  },
  nextButton: {
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
  nextButtonText: {
    color: '#FFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
});
