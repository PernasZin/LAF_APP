/**
 * Premium Restrictions Step
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { Check, Leaf, Milk, Wheat, Egg, AlertTriangle, Activity } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

const RESTRICTIONS = [
  { value: 'vegetariano', label: 'Vegetariano', icon: Leaf, color: '#22C55E' },
  { value: 'vegano', label: 'Vegano', icon: Leaf, color: '#10B981' },
  { value: 'sem_lactose', label: 'Sem Lactose', icon: Milk, color: '#3B82F6' },
  { value: 'sem_gluten', label: 'Sem Glúten', icon: Wheat, color: '#F59E0B' },
  { value: 'diabetico', label: 'Diabético', icon: Activity, color: '#8B5CF6' },
  { value: 'sem_ovo', label: 'Sem Ovos', icon: Egg, color: '#EAB308' },
  { value: 'sem_amendoim', label: 'Sem Amendoim', icon: AlertTriangle, color: '#EF4444' },
];

const PREFERENCES = [
  { value: 'low_carb', label: 'Low Carb' },
  { value: 'high_protein', label: 'Alta Proteína' },
  { value: 'mediterranean', label: 'Mediterrânea' },
  { value: 'whole_foods', label: 'Comida Real' },
];

export default function RestrictionsStep({ formData, updateFormData, theme, isDark }: Props) {
  const toggleRestriction = (value: string) => {
    const current = formData.dietary_restrictions || [];
    const updated = current.includes(value)
      ? current.filter((r: string) => r !== value)
      : [...current, value];
    updateFormData({ dietary_restrictions: updated });
  };

  const togglePreference = (value: string) => {
    const current = formData.food_preferences || [];
    const updated = current.includes(value)
      ? current.filter((p: string) => p !== value)
      : [...current, value];
    updateFormData({ food_preferences: updated });
  };

  return (
    <View style={styles.container}>
      {/* Restrictions */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>Restrições Alimentares</Text>
      <Text style={[styles.sectionDesc, { color: theme.textTertiary }]}>
        Selecione suas restrições (opcional)
      </Text>
      
      <View style={styles.restrictionsGrid}>
        {RESTRICTIONS.map((item) => {
          const isSelected = formData.dietary_restrictions?.includes(item.value);
          const Icon = item.icon;
          
          return (
            <TouchableOpacity
              key={item.value}
              style={[
                styles.restrictionChip,
                {
                  backgroundColor: isSelected
                    ? `${item.color}15`
                    : isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)',
                  borderColor: isSelected ? item.color : theme.border,
                }
              ]}
              onPress={() => toggleRestriction(item.value)}
            >
              <Icon size={18} color={isSelected ? item.color : theme.textTertiary} />
              <Text style={[
                styles.restrictionLabel,
                { color: isSelected ? item.color : theme.text }
              ]}>
                {item.label}
              </Text>
              {isSelected && (
                <View style={[styles.checkMark, { backgroundColor: item.color }]}>
                  <Check size={12} color="#FFF" strokeWidth={3} />
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Preferences */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary, marginTop: spacing.xl }]}>
        Preferências
      </Text>
      <Text style={[styles.sectionDesc, { color: theme.textTertiary }]}>
        Estilo de alimentação preferido (opcional)
      </Text>
      
      <View style={styles.preferencesRow}>
        {PREFERENCES.map((item) => {
          const isSelected = formData.food_preferences?.includes(item.value);
          
          return (
            <TouchableOpacity
              key={item.value}
              style={[
                styles.preferenceChip,
                {
                  backgroundColor: isSelected
                    ? premiumColors.primary
                    : isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)',
                  borderColor: isSelected ? premiumColors.primary : theme.border,
                }
              ]}
              onPress={() => togglePreference(item.value)}
            >
              <Text style={[
                styles.preferenceLabel,
                { color: isSelected ? '#FFF' : theme.text }
              ]}>
                {item.label}
              </Text>
            </TouchableOpacity>
          );
        })}
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
    marginBottom: spacing.xs,
  },
  sectionDesc: {
    fontSize: 14,
    marginBottom: spacing.md,
  },
  restrictionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  restrictionChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    gap: spacing.xs,
  },
  restrictionLabel: {
    fontSize: 13,
    fontWeight: '600',
  },
  checkMark: {
    width: 18,
    height: 18,
    borderRadius: radius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 2,
  },
  preferencesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  preferenceChip: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1.5,
  },
  preferenceLabel: {
    fontSize: 13,
    fontWeight: '600',
  },
});
