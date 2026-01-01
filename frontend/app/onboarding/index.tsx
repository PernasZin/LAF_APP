import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import BasicInfoStep from './steps/BasicInfoStep';
import PhysicalDataStep from './steps/PhysicalDataStep';
import TrainingLevelStep from './steps/TrainingLevelStep';
import GoalStep from './steps/GoalStep';
import AthleteStep from './steps/AthleteStep';
import RestrictionsStep from './steps/RestrictionsStep';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Safe fetch with configurable timeout for onboarding
const safeFetch = async (url: string, options?: RequestInit, timeout = 15000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);
    // Defensive check for error properties
    const errorName = typeof error?.name === 'string' ? error.name : '';
    if (errorName === 'AbortError') {
      throw new Error('A requisição demorou muito tempo. Verifique sua conexão.');
    }
    throw error;
  }
};

// Utility to safely extract error message
const getErrorMessage = (error: unknown): string => {
  if (error === null || error === undefined) {
    return 'Erro desconhecido';
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof Error) {
    return error.message || 'Erro desconhecido';
  }
  
  if (typeof error === 'object') {
    const err = error as any;
    if (typeof err.message === 'string') {
      return err.message;
    }
    if (typeof err.detail === 'string') {
      return err.detail;
    }
  }
  
  return 'Erro desconhecido';
};

// Utility to safely check if error is timeout-related
const isTimeoutError = (error: unknown): boolean => {
  if (error === null || error === undefined) {
    return false;
  }
  
  const message = getErrorMessage(error);
  const code = typeof (error as any)?.code === 'string' ? (error as any).code : '';
  const name = typeof (error as any)?.name === 'string' ? (error as any).name : '';
  
  return (
    code === 'ECONNABORTED' ||
    name === 'AbortError' ||
    message.toLowerCase().includes('timeout') ||
    message.toLowerCase().includes('demorou')
  );
};

// Utility to safely check if error is network-related
const isNetworkError = (error: unknown): boolean => {
  if (error === null || error === undefined) {
    return false;
  }
  
  const message = getErrorMessage(error);
  const hasResponse = typeof (error as any)?.response === 'object' && (error as any).response !== null;
  
  return (
    message === 'Network Error' ||
    message.toLowerCase().includes('network') ||
    message.toLowerCase().includes('conexão') ||
    (!hasResponse && message.toLowerCase().includes('fetch'))
  );
};

