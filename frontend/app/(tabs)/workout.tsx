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
  const styles = createStyles(colors);
  
  const [loading, setLoading] = useState(false);
  const [workoutPlan, setWorkoutPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  
  // Exercise detail modal
  const [selectedExercise, setSelectedExercise] = useState<any>(null);
  const [selectedDayIndex, setSelectedDayIndex] = useState(-1);
  const [selectedExerciseIndex, setSelectedExerciseIndex] = useState(-1);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  
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
        loadWorkout(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
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
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/generate?user_id=${userId}`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setWorkoutPlan(data);
      } else {
        Alert.alert('Erro', 'Erro ao gerar treino. Tente novamente.');
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro de conexão.');
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
      }
    } catch (error) {
      console.error('Erro ao atualizar exercício:', error);
    }
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

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.text }]}>Gerando treino...</Text>
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
          <Text style={[styles.emptyTitle, { color: colors.text }]}>Nenhum treino gerado</Text>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
            Gere seu plano de treino personalizado
          </Text>
          <TouchableOpacity
            style={[styles.generateButton, { backgroundColor: colors.primary }]}
            onPress={generateWorkout}
            activeOpacity={0.8}
          >
            <Ionicons name="sparkles" size={20} color="#fff" />
            <Text style={styles.generateButtonText}>Gerar Meu Treino</Text>
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
            <Text style={[styles.headerTitle, { color: colors.text }]}>Seu Treino</Text>
            <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
              {workoutPlan.notes || `${workoutPlan.weekly_frequency}x por semana`}
            </Text>
          </View>
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
                {completedExercises}/{totalExercises} exercícios
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
                    <Text style={[styles.exerciseInfoLabel, { color: colors.textSecondary }]}>Séries</Text>
                    <Text style={[styles.exerciseInfoValue, { color: colors.text }]}>{selectedExercise?.sets}</Text>
                  </View>
                  <View style={styles.exerciseInfoItem}>
                    <Ionicons name="fitness-outline" size={24} color={colors.primary} />
                    <Text style={[styles.exerciseInfoLabel, { color: colors.textSecondary }]}>Repetições</Text>
                    <Text style={[styles.exerciseInfoValue, { color: colors.text }]}>{selectedExercise?.reps}</Text>
                  </View>
                  <View style={styles.exerciseInfoItem}>
                    <Ionicons name="time-outline" size={24} color={colors.primary} />
                    <Text style={[styles.exerciseInfoLabel, { color: colors.textSecondary }]}>Descanso</Text>
                    <Text style={[styles.exerciseInfoValue, { color: colors.text }]}>{selectedExercise?.rest}</Text>
                  </View>
                </View>
              </View>

              {/* Execution Notes - TEXT GUIDANCE */}
              {selectedExercise?.notes && (
                <View style={[styles.notesCard, { backgroundColor: colors.primary + '15', borderColor: colors.primary + '30' }]}>
                  <View style={styles.notesHeader}>
                    <Ionicons name="bulb-outline" size={20} color={colors.primary} />
                    <Text style={[styles.notesTitle, { color: colors.primary }]}>Como executar</Text>
                  </View>
                  <Text style={[styles.notesText, { color: colors.text }]}>{selectedExercise.notes}</Text>
                </View>
              )}

              {/* Rest Timer */}
              <View style={[styles.timerCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                <Text style={[styles.timerTitle, { color: colors.textSecondary }]}>Timer de Descanso</Text>
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
                      <Text style={styles.timerButtonText}>Iniciar</Text>
                    </TouchableOpacity>
                  ) : (
                    <TouchableOpacity
                      style={[styles.timerButton, { backgroundColor: colors.error }]}
                      onPress={resetTimer}
                    >
                      <Ionicons name="refresh" size={20} color="#fff" />
                      <Text style={styles.timerButtonText}>Reiniciar</Text>
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
                  {selectedExercise?.completed ? 'Concluído!' : 'Marcar como Concluído'}
                </Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

function WorkoutDayCard({ day, dayIndex, colors, onExercisePress, onToggleComplete }: any) {
  const [expanded, setExpanded] = useState(dayIndex === 0);
  const completedCount = day.exercises?.filter((ex: any) => ex.completed)?.length || 0;
  const totalCount = day.exercises?.length || 0;
  const dayComplete = completedCount === totalCount && totalCount > 0;

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
            <Text style={[cardStyles.dayName, { color: colors.text }]}>{day.name}</Text>
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
                    {exercise.name}
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
  header: { marginBottom: 16 },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
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
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 },
  modalTitle: { fontSize: 22, fontWeight: '700', flex: 1, marginRight: 16 },
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
