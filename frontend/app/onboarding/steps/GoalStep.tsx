import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

export default function GoalStep({ data, updateData }: Props) {
  const goals = [
    {
      value: 'cutting',
      label: 'Emagrecimento (Cutting)',
      icon: 'trending-down' as any,
      desc: 'Perder gordura e definir',
      color: '#EF4444',
    },
    {
      value: 'bulking',
      label: 'Ganho de Massa (Bulking)',
      icon: 'trending-up' as any,
      desc: 'Ganhar músculo e força',
      color: '#10B981',
    },
    {
      value: 'manutencao',
      label: 'Manutenção',
      icon: 'remove' as any,
      desc: 'Manter peso e melhorar performance',
      color: '#3B82F6',
    },
    {
      value: 'atleta',
      label: 'Atleta/Competição',
      icon: 'trophy' as any,
      desc: 'Performance máxima',
      color: '#F59E0B',
    },
  ];

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
            onPress={() => updateData({ goal: goal.value })}
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