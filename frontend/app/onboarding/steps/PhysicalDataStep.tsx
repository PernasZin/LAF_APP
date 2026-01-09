import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  data: any;
  updateData: (data: any) => void;
  language: SupportedLanguage;
}

export default function PhysicalDataStep({ data, updateData, language }: Props) {
  const t = translations[language].onboarding;
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t.physicalDataTitle}</Text>
      <Text style={styles.description}>
        {t.physicalDataDesc}
      </Text>

      {/* Altura */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.height}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.heightPlaceholder}
          value={data.height}
          onChangeText={(text) => updateData({ height: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {/* Peso Atual */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.currentWeight}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.currentWeightPlaceholder}
          value={data.weight}
          onChangeText={(text) => updateData({ weight: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {/* Peso Meta */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.targetWeight}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.targetWeightPlaceholder}
          value={data.target_weight}
          onChangeText={(text) => updateData({ target_weight: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {/* Percentual de Gordura */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.bodyFatPercentage}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.bodyFatPlaceholder}
          value={data.body_fat_percentage}
          onChangeText={(text) => updateData({ body_fat_percentage: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
        <Text style={styles.hint}>
          {t.bodyFatHint}
        </Text>
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
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F9FAFB',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#000000',
  },
  hint: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 4,
  },
});