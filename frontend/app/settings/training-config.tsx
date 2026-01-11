/**
 * LAF Premium Training Config Screen
 * ===================================
 * Configurações de frequência e tempo de treino
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Check, Calendar, Clock, Dumbbell } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const GlassCard = ({ children, style, isDark }: any) => {
  const cardStyle = {
    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
    borderWidth: 1,
    borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
    borderRadius: radius.xl,
    overflow: 'hidden' as const,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: isDark ? 0.3 : 0.08,
    shadowRadius: 16,
    elevation: 8,
  };
  return <View style={[cardStyle, style]}>{children}</View>;
};

// Frequências de treino
const FREQUENCIES = [
  { value: 2, label: '2x por semana', desc: 'Full Body' },
  { value: 3, label: '3x por semana', desc: 'ABC' },
  { value: 4, label: '4x por semana', desc: 'ABCD' },
  { value: 5, label: '5x por semana', desc: 'ABCDE' },
  { value: 6, label: '6x por semana', desc: 'PPL 2x' },
];

// Tempo de treino
const DURATIONS = [
  { value: 30, label: '30 minutos', desc: 'Treino rápido' },
  { value: 60, label: '1 hora', desc: 'Treino padrão' },
  { value: 90, label: '1h 30min', desc: 'Treino completo' },
  { value: 120, label: '2 horas', desc: 'Treino extenso' },
];

// Níveis de treino
const LEVELS = [
  { value: 'novato', label: '🆕 Novato', desc: 'Nunca treinei' },
  { value: 'iniciante', label: '🌱 Iniciante', desc: '0-1 anos de academia' },
  { value: 'intermediario', label: '💪 Intermediário', desc: '1-2 anos de academia' },
  { value: 'avancado', label: '🏆 Avançado', desc: '3+ anos de academia' },
];

export default function TrainingConfigScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  const [frequency, setFrequency] = useState(3);
  const [duration, setDuration] = useState(60);
  const [level, setLevel] = useState('intermediario');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        const response = await fetch(`${BACKEND_URL}/api/user/profile/${id}`);
        if (response.ok) {
          const data = await response.json();
          setFrequency(data.weekly_training_frequency || 3);
          // O backend usa available_time_per_session, mas também pode vir como training_duration
          setDuration(data.available_time_per_session || data.training_duration || 60);
          setLevel(data.training_level || 'intermediario');
        }
      }
    } catch (error) {
      console.error('Error loading config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!userId) return;
    setSaving(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/user/profile/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weekly_training_frequency: frequency,
          training_duration: duration,
          training_level: level,
        }),
      });

      if (response.ok) {
        Alert.alert(
          'Sucesso!', 
          'Configurações salvas! Gere um novo treino para aplicar as mudanças.',
          [{ text: 'OK', onPress: () => router.back() }]
        );
      } else {
        Alert.alert('Erro', 'Não foi possível salvar');
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <View style={styles.loadingContainer}>
          <Text style={{ color: theme.text }}>Carregando...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
              <ArrowLeft size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.headerTitle, { color: theme.text }]}>Configurar Treino</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Nível de Treino */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <View style={styles.sectionHeader}>
              <Dumbbell size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>Nível de Experiência</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.card}>
              {LEVELS.map((item, index) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.optionItem,
                    { borderBottomColor: theme.border },
                    index === LEVELS.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => setLevel(item.value)}
                >
                  <View style={styles.optionContent}>
                    <Text style={[styles.optionLabel, { color: theme.text }]}>{item.label}</Text>
                    <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{item.desc}</Text>
                  </View>
                  <View style={[
                    styles.radioOuter,
                    { borderColor: level === item.value ? premiumColors.primary : theme.border }
                  ]}>
                    {level === item.value && (
                      <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </GlassCard>
            
            {level === 'novato' && (
              <View style={[styles.infoBox, { backgroundColor: premiumColors.primary + '15' }]}>
                <Text style={[styles.infoText, { color: premiumColors.primary }]}>
                  💡 Novatos começam com treino de adaptação por 4-8 semanas. Após 30 treinos concluídos, você receberá treinos para hipertrofia!
                </Text>
              </View>
            )}
          </Animated.View>

          {/* Frequência */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <View style={styles.sectionHeader}>
              <Calendar size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>Frequência Semanal</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.card}>
              {FREQUENCIES.map((item, index) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.optionItem,
                    { borderBottomColor: theme.border },
                    index === FREQUENCIES.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => setFrequency(item.value)}
                >
                  <View style={styles.optionContent}>
                    <Text style={[styles.optionLabel, { color: theme.text }]}>{item.label}</Text>
                    <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{item.desc}</Text>
                  </View>
                  <View style={[
                    styles.radioOuter,
                    { borderColor: frequency === item.value ? premiumColors.primary : theme.border }
                  ]}>
                    {frequency === item.value && (
                      <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </GlassCard>
          </Animated.View>

          {/* Duração */}
          <Animated.View entering={FadeInDown.delay(300).springify()}>
            <View style={styles.sectionHeader}>
              <Clock size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>Tempo Disponível</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.card}>
              {DURATIONS.map((item, index) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.optionItem,
                    { borderBottomColor: theme.border },
                    index === DURATIONS.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => setDuration(item.value)}
                >
                  <View style={styles.optionContent}>
                    <Text style={[styles.optionLabel, { color: theme.text }]}>{item.label}</Text>
                    <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{item.desc}</Text>
                  </View>
                  <View style={[
                    styles.radioOuter,
                    { borderColor: duration === item.value ? premiumColors.primary : theme.border }
                  ]}>
                    {duration === item.value && (
                      <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </GlassCard>
          </Animated.View>

          {/* Save Button */}
          <Animated.View entering={FadeInDown.delay(400).springify()} style={styles.saveContainer}>
            <TouchableOpacity onPress={handleSave} disabled={saving} activeOpacity={0.9}>
              <LinearGradient
                colors={saving
                  ? ['#9CA3AF', '#6B7280']
                  : [premiumColors.gradient.start, premiumColors.gradient.end]
                }
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.saveButton}
              >
                <Check size={20} color="#FFF" />
                <Text style={styles.saveButtonText}>
                  {saving ? 'Salvando...' : 'Salvar Configurações'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>

          <View style={{ height: 40 }} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700' },

  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  sectionTitle: { fontSize: 16, fontWeight: '700' },

  card: { padding: spacing.base, marginBottom: spacing.sm },

  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  optionContent: { flex: 1 },
  optionLabel: { fontSize: 16, fontWeight: '600' },
  optionDesc: { fontSize: 13, marginTop: 2 },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  radioInner: { width: 12, height: 12, borderRadius: 6 },

  infoBox: {
    padding: spacing.md,
    borderRadius: radius.lg,
    marginTop: spacing.sm,
  },
  infoText: { fontSize: 13, lineHeight: 18 },

  saveContainer: { marginTop: spacing.xl },
  saveButton: {
    height: 56,
    borderRadius: radius.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  saveButtonText: { color: '#FFF', fontSize: 17, fontWeight: '700' },
});
