import React, { useEffect, useState, useCallback, useRef } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, RefreshControl, Modal, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';
import { Toast, WorkoutSkeleton } from '../../components';
import { useToast } from '../../hooks/useToast';
import { useHaptics } from '../../hooks/useHaptics';
import { useTranslation, translateExercise, translateWorkoutName, translateExerciseNotes } from '../../i18n';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

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

export default function WorkoutScreen() {
  const { colors } = useTheme();
  const { t, language } = useTranslation();
  const styles = createStyles(colors);
  const { toast, showSuccess, showError, hideToast } = useToast();
  const { lightImpact, mediumImpact, successFeedback, errorFeedback, selectionFeedback } = useHaptics();
  
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [workoutPlan, setWorkoutPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  
  // Exercise detail modal
  const [selectedExercise, setSelectedExercise] = useState<any>(null);
  const [selectedDayIndex, setSelectedDayIndex] = useState(-1);
  const [selectedExerciseIndex, setSelectedExerciseIndex] = useState(-1);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  
  // History modal
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [workoutHistory, setWorkoutHistory] = useState<any[]>([]);
  const [historyStats, setHistoryStats] = useState<any>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // Timer state
  const [timerActive, setTimerActive] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadUserData();
      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
      };
    }, [])
  );

  useEffect(() => {
    if (timerActive && timerSeconds > 0) {
      timerRef.current = setInterval(() => {
        setTimerSeconds((prev) => {
          if (prev <= 1) {
            setTimerActive(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timerActive]);

  const loadUserData = async () => {
    try {
      setInitialLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
      
      if (id && BACKEND_URL) {
        try {
          const profileResponse = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
          if (profileResponse.ok) {
            const data = await profileResponse.json();
            setUserProfile(data);
          }
        } catch (err) {
          console.log('Profile load error');
        }
        await loadWorkout(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const loadWorkout = async (uid: string) => {
    if (!uid || !BACKEND_URL) return;
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/${uid}`);
      if (response.ok) {
        const data = await response.json();
        setWorkoutPlan(data);
      }
    } catch (error: any) {
      console.log('Workout not loaded');
    }
  };

  const generateWorkout = async () => {
    if (!userId || !BACKEND_URL) return;
    
    if (workoutPlan) {
      Alert.alert(
        'Regenerar Treino',
        'Isso irá substituir seu treino atual e corrigir as instruções. Deseja continuar?',
        [
          { text: 'Cancelar', style: 'cancel' },
          { text: 'Regenerar', style: 'destructive', onPress: doGenerateWorkout }
        ]
      );
      return;
    }
    
    doGenerateWorkout();
  };

  const doGenerateWorkout = async () => {
    setLoading(true);
    mediumImpact(); // Haptic ao iniciar
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/generate?user_id=${userId}`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setWorkoutPlan(data);
        successFeedback(); // Haptic de sucesso
        showSuccess('Treino gerado com sucesso!');
      } else {
        errorFeedback(); // Haptic de erro
        showError('Erro ao gerar treino. Tente novamente.');
      }
    } catch (error) {
      errorFeedback();
      showError('Erro de conexão.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  const openExerciseDetail = (exercise: any, dayIndex: number, exerciseIndex: number) => {
    setSelectedExercise(exercise);
    setSelectedDayIndex(dayIndex);
    setSelectedExerciseIndex(exerciseIndex);
    setShowExerciseModal(true);
    setTimerSeconds(exercise.rest_seconds || 60);
    setTimerActive(false);
  };

  const toggleExerciseComplete = async (dayIndex: number, exerciseIndex: number, completed: boolean) => {
    if (!workoutPlan) return;
    
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/${workoutPlan.id}/exercise/complete`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workout_day_index: dayIndex,
          exercise_index: exerciseIndex,
          completed: completed
        })
      });
      
      if (response.ok) {
        const updatedWorkout = await response.json();
        setWorkoutPlan(updatedWorkout);
        
        if (selectedExercise && selectedDayIndex === dayIndex && selectedExerciseIndex === exerciseIndex) {
          setSelectedExercise({ ...selectedExercise, completed: completed });
        }
        
        // Verifica se o dia foi completado para salvar no histórico
        const day = updatedWorkout.workout_days[dayIndex];
        const allCompleted = day.exercises?.every((ex: any) => ex.completed);
        
        if (allCompleted && completed) {
          // Salva no histórico automaticamente
          saveToHistory(day);
          successFeedback();
          showSuccess(`${day.name} concluído! 🎉`);
        }
      }
    } catch (error) {
      console.error('Erro ao atualizar exercício:', error);
    }
  };

  // Salvar treino no histórico
  const saveToHistory = async (day: any) => {
    if (!userId || !BACKEND_URL) return;
    
    try {
      await safeFetch(`${BACKEND_URL}/api/workout/history/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workout_day_name: `${day.name} - ${day.day}`,
          exercises_completed: day.exercises?.length || 0,
          total_exercises: day.exercises?.length || 0,
          duration_minutes: day.duration || null
        })
      });
    } catch (error) {
      console.log('Could not save to history');
    }
  };

  // Carregar histórico de treinos
  const loadWorkoutHistory = async () => {
    if (!userId || !BACKEND_URL) return;
    
    setLoadingHistory(true);
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/history/${userId}?days=90`);
      if (response.ok) {
        const data = await response.json();
        setWorkoutHistory(data.history || []);
        setHistoryStats(data.stats || null);
      }
    } catch (error) {
      console.log('Could not load workout history');
    } finally {
      setLoadingHistory(false);
    }
  };

  const openHistoryModal = () => {
    selectionFeedback();
    loadWorkoutHistory();
    setShowHistoryModal(true);
  };

  const formatHistoryDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Hoje';
    if (diffDays === 1) return 'Ontem';
    if (diffDays < 7) return `${diffDays} dias atrás`;
    
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  };

  const startRestTimer = () => setTimerActive(true);
  
  const resetTimer = () => {
    setTimerActive(false);
    setTimerSeconds(selectedExercise?.rest_seconds || 60);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const totalExercises = workoutPlan?.workout_days?.reduce((sum: number, day: any) => sum + (day.exercises?.length || 0), 0) || 0;
  const completedExercises = workoutPlan?.workout_days?.reduce((sum: number, day: any) => 
    sum + (day.exercises?.filter((ex: any) => ex.completed)?.length || 0), 0) || 0;
  const progressPercent = totalExercises > 0 ? Math.round((completedExercises / totalExercises) * 100) : 0;

  // Show skeleton while loading initially
  if (initialLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <WorkoutSkeleton />
      </SafeAreaView>
    );
  }

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.text }]}>{t.workout.generating}</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!workoutPlan) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
        >
          <Ionicons name="barbell-outline" size={80} color={colors.textTertiary} />
          <Text style={[styles.emptyTitle, { color: colors.text }]}>{t.workout.noData}</Text>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
            {t.workout.generating.replace('...', '')}
          </Text>
          <TouchableOpacity
            style={[styles.generateButton, { backgroundColor: colors.primary }]}
            onPress={generateWorkout}
            activeOpacity={0.8}
          >
            <Ionicons name="sparkles" size={20} color="#fff" />
            <Text style={styles.generateButtonText}>{t.workout.generateWorkout}</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={{ flex: 1 }}>
            <Text style={[styles.headerTitle, { color: colors.text }]}>{t.workout.title}</Text>
            <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
              {workoutPlan.notes || `${workoutPlan.weekly_frequency}x ${t.home.weeklyFrequency.replace('x/', '')}`}
            </Text>
          </View>
          <TouchableOpacity
            style={[styles.historyButton, { backgroundColor: colors.success + '15' }]}
            onPress={openHistoryModal}
            activeOpacity={0.7}
          >
            <Ionicons name="time-outline" size={20} color={colors.success} />
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.regenerateButton, { backgroundColor: colors.primary + '15' }]}
            onPress={generateWorkout}
            activeOpacity={0.7}
          >
            <Ionicons name="refresh-outline" size={20} color={colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Progress Card */}
        <View style={[styles.progressCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.progressHeader}>
            <Ionicons name="trophy-outline" size={24} color={colors.primary} />
            <Text style={[styles.progressTitle, { color: colors.text }]}>Progresso da Semana</Text>
          </View>
          <View style={styles.progressContent}>
            <Text style={[styles.progressPercent, { color: colors.primary }]}>{progressPercent}%</Text>
            <View style={styles.progressBarContainer}>
              <View style={[styles.progressBarBg, { backgroundColor: colors.border }]}>
                <View style={[styles.progressBarFill, { width: `${progressPercent}%`, backgroundColor: colors.primary }]} />
              </View>
              <Text style={[styles.progressText, { color: colors.textSecondary }]}>
                {completedExercises}/{totalExercises} {t.workout.exercises}
              </Text>
            </View>
          </View>
        </View>

        {/* Workout Days */}
        {workoutPlan.workout_days.map((day: any, dayIndex: number) => (
          <WorkoutDayCard 
            key={day.id || dayIndex} 
            day={day}
            dayIndex={dayIndex}
            colors={colors}
            onExercisePress={openExerciseDetail}
            onToggleComplete={toggleExerciseComplete}
            language={language}
          />
        ))}
      </ScrollView>

      {/* Exercise Detail Modal - TEXT ONLY */}
      <Modal
        visible={showExerciseModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowExerciseModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.background }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]} numberOfLines={2}>
                {selectedExercise?.name}
              </Text>
              <TouchableOpacity onPress={() => setShowExerciseModal(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Exercise Info */}
              <View style={[styles.exerciseInfo, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                <View style={styles.exerciseInfoRow}>
                  <View style={styles.exerciseInfoItem}>
                    <Ionicons name="repeat-outline" size={24} color={colors.primary} />
                    <Text style={[styles.exerciseInfoLabel, { color: colors.textSecondary }]}>{t.workout.sets}</Text>
                    <Text style={[styles.exerciseInfoValue, { color: colors.text }]}>{selectedExercise?.sets}</Text>
                  </View>
                  <View style={styles.exerciseInfoItem}>
                    <Ionicons name="fitness-outline" size={24} color={colors.primary} />
                    <Text style={[styles.exerciseInfoLabel, { color: colors.textSecondary }]}>{t.workout.reps}</Text>
                    <Text style={[styles.exerciseInfoValue, { color: colors.text }]}>{selectedExercise?.reps}</Text>
                  </View>
                  <View style={styles.exerciseInfoItem}>
                    <Ionicons name="time-outline" size={24} color={colors.primary} />
                    <Text style={[styles.exerciseInfoLabel, { color: colors.textSecondary }]}>{t.workout.rest}</Text>
                    <Text style={[styles.exerciseInfoValue, { color: colors.text }]}>{selectedExercise?.rest}</Text>
                  </View>
                </View>
              </View>

              {/* Execution Notes - TEXT GUIDANCE */}
              {selectedExercise?.notes && (
                <View style={[styles.notesCard, { backgroundColor: colors.primary + '15', borderColor: colors.primary + '30' }]}>
                  <View style={styles.notesHeader}>
                    <Ionicons name="bulb-outline" size={20} color={colors.primary} />
                    <Text style={[styles.notesTitle, { color: colors.primary }]}>{t.workout.howToExecute}</Text>
                  </View>
                  <Text style={[styles.notesText, { color: colors.text }]}>{selectedExercise.notes}</Text>
                </View>
              )}

              {/* Rest Timer */}
              <View style={[styles.timerCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                <Text style={[styles.timerTitle, { color: colors.textSecondary }]}>{t.workout.restTimer}</Text>
                <Text style={[
                  styles.timerDisplay, 
                  { color: timerActive && timerSeconds <= 10 ? colors.error : colors.text }
                ]}>
                  {formatTime(timerSeconds)}
                </Text>
                <View style={styles.timerButtons}>
                  {!timerActive ? (
                    <TouchableOpacity
                      style={[styles.timerButton, { backgroundColor: colors.primary }]}
                      onPress={startRestTimer}
                    >
                      <Ionicons name="play" size={20} color="#fff" />
                      <Text style={styles.timerButtonText}>{t.workout.start}</Text>
                    </TouchableOpacity>
                  ) : (
                    <TouchableOpacity
                      style={[styles.timerButton, { backgroundColor: colors.error }]}
                      onPress={resetTimer}
                    >
                      <Ionicons name="refresh" size={20} color="#fff" />
                      <Text style={styles.timerButtonText}>{t.workout.restart}</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>

              {/* Complete Button */}
              <TouchableOpacity
                style={[
                  styles.completeButton,
                  { backgroundColor: selectedExercise?.completed ? colors.success : colors.primary }
                ]}
                onPress={() => {
                  toggleExerciseComplete(selectedDayIndex, selectedExerciseIndex, !selectedExercise?.completed);
                }}
              >
                <Ionicons 
                  name={selectedExercise?.completed ? 'checkmark-circle' : 'checkmark-circle-outline'} 
                  size={24} 
                  color="#fff" 
                />
                <Text style={styles.completeButtonText}>
                  {selectedExercise?.completed ? t.workout.completed : t.workout.markComplete}
                </Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* History Modal */}
      <Modal
        visible={showHistoryModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowHistoryModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.historyModalContent, { backgroundColor: colors.background }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>📊 {t.workout.history}</Text>
              <TouchableOpacity onPress={() => setShowHistoryModal(false)}>
                <Ionicons name="close" size={28} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            {/* Stats Summary */}
            {historyStats && (
              <View style={[styles.historyStats, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                <View style={styles.statItem}>
                  <Text style={[styles.statValue, { color: colors.primary }]}>{historyStats.total_workouts}</Text>
                  <Text style={[styles.statLabel, { color: colors.textSecondary }]}>{t.workout.workouts}</Text>
                </View>
                <View style={[styles.statDivider, { backgroundColor: colors.border }]} />
                <View style={styles.statItem}>
                  <Text style={[styles.statValue, { color: colors.success }]}>{historyStats.total_exercises}</Text>
                  <Text style={[styles.statLabel, { color: colors.textSecondary }]}>{t.workout.exercises}</Text>
                </View>
                <View style={[styles.statDivider, { backgroundColor: colors.border }]} />
                <View style={styles.statItem}>
                  <Text style={[styles.statValue, { color: colors.warning }]}>
                    {historyStats.this_week_count}/{historyStats.target_frequency || '-'}
                  </Text>
                  <Text style={[styles.statLabel, { color: colors.textSecondary }]}>{t.workout.thisWeek}</Text>
                </View>
              </View>
            )}
            
            <ScrollView style={styles.historyList} showsVerticalScrollIndicator={false}>
              {loadingHistory ? (
                <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
              ) : workoutHistory.length === 0 ? (
                <View style={styles.emptyHistory}>
                  <Ionicons name="fitness-outline" size={48} color={colors.textTertiary} />
                  <Text style={[styles.emptyHistoryText, { color: colors.textSecondary }]}>
                    {t.workout.noHistory}
                  </Text>
                  <Text style={[styles.emptyHistoryHint, { color: colors.textTertiary }]}>
                    {t.workout.completeHint}
                  </Text>
                </View>
              ) : (
                workoutHistory.map((item, idx) => (
                  <View key={item.id || idx} style={[styles.historyItem, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                    <View style={[styles.historyIcon, { backgroundColor: colors.success + '20' }]}>
                      <Ionicons name="checkmark-circle" size={24} color={colors.success} />
                    </View>
                    <View style={styles.historyInfo}>
                      <Text style={[styles.historyName, { color: colors.text }]}>{item.workout_day_name}</Text>
                      <Text style={[styles.historyMeta, { color: colors.textSecondary }]}>
                        {item.exercises_completed} exercícios • {formatHistoryDate(item.completed_at)}
                      </Text>
                    </View>
                  </View>
                ))
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Toast notification */}
      <Toast
        visible={toast.visible}
        message={toast.message}
        type={toast.type}
        onHide={hideToast}
      />
    </SafeAreaView>
  );
}

function WorkoutDayCard({ day, dayIndex, colors, onExercisePress, onToggleComplete, language }: any) {
  const [expanded, setExpanded] = useState(dayIndex === 0);
  const completedCount = day.exercises?.filter((ex: any) => ex.completed)?.length || 0;
  const totalCount = day.exercises?.length || 0;
  const dayComplete = completedCount === totalCount && totalCount > 0;
  
  // Translate workout name
  const translatedDayName = translateWorkoutName(day.name, language);

  return (
    <View style={[cardStyles.dayCard, { backgroundColor: colors.backgroundCard, borderColor: dayComplete ? colors.success : colors.border }]}>
      <TouchableOpacity style={cardStyles.dayHeader} onPress={() => setExpanded(!expanded)} activeOpacity={0.7}>
        <View style={cardStyles.dayHeaderLeft}>
          <View style={[cardStyles.dayIcon, { backgroundColor: dayComplete ? colors.success + '20' : colors.primary + '20' }]}>
            <Ionicons 
              name={dayComplete ? 'checkmark-circle' : 'barbell-outline'} 
              size={24} 
              color={dayComplete ? colors.success : colors.primary} 
            />
          </View>
          <View style={cardStyles.dayInfo}>
            <Text style={[cardStyles.dayName, { color: colors.text }]}>{translatedDayName}</Text>
            <Text style={[cardStyles.dayMeta, { color: colors.textSecondary }]}>
              {day.day} • {day.duration} min • {completedCount}/{totalCount}
            </Text>
          </View>
        </View>
        <Ionicons name={expanded ? 'chevron-up' : 'chevron-down'} size={20} color={colors.textSecondary} />
      </TouchableOpacity>

      {expanded && (
        <View style={[cardStyles.exercisesList, { borderTopColor: colors.border }]}>
          {day.exercises.map((exercise: any, idx: number) => (
            <TouchableOpacity 
              key={exercise.id || idx} 
              style={[
                cardStyles.exerciseItem, 
                { borderBottomColor: colors.border },
                exercise.completed && { backgroundColor: colors.success + '10' }
              ]}
              onPress={() => onExercisePress(exercise, dayIndex, idx)}
              activeOpacity={0.7}
            >
              <View style={cardStyles.exerciseLeft}>
                <TouchableOpacity
                  style={[
                    cardStyles.checkbox,
                    { borderColor: exercise.completed ? colors.success : colors.border },
                    exercise.completed && { backgroundColor: colors.success }
                  ]}
                  onPress={() => onToggleComplete(dayIndex, idx, !exercise.completed)}
                >
                  {exercise.completed && <Ionicons name="checkmark" size={14} color="#fff" />}
                </TouchableOpacity>
                <View style={cardStyles.exerciseTextContainer}>
                  <Text style={[
                    cardStyles.exerciseName, 
                    { color: colors.text },
                    exercise.completed && { textDecorationLine: 'line-through', color: colors.textSecondary }
                  ]}>
                    {translateExercise(exercise.name, language)}
                  </Text>
                  <Text style={[cardStyles.exerciseDetails, { color: colors.textSecondary }]}>
                    {exercise.sets}x{exercise.reps} • {exercise.rest}
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.textTertiary} />
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
}

const cardStyles = StyleSheet.create({
  dayCard: { borderRadius: 16, marginBottom: 16, borderWidth: 1 },
  dayHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  dayHeaderLeft: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  dayIcon: { width: 48, height: 48, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  dayInfo: { flex: 1 },
  dayName: { fontSize: 17, fontWeight: '700' },
  dayMeta: { fontSize: 13, marginTop: 4 },
  exercisesList: { borderTopWidth: 1 },
  exerciseItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 14, paddingHorizontal: 16, borderBottomWidth: 1 },
  exerciseLeft: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  checkbox: { width: 24, height: 24, borderRadius: 6, borderWidth: 2, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  exerciseTextContainer: { flex: 1 },
  exerciseName: { fontSize: 15, fontWeight: '500' },
  exerciseDetails: { fontSize: 12, marginTop: 2 },
});

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  loadingText: { fontSize: 18, fontWeight: '600', marginTop: 16 },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  emptyTitle: { fontSize: 20, fontWeight: '600', marginTop: 16 },
  emptyText: { fontSize: 14, textAlign: 'center', marginTop: 8 },
  generateButton: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 14, paddingHorizontal: 24, borderRadius: 12, marginTop: 24 },
  generateButtonText: { fontSize: 16, fontWeight: '600', color: '#fff' },
  scrollView: { flex: 1 },
  content: { padding: 16 },
  header: { marginBottom: 16, flexDirection: 'row', alignItems: 'center' },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
  historyButton: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 8 },
  regenerateButton: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  progressCard: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  progressHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
  progressTitle: { fontSize: 16, fontWeight: '600' },
  progressContent: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  progressPercent: { fontSize: 32, fontWeight: '700' },
  progressBarContainer: { flex: 1 },
  progressBarBg: { height: 8, borderRadius: 4 },
  progressBarFill: { height: '100%', borderRadius: 4 },
  progressText: { fontSize: 12, marginTop: 4 },
  // Modal
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 20, maxHeight: '85%' },
  historyModalContent: { borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 20, maxHeight: '90%', minHeight: '60%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 },
  modalTitle: { fontSize: 22, fontWeight: '700', flex: 1, marginRight: 16 },
  // History Modal Styles
  historyStats: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', borderRadius: 16, padding: 16, marginBottom: 16, borderWidth: 1 },
  statItem: { alignItems: 'center' },
  statValue: { fontSize: 24, fontWeight: '700' },
  statLabel: { fontSize: 12, marginTop: 4 },
  statDivider: { width: 1, height: 40 },
  historyList: { flex: 1 },
  emptyHistory: { alignItems: 'center', paddingTop: 40 },
  emptyHistoryText: { fontSize: 16, fontWeight: '600', marginTop: 16 },
  emptyHistoryHint: { fontSize: 13, marginTop: 8, textAlign: 'center' },
  historyItem: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 12, marginBottom: 10, borderWidth: 1 },
  historyIcon: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  historyInfo: { flex: 1, marginLeft: 12 },
  historyName: { fontSize: 15, fontWeight: '600' },
  historyMeta: { fontSize: 12, marginTop: 4 },
  // Exercise Modal Styles
  exerciseInfo: { borderRadius: 16, padding: 20, marginBottom: 16, borderWidth: 1 },
  exerciseInfoRow: { flexDirection: 'row', justifyContent: 'space-around' },
  exerciseInfoItem: { alignItems: 'center', gap: 6 },
  exerciseInfoLabel: { fontSize: 12 },
  exerciseInfoValue: { fontSize: 20, fontWeight: '700' },
  notesCard: { borderRadius: 16, padding: 16, marginBottom: 16, borderWidth: 1 },
  notesHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  notesTitle: { fontSize: 14, fontWeight: '600' },
  notesText: { fontSize: 15, lineHeight: 22 },
  timerCard: { borderRadius: 16, padding: 20, marginBottom: 16, alignItems: 'center', borderWidth: 1 },
  timerTitle: { fontSize: 14, marginBottom: 8 },
  timerDisplay: { fontSize: 48, fontWeight: '700', fontVariant: ['tabular-nums'] },
  timerButtons: { flexDirection: 'row', gap: 12, marginTop: 16 },
  timerButton: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 12, paddingHorizontal: 24, borderRadius: 12 },
  timerButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  completeButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 16, borderRadius: 12, marginBottom: 20 },
  completeButtonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
