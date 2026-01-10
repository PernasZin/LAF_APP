import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';
import { getColors } from '../../theme/colors';
import { translations, SupportedLanguage } from '../../i18n/translations';
import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeout);
    return response;
  } catch (error) {
    clearTimeout(timeout);
    throw error;
  }
};

interface CardioExercise {
  id: string;
  name: string;
  name_en: string;
  name_es: string;
  duration_minutes: number;
  intensity: string;
  calories_burned: number;
  heart_rate_zone: string;
  description: string;
  description_en: string;
  description_es: string;
  how_to_feel: string;
  how_to_feel_en: string;
  how_to_feel_es: string;
  substitutes: string[];
  substitutes_detailed?: {
    id: string;
    name: string;
    name_en: string;
    name_es: string;
    original_duration: number;
    equivalent_duration: number;
    intensity: string;
  }[];
  sessions_per_week: number;
}

export default function CardioScreen() {
  const router = useRouter();
  const { theme } = useTheme();
  const colors = getColors(theme);
  
  const [language, setLanguage] = useState<SupportedLanguage>('pt-BR');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [cardioData, setCardioData] = useState<any>(null);
  const [selectedExercise, setSelectedExercise] = useState<CardioExercise | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Recarrega quando a tela ganha foco
  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  const loadData = async () => {
    try {
      const [id, lang] = await Promise.all([
        AsyncStorage.getItem('userId'),
        AsyncStorage.getItem('language'),
      ]);
      
      setUserId(id);
      if (lang) setLanguage(lang as SupportedLanguage);
      
      if (id && BACKEND_URL) {
        const response = await safeFetch(`${BACKEND_URL}/api/cardio/${id}`);
        if (response.ok) {
          const data = await response.json();
          setCardioData(data);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar cardio:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const getLocalizedText = (base: string, en: string, es: string) => {
    if (language === 'en-US') return en;
    if (language === 'es-ES') return es;
    return base;
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'low': return '#10B981';
      case 'moderate': return '#F59E0B';
      case 'high': return '#EF4444';
      default: return colors.primary;
    }
  };

  const getIntensityLabel = (intensity: string) => {
    const labels: Record<string, Record<string, string>> = {
      low: { 'pt-BR': 'Leve', 'en-US': 'Light', 'es-ES': 'Ligero' },
      moderate: { 'pt-BR': 'Moderada', 'en-US': 'Moderate', 'es-ES': 'Moderada' },
      high: { 'pt-BR': 'Intensa', 'en-US': 'Intense', 'es-ES': 'Intensa' },
    };
    return labels[intensity]?.[language] || intensity;
  };

  const getExerciseIcon = (id: string) => {
    if (id.includes('caminhada')) return 'walk';
    if (id.includes('bicicleta')) return 'bicycle';
    if (id.includes('escada')) return 'trending-up';
    return 'fitness';
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['bottom']}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>
          {language === 'en-US' ? 'Cardio Plan' : language === 'es-ES' ? 'Plan de Cardio' : 'Plano de Cardio'}
        </Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
      >
        {/* Resumo Semanal */}
        {cardioData && (
          <View style={[styles.summaryCard, { backgroundColor: colors.primary + '15', borderColor: colors.primary }]}>
            <Text style={[styles.summaryTitle, { color: colors.primary }]}>
              {language === 'en-US' ? 'Weekly Summary' : language === 'es-ES' ? 'Resumen Semanal' : 'Resumo Semanal'}
            </Text>
            <View style={styles.summaryRow}>
              <View style={styles.summaryItem}>
                <Ionicons name="calendar" size={24} color={colors.primary} />
                <Text style={[styles.summaryValue, { color: colors.text }]}>
                  {cardioData.weekly_summary.total_sessions}
                </Text>
                <Text style={[styles.summaryLabel, { color: colors.textSecondary }]}>
                  {language === 'en-US' ? 'sessions' : language === 'es-ES' ? 'sesiones' : 'sessões'}
                </Text>
              </View>
              <View style={styles.summaryItem}>
                <Ionicons name="time" size={24} color={colors.primary} />
                <Text style={[styles.summaryValue, { color: colors.text }]}>
                  {cardioData.weekly_summary.total_duration_minutes}
                </Text>
                <Text style={[styles.summaryLabel, { color: colors.textSecondary }]}>min</Text>
              </View>
              <View style={styles.summaryItem}>
                <Ionicons name="flame" size={24} color={colors.primary} />
                <Text style={[styles.summaryValue, { color: colors.text }]}>
                  {cardioData.weekly_summary.total_calories_burned}
                </Text>
                <Text style={[styles.summaryLabel, { color: colors.textSecondary }]}>kcal</Text>
              </View>
            </View>
          </View>
        )}

        {/* Dica */}
        <View style={[styles.tipCard, { backgroundColor: colors.info + '15' }]}>
          <Ionicons name="information-circle" size={20} color={colors.info} />
          <Text style={[styles.tipText, { color: colors.info }]}>
            {cardioData?.tips?.[language === 'en-US' ? 'en' : language === 'es-ES' ? 'es' : 'pt'] ||
              'Faça o cardio em qualquer horário do dia. O importante é a consistência!'}
          </Text>
        </View>

        {/* Lista de Exercícios */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          {language === 'en-US' ? 'Your Exercises' : language === 'es-ES' ? 'Tus Ejercicios' : 'Seus Exercícios'}
        </Text>

        {cardioData?.exercises?.map((exercise: CardioExercise, index: number) => (
          <TouchableOpacity
            key={exercise.id}
            style={[styles.exerciseCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}
            onPress={() => {
              setSelectedExercise(exercise);
              setShowDetails(true);
            }}
          >
            <View style={styles.exerciseHeader}>
              <View style={[styles.exerciseIcon, { backgroundColor: getIntensityColor(exercise.intensity) + '20' }]}>
                <Ionicons name={getExerciseIcon(exercise.id) as any} size={24} color={getIntensityColor(exercise.intensity)} />
              </View>
              <View style={styles.exerciseInfo}>
                <Text style={[styles.exerciseName, { color: colors.text }]}>
                  {getLocalizedText(exercise.name, exercise.name_en, exercise.name_es)}
                </Text>
                <View style={styles.exerciseMeta}>
                  <View style={[styles.intensityBadge, { backgroundColor: getIntensityColor(exercise.intensity) + '20' }]}>
                    <Text style={[styles.intensityText, { color: getIntensityColor(exercise.intensity) }]}>
                      {getIntensityLabel(exercise.intensity)}
                    </Text>
                  </View>
                  <Text style={[styles.exerciseDetail, { color: colors.textSecondary }]}>
                    {exercise.duration_minutes} min
                  </Text>
                  <Text style={[styles.exerciseDetail, { color: colors.textSecondary }]}>
                    {exercise.calories_burned} kcal
                  </Text>
                </View>
              </View>
              <View style={styles.sessionsBadge}>
                <Text style={[styles.sessionsNumber, { color: colors.primary }]}>
                  {exercise.sessions_per_week}x
                </Text>
                <Text style={[styles.sessionsLabel, { color: colors.textSecondary }]}>
                  /{language === 'en-US' ? 'wk' : 'sem'}
                </Text>
              </View>
            </View>
            
            <Text style={[styles.heartRateZone, { color: colors.textSecondary }]}>
              ❤️ {exercise.heart_rate_zone}
            </Text>
            
            {exercise.substitutes && exercise.substitutes.length > 0 && (
              <Text style={[styles.substitutesText, { color: colors.textTertiary }]}>
                {language === 'en-US' ? 'Substitutes: ' : language === 'es-ES' ? 'Sustitutos: ' : 'Substitutos: '}
                {exercise.substitutes.join(', ')}
              </Text>
            )}
          </TouchableOpacity>
        ))}

        <View style={{ height: 40 }} />
      </ScrollView>

      {/* Modal de Detalhes */}
      <Modal
        visible={showDetails}
        transparent
        animationType="slide"
        onRequestClose={() => setShowDetails(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.backgroundCard }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>
                {selectedExercise && getLocalizedText(
                  selectedExercise.name,
                  selectedExercise.name_en,
                  selectedExercise.name_es
                )}
              </Text>
              <TouchableOpacity onPress={() => setShowDetails(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalScroll}>
              {selectedExercise && (
                <>
                  {/* Descrição */}
                  <View style={styles.detailSection}>
                    <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>
                      {language === 'en-US' ? 'Description' : language === 'es-ES' ? 'Descripción' : 'Descrição'}
                    </Text>
                    <Text style={[styles.detailText, { color: colors.text }]}>
                      {getLocalizedText(
                        selectedExercise.description,
                        selectedExercise.description_en,
                        selectedExercise.description_es
                      )}
                    </Text>
                  </View>

                  {/* Zona de FC */}
                  <View style={styles.detailSection}>
                    <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>
                      {language === 'en-US' ? 'Heart Rate Zone' : language === 'es-ES' ? 'Zona de FC' : 'Zona de FC'}
                    </Text>
                    <Text style={[styles.detailText, { color: colors.text }]}>
                      ❤️ {selectedExercise.heart_rate_zone}
                    </Text>
                  </View>

                  {/* Como Saber se Está Funcionando */}
                  <View style={[styles.howToFeelSection, { backgroundColor: colors.success + '15' }]}>
                    <Text style={[styles.howToFeelTitle, { color: colors.success }]}>
                      {language === 'en-US' ? '🎯 How to Know It\'s Working' : 
                       language === 'es-ES' ? '🎯 Cómo Saber si Funciona' : 
                       '🎯 Como Saber se Está Funcionando'}
                    </Text>
                    <Text style={[styles.howToFeelText, { color: colors.text }]}>
                      {getLocalizedText(
                        selectedExercise.how_to_feel,
                        selectedExercise.how_to_feel_en,
                        selectedExercise.how_to_feel_es
                      )}
                    </Text>
                  </View>

                  {/* Estatísticas */}
                  <View style={styles.statsRow}>
                    <View style={[styles.statItem, { backgroundColor: colors.backgroundSecondary }]}>
                      <Ionicons name="time" size={20} color={colors.primary} />
                      <Text style={[styles.statValue, { color: colors.text }]}>
                        {selectedExercise.duration_minutes} min
                      </Text>
                    </View>
                    <View style={[styles.statItem, { backgroundColor: colors.backgroundSecondary }]}>
                      <Ionicons name="flame" size={20} color={colors.warning} />
                      <Text style={[styles.statValue, { color: colors.text }]}>
                        {selectedExercise.calories_burned} kcal
                      </Text>
                    </View>
                  </View>

                  {/* Substitutos com tempo equivalente */}
                  {selectedExercise.substitutes_detailed && selectedExercise.substitutes_detailed.length > 0 && (
                    <View style={styles.detailSection}>
                      <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>
                        {language === 'en-US' ? 'Can be substituted by:' : 
                         language === 'es-ES' ? 'Puede sustituirse por:' : 
                         'Pode ser substituído por:'}
                      </Text>
                      {selectedExercise.substitutes_detailed.map((sub, idx) => (
                        <View key={idx} style={[styles.substituteItemDetailed, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                          <View style={styles.substituteHeader}>
                            <Ionicons name="swap-horizontal" size={18} color={colors.primary} />
                            <Text style={[styles.substituteNameText, { color: colors.text }]}>
                              {getLocalizedText(sub.name, sub.name_en, sub.name_es)}
                            </Text>
                          </View>
                          <View style={styles.substituteTimeRow}>
                            <View style={[styles.timeBox, { backgroundColor: colors.warning + '20' }]}>
                              <Text style={[styles.timeBoxLabel, { color: colors.textSecondary }]}>
                                {language === 'en-US' ? 'Original' : 'Original'}
                              </Text>
                              <Text style={[styles.timeBoxValue, { color: colors.warning }]}>
                                {sub.original_duration} min
                              </Text>
                            </View>
                            <Ionicons name="arrow-forward" size={20} color={colors.textTertiary} />
                            <View style={[styles.timeBox, { backgroundColor: colors.success + '20' }]}>
                              <Text style={[styles.timeBoxLabel, { color: colors.textSecondary }]}>
                                {language === 'en-US' ? 'Equivalent' : language === 'es-ES' ? 'Equivalente' : 'Equivalente'}
                              </Text>
                              <Text style={[styles.timeBoxValue, { color: colors.success }]}>
                                {sub.equivalent_duration} min
                              </Text>
                            </View>
                          </View>
                          <Text style={[styles.substituteNote, { color: colors.textTertiary }]}>
                            {language === 'en-US' 
                              ? `Do ${sub.equivalent_duration} min to burn same calories`
                              : language === 'es-ES'
                              ? `Haz ${sub.equivalent_duration} min para quemar las mismas calorías`
                              : `Faça ${sub.equivalent_duration} min para queimar as mesmas calorias`}
                          </Text>
                        </View>
                      ))}
                    </View>
                  )}
                </>
              )}
            </ScrollView>

            <TouchableOpacity
              style={[styles.closeButton, { backgroundColor: colors.primary }]}
              onPress={() => setShowDetails(false)}
            >
              <Text style={styles.closeButtonText}>
                {language === 'en-US' ? 'Close' : language === 'es-ES' ? 'Cerrar' : 'Fechar'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  summaryCard: {
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 16,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 16,
    textAlign: 'center',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 24,
    fontWeight: '800',
    marginTop: 8,
  },
  summaryLabel: {
    fontSize: 12,
    marginTop: 2,
  },
  tipCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 14,
    borderRadius: 12,
    marginBottom: 20,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
  },
  exerciseCard: {
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 12,
  },
  exerciseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  exerciseIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  exerciseInfo: {
    flex: 1,
    marginLeft: 12,
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  exerciseMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  intensityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  intensityText: {
    fontSize: 11,
    fontWeight: '600',
  },
  exerciseDetail: {
    fontSize: 12,
  },
  sessionsBadge: {
    alignItems: 'center',
  },
  sessionsNumber: {
    fontSize: 20,
    fontWeight: '800',
  },
  sessionsLabel: {
    fontSize: 10,
  },
  heartRateZone: {
    fontSize: 13,
    marginTop: 10,
  },
  substitutesText: {
    fontSize: 12,
    marginTop: 6,
    fontStyle: 'italic',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
  },
  modalScroll: {
    maxHeight: 500,
  },
  detailSection: {
    marginBottom: 16,
  },
  detailLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  detailText: {
    fontSize: 15,
    lineHeight: 22,
  },
  howToFeelSection: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  howToFeelTitle: {
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 8,
  },
  howToFeelText: {
    fontSize: 14,
    lineHeight: 22,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  statItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    borderRadius: 10,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
  },
  substituteItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 8,
    borderBottomWidth: 1,
  },
  substituteText: {
    fontSize: 14,
  },
  substituteItemDetailed: {
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
  },
  substituteHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 12,
  },
  substituteNameText: {
    fontSize: 16,
    fontWeight: '600',
  },
  substituteTimeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 10,
  },
  timeBox: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    minWidth: 90,
  },
  timeBoxLabel: {
    fontSize: 10,
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  timeBoxValue: {
    fontSize: 18,
    fontWeight: '800',
  },
  substituteNote: {
    fontSize: 12,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  closeButton: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  closeButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
});
