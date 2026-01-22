/**
 * LAF Premium Workout Screen
 * ==========================
 * Sistema de Ciclo Automático de Treino/Descanso
 * Com Timer Ativo e Botão "Iniciar Treino"
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, RefreshControl, Modal, Alert, Dimensions
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import {
  Dumbbell, Timer, Play, Pause, RotateCcw, ChevronRight,
  X, Check, Target, Flame, Calendar, Clock, Repeat,
  Moon, Sun, CheckCircle, Square, StopCircle, History, Award
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { WorkoutSkeleton } from '../../components';
import { useTranslation, translateExercise, translateWorkoutName, translateExerciseFocus, translateWorkoutDayName, translateWorkoutNotes } from '../../i18n';

import { config } from '../../config';
const BACKEND_URL = config.BACKEND_URL;

const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

// ==================== COMPONENTS ====================

// Glass Card Component
const GlassCard = ({ children, style, isDark, onPress }: any) => {
  const cardStyle = {
    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
    borderWidth: 1,
    borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
    borderRadius: radius.xl,
    overflow: 'hidden' as const,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: isDark ? 0.3 : 0.08,
    shadowRadius: 16,
    elevation: 8,
  };
  if (onPress) {
    return <TouchableOpacity onPress={onPress} activeOpacity={0.8} style={[cardStyle, style]}>{children}</TouchableOpacity>;
  }
  return <View style={[cardStyle, style]}>{children}</View>;
};

// Day Type Badge Component
const DayTypeBadge = ({ dayType, dietType, workoutStatus, isDark, theme }: { 
  dayType: 'train' | 'rest', 
  dietType?: 'training' | 'rest',
  workoutStatus?: string,
  isDark: boolean, 
  theme: any 
}) => {
  const isTrainingDay = dayType === 'train';
  const isTrainingDiet = dietType === 'training';
  
  // Determina cor e ícone baseado na dieta atual
  const badgeColor = isTrainingDiet ? premiumColors.primary : '#6B7280';
  
  // Texto dinâmico
  let badgeText = '';
  if (isTrainingDay) {
    badgeText = 'Dia de Treino';
  } else if (workoutStatus === 'bonus') {
    badgeText = 'Treino Bônus!';
  } else {
    badgeText = 'Dia de Descanso';
  }
  
  return (
    <View style={[
      styles.dayTypeBadge,
      { backgroundColor: badgeColor + '20' }
    ]}>
      {isTrainingDiet ? (
        <Dumbbell size={16} color={badgeColor} />
      ) : (
        <Moon size={16} color={badgeColor} />
      )}
      <Text style={[
        styles.dayTypeBadgeText,
        { color: badgeColor }
      ]}>
        {badgeText}
      </Text>
    </View>
  );
};

// Simple Finish Workout Component
const FinishWorkoutCard = ({ 
  onFinish,
  isDark,
  theme,
  tomorrowIsRest,
  trainingPhrase,
  tomorrowPhrase
}: any) => {
  return (
    <Animated.View entering={FadeInDown.springify()}>
      <GlassCard isDark={isDark} style={styles.finishWorkoutCard}>
        <LinearGradient
          colors={[premiumColors.primary + '15', premiumColors.accent + '10']}
          style={StyleSheet.absoluteFill}
        />
        
        <View style={styles.finishWorkoutContent}>
          <View style={[styles.finishIconBg, { backgroundColor: premiumColors.primary + '20' }]}>
            <Dumbbell size={32} color={premiumColors.primary} strokeWidth={2} />
          </View>
          
          <Text style={[styles.finishWorkoutTitle, { color: theme.text }]}>
            {trainingPhrase}
          </Text>
          
          <TouchableOpacity style={styles.finishTodayBtn} onPress={onFinish}>
            <LinearGradient
              colors={['#10B981', '#059669']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.finishTodayBtnGradient}
            >
              <CheckCircle size={22} color="#FFF" />
              <Text style={styles.finishTodayBtnText}>Finalizar Treino de Hoje</Text>
            </LinearGradient>
          </TouchableOpacity>
          
          <Text style={[styles.motivationPhrase, { color: theme.textSecondary }]}>
            {tomorrowPhrase}
          </Text>
        </View>
      </GlassCard>
    </Animated.View>
  );
};

// Workout Day Card
const WorkoutDayCard = ({ day, index, isDark, theme, onExercisePress, language, t, isToday }: any) => {
  const totalExercises = day.exercises?.length || 0;
  const todayLabel = language === 'en-US' ? 'TODAY' : language === 'es-ES' ? 'HOY' : 'HOJE';
  
  return (
    <Animated.View entering={FadeInDown.delay(index * 100).springify()}>
      <GlassCard isDark={isDark} style={[styles.dayCard, isToday && styles.todayCard]}>
        {isToday && (
          <LinearGradient
            colors={[premiumColors.primary + '10', 'transparent']}
            style={StyleSheet.absoluteFill}
          />
        )}
        
        {/* Day Header */}
        <View style={styles.dayHeader}>
          <View style={[styles.dayIconBg, { backgroundColor: isToday ? premiumColors.primary + '20' : 'rgba(107, 114, 128, 0.15)' }]}>
            <Dumbbell size={22} color={isToday ? premiumColors.primary : '#6B7280'} strokeWidth={2.5} />
          </View>
          <View style={styles.dayHeaderContent}>
            <View style={styles.dayTitleRow}>
              <Text style={[styles.dayName, { color: theme.text }]}>
                {translateWorkoutDayName(day.name || `Dia ${index + 1}`, language)}
              </Text>
              {isToday && (
                <View style={[styles.todayBadge, { backgroundColor: premiumColors.primary }]}>
                  <Text style={styles.todayBadgeText}>{todayLabel}</Text>
                </View>
              )}
            </View>
            <Text style={[styles.dayExerciseCount, { color: theme.textTertiary }]}>
              {totalExercises} {t.workout.exercises}
            </Text>
          </View>
        </View>

        {/* Exercises List */}
        <View style={styles.exercisesList}>
          {day.exercises?.map((exercise: any, exIndex: number) => (
            <TouchableOpacity
              key={exIndex}
              style={[styles.exerciseItem, { borderBottomColor: theme.border }]}
              onPress={() => onExercisePress(exercise, index, exIndex)}
              activeOpacity={0.7}
            >
              <View style={styles.exerciseInfo}>
                <Text style={[styles.exerciseName, { color: theme.text }]} numberOfLines={1}>
                  {translateExercise(exercise.name, language)}
                </Text>
                {exercise.focus && (
                  <Text style={[styles.exerciseFocus, { color: premiumColors.primary }]} numberOfLines={1}>
                    {translateExerciseFocus(exercise.focus, language)}
                  </Text>
                )}
                <View style={styles.exerciseDetails}>
                  <View style={styles.exerciseDetail}>
                    <Repeat size={12} color={theme.textTertiary} />
                    <Text style={[styles.exerciseDetailText, { color: theme.textTertiary }]}>
                      {exercise.sets || 3} x {exercise.reps || '8-12'}
                    </Text>
                  </View>
                  {exercise.rest && (
                    <View style={styles.exerciseDetail}>
                      <Timer size={12} color={theme.textTertiary} />
                      <Text style={[styles.exerciseDetailText, { color: theme.textTertiary }]}>
                        {exercise.rest}s
                      </Text>
                    </View>
                  )}
                </View>
              </View>
              <ChevronRight size={18} color={theme.textTertiary} />
            </TouchableOpacity>
          ))}
        </View>
      </GlassCard>
    </Animated.View>
  );
};

