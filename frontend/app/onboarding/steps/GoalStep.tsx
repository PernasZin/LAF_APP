import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  data: any;
  updateData: (data: any) => void;
  language: SupportedLanguage;
}

export default function GoalStep({ data, updateData, language }: Props) {
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
  ];

  const handleGoalSelect = (goalValue: string) => {
    updateData({ goal: goalValue });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t.goalTitle}</Text>
      <Text style={styles.description}>
        {t.goalDesc}
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
});