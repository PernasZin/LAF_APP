import React, { useState, useCallback } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, RefreshControl, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { router } from 'expo-router';
import { useTheme } from '../theme/ThemeContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Safe fetch with timeout
const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);
  
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

export default function PeakWeekScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [peakWeekData, setPeakWeekData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  const loadData = async () => {
    try {
      setError(null);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
      
      if (id && BACKEND_URL) {
        const response = await safeFetch(`${BACKEND_URL}/api/peak-week/${id}`);
        
        if (response.ok) {
          const data = await response.json();
          setPeakWeekData(data);
        } else {
          const errorData = await response.json().catch(() => ({}));
          setError(errorData.detail || 'Erro ao carregar Peak Week');
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setError('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
            Carregando protocolo...
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.errorContainer}>
          <Ionicons name="warning-outline" size={64} color={colors.warning} />
          <Text style={[styles.errorTitle, { color: colors.text }]}>Peak Week</Text>
          <Text style={[styles.errorText, { color: colors.textSecondary }]}>{error}</Text>
          <TouchableOpacity 
            style={[styles.retryButton, { backgroundColor: colors.primary }]}
            onPress={() => router.back()}
          >
            <Text style={styles.retryButtonText}>Voltar</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const { 
    protocols, safety_warnings, disclaimer, current_day, days_to_competition, 
    current_weight, target_weight, has_weigh_in, weigh_in_info,
    blocked_foods, priority_foods, safety_limits
  } = peakWeekData || {};

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
            <Text style={[styles.headerTitle, { color: colors.text }]}>🏆 Peak Week</Text>
            <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
              {days_to_competition} dia(s) para a competição
            </Text>
          </View>
        </View>

        {/* Weigh-In Strategy Card (if applicable) */}
        {has_weigh_in && weigh_in_info && (
          <View style={[styles.weighInCard, { backgroundColor: '#FEF3C7', borderColor: '#D97706' }]}>
            <View style={styles.weighInHeader}>
              <Text style={styles.weighInEmoji}>⚖️</Text>
              <Text style={[styles.weighInTitle, { color: '#92400E' }]}>
                ESTRATÉGIA COM PESAGEM
              </Text>
            </View>
            <View style={styles.weighInBadge}>
              <Text style={styles.weighInBadgeText}>{weigh_in_info.strategy}</Text>
            </View>
            {weigh_in_info.notes?.map((note: string, index: number) => (
              <Text key={index} style={[styles.weighInNote, { color: '#78350F' }]}>
                {note}
              </Text>
            ))}
          </View>
        )}

        {/* Quick Access to Water/Sodium Tracker */}
        <TouchableOpacity 
          style={[styles.trackerButton, { backgroundColor: '#06B6D4' }]}
          onPress={() => router.push('/water-tracker')}
          activeOpacity={0.8}
        >
          <Ionicons name="water" size={20} color="#fff" />
          <Text style={styles.trackerButtonText}>💧🧂 Tracker de Água e Sódio</Text>
          <Ionicons name="chevron-forward" size={20} color="#fff" />
        </TouchableOpacity>

        {/* Current Day Highlight */}
        <View style={[styles.currentDayCard, { backgroundColor: colors.primary + '15', borderColor: colors.primary }]}>
          <View style={styles.currentDayHeader}>
            <Text style={[styles.currentDayLabel, { color: colors.primary }]}>HOJE - DIA {current_day}</Text>
            <View style={[styles.dayBadge, { backgroundColor: colors.primary }]}>
              <Text style={styles.dayBadgeText}>D-{days_to_competition}</Text>
            </View>
          </View>
          {protocols && protocols[0] && (
            <View style={styles.todayStats}>
              <View style={styles.todayStat}>
                <Text style={styles.todayStatEmoji}>💧</Text>
                <Text style={[styles.todayStatValue, { color: colors.text }]}>
                  {protocols[0].water_liters}L
                </Text>
                <Text style={[styles.todayStatLabel, { color: colors.textSecondary }]}>Água</Text>
              </View>
              <View style={styles.todayStat}>
                <Text style={styles.todayStatEmoji}>🧂</Text>
                <Text style={[styles.todayStatValue, { color: colors.text }]}>
                  {protocols[0].sodium_mg}mg
                </Text>
                <Text style={[styles.todayStatLabel, { color: colors.textSecondary }]}>Sódio</Text>
              </View>
              <View style={styles.todayStat}>
                <Text style={styles.todayStatEmoji}>🍚</Text>
                <Text style={[styles.todayStatValue, { color: colors.text }]}>
                  {protocols[0].carb_total_grams}g
                </Text>
                <Text style={[styles.todayStatLabel, { color: colors.textSecondary }]}>Carbs</Text>
              </View>
            </View>
          )}
          {/* Current Phase */}
          {protocols && protocols[0]?.phase_name && (
            <View style={[styles.phaseBadgeContainer, { backgroundColor: getPhaseColor(protocols[0].phase) + '20' }]}>
              <Text style={[styles.phaseBadgeText, { color: getPhaseColor(protocols[0].phase) }]}>
                {protocols[0].phase_name}
              </Text>
            </View>
          )}
        </View>

        {/* Weight Info */}
        <View style={[styles.weightCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.weightRow}>
            <View style={styles.weightItem}>
              <Text style={[styles.weightLabel, { color: colors.textSecondary }]}>Peso Atual</Text>
              <Text style={[styles.weightValue, { color: colors.text }]}>{current_weight?.toFixed(1)}kg</Text>
            </View>
            <Ionicons name="arrow-forward" size={20} color={colors.textTertiary} />
            <View style={styles.weightItem}>
              <Text style={[styles.weightLabel, { color: colors.textSecondary }]}>Meta</Text>
              <Text style={[styles.weightValue, { color: colors.primary }]}>{target_weight?.toFixed(1)}kg</Text>
            </View>
          </View>
        </View>

        {/* Safety Warnings */}
        <View style={[styles.warningsCard, { backgroundColor: '#FEF3C7', borderColor: '#F59E0B' }]}>
          <View style={styles.warningsHeader}>
            <Ionicons name="warning" size={24} color="#B45309" />
            <Text style={[styles.warningsTitle, { color: '#B45309' }]}>Avisos de Segurança</Text>
          </View>
          {safety_warnings?.map((warning: string, index: number) => (
            <Text key={index} style={[styles.warningText, { color: '#92400E' }]}>
              {warning}
            </Text>
          ))}
        </View>

        {/* Daily Protocols */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>📅 Protocolo Diário</Text>
        
        {protocols?.map((protocol: any, index: number) => (
          <View 
            key={index} 
            style={[
              styles.protocolCard, 
              { 
                backgroundColor: colors.backgroundCard, 
                borderColor: protocol.day === current_day ? colors.primary : colors.border,
                borderWidth: protocol.day === current_day ? 2 : 1
              }
            ]}
          >
            <View style={styles.protocolHeader}>
              <View style={styles.protocolDayInfo}>
                <Text style={[styles.protocolDay, { color: colors.text }]}>
                  Dia {protocol.day} - {protocol.day_name}
                </Text>
                <Text style={[styles.protocolDaysTo, { color: colors.textSecondary }]}>
                  {protocol.days_to_competition > 0 ? `D-${protocol.days_to_competition}` : '🏆 COMPETIÇÃO'}
                </Text>
              </View>
              {protocol.day === current_day && (
                <View style={[styles.todayTag, { backgroundColor: colors.primary }]}>
                  <Text style={styles.todayTagText}>HOJE</Text>
                </View>
              )}
            </View>

            {/* Water */}
            <View style={styles.protocolItem}>
              <View style={styles.protocolItemHeader}>
                <Text style={styles.protocolItemEmoji}>💧</Text>
                <Text style={[styles.protocolItemTitle, { color: colors.text }]}>Água</Text>
                <Text style={[styles.protocolItemValue, { color: colors.primary }]}>
                  {protocol.water_liters}L
                </Text>
              </View>
              <Text style={[styles.protocolItemNote, { color: colors.textSecondary }]}>
                {protocol.water_note}
              </Text>
            </View>

            {/* Sodium */}
            <View style={styles.protocolItem}>
              <View style={styles.protocolItemHeader}>
                <Text style={styles.protocolItemEmoji}>🧂</Text>
                <Text style={[styles.protocolItemTitle, { color: colors.text }]}>Sódio</Text>
                <Text style={[styles.protocolItemValue, { color: colors.warning }]}>
                  {protocol.sodium_mg}mg
                </Text>
              </View>
              <Text style={[styles.protocolItemNote, { color: colors.textSecondary }]}>
                {protocol.sodium_note}
              </Text>
            </View>

            {/* Carbs */}
            <View style={styles.protocolItem}>
              <View style={styles.protocolItemHeader}>
                <Text style={styles.protocolItemEmoji}>🍚</Text>
                <Text style={[styles.protocolItemTitle, { color: colors.text }]}>Carboidratos</Text>
                <View style={[styles.carbStrategyBadge, { backgroundColor: getCarbColor(protocol.carb_strategy) + '20' }]}>
                  <Text style={[styles.carbStrategyText, { color: getCarbColor(protocol.carb_strategy) }]}>
                    {protocol.carb_strategy === 'depletion' ? 'DEPLEÇÃO' : 
                     protocol.carb_strategy === 'loading' ? 'CARGA' : 'TRANSIÇÃO'}
                  </Text>
                </View>
              </View>
              <Text style={[styles.protocolItemValue, { color: colors.text, marginTop: 4 }]}>
                {protocol.carb_total_grams}g ({protocol.carb_grams_per_kg}g/kg)
              </Text>
              <Text style={[styles.protocolItemNote, { color: colors.textSecondary }]}>
                {protocol.carb_note}
              </Text>
            </View>

            {/* Training */}
            <View style={styles.protocolItem}>
              <View style={styles.protocolItemHeader}>
                <Text style={styles.protocolItemEmoji}>🏋️</Text>
                <Text style={[styles.protocolItemTitle, { color: colors.text }]}>Treino</Text>
                <Text style={[styles.protocolItemValue, { color: colors.textSecondary }]}>
                  {protocol.training_type === 'full_body' ? 'Full Body' :
                   protocol.training_type === 'light_pump' ? 'Pump Leve' :
                   protocol.training_type === 'posing' ? 'Poses' : 'Descanso'}
                </Text>
              </View>
              <Text style={[styles.protocolItemNote, { color: colors.textSecondary }]}>
                {protocol.training_note}
              </Text>
            </View>

            {/* General Notes */}
            <View style={[styles.generalNote, { backgroundColor: colors.primary + '10' }]}>
              <Text style={[styles.generalNoteText, { color: colors.text }]}>
                💡 {protocol.general_notes}
              </Text>
            </View>

            {/* Warning if any */}
            {protocol.warning && (
              <View style={[styles.protocolWarning, { backgroundColor: '#FEE2E2' }]}>
                <Text style={[styles.protocolWarningText, { color: '#B91C1C' }]}>
                  {protocol.warning}
                </Text>
              </View>
            )}
          </View>
        ))}

        {/* Disclaimer */}
        <View style={[styles.disclaimerCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Ionicons name="information-circle" size={20} color={colors.textSecondary} />
          <Text style={[styles.disclaimerText, { color: colors.textSecondary }]}>
            {disclaimer}
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function getCarbColor(strategy: string): string {
  switch (strategy) {
    case 'depletion': return '#EF4444';
    case 'loading': return '#10B981';
    case 'moderate': return '#F59E0B';
    default: return '#6B7280';
  }
}

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 12, fontSize: 14 },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  errorTitle: { fontSize: 24, fontWeight: '700', marginTop: 16 },
  errorText: { fontSize: 14, textAlign: 'center', marginTop: 8, lineHeight: 20 },
  retryButton: { paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8, marginTop: 24 },
  retryButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  
  content: { padding: 16, paddingBottom: 32 },
  
  // Header
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backButton: { padding: 8, marginRight: 8 },
  headerContent: { flex: 1 },
  headerTitle: { fontSize: 28, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 2 },
  
  // Tracker Button
  trackerButton: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center', 
    gap: 8, 
    paddingVertical: 14, 
    borderRadius: 12, 
    marginBottom: 16 
  },
  trackerButtonText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  
  // Current Day Card
  currentDayCard: { padding: 16, borderRadius: 16, borderWidth: 2, marginBottom: 16 },
  currentDayHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  currentDayLabel: { fontSize: 14, fontWeight: '700' },
  dayBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  dayBadgeText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  todayStats: { flexDirection: 'row', justifyContent: 'space-around' },
  todayStat: { alignItems: 'center' },
  todayStatEmoji: { fontSize: 24, marginBottom: 4 },
  todayStatValue: { fontSize: 20, fontWeight: '700' },
  todayStatLabel: { fontSize: 11, marginTop: 2 },
  
  // Weight Card
  weightCard: { padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 16 },
  weightRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  weightItem: { alignItems: 'center' },
  weightLabel: { fontSize: 12 },
  weightValue: { fontSize: 24, fontWeight: '700', marginTop: 4 },
  
  // Warnings Card
  warningsCard: { padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 20 },
  warningsHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
  warningsTitle: { fontSize: 16, fontWeight: '700' },
  warningText: { fontSize: 13, lineHeight: 20, marginBottom: 4 },
  
  // Section Title
  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: 12 },
  
  // Protocol Card
  protocolCard: { padding: 16, borderRadius: 12, marginBottom: 12 },
  protocolHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  protocolDayInfo: {},
  protocolDay: { fontSize: 16, fontWeight: '700' },
  protocolDaysTo: { fontSize: 12, marginTop: 2 },
  todayTag: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  todayTagText: { color: '#fff', fontSize: 10, fontWeight: '700' },
  
  // Protocol Item
  protocolItem: { marginBottom: 12 },
  protocolItemHeader: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  protocolItemEmoji: { fontSize: 16 },
  protocolItemTitle: { fontSize: 14, fontWeight: '600', flex: 1 },
  protocolItemValue: { fontSize: 14, fontWeight: '700' },
  protocolItemNote: { fontSize: 12, marginTop: 4, marginLeft: 24, lineHeight: 16 },
  
  // Carb Strategy Badge
  carbStrategyBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
  carbStrategyText: { fontSize: 10, fontWeight: '700' },
  
  // General Note
  generalNote: { padding: 12, borderRadius: 8, marginTop: 8 },
  generalNoteText: { fontSize: 13, lineHeight: 18 },
  
  // Protocol Warning
  protocolWarning: { padding: 12, borderRadius: 8, marginTop: 8 },
  protocolWarningText: { fontSize: 12, fontWeight: '600' },
  
  // Disclaimer
  disclaimerCard: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, padding: 16, borderRadius: 12, borderWidth: 1, marginTop: 8 },
  disclaimerText: { flex: 1, fontSize: 12, lineHeight: 18 },
});
