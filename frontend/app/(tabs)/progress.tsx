import React, { useState, useCallback } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, RefreshControl, Modal, TextInput, Alert,
  Dimensions
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';
import Svg, { Path, Circle, Line, Text as SvgText } from 'react-native-svg';
import { Toast, ProgressSkeleton } from '../../components';
import { useToast } from '../../hooks/useToast';
import { useHaptics } from '../../hooks/useHaptics';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const SCREEN_WIDTH = Dimensions.get('window').width;

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

export default function ProgressScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);
  const { toast, showSuccess, showError, hideToast } = useToast();
  const { lightImpact, successFeedback, errorFeedback } = useHaptics();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [progressData, setProgressData] = useState<any>(null);
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [newWeight, setNewWeight] = useState('');
  const [saving, setSaving] = useState(false);

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
      const response = await safeFetch(`${BACKEND_URL}/api/progress/weight/${uid}?days=30`);
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

  const handleRecordWeight = async () => {
    if (!newWeight || !userId) return;
    
    const weight = parseFloat(newWeight.replace(',', '.'));
    if (isNaN(weight) || weight < 30 || weight > 300) {
      errorFeedback(); // Haptic de erro
      showError('Digite um peso entre 30kg e 300kg.');
      return;
    }
    
    setSaving(true);
    lightImpact(); // Haptic ao iniciar
    
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/progress/weight/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ weight }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setShowModal(false);
        setNewWeight('');
        successFeedback(); // Haptic de sucesso
        
        // Verifica se a dieta foi ajustada
        if (result.diet_adjusted) {
          // Mostra mensagem de ajuste de dieta (discreto)
          showInfo('Dieta ajustada com base no seu progresso');
        } else {
          showSuccess('Peso registrado com sucesso!');
        }
        
        await loadProgress(userId);
      } else {
        const error = await response.json().catch(() => ({}));
        errorFeedback(); // Haptic de erro
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
          <Text style={[styles.headerTitle, { color: colors.text }]}>Progresso</Text>
          <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
            Últimos 30 dias
          </Text>
        </View>

        {/* Current Weight Card */}
        <View style={[styles.weightCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.weightCardHeader}>
            <Ionicons name="scale-outline" size={24} color={colors.primary} />
            <Text style={[styles.weightCardTitle, { color: colors.textSecondary }]}>Peso Atual</Text>
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
                {stats.total_change > 0 ? '+' : ''}{stats.total_change.toFixed(1)} kg no período
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
          onPress={() => canRecord ? setShowModal(true) : null}
          disabled={!canRecord}
          activeOpacity={0.8}
        >
          <Ionicons name="add-circle-outline" size={20} color={canRecord ? '#fff' : colors.textTertiary} />
          <Text style={[styles.recordButtonText, { color: canRecord ? '#fff' : colors.textTertiary }]}>
            {canRecord ? 'Registrar Peso' : `Próximo registro em ${daysUntilNext} dias`}
          </Text>
        </TouchableOpacity>

        {/* Chart */}
        {history.length > 0 ? (
          <View style={[styles.chartCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Text style={[styles.chartTitle, { color: colors.text }]}>Evolução do Peso</Text>
            <WeightChart data={history} colors={colors} />
          </View>
        ) : (
          <View style={[styles.emptyChart, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Ionicons name="analytics-outline" size={48} color={colors.textTertiary} />
            <Text style={[styles.emptyChartText, { color: colors.textSecondary }]}>
              Nenhum registro de peso ainda
            </Text>
            <Text style={[styles.emptyChartSubtext, { color: colors.textTertiary }]}>
              Registre seu peso a cada 2 semanas para acompanhar sua evolução
            </Text>
          </View>
        )}

        {/* History List */}
        {history.length > 0 && (
          <View style={styles.historySection}>
            <Text style={[styles.historyTitle, { color: colors.text }]}>Histórico</Text>
            {history.slice().reverse().map((record: any, index: number) => (
              <View 
                key={record.id} 
                style={[styles.historyItem, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}
              >
                <View style={styles.historyItemLeft}>
                  <Text style={[styles.historyWeight, { color: colors.text }]}>
                    {record.weight.toFixed(1)} kg
                  </Text>
                  <Text style={[styles.historyDate, { color: colors.textSecondary }]}>
                    {formatDate(record.recorded_at)}
                  </Text>
                </View>
                {index < history.length - 1 && (
                  <View style={styles.historyItemRight}>
                    {(() => {
                      const prevRecord = history[history.length - 2 - index];
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
            Registre seu peso a cada 2 semanas para um acompanhamento preciso e evitar flutuações diárias.
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
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>Registrar Peso</Text>
              <TouchableOpacity onPress={() => setShowModal(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <Text style={[styles.modalLabel, { color: colors.textSecondary }]}>
              Seu peso atual (kg)
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
              style={[styles.saveButton, { backgroundColor: colors.primary }, saving && { opacity: 0.7 }]}
              onPress={handleRecordWeight}
              disabled={saving || !newWeight}
              activeOpacity={0.8}
            >
              {saving ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.saveButtonText}>Salvar</Text>
              )}
            </TouchableOpacity>
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

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  content: { padding: 16 },
  header: { marginBottom: 20 },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
  weightCard: { padding: 20, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  weightCardHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  weightCardTitle: { fontSize: 14, fontWeight: '500' },
  currentWeight: { fontSize: 48, fontWeight: '700' },
  weightUnit: { fontSize: 24, fontWeight: '400' },
  changeIndicator: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginTop: 12 },
  changeText: { fontSize: 13, fontWeight: '600' },
  recordButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 14, borderRadius: 12, marginBottom: 20 },
  recordButtonText: { fontSize: 16, fontWeight: '600' },
  chartCard: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 20 },
  chartTitle: { fontSize: 16, fontWeight: '600', marginBottom: 12 },
  emptyChart: { padding: 32, borderRadius: 16, borderWidth: 1, alignItems: 'center', marginBottom: 20 },
  emptyChartText: { fontSize: 16, fontWeight: '500', marginTop: 12 },
  emptyChartSubtext: { fontSize: 13, textAlign: 'center', marginTop: 8, lineHeight: 18 },
  historySection: { marginBottom: 20 },
  historyTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  historyItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 8 },
  historyItemLeft: {},
  historyWeight: { fontSize: 18, fontWeight: '600' },
  historyDate: { fontSize: 13, marginTop: 2 },
  historyItemRight: {},
  historyDiff: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  historyDiffText: { fontSize: 13, fontWeight: '600' },
  infoBox: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, padding: 16, borderRadius: 12 },
  infoBoxText: { flex: 1, fontSize: 13, lineHeight: 18 },
  // Modal styles
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  modalLabel: { fontSize: 14, marginBottom: 8 },
  inputContainer: { flexDirection: 'row', alignItems: 'center', borderRadius: 12, borderWidth: 1, paddingHorizontal: 16, height: 60, marginBottom: 24 },
  input: { flex: 1, fontSize: 24, fontWeight: '600' },
  inputUnit: { fontSize: 18 },
  saveButton: { paddingVertical: 16, borderRadius: 12, alignItems: 'center' },
  saveButtonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
