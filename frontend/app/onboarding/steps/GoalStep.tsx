import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Platform, Modal, Pressable, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { translations, SupportedLanguage } from '../../../i18n/translations';

// DateTimePicker só funciona em iOS/Android, não na web
let DateTimePicker: any = null;
if (Platform.OS !== 'web') {
  DateTimePicker = require('@react-native-community/datetimepicker').default;
}

interface Props {
  data: any;
  updateData: (data: any) => void;
  language: SupportedLanguage;
}

export default function GoalStep({ data, updateData, language }: Props) {
  const [showDatePicker, setShowDatePicker] = useState(false);
  const t = translations[language].onboarding;
  
  const goals = [
    {
      value: 'cutting',
      label: t.cutting,
      icon: 'trending-down' as any,
      desc: t.cuttingDesc,
      color: '#EF4444',
    },
    {
      value: 'bulking',
      label: t.bulking,
      icon: 'trending-up' as any,
      desc: t.bulkingDesc,
      color: '#10B981',
    },
    {
      value: 'manutencao',
      label: t.maintenance,
      icon: 'remove' as any,
      desc: t.maintenanceDesc,
      color: '#3B82F6',
    },
    {
      value: 'atleta',
      label: t.athlete,
      icon: 'trophy' as any,
      desc: t.athleteDesc,
      color: '#F59E0B',
    },
  ];

  const handleGoalSelect = (goalValue: string) => {
    updateData({ goal: goalValue });
    // Se selecionou atleta, não precisa mais de campos extras
    // A data será selecionada abaixo
  };

  const handleDateChange = (event: any, selectedDate?: Date) => {
    if (Platform.OS === 'android') {
      setShowDatePicker(false);
    }
    
    if (selectedDate) {
      // Formata para ISO string (YYYY-MM-DD)
      const isoDate = selectedDate.toISOString().split('T')[0];
      updateData({ athlete_competition_date: isoDate });
    }
  };

  const formatDateDisplay = (dateStr: string) => {
    if (!dateStr) return t.selectDate;
    const date = new Date(dateStr);
    // Use appropriate locale based on language
    const locale = language === 'pt-BR' ? 'pt-BR' : language === 'es-ES' ? 'es-ES' : 'en-US';
    return date.toLocaleDateString(locale, {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const getWeeksToCompetition = (dateStr: string) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const weeks = Math.floor(diff / (1000 * 60 * 60 * 24 * 7));
    return weeks > 0 ? weeks : 0;
  };

  const getPhaseFromWeeks = (weeks: number | null) => {
    if (weeks === null) return null;
    if (weeks > 20) return { phase: 'OFF-SEASON', color: '#10B981' };
    if (weeks >= 16) return { phase: 'PRÉ-PREP', color: '#3B82F6' };
    if (weeks >= 8) return { phase: 'PREP', color: '#F59E0B' };
    if (weeks >= 1) return { phase: 'PEAK WEEK', color: '#EF4444' };
    return { phase: 'PÓS-SHOW', color: '#8B5CF6' };
  };

  const weeks = getWeeksToCompetition(data.athlete_competition_date);
  const phaseInfo = getPhaseFromWeeks(weeks);

  // Data mínima: hoje
  const minDate = new Date();
  // Data máxima: 2 anos no futuro
  const maxDate = new Date();
  maxDate.setFullYear(maxDate.getFullYear() + 2);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Qual seu objetivo?</Text>
      <Text style={styles.description}>
        Vamos ajustar seu plano de dieta e treino para seu objetivo específico.
      </Text>

      <View style={styles.goalsContainer}>
        {goals.map((goal) => (
          <TouchableOpacity
            key={goal.value}
            style={[
              styles.goalCard,
              data.goal === goal.value && styles.goalCardActive,
            ]}
            onPress={() => handleGoalSelect(goal.value)}
            activeOpacity={0.7}
          >
            <View
              style={[
                styles.iconContainer,
                { backgroundColor: goal.color + '20' },
              ]}
            >
              <Ionicons
                name={goal.icon}
                size={28}
                color={data.goal === goal.value ? goal.color : '#6B7280'}
              />
            </View>
            <View style={styles.goalContent}>
              <Text
                style={[
                  styles.goalLabel,
                  data.goal === goal.value && styles.goalLabelActive,
                ]}
              >
                {goal.label}
              </Text>
              <Text style={styles.goalDesc}>{goal.desc}</Text>
            </View>
            {data.goal === goal.value && (
              <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* Campo de Data do Campeonato - APENAS para Atleta */}
      {data.goal === 'atleta' && (
        <View style={styles.athleteSection}>
          <View style={styles.divider} />
          
          <Text style={styles.athleteTitle}>
            <Ionicons name="calendar" size={20} color="#F59E0B" /> Data do Campeonato *
          </Text>
          <Text style={styles.athleteDesc}>
            Informe a data do seu campeonato. O sistema controlará sua preparação automaticamente até o dia do evento.
          </Text>

          {/* Input de Data - WEB */}
          {Platform.OS === 'web' ? (
            <View style={styles.webDateContainer}>
              <Ionicons name="calendar-outline" size={24} color="#F59E0B" />
              <input
                type="date"
                value={data.athlete_competition_date || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  updateData({ athlete_competition_date: value });
                }}
                min={new Date().toISOString().split('T')[0]}
                max={new Date(Date.now() + 730 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
                style={{
                  flex: 1,
                  border: 'none',
                  background: 'transparent',
                  fontSize: 16,
                  fontWeight: '500',
                  color: '#92400E',
                  marginLeft: 12,
                  outline: 'none',
                }}
              />
            </View>
          ) : (
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowDatePicker(true)}
            >
              <Ionicons name="calendar-outline" size={24} color="#F59E0B" />
              <Text style={styles.dateButtonText}>
                {formatDateDisplay(data.athlete_competition_date)}
              </Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>
          )}

          {/* Mostra informação de fase calculada */}
          {data.athlete_competition_date && weeks !== null && phaseInfo && (
            <View style={styles.phaseInfoContainer}>
              <View style={[styles.phaseBadge, { backgroundColor: phaseInfo.color + '20' }]}>
                <Text style={[styles.phaseBadgeText, { color: phaseInfo.color }]}>
                  {phaseInfo.phase}
                </Text>
              </View>
              <Text style={styles.weeksText}>
                {weeks > 0 ? `${weeks} semanas até o campeonato` : 'Campeonato passou'}
              </Text>
            </View>
          )}

          {/* Date Picker Modal para iOS */}
          {Platform.OS === 'ios' && showDatePicker && DateTimePicker && (
            <Modal
              transparent
              animationType="slide"
              visible={showDatePicker}
              onRequestClose={() => setShowDatePicker(false)}
            >
              <View style={styles.modalOverlay}>
                <View style={styles.modalContent}>
                  <View style={styles.modalHeader}>
                    <Text style={styles.modalTitle}>Data do Campeonato</Text>
                    <Pressable onPress={() => setShowDatePicker(false)}>
                      <Text style={styles.modalDone}>OK</Text>
                    </Pressable>
                  </View>
                  <DateTimePicker
                    value={data.athlete_competition_date ? new Date(data.athlete_competition_date) : new Date()}
                    mode="date"
                    display="spinner"
                    onChange={handleDateChange}
                    minimumDate={minDate}
                    maximumDate={maxDate}
                    locale="pt-BR"
                    themeVariant="light"
                    textColor="#000000"
                  />
                </View>
              </View>
            </Modal>
          )}

          {/* Date Picker inline para Android */}
          {Platform.OS === 'android' && showDatePicker && DateTimePicker && (
            <DateTimePicker
              value={data.athlete_competition_date ? new Date(data.athlete_competition_date) : new Date()}
              mode="date"
              display="default"
              onChange={handleDateChange}
              minimumDate={minDate}
              maximumDate={maxDate}
            />
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 32,
    lineHeight: 24,
  },
  goalsContainer: {
    gap: 16,
  },
  goalCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
    gap: 12,
  },
  goalCardActive: {
    borderColor: '#10B981',
    backgroundColor: '#F0FDF4',
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  goalContent: {
    flex: 1,
  },
  goalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  goalLabelActive: {
    color: '#10B981',
  },
  goalDesc: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  // Athlete Section
  athleteSection: {
    marginTop: 24,
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginBottom: 24,
  },
  athleteTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  athleteDesc: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16,
    lineHeight: 20,
  },
  dateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#F59E0B',
    backgroundColor: '#FFFBEB',
    gap: 12,
  },
  dateButtonText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: '#92400E',
  },
  webDateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#F59E0B',
    backgroundColor: '#FFFBEB',
  },
  // Phase Info
  phaseInfoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    gap: 12,
  },
  phaseBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  phaseBadgeText: {
    fontSize: 12,
    fontWeight: '700',
  },
  weeksText: {
    fontSize: 14,
    color: '#6B7280',
  },
  // Modal
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: 40,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  modalDone: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F59E0B',
  },
});