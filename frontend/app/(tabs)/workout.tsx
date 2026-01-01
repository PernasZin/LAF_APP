import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Safe fetch with timeout
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
  const [loading, setLoading] = useState(false);
  const [workoutPlan, setWorkoutPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);

  // Carrega dados quando a tela ganha foco
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
        // Busca perfil atualizado do backend (Single Source of Truth)
        try {
          const profileResponse = await axios.get(`${BACKEND_URL}/api/user/profile/${id}`);
          if (profileResponse.data) {
            setUserProfile(profileResponse.data);
            await AsyncStorage.setItem('userProfile', JSON.stringify(profileResponse.data));
          }
        } catch (err) {
          const profileData = await AsyncStorage.getItem('userProfile');
          if (profileData) {
            setUserProfile(JSON.parse(profileData));
          }
        }
        
        // Carrega treino existente
        loadWorkout(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const loadWorkout = async (uid: string) => {
    if (!uid) return;
    
    try {
      const response = await axios.get(`${BACKEND_URL}/api/workout/${uid}`);
      setWorkoutPlan(response.data);
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Erro ao carregar treino:', error);
      }
    }
  };

  const generateWorkout = async () => {
    if (!userId) return;
    
    setLoading(true);
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/workout/generate?user_id=${userId}`
      );
      setWorkoutPlan(response.data);
    } catch (error) {
      console.error('Erro ao gerar treino:', error);
      alert('Erro ao gerar treino. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  // Frequência configurada no perfil (Single Source of Truth)
  const configuredFrequency = userProfile?.weekly_training_frequency || workoutPlan?.weekly_frequency || 0;
  const actualWorkouts = workoutPlan?.workout_days?.length || 0;
  const frequencyMatch = actualWorkouts === configuredFrequency;

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#10B981" />
          <Text style={styles.loadingText}>Gerando seu plano de treino...</Text>
          <Text style={styles.loadingSubtext}>Isso pode levar alguns segundos</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!workoutPlan) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
          <Ionicons name="barbell-outline" size={80} color="#D1D5DB" />
          <Text style={styles.emptyTitle}>Nenhum treino gerado</Text>
          <Text style={styles.emptyText}>
            Gere seu plano de treino personalizado baseado em seus objetivos
          </Text>
          <TouchableOpacity
            style={styles.generateButton}
            onPress={generateWorkout}
            activeOpacity={0.8}
          >
            <Ionicons name="sparkles" size={20} color="#fff" />
            <Text style={styles.generateButtonText}>Gerar Treino com IA</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>Seu Plano de Treino</Text>
            <View style={styles.frequencyRow}>
              <Text style={styles.headerSubtitle}>
                {actualWorkouts} treinos
              </Text>
              {frequencyMatch ? (
                <Ionicons name="checkmark-circle" size={16} color="#10B981" style={{marginLeft: 6}} />
              ) : (
                <Ionicons name="alert-circle" size={16} color="#F59E0B" style={{marginLeft: 6}} />
              )}
            </View>
            <Text style={styles.headerMeta}>
              Meta: {configuredFrequency}x por semana
            </Text>
          </View>
          <TouchableOpacity
            style={styles.regenerateButton}
            onPress={generateWorkout}
          >
            <Ionicons name="refresh" size={20} color="#10B981" />
          </TouchableOpacity>
        </View>

        {/* Workout Days */}
        {workoutPlan.workout_days.map((day: any, index: number) => (
          <WorkoutDayCard key={day.id || index} day={day} />
        ))}

        {/* Notes */}
        {workoutPlan.notes && (
          <View style={styles.notesCard}>
            <Ionicons name="information-circle-outline" size={20} color="#6B7280" />
            <Text style={styles.notesText}>{workoutPlan.notes}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function WorkoutDayCard({ day }: any) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={styles.dayCard}>
      <TouchableOpacity
        style={styles.dayHeader}
        onPress={() => setExpanded(!expanded)}
        activeOpacity={0.7}
      >
        <View style={styles.dayHeaderLeft}>
          <Ionicons name="calendar-outline" size={24} color="#10B981" />
          <View style={styles.dayInfo}>
            <Text style={styles.dayName}>{day.name}</Text>
            <Text style={styles.dayDay}>{day.day} • {day.duration} min</Text>
          </View>
        </View>
        <View style={styles.dayHeaderRight}>
          <Text style={styles.exerciseCount}>{day.exercises.length} exercícios</Text>
          <Ionicons
            name={expanded ? 'chevron-up' : 'chevron-down'}
            size={20}
            color="#6B7280"
          />
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.exercisesList}>
          {day.exercises.map((exercise: any, idx: number) => (
            <View key={exercise.id || idx} style={styles.exerciseItem}>
              <View style={styles.exerciseHeader}>
                <Text style={styles.exerciseName}>{exercise.name}</Text>
                <Text style={styles.muscleGroup}>{exercise.muscle_group}</Text>
              </View>
              <View style={styles.exerciseDetails}>
                <View style={styles.detailItem}>
                  <Ionicons name="repeat" size={14} color="#6B7280" />
                  <Text style={styles.detailText}>{exercise.sets} séries</Text>
                </View>
                <View style={styles.detailItem}>
                  <Ionicons name="fitness" size={14} color="#6B7280" />
                  <Text style={styles.detailText}>{exercise.reps} reps</Text>
                </View>
                <View style={styles.detailItem}>
                  <Ionicons name="time-outline" size={14} color="#6B7280" />
                  <Text style={styles.detailText}>{exercise.rest}</Text>
                </View>
              </View>
              {exercise.notes && (
                <Text style={styles.exerciseNotes}>💡 {exercise.notes}</Text>
              )}
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  emptyText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
  generateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#10B981',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginTop: 24,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  headerMeta: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 2,
  },
  frequencyRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  regenerateButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F0FDF4',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dayCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  dayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  dayHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  dayInfo: {
    flex: 1,
  },
  dayName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  dayDay: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  dayHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  exerciseCount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
  },
  exercisesList: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    padding: 16,
    gap: 16,
  },
  exerciseItem: {
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  exerciseHeader: {
    marginBottom: 8,
  },
  exerciseName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#111827',
  },
  muscleGroup: {
    fontSize: 13,
    color: '#10B981',
    marginTop: 2,
  },
  exerciseDetails: {
    flexDirection: 'row',
    gap: 16,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    fontSize: 13,
    color: '#6B7280',
  },
  exerciseNotes: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
    fontStyle: 'italic',
  },
  notesCard: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  notesText: {
    flex: 1,
    fontSize: 12,
    color: '#92400E',
    lineHeight: 18,
  },
});

