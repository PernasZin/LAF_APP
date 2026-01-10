import React, { useState, useCallback, useEffect } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, RefreshControl, Modal, TextInput
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { router } from 'expo-router';
import { useTheme } from '../theme/ThemeContext';
import Svg, { Circle, Path, Text as SvgText } from 'react-native-svg';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Opções rápidas de água (em ml)
const WATER_QUICK_OPTIONS = [
  { label: '200ml', value: 200, icon: '🥛' },
  { label: '300ml', value: 300, icon: '🥤' },
  { label: '500ml', value: 500, icon: '💧' },
  { label: '1L', value: 1000, icon: '🧴' },
];

// Opções rápidas de sódio (em mg) - baseado em alimentos comuns
const SODIUM_QUICK_OPTIONS = [
  { label: '100mg', value: 100, desc: 'Ovo' },
  { label: '200mg', value: 200, desc: 'Arroz temp.' },
  { label: '400mg', value: 400, desc: 'Frango temp.' },
  { label: '500mg', value: 500, desc: 'Refeição' },
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

export default function WaterSodiumTrackerScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [trackerData, setTrackerData] = useState<any>(null);
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState<'water' | 'sodium'>('water');
  const [customValue, setCustomValue] = useState('');
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
        await loadTracker(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTracker = async (uid: string) => {
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/tracker/water-sodium/${uid}`);
      if (response.ok) {
        const data = await response.json();
        setTrackerData(data);
      }
    } catch (error) {
      console.error('Erro ao carregar tracker:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleQuickAdd = async (type: 'water' | 'sodium', value: number) => {
    if (!userId) return;
    
    setSaving(true);
    try {
      const body = type === 'water' 
        ? { water_ml: value } 
        : { sodium_mg: value };
      
      const response = await safeFetch(`${BACKEND_URL}/api/tracker/water-sodium/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      
      if (response.ok) {
        await loadTracker(userId);
      }
    } catch (error) {
      console.error('Erro ao adicionar:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleCustomAdd = async () => {
    if (!userId || !customValue) return;
    
    const value = parseInt(customValue);
    if (isNaN(value) || value <= 0) return;
    
    setSaving(true);
    try {
      const body = modalType === 'water' 
        ? { water_ml: value } 
        : { sodium_mg: value };
      
      const response = await safeFetch(`${BACKEND_URL}/api/tracker/water-sodium/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      
      if (response.ok) {
        setShowModal(false);
        setCustomValue('');
        await loadTracker(userId);
      }
    } catch (error) {
      console.error('Erro ao adicionar:', error);
    } finally {
      setSaving(false);
    }
  };

  const openCustomModal = (type: 'water' | 'sodium') => {
    setModalType(type);
    setCustomValue('');
    setShowModal(true);
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  const { 
    water_ml = 0, 
    water_target_ml = 3000, 
    water_percent = 0,
    sodium_mg = 0, 
    sodium_target_mg = 2000, 
    sodium_percent = 0,
    warnings = []
  } = trackerData || {};

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
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
          <View style={styles.headerContent}>
            <Text style={[styles.headerTitle, { color: colors.text }]}>💧🧂 Tracker</Text>
            <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
              Controle de água e sódio
            </Text>
          </View>
        </View>

        {/* Warnings */}
        {warnings.length > 0 && (
          <View style={[styles.warningsCard, { backgroundColor: '#FEE2E2', borderColor: '#EF4444' }]}>
            {warnings.map((warning: any, index: number) => (
              <View key={index} style={styles.warningRow}>
                <Text style={styles.warningIcon}>{warning.icon || '⚠️'}</Text>
                <Text style={[styles.warningText, { color: '#B91C1C' }]}>
                  {warning.message || warning}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Progress Circles */}
        <View style={styles.progressRow}>
          {/* Water Progress */}
          <View style={[styles.progressCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <CircularProgress 
              percentage={water_percent} 
              color="#06B6D4" 
              size={120}
              strokeWidth={10}
            />
            <Text style={styles.progressEmoji}>💧</Text>
            <Text style={[styles.progressValue, { color: colors.text }]}>
              {(water_ml / 1000).toFixed(1)}L
            </Text>
            <Text style={[styles.progressTarget, { color: colors.textSecondary }]}>
              Meta: {(water_target_ml / 1000).toFixed(1)}L
            </Text>
            <Text style={[styles.progressPercent, { color: '#06B6D4' }]}>
              {water_percent}%
            </Text>
          </View>

          {/* Sodium Progress */}
          <View style={[styles.progressCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <CircularProgress 
              percentage={sodium_percent} 
              color="#F59E0B" 
              size={120}
              strokeWidth={10}
            />
            <Text style={styles.progressEmoji}>🧂</Text>
            <Text style={[styles.progressValue, { color: colors.text }]}>
              {sodium_mg}mg
            </Text>
            <Text style={[styles.progressTarget, { color: colors.textSecondary }]}>
              Meta: {sodium_target_mg}mg
            </Text>
            <Text style={[styles.progressPercent, { color: '#F59E0B' }]}>
              {sodium_percent}%
            </Text>
          </View>
        </View>

        {/* Safety Limits */}
        <View style={[styles.safetyCard, { backgroundColor: colors.primary + '10' }]}>
          <Ionicons name="shield-checkmark" size={20} color={colors.primary} />
          <Text style={[styles.safetyText, { color: colors.text }]}>
            Limites seguros: Água ≥ 2L/dia | Sódio ≥ 500mg/dia
          </Text>
        </View>

        {/* Quick Add - Water */}
        <View style={styles.quickAddSection}>
          <View style={styles.quickAddHeader}>
            <Text style={[styles.quickAddTitle, { color: colors.text }]}>💧 Adicionar Água</Text>
            <TouchableOpacity onPress={() => openCustomModal('water')}>
              <Text style={[styles.customLink, { color: colors.primary }]}>Personalizado</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.quickAddGrid}>
            {WATER_QUICK_OPTIONS.map((option) => (
              <TouchableOpacity
                key={option.value}
                style={[styles.quickAddButton, { backgroundColor: '#06B6D4' + '20', borderColor: '#06B6D4' }]}
                onPress={() => handleQuickAdd('water', option.value)}
                disabled={saving}
              >
                <Text style={styles.quickAddEmoji}>{option.icon}</Text>
                <Text style={[styles.quickAddLabel, { color: '#06B6D4' }]}>{option.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Quick Add - Sodium */}
        <View style={styles.quickAddSection}>
          <View style={styles.quickAddHeader}>
            <Text style={[styles.quickAddTitle, { color: colors.text }]}>🧂 Adicionar Sódio</Text>
            <TouchableOpacity onPress={() => openCustomModal('sodium')}>
              <Text style={[styles.customLink, { color: colors.primary }]}>Personalizado</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.quickAddGrid}>
            {SODIUM_QUICK_OPTIONS.map((option) => (
              <TouchableOpacity
                key={option.value}
                style={[styles.quickAddButton, { backgroundColor: '#F59E0B' + '20', borderColor: '#F59E0B' }]}
                onPress={() => handleQuickAdd('sodium', option.value)}
                disabled={saving}
              >
                <Text style={[styles.quickAddLabel, { color: '#F59E0B' }]}>{option.label}</Text>
                <Text style={[styles.quickAddDesc, { color: colors.textSecondary }]}>{option.desc}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Peak Week Protocol Info */}
        {is_peak_week && peakWeekData && (
          <TouchableOpacity 
            style={[styles.peakWeekCard, { backgroundColor: '#EF4444' + '15', borderColor: '#EF4444' }]}
            onPress={() => router.push('/peak-week')}
          >
            <View style={styles.peakWeekHeader}>
              <Text style={[styles.peakWeekTitle, { color: '#EF4444' }]}>
                🏆 Protocolo Peak Week - Dia {currentDay}
              </Text>
              <Ionicons name="chevron-forward" size={20} color="#EF4444" />
            </View>
            <Text style={[styles.peakWeekInfo, { color: colors.textSecondary }]}>
              Toque para ver o protocolo completo do dia
            </Text>
          </TouchableOpacity>
        )}

        {/* History Link */}
        <TouchableOpacity 
          style={[styles.historyButton, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}
          onPress={() => {/* TODO: Navegar para histórico */}}
        >
          <Ionicons name="time-outline" size={20} color={colors.textSecondary} />
          <Text style={[styles.historyButtonText, { color: colors.text }]}>Ver Histórico</Text>
          <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
        </TouchableOpacity>
      </ScrollView>

      {/* Custom Value Modal */}
      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.background }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>
                {modalType === 'water' ? '💧 Adicionar Água' : '🧂 Adicionar Sódio'}
              </Text>
              <TouchableOpacity onPress={() => setShowModal(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <View style={[styles.inputContainer, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
              <TextInput
                style={[styles.input, { color: colors.text }]}
                value={customValue}
                onChangeText={setCustomValue}
                placeholder="0"
                placeholderTextColor={colors.textTertiary}
                keyboardType="numeric"
                autoFocus
              />
              <Text style={[styles.inputUnit, { color: colors.textSecondary }]}>
                {modalType === 'water' ? 'ml' : 'mg'}
              </Text>
            </View>

            <TouchableOpacity
              style={[
                styles.saveButton, 
                { backgroundColor: modalType === 'water' ? '#06B6D4' : '#F59E0B' },
                (!customValue || saving) && { opacity: 0.5 }
              ]}
              onPress={handleCustomAdd}
              disabled={!customValue || saving}
            >
              {saving ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.saveButtonText}>Adicionar</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

// Circular Progress Component
function CircularProgress({ percentage, color, size, strokeWidth }: { 
  percentage: number; 
  color: string; 
  size: number;
  strokeWidth: number;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <Svg width={size} height={size} style={{ position: 'absolute', top: 16 }}>
      {/* Background Circle */}
      <Circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="#E5E7EB"
        strokeWidth={strokeWidth}
        fill="none"
      />
      {/* Progress Circle */}
      <Circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={color}
        strokeWidth={strokeWidth}
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
    </Svg>
  );
}

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  content: { padding: 16, paddingBottom: 32 },
  
  // Header
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backButton: { padding: 8, marginRight: 8 },
  headerContent: { flex: 1 },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 2, fontWeight: '600' },
  
  // Warnings
  warningsCard: { padding: 12, borderRadius: 12, borderWidth: 1, marginBottom: 16 },
  warningRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  warningIcon: { fontSize: 16, marginRight: 8 },
  warningText: { flex: 1, fontSize: 13, fontWeight: '500' },
  
  // Progress
  progressRow: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  progressCard: { 
    flex: 1, 
    padding: 16, 
    borderRadius: 16, 
    borderWidth: 1, 
    alignItems: 'center' 
  },
  progressEmoji: { fontSize: 28, marginTop: 130 },
  progressValue: { fontSize: 24, fontWeight: '700', marginTop: 8 },
  progressTarget: { fontSize: 12, marginTop: 2 },
  progressPercent: { fontSize: 14, fontWeight: '600', marginTop: 4 },
  
  // Safety
  safetyCard: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 8, 
    padding: 12, 
    borderRadius: 12, 
    marginBottom: 20 
  },
  safetyText: { flex: 1, fontSize: 12 },
  
  // Quick Add
  quickAddSection: { marginBottom: 20 },
  quickAddHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: 12 
  },
  quickAddTitle: { fontSize: 16, fontWeight: '600' },
  customLink: { fontSize: 14 },
  quickAddGrid: { flexDirection: 'row', gap: 8 },
  quickAddButton: { 
    flex: 1, 
    padding: 12, 
    borderRadius: 12, 
    borderWidth: 1, 
    alignItems: 'center' 
  },
  quickAddEmoji: { fontSize: 20, marginBottom: 4 },
  quickAddLabel: { fontSize: 14, fontWeight: '600' },
  quickAddDesc: { fontSize: 10, marginTop: 2 },
  
  // Peak Week Card
  peakWeekCard: { padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 16 },
  peakWeekHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  peakWeekTitle: { fontSize: 14, fontWeight: '700' },
  peakWeekInfo: { fontSize: 12, marginTop: 4 },
  
  // History Button
  historyButton: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 8, 
    padding: 16, 
    borderRadius: 12, 
    borderWidth: 1 
  },
  historyButtonText: { flex: 1, fontSize: 14, fontWeight: '500' },
  
  // Modal
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24 },
  modalHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: 24 
  },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  inputContainer: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    borderRadius: 12, 
    borderWidth: 1, 
    paddingHorizontal: 16, 
    height: 60, 
    marginBottom: 24 
  },
  input: { flex: 1, fontSize: 24, fontWeight: '600' },
  inputUnit: { fontSize: 18 },
  saveButton: { paddingVertical: 16, borderRadius: 12, alignItems: 'center' },
  saveButtonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
