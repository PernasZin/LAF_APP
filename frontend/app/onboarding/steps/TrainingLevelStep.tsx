/**
 * Premium Training Level Step
 * Com suporte a i18n
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { User, Dumbbell, Trophy, Clock, Calendar } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

const FREQUENCIES = [
  { value: '2', label: '2x' },
  { value: '3', label: '3x' },
  { value: '4', label: '4x' },
  { value: '5', label: '5x' },
  { value: '6', label: '6x' },
];

const DURATIONS = [
  { value: '30', label: '30 min' },
  { value: '45', label: '45 min' },
  { value: '60', label: '60 min' },
  { value: '90', label: '90 min' },
];

export default function TrainingLevelStep({ formData, updateFormData, theme, isDark }: Props) {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const t = translations[language]?.onboarding || translations['pt-BR'].onboarding;

  // Níveis de experiência com exercícios
  const LEVELS = [
    { value: 'novato', label: t.novice || '🆕 Novato', desc: t.noviceDesc || 'Nunca pratiquei', icon: User },
    { value: 'iniciante', label: t.beginner || 'Iniciante', desc: t.beginnerDesc || '0-1 ano de prática', icon: User },
    { value: 'intermediario', label: t.intermediate || 'Intermediário', desc: t.intermediateDesc || '1-3 anos', icon: Dumbbell },
    { value: 'avancado', label: t.advanced || 'Avançado', desc: t.advancedDesc || '3+ anos', icon: Trophy },
  ];

  return (
    <View style={styles.container}>
      {/* Training Level */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
        {t.trainingLevelTitle || t.steps?.trainingLevel || 'Nível de Treino'}
      </Text>
      <View style={styles.levelsGrid}>
        {LEVELS.map((level) => {
          const isSelected = formData.training_level === level.value;
          const Icon = level.icon;
          return (
            <TouchableOpacity
              key={level.value}
              style={[
                styles.levelCard,
                {
                  backgroundColor: isSelected
                    ? isDark ? 'rgba(16, 185, 129, 0.15)' : 'rgba(16, 185, 129, 0.1)'
                    : isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
                  borderColor: isSelected ? premiumColors.primary : theme.border,
                }
              ]}
              onPress={() => updateFormData({ training_level: level.value })}
            >
              <View style={[
                styles.iconContainer,
                { backgroundColor: isSelected ? `${premiumColors.primary}20` : theme.input.background }
              ]}>
                <Icon size={24} color={isSelected ? premiumColors.primary : theme.textTertiary} />
              </View>
              <Text style={[styles.levelLabel, { color: isSelected ? premiumColors.primary : theme.text }]}>
                {level.label}
              </Text>
              <Text style={[styles.levelDesc, { color: theme.textTertiary }]}>
                {level.desc}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Frequency */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Calendar size={18} color={premiumColors.primary} />
          <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
            {t.daysPerWeek || 'Dias por semana'}
          </Text>
        </View>
        <View style={styles.optionsRow}>
          {FREQUENCIES.map((freq) => {
            const isSelected = formData.weekly_training_frequency === freq.value;
            return (
              <TouchableOpacity
                key={freq.value}
                style={[
                  styles.optionChip,
                  {
                    backgroundColor: isSelected ? premiumColors.primary : theme.input.background,
                    borderColor: isSelected ? premiumColors.primary : theme.border,
                  }
                ]}
                onPress={() => updateFormData({ weekly_training_frequency: freq.value })}
              >
                <Text style={[
                  styles.optionChipText,
                  { color: isSelected ? '#FFF' : theme.text }
                ]}>
                  {freq.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Duration */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Clock size={18} color={premiumColors.primary} />
          <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
            {t.timePerSession || 'Duração do treino'}
          </Text>
        </View>
        <View style={styles.optionsRow}>
          {DURATIONS.map((dur) => {
            const isSelected = formData.available_time_per_session === dur.value;
            return (
              <TouchableOpacity
                key={dur.value}
                style={[
                  styles.optionChip,
                  {
                    backgroundColor: isSelected ? premiumColors.primary : theme.input.background,
                    borderColor: isSelected ? premiumColors.primary : theme.border,
                  }
                ]}
                onPress={() => updateFormData({ available_time_per_session: dur.value })}
              >
                <Text style={[
                  styles.optionChipText,
                  { color: isSelected ? '#FFF' : theme.text }
                ]}>
                  {dur.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: spacing.lg },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: spacing.md,
  },
  levelsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  levelCard: {
    width: '47%',
    padding: spacing.base,
    borderRadius: radius.xl,
    borderWidth: 2,
    alignItems: 'center',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  levelLabel: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 2,
  },
  levelDesc: {
    fontSize: 12,
    textAlign: 'center',
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  optionsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  optionChip: {
    paddingHorizontal: spacing.base,
    paddingVertical: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1.5,
  },
  optionChipText: {
    fontSize: 14,
    fontWeight: '600',
  },
});