export default function OnboardingScreen() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  
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
    // Atleta/Competição (OBRIGATÓRIO se goal === 'atleta')
    weeks_to_competition: '',
    competition_phase: '',
    competition_phase_manual: false,
    competition_start_date: null as Date | null,
    // Restrições
    dietary_restrictions: [] as string[],
    food_preferences: [] as string[],
    injury_history: [] as string[],
  });
  
  console.log('🎯 OnboardingScreen mounted. Backend URL:', BACKEND_URL);

  // Verifica se já completou onboarding
  React.useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      const hasCompleted = await AsyncStorage.getItem('hasCompletedOnboarding');
      const userId = await AsyncStorage.getItem('userId');
      
      console.log('📋 Checking onboarding status:', { hasCompleted, userId });
      
      if (hasCompleted === 'true' && userId) {
        console.log('✅ Onboarding already completed, redirecting to home');
        router.replace('/(tabs)');
        return;
      }
    } catch (error) {
      console.error('Error checking onboarding status:', error);
    } finally {
      setIsChecking(false);
    }
  };

  // Mostra loading enquanto verifica status
  if (isChecking) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Text style={{ fontSize: 16, color: '#6B7280' }}>Carregando...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Dynamic steps based on goal selection
  const getSteps = () => {
    const baseSteps = [
      { title: 'Dados Básicos', component: BasicInfoStep },
      { title: 'Dados Físicos', component: PhysicalDataStep },
      { title: 'Nível de Treino', component: TrainingLevelStep },
      { title: 'Seu Objetivo', component: GoalStep },
    ];
    
    // Add athlete step if goal is 'atleta'
    if (formData.goal === 'atleta') {
      baseSteps.push({ title: 'Competição', component: AthleteStep });
    }
    
    baseSteps.push({ title: 'Preferências', component: RestrictionsStep });
    
    return baseSteps;
  };

  const steps = getSteps();

  const updateFormData = (data: any) => {
    setFormData({ ...formData, ...data });
  };

  const validateCurrentStep = () => {
    console.log('Validating step:', currentStep, 'Data:', formData);
    
    // Find which step we're validating based on current position
    const currentStepTitle = steps[currentStep]?.title;
    
    switch (currentStepTitle) {
      case 'Dados Básicos':
        if (!formData.name || !formData.age || !formData.sex) {
          Alert.alert('Campos Obrigatórios', 'Preencha nome, idade e sexo.');
          return false;
        }
        if (parseInt(formData.age) < 15 || parseInt(formData.age) > 100) {
          Alert.alert('Idade Inválida', 'Idade deve estar entre 15 e 100 anos.');
          return false;
        }
        break;
      
      case 'Dados Físicos':
        if (!formData.height || !formData.weight) {
          Alert.alert('Campos Obrigatórios', 'Preencha altura e peso atual.');
          return false;
        }
        if (parseFloat(formData.height) < 100 || parseFloat(formData.height) > 250) {
          Alert.alert('Altura Inválida', 'Altura deve estar entre 100cm e 250cm.');
          return false;
        }
        if (parseFloat(formData.weight) < 30 || parseFloat(formData.weight) > 300) {
          Alert.alert('Peso Inválido', 'Peso deve estar entre 30kg e 300kg.');
          return false;
        }
        break;
      
      case 'Nível de Treino':
        if (!formData.training_level || !formData.weekly_training_frequency || !formData.available_time_per_session) {
          Alert.alert('Campos Obrigatórios', 'Preencha todos os campos de treino.');
          return false;
        }
        if (parseInt(formData.weekly_training_frequency) < 0 || parseInt(formData.weekly_training_frequency) > 7) {
          Alert.alert('Frequência Inválida', 'Frequência deve estar entre 0 e 7 dias por semana.');
          return false;
        }
        break;
      
      case 'Seu Objetivo':
        if (!formData.goal) {
          Alert.alert('Objetivo Obrigatório', 'Selecione seu objetivo principal.');
          return false;
        }
        break;
      
      case 'Competição':
        // Athlete-specific validation
        if (formData.goal === 'atleta') {
          if (!formData.competition_phase) {
            Alert.alert('Fase Obrigatória', 'Selecione sua fase de competição atual.');
            return false;
          }
          if (!formData.weeks_to_competition || parseInt(formData.weeks_to_competition) < 0) {
            Alert.alert('Semanas Obrigatórias', 'Informe as semanas até sua próxima competição.');
            return false;
          }
        }
        break;
      
      case 'Preferências':
        // Este step é opcional
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
    } else {
      router.back();
    }
  };

  const handleSubmit = async () => {
    console.log('🚀 handleSubmit called');
    console.log('📦 Form data:', JSON.stringify(formData, null, 2));
    
    setLoading(true);
    
    try {
      // Prepara dados para API
      const profileData: any = {
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

      // Add athlete-specific fields
      if (formData.goal === 'atleta') {
        profileData.competition_phase = formData.competition_phase;
        profileData.weeks_to_competition = parseInt(formData.weeks_to_competition);
        // Calculate competition date for timeline tracking
        if (formData.weeks_to_competition) {
          const competitionDate = new Date();
          competitionDate.setDate(competitionDate.getDate() + (parseInt(formData.weeks_to_competition) * 7));
          profileData.competition_date = competitionDate.toISOString();
        }
      }

      console.log('📡 Sending to backend:', JSON.stringify(profileData, null, 2));
      console.log('🌐 Backend URL:', `${BACKEND_URL}/api/user/profile`);

      // Cria perfil no backend com safeFetch (timeout + abort signal)
      const response = await safeFetch(
        `${BACKEND_URL}/api/user/profile`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profileData),
        },
        15000 // 15 segundos timeout
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw { response: { status: response.status, data: errorData } };
      }

      const data = await response.json();
      console.log('✅ Response received:', response.status, data);

      // Valida resposta
      if (!data || !data.id) {
        throw new Error('Resposta inválida do servidor - ID não encontrado');
      }

      if (!data.tdee || !data.target_calories || !data.macros) {
        throw new Error('Dados incompletos retornados pelo servidor');
      }

      // Salva perfil localmente
      await AsyncStorage.setItem('userId', data.id);
      await AsyncStorage.setItem('userProfile', JSON.stringify(data));
      await AsyncStorage.setItem('hasCompletedOnboarding', 'true');

      console.log('💾 Profile saved to AsyncStorage');
      console.log('🏠 Navigating to home immediately');

      // Navegação imediata sem Alert
      setLoading(false);
      router.replace('/(tabs)');
      
    } catch (error: unknown) {
      console.error('❌ Erro ao criar perfil:', error);
      
      // DEFENSIVE ERROR HANDLING - Never crash on malformed errors
      let errorMessage = 'Não foi possível criar seu perfil. ';
      
      try {
        // Safe extraction of error details
        const errorObj = error as any;
        const responseStatus = errorObj?.response?.status;
        const responseData = errorObj?.response?.data;
        const responseDetail = typeof responseData?.detail === 'string' ? responseData.detail : '';
        
        console.error('❌ Error details:', {
          message: getErrorMessage(error),
          status: responseStatus,
          detail: responseDetail,
        });
        
        if (isTimeoutError(error)) {
          errorMessage += 'A requisição demorou muito tempo. Verifique sua conexão e tente novamente.';
        } else if (isNetworkError(error)) {
          errorMessage += 'Sem conexão com o servidor. Verifique sua internet.';
        } else if (responseStatus === 400) {
          errorMessage += responseDetail || 'Dados inválidos. Verifique os campos preenchidos.';
        } else if (responseStatus === 500) {
          errorMessage += 'Erro no servidor. Tente novamente em alguns instantes.';
        } else if (responseDetail) {
          errorMessage += responseDetail;
        } else {
          const msg = getErrorMessage(error);
          errorMessage += msg !== 'Erro desconhecido' ? msg : 'Tente novamente.';
        }
      } catch (extractionError) {
        // Even error extraction failed - use safest fallback
        console.error('❌ Error extraction failed:', extractionError);
        errorMessage += 'Tente novamente.';
      }
      
      Alert.alert(
        'Erro ao Criar Perfil',
        `${errorMessage}\n\nDeseja tentar novamente?`,
        [
          {
            text: 'Cancelar',
            style: 'cancel',
          },
          {
            text: 'Tentar Novamente',
            onPress: () => handleSubmit(),
            style: 'default',
          }
        ]
      );
    } finally {
      setLoading(false);
      console.log('🏁 handleSubmit completed');
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
          <TouchableOpacity onPress={handleBack} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#374151" />
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
              {loading ? 'Criando perfil...' : currentStep === steps.length - 1 ? 'Finalizar' : 'Próximo'}
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
