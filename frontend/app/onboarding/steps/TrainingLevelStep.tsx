import React from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  data: any;
  updateData: (data: any) => void;
  language: SupportedLanguage;
}

export default function TrainingLevelStep({ data, updateData, language }: Props) {
  const t = translations[language].onboarding;
  
  const levels = [
    { value: 'iniciante', label: t.beginner, icon: 'star-outline' as any, desc: t.beginnerDesc },
    { value: 'intermediario', label: t.intermediate, icon: 'star-half-outline' as any, desc: t.intermediateDesc },
    { value: 'avancado', label: t.advanced, icon: 'star' as any, desc: t.advancedDesc },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t.trainingLevelTitle}</Text>
      <Text style={styles.description}>
        {t.trainingLevelDesc}
      </Text>

      {/* Nível */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.currentLevel}</Text>
        <View style={styles.levelContainer}>
          {levels.map((level) => (
            <TouchableOpacity
              key={level.value}
              style={[
                styles.levelCard,
                data.training_level === level.value && styles.levelCardActive,
              ]}
              onPress={() => updateData({ training_level: level.value })}
              activeOpacity={0.7}
            >
              <Ionicons
                name={level.icon}
                size={32}
                color={data.training_level === level.value ? '#10B981' : '#6B7280'}
              />
              <Text
                style={[
                  styles.levelLabel,
                  data.training_level === level.value && styles.levelLabelActive,
                ]}
              >
                {level.label}
              </Text>
              <Text style={styles.levelDesc}>{level.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Frequência */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.daysPerWeek}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.daysPlaceholder}
          value={data.weekly_training_frequency}
          onChangeText={(text) => updateData({ weekly_training_frequency: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {/* Tempo Disponível */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>{t.timePerSession}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.timePlaceholder}
          value={data.available_time_per_session}
          onChangeText={(text) => updateData({ available_time_per_session: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
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
  levelContainer: {
    gap: 12,
  },
  levelCard: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
    alignItems: 'center',
  },
  levelCardActive: {
    borderColor: '#10B981',
    backgroundColor: '#F0FDF4',
  },
  levelLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginTop: 8,
  },
  levelLabelActive: {
    color: '#10B981',
  },
  levelDesc: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 4,
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
});