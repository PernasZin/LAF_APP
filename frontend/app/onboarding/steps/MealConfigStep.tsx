/**
 * Premium Meal Config Step
 * Com suporte a i18n
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Utensils, Plus, Minus, Clock } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

export default function MealConfigStep({ formData, updateFormData, theme, isDark }: Props) {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const t = translations[language]?.onboarding || translations['pt-BR'].onboarding;
  const tMeals = translations[language]?.meals || translations['pt-BR'].meals;

  const MEAL_PRESETS: Record<number, { nameKey: string; time: string }[]> = {
    4: [
      { nameKey: 'breakfast', time: '07:00' },
      { nameKey: 'lunch', time: '12:00' },
      { nameKey: 'afternoonSnack', time: '16:00' },
      { nameKey: 'dinner', time: '20:00' },
    ],
    5: [
      { nameKey: 'breakfast', time: '07:00' },
      { nameKey: 'morningSnack', time: '10:00' },
      { nameKey: 'lunch', time: '12:30' },
      { nameKey: 'afternoonSnack', time: '16:00' },
      { nameKey: 'dinner', time: '19:30' },
    ],
    6: [
      { nameKey: 'breakfast', time: '07:00' },
      { nameKey: 'morningSnack', time: '10:00' },
      { nameKey: 'lunch', time: '12:30' },
      { nameKey: 'afternoonSnack', time: '16:00' },
      { nameKey: 'dinner', time: '19:30' },
      { nameKey: 'eveningSnack', time: '21:30' },
    ],
  };

  const getMealName = (nameKey: string): string => {
    const mealNames: Record<string, string> = {
      breakfast: tMeals.breakfast,
      morningSnack: tMeals.morningSnack,
      lunch: tMeals.lunch,
      afternoonSnack: tMeals.afternoonSnack,
      dinner: tMeals.dinner,
      eveningSnack: tMeals.eveningSnack,
    };
    return mealNames[nameKey] || nameKey;
  };

  const mealCount = formData.meal_count || 5;
  const meals = MEAL_PRESETS[mealCount] || MEAL_PRESETS[5];

  const handleMealCountChange = (delta: number) => {
    const newCount = Math.max(4, Math.min(6, mealCount + delta));
    const newMeals = MEAL_PRESETS[newCount];
    updateFormData({
      meal_count: newCount,
      meal_times: newMeals.map(m => m.time),
    });
  };

  return (
    <View style={styles.container}>
      {/* Meal Count Selector */}
      <View style={[
        styles.countCard,
        {
          backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.9)',
          borderColor: theme.border,
        }
      ]}>
        <View style={styles.countHeader}>
          <Utensils size={20} color={premiumColors.primary} />
          <Text style={[styles.countLabel, { color: theme.text }]}>{t.mealsPerDay}</Text>
        </View>
        
        <View style={styles.countControls}>
          <TouchableOpacity
            style={[
              styles.countButton,
              { backgroundColor: theme.input.background, borderColor: theme.border }
            ]}
            onPress={() => handleMealCountChange(-1)}
            disabled={mealCount <= 4}
          >
            <Minus size={20} color={mealCount <= 4 ? theme.textTertiary : theme.text} />
          </TouchableOpacity>
          
          <View style={[styles.countDisplay, { backgroundColor: `${premiumColors.primary}15` }]}>
            <Text style={[styles.countNumber, { color: premiumColors.primary }]}>{mealCount}</Text>
          </View>
          
          <TouchableOpacity
            style={[
              styles.countButton,
              { backgroundColor: theme.input.background, borderColor: theme.border }
            ]}
            onPress={() => handleMealCountChange(1)}
            disabled={mealCount >= 6}
          >
            <Plus size={20} color={mealCount >= 6 ? theme.textTertiary : theme.text} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Meals Preview */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>{t.distribution}</Text>
      <View style={styles.mealsContainer}>
        {meals.map((meal, index) => (
          <View
            key={index}
            style={[
              styles.mealItem,
              {
                backgroundColor: isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)',
                borderColor: theme.border,
              }
            ]}
          >
            <View style={[styles.mealNumber, { backgroundColor: `${premiumColors.primary}20` }]}>
              <Text style={[styles.mealNumberText, { color: premiumColors.primary }]}>{index + 1}</Text>
            </View>
            <Text style={[styles.mealName, { color: theme.text }]}>{getMealName(meal.nameKey)}</Text>
            <View style={styles.mealTime}>
              <Clock size={14} color={theme.textTertiary} />
              <Text style={[styles.mealTimeText, { color: theme.textTertiary }]}>{meal.time}</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: spacing.lg },
  countCard: {
    padding: spacing.lg,
    borderRadius: radius.xl,
    borderWidth: 1,
    marginBottom: spacing.xl,
  },
  countHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  countLabel: {
    fontSize: 16,
    fontWeight: '600',
  },
  countControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.lg,
  },
  countButton: {
    width: 48,
    height: 48,
    borderRadius: radius.lg,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  countDisplay: {
    width: 72,
    height: 72,
    borderRadius: radius.xl,
    alignItems: 'center',
    justifyContent: 'center',
  },
  countNumber: {
    fontSize: 32,
    fontWeight: '800',
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: spacing.md,
  },
  mealsContainer: {
    gap: spacing.sm,
  },
  mealItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1,
    gap: spacing.md,
  },
  mealNumber: {
    width: 28,
    height: 28,
    borderRadius: radius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mealNumberText: {
    fontSize: 13,
    fontWeight: '700',
  },
  mealName: {
    flex: 1,
    fontSize: 15,
    fontWeight: '600',
  },
  mealTime: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  mealTimeText: {
    fontSize: 13,
    fontWeight: '500',
  },
});
