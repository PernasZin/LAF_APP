/**
 * LAF Premium Training Config Screen
 * ===================================
 * Configurações de frequência, tempo de treino e cardio
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Check, Calendar, Clock, Dumbbell, Heart } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

import { config } from '../../config';
const BACKEND_URL = config.BACKEND_URL;

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

export default function TrainingConfigScreen() {
  const { t } = useTranslation();
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  const [frequency, setFrequency] = useState(3);
  const [duration, setDuration] = useState(60);
  const [level, setLevel] = useState('intermediario');
  // Cardio (NOVO)
  const [cardioMinutos, setCardioMinutos] = useState(0);
  const [cardioIntensidade, setCardioIntensidade] = useState('moderado');

  // Níveis de treino - usando traduções (inclui Low Volume apenas aqui)
  const LEVELS = [
    { value: 'novato', label: t.trainingConfig.novice, desc: t.trainingConfig.noviceDesc },
    { value: 'iniciante', label: t.trainingConfig.beginner, desc: t.trainingConfig.beginnerDesc },
    { value: 'intermediario', label: t.trainingConfig.intermediate, desc: t.trainingConfig.intermediateDesc },
    { value: 'avancado', label: t.trainingConfig.advanced, desc: t.trainingConfig.advancedDesc },
    { value: 'low_volume', label: t.trainingConfig.lowVolume, desc: t.trainingConfig.lowVolumeDesc },
  ];

  // Frequências de treino - usando traduções
  const FREQUENCIES = [
    { value: 2, label: t.trainingConfig.freq2x, desc: t.trainingConfig.freq2xDesc },
    { value: 3, label: t.trainingConfig.freq3x, desc: t.trainingConfig.freq3xDesc },
    { value: 4, label: t.trainingConfig.freq4x, desc: t.trainingConfig.freq4xDesc },
    { value: 5, label: t.trainingConfig.freq5x, desc: t.trainingConfig.freq5xDesc },
    { value: 6, label: t.trainingConfig.freq6x, desc: t.trainingConfig.freq6xDesc },
  ];

  // Tempo de treino - usando traduções
  const DURATIONS = [
    { value: 30, label: t.trainingConfig.dur30, desc: t.trainingConfig.dur30Desc },
    { value: 60, label: t.trainingConfig.dur60, desc: t.trainingConfig.dur60Desc },
    { value: 90, label: t.trainingConfig.dur90, desc: t.trainingConfig.dur90Desc },
    { value: 120, label: t.trainingConfig.dur120, desc: t.trainingConfig.dur120Desc },
  ];

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        const response = await fetch(`${BACKEND_URL}/api/user/profile/${id}`);
        if (response.ok) {
          const data = await response.json();
          setFrequency(data.weekly_training_frequency || 3);
          // O backend usa available_time_per_session, mas também pode vir como training_duration
          setDuration(data.available_time_per_session || data.training_duration || 60);
          setLevel(data.training_level || 'intermediario');
        }
      }
    } catch (error) {
      console.error('Error loading config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!userId) return;
    setSaving(true);

    try {
      // 1. Salva as configurações de treino
      const response = await fetch(`${BACKEND_URL}/api/user/profile/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weekly_training_frequency: frequency,
          training_duration: duration,
          training_level: level,
        }),
      });

      if (response.ok) {
        const profileData = await response.json();
        await AsyncStorage.setItem('userProfile', JSON.stringify(profileData));
        
        // 2. Regenera o treino automaticamente com as novas configurações
        const workoutResponse = await fetch(`${BACKEND_URL}/api/workout/generate?user_id=${userId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        
        if (workoutResponse.ok) {
          const workoutData = await workoutResponse.json();
          await AsyncStorage.setItem('userWorkout', JSON.stringify(workoutData));
        }
        
        Alert.alert(
          t.trainingConfig.successTitle, 
          t.trainingConfig.successMessage,
          [{ text: 'OK', onPress: () => router.back() }]
        );
      } else {
        Alert.alert(t.trainingConfig.errorTitle, t.trainingConfig.errorSave);
      }
    } catch (error) {
      console.error('Erro ao salvar:', error);
      Alert.alert(t.trainingConfig.errorTitle, t.trainingConfig.errorConnect);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <View style={styles.loadingContainer}>
          <Text style={{ color: theme.text }}>{t.common.loading}</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
              <ArrowLeft size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.headerTitle, { color: theme.text }]}>{t.trainingConfig.title}</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Nível de Treino */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <View style={styles.sectionHeader}>
              <Dumbbell size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.trainingConfig.experienceLevel}</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.card}>
              {LEVELS.map((item, index) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.optionItem,
                    { borderBottomColor: theme.border },
                    index === LEVELS.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => setLevel(item.value)}
                >
                  <View style={styles.optionContent}>
                    <Text style={[styles.optionLabel, { color: theme.text }]}>{item.label}</Text>
                    <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{item.desc}</Text>
                  </View>
                  <View style={[
                    styles.radioOuter,
                    { borderColor: level === item.value ? premiumColors.primary : theme.border }
                  ]}>
                    {level === item.value && (
                      <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </GlassCard>
            
            {level === 'novato' && (
              <View style={[styles.infoBox, { backgroundColor: premiumColors.primary + '15' }]}>
                <Text style={[styles.infoText, { color: premiumColors.primary }]}>
                  {t.trainingConfig.noviceHint}
                </Text>
              </View>
            )}
          </Animated.View>

          {/* Frequência */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <View style={styles.sectionHeader}>
              <Calendar size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.trainingConfig.weeklyFrequency}</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.card}>
              {FREQUENCIES.map((item, index) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.optionItem,
                    { borderBottomColor: theme.border },
                    index === FREQUENCIES.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => setFrequency(item.value)}
                >
                  <View style={styles.optionContent}>
                    <Text style={[styles.optionLabel, { color: theme.text }]}>{item.label}</Text>
                    <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{item.desc}</Text>
                  </View>
                  <View style={[
                    styles.radioOuter,
                    { borderColor: frequency === item.value ? premiumColors.primary : theme.border }
                  ]}>
                    {frequency === item.value && (
                      <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </GlassCard>
          </Animated.View>

          {/* Duração */}
          <Animated.View entering={FadeInDown.delay(300).springify()}>
            <View style={styles.sectionHeader}>
              <Clock size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.trainingConfig.availableTime}</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.card}>
              {DURATIONS.map((item, index) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.optionItem,
                    { borderBottomColor: theme.border },
                    index === DURATIONS.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => setDuration(item.value)}
                >
                  <View style={styles.optionContent}>
                    <Text style={[styles.optionLabel, { color: theme.text }]}>{item.label}</Text>
                    <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{item.desc}</Text>
                  </View>
                  <View style={[
                    styles.radioOuter,
                    { borderColor: duration === item.value ? premiumColors.primary : theme.border }
                  ]}>
                    {duration === item.value && (
                      <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </GlassCard>
          </Animated.View>

          {/* Save Button */}
          <Animated.View entering={FadeInDown.delay(400).springify()} style={styles.saveContainer}>
            <TouchableOpacity onPress={handleSave} disabled={saving} activeOpacity={0.9}>
              <LinearGradient
                colors={saving
                  ? ['#9CA3AF', '#6B7280']
                  : [premiumColors.gradient.start, premiumColors.gradient.end]
                }
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.saveButton}
              >
                <Check size={20} color="#FFF" />
                <Text style={styles.saveButtonText}>
                  {saving ? t.trainingConfig.savingSettings : t.trainingConfig.saveSettings}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>

          <View style={{ height: 40 }} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700' },

  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  sectionTitle: { fontSize: 16, fontWeight: '700' },

  card: { padding: spacing.base, marginBottom: spacing.sm },

  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  optionContent: { flex: 1 },
  optionLabel: { fontSize: 16, fontWeight: '600' },
  optionDesc: { fontSize: 13, marginTop: 2 },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  radioInner: { width: 12, height: 12, borderRadius: 6 },

  infoBox: {
    padding: spacing.md,
    borderRadius: radius.lg,
    marginTop: spacing.sm,
  },
  infoText: { fontSize: 13, lineHeight: 18 },

  saveContainer: { marginTop: spacing.xl },
  saveButton: {
    height: 56,
    borderRadius: radius.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  saveButtonText: { color: '#FFF', fontSize: 17, fontWeight: '700' },
});
