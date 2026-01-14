/**
 * Premium Goal Step
 * Com suporte a i18n
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { TrendingDown, Scale, TrendingUp, Check } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

export default function GoalStep({ formData, updateFormData, theme, isDark }: Props) {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const t = translations[language]?.onboarding || translations['pt-BR'].onboarding;

  const GOALS = [
    {
      value: 'cutting',
      label: t.cutting,
      desc: t.cuttingDesc,
      icon: TrendingDown,
      color: '#EF4444',
      gradient: ['#EF4444', '#F97316'],
    },
    {
      value: 'manutencao',
      label: t.maintenance,
      desc: t.maintenanceDesc,
      icon: Scale,
      color: '#10B981',
      gradient: ['#10B981', '#14B8A6'],
    },
    {
      value: 'bulking',
      label: t.bulking,
      desc: t.bulkingDesc,
      icon: TrendingUp,
      color: '#3B82F6',
      gradient: ['#3B82F6', '#8B5CF6'],
    },
  ];

  return (
    <View style={styles.container}>
      <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
        {t.goalDesc}
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
