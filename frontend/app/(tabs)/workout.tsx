import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);
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

  useFocusEffect(
    useCallback(() => {
      loadUserData();
    }, [])
  );

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
            await AsyncStorage.setItem('userProfile', JSON.stringify(data));
          }
        } catch (err) {
          const profileData = await AsyncStorage.getItem('userProfile');
          if (profileData) {
            setUserProfile(JSON.parse(profileData));
          }
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
      console.log('Workout not loaded (may not exist yet)');
    }
  };

  const generateWorkout = async () => {
    if (!userId || !BACKEND_URL) return;
    setLoading(true);
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/workout/generate?user_id=${userId}`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setWorkoutPlan(data);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        alert(`Erro ao gerar treino: ${errorData.detail || 'Tente novamente'}`);
      }
    } catch (error) {
      console.error('Erro ao gerar treino:', error);
      alert('Erro de conexão. Verifique sua internet e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  const configuredFrequency = userProfile?.weekly_training_frequency || workoutPlan?.weekly_frequency || 0;
  const actualWorkouts = workoutPlan?.workout_days?.length || 0;
  const frequencyMatch = actualWorkouts === configuredFrequency;

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.text }]}>Gerando seu plano de treino...</Text>
          <Text style={[styles.loadingSubtext, { color: colors.textSecondary }]}>Isso pode levar alguns segundos</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!workoutPlan) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} colors={[colors.primary]} />}
        >
          <Ionicons name="barbell-outline" size={80} color={colors.textTertiary} />
          <Text style={[styles.emptyTitle, { color: colors.text }]}>Nenhum treino gerado</Text>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
            Gere seu plano de treino personalizado baseado em seus objetivos
          </Text>
          <TouchableOpacity
            style={[styles.generateButton, { backgroundColor: colors.primary }]}
            onPress={generateWorkout}
            activeOpacity={0.8}
          >
            <Ionicons name="sparkles" size={20} color={colors.textInverse} />
            <Text style={[styles.generateButtonText, { color: colors.textInverse }]}>Gerar Treino com IA</Text>
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
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} colors={[colors.primary]} />}
      >
        <View style={styles.header}>
          <View>
            <Text style={[styles.headerTitle, { color: colors.text }]}>Seu Plano de Treino</Text>
            <View style={styles.frequencyRow}>
              <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>{actualWorkouts} treinos</Text>
              <Ionicons name={frequencyMatch ? "checkmark-circle" : "alert-circle"} size={16} color={frequencyMatch ? colors.success : colors.warning} style={{marginLeft: 6}} />
            </View>
            <Text style={[styles.headerMeta, { color: colors.textTertiary }]}>Meta: {configuredFrequency}x por semana</Text>
          </View>
          <TouchableOpacity style={[styles.regenerateButton, { backgroundColor: colors.primary + '20' }]} onPress={generateWorkout}>
            <Ionicons name="refresh" size={20} color={colors.primary} />
          </TouchableOpacity>
        </View>

        {workoutPlan.workout_days.map((day: any, index: number) => (
          <WorkoutDayCard key={day.id || index} day={day} colors={colors} />
        ))}

        {workoutPlan.notes && (
          <View style={[styles.notesCard, { backgroundColor: colors.warning + '20' }]}>
            <Ionicons name="information-circle-outline" size={20} color={colors.warning} />
            <Text style={[styles.notesText, { color: colors.text }]}>{workoutPlan.notes}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function WorkoutDayCard({ day, colors }: any) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={[cardStyles.dayCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
      <TouchableOpacity style={cardStyles.dayHeader} onPress={() => setExpanded(!expanded)} activeOpacity={0.7}>
        <View style={cardStyles.dayHeaderLeft}>
          <Ionicons name="calendar-outline" size={24} color={colors.primary} />
          <View style={cardStyles.dayInfo}>
            <Text style={[cardStyles.dayName, { color: colors.text }]}>{day.name}</Text>
            <Text style={[cardStyles.dayDay, { color: colors.textSecondary }]}>{day.day} • {day.duration} min</Text>
          </View>
        </View>
        <View style={cardStyles.dayHeaderRight}>
          <Text style={[cardStyles.exerciseCount, { color: colors.primary }]}>{day.exercises.length} exercícios</Text>
          <Ionicons name={expanded ? 'chevron-up' : 'chevron-down'} size={20} color={colors.textSecondary} />
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={[cardStyles.exercisesList, { borderTopColor: colors.border }]}>
          {day.exercises.map((exercise: any, idx: number) => (
            <View key={exercise.id || idx} style={[cardStyles.exerciseItem, { borderBottomColor: colors.border }]}>
              <View style={cardStyles.exerciseHeader}>
                <Text style={[cardStyles.exerciseName, { color: colors.text }]}>{exercise.name}</Text>
                <Text style={[cardStyles.muscleGroup, { color: colors.primary }]}>{exercise.muscle_group}</Text>
              </View>
              <View style={cardStyles.exerciseDetails}>
                <View style={cardStyles.detailItem}>
                  <Ionicons name="repeat" size={14} color={colors.textSecondary} />
                  <Text style={[cardStyles.detailText, { color: colors.textSecondary }]}>{exercise.sets} séries</Text>
                </View>
                <View style={cardStyles.detailItem}>
                  <Ionicons name="fitness" size={14} color={colors.textSecondary} />
                  <Text style={[cardStyles.detailText, { color: colors.textSecondary }]}>{exercise.reps} reps</Text>
                </View>
                <View style={cardStyles.detailItem}>
                  <Ionicons name="time-outline" size={14} color={colors.textSecondary} />
                  <Text style={[cardStyles.detailText, { color: colors.textSecondary }]}>{exercise.rest}</Text>
                </View>
              </View>
              {exercise.notes && (
                <Text style={[cardStyles.exerciseNotes, { color: colors.textSecondary }]}>💡 {exercise.notes}</Text>
              )}
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const cardStyles = StyleSheet.create({
  dayCard: { borderRadius: 12, marginBottom: 12, borderWidth: 1 },
  dayHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  dayHeaderLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  dayInfo: { flex: 1 },
  dayName: { fontSize: 16, fontWeight: '600' },
  dayDay: { fontSize: 14, marginTop: 2 },
  dayHeaderRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  exerciseCount: { fontSize: 14, fontWeight: '600' },
  exercisesList: { borderTopWidth: 1, padding: 16, gap: 16 },
  exerciseItem: { paddingBottom: 16, borderBottomWidth: 1 },
  exerciseHeader: { marginBottom: 8 },
  exerciseName: { fontSize: 15, fontWeight: '600' },
  muscleGroup: { fontSize: 13, marginTop: 2 },
  exerciseDetails: { flexDirection: 'row', gap: 16 },
  detailItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  detailText: { fontSize: 13 },
  exerciseNotes: { fontSize: 12, marginTop: 8, fontStyle: 'italic' },
});

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  loadingText: { fontSize: 18, fontWeight: '600', marginTop: 16 },
  loadingSubtext: { fontSize: 14, marginTop: 8 },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  emptyTitle: { fontSize: 20, fontWeight: '600', marginTop: 16 },
  emptyText: { fontSize: 14, textAlign: 'center', marginTop: 8, lineHeight: 20 },
  generateButton: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 14, paddingHorizontal: 24, borderRadius: 12, marginTop: 24 },
  generateButtonText: { fontSize: 16, fontWeight: '600' },
  scrollView: { flex: 1 },
  content: { padding: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  headerTitle: { fontSize: 24, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
  headerMeta: { fontSize: 12, marginTop: 2 },
  frequencyRow: { flexDirection: 'row', alignItems: 'center', marginTop: 4 },
  regenerateButton: { width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center' },
  notesCard: { flexDirection: 'row', gap: 12, padding: 12, borderRadius: 8, marginTop: 8 },
  notesText: { flex: 1, fontSize: 12, lineHeight: 18 },
});
