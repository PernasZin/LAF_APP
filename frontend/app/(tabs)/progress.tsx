import React, { useState, useCallback } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, RefreshControl, Modal, TextInput, Alert,
  Dimensions, Platform
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { router } from 'expo-router';
import { useTheme } from '../../theme/ThemeContext';
import Svg, { Path, Circle, Line, Text as SvgText, Rect } from 'react-native-svg';
import { Toast, ProgressSkeleton } from '../../components';
import { useToast } from '../../hooks/useToast';
import { useHaptics } from '../../hooks/useHaptics';
import { useTranslation } from '../../i18n';
import Slider from '@react-native-community/slider';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const SCREEN_WIDTH = Dimensions.get('window').width;

// Categorias do questionário
const QUESTIONNAIRE_CATEGORIES = [
  { key: 'diet', label: 'Dieta', icon: 'nutrition-outline', emoji: '🍽️' },
  { key: 'training', label: 'Treino', icon: 'barbell-outline', emoji: '🏋️' },
  { key: 'cardio', label: 'Cardio', icon: 'fitness-outline', emoji: '🏃' },
  { key: 'sleep', label: 'Sono', icon: 'moon-outline', emoji: '😴' },
  { key: 'hydration', label: 'Hidratação', icon: 'water-outline', emoji: '💧' },
];

// Safe fetch with timeout
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