// ==================== MAIN SCREEN ====================

export default function WorkoutScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t, language } = useTranslation();

  const [initialLoading, setInitialLoading] = useState(true);
  const [workoutPlan, setWorkoutPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Cycle status
  const [cycleStatus, setCycleStatus] = useState<any>(null);
  const [dayType, setDayType] = useState<'train' | 'rest'>('rest');
  const [dietType, setDietType] = useState<'training' | 'rest'>('rest');
  const [workoutStatus, setWorkoutStatus] = useState<string>('rest');
  const [isTrainingBlocked, setIsTrainingBlocked] = useState(false);
  const [tomorrowIsRest, setTomorrowIsRest] = useState(false);

  // Training session state
  const [isTraining, setIsTraining] = useState(false);
  const [trainingSeconds, setTrainingSeconds] = useState(0);
  const [sessionStartedAt, setSessionStartedAt] = useState<string | null>(null);
  const [hasTrainedToday, setHasTrainedToday] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimestampRef = useRef<number | null>(null); // Timestamp de início para calcular tempo real

  // Rest timer state - com persistência para pausar/continuar
  const [restTimerActive, setRestTimerActive] = useState(false);
  const [restTimerSeconds, setRestTimerSeconds] = useState(0);
  const [restTimerInitialSeconds, setRestTimerInitialSeconds] = useState(0); // Para resetar
  const [restTimerPaused, setRestTimerPaused] = useState(false);
  const restTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Exercise modal
  const [selectedExercise, setSelectedExercise] = useState<any>(null);
  const [showExerciseModal, setShowExerciseModal] = useState(false);

  // History modal
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [workoutHistory, setWorkoutHistory] = useState<any[]>([]);
  const [historyStats, setHistoryStats] = useState<any>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Frases motivacionais - fixas até sair da tela
  const [trainingPhrase, setTrainingPhrase] = useState('');
  const [tomorrowPhrase, setTomorrowPhrase] = useState('');
  
  // Índice do treino atual (A=0, B=1, C=2, D=3)
  const [currentWorkoutIndex, setCurrentWorkoutIndex] = useState(0);

  // ==================== EFFECTS ====================

  // Gera frases aleatórias ao entrar na tela
  useFocusEffect(
    useCallback(() => {
      // Frases motivacionais
      const trainingPhrases = [
        "💪 Bora treinar! Cada repetição conta.",
        "🔥 Hoje é dia de evoluir!",
        "⚡ Seu futuro eu agradece o treino de hoje.",
        "🎯 Foco no objetivo, bora!"
      ];
      
      const restPhrases = [
        "😴 Amanhã é descanso! Aproveite para recuperar.",
        "🛌 Descanse bem, músculos crescem no repouso!",
        "✨ Amanhã relaxe, você merece!",
        "🌙 Recuperação é parte do treino!"
      ];
      
      const nextTrainingPhrases = [
        "💥 Amanhã tem mais! Prepare-se.",
        "🚀 Descanse hoje, amanhã você volta ainda mais forte!",
        "⭐ Boa recuperação para o treino de amanhã!"
      ];
      
      // Escolhe frases aleatórias
      setTrainingPhrase(trainingPhrases[Math.floor(Math.random() * trainingPhrases.length)]);
      
      // A frase de amanhã será atualizada quando tomorrowIsRest mudar
      // Por enquanto, define uma padrão
      setTomorrowPhrase(nextTrainingPhrases[Math.floor(Math.random() * nextTrainingPhrases.length)]);
      
      // Carrega dados
      loadData();
      
      return () => {
        // Ao sair, apenas limpa intervals - NÃO para o timer
        // O tempo real continua sendo calculado pelo timestamp
        if (timerRef.current) clearInterval(timerRef.current);
        if (restTimerRef.current) clearInterval(restTimerRef.current);
      };
    }, [])
  );
  
  // Efeito para restaurar timer ao voltar para a tela
  useEffect(() => {
    const restoreTimerIfNeeded = async () => {
      // Se já está treinando, não precisa restaurar
      if (isTraining && startTimestampRef.current) return;
      
      // Verifica se tem timestamp salvo
      const savedTimestamp = await AsyncStorage.getItem('training_start_timestamp');
      if (savedTimestamp) {
        const timestamp = parseInt(savedTimestamp, 10);
        if (!isNaN(timestamp) && timestamp > 0) {
          // Verifica se é de hoje
          const savedDate = new Date(timestamp);
          const today = new Date();
          if (savedDate.toDateString() === today.toDateString()) {
            startTimestampRef.current = timestamp;
            setIsTraining(true);
          }
        }
      }
    };
    
    restoreTimerIfNeeded();
  }, []);

  // Atualiza a frase de amanhã quando tomorrowIsRest muda
  useEffect(() => {
    const restPhrases = [
      "😴 Amanhã é descanso! Aproveite para recuperar.",
      "🛌 Descanse bem, músculos crescem no repouso!",
      "✨ Amanhã relaxe, você merece!",
      "🌙 Recuperação é parte do treino!"
    ];
    
    const nextTrainingPhrases = [
      "💥 Amanhã tem mais! Prepare-se.",
      "🚀 Descanse hoje, amanhã você volta ainda mais forte!",
      "⭐ Boa recuperação para o treino de amanhã!"
    ];
    
    if (tomorrowIsRest) {
      setTomorrowPhrase(restPhrases[Math.floor(Math.random() * restPhrases.length)]);
    } else {
      setTomorrowPhrase(nextTrainingPhrases[Math.floor(Math.random() * nextTrainingPhrases.length)]);
    }
  }, [tomorrowIsRest]);

  // Training timer effect - usa timestamp para calcular tempo real
  useEffect(() => {
    if (isTraining && startTimestampRef.current) {
      // Calcula tempo decorrido baseado no timestamp de início
      const updateTimer = () => {
        const now = Date.now();
        const elapsed = Math.floor((now - startTimestampRef.current!) / 1000);
        setTrainingSeconds(elapsed);
      };
      
      // Atualiza imediatamente
      updateTimer();
      
      // Atualiza a cada segundo
      timerRef.current = setInterval(updateTimer, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isTraining]);

  // ==================== FUNCTIONS ====================

  const loadData = async () => {
    try {
      setInitialLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        // Load cycle status
        await loadCycleStatus(id);
        
        // Load workout plan
        const response = await safeFetch(`${BACKEND_URL}/api/workout/${id}`);
        if (response.ok) {
          const data = await response.json();
          setWorkoutPlan(data);
          
          // Carrega o índice do treino salvo (se existir)
          const savedIndex = await AsyncStorage.getItem('next_workout_index');
          if (savedIndex) {
            const index = parseInt(savedIndex, 10);
            if (!isNaN(index) && index >= 0 && index < (data.workout_days?.length || 4)) {
              setCurrentWorkoutIndex(index);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error loading workout:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const loadCycleStatus = async (id: string) => {
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/training-cycle/status/${id}`);
      if (response.ok) {
        const data = await response.json();
        setCycleStatus(data);
        setDayType(data.planned_day_type || data.day_type);
        setDietType(data.diet?.type || 'rest');
        setWorkoutStatus(data.workout_status || 'rest');
        setHasTrainedToday(data.has_trained_today);
        setIsTrainingBlocked(data.is_training_blocked || false);
        
        // Calcula se amanhã é dia de descanso
        const trainingDays = data.training_days || [];
        if (trainingDays.length > 0) {
          const tomorrow = new Date();
          tomorrow.setDate(tomorrow.getDate() + 1);
          const tomorrowWeekday = (tomorrow.getDay()) ; // 0=Domingo, 1=Segunda, etc
          setTomorrowIsRest(!trainingDays.includes(tomorrowWeekday));
        } else {
          // Se não tem training_days, assume que amanhã é treino
          setTomorrowIsRest(false);
        }
        
        // Define o índice do treino atual baseado no backend
        if (data.today_workout_index !== undefined) {
          setCurrentWorkoutIndex(data.today_workout_index);
        }
        
        // Se treino em andamento no backend
        if (data.is_training_in_progress && data.training_session?.started_at) {
          setSessionStartedAt(data.training_session.started_at);
          
          // Verifica se tem timestamp local salvo
          const savedTimestamp = await AsyncStorage.getItem('training_start_timestamp');
          if (savedTimestamp) {
            const timestamp = parseInt(savedTimestamp, 10);
            if (!isNaN(timestamp) && timestamp > 0) {
              startTimestampRef.current = timestamp;
              setIsTraining(true);
              return;
            }
          }
          
          // Se não tem timestamp local, usa o do servidor
          const startTime = new Date(data.training_session.started_at).getTime();
          startTimestampRef.current = startTime;
          await AsyncStorage.setItem('training_start_timestamp', startTime.toString());
          setIsTraining(true);
        } else {
          // Não há treino em andamento - limpa timestamp
          startTimestampRef.current = null;
          await AsyncStorage.removeItem('training_start_timestamp');
        }
      }
    } catch (error) {
      console.error('Error loading cycle status:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  // Carrega apenas o plano de treino (usado após finalizar)
  const loadWorkoutPlan = async (id: string) => {
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/${id}`);
      if (response.ok) {
        const data = await response.json();
        setWorkoutPlan(data);
      }
    } catch (error) {
      console.error('Error loading workout plan:', error);
    }
  };

  // Start workout
  const startWorkout = async () => {
    if (!userId || !BACKEND_URL) return;
    
    if (hasTrainedToday) {
      Alert.alert('Treino Concluído', 'Você já treinou hoje! Descanse e volte amanhã. 💪');
      return;
    }

    try {
      // Verifica se já existe uma sessão em andamento no backend
      const statusResponse = await safeFetch(`${BACKEND_URL}/api/training-cycle/status/${userId}`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        if (statusData.is_training_in_progress && statusData.training_session?.started_at) {
          // Sessão já existe - restaura o timestamp
          const startTime = new Date(statusData.training_session.started_at).getTime();
          startTimestampRef.current = startTime;
          await AsyncStorage.setItem('training_start_timestamp', startTime.toString());
          setIsTraining(true);
          return;
        }
      }

      // Verifica se há timestamp salvo localmente
      const savedTimestamp = await AsyncStorage.getItem('training_start_timestamp');
      if (savedTimestamp) {
        const timestamp = parseInt(savedTimestamp, 10);
        if (!isNaN(timestamp) && timestamp > 0) {
          // Verifica se o timestamp é de hoje
          const savedDate = new Date(timestamp);
          const today = new Date();
          if (savedDate.toDateString() === today.toDateString()) {
            startTimestampRef.current = timestamp;
            setIsTraining(true);
            return;
          } else {
            // Timestamp de outro dia - limpa
            await AsyncStorage.removeItem('training_start_timestamp');
          }
        }
      }

      // Novo treino - chama backend
      const response = await safeFetch(
        `${BACKEND_URL}/api/training-cycle/start-session/${userId}`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' } }
      );

      if (response.ok) {
        const data = await response.json();
        const startTime = Date.now();
        startTimestampRef.current = startTime;
        setSessionStartedAt(data.session.started_at);
        setIsTraining(true);
        setTrainingSeconds(0);
        
        // Salva timestamp localmente
        await AsyncStorage.setItem('training_start_timestamp', startTime.toString());
      } else {
        const errorData = await response.json().catch(() => ({}));
        Alert.alert('Erro', errorData.detail || 'Não foi possível iniciar o treino');
      }
    } catch (error) {
      console.error('Error starting workout:', error);
      Alert.alert('Erro', 'Falha na conexão');
    }
  };

  // Pause workout - agora apenas para a UI, o timer continua baseado no timestamp
  const pauseWorkout = async () => {
    // Como usamos timestamp, o timer continua "funcionando" mesmo pausado
    // Aqui apenas paramos a atualização visual
    setIsTraining(false);
  };

  // Finish workout
  const finishWorkout = async () => {
    if (!userId || !BACKEND_URL) {
      Alert.alert('Erro', 'Usuário não identificado');
      return;
    }

    // Calcula tempo real baseado no timestamp
    const currentTime = startTimestampRef.current 
      ? Math.floor((Date.now() - startTimestampRef.current) / 1000)
      : trainingSeconds;
    
    Alert.alert(
      'Finalizar Treino',
      `Deseja finalizar o treino?\nTempo: ${formatTime(currentTime)}`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Finalizar',
          onPress: async () => {
            try {
              // Para o timer imediatamente
              setIsTraining(false);
              if (timerRef.current) clearInterval(timerRef.current);
              
              // Primeiro tenta finalizar diretamente
              let response = await safeFetch(
                `${BACKEND_URL}/api/training-cycle/finish-session/${userId}`,
                {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    duration_seconds: currentTime,
                    exercises_completed: workoutPlan?.workout_days?.[0]?.exercises?.length || 0
                  })
                }
              );

              // Se falhou porque não tem sessão, cria uma e finaliza
              if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                
                if (errorData.detail?.includes('Nenhuma sessão') || errorData.detail?.includes('No active')) {
                  // Cria sessão
                  await safeFetch(
                    `${BACKEND_URL}/api/training-cycle/start-session/${userId}`,
                    { method: 'POST', headers: { 'Content-Type': 'application/json' } }
                  );
                  
                  // Tenta finalizar novamente
                  response = await safeFetch(
                    `${BACKEND_URL}/api/training-cycle/finish-session/${userId}`,
                    {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        duration_seconds: currentTime,
                        exercises_completed: workoutPlan?.workout_days?.[0]?.exercises?.length || 0
                      })
                    }
                  );
                }
              }

              if (response.ok) {
                const data = await response.json();
                
                // Limpa estados
                setTrainingSeconds(0);
                setHasTrainedToday(true);
                setWorkoutStatus('completed');
                startTimestampRef.current = null;
                
                // Limpa AsyncStorage
                await AsyncStorage.multiRemove([
                  'training_start_timestamp',
                  'training_in_progress',
                  'training_start_time',
                  'training_paused_seconds'
                ]);
                
                Alert.alert(
                  '🎉 Treino Concluído!',
                  `Parabéns! Você treinou por ${data.session?.duration_formatted || formatTime(currentTime)}.\n\nPróximo treino: ${data.next_workout || 'Amanhã'}`
                );
                
                // Recarrega status para atualizar qual é o próximo treino
                await loadCycleStatus(userId);
                await loadWorkoutPlan(userId);
              } else {
                const errorData = await response.json().catch(() => ({}));
                Alert.alert('Erro', errorData.detail || 'Não foi possível finalizar o treino');
              }
            } catch (error) {
              console.error('Error finishing workout:', error);
              Alert.alert('Erro', 'Falha na conexão. Tente novamente.');
            }
          }
        }
      ]
    );
  };

  // Simple finish workout (sem timer)
  const finishWorkoutSimple = async () => {
    if (!userId || !BACKEND_URL) {
      Alert.alert('Erro', 'Usuário não identificado');
      return;
    }

    Alert.alert(
      'Finalizar Treino',
      'Marcar o treino de hoje como concluído?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Confirmar',
          onPress: async () => {
            try {
              // Primeiro inicia a sessão (necessário para o backend)
              await safeFetch(
                `${BACKEND_URL}/api/training-cycle/start-session/${userId}`,
                { method: 'POST', headers: { 'Content-Type': 'application/json' } }
              );
              
              // Depois finaliza
              const response = await safeFetch(
                `${BACKEND_URL}/api/training-cycle/finish-session/${userId}`,
                {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    duration_seconds: 0, // Sem timer
                    exercises_completed: workoutPlan?.workout_days?.[0]?.exercises?.length || 0
                  })
                }
              );

              if (response.ok) {
                const data = await response.json();
                
                // Limpa estados
                setHasTrainedToday(true);
                setWorkoutStatus('completed');
                
                // Avança o índice do treino (A→B→C→D→A)
                const totalWorkouts = workoutPlan?.workout_days?.length || 4;
                const nextIndex = (currentWorkoutIndex + 1) % totalWorkouts;
                setCurrentWorkoutIndex(nextIndex);
                
                // Salva o próximo índice no AsyncStorage para persistir
                await AsyncStorage.setItem('next_workout_index', nextIndex.toString());
                
                const workoutLetters = ['A', 'B', 'C', 'D', 'E', 'F'];
                const nextWorkoutLetter = workoutLetters[nextIndex] || `${nextIndex + 1}`;
                
                Alert.alert(
                  '🎉 Treino Concluído!',
                  `Parabéns pelo treino de hoje!\n\nPróximo treino: Treino ${nextWorkoutLetter}`
                );
                
                // Recarrega status para atualizar qual é o próximo treino
                await loadCycleStatus(userId);
                await loadWorkoutPlan(userId);
              } else {
                const errorData = await response.json().catch(() => ({}));
                Alert.alert('Erro', errorData.detail || 'Não foi possível finalizar o treino');
              }
            } catch (error) {
              console.error('Error finishing workout:', error);
              Alert.alert('Erro', 'Falha na conexão. Tente novamente.');
            }
          }
        }
      ]
    );
  };

  // Format time helper
  const formatTime = (seconds: number) => {
    const secs = Math.max(0, Math.floor(Number(seconds) || 0));
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remainingSecs.toString().padStart(2, '0')}`;
  };

  // Generate workout
  const handleGenerateWorkout = async () => {
    if (!userId || !BACKEND_URL) {
      Alert.alert('Erro', 'Usuário não identificado');
      return;
    }

    setGenerating(true);
    try {
      const response = await safeFetch(
        `${BACKEND_URL}/api/workout/generate?user_id=${userId}`,
        { method: 'POST' }
      );

      if (response.ok) {
        const data = await response.json();
        setWorkoutPlan(data);
        Alert.alert('Sucesso!', 'Seu treino foi gerado com sucesso!');
      } else {
        const errorData = await response.json().catch(() => ({}));
        Alert.alert('Erro', errorData.detail || 'Não foi possível gerar o treino');
      }
    } catch (error) {
      console.error('Error generating workout:', error);
      Alert.alert('Erro', 'Falha na conexão. Tente novamente.');
    } finally {
      setGenerating(false);
    }
  };

  const handleExercisePress = (exercise: any, dayIndex: number, exIndex: number) => {
    setSelectedExercise(exercise);
    setShowExerciseModal(true);
  };

  // Rest timer functions - com suporte a pausar/continuar
  const startRestTimer = (seconds: number | string) => {
    const secs = Number(seconds) || 60;
    setRestTimerSeconds(secs);
    setRestTimerInitialSeconds(secs);
    setRestTimerActive(true);
    setRestTimerPaused(false);
    
    if (restTimerRef.current) clearInterval(restTimerRef.current);
    
    restTimerRef.current = setInterval(() => {
      setRestTimerSeconds((prev) => {
        if (prev <= 1) {
          setRestTimerActive(false);
          setRestTimerPaused(false);
          if (restTimerRef.current) clearInterval(restTimerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const pauseRestTimer = () => {
    setRestTimerPaused(true);
    if (restTimerRef.current) {
      clearInterval(restTimerRef.current);
      restTimerRef.current = null;
    }
  };

  const resumeRestTimer = () => {
    setRestTimerPaused(false);
    restTimerRef.current = setInterval(() => {
      setRestTimerSeconds((prev) => {
        if (prev <= 1) {
          setRestTimerActive(false);
          setRestTimerPaused(false);
          if (restTimerRef.current) clearInterval(restTimerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopRestTimer = () => {
    setRestTimerActive(false);
    setRestTimerPaused(false);
    setRestTimerSeconds(0);
    if (restTimerRef.current) clearInterval(restTimerRef.current);
  };

  const resetRestTimer = () => {
    if (restTimerRef.current) clearInterval(restTimerRef.current);
    setRestTimerSeconds(restTimerInitialSeconds);
    setRestTimerPaused(false);
    restTimerRef.current = setInterval(() => {
      setRestTimerSeconds((prev) => {
        if (prev <= 1) {
          setRestTimerActive(false);
          if (restTimerRef.current) clearInterval(restTimerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Load workout history
  const loadHistory = async () => {
    if (!userId) return;
    try {
      setLoadingHistory(true);
      const response = await safeFetch(`${BACKEND_URL}/api/workout/history/${userId}?days=30`);
      if (response.ok) {
        const data = await response.json();
        setWorkoutHistory(data.history || []);
        setHistoryStats(data.stats || null);
      }
    } catch (error) {
      console.error('Error loading workout history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const openHistory = () => {
    setShowHistoryModal(true);
    loadHistory();
  };

  // Format date for history
  const formatHistoryDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const mins = date.getMinutes().toString().padStart(2, '0');
    return { date: `${day}/${month}`, time: `${hours}:${mins}` };
  };

  // Get today's workout day index
  const getTodayWorkoutIndex = () => {
    // Usa o índice atual do estado (gerenciado localmente após finalizar)
    return currentWorkoutIndex;
  };

  // ==================== RENDER ====================

  if (initialLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <WorkoutSkeleton />
      </SafeAreaView>
    );
  }

  const todayWorkoutIndex = getTodayWorkoutIndex();

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

      <SafeAreaView style={styles.safeArea}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={premiumColors.primary} />
          }
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <View>
              <Text style={[styles.headerTitle, { color: theme.text }]}>{t.workout.title}</Text>
              <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
                {workoutPlan?.weekly_split || t.workout.customWorkout}
              </Text>
            </View>
            <TouchableOpacity 
              style={[styles.historyButton, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.5)' : 'rgba(226, 232, 240, 0.8)' }]}
              onPress={openHistory}
            >
              <History size={20} color={premiumColors.primary} />
            </TouchableOpacity>
          </Animated.View>

          {/* Bloqueio de Treino - Dia de Descanso */}
          {isTrainingBlocked && (
            <Animated.View entering={FadeInDown.delay(100).springify()}>
              <GlassCard isDark={isDark} style={styles.restDayCard}>
                <LinearGradient
                  colors={isDark 
                    ? ['rgba(107, 114, 128, 0.15)', 'rgba(71, 85, 105, 0.1)']
                    : ['rgba(107, 114, 128, 0.1)', 'rgba(156, 163, 175, 0.05)']}
                  style={StyleSheet.absoluteFill}
                />
                <View style={styles.restDayContent}>
                  <View style={[styles.restDayIconBg, { backgroundColor: '#6B728020' }]}>
                    <Moon size={32} color="#6B7280" />
                  </View>
                  <Text style={[styles.restDayTitle, { color: theme.text }]}>
                    Hoje é dia de DESCANSO 💤
                  </Text>
                  <Text style={[styles.restDaySubtitle, { color: theme.textSecondary }]}>
                    Treino bloqueado para recuperação muscular
                  </Text>
                  <View style={[styles.restDayDietBadge, { backgroundColor: isDark ? 'rgba(107, 114, 128, 0.2)' : 'rgba(107, 114, 128, 0.1)' }]}>
                    <Text style={[styles.restDayDietText, { color: '#6B7280' }]}>
                      🍽️ Dieta de descanso: -5% cal, -20% carbs
                    </Text>
                  </View>
                  <Text style={[styles.restDayMessage, { color: theme.textTertiary }]}>
                    Aproveite para descansar e se recuperar.{'\n'}
                    Seu próximo treino está programado!
                  </Text>
                </View>
              </GlassCard>
            </Animated.View>
          )}

          {/* Finish Workout Card - Only show on training days */}
          {!isTrainingBlocked && dayType === 'train' && !hasTrainedToday && (
            <FinishWorkoutCard
              onFinish={finishWorkoutSimple}
              isDark={isDark}
              theme={theme}
              tomorrowIsRest={tomorrowIsRest}
              trainingPhrase={trainingPhrase}
              tomorrowPhrase={tomorrowPhrase}
            />
          )}

          {/* Already Trained Today Banner */}
          {hasTrainedToday && (
            <Animated.View entering={FadeInDown.delay(200).springify()}>
              <GlassCard isDark={isDark} style={styles.trainedBanner}>
                <LinearGradient
                  colors={['rgba(16, 185, 129, 0.15)', 'rgba(5, 150, 105, 0.1)']}
                  style={StyleSheet.absoluteFill}
                />
                <CheckCircle size={24} color="#10B981" />
                <View style={styles.trainedBannerContent}>
                  <Text style={[styles.trainedBannerTitle, { color: '#10B981' }]}>
                    ✅ Treino Concluído!
                  </Text>
                  <Text style={[styles.trainedBannerText, { color: theme.textSecondary }]}>
                    Parabéns! Dieta de treino ativa.
                  </Text>
                </View>
              </GlassCard>
            </Animated.View>
          )}

          {/* Rest Timer (for exercises) - com pausar/continuar */}
          {restTimerActive && (
            <Animated.View entering={FadeInUp.springify()}>
              <GlassCard isDark={isDark} style={styles.restTimerCard}>
                <Text style={[styles.restTimerLabel, { color: theme.textSecondary }]}>
                  {restTimerPaused ? 'Descanso (Pausado)' : 'Descanso'}
                </Text>
                <Text style={[styles.restTimerDisplay, { color: restTimerPaused ? '#F59E0B' : theme.text }]}>
                  {formatTime(restTimerSeconds)}
                </Text>
                <View style={styles.restTimerButtons}>
                  {/* Botão Pausar/Continuar */}
                  {restTimerPaused ? (
                    <TouchableOpacity
                      style={[styles.restTimerBtn, { backgroundColor: '#10B98120' }]}
                      onPress={resumeRestTimer}
                    >
                      <Play size={20} color="#10B981" />
                      <Text style={[styles.restTimerBtnText, { color: '#10B981' }]}>Continuar</Text>
                    </TouchableOpacity>
                  ) : (
                    <TouchableOpacity
                      style={[styles.restTimerBtn, { backgroundColor: '#F59E0B20' }]}
                      onPress={pauseRestTimer}
                    >
                      <Pause size={20} color="#F59E0B" />
                      <Text style={[styles.restTimerBtnText, { color: '#F59E0B' }]}>Pausar</Text>
                    </TouchableOpacity>
                  )}
                  
                  {/* Botão Resetar */}
                  <TouchableOpacity
                    style={[styles.restTimerBtn, { backgroundColor: '#3B82F620' }]}
                    onPress={resetRestTimer}
                  >
                    <RotateCcw size={20} color="#3B82F6" />
                    <Text style={[styles.restTimerBtnText, { color: '#3B82F6' }]}>Resetar</Text>
                  </TouchableOpacity>
                  
                  {/* Botão Parar */}
                  <TouchableOpacity
                    style={[styles.restTimerBtn, { backgroundColor: '#EF444420' }]}
                    onPress={stopRestTimer}
                  >
                    <StopCircle size={20} color="#EF4444" />
                    <Text style={[styles.restTimerBtnText, { color: '#EF4444' }]}>Parar</Text>
                  </TouchableOpacity>
                </View>
              </GlassCard>
            </Animated.View>
          )}

          {/* Workout Days */}
          {(workoutPlan?.days || workoutPlan?.workout_days)?.length > 0 ? (
            <>
              {(workoutPlan.days || workoutPlan.workout_days).map((day: any, index: number) => (
                <WorkoutDayCard
                  key={index}
                  day={day}
                  index={index}
                  isDark={isDark}
                  theme={theme}
                  onExercisePress={handleExercisePress}
                  language={language}
                  t={t}
                  isToday={index === currentWorkoutIndex}
                  hasTrainedToday={hasTrainedToday}
                />
              ))}
            </>
          ) : (
            /* Empty State */
            <Animated.View entering={FadeInDown.delay(200).springify()}>
              <GlassCard isDark={isDark} style={styles.emptyStateCard}>
                <View style={styles.emptyStateContent}>
                  <View style={[styles.emptyIconBg, { backgroundColor: premiumColors.primary + '15' }]}>
                    <Dumbbell size={40} color={premiumColors.primary} strokeWidth={1.5} />
                  </View>
                  <Text style={[styles.emptyTitle, { color: theme.text }]}>
                    {t.workout.noData}
                  </Text>
                  <Text style={[styles.emptyDescription, { color: theme.textSecondary }]}>
                    {t.workout.generating.replace('...', '')}
                  </Text>
                  <TouchableOpacity
                    style={[styles.generateButton, { opacity: generating ? 0.7 : 1 }]}
                    onPress={handleGenerateWorkout}
                    disabled={generating}
                  >
                    <LinearGradient
                      colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                      style={styles.generateButtonGradient}
                    >
                      {generating ? (
                        <ActivityIndicator size="small" color="#FFF" />
                      ) : (
                        <>
                          <Target size={20} color="#FFF" strokeWidth={2} />
                          <Text style={styles.generateButtonText}>{t.workout.generateWorkout}</Text>
                        </>
                      )}
                    </LinearGradient>
                  </TouchableOpacity>
                </View>
              </GlassCard>
            </Animated.View>
          )}

          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>

      {/* Exercise Detail Modal */}
      <Modal visible={showExerciseModal} transparent animationType="slide">
        <View style={[styles.modalOverlay, { backgroundColor: theme.overlay }]}>
          <View style={[styles.modalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: theme.text }]}>
                {selectedExercise ? translateExercise(selectedExercise.name, language) : ''}
              </Text>
              <TouchableOpacity onPress={() => setShowExerciseModal(false)}>
                <X size={24} color={theme.text} />
              </TouchableOpacity>
            </View>

            {selectedExercise && (
              <View style={styles.exerciseModalContent}>
                {selectedExercise.focus && (
                  <View style={[styles.focusBadge, { backgroundColor: premiumColors.primary + '15' }]}>
                    <Target size={16} color={premiumColors.primary} />
                    <Text style={[styles.focusBadgeText, { color: premiumColors.primary }]}>
                      {translateExerciseFocus(selectedExercise.focus, language)}
                    </Text>
                  </View>
                )}

                <View style={styles.exerciseModalStats}>
                  <View style={[styles.exerciseModalStat, { backgroundColor: premiumColors.primary + '15' }]}>
                    <Repeat size={20} color={premiumColors.primary} />
                    <Text style={[styles.exerciseModalStatValue, { color: theme.text }]}>
                      {selectedExercise.sets || 3}
                    </Text>
                    <Text style={[styles.exerciseModalStatLabel, { color: theme.textTertiary }]}>{t.workout.sets}</Text>
                  </View>
                  <View style={[styles.exerciseModalStat, { backgroundColor: '#F59E0B15' }]}>
                    <Target size={20} color="#F59E0B" />
                    <Text style={[styles.exerciseModalStatValue, { color: theme.text }]}>
                      {selectedExercise.reps || '8-12'}
                    </Text>
                    <Text style={[styles.exerciseModalStatLabel, { color: theme.textTertiary }]}>{t.workout.reps}</Text>
                  </View>
                  <View style={[styles.exerciseModalStat, { backgroundColor: '#3B82F615' }]}>
                    <Timer size={20} color="#3B82F6" />
                    <Text style={[styles.exerciseModalStatValue, { color: theme.text }]}>
                      {selectedExercise.rest || 60}s
                    </Text>
                    <Text style={[styles.exerciseModalStatLabel, { color: theme.textTertiary }]}>{t.workout.rest}</Text>
                  </View>
                </View>

                {selectedExercise.notes && (
                  <View style={[styles.exerciseNotes, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.5)' }]}>
                    <Text style={[styles.exerciseNotesText, { color: theme.textSecondary }]}>
                      {translateWorkoutNotes(selectedExercise.notes, language)}
                    </Text>
                  </View>
                )}

                <TouchableOpacity
                  style={styles.startTimerBtn}
                  onPress={() => {
                    setShowExerciseModal(false);
                    // Usa rest_seconds (número) ao invés de rest (string "75s")
                    startRestTimer(selectedExercise.rest_seconds || 60);
                  }}
                >
                  <LinearGradient
                    colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.startTimerBtnGradient}
                  >
                    <Timer size={20} color="#FFF" />
                    <Text style={styles.startTimerBtnText}>{t.workout.start} Timer</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>

      {/* History Modal */}
      <Modal
        visible={showHistoryModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowHistoryModal(false)}
      >
        <View style={styles.historyModalOverlay}>
          <View style={[styles.historyModalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            {/* Header */}
            <View style={styles.historyModalHeader}>
              <View style={styles.historyModalTitleRow}>
                <History size={24} color={premiumColors.primary} />
                <Text style={[styles.historyModalTitle, { color: theme.text }]}>
                  {t.workout.workoutHistory}
                </Text>
              </View>
              <TouchableOpacity onPress={() => setShowHistoryModal(false)}>
                <X size={24} color={theme.textTertiary} />
              </TouchableOpacity>
            </View>

            {/* Stats Cards */}
            {historyStats && (
              <View style={styles.historyStatsRow}>
                <View style={[styles.historyStatCard, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.5)' }]}>
                  <Dumbbell size={20} color={premiumColors.primary} />
                  <Text style={[styles.historyStatValue, { color: theme.text }]}>
                    {historyStats.this_week_count}
                  </Text>
                  <Text style={[styles.historyStatLabel, { color: theme.textTertiary }]}>
                    {t.workout.thisWeek}
                  </Text>
                </View>
                <View style={[styles.historyStatCard, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.5)' }]}>
                  <Award size={20} color="#F59E0B" />
                  <Text style={[styles.historyStatValue, { color: theme.text }]}>
                    {historyStats.total_workouts}
                  </Text>
                  <Text style={[styles.historyStatLabel, { color: theme.textTertiary }]}>
                    {t.workout.allTime}
                  </Text>
                </View>
                <View style={[styles.historyStatCard, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.5)' }]}>
                  <Target size={20} color="#10B981" />
                  <Text style={[styles.historyStatValue, { color: theme.text }]}>
                    {historyStats.this_week_count}/{historyStats.target_frequency}
                  </Text>
                  <Text style={[styles.historyStatLabel, { color: theme.textTertiary }]}>
                    {t.workout.frequency}
                  </Text>
                </View>
              </View>
            )}

            {/* History List */}
            <ScrollView style={styles.historyList} showsVerticalScrollIndicator={false}>
              {loadingHistory ? (
                <ActivityIndicator size="large" color={premiumColors.primary} style={{ marginTop: 40 }} />
              ) : workoutHistory.length === 0 ? (
                <View style={styles.historyEmpty}>
                  <Dumbbell size={48} color={theme.textTertiary} />
                  <Text style={[styles.historyEmptyTitle, { color: theme.text }]}>
                    {t.workout.noWorkoutsYet}
                  </Text>
                  <Text style={[styles.historyEmptySubtitle, { color: theme.textTertiary }]}>
                    {t.workout.startTrainingToSee}
                  </Text>
                </View>
              ) : (
                workoutHistory.map((item, index) => {
                  const { date, time } = formatHistoryDate(item.completed_at);
                  return (
                    <Animated.View 
                      key={item.id || index}
                      entering={FadeInDown.delay(index * 50)}
                    >
                      <View style={[styles.historyItem, { borderBottomColor: theme.border }]}>
                        <View style={[styles.historyDateBadge, { backgroundColor: premiumColors.primary + '15' }]}>
                          <Text style={[styles.historyDate, { color: premiumColors.primary }]}>{date}</Text>
                          <Text style={[styles.historyTime, { color: premiumColors.primary }]}>{time}</Text>
                        </View>
                        <View style={styles.historyItemContent}>
                          <Text style={[styles.historyItemTitle, { color: theme.text }]} numberOfLines={1}>
                            {translateWorkoutDayName(item.workout_day_name, language)}
                          </Text>
                          <View style={styles.historyItemStats}>
                            <View style={styles.historyItemStat}>
                              <CheckCircle size={12} color="#10B981" />
                              <Text style={[styles.historyItemStatText, { color: theme.textSecondary }]}>
                                {item.exercises_completed}/{item.total_exercises} {t.workout.exercises}
                              </Text>
                            </View>
                            {item.duration_minutes && (
                              <View style={styles.historyItemStat}>
                                <Clock size={12} color={theme.textTertiary} />
                                <Text style={[styles.historyItemStatText, { color: theme.textSecondary }]}>
                                  {item.duration_minutes} {t.workout.minutes}
                                </Text>
                              </View>
                            )}
                          </View>
                        </View>
                        <CheckCircle size={20} color="#10B981" />
                      </View>
                    </Animated.View>
                  );
                })
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

// ==================== STYLES ====================

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg, gap: spacing.lg },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  headerTitle: { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  headerSubtitle: { fontSize: 14, marginTop: 4 },

  dayTypeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: radius.full,
  },
  dayTypeBadgeText: { fontSize: 12, fontWeight: '700' },

  statusCard: { padding: spacing.base },
  statusRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around' },
  statusItem: { alignItems: 'center', gap: 4 },
  statusLabel: { fontSize: 11, fontWeight: '500' },
  statusValue: { fontSize: 18, fontWeight: '800' },
  statusDivider: { width: 1, height: 40 },

  timerCard: { padding: spacing.xl, alignItems: 'center' },
  timerHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: spacing.md },
  timerLabel: { fontSize: 14, fontWeight: '600' },
  timerDisplay: { fontSize: 64, fontWeight: '800', letterSpacing: -2, fontVariant: ['tabular-nums'] },
  timerButtons: { marginTop: spacing.lg, width: '100%' },
  
  startWorkoutBtn: { borderRadius: radius.lg, overflow: 'hidden' },
  startWorkoutBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 16,
    paddingHorizontal: 24,
  },
  startWorkoutBtnText: { color: '#FFF', fontSize: 18, fontWeight: '700' },
  
  activeTimerButtons: { flexDirection: 'row', gap: spacing.md },
  pauseBtn: { flex: 1, height: 56, borderRadius: radius.lg, alignItems: 'center', justifyContent: 'center' },
  finishBtn: { flex: 2, height: 56, borderRadius: radius.lg, overflow: 'hidden' },
  finishBtnGradient: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 },
  finishBtnText: { color: '#FFF', fontSize: 16, fontWeight: '700' },

  trainedBanner: { flexDirection: 'row', alignItems: 'center', padding: spacing.base, gap: spacing.md },
  trainedBannerContent: { flex: 1 },
  trainedBannerTitle: { fontSize: 16, fontWeight: '700' },
  trainedBannerText: { fontSize: 13, marginTop: 2 },

  // Finish Workout Card Styles
  finishWorkoutCard: { padding: spacing.xl, overflow: 'hidden' },
  finishWorkoutContent: { alignItems: 'center' },
  finishIconBg: { width: 64, height: 64, borderRadius: 32, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md },
  finishWorkoutTitle: { fontSize: 18, fontWeight: '700', textAlign: 'center', marginBottom: spacing.lg },
  finishTodayBtn: { borderRadius: radius.lg, overflow: 'hidden', width: '100%', marginBottom: spacing.md },
  finishTodayBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 16,
    paddingHorizontal: 24,
  },
  finishTodayBtnText: { color: '#FFF', fontSize: 17, fontWeight: '700' },
  motivationPhrase: { fontSize: 14, textAlign: 'center', fontStyle: 'italic', paddingHorizontal: spacing.md },

  // Rest Day Card Styles
  restDayCard: { padding: spacing.xl, overflow: 'hidden' },
  restDayContent: { alignItems: 'center' },
  restDayIconBg: { width: 72, height: 72, borderRadius: 36, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md },
  restDayTitle: { fontSize: 22, fontWeight: '800', textAlign: 'center', marginBottom: spacing.xs },
  restDaySubtitle: { fontSize: 14, fontWeight: '500', textAlign: 'center', marginBottom: spacing.md },
  restDayDietBadge: { paddingHorizontal: spacing.lg, paddingVertical: spacing.sm, borderRadius: radius.lg, marginBottom: spacing.md },
  restDayDietText: { fontSize: 13, fontWeight: '600' },
  restDayMessage: { fontSize: 14, textAlign: 'center', lineHeight: 22 },

  restTimerCard: { padding: spacing.lg, alignItems: 'center' },
  restTimerLabel: { fontSize: 12, fontWeight: '600', marginBottom: 4 },
  restTimerDisplay: { fontSize: 48, fontWeight: '800', fontVariant: ['tabular-nums'] },
  restTimerButtons: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.md, justifyContent: 'center' },
  restTimerBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 16, paddingVertical: 10, borderRadius: radius.lg },
  restTimerBtnText: { fontSize: 14, fontWeight: '600' },

  dayCard: { marginBottom: spacing.md },
  todayCard: { borderColor: premiumColors.primary + '50', borderWidth: 2 },
  dayHeader: { flexDirection: 'row', alignItems: 'center', padding: spacing.base, gap: spacing.md },
  dayIconBg: { width: 44, height: 44, borderRadius: radius.lg, alignItems: 'center', justifyContent: 'center' },
  dayHeaderContent: { flex: 1 },
  dayTitleRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  dayName: { fontSize: 16, fontWeight: '700', letterSpacing: -0.3 },
  todayBadge: { paddingHorizontal: spacing.sm, paddingVertical: 2, borderRadius: radius.sm },
  todayBadgeText: { color: '#FFF', fontSize: 10, fontWeight: '800' },
  dayExerciseCount: { fontSize: 13, marginTop: 2 },

  exercisesList: { paddingHorizontal: spacing.base },
  exerciseItem: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: spacing.md, borderBottomWidth: 1 },
  exerciseInfo: { flex: 1 },
  exerciseName: { fontSize: 15, fontWeight: '600' },
  exerciseFocus: { fontSize: 12, fontWeight: '500', marginTop: 2 },
  exerciseDetails: { flexDirection: 'row', gap: spacing.md, marginTop: 4 },
  exerciseDetail: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  exerciseDetailText: { fontSize: 12 },

  emptyStateCard: { marginTop: spacing.lg },
  emptyStateContent: { alignItems: 'center', padding: spacing.xl },
  emptyIconBg: { width: 80, height: 80, borderRadius: 40, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.lg },
  emptyTitle: { fontSize: 20, fontWeight: '700', marginBottom: spacing.sm },
  emptyDescription: { fontSize: 14, textAlign: 'center', marginBottom: spacing.xl },
  generateButton: { borderRadius: radius.lg, overflow: 'hidden' },
  generateButtonGradient: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, paddingVertical: 14, paddingHorizontal: 24 },
  generateButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },

  modalOverlay: { flex: 1, justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: radius['2xl'], borderTopRightRadius: radius['2xl'], padding: spacing.lg },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg },
  modalTitle: { fontSize: 20, fontWeight: '700', flex: 1 },

  exerciseModalContent: { gap: spacing.lg },
  focusBadge: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', gap: spacing.xs, paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.lg },
  focusBadgeText: { fontSize: 13, fontWeight: '600' },

  exerciseModalStats: { flexDirection: 'row', gap: spacing.md },
  exerciseModalStat: { flex: 1, alignItems: 'center', padding: spacing.base, borderRadius: radius.lg, gap: 4 },
  exerciseModalStatValue: { fontSize: 24, fontWeight: '800' },
  exerciseModalStatLabel: { fontSize: 11, fontWeight: '600' },

  exerciseNotes: { padding: spacing.base, borderRadius: radius.lg },
  exerciseNotesText: { fontSize: 14, lineHeight: 20 },

  startTimerBtn: { borderRadius: radius.lg, overflow: 'hidden', marginTop: spacing.sm },
  startTimerBtnGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, paddingVertical: 14 },
  startTimerBtnText: { color: '#FFF', fontSize: 16, fontWeight: '700' },

  // History Button
  historyButton: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },

  // History Modal
  historyModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  historyModalContent: {
    borderTopLeftRadius: radius['2xl'],
    borderTopRightRadius: radius['2xl'],
    padding: spacing.lg,
    maxHeight: '85%',
  },
  historyModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  historyModalTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  historyModalTitle: {
    fontSize: 20,
    fontWeight: '700',
  },
  historyStatsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  historyStatCard: {
    flex: 1,
    alignItems: 'center',
    padding: spacing.base,
    borderRadius: radius.lg,
    gap: 6,
  },
  historyStatValue: {
    fontSize: 24,
    fontWeight: '800',
  },
  historyStatLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
  historyList: {
    flex: 1,
  },
  historyEmpty: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
    gap: spacing.md,
  },
  historyEmptyTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginTop: spacing.sm,
  },
  historyEmptySubtitle: {
    fontSize: 14,
    textAlign: 'center',
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.base,
    borderBottomWidth: 1,
    gap: spacing.md,
  },
  historyDateBadge: {
    width: 50,
    height: 50,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  historyDate: {
    fontSize: 14,
    fontWeight: '700',
  },
  historyTime: {
    fontSize: 10,
    fontWeight: '500',
  },
  historyItemContent: {
    flex: 1,
    gap: 4,
  },
  historyItemTitle: {
    fontSize: 15,
    fontWeight: '600',
  },
  historyItemStats: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  historyItemStat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  historyItemStatText: {
    fontSize: 12,
  },
});
