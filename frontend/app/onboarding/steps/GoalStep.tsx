/**
 * Premium Goal Step
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { TrendingDown, Scale, TrendingUp, Check } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

const GOALS = [
  {
    value: 'cutting',
    label: 'Emagrecimento',
    desc: 'Perder gordura mantendo massa muscular',
    icon: TrendingDown,
    color: '#EF4444',
    gradient: ['#EF4444', '#F97316'],
  },
  {
    value: 'manutencao',
    label: 'Manutenção',
    desc: 'Manter peso e melhorar composição',
    icon: Scale,
    color: '#10B981',
    gradient: ['#10B981', '#14B8A6'],
  },
  {
    value: 'bulking',
    label: 'Ganho de Massa',
    desc: 'Aumentar massa muscular',
    icon: TrendingUp,
    color: '#3B82F6',
    gradient: ['#3B82F6', '#8B5CF6'],
  },
];

export default function GoalStep({ formData, updateFormData, theme, isDark }: Props) {
  return (
    <View style={styles.container}>
      <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
        Escolha seu objetivo principal
      </Text>
      
      <View style={styles.goalsContainer}>
        {GOALS.map((goal) => {
          const isSelected = formData.goal === goal.value;
          const Icon = goal.icon;
          
          return (
            <TouchableOpacity
              key={goal.value}
              style={[
                styles.goalCard,
                {
                  backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.9)',
                  borderColor: isSelected ? goal.color : theme.border,
                  borderWidth: isSelected ? 2 : 1,
                }
              ]}
              onPress={() => updateFormData({ goal: goal.value })}
              activeOpacity={0.8}
            >
              <View style={styles.goalContent}>
                <LinearGradient
                  colors={goal.gradient as [string, string]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.goalIconContainer}
                >
                  <Icon size={28} color="#FFF" strokeWidth={2.5} />
                </LinearGradient>
                
                <View style={styles.goalText}>
                  <Text style={[styles.goalLabel, { color: theme.text }]}>
                    {goal.label}
                  </Text>
                  <Text style={[styles.goalDesc, { color: theme.textTertiary }]}>
                    {goal.desc}
                  </Text>
                </View>
              </View>
              
              {isSelected && (
                <View style={[styles.checkBadge, { backgroundColor: goal.color }]}>
                  <Check size={16} color="#FFF" strokeWidth={3} />
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: spacing.lg },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  goalsContainer: {
    gap: spacing.md,
  },
  goalCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.lg,
    borderRadius: radius.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 4,
  },
  goalContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  goalIconContainer: {
    width: 56,
    height: 56,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.base,
  },
  goalText: {
    flex: 1,
  },
  goalLabel: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
    letterSpacing: -0.3,
  },
  goalDesc: {
    fontSize: 13,
    lineHeight: 18,
  },
  checkBadge: {
    width: 28,
    height: 28,
    borderRadius: radius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