export default function ProgressScreen() {
  const { colors } = useTheme();
  const { t } = useTranslation();
  const styles = createStyles(colors);
  const { toast, showSuccess, showError, showInfo, hideToast } = useToast();
  const { lightImpact, successFeedback, errorFeedback } = useHaptics();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [progressData, setProgressData] = useState<any>(null);
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalStep, setModalStep] = useState<'weight' | 'questionnaire'>('weight');
  const [newWeight, setNewWeight] = useState('');
  const [saving, setSaving] = useState(false);
  
  // Questionário state
  const [questionnaire, setQuestionnaire] = useState({
    diet: 5,
    training: 5,
    cardio: 5,
    sleep: 5,
    hydration: 5,
  });

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  const loadData = async () => {
    try {
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
      
      if (id && BACKEND_URL) {
        await loadProgress(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProgress = async (uid: string) => {
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/progress/weight/${uid}?days=365`);
      if (response.ok) {
        const data = await response.json();
        setProgressData(data);
      }
    } catch (error) {
      console.error('Erro ao carregar progresso:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleOpenModal = () => {
    setNewWeight('');
    setQuestionnaire({ diet: 5, training: 5, cardio: 5, sleep: 5, hydration: 5 });
    setModalStep('weight');
    setShowModal(true);
    lightImpact();
  };

  const handleWeightNext = () => {
    const weight = parseFloat(newWeight.replace(',', '.'));
    if (isNaN(weight) || weight < 30 || weight > 300) {
      errorFeedback();
      showError('Digite um peso entre 30kg e 300kg.');
      return;
    }
    lightImpact();
    setModalStep('questionnaire');
  };

  const handleRecordWeight = async () => {
    if (!newWeight || !userId) return;
    
    const weight = parseFloat(newWeight.replace(',', '.'));
    if (isNaN(weight) || weight < 30 || weight > 300) {
      errorFeedback();
      showError('Digite um peso entre 30kg e 300kg.');
      return;
    }
    
    setSaving(true);
    lightImpact();
    
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/progress/weight/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          weight,
          questionnaire: {
            diet: questionnaire.diet,
            training: questionnaire.training,
            cardio: questionnaire.cardio,
            sleep: questionnaire.sleep,
            hydration: questionnaire.hydration,
          }
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setShowModal(false);
        setNewWeight('');
        successFeedback();
        
        // Verifica se a dieta foi ajustada
        if (result.diet_adjusted) {
          showInfo(`Peso registrado! ${result.message || 'Dieta ajustada com base no seu progresso.'}`);
        } else {
          showSuccess('Peso e avaliação registrados com sucesso!');
        }
        
        await loadProgress(userId);
      } else {
        const error = await response.json().catch(() => ({}));
        errorFeedback();
        showError(error.detail || 'Não foi possível registrar o peso.');
      }
    } catch (error) {
      console.error('Erro ao registrar peso:', error);
      errorFeedback();
      showError('Erro de conexão ao registrar peso.');
    } finally {
      setSaving(false);
    }
  };

  const updateQuestionnaireValue = (key: string, value: number) => {
    setQuestionnaire(prev => ({ ...prev, [key]: Math.round(value) }));
    lightImpact();
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return colors.success;
    if (score >= 5) return colors.warning;
    return colors.error;
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <ProgressSkeleton />
      </SafeAreaView>
    );
  }

  const currentWeight = progressData?.current_weight || 0;
  const history = progressData?.history || [];
  const canRecord = progressData?.can_record ?? true;
  const daysUntilNext = progressData?.days_until_next_record || 0;
  const stats = progressData?.stats || {};
  const isAthlete = progressData?.is_athlete || false;
  const athletePhase = progressData?.athlete_phase;
  const blockPeriod = progressData?.block_period_days || 14;
  const questionnaireAverages = stats.questionnaire_averages;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>{t.progress.title}</Text>
          <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
            {isAthlete ? `🏆 Modo Atleta - Registro semanal` : 'Acompanhe sua evolução'}
          </Text>
        </View>

        {/* Athlete Phase Badge */}
        {isAthlete && athletePhase && (
          <View style={[styles.athletePhaseBadge, { backgroundColor: getPhaseColor(athletePhase) + '20' }]}>
            <Ionicons name="trophy" size={16} color={getPhaseColor(athletePhase)} />
            <Text style={[styles.athletePhaseText, { color: getPhaseColor(athletePhase) }]}>
              {formatPhaseName(athletePhase)}
            </Text>
          </View>
        )}

        {/* Current Weight Card */}
        <View style={[styles.weightCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.weightCardHeader}>
            <Ionicons name="scale-outline" size={24} color={colors.primary} />
            <Text style={[styles.weightCardTitle, { color: colors.textSecondary }]}>{t.progress.currentWeight}</Text>
          </View>
          <Text style={[styles.currentWeight, { color: colors.text }]}>
            {currentWeight.toFixed(1)} <Text style={styles.weightUnit}>kg</Text>
          </Text>
          
          {stats.total_change !== undefined && stats.total_change !== 0 && (
            <View style={[
              styles.changeIndicator, 
              { backgroundColor: stats.total_change < 0 ? colors.success + '20' : colors.warning + '20' }
            ]}>
              <Ionicons 
                name={stats.total_change < 0 ? 'trending-down' : 'trending-up'} 
                size={16} 
                color={stats.total_change < 0 ? colors.success : colors.warning} 
              />
              <Text style={[
                styles.changeText, 
                { color: stats.total_change < 0 ? colors.success : colors.warning }
              ]}>
                {stats.total_change > 0 ? '+' : ''}{stats.total_change.toFixed(1)} kg
              </Text>
            </View>
          )}

          {/* Progress to Goal */}
          {stats.progress_percent > 0 && (
            <View style={styles.progressToGoal}>
              <Text style={[styles.progressLabel, { color: colors.textSecondary }]}>
                Progresso para o objetivo
              </Text>
              <View style={[styles.progressBar, { backgroundColor: colors.border }]}>
                <View 
                  style={[
                    styles.progressFill, 
                    { backgroundColor: colors.primary, width: `${Math.min(100, stats.progress_percent)}%` }
                  ]} 
                />
              </View>
              <Text style={[styles.progressPercent, { color: colors.primary }]}>
                {stats.progress_percent.toFixed(0)}%
              </Text>
            </View>
          )}
        </View>

        {/* Record Button */}
        <TouchableOpacity
          style={[
            styles.recordButton,
            { backgroundColor: canRecord ? colors.primary : colors.border }
          ]}
          onPress={canRecord ? handleOpenModal : undefined}
          disabled={!canRecord}
          activeOpacity={0.8}
        >
          <Ionicons name="add-circle-outline" size={20} color={canRecord ? '#fff' : colors.textTertiary} />
          <Text style={[styles.recordButtonText, { color: canRecord ? '#fff' : colors.textTertiary }]}>
            {canRecord 
              ? '📝 Registrar Peso e Avaliação' 
              : `Próximo registro em ${daysUntilNext} dia${daysUntilNext !== 1 ? 's' : ''}`}
          </Text>
        </TouchableOpacity>

        {/* Questionnaire Averages Card */}
        {questionnaireAverages && (
          <View style={[styles.questionnaireCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Text style={[styles.chartTitle, { color: colors.text }]}>📊 Média das Avaliações</Text>
            <View style={styles.questionnaireGrid}>
              {QUESTIONNAIRE_CATEGORIES.map(cat => (
                <View key={cat.key} style={styles.questionnaireItem}>
                  <Text style={styles.questionnaireEmoji}>{cat.emoji}</Text>
                  <Text style={[styles.questionnaireItemLabel, { color: colors.textSecondary }]}>
                    {cat.label}
                  </Text>
                  <Text style={[
                    styles.questionnaireItemValue, 
                    { color: getScoreColor(questionnaireAverages[cat.key]) }
                  ]}>
                    {questionnaireAverages[cat.key].toFixed(1)}
                  </Text>
                </View>
              ))}
              <View style={styles.questionnaireItem}>
                <Text style={styles.questionnaireEmoji}>⭐</Text>
                <Text style={[styles.questionnaireItemLabel, { color: colors.textSecondary }]}>
                  Geral
                </Text>
                <Text style={[
                  styles.questionnaireItemValue, 
                  { color: getScoreColor(questionnaireAverages.overall) }
                ]}>
                  {questionnaireAverages.overall.toFixed(1)}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Chart */}
        {history.length > 0 ? (
          <View style={[styles.chartCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Text style={[styles.chartTitle, { color: colors.text }]}>{t.progress.evolution}</Text>
            <WeightChart data={history} colors={colors} />
          </View>
        ) : (
          <View style={[styles.emptyChart, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Ionicons name="analytics-outline" size={48} color={colors.textTertiary} />
            <Text style={[styles.emptyChartText, { color: colors.textSecondary }]}>
              {t.progress.noRecords}
            </Text>
            <Text style={[styles.emptyChartSubtext, { color: colors.textTertiary }]}>
              Registre seu peso para ver a evolução
            </Text>
          </View>
        )}

        {/* History List */}
        {history.length > 0 && (
          <View style={styles.historySection}>
            <Text style={[styles.historyTitle, { color: colors.text }]}>{t.progress.weightHistory}</Text>
            {history.slice().reverse().slice(0, 10).map((record: any, index: number) => (
              <View 
                key={record.id} 
                style={[styles.historyItem, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}
              >
                <View style={styles.historyItemLeft}>
                  <View style={styles.historyWeightRow}>
                    <Text style={[styles.historyWeight, { color: colors.text }]}>
                      {record.weight.toFixed(1)} kg
                    </Text>
                    {record.questionnaire_average && (
                      <View style={[styles.historyScoreBadge, { backgroundColor: getScoreColor(record.questionnaire_average) + '20' }]}>
                        <Text style={[styles.historyScoreText, { color: getScoreColor(record.questionnaire_average) }]}>
                          ⭐ {record.questionnaire_average.toFixed(1)}
                        </Text>
                      </View>
                    )}
                  </View>
                  <Text style={[styles.historyDate, { color: colors.textSecondary }]}>
                    {formatDate(record.recorded_at)}
                    {record.athlete_phase && ` • ${formatPhaseName(record.athlete_phase)}`}
                  </Text>
                </View>
                {index < history.length - 1 && (
                  <View style={styles.historyItemRight}>
                    {(() => {
                      const prevIndex = history.length - 2 - index;
                      if (prevIndex < 0) return null;
                      const prevRecord = history[prevIndex];
                      if (!prevRecord) return null;
                      const diff = record.weight - prevRecord.weight;
                      return (
                        <View style={[
                          styles.historyDiff,
                          { backgroundColor: diff <= 0 ? colors.success + '20' : colors.warning + '20' }
                        ]}>
                          <Text style={[
                            styles.historyDiffText,
                            { color: diff <= 0 ? colors.success : colors.warning }
                          ]}>
                            {diff > 0 ? '+' : ''}{diff.toFixed(1)}
                          </Text>
                        </View>
                      );
                    })()}
                  </View>
                )}
              </View>
            ))}
          </View>
        )}

        {/* Info Box */}
        <View style={[styles.infoBox, { backgroundColor: colors.primary + '10' }]}>
          <Ionicons name="information-circle-outline" size={20} color={colors.primary} />
          <Text style={[styles.infoBoxText, { color: colors.text }]}>
            {isAthlete 
              ? `🏆 Modo Atleta: Registre seu peso semanalmente para acompanhar a preparação com máxima precisão.`
              : `Registre seu peso semanalmente para acompanhar seu progresso. O questionário ajuda a identificar o que pode ser melhorado.`}
          </Text>
        </View>
      </ScrollView>

      {/* Record Weight Modal */}
      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.background }]}>
            {modalStep === 'weight' ? (
              <>
                {/* Step 1: Weight */}
                <View style={styles.modalHeader}>
                  <Text style={[styles.modalTitle, { color: colors.text }]}>📝 Registrar Peso</Text>
                  <TouchableOpacity onPress={() => setShowModal(false)}>
                    <Ionicons name="close" size={24} color={colors.textSecondary} />
                  </TouchableOpacity>
                </View>

                <Text style={[styles.modalLabel, { color: colors.textSecondary }]}>
                  Qual seu peso atual?
                </Text>
                
                <View style={[styles.inputContainer, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                  <TextInput
                    style={[styles.input, { color: colors.text }]}
                    value={newWeight}
                    onChangeText={setNewWeight}
                    placeholder={currentWeight.toFixed(1)}
                    placeholderTextColor={colors.textTertiary}
                    keyboardType="decimal-pad"
                    autoFocus
                  />
                  <Text style={[styles.inputUnit, { color: colors.textSecondary }]}>kg</Text>
                </View>

                <TouchableOpacity
                  style={[styles.saveButton, { backgroundColor: colors.primary }, !newWeight && { opacity: 0.5 }]}
                  onPress={handleWeightNext}
                  disabled={!newWeight}
                  activeOpacity={0.8}
                >
                  <Text style={styles.saveButtonText}>Próximo →</Text>
                </TouchableOpacity>
              </>
            ) : (
              <>
                {/* Step 2: Questionnaire */}
                <View style={styles.modalHeader}>
                  <TouchableOpacity onPress={() => setModalStep('weight')}>
                    <Ionicons name="arrow-back" size={24} color={colors.textSecondary} />
                  </TouchableOpacity>
                  <Text style={[styles.modalTitle, { color: colors.text }]}>📊 Avaliação Semanal</Text>
                  <TouchableOpacity onPress={() => setShowModal(false)}>
                    <Ionicons name="close" size={24} color={colors.textSecondary} />
                  </TouchableOpacity>
                </View>

                <Text style={[styles.modalSubtitle, { color: colors.textSecondary }]}>
                  Avalie de 0 a 10 como foi sua semana:
                </Text>

                <ScrollView style={styles.questionnaireScroll} showsVerticalScrollIndicator={false}>
                  {QUESTIONNAIRE_CATEGORIES.map(cat => (
                    <View key={cat.key} style={styles.sliderContainer}>
                      <View style={styles.sliderHeader}>
                        <Text style={styles.sliderEmoji}>{cat.emoji}</Text>
                        <Text style={[styles.sliderLabel, { color: colors.text }]}>{cat.label}</Text>
                        <Text style={[
                          styles.sliderValue, 
                          { color: getScoreColor(questionnaire[cat.key as keyof typeof questionnaire]) }
                        ]}>
                          {questionnaire[cat.key as keyof typeof questionnaire]}
                        </Text>
                      </View>
                      <Slider
                        style={styles.slider}
                        minimumValue={0}
                        maximumValue={10}
                        step={1}
                        value={questionnaire[cat.key as keyof typeof questionnaire]}
                        onValueChange={(value) => updateQuestionnaireValue(cat.key, value)}
                        minimumTrackTintColor={colors.primary}
                        maximumTrackTintColor={colors.border}
                        thumbTintColor={colors.primary}
                      />
                      <View style={styles.sliderLabels}>
                        <Text style={[styles.sliderMinMax, { color: colors.textTertiary }]}>Péssimo</Text>
                        <Text style={[styles.sliderMinMax, { color: colors.textTertiary }]}>Excelente</Text>
                      </View>
                    </View>
                  ))}
                </ScrollView>

                {/* Summary */}
                <View style={[styles.summaryBox, { backgroundColor: colors.backgroundCard }]}>
                  <Text style={[styles.summaryText, { color: colors.textSecondary }]}>
                    Peso: <Text style={{ color: colors.text, fontWeight: '700' }}>{newWeight} kg</Text>
                  </Text>
                  <Text style={[styles.summaryText, { color: colors.textSecondary }]}>
                    Média: <Text style={[{ fontWeight: '700' }, { color: getScoreColor(
                      (questionnaire.diet + questionnaire.training + questionnaire.cardio + questionnaire.sleep + questionnaire.hydration) / 5
                    ) }]}>
                      {((questionnaire.diet + questionnaire.training + questionnaire.cardio + questionnaire.sleep + questionnaire.hydration) / 5).toFixed(1)}
                    </Text>
                  </Text>
                </View>

                <TouchableOpacity
                  style={[styles.saveButton, { backgroundColor: colors.primary }, saving && { opacity: 0.7 }]}
                  onPress={handleRecordWeight}
                  disabled={saving}
                  activeOpacity={0.8}
                >
                  {saving ? (
                    <ActivityIndicator size="small" color="#fff" />
                  ) : (
                    <Text style={styles.saveButtonText}>✓ Salvar Registro</Text>
                  )}
                </TouchableOpacity>
              </>
            )}
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

// Simple Weight Chart Component
function WeightChart({ data, colors }: { data: any[], colors: any }) {
  if (data.length < 2) {
    return (
      <View style={{ height: 150, justifyContent: 'center', alignItems: 'center' }}>
        <Text style={{ color: colors.textSecondary }}>Mínimo 2 registros para o gráfico</Text>
      </View>
    );
  }

  const chartWidth = SCREEN_WIDTH - 64;
  const chartHeight = 150;
  const padding = { top: 20, bottom: 30, left: 40, right: 20 };
  const graphWidth = chartWidth - padding.left - padding.right;
  const graphHeight = chartHeight - padding.top - padding.bottom;

  const weights = data.map(d => d.weight);
  const minWeight = Math.min(...weights) - 1;
  const maxWeight = Math.max(...weights) + 1;
  const weightRange = maxWeight - minWeight;

  const getX = (index: number) => padding.left + (index / (data.length - 1)) * graphWidth;
  const getY = (weight: number) => padding.top + ((maxWeight - weight) / weightRange) * graphHeight;

  // Create path
  let pathD = `M ${getX(0)} ${getY(data[0].weight)}`;
  for (let i = 1; i < data.length; i++) {
    pathD += ` L ${getX(i)} ${getY(data[i].weight)}`;
  }

  return (
    <Svg width={chartWidth} height={chartHeight}>
      {/* Grid lines */}
      {[0, 0.5, 1].map((ratio, i) => {
        const y = padding.top + ratio * graphHeight;
        const weight = maxWeight - ratio * weightRange;
        return (
          <React.Fragment key={i}>
            <Line
              x1={padding.left}
              y1={y}
              x2={chartWidth - padding.right}
              y2={y}
              stroke={colors.border}
              strokeWidth={1}
              strokeDasharray="4,4"
            />
            <SvgText
              x={padding.left - 5}
              y={y + 4}
              fill={colors.textTertiary}
              fontSize={10}
              textAnchor="end"
            >
              {weight.toFixed(0)}
            </SvgText>
          </React.Fragment>
        );
      })}

      {/* Line */}
      <Path
        d={pathD}
        stroke={colors.primary}
        strokeWidth={2}
        fill="none"
      />

      {/* Points */}
      {data.map((d, i) => (
        <Circle
          key={i}
          cx={getX(i)}
          cy={getY(d.weight)}
          r={4}
          fill={colors.primary}
        />
      ))}

      {/* Date labels */}
      {data.length <= 5 ? (
        data.map((d, i) => (
          <SvgText
            key={i}
            x={getX(i)}
            y={chartHeight - 5}
            fill={colors.textTertiary}
            fontSize={9}
            textAnchor="middle"
          >
            {formatShortDate(d.recorded_at)}
          </SvgText>
        ))
      ) : (
        [0, data.length - 1].map((i) => (
          <SvgText
            key={i}
            x={getX(i)}
            y={chartHeight - 5}
            fill={colors.textTertiary}
            fontSize={9}
            textAnchor="middle"
          >
            {formatShortDate(data[i].recorded_at)}
          </SvgText>
        ))
      )}
    </Svg>
  );
}

// Helper functions
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatShortDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
}

function getPhaseColor(phase: string): string {
  const colors: { [key: string]: string } = {
    off_season: '#10B981',
    pre_contest: '#3B82F6',
    peak_week: '#EF4444',
    post_show: '#8B5CF6',
  };
  return colors[phase] || '#6B7280';
}

function formatPhaseName(phase: string): string {
  const names: { [key: string]: string } = {
    off_season: 'OFF-SEASON',
    pre_contest: 'PREP',
    peak_week: 'PEAK WEEK',
    post_show: 'PÓS-SHOW',
  };
  return names[phase] || phase.toUpperCase();
}

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  content: { padding: 16, paddingBottom: 32 },
  header: { marginBottom: 16 },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
  
  // Athlete Phase Badge
  athletePhaseBadge: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    alignSelf: 'flex-start',
    gap: 6, 
    paddingHorizontal: 12, 
    paddingVertical: 6, 
    borderRadius: 20, 
    marginBottom: 16 
  },
  athletePhaseText: { fontSize: 12, fontWeight: '700' },
  
  // Weight Card
  weightCard: { padding: 20, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  weightCardHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  weightCardTitle: { fontSize: 14, fontWeight: '500' },
  currentWeight: { fontSize: 48, fontWeight: '700' },
  weightUnit: { fontSize: 24, fontWeight: '400' },
  changeIndicator: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginTop: 12 },
  changeText: { fontSize: 13, fontWeight: '600' },
  
  // Progress to Goal
  progressToGoal: { marginTop: 16 },
  progressLabel: { fontSize: 12, marginBottom: 6 },
  progressBar: { height: 8, borderRadius: 4, overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 4 },
  progressPercent: { fontSize: 12, fontWeight: '600', marginTop: 4, textAlign: 'right' },
  
  // Record Button
  recordButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 14, borderRadius: 12, marginBottom: 20 },
  recordButtonText: { fontSize: 16, fontWeight: '600' },
  
  // Questionnaire Card
  questionnaireCard: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 20 },
  questionnaireGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginTop: 12 },
  questionnaireItem: { width: '30%', alignItems: 'center', padding: 12, borderRadius: 12, backgroundColor: 'rgba(0,0,0,0.03)' },
  questionnaireEmoji: { fontSize: 24, marginBottom: 4 },
  questionnaireItemLabel: { fontSize: 11, marginBottom: 2 },
  questionnaireItemValue: { fontSize: 18, fontWeight: '700' },
  
  // Chart
  chartCard: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 20 },
  chartTitle: { fontSize: 16, fontWeight: '600', marginBottom: 12 },
  emptyChart: { padding: 32, borderRadius: 16, borderWidth: 1, alignItems: 'center', marginBottom: 20 },
  emptyChartText: { fontSize: 16, fontWeight: '500', marginTop: 12 },
  emptyChartSubtext: { fontSize: 13, textAlign: 'center', marginTop: 8, lineHeight: 18 },
  
  // History
  historySection: { marginBottom: 20 },
  historyTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  historyItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 8 },
  historyItemLeft: { flex: 1 },
  historyWeightRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  historyWeight: { fontSize: 18, fontWeight: '600' },
  historyScoreBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10 },
  historyScoreText: { fontSize: 11, fontWeight: '600' },
  historyDate: { fontSize: 13, marginTop: 2 },
  historyItemRight: {},
  historyDiff: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  historyDiffText: { fontSize: 13, fontWeight: '600' },
  
  // Info Box
  infoBox: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, padding: 16, borderRadius: 12 },
  infoBoxText: { flex: 1, fontSize: 13, lineHeight: 18 },
  
  // Modal styles
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, maxHeight: '85%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  modalSubtitle: { fontSize: 14, marginBottom: 16 },
  modalLabel: { fontSize: 14, marginBottom: 8 },
  inputContainer: { flexDirection: 'row', alignItems: 'center', borderRadius: 12, borderWidth: 1, paddingHorizontal: 16, height: 60, marginBottom: 24 },
  input: { flex: 1, fontSize: 24, fontWeight: '600' },
  inputUnit: { fontSize: 18 },
  saveButton: { paddingVertical: 16, borderRadius: 12, alignItems: 'center' },
  saveButtonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  
  // Questionnaire Modal
  questionnaireScroll: { maxHeight: 350 },
  sliderContainer: { marginBottom: 20 },
  sliderHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  sliderEmoji: { fontSize: 24, marginRight: 8 },
  sliderLabel: { flex: 1, fontSize: 16, fontWeight: '600' },
  sliderValue: { fontSize: 24, fontWeight: '700', minWidth: 40, textAlign: 'right' },
  slider: { width: '100%', height: 40 },
  sliderLabels: { flexDirection: 'row', justifyContent: 'space-between', marginTop: -8 },
  sliderMinMax: { fontSize: 11 },
  
  // Summary Box
  summaryBox: { flexDirection: 'row', justifyContent: 'space-around', padding: 12, borderRadius: 12, marginBottom: 16 },
  summaryText: { fontSize: 14 },
});
