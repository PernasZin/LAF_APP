/**
 * Training Split Step - Escolha da Divisão de Treino
 * FULL BODY (2x) ou PPL (6x)
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Dumbbell, Repeat } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

const TRAINING_SPLITS = [
  { 
    value: 'full_body', 
    label: 'FULL BODY', 
    frequency: 2,
    desc: '2 treinos por semana',
    descEn: '2 workouts per week',
    icon: Dumbbell,
    color: '#3B82F6'
  },
  { 
    value: 'ppl', 
    label: 'PPL', 
    frequency: 6,
    desc: '6 treinos por semana',
    descEn: '6 workouts per week',
    icon: Repeat,
    color: '#10B981'
  },
];

export default function TrainingSplitStep({ formData, updateFormData, theme, isDark }: Props) {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const isEnglish = language === 'en-US';

  const handleSelectSplit = (split: typeof TRAINING_SPLITS[0]) => {
    updateFormData({ 
      training_split: split.value,
      weekly_training_frequency: split.frequency.toString(),
      // Limpa os dias selecionados quando muda a divisão
      training_days: []
    });
  };

  return (
    <View style={styles.container}>
      <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
        {isEnglish ? 'CHOOSE YOUR TRAINING SPLIT' : 'ESCOLHA SUA DIVISÃO DE TREINO'}
      </Text>
      
      <View style={styles.splitsContainer}>
        {TRAINING_SPLITS.map((split) => {
          const isSelected = formData.training_split === split.value;
          const Icon = split.icon;
          
          return (
            <TouchableOpacity
              key={split.value}
              style={[
                styles.splitCard,
                {
                  backgroundColor: isSelected
                    ? isDark ? `${split.color}20` : `${split.color}15`
                    : isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
                  borderColor: isSelected ? split.color : theme.border,
                }
              ]}
              onPress={() => handleSelectSplit(split)}
              activeOpacity={0.8}
            >
              <View style={[
                styles.iconContainer,
                { backgroundColor: isSelected ? `${split.color}25` : theme.input.background }
              ]}>
                <Icon size={32} color={isSelected ? split.color : theme.textTertiary} strokeWidth={2} />
              </View>
              
              <Text style={[
                styles.splitLabel, 
                { color: isSelected ? split.color : theme.text }
              ]}>
                {split.label}
              </Text>
              
              <View style={[
                styles.frequencyBadge,
                { backgroundColor: isSelected ? split.color : theme.input.background }
              ]}>
                <Text style={[
                  styles.frequencyText,
                  { color: isSelected ? '#FFF' : theme.textSecondary }
                ]}>
                  {split.frequency}x / {isEnglish ? 'week' : 'semana'}
                </Text>
              </View>
              
              <Text style={[styles.splitDesc, { color: theme.textTertiary }]}>
                {isEnglish ? split.descEn : split.desc}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <View style={[styles.infoBox, { backgroundColor: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.08)' }]}>
        <Text style={[styles.infoText, { color: theme.textSecondary }]}>
          {isEnglish 
            ? '💡 FULL BODY: Train all muscle groups each session.\nPPL: Push, Pull, Legs split for more volume.'
            : '💡 FULL BODY: Treina todos os grupos musculares por sessão.\nPPL: Divisão Push, Pull, Legs para mais volume.'}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    paddingTop: spacing.lg,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  splitsContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  splitCard: {
    flex: 1,
    padding: spacing.lg,
    borderRadius: radius.xl,
    borderWidth: 2,
    alignItems: 'center',
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: radius.xl,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  splitLabel: {
    fontSize: 20,
    fontWeight: '800',
    letterSpacing: 1,
    marginBottom: spacing.sm,
  },
  frequencyBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    marginBottom: spacing.sm,
  },
  frequencyText: {
    fontSize: 13,
    fontWeight: '700',
  },
  splitDesc: {
    fontSize: 12,
    textAlign: 'center',
  },
  infoBox: {
    padding: spacing.base,
    borderRadius: radius.lg,
  },
  infoText: {
    fontSize: 13,
    lineHeight: 20,
  },
});
