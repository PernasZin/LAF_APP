/**
 * Premium Physical Data Step
 */
import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { Ruler, Scale } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

const GlassCard = ({ children, style, isDark }: any) => (
  <View style={[
    {
      backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
      borderWidth: 1,
      borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
      borderRadius: radius.xl,
      padding: spacing.lg,
    },
    style
  ]}>
    {children}
  </View>
);

const InputField = ({ icon: Icon, label, value, onChangeText, placeholder, unit, theme }: any) => (
  <View style={styles.inputGroup}>
    <View style={styles.labelRow}>
      <Icon size={18} color={premiumColors.primary} />
      <Text style={[styles.label, { color: theme.textSecondary }]}>{label}</Text>
    </View>
    <View style={styles.inputWrapper}>
      <TextInput
        style={[
          styles.input,
          {
            backgroundColor: theme.input.background,
            borderColor: theme.input.border,
            color: theme.text,
          }
        ]}
        placeholder={placeholder}
        placeholderTextColor={theme.input.placeholder}
        value={value}
        onChangeText={onChangeText}
        keyboardType="numeric"
      />
      {unit && (
        <View style={[styles.unitBadge, { backgroundColor: `${premiumColors.primary}15` }]}>
          <Text style={[styles.unitText, { color: premiumColors.primary }]}>{unit}</Text>
        </View>
      )}
    </View>
  </View>
);

export default function PhysicalDataStep({ formData, updateFormData, theme, isDark }: Props) {
  return (
    <View style={styles.container}>
      <GlassCard isDark={isDark} style={styles.card}>
        <InputField
          icon={Ruler}
          label="Altura"
          value={formData.height}
          onChangeText={(text: string) => updateFormData({ height: text })}
          placeholder="170"
          unit="cm"
          theme={theme}
        />

        <InputField
          icon={Scale}
          label="Peso Atual"
          value={formData.weight}
          onChangeText={(text: string) => updateFormData({ weight: text })}
          placeholder="70"
          unit="kg"
          theme={theme}
        />
      </GlassCard>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: spacing.lg },
  card: { marginBottom: spacing.lg },
  inputGroup: { marginBottom: spacing.lg },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  input: {
    flex: 1,
    height: 52,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    paddingHorizontal: spacing.base,
    fontSize: 16,
    fontWeight: '500',
  },
  unitBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
  },
  unitText: {
    fontSize: 14,
    fontWeight: '700',
  },
});
