/**
 * LAF Premium Progress Screen
 * ============================
 * Sistema de check-in quinzenal com questionário e ajuste de dieta
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
  X, Check, Target, Clock, Smile, Droplets, Moon, Dumbbell, Utensils,
  AlertCircle, ThumbsUp, ThumbsDown, ChevronRight, Frown, Meh
} from 'lucide-react-native';
import Slider from '@react-native-community/slider';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { ProgressSkeleton } from '../../components';
import { useTranslation } from '../../i18n';

import { config } from '../../config';
const BACKEND_URL = config.BACKEND_URL;

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
  const language = useSettingsStore((state) => state.language) || 'pt-BR';
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();
  // Use t.progress para todas as traduções
  const p = t.progress;

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [progressData, setProgressData] = useState<any>(null);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [showWeightModal, setShowWeightModal] = useState(false);
  const [newWeight, setNewWeight] = useState('');
  const [saving, setSaving] = useState(false);
  const [step, setStep] = useState(1); // 1 = peso, 2 = mini avaliação

  // Questionário simplificado
  const [questionnaire, setQuestionnaire] = useState({
    followedDiet: 'yes' as 'yes' | 'mostly' | 'no',
    followedTraining: 'yes' as 'yes' | 'mostly' | 'no',
    feeling: 7, // 1-10 como está se sentindo
    observations: '',
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
        const profileRes = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          setUserProfile(profileData);
        }

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
      const response = await safeFetch(`${BACKEND_URL}/api/progress/checkin/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          weight: parseFloat(newWeight),
          questionnaire: questionnaire
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setShowWeightModal(false);
        setNewWeight('');
        setStep(1);
        setQuestionnaire({
          followedDiet: 'yes',
          followedTraining: 'yes',
          feeling: 7,
          observations: '',
        });
        await loadProgress();
        
        // Verifica se deve sugerir mudança de objetivo
        if (result.suggest_goal_change && result.suggested_goal) {
          const goalNames: Record<string, string> = {
            cutting: 'Cutting',
            bulking: 'Bulking', 
            manutencao: 'Manutenção'
          };
          
          const suggestedGoalName = goalNames[result.suggested_goal] || result.suggested_goal;
          
          Alert.alert(
            result.suggested_goal === 'cutting' ? '💪 Hora de definir!' : '🎯 Hora de crescer!',
            result.suggest_reason || `Considere mudar para ${suggestedGoalName}.`,
            [
              { 
                text: 'Ainda não', 
                style: 'cancel' 
              },
              { 
                text: `Sim, quero ${suggestedGoalName}!`, 
                onPress: async () => {
                  try {
                    const switchResponse = await safeFetch(`${BACKEND_URL}/api/user/${userId}/switch-goal/${result.suggested_goal}`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                    });
                    
                    if (switchResponse.ok) {
                      const switchResult = await switchResponse.json();
                      Alert.alert(
                        '✅ Objetivo alterado!',
                        `${switchResult.message}\nNovas calorias: ${switchResult.new_calories}kcal`
                      );
                      // Recarrega dados
                      await loadProgress();
                    } else {
                      const error = await switchResponse.json();
                      Alert.alert('Erro', error.detail || 'Não foi possível alterar objetivo');
                    }
                  } catch (error) {
                    Alert.alert('Erro', 'Falha na conexão. Tente novamente.');
                  }
                }
              }
            ]
          );
        } else {
          // Mostrar resultado do ajuste normal
          let message = result.diet_kept ? p.dietKept : p.dietAdjusted;
          if (result.calories_change) {
            const changeText = result.calories_change > 0 
              ? `${p.caloriesIncreased} ${result.calories_change}kcal` 
              : `${p.caloriesDecreased} ${Math.abs(result.calories_change)}kcal`;
            message += `\n${changeText}`;
          }
          if (result.foods_replaced > 0) {
            message += `\n${result.foods_replaced} ${p.foodsReplaced}`;
          }
          
          Alert.alert(t.common.success, message);
        }
      } else {
        const data = await response.json();
        Alert.alert(t.common.warning || 'Warning', data.detail || t.common.error);
      }
    } catch (error) {
      Alert.alert(t.common.error, t.common.connectionError || 'Could not save');
    } finally {
      setSaving(false);
    }
  };

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

  const FollowedOption = ({ label, value, selected, onSelect }: any) => (
    <TouchableOpacity 
      style={[
        styles.followedOption, 
        { borderColor: selected ? premiumColors.primary : theme.border },
        selected && { backgroundColor: premiumColors.primary + '15' }
      ]}
      onPress={() => onSelect(value)}
    >
      {value === 'yes' && <ThumbsUp size={16} color={selected ? premiumColors.primary : theme.textTertiary} />}
      {value === 'mostly' && <Meh size={16} color={selected ? premiumColors.primary : theme.textTertiary} />}
      {value === 'no' && <ThumbsDown size={16} color={selected ? premiumColors.primary : theme.textTertiary} />}
      <Text style={[styles.followedOptionText, { color: selected ? premiumColors.primary : theme.text }]}>{label}</Text>
    </TouchableOpacity>
  );

  const renderModalStep = () => {
    if (step === 1) {
      return (
        <>
          <Text style={[styles.stepTitle, { color: theme.textSecondary }]}>
            {p.checkInTitle} - 1/3
          </Text>
          <View style={styles.weightInputContainer}>
            <TextInput
              style={[styles.weightInput, { color: theme.text, borderColor: premiumColors.primary }]}
              value={newWeight}
              onChangeText={setNewWeight}
              keyboardType="decimal-pad"
              placeholder="0.0"
              placeholderTextColor={theme.textTertiary}
              autoFocus
            />
            <Text style={[styles.weightInputUnit, { color: theme.textSecondary }]}>kg</Text>
          </View>
          {currentWeight > 0 && (
            <Text style={[styles.lastWeightHint, { color: theme.textTertiary }]}>
              {p.lastWeight}: {currentWeight.toFixed(1)}kg
            </Text>
          )}
          <TouchableOpacity
            onPress={() => newWeight && setStep(2)}
            disabled={!newWeight}
            style={{ marginTop: spacing.xl }}
          >
            <LinearGradient
              colors={!newWeight ? ['#9CA3AF', '#6B7280'] : [premiumColors.gradient.start, premiumColors.gradient.end]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.nextButton}
            >
              <Text style={styles.nextButtonText}>{t.common.next || 'Próximo'}</Text>
              <ChevronRight size={20} color="#FFF" />
            </LinearGradient>
          </TouchableOpacity>
        </>
      );
    }

    if (step === 2) {
      return (
        <ScrollView showsVerticalScrollIndicator={false}>
          <Text style={[styles.stepTitle, { color: theme.textSecondary }]}>
            {p.checkInTitle} - 2/3
          </Text>
          <Text style={[styles.questionnaireTitle, { color: theme.text }]}>
            {p.howWasWeek}
          </Text>

          <QuestionnaireSlider
            label={p.diet}
            icon={Utensils}
            value={questionnaire.diet}
            onChange={(v: number) => setQuestionnaire({...questionnaire, diet: v})}
            color="#10B981"
          />
          <QuestionnaireSlider
            label={p.training}
            icon={Dumbbell}
            value={questionnaire.training}
            onChange={(v: number) => setQuestionnaire({...questionnaire, training: v})}
            color="#3B82F6"
          />
          <QuestionnaireSlider
            label={p.cardio}
            icon={TrendingUp}
            value={questionnaire.cardio}
            onChange={(v: number) => setQuestionnaire({...questionnaire, cardio: v})}
            color="#F59E0B"
          />
          <QuestionnaireSlider
            label={p.sleep}
            icon={Moon}
            value={questionnaire.sleep}
            onChange={(v: number) => setQuestionnaire({...questionnaire, sleep: v})}
            color="#8B5CF6"
          />
          <QuestionnaireSlider
            label={p.hydration}
            icon={Droplets}
            value={questionnaire.hydration}
            onChange={(v: number) => setQuestionnaire({...questionnaire, hydration: v})}
            color="#06B6D4"
          />
          <QuestionnaireSlider
            label={p.energy}
            icon={Smile}
            value={questionnaire.energy}
            onChange={(v: number) => setQuestionnaire({...questionnaire, energy: v})}
            color="#EC4899"
          />
          <QuestionnaireSlider
            label={p.hunger}
            icon={Frown}
            value={questionnaire.hunger}
            onChange={(v: number) => setQuestionnaire({...questionnaire, hunger: v})}
            color="#EF4444"
          />

          {/* Followed questions */}
          <View style={styles.followedSection}>
            <Text style={[styles.followedLabel, { color: theme.text }]}>{p.followedDiet}</Text>
            <View style={styles.followedOptions}>
              <FollowedOption label={p.yes} value="yes" selected={questionnaire.followedDiet === 'yes'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedDiet: v})} />
              <FollowedOption label={p.mostly} value="mostly" selected={questionnaire.followedDiet === 'mostly'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedDiet: v})} />
              <FollowedOption label={p.no} value="no" selected={questionnaire.followedDiet === 'no'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedDiet: v})} />
            </View>
          </View>

          <View style={styles.followedSection}>
            <Text style={[styles.followedLabel, { color: theme.text }]}>{p.followedTraining}</Text>
            <View style={styles.followedOptions}>
              <FollowedOption label={p.yes} value="yes" selected={questionnaire.followedTraining === 'yes'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedTraining: v})} />
              <FollowedOption label={p.mostly} value="mostly" selected={questionnaire.followedTraining === 'mostly'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedTraining: v})} />
              <FollowedOption label={p.no} value="no" selected={questionnaire.followedTraining === 'no'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedTraining: v})} />
            </View>
          </View>

          <View style={styles.followedSection}>
            <Text style={[styles.followedLabel, { color: theme.text }]}>{p.followedCardio}</Text>
            <View style={styles.followedOptions}>
              <FollowedOption label={p.yes} value="yes" selected={questionnaire.followedCardio === 'yes'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedCardio: v})} />
              <FollowedOption label={p.mostly} value="mostly" selected={questionnaire.followedCardio === 'mostly'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedCardio: v})} />
              <FollowedOption label={p.no} value="no" selected={questionnaire.followedCardio === 'no'} onSelect={(v: string) => setQuestionnaire({...questionnaire, followedCardio: v})} />
            </View>
          </View>

          <TouchableOpacity onPress={() => setStep(3)} style={{ marginTop: spacing.lg }}>
            <LinearGradient
              colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.nextButton}
            >
              <Text style={styles.nextButtonText}>{t.common.next || 'Próximo'}</Text>
              <ChevronRight size={20} color="#FFF" />
            </LinearGradient>
          </TouchableOpacity>
        </ScrollView>
      );
    }

    if (step === 3) {
      return (
        <ScrollView showsVerticalScrollIndicator={false}>
          <Text style={[styles.stepTitle, { color: theme.textSecondary }]}>
            {p.checkInTitle} - 3/3
          </Text>

          {/* Bored Foods */}
          <View style={styles.inputSection}>
            <View style={styles.inputLabelRow}>
              <AlertCircle size={18} color="#F59E0B" />
              <Text style={[styles.inputSectionLabel, { color: theme.text }]}>{p.boredFoods}</Text>
            </View>
            <Text style={[styles.inputHint, { color: theme.textTertiary }]}>{p.boredFoodsHint}</Text>
            <TextInput
              style={[styles.textArea, { color: theme.text, borderColor: theme.border, backgroundColor: isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(241, 245, 249, 0.8)' }]}
              value={questionnaire.boredFoods}
              onChangeText={(v) => setQuestionnaire({...questionnaire, boredFoods: v})}
              placeholder={p.boredFoodsPlaceholder}
              placeholderTextColor={theme.textTertiary}
              multiline
              numberOfLines={2}
            />
          </View>

          {/* Observations */}
          <View style={styles.inputSection}>
            <Text style={[styles.inputSectionLabel, { color: theme.text }]}>{p.observations}</Text>
            <TextInput
              style={[styles.textArea, { color: theme.text, borderColor: theme.border, backgroundColor: isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(241, 245, 249, 0.8)' }]}
              value={questionnaire.observations}
              onChangeText={(v) => setQuestionnaire({...questionnaire, observations: v})}
              placeholder={p.observationsPlaceholder}
              placeholderTextColor={theme.textTertiary}
              multiline
              numberOfLines={3}
            />
          </View>

          <TouchableOpacity
            onPress={handleSaveWeight}
            disabled={saving}
            style={{ marginTop: spacing.lg }}
          >
            <LinearGradient
              colors={saving ? ['#9CA3AF', '#6B7280'] : [premiumColors.gradient.start, premiumColors.gradient.end]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.saveButton}
            >
              <Check size={20} color="#FFF" />
              <Text style={styles.saveButtonText}>
                {saving ? t.common.saving : p.saveAndAdjust}
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        </ScrollView>
      );
    }
  };

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

              {targetWeight && (
                <View style={[styles.targetRow, { borderTopColor: theme.border }]}>
                  <Target size={16} color={theme.textTertiary} />
                  <Text style={[styles.targetText, { color: theme.textSecondary }]}>
                    {p.goal}: {targetWeight}kg
                  </Text>
                </View>
              )}

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

      {/* Weight Modal with Full Questionnaire */}
      <Modal visible={showWeightModal} transparent animationType="slide">
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={[styles.modalOverlay, { backgroundColor: theme.overlay }]}
        >
          <View style={[styles.modalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            <View style={styles.modalHeader}>
              <TouchableOpacity onPress={() => step > 1 ? setStep(step - 1) : setShowWeightModal(false)}>
                <Text style={[styles.backText, { color: premiumColors.primary }]}>
                  {step > 1 ? '← Voltar' : 'Cancelar'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => { setShowWeightModal(false); setStep(1); }}>
                <X size={24} color={theme.text} />
              </TouchableOpacity>
            </View>

            {renderModalStep()}
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
  modalContent: { borderTopLeftRadius: radius['2xl'], borderTopRightRadius: radius['2xl'], padding: spacing.lg, maxHeight: '90%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg },
  backText: { fontSize: 16, fontWeight: '600' },

  stepTitle: { fontSize: 12, fontWeight: '700', letterSpacing: 1, textAlign: 'center', marginBottom: spacing.md },
  weightInputContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.md, marginVertical: spacing.lg },
  weightInput: { fontSize: 48, fontWeight: '800', textAlign: 'center', width: 150, borderBottomWidth: 3, paddingVertical: spacing.sm },
  weightInputUnit: { fontSize: 24, fontWeight: '600' },
  lastWeightHint: { fontSize: 13, textAlign: 'center' },

  questionnaireTitle: { fontSize: 14, fontWeight: '700', letterSpacing: 0.5, marginBottom: spacing.lg, textAlign: 'center' },
  questionnaireRow: { marginBottom: spacing.md },
  questionnaireHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs },
  questionnaireLabel: { flex: 1, fontSize: 14, fontWeight: '600' },
  questionnaireValue: { fontSize: 18, fontWeight: '800', width: 30, textAlign: 'right' },
  slider: { width: '100%', height: 36 },

  followedSection: { marginBottom: spacing.lg },
  followedLabel: { fontSize: 14, fontWeight: '600', marginBottom: spacing.sm },
  followedOptions: { flexDirection: 'row', gap: spacing.sm },
  followedOption: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.xs, paddingVertical: spacing.sm, borderRadius: radius.lg, borderWidth: 1.5 },
  followedOptionText: { fontSize: 13, fontWeight: '600' },

  inputSection: { marginBottom: spacing.lg },
  inputLabelRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs },
  inputSectionLabel: { fontSize: 14, fontWeight: '700' },
  inputHint: { fontSize: 12, marginBottom: spacing.sm },
  textArea: { borderWidth: 1, borderRadius: radius.lg, padding: spacing.md, fontSize: 15, minHeight: 60, textAlignVertical: 'top' },

  nextButton: { height: 52, borderRadius: radius.lg, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm },
  nextButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  saveButton: { height: 52, borderRadius: radius.lg, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm },
  saveButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
});
