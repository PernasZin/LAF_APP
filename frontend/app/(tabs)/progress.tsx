/**
 * LAF Premium Progress Screen
 * ============================
 * Corrigido: Endpoints corretos e peso inicial do perfil
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  RefreshControl, Modal, TextInput, KeyboardAvoidingView, Platform, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import Animated, { FadeInDown } from 'react-native-reanimated';
import {
  TrendingUp, TrendingDown, Scale, Calendar, Plus,
  X, Check, Target, Clock, Smile, Droplets, Moon, Dumbbell, Utensils
} from 'lucide-react-native';
import Slider from '@react-native-community/slider';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { ProgressSkeleton } from '../../components';
import { useTranslation } from '../../i18n';

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

const GlassCard = ({ children, style, isDark }: any) => {
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
  return <View style={[cardStyle, style]}>{children}</View>;
};

export default function ProgressScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const language = useSettingsStore((state) => state.language);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [progressData, setProgressData] = useState<any>(null);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [showWeightModal, setShowWeightModal] = useState(false);
  const [newWeight, setNewWeight] = useState('');
  const [saving, setSaving] = useState(false);

  // Questionário
  const [questionnaire, setQuestionnaire] = useState({
    diet: 5,
    training: 5,
    cardio: 5,
    sleep: 5,
    hydration: 5,
  });

  useFocusEffect(
    useCallback(() => {
      loadProgress();
    }, [])
  );

  const loadProgress = async () => {
    try {
      setLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        // Carregar perfil para pegar peso atual
        const profileRes = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          setUserProfile(profileData);
        }

        // Carregar histórico de peso - endpoint correto
        const weightRes = await safeFetch(`${BACKEND_URL}/api/progress/weight/${id}`);
        if (weightRes.ok) {
          const data = await weightRes.json();
          setProgressData(data);
        }
      }
    } catch (error) {
      console.error('Error loading progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadProgress();
    setRefreshing(false);
  };

  const handleSaveWeight = async () => {
    if (!newWeight || !userId) return;

    setSaving(true);
    try {
      // Endpoint correto com questionário
      const response = await safeFetch(`${BACKEND_URL}/api/progress/weight/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          weight: parseFloat(newWeight),
          questionnaire: questionnaire
        }),
      });

      if (response.ok) {
        setShowWeightModal(false);
        setNewWeight('');
        // Reset questionnaire
        setQuestionnaire({ diet: 5, training: 5, cardio: 5, sleep: 5, hydration: 5 });
        await loadProgress();
        Alert.alert(t.common.success, t.progress.weightSaved || 'Weight saved successfully!');
      } else {
        const data = await response.json();
        Alert.alert(t.common.warning || 'Warning', data.detail || t.common.error);
      }
    } catch (error) {
      Alert.alert(t.common.error, t.common.connectionError || 'Could not save weight');
    } finally {
      setSaving(false);
    }
  };

  // Peso atual vem do perfil do usuário
  const currentWeight = userProfile?.weight || progressData?.current_weight || 0;
  const targetWeight = userProfile?.target_weight || progressData?.target_weight;
  const history = progressData?.history || [];
  const canRecord = progressData?.can_record ?? true;
  const daysUntilNext = progressData?.days_until_next_record || 0;
  const stats = progressData?.stats || {};

  const weightChange = history.length >= 2 
    ? history[history.length - 1]?.weight - history[history.length - 2]?.weight 
    : 0;

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <ProgressSkeleton />
      </SafeAreaView>
    );
  }

  const QuestionnaireSlider = ({ label, icon: Icon, value, onChange, color }: any) => (
    <View style={styles.questionnaireRow}>
      <View style={styles.questionnaireHeader}>
        <Icon size={18} color={color} />
        <Text style={[styles.questionnaireLabel, { color: theme.text }]}>{label}</Text>
        <Text style={[styles.questionnaireValue, { color }]}>{value}</Text>
      </View>
      <Slider
        style={styles.slider}
        minimumValue={0}
        maximumValue={10}
        step={1}
        value={value}
        onValueChange={onChange}
        minimumTrackTintColor={color}
        maximumTrackTintColor={theme.border}
        thumbTintColor={color}
      />
    </View>
  );

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
              <Text style={[styles.headerTitle, { color: theme.text }]}>{t.progress.title}</Text>
              <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
                {t.progress.subtitle}
              </Text>
            </View>
          </Animated.View>

          {/* Current Weight Card */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <GlassCard isDark={isDark} style={styles.weightCard}>
              <LinearGradient
                colors={[premiumColors.gradient.start + '10', premiumColors.gradient.end + '10']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={StyleSheet.absoluteFill}
              />
              <View style={styles.weightHeader}>
                <View style={[styles.weightIconBg, { backgroundColor: premiumColors.primary + '20' }]}>
                  <Scale size={24} color={premiumColors.primary} strokeWidth={2.5} />
                </View>
                <Text style={[styles.weightLabel, { color: theme.textSecondary }]}>{t.progress.currentWeight}</Text>
              </View>
              <View style={styles.weightValueRow}>
                <Text style={[styles.weightValue, { color: theme.text }]}>
                  {currentWeight.toFixed(1)}
                </Text>
                <Text style={[styles.weightUnit, { color: theme.textTertiary }]}>kg</Text>
                {weightChange !== 0 && (
                  <View style={[styles.weightChangeBadge, { backgroundColor: weightChange < 0 ? '#10B98120' : '#EF444420' }]}>
                    {weightChange < 0 ? (
                      <TrendingDown size={16} color="#10B981" />
                    ) : (
                      <TrendingUp size={16} color="#EF4444" />
                    )}
                    <Text style={[styles.weightChangeText, { color: weightChange < 0 ? '#10B981' : '#EF4444' }]}>
                      {Math.abs(weightChange).toFixed(1)}kg
                    </Text>
                  </View>
                )}
              </View>

              {/* Target Weight */}
              {targetWeight && (
                <View style={[styles.targetRow, { borderTopColor: theme.border }]}>
                  <Target size={16} color={theme.textTertiary} />
                  <Text style={[styles.targetText, { color: theme.textSecondary }]}>
                    Meta: {targetWeight}kg
                  </Text>
                </View>
              )}

              {/* Add Weight Button */}
              {canRecord ? (
                <TouchableOpacity onPress={() => setShowWeightModal(true)}>
                  <LinearGradient
                    colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.addWeightButton}
                  >
                    <Plus size={20} color="#FFF" />
                    <Text style={styles.addWeightButtonText}>{t.progress.recordWeight}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              ) : (
                <View style={[styles.blockedBanner, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)' }]}>
                  <Clock size={18} color={theme.textTertiary} />
                  <Text style={[styles.blockedText, { color: theme.textSecondary }]}>
                    {t.progress.nextRecordIn} {daysUntilNext} {t.progress.days}
                  </Text>
                </View>
              )}
            </GlassCard>
          </Animated.View>

          {/* Stats Cards */}
          <Animated.View entering={FadeInDown.delay(200).springify()} style={styles.statsRow}>
            <GlassCard isDark={isDark} style={styles.statCard}>
              <Target size={20} color="#3B82F6" />
              <Text style={[styles.statValue, { color: theme.text }]}>
                {stats.total_change ? `${stats.total_change > 0 ? '+' : ''}${stats.total_change.toFixed(1)}` : '0'}kg
              </Text>
              <Text style={[styles.statLabel, { color: theme.textTertiary }]}>{t.progress.total}</Text>
            </GlassCard>
            <GlassCard isDark={isDark} style={styles.statCard}>
              <Calendar size={20} color="#F59E0B" />
              <Text style={[styles.statValue, { color: theme.text }]}>
                {stats.total_records || history.length || 0}
              </Text>
              <Text style={[styles.statLabel, { color: theme.textTertiary }]}>{t.progress.records}</Text>
            </GlassCard>
          </Animated.View>

          {/* History */}
          <Animated.View entering={FadeInDown.delay(300).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.progress.history}</Text>
            <GlassCard isDark={isDark} style={styles.historyCard}>
              {history.length === 0 ? (
                <View style={styles.emptyHistory}>
                  <Scale size={40} color={theme.textTertiary} />
                  <Text style={[styles.emptyText, { color: theme.textSecondary }]}>
                    {t.progress.noRecords}
                  </Text>
                  <Text style={[styles.emptySubtext, { color: theme.textTertiary }]}>
                    {t.progress.recordEvery2Weeks}
                  </Text>
                </View>
              ) : (
                history.slice(-10).reverse().map((record: any, index: number) => (
                  <View key={index} style={[styles.historyItem, { borderBottomColor: theme.border }]}>
                    <View style={styles.historyDate}>
                      <Calendar size={14} color={theme.textTertiary} />
                      <Text style={[styles.historyDateText, { color: theme.textSecondary }]}>
                        {new Date(record.recorded_at).toLocaleDateString(language || 'pt-BR')}
                      </Text>
                    </View>
                    <View style={styles.historyRight}>
                      {record.questionnaire_average && (
                        <View style={[styles.avgBadge, { backgroundColor: premiumColors.primary + '15' }]}>
                          <Smile size={12} color={premiumColors.primary} />
                          <Text style={[styles.avgText, { color: premiumColors.primary }]}>
                            {record.questionnaire_average.toFixed(1)}
                          </Text>
                        </View>
                      )}
                      <Text style={[styles.historyWeight, { color: theme.text }]}>
                        {record.weight?.toFixed(1)}kg
                      </Text>
                    </View>
                  </View>
                ))
              )}
            </GlassCard>
          </Animated.View>

          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>

      {/* Weight Modal with Questionnaire */}
      <Modal visible={showWeightModal} transparent animationType="slide">
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={[styles.modalOverlay, { backgroundColor: theme.overlay }]}
        >
          <View style={[styles.modalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: theme.text }]}>{t.progress.recordWeight}</Text>
              <TouchableOpacity onPress={() => setShowWeightModal(false)}>
                <X size={24} color={theme.text} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Weight Input */}
              <View style={styles.weightInputContainer}>
                <TextInput
                  style={[styles.weightInput, { color: theme.text, borderColor: theme.border }]}
                  value={newWeight}
                  onChangeText={setNewWeight}
                  keyboardType="decimal-pad"
                  placeholder="0.0"
                  placeholderTextColor={theme.textTertiary}
                />
                <Text style={[styles.weightInputUnit, { color: theme.textSecondary }]}>kg</Text>
              </View>

              {/* Questionnaire */}
              <Text style={[styles.questionnaireTitle, { color: theme.textSecondary }]}>
                {t.progress.howWasYourWeek || 'HOW WAS YOUR WEEK?'}
              </Text>

              <QuestionnaireSlider
                label={t.tabs.diet}
                icon={Utensils}
                value={questionnaire.diet}
                onChange={(v: number) => setQuestionnaire({...questionnaire, diet: v})}
                color="#10B981"
              />
              <QuestionnaireSlider
                label={t.workout.training}
                icon={Dumbbell}
                value={questionnaire.training}
                onChange={(v: number) => setQuestionnaire({...questionnaire, training: v})}
                color="#3B82F6"
              />
              <QuestionnaireSlider
                label={t.tabs.cardio}
                icon={TrendingUp}
                value={questionnaire.cardio}
                onChange={(v: number) => setQuestionnaire({...questionnaire, cardio: v})}
                color="#F59E0B"
              />
              <QuestionnaireSlider
                label={t.progress.sleep || 'Sleep'}
                icon={Moon}
                value={questionnaire.sleep}
                onChange={(v: number) => setQuestionnaire({...questionnaire, sleep: v})}
                color="#8B5CF6"
              />
              <QuestionnaireSlider
                label={t.home.waterTracker}
                icon={Droplets}
                value={questionnaire.hydration}
                onChange={(v: number) => setQuestionnaire({...questionnaire, hydration: v})}
                color="#06B6D4"
              />

              <TouchableOpacity
                onPress={handleSaveWeight}
                disabled={!newWeight || saving}
                style={{ marginTop: spacing.lg }}
              >
                <LinearGradient
                  colors={!newWeight ? ['#9CA3AF', '#6B7280'] : [premiumColors.gradient.start, premiumColors.gradient.end]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.saveButton}
                >
                  <Check size={20} color="#FFF" />
                  <Text style={styles.saveButtonText}>
                    {saving ? t.common.saving : t.common.save}
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg, gap: spacing.lg },

  header: { marginBottom: spacing.sm },
  headerTitle: { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  headerSubtitle: { fontSize: 14, marginTop: 4 },

  weightCard: { padding: spacing.lg },
  weightHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.md },
  weightIconBg: { width: 48, height: 48, borderRadius: radius.lg, alignItems: 'center', justifyContent: 'center' },
  weightLabel: { fontSize: 14, fontWeight: '600' },
  weightValueRow: { flexDirection: 'row', alignItems: 'baseline', gap: spacing.sm, marginBottom: spacing.md },
  weightValue: { fontSize: 56, fontWeight: '800', letterSpacing: -2 },
  weightUnit: { fontSize: 24, fontWeight: '600' },
  weightChangeBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: radius.full, marginLeft: spacing.sm },
  weightChangeText: { fontSize: 14, fontWeight: '700' },
  targetRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, paddingTop: spacing.md, marginBottom: spacing.md, borderTopWidth: 1 },
  targetText: { fontSize: 14, fontWeight: '600' },
  addWeightButton: { height: 52, borderRadius: radius.lg, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm },
  addWeightButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  blockedBanner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, padding: spacing.md, borderRadius: radius.lg },
  blockedText: { fontSize: 14, fontWeight: '600' },

  statsRow: { flexDirection: 'row', gap: spacing.md },
  statCard: { flex: 1, padding: spacing.base, alignItems: 'center', gap: spacing.xs },
  statValue: { fontSize: 24, fontWeight: '800' },
  statLabel: { fontSize: 12, fontWeight: '600' },

  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: spacing.sm },
  historyCard: { padding: spacing.base },
  emptyHistory: { alignItems: 'center', padding: spacing.xl, gap: spacing.sm },
  emptyText: { fontSize: 16, fontWeight: '600' },
  emptySubtext: { fontSize: 13 },
  historyItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: spacing.md, borderBottomWidth: 1 },
  historyDate: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  historyDateText: { fontSize: 14 },
  historyRight: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  avgBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: spacing.sm, paddingVertical: 2, borderRadius: radius.full },
  avgText: { fontSize: 12, fontWeight: '700' },
  historyWeight: { fontSize: 16, fontWeight: '700' },

  modalOverlay: { flex: 1, justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: radius['2xl'], borderTopRightRadius: radius['2xl'], padding: spacing.lg, maxHeight: '85%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  weightInputContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.md, marginBottom: spacing.xl },
  weightInput: { fontSize: 48, fontWeight: '800', textAlign: 'center', width: 150, borderBottomWidth: 2, paddingVertical: spacing.sm },
  weightInputUnit: { fontSize: 24, fontWeight: '600' },

  questionnaireTitle: { fontSize: 12, fontWeight: '700', letterSpacing: 1, marginBottom: spacing.md },
  questionnaireRow: { marginBottom: spacing.lg },
  questionnaireHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs },
  questionnaireLabel: { flex: 1, fontSize: 15, fontWeight: '600' },
  questionnaireValue: { fontSize: 18, fontWeight: '800' },
  slider: { width: '100%', height: 40 },

  saveButton: { height: 52, borderRadius: radius.lg, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm },
  saveButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
});
