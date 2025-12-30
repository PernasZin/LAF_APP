import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

import BasicInfoStep from './steps/BasicInfoStep';
import PhysicalDataStep from './steps/PhysicalDataStep';
import TrainingLevelStep from './steps/TrainingLevelStep';
import GoalStep from './steps/GoalStep';
import RestrictionsStep from './steps/RestrictionsStep';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function OnboardingScreen() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  
  console.log('🎯 OnboardingScreen mounted. Backend URL:', BACKEND_URL);
  
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
    // Restrições
    dietary_restrictions: [] as string[],
    food_preferences: [] as string[],
    injury_history: [] as string[],
  });

  const steps = [
    { title: 'Dados Básicos', component: BasicInfoStep },
    { title: 'Dados Físicos', component: PhysicalDataStep },
    { title: 'Nível de Treino', component: TrainingLevelStep },
    { title: 'Seu Objetivo', component: GoalStep },
    { title: 'Preferências', component: RestrictionsStep },
  ];

  const updateFormData = (data: any) => {
    setFormData({ ...formData, ...data });
  };

  const validateCurrentStep = () => {
    console.log('Validating step:', currentStep, 'Data:', formData);
    
    switch (currentStep) {
      case 0: // Dados Básicos
        if (!formData.name || !formData.age || !formData.sex) {
          Alert.alert('Campos Obrigatórios', 'Preencha nome, idade e sexo.');
          return false;
        }
        if (parseInt(formData.age) < 15 || parseInt(formData.age) > 100) {
          Alert.alert('Idade Inválida', 'Idade deve estar entre 15 e 100 anos.');
          return false;
        }
        break;
      
      case 1: // Dados Físicos
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
      
      case 2: // Nível de Treino
        if (!formData.training_level || !formData.weekly_training_frequency || !formData.available_time_per_session) {
          Alert.alert('Campos Obrigatórios', 'Preencha todos os campos de treino.');
          return false;
        }
        if (parseInt(formData.weekly_training_frequency) < 0 || parseInt(formData.weekly_training_frequency) > 7) {
          Alert.alert('Frequência Inválida', 'Frequência deve estar entre 0 e 7 dias por semana.');
          return false;
        }
        break;
      
      case 3: // Objetivo
        if (!formData.goal) {
          Alert.alert('Objetivo Obrigatório', 'Selecione seu objetivo principal.');
          return false;
        }
        break;
      
      case 4: // Preferências (opcional)
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
      const profileData = {
        name: formData.name,
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

      console.log('📡 Sending to backend:', JSON.stringify(profileData, null, 2));
      console.log('🌐 Backend URL:', `${BACKEND_URL}/api/user/profile`);

      // Cria perfil no backend
      const response = await axios.post(
        `${BACKEND_URL}/api/user/profile`,
        profileData
      );

      console.log('✅ Response received:', response.status, response.data);

      // Salva ID do usuário localmente
      await AsyncStorage.setItem('userId', response.data.id);
      await AsyncStorage.setItem('userProfile', JSON.stringify(response.data));

      console.log('💾 Profile saved to AsyncStorage');

      Alert.alert(
        'Perfil Criado! ✅',
        `Seu perfil foi configurado com sucesso!\n\nTDEE: ${response.data.tdee} kcal/dia\nMeta: ${response.data.target_calories} kcal/dia`,
        [
          {
            text: 'Continuar',
            onPress: () => {
              console.log('🏠 Navigating to home');
              router.replace('/home/');
            },
          },
        ]
      );
    } catch (error: any) {
      console.error('❌ Erro ao criar perfil:', error);
      console.error('❌ Error details:', error.response?.data || error.message);
      Alert.alert(
        'Erro',
        `Não foi possível criar seu perfil.\n\nDetalhes: ${error.response?.data?.detail || error.message || 'Erro desconhecido'}`
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