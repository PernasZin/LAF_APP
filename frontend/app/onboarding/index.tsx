import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

import BasicInfoStep from './steps/BasicInfoStep';
import PhysicalDataStep from './steps/PhysicalDataStep';
import TrainingLevelStep from './steps/TrainingLevelStep';
import GoalStep from './steps/GoalStep';
import MealConfigStep from './steps/MealConfigStep';
import RestrictionsStep from './steps/RestrictionsStep';

import { useAuthStore } from '../../stores/authStore';
import { useSettingsStore } from '../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../i18n/translations';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function OnboardingScreen() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Auth store - SINGLE SOURCE OF TRUTH
  const userId = useAuthStore((s) => s.userId);
  const setProfileCompleted = useAuthStore((s) => s.setProfileCompleted);
  
  // Language - get from settings store
  const language = useSettingsStore((s) => s.language) as SupportedLanguage;
  const t = translations[language].onboarding;
  
  // Form data state
  const [formData, setFormData] = useState({
    // Básico
    name: '',
    age: '',
    sex: '',
    // Físico
    height: '',
    weight: '',
    target_weight: '',
    body_fat_percentage: '',
    // Treino
    training_level: '',
    weekly_training_frequency: '',
    available_time_per_session: '',
    // Objetivo
    goal: '',
    // Atleta/Competição - NOVO: apenas data, sistema calcula o resto
    athlete_competition_date: '', // ISO date string YYYY-MM-DD
    // Configuração de Refeições
    meal_count: 5,
    meal_times: ['07:00', '10:00', '13:00', '16:00', '20:00'],
    // Restrições
    dietary_restrictions: [] as string[],
    food_preferences: [] as string[],
    injury_history: [] as string[],
  });
  
  console.log('🎯 OnboardingScreen - userId:', userId);

  // Steps - translated titles
  const getMealConfigTitle = () => {
    if (language === 'en-US') return 'Meal Plan';
    if (language === 'es-ES') return 'Plan de Comidas';
    return 'Plano de Refeições';
  };

  const steps = [
    { title: t.steps.basicInfo, component: BasicInfoStep },
    { title: t.steps.physicalData, component: PhysicalDataStep },
    { title: t.steps.trainingLevel, component: TrainingLevelStep },
    { title: t.steps.yourGoal, component: GoalStep },
    { title: getMealConfigTitle(), component: MealConfigStep },
    { title: t.steps.preferences, component: RestrictionsStep },
  ];

  const updateFormData = (data: any) => {
    setFormData({ ...formData, ...data });
  };

  // Step validation keys for translation matching
  const stepValidationKeys = ['basicInfo', 'physicalData', 'trainingLevel', 'yourGoal', 'preferences'];

  const validateCurrentStep = () => {
    console.log('Validating step:', currentStep, 'Data:', formData);
    
    const currentStepKey = stepValidationKeys[currentStep];
    
    switch (currentStepKey) {
      case 'basicInfo':
        if (!formData.name || !formData.age || !formData.sex) {
          Alert.alert(t.requiredFields, t.fillNameAgeSex);
          return false;
        }
        if (parseInt(formData.age) < 15 || parseInt(formData.age) > 100) {
          Alert.alert(t.requiredFields, t.invalidAge);
          return false;
        }
        break;
      
      case 'physicalData':
        if (!formData.height || !formData.weight) {
          Alert.alert(t.requiredFields, t.fillHeightWeight);
          return false;
        }
        if (parseFloat(formData.height) < 100 || parseFloat(formData.height) > 250) {
          Alert.alert(t.requiredFields, t.invalidHeight);
          return false;
        }
        if (parseFloat(formData.weight) < 30 || parseFloat(formData.weight) > 300) {
          Alert.alert(t.requiredFields, t.invalidWeight);
          return false;
        }
        break;
      
      case 'trainingLevel':
        if (!formData.training_level || !formData.weekly_training_frequency || !formData.available_time_per_session) {
          Alert.alert(t.requiredFields, t.fillTrainingFields);
          return false;
        }
        if (parseInt(formData.weekly_training_frequency) < 0 || parseInt(formData.weekly_training_frequency) > 7) {
          Alert.alert(t.requiredFields, t.invalidFrequency);
          return false;
        }
        break;
      
      case 'yourGoal':
        if (!formData.goal) {
          Alert.alert(t.requiredFields, t.selectGoal);
          return false;
        }
        // Se for atleta, data do campeonato é OBRIGATÓRIA
        if (formData.goal === 'atleta' && !formData.athlete_competition_date) {
          Alert.alert(
            t.dateRequired, 
            t.dateRequiredMessage,
            [{ text: 'OK' }]
          );
          return false;
        }
        break;
      
      case 'preferences':
        // Optional step
        break;
    }
    
    return true;
  };

  const handleNext = () => {
    console.log('handleNext called, current step:', currentStep);
    
    if (!validateCurrentStep()) {
      return;
    }
    
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
    console.log('🚀 handleSubmit called');
    
    // CRITICAL: userId must exist from auth
    if (!userId) {
      Alert.alert(t.error, t.sessionExpired);
      router.replace('/auth/login');
      return;
    }
    
    setLoading(true);
    
    try {
      // Prepare profile data - MUST include userId
      const profileData: any = {
        id: userId,  // REQUIRED: links profile to auth user
        name: formData.name.trim(),
        age: parseInt(formData.age),
        sex: formData.sex,
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        target_weight: formData.target_weight ? parseFloat(formData.target_weight) : null,
        body_fat_percentage: formData.body_fat_percentage ? parseFloat(formData.body_fat_percentage) : null,
        training_level: formData.training_level,
        weekly_training_frequency: parseInt(formData.weekly_training_frequency),
        available_time_per_session: parseInt(formData.available_time_per_session),
        goal: formData.goal,
        dietary_restrictions: formData.dietary_restrictions,
        food_preferences: formData.food_preferences,
        injury_history: formData.injury_history,
      };

      // Add athlete-specific field (APENAS a data - backend calcula tudo)
      if (formData.goal === 'atleta' && formData.athlete_competition_date) {
        profileData.athlete_competition_date = formData.athlete_competition_date;
      }

      console.log('📡 Sending to backend:', JSON.stringify(profileData, null, 2));
      console.log('🌐 Backend URL:', `${BACKEND_URL}/api/user/profile`);

      // Call backend - uses UPSERT (idempotent)
      const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Backend error:', errorData);
        throw new Error(errorData.detail || 'Erro ao salvar perfil');
      }

      const data = await response.json();
      console.log('✅ Profile saved:', data.id);

      // SUCCESS: Update auth store - profileCompleted = true
      await setProfileCompleted(true);
      console.log('✅ profileCompleted set to true in authStore');

      // Navigate to tabs - AuthGuard will handle routing
      setLoading(false);
      router.replace('/(tabs)');
      
    } catch (error: any) {
      console.error('❌ Error saving profile:', error);
      
      let errorMessage = t.couldNotSaveProfile;
      if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert(t.error, errorMessage);
      setLoading(false);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity 
            onPress={handleBack} 
            style={styles.backButton}
            disabled={currentStep === 0}
          >
            {currentStep > 0 && (
              <Ionicons name="arrow-back" size={24} color="#374151" />
            )}
          </TouchableOpacity>
          <Text style={styles.headerTitle}>{steps[currentStep].title}</Text>
          <View style={styles.stepIndicator}>
            <Text style={styles.stepText}>{currentStep + 1}/{steps.length}</Text>
          </View>
        </View>

        {/* Progress Bar */}
        <View style={styles.progressBarContainer}>
          <View style={[styles.progressBar, { width: `${progress}%` }]} />
        </View>

        {/* Content */}
        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <CurrentStepComponent 
            data={formData}
            updateData={updateFormData}
            language={language}
          />
        </ScrollView>

        {/* Footer Button */}
        <View style={styles.footer}>
          <TouchableOpacity
            style={[styles.nextButton, loading && styles.nextButtonDisabled]}
            onPress={handleNext}
            disabled={loading}
            activeOpacity={0.8}
          >
            <Text style={styles.nextButtonText}>
              {loading ? t.saving : currentStep === steps.length - 1 ? t.finish : translations[language].common.next}
            </Text>
            {!loading && <Ionicons name="arrow-forward" size={20} color="#fff" />}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
  },
  stepIndicator: {
    width: 40,
    alignItems: 'flex-end',
  },
  stepText: {
    fontSize: 14,
    color: '#10B981',
    fontWeight: '600',
  },
  progressBarContainer: {
    height: 4,
    backgroundColor: '#E5E7EB',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#10B981',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  nextButton: {
    backgroundColor: '#10B981',
    paddingVertical: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  nextButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  nextButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
