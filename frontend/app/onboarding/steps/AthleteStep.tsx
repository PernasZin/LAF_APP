import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

// Automatic phase derivation based on weeks to competition
const derivePhaseFromWeeks = (weeks: number): string => {
  if (weeks > 20) return 'off_season';
  if (weeks >= 16) return 'pre_prep';
  if (weeks >= 8) return 'prep';
  if (weeks >= 1) return 'peak_week';
  return 'post_show';
};

export default function AthleteStep({ data, updateData }: Props) {
  const phases = [
    {
      value: 'off_season',
      label: 'Off-Season',
      desc: 'Ganho de massa, superávit calórico',
      icon: 'barbell-outline' as any,
      color: '#10B981',
      weeksRange: '> 20 semanas',
    },
    {
      value: 'pre_prep',
      label: 'Pré-Prep',
      desc: 'Transição, ajuste gradual',
      icon: 'sync-outline' as any,
      color: '#3B82F6',
      weeksRange: '16-20 semanas',
    },
    {
      value: 'prep',
      label: 'Prep (Contest)',
      desc: 'Déficit agressivo, alta proteína',
      icon: 'flame-outline' as any,
      color: '#F59E0B',
      weeksRange: '8-15 semanas',
    },
    {
      value: 'peak_week',
      label: 'Peak Week',
      desc: 'Semana da competição',
      icon: 'trophy-outline' as any,
      color: '#EF4444',
      weeksRange: '≤ 7 semanas',
    },
    {
      value: 'post_show',
      label: 'Pós-Show',
      desc: 'Recuperação, reverse diet',
      icon: 'refresh-outline' as any,
      color: '#8B5CF6',
      weeksRange: 'Após competição',
    },
  ];

  // Auto-derive phase when weeks change
  useEffect(() => {
    if (data.weeks_to_competition && data.weeks_to_competition > 0) {
      const derivedPhase = derivePhaseFromWeeks(parseInt(data.weeks_to_competition));
      // Only auto-update if no manual selection or if weeks changed
      if (!data.competition_phase_manual) {
        updateData({ competition_phase: derivedPhase });
      }
    }
  }, [data.weeks_to_competition]);

  const handleWeeksChange = (value: string) => {
    const weeks = parseInt(value) || 0;
    if (weeks >= 0 && weeks <= 52) {
      updateData({ 
        weeks_to_competition: value,
        competition_phase_manual: false // Reset manual flag when weeks change
      });
    }
  };

  const handlePhaseSelect = (phase: string) => {
    updateData({ 
      competition_phase: phase,
      competition_phase_manual: true // Mark as manually selected
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Fase de Competição</Text>
      <Text style={styles.description}>
        Como atleta, seu plano será ajustado para sua fase atual de preparação.
      </Text>

      {/* Weeks to Competition Input */}
      <View style={styles.weeksSection}>
        <Text style={styles.sectionTitle}>Semanas até a competição</Text>
        <View style={styles.weeksInputContainer}>
          <TextInput
            style={styles.weeksInput}
            value={data.weeks_to_competition || ''}
            onChangeText={handleWeeksChange}
            placeholder="Ex: 12"
            keyboardType="number-pad"
            maxLength={2}
          />
          <Text style={styles.weeksLabel}>semanas</Text>
        </View>
        {data.weeks_to_competition > 0 && (
          <Text style={styles.derivedPhaseHint}>
            Fase sugerida: {phases.find(p => p.value === derivePhaseFromWeeks(parseInt(data.weeks_to_competition)))?.label || 'Off-Season'}
          </Text>
        )}
      </View>

      {/* Phase Selection */}
      <View style={styles.phasesSection}>
        <Text style={styles.sectionTitle}>Selecione sua fase atual</Text>
        <Text style={styles.hint}>
          {data.competition_phase_manual 
            ? '(Seleção manual ativa)' 
            : '(Auto-derivada das semanas)'}
        </Text>
        
        <View style={styles.phasesContainer}>
          {phases.map((phase) => (
            <TouchableOpacity
              key={phase.value}
              style={[
                styles.phaseCard,
                data.competition_phase === phase.value && styles.phaseCardActive,
                data.competition_phase === phase.value && { borderColor: phase.color },
              ]}
              onPress={() => handlePhaseSelect(phase.value)}
              activeOpacity={0.7}
            >
              <View style={[styles.phaseIcon, { backgroundColor: phase.color + '20' }]}>
                <Ionicons
                  name={phase.icon}
                  size={20}
                  color={data.competition_phase === phase.value ? phase.color : '#9CA3AF'}
                />
              </View>
              <View style={styles.phaseContent}>
                <Text style={[
                  styles.phaseLabel,
                  data.competition_phase === phase.value && { color: phase.color }
                ]}>
                  {phase.label}
                </Text>
                <Text style={styles.phaseDesc}>{phase.desc}</Text>
                <Text style={styles.phaseWeeks}>{phase.weeksRange}</Text>
              </View>
              {data.competition_phase === phase.value && (
                <Ionicons name="checkmark-circle" size={22} color={phase.color} />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>
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
    marginBottom: 24,
    lineHeight: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  hint: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 12,
  },
  weeksSection: {
    marginBottom: 24,
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
  },
  weeksInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  weeksInput: {
    flex: 1,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    maxWidth: 100,
  },
  weeksLabel: {
    fontSize: 16,
    color: '#6B7280',
  },
  derivedPhaseHint: {
    fontSize: 14,
    color: '#10B981',
    marginTop: 8,
    fontWeight: '500',
  },
  phasesSection: {
    flex: 1,
  },
  phasesContainer: {
    gap: 10,
  },
  phaseCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#fff',
    gap: 10,
  },
  phaseCardActive: {
    backgroundColor: '#F0FDF4',
  },
  phaseIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  phaseContent: {
    flex: 1,
  },
  phaseLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: '#374151',
  },
  phaseDesc: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  phaseWeeks: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 2,
  },
});
