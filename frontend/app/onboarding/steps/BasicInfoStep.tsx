/**
 * Premium Basic Info Step
 * Com suporte a i18n
 */
import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { User, Calendar, Users } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

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

export default function BasicInfoStep({ formData, updateFormData, theme, isDark }: Props) {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  const t = translations[language]?.onboarding || translations['pt-BR'].onboarding;
  
  const sexOptions = [
    { value: 'masculino', label: t.male, icon: '♂️' },
    { value: 'feminino', label: t.female, icon: '♀️' },
  ];

  return (
    <View style={styles.container}>
      <GlassCard isDark={isDark} style={styles.card}>
        <View style={styles.inputGroup}>
          <View style={styles.labelRow}>
            <User size={18} color={premiumColors.primary} />
            <Text style={[styles.label, { color: theme.textSecondary }]}>{t.name}</Text>
          </View>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: theme.input.background,
                borderColor: theme.input.border,
                color: theme.text,
              }
            ]}
            placeholder={t.yourName}
            placeholderTextColor={theme.input.placeholder}
            value={formData.name}
            onChangeText={(text) => updateFormData({ name: text })}
          />
        </View>

        <View style={styles.inputGroup}>
          <View style={styles.labelRow}>
            <Calendar size={18} color={premiumColors.primary} />
            <Text style={[styles.label, { color: theme.textSecondary }]}>{t.age}</Text>
          </View>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: theme.input.background,
                borderColor: theme.input.border,
                color: theme.text,
              }
            ]}
            placeholder="25"
            placeholderTextColor={theme.input.placeholder}
            value={formData.age}
            onChangeText={(text) => updateFormData({ age: text })}
            keyboardType="numeric"
          />
        </View>

        <View style={styles.inputGroup}>
          <View style={styles.labelRow}>
            <Users size={18} color={premiumColors.primary} />
            <Text style={[styles.label, { color: theme.textSecondary }]}>{t.sex}</Text>
          </View>
          <View style={styles.optionsRow}>
            {sexOptions.map((option) => {
              const isSelected = formData.sex === option.value;
              return (
                <TouchableOpacity
                  key={option.value}
                  style={[
                    styles.optionButton,
                    {
                      backgroundColor: isSelected
                        ? `${premiumColors.primary}20`
                        : theme.input.background,
                      borderColor: isSelected
                        ? premiumColors.primary
                        : theme.input.border,
                    }
                  ]}
                  onPress={() => updateFormData({ sex: option.value })}
                >
                  <Text style={styles.optionIcon}>{option.icon}</Text>
                  <Text style={[
                    styles.optionLabel,
                    { color: isSelected ? premiumColors.primary : theme.text }
                  ]}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>
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
  input: {
    height: 52,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    paddingHorizontal: spacing.base,
    fontSize: 16,
    fontWeight: '500',
  },
  optionsRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  optionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 52,
    borderRadius: radius.lg,
    borderWidth: 2,
    gap: spacing.sm,
  },
  optionIcon: { fontSize: 20 },
  optionLabel: {
    fontSize: 15,
    fontWeight: '600',
  },
});
