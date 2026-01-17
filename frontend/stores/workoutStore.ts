import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import config from '../config';

// ==================== TYPES ====================

interface WorkoutDayStatus {
  date: string;
  trained: boolean;
  completedAt: string | null;
  isScheduledTrainingDay: boolean;
  isTrainingDay: boolean;
  dietType: 'training' | 'rest';
  calorieMultiplier: number;
  carbMultiplier: number;
}

interface AdjustedMacros {
  baseCalories: number;
  adjustedCalories: number;
  baseProtein: number;
  adjustedProtein: number;
  baseCarbs: number;
  adjustedCarbs: number;
  baseFat: number;
  adjustedFat: number;
  dietType: 'training' | 'rest';
  isTrainingDay: boolean;
  multiplierInfo: string;
}

interface WorkoutHistory {
  date: string;
  trained: boolean;
  completedAt: string | null;
}

interface WorkoutStore {
  // State
  todayStatus: WorkoutDayStatus | null;
  adjustedMacros: AdjustedMacros | null;
  history: WorkoutHistory[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchTodayStatus: (userId: string) => Promise<void>;
  finishWorkout: (userId: string, date?: string) => Promise<boolean>;
  fetchAdjustedMacros: (userId: string, date?: string) => Promise<void>;
  fetchHistory: (userId: string, days?: number) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

// ==================== HELPERS ====================

const getTodayDate = (): string => {
  const now = new Date();
  return now.toISOString().split('T')[0]; // YYYY-MM-DD
};

// ==================== STORE ====================

export const useWorkoutStore = create<WorkoutStore>()(
  persist(
    (set, get) => ({
      // Initial state
      todayStatus: null,
      adjustedMacros: null,
      history: [],
      isLoading: false,
      error: null,
      
      // Fetch today's workout status
      fetchTodayStatus: async (userId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const today = getTodayDate();
          const response = await fetch(
            `${config.backendUrl}/api/workout/status/${userId}?date=${today}`
          );
          
          if (!response.ok) {
            throw new Error('Erro ao buscar status do treino');
          }
          
          const data = await response.json();
          
          set({
            todayStatus: {
              date: data.date,
              trained: data.trained,
              completedAt: data.completed_at,
              isScheduledTrainingDay: data.is_scheduled_training_day,
              isTrainingDay: data.is_training_day,
              dietType: data.diet_type,
              calorieMultiplier: data.calorie_multiplier,
              carbMultiplier: data.carb_multiplier,
            },
            isLoading: false,
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Erro desconhecido',
            isLoading: false 
          });
        }
      },
      
      // Mark today's workout as finished
      finishWorkout: async (userId: string, date?: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(
            `${config.backendUrl}/api/workout/finish/${userId}`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ date: date || getTodayDate() }),
            }
          );
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao marcar treino');
          }
          
          const data = await response.json();
          
          // Update today's status
          set({
            todayStatus: {
              ...get().todayStatus!,
              trained: true,
              completedAt: data.completed_at,
              isTrainingDay: true,
              dietType: 'training',
              calorieMultiplier: 1.05,
              carbMultiplier: 1.15,
            },
            isLoading: false,
          });
          
          // Refresh adjusted macros
          await get().fetchAdjustedMacros(userId);
          
          return true;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Erro desconhecido',
            isLoading: false 
          });
          return false;
        }
      },
      
      // Fetch adjusted macros for the day
      fetchAdjustedMacros: async (userId: string, date?: string) => {
        try {
          const targetDate = date || getTodayDate();
          const response = await fetch(
            `${config.backendUrl}/api/workout/adjusted-macros/${userId}?date=${targetDate}`
          );
          
          if (!response.ok) {
            // Pode não ter dieta ainda, não é erro crítico
            return;
          }
          
          const data = await response.json();
          
          set({
            adjustedMacros: {
              baseCalories: data.base_calories,
              adjustedCalories: data.adjusted_calories,
              baseProtein: data.base_protein,
              adjustedProtein: data.adjusted_protein,
              baseCarbs: data.base_carbs,
              adjustedCarbs: data.adjusted_carbs,
              baseFat: data.base_fat,
              adjustedFat: data.adjusted_fat,
              dietType: data.diet_type,
              isTrainingDay: data.trained,
              multiplierInfo: data.multiplier_info,
            },
          });
        } catch (error) {
          // Silently fail - macros adjustment is optional
          console.log('Could not fetch adjusted macros:', error);
        }
      },
      
      // Fetch workout history
      fetchHistory: async (userId: string, days: number = 30) => {
        try {
          const response = await fetch(
            `${config.backendUrl}/api/workout/history/${userId}?days=${days}`
          );
          
          if (!response.ok) {
            throw new Error('Erro ao buscar histórico');
          }
          
          const data = await response.json();
          
          set({
            history: data.history.map((h: any) => ({
              date: h.date,
              trained: h.trained,
              completedAt: h.completed_at,
            })),
          });
        } catch (error) {
          console.log('Could not fetch workout history:', error);
        }
      },
      
      clearError: () => set({ error: null }),
      
      reset: () => set({
        todayStatus: null,
        adjustedMacros: null,
        history: [],
        isLoading: false,
        error: null,
      }),
    }),
    {
      name: 'workout-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        todayStatus: state.todayStatus,
        history: state.history,
      }),
    }
  )
);

// ==================== UTILITY FUNCTIONS ====================

/**
 * Retorna o status de treino do dia atual
 */
export const getTodayStatus = () => {
  return useWorkoutStore.getState().todayStatus;
};

/**
 * Verifica se hoje é dia de treino
 */
export const isTrainingDay = (): boolean => {
  const status = useWorkoutStore.getState().todayStatus;
  return status?.trained || status?.isScheduledTrainingDay || false;
};

/**
 * Ajusta macros baseado no tipo de dia
 */
export const adjustMacrosByDay = (
  baseCalories: number,
  baseProtein: number,
  baseCarbs: number,
  baseFat: number,
  trained: boolean
): AdjustedMacros => {
  const isTraining = trained;
  
  const calorieMultiplier = isTraining ? 1.05 : 0.95;
  const carbMultiplier = isTraining ? 1.15 : 0.80;
  
  return {
    baseCalories,
    adjustedCalories: Math.round(baseCalories * calorieMultiplier),
    baseProtein,
    adjustedProtein: baseProtein, // Não muda
    baseCarbs,
    adjustedCarbs: Math.round(baseCarbs * carbMultiplier),
    baseFat,
    adjustedFat: baseFat, // Não muda
    dietType: isTraining ? 'training' : 'rest',
    isTrainingDay: isTraining,
    multiplierInfo: isTraining 
      ? '+5% calorias, +15% carbs' 
      : '-5% calorias, -20% carbs',
  };
};
