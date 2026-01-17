/**
 * Training Days Step - Escolha dos Dias de Treino
 * Contador com limite baseado na divisão escolhida
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Check, Calendar } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

const WEEKDAYS = [
  { value: 0, labelPt: 'Domingo', labelEn: 'Sunday', short: 'Dom' },
  { value: 1, labelPt: 'Segunda', labelEn: 'Monday', short: 'Seg' },
  { value: 2, labelPt: 'Terça', labelEn: 'Tuesday', short: 'Ter' },
  { value: 3, labelPt: 'Quarta', labelEn: 'Wednesday', short: 'Qua' },
  { value: 4, labelPt: 'Quinta', labelEn: 'Thursday', short: 'Qui' },
  { value: 5, labelPt: 'Sexta', labelEn: 'Friday', short: 'Sex' },
  { value: 6, labelPt: 'Sábado', labelEn: 'Saturday', short: 'Sáb' },
];

export default function TrainingDaysStep({ formData, updateFormData, theme, isDark }: Props) {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const isEnglish = language === 'en-US';

  // Usa a frequência selecionada no step anterior
  const limit = parseInt(formData.weekly_training_frequency) || 3;
  const selectedDays: number[] = formData.training_days || [];
  const selectedCount = selectedDays.length;

  const handleDayToggle = (dayValue: number) => {
    const isSelected = selectedDays.includes(dayValue);
    
    if (isSelected) {
      // Remove o dia
      updateFormData({ 
        training_days: selectedDays.filter(d => d !== dayValue) 
      });
    } else {
      // Adiciona o dia (se não ultrapassou o limite)
      if (selectedCount < limit) {
        updateFormData({ 
          training_days: [...selectedDays, dayValue].sort((a, b) => a - b)
        });
      }
    }
  };

  const canContinue = selectedCount === limit;

  return (
    <View style={styles.container}>
      {/* Header com contador */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <Calendar size={20} color={premiumColors.primary} />
          <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
            {isEnglish ? 'CHOOSE YOUR TRAINING DAYS' : 'ESCOLHA SEUS DIAS DE TREINO'}
          </Text>
        </View>
        
        {/* Contador */}
        <View style={[
          styles.counterBadge, 
          { 
            backgroundColor: canContinue ? premiumColors.primary : theme.input.background,
          }
        ]}>
          <Text style={[
            styles.counterText, 
            { color: canContinue ? '#FFF' : theme.text }
          ]}>
            {selectedCount} / {limit}
          </Text>
        </View>
      </View>

      {/* Frequência selecionada */}
      <View style={[styles.splitInfo, { backgroundColor: isDark ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.08)' }]}>
        <Text style={[styles.splitInfoText, { color: premiumColors.primary }]}>
          {limit}x {isEnglish ? 'per week' : 'por semana'} - {isEnglish ? 'Select your training days' : 'Selecione seus dias de treino'}
        </Text>
      </View>

      {/* Grid de dias */}
      <View style={styles.daysGrid}>
        {WEEKDAYS.map((day) => {
          const isSelected = selectedDays.includes(day.value);
          const isDisabled = !isSelected && selectedCount >= limit;
          
          return (
            <TouchableOpacity
              key={day.value}
              style={[
                styles.dayCard,
                {
                  backgroundColor: isSelected
                    ? isDark ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.15)'
                    : isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
                  borderColor: isSelected ? premiumColors.primary : theme.border,
                  opacity: isDisabled ? 0.5 : 1,
                }
              ]}
              onPress={() => handleDayToggle(day.value)}
              disabled={isDisabled}
              activeOpacity={0.7}
            >
              <View style={[
                styles.checkCircle,
                {
                  backgroundColor: isSelected ? premiumColors.primary : 'transparent',
                  borderColor: isSelected ? premiumColors.primary : theme.border,
                }
              ]}>
                {isSelected && <Check size={14} color="#FFF" strokeWidth={3} />}
              </View>
              
              <Text style={[
                styles.dayLabel,
                { color: isSelected ? premiumColors.primary : theme.text }
              ]}>
                {isEnglish ? day.labelEn : day.labelPt}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Mensagem de status */}
      <View style={[
        styles.statusBox, 
        { 
          backgroundColor: canContinue 
            ? isDark ? 'rgba(16, 185, 129, 0.15)' : 'rgba(16, 185, 129, 0.1)'
            : isDark ? 'rgba(245, 158, 11, 0.15)' : 'rgba(245, 158, 11, 0.1)'
        }
      ]}>
        <Text style={[
          styles.statusText, 
          { color: canContinue ? '#10B981' : '#F59E0B' }
        ]}>
          {canContinue 
            ? (isEnglish ? '✅ Perfect! You can continue.' : '✅ Perfeito! Você pode continuar.')
            : (isEnglish 
                ? `⚠️ Select exactly ${limit} days to continue.`
                : `⚠️ Selecione exatamente ${limit} dias para continuar.`)
          }
        </Text>
      </View>

      {/* Preview dos dias selecionados */}
      {selectedDays.length > 0 && (
        <View style={styles.previewSection}>
          <Text style={[styles.previewLabel, { color: theme.textTertiary }]}>
            {isEnglish ? 'Your training days:' : 'Seus dias de treino:'}
          </Text>
          <View style={styles.previewDays}>
            {selectedDays.map((dayValue) => {
              const day = WEEKDAYS.find(d => d.value === dayValue);
              return (
                <View 
                  key={dayValue} 
                  style={[styles.previewChip, { backgroundColor: premiumColors.primary + '20' }]}
                >
                  <Text style={[styles.previewChipText, { color: premiumColors.primary }]}>
                    {isEnglish ? day?.labelEn : day?.labelPt}
                  </Text>
                </View>
              );
            })}
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    paddingTop: spacing.lg,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  counterBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
  },
  counterText: {
    fontSize: 14,
    fontWeight: '800',
  },
  splitInfo: {
    padding: spacing.sm,
    borderRadius: radius.lg,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  splitInfoText: {
    fontSize: 14,
    fontWeight: '700',
  },
  daysGrid: {
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  dayCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.base,
    borderRadius: radius.lg,
    borderWidth: 2,
    gap: spacing.md,
  },
  checkCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dayLabel: {
    fontSize: 16,
    fontWeight: '600',
  },
  statusBox: {
    padding: spacing.base,
    borderRadius: radius.lg,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
  },
  previewSection: {
    marginTop: spacing.sm,
  },
  previewLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  previewDays: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  previewChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
  },
  previewChipText: {
    fontSize: 12,
    fontWeight: '600',
  },
});
