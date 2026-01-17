import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Dumbbell, CheckCircle, Moon, Flame } from 'lucide-react-native';
import { useWorkoutStore, adjustMacrosByDay } from '../stores/workoutStore';

interface WorkoutTrackerProps {
  userId: string;
  baseCalories?: number;
  baseCarbs?: number;
  baseProtein?: number;
  baseFat?: number;
  onWorkoutFinished?: () => void;
}

export const WorkoutTracker: React.FC<WorkoutTrackerProps> = ({
  userId,
  baseCalories = 0,
  baseCarbs = 0,
  baseProtein = 0,
  baseFat = 0,
  onWorkoutFinished,
}) => {
  const {
    todayStatus,
    adjustedMacros,
    isLoading,
    error,
    fetchTodayStatus,
    finishWorkout,
    fetchAdjustedMacros,
    clearError,
  } = useWorkoutStore();

  const [finishing, setFinishing] = useState(false);

  useEffect(() => {
    if (userId) {
      fetchTodayStatus(userId);
      fetchAdjustedMacros(userId);
    }
  }, [userId]);

  const handleFinishWorkout = async () => {
    Alert.alert(
      '🏋️ Concluir Treino',
      'Tem certeza que deseja marcar o treino de hoje como concluído?',
      [
        {
          text: 'Cancelar',
          style: 'cancel',
        },
        {
          text: 'Concluir',
          onPress: async () => {
            setFinishing(true);
            const success = await finishWorkout(userId);
            setFinishing(false);
            
            if (success) {
              onWorkoutFinished?.();
            }
          },
        },
      ]
    );
  };

  // Se já treinou
  const trained = todayStatus?.trained || false;
  const isScheduledTraining = todayStatus?.isScheduledTrainingDay || false;
  
  // Determina tipo de dia
  const dietType = trained ? 'training' : 'rest';
  const isTrainingDay = trained;

  // Calcula macros ajustados localmente se não tiver do servidor
  const localAdjusted = adjustMacrosByDay(
    baseCalories,
    baseProtein,
    baseCarbs,
    baseFat,
    isTrainingDay
  );

  const displayMacros = adjustedMacros || localAdjusted;

  return (
    <View style={styles.container}>
      {/* Header - Tipo de Dia */}
      <LinearGradient
        colors={isTrainingDay ? ['#4CAF50', '#45a049'] : ['#607D8B', '#546E7A']}
        style={styles.headerGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <View style={styles.headerContent}>
          {isTrainingDay ? (
            <>
              <Dumbbell size={24} color="#fff" />
              <Text style={styles.headerTitle}>Hoje: Dia de Treino 🏋️</Text>
            </>
          ) : (
            <>
              <Moon size={24} color="#fff" />
              <Text style={styles.headerTitle}>Hoje: Dia de Descanso 💤</Text>
            </>
          )}
        </View>
        
        <View style={styles.dietTypeTag}>
          <Text style={styles.dietTypeText}>
            Dieta: {isTrainingDay ? 'Treino' : 'Descanso'}
          </Text>
        </View>
      </LinearGradient>

      {/* Macros Ajustados */}
      {baseCalories > 0 && (
        <View style={styles.macrosContainer}>
          <Text style={styles.macrosTitle}>Macros do Dia</Text>
          
          <View style={styles.macrosRow}>
            <View style={styles.macroItem}>
              <Flame size={16} color="#FF5722" />
              <Text style={styles.macroValue}>
                {Math.round(displayMacros.adjustedCalories)}
              </Text>
              <Text style={styles.macroLabel}>kcal</Text>
            </View>
            
            <View style={styles.macroDivider} />
            
            <View style={styles.macroItem}>
              <Text style={[styles.macroValue, styles.proteinColor]}>
                {Math.round(displayMacros.adjustedProtein)}g
              </Text>
              <Text style={styles.macroLabel}>Proteína</Text>
            </View>
            
            <View style={styles.macroDivider} />
            
            <View style={styles.macroItem}>
              <Text style={[styles.macroValue, styles.carbsColor]}>
                {Math.round(displayMacros.adjustedCarbs)}g
              </Text>
              <Text style={styles.macroLabel}>Carbs</Text>
            </View>
            
            <View style={styles.macroDivider} />
            
            <View style={styles.macroItem}>
              <Text style={[styles.macroValue, styles.fatColor]}>
                {Math.round(displayMacros.adjustedFat)}g
              </Text>
              <Text style={styles.macroLabel}>Gordura</Text>
            </View>
          </View>

          <Text style={styles.multiplierInfo}>
            {displayMacros.multiplierInfo}
          </Text>
        </View>
      )}

      {/* Botão de Concluir Treino */}
      <View style={styles.buttonContainer}>
        {trained ? (
          <View style={styles.completedContainer}>
            <CheckCircle size={24} color="#4CAF50" />
            <Text style={styles.completedText}>✅ Treino concluído hoje</Text>
          </View>
        ) : (
          <TouchableOpacity
            style={[
              styles.finishButton,
              (isLoading || finishing) && styles.finishButtonDisabled,
            ]}
            onPress={handleFinishWorkout}
            disabled={isLoading || finishing}
          >
            {finishing ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <>
                <Dumbbell size={20} color="#fff" />
                <Text style={styles.finishButtonText}>
                  Concluir treino de hoje
                </Text>
              </>
            )}
          </TouchableOpacity>
        )}
      </View>

      {/* Scheduled Training Info */}
      {!trained && isScheduledTraining && (
        <Text style={styles.scheduledText}>
          📅 Treino agendado para hoje
        </Text>
      )}

      {/* Error */}
      {error && (
        <TouchableOpacity onPress={clearError}>
          <Text style={styles.errorText}>{error}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  headerGradient: {
    padding: 16,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  dietTypeTag: {
    marginTop: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  dietTypeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  macrosContainer: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  macrosTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 12,
    textAlign: 'center',
  },
  macrosRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  macroItem: {
    alignItems: 'center',
    flex: 1,
  },
  macroValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  macroLabel: {
    fontSize: 11,
    color: '#888',
    marginTop: 2,
  },
  macroDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#e0e0e0',
  },
  proteinColor: {
    color: '#E91E63',
  },
  carbsColor: {
    color: '#FF9800',
  },
  fatColor: {
    color: '#2196F3',
  },
  multiplierInfo: {
    fontSize: 11,
    color: '#888',
    textAlign: 'center',
    marginTop: 12,
    fontStyle: 'italic',
  },
  buttonContainer: {
    padding: 16,
  },
  finishButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4CAF50',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  finishButtonDisabled: {
    opacity: 0.6,
  },
  finishButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  completedContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E8F5E9',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  completedText: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: '600',
  },
  scheduledText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    paddingBottom: 12,
  },
  errorText: {
    fontSize: 12,
    color: '#F44336',
    textAlign: 'center',
    padding: 8,
  },
});

export default WorkoutTracker;
