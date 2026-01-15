/**
 * LAF Premium Workout Screen
 * ==========================
 * Glassmorphism + Gradientes + Animações
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
import Animated, { FadeInDown } from 'react-native-reanimated';
import {
  Dumbbell, Timer, Play, Pause, RotateCcw, ChevronRight,
  X, Check, Target, Flame, Calendar, Clock, Repeat
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { WorkoutSkeleton } from '../../components';
import { useTranslation, translateExercise, translateWorkoutName, translateExerciseFocus, translateWorkoutDayName, translateWorkoutNotes } from '../../i18n';

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

// Workout Day Card
const WorkoutDayCard = ({ day, index, isDark, theme, onExercisePress, language, t }: any) => {
  const isToday = index === new Date().getDay() - 1;
  const totalExercises = day.exercises?.length || 0;
  
  // Tradução para "HOJE"
  const todayLabel = language === 'en-US' ? 'TODAY' : language === 'es-ES' ? 'HOY' : 'HOJE';
  
  return (
    <Animated.View entering={FadeInDown.delay(index * 100).springify()}>
      <GlassCard isDark={isDark} style={styles.dayCard}>
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

  // Timer state
  const [timerActive, setTimerActive] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [showTimer, setShowTimer] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Exercise modal
  const [selectedExercise, setSelectedExercise] = useState<any>(null);
  const [showExerciseModal, setShowExerciseModal] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadWorkout();
      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
      };
    }, [])
  );

  const loadWorkout = async () => {
    try {
      setInitialLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        const response = await safeFetch(`${BACKEND_URL}/api/workout/${id}`);
        if (response.ok) {
          const data = await response.json();
          setWorkoutPlan(data);
        }
      }
    } catch (error) {
      console.error('Error loading workout:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadWorkout();
    setRefreshing(false);
  };

  // Função para GERAR novo treino
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

  const startTimer = (seconds: number) => {
    setTimerSeconds(seconds);
    setTimerActive(true);
    setShowTimer(true);
    timerRef.current = setInterval(() => {
      setTimerSeconds((prev) => {
        if (prev <= 1) {
          setTimerActive(false);
          if (timerRef.current) clearInterval(timerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopTimer = () => {
    setTimerActive(false);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (initialLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <WorkoutSkeleton />
      </SafeAreaView>
    );
  }

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
              style={[styles.timerButton, { backgroundColor: showTimer ? premiumColors.primary : (isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)') }]}
              onPress={() => setShowTimer(!showTimer)}
            >
              <Timer size={20} color={showTimer ? '#FFF' : theme.text} />
            </TouchableOpacity>
          </Animated.View>

          {/* Timer Card */}
          {showTimer && (
            <Animated.View entering={FadeInDown.springify()}>
              <GlassCard isDark={isDark} style={styles.timerCard}>
                <Text style={[styles.timerDisplay, { color: theme.text }]}>
                  {formatTime(timerSeconds)}
                </Text>
                <View style={styles.timerButtons}>
                  <TouchableOpacity
                    style={[styles.timerBtn, { backgroundColor: '#EF4444' + '20' }]}
                    onPress={() => { stopTimer(); setTimerSeconds(0); }}
                  >
                    <RotateCcw size={20} color="#EF4444" />
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.timerMainBtn}
                    onPress={() => timerActive ? stopTimer() : startTimer(timerSeconds || 60)}
                  >
                    <LinearGradient
                      colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                      style={styles.timerMainBtnGradient}
                    >
                      {timerActive ? <Pause size={24} color="#FFF" /> : <Play size={24} color="#FFF" />}
                    </LinearGradient>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.timerBtn, { backgroundColor: premiumColors.primary + '20' }]}
                    onPress={() => startTimer(60)}
                  >
                    <Text style={[styles.timerBtnText, { color: premiumColors.primary }]}>60s</Text>
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
                />
              ))}
            </>
          ) : (
            /* Estado Vazio - Sem Treino */
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
                {/* Foco muscular */}
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
                    startTimer(selectedExercise.rest || 60);
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
    </View>
  );
}

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
  timerButton: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },

  timerCard: {
    padding: spacing.xl,
    alignItems: 'center',
  },
  timerDisplay: {
    fontSize: 56,
    fontWeight: '800',
    letterSpacing: -2,
    fontVariant: ['tabular-nums'],
  },
  timerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.lg,
    marginTop: spacing.lg,
  },
  timerBtn: {
    width: 48,
    height: 48,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  timerBtnText: { fontSize: 14, fontWeight: '700' },
  timerMainBtn: {
    width: 64,
    height: 64,
    borderRadius: 32,
    overflow: 'hidden',
  },
  timerMainBtnGradient: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },

  dayCard: { marginBottom: spacing.md },
  dayHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.base,
    gap: spacing.md,
  },
  dayIconBg: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dayHeaderContent: { flex: 1 },
  dayTitleRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  dayName: { fontSize: 16, fontWeight: '700', letterSpacing: -0.3 },
  todayBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.sm,
  },
  todayBadgeText: { color: '#FFF', fontSize: 10, fontWeight: '800' },
  dayExerciseCount: { fontSize: 13, marginTop: 2 },

  exercisesList: { paddingHorizontal: spacing.base },
  exerciseItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  exerciseInfo: { flex: 1 },
  exerciseName: { fontSize: 15, fontWeight: '600' },
  exerciseFocus: { fontSize: 12, fontWeight: '500', marginTop: 2 },
  exerciseDetails: { flexDirection: 'row', gap: spacing.md, marginTop: 4 },
  exerciseDetail: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  exerciseDetailText: { fontSize: 12 },

  modalOverlay: { flex: 1, justifyContent: 'flex-end' },
  modalContent: {
    borderTopLeftRadius: radius['2xl'],
    borderTopRightRadius: radius['2xl'],
    padding: spacing.lg,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  modalTitle: { fontSize: 20, fontWeight: '700', flex: 1 },

  exerciseModalContent: { gap: spacing.lg },
  focusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.lg,
  },
  focusBadgeText: { fontSize: 14, fontWeight: '600' },
  exerciseModalStats: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  exerciseModalStat: {
    flex: 1,
    alignItems: 'center',
    padding: spacing.base,
    borderRadius: radius.lg,
    gap: spacing.xs,
  },
  exerciseModalStatValue: { fontSize: 24, fontWeight: '800' },
  exerciseModalStatLabel: { fontSize: 12, fontWeight: '600' },
  exerciseNotes: {
    padding: spacing.base,
    borderRadius: radius.lg,
  },
  exerciseNotesText: { fontSize: 14, lineHeight: 20 },
  startTimerBtn: {
    height: 52,
    borderRadius: radius.lg,
    overflow: 'hidden',
  },
  startTimerBtnGradient: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  startTimerBtnText: { color: '#FFF', fontSize: 16, fontWeight: '700' },

  // Empty State Styles
  emptyStateCard: { padding: spacing.xl },
  emptyStateContent: { alignItems: 'center', gap: spacing.md },
  emptyIconBg: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  emptyTitle: { fontSize: 20, fontWeight: '700', textAlign: 'center' },
  emptyDescription: { 
    fontSize: 14, 
    textAlign: 'center', 
    lineHeight: 20,
    paddingHorizontal: spacing.lg,
  },
  generateButton: { 
    marginTop: spacing.md,
    borderRadius: radius.xl,
    overflow: 'hidden',
  },
  generateButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
  },
  generateButtonText: { 
    color: '#FFF', 
    fontSize: 16, 
    fontWeight: '700',
  },
  regenerateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.lg,
    marginTop: spacing.sm,
  },
  regenerateButtonText: { fontSize: 14, fontWeight: '600' },
});
