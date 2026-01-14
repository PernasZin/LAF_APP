/**
 * LAF Premium Cardio Screen
 * ==========================
 * Glassmorphism + Gradientes + Animações
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  RefreshControl
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import Animated, { FadeInDown } from 'react-native-reanimated';
import {
  Activity, Flame, Clock, Footprints, Heart,
  Calendar, TrendingUp, Zap, Bike, ArrowUpDown
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { CardioSkeleton } from '../../components';
import { useTranslation } from '../../i18n';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

// Glass Card Component
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

// Cardio Exercise Card - Ícones específicos para cada tipo
const CardioExerciseCard = ({ exercise, index, isDark, theme, language, t }: any) => {
  const intensityColors: any = {
    light: '#10B981',
    moderate: '#F59E0B', 
    high: '#EF4444',
  };
  
  const intensityLabels: any = {
    light: { pt: 'Leve', en: 'Light', es: 'Ligero' },
    moderate: { pt: 'Moderado', en: 'Moderate', es: 'Moderado' },
    high: { pt: 'Intenso', en: 'High', es: 'Intenso' },
  };
  
  // Determina o ícone baseado no nome do exercício
  const getExerciseIcon = (name: string) => {
    const nameLower = name.toLowerCase();
    if (nameLower.includes('caminhada') || nameLower.includes('walking')) {
      return Footprints;
    } else if (nameLower.includes('bicicleta') || nameLower.includes('bike') || nameLower.includes('cycling')) {
      return Bike;
    } else if (nameLower.includes('escada') || nameLower.includes('stair')) {
      return ArrowUpDown;
    }
    return Activity;
  };
  
  const color = intensityColors[exercise.intensity] || '#F59E0B';
  const intensityLabel = intensityLabels[exercise.intensity]?.[language === 'en-US' ? 'en' : language === 'es-ES' ? 'es' : 'pt'] || 'Moderado';
  
  // Nome traduzido
  const name = language === 'en-US' ? exercise.name_en : language === 'es-ES' ? exercise.name_es : exercise.name;
  
  const IconComponent = getExerciseIcon(exercise.name);

  return (
    <Animated.View entering={FadeInDown.delay(index * 100).springify()}>
      <GlassCard isDark={isDark} style={styles.sessionCard}>
        <View style={styles.sessionHeader}>
          <View style={[styles.sessionIconBg, { backgroundColor: color + '20' }]}>
            <IconComponent size={22} color={color} strokeWidth={2.5} />
          </View>
          <View style={styles.sessionInfo}>
            <Text style={[styles.sessionType, { color: theme.text }]}>{name}</Text>
            <Text style={[styles.sessionDay, { color: theme.textTertiary }]}>
              {exercise.sessions_per_week}x {t.cardio.perWeek}
            </Text>
          </View>
          <View style={[styles.sessionBadge, { backgroundColor: color + '15' }]}>
            <Text style={[styles.sessionBadgeText, { color: color }]}>
              {intensityLabel}
            </Text>
          </View>
        </View>

        <View style={styles.sessionStats}>
          <View style={styles.sessionStat}>
            <Clock size={16} color={theme.textTertiary} />
            <Text style={[styles.sessionStatValue, { color: theme.text }]}>
              {exercise.duration_minutes} min
            </Text>
          </View>
          <View style={styles.sessionStat}>
            <Flame size={16} color="#EF4444" />
            <Text style={[styles.sessionStatValue, { color: theme.text }]}>
              {exercise.calories_burned} kcal
            </Text>
          </View>
          {exercise.heart_rate_zone && (
            <View style={styles.sessionStat}>
              <Heart size={16} color="#EC4899" />
              <Text style={[styles.sessionStatValue, { color: theme.text, fontSize: 11 }]}>
                {exercise.heart_rate_zone.split(' ')[0]}
              </Text>
            </View>
          )}
        </View>

        {/* Descrição de como se sentir */}
        {exercise.how_to_feel && (
          <Text style={[styles.sessionNotes, { color: theme.textSecondary }]}>
            💡 {language === 'en-US' ? exercise.how_to_feel_en : language === 'es-ES' ? exercise.how_to_feel_es : exercise.how_to_feel}
          </Text>
        )}
        
        {/* Substitutos */}
        {exercise.substitutes_detailed?.length > 0 && (
          <View style={styles.substitutesSection}>
            <Text style={[styles.substitutesTitle, { color: theme.textTertiary }]}>
              {t.cardio.substitutes}:
            </Text>
            <View style={styles.substitutesList}>
              {exercise.substitutes_detailed.map((sub: any, i: number) => (
                <View key={i} style={[styles.substituteChip, { backgroundColor: isDark ? 'rgba(51, 65, 85, 0.5)' : 'rgba(241, 245, 249, 0.8)' }]}>
                  <Text style={[styles.substituteText, { color: theme.text }]}>
                    {language === 'en-US' ? sub.name_en : language === 'es-ES' ? sub.name_es : sub.name}
                  </Text>
                  <Text style={[styles.substituteTime, { color: theme.textTertiary }]}>
                    {sub.equivalent_duration}min
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </GlassCard>
    </Animated.View>
  );
};

export default function CardioScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const language = useSettingsStore((state) => state.language);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [cardioData, setCardioData] = useState<any>(null);

  useFocusEffect(
    useCallback(() => {
      loadCardio();
    }, [])
  );

  const loadCardio = async () => {
    try {
      setLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        const response = await safeFetch(`${BACKEND_URL}/api/cardio/${id}`);
        if (response.ok) {
          const data = await response.json();
          setCardioData(data);
        }
      }
    } catch (error) {
      console.error('Error loading cardio:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCardio();
    setRefreshing(false);
  };

  // Usa weekly_summary do backend
  const totalMinutes = cardioData?.weekly_summary?.total_duration_minutes || 0;
  const totalCalories = cardioData?.weekly_summary?.total_calories_burned || 0;
  const totalSessions = cardioData?.weekly_summary?.total_sessions || 0;
  
  // Tradução do objetivo
  const goalLabels: any = {
    cutting: { pt: 'Cutting', en: 'Cutting', es: 'Definición' },
    bulking: { pt: 'Bulking', en: 'Bulking', es: 'Volumen' },
    manutencao: { pt: 'Manutenção', en: 'Maintenance', es: 'Mantenimiento' },
  };
  const goalLabel = goalLabels[cardioData?.goal]?.[language === 'en-US' ? 'en' : language === 'es-ES' ? 'es' : 'pt'] || 'Manutenção';

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <CardioSkeleton />
      </SafeAreaView>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']
        }
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={premiumColors.primary} />
          }
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <View>
              <Text style={[styles.headerTitle, { color: theme.text }]}>{t.cardio.title}</Text>
              <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
                {totalSessions} {t.cardio.sessionsPerWeek} • {goalLabel}
              </Text>
            </View>
          </Animated.View>

          {/* Summary Card */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <GlassCard isDark={isDark} style={styles.summaryCard}>
              <LinearGradient
                colors={[premiumColors.gradient.start + '10', premiumColors.gradient.end + '10']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={StyleSheet.absoluteFill}
              />
              <View style={styles.summaryStats}>
                <View style={styles.summaryStat}>
                  <Clock size={24} color={premiumColors.primary} />
                  <Text style={[styles.summaryValue, { color: theme.text }]}>{totalMinutes}</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>{t.cardio.minPerWeek}</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Flame size={24} color="#EF4444" />
                  <Text style={[styles.summaryValue, { color: theme.text }]}>{totalCalories}</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>{t.cardio.kcalPerWeek}</Text>
                </View>
              </View>
            </GlassCard>
          </Animated.View>
          
          {/* Dica do cardio */}
          {cardioData?.tips && (
            <Animated.View entering={FadeInDown.delay(150).springify()}>
              <GlassCard isDark={isDark} style={styles.tipCard}>
                <Text style={[styles.tipText, { color: theme.text }]}>
                  💡 {language === 'en-US' ? cardioData.tips.en : language === 'es-ES' ? cardioData.tips.es : cardioData.tips.pt}
                </Text>
              </GlassCard>
            </Animated.View>
          )}

          {/* Exercises */}
          <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.cardio.yourExercises}</Text>
          {cardioData?.exercises?.map((exercise: any, index: number) => (
            <CardioExerciseCard
              key={index}
              exercise={exercise}
              index={index}
              isDark={isDark}
              theme={theme}
              language={language}
            />
          ))}

          {(!cardioData?.exercises || cardioData.exercises.length === 0) && (
            <GlassCard isDark={isDark} style={styles.emptyCard}>
              <Activity size={48} color={theme.textTertiary} />
              <Text style={[styles.emptyText, { color: theme.textSecondary }]}>
                {t.workout.noData}
              </Text>
            </GlassCard>
          )}

          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg, gap: spacing.lg },

  header: { marginBottom: spacing.sm },
  headerTitle: { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  headerSubtitle: { fontSize: 14, marginTop: 4 },

  summaryCard: { padding: spacing.lg },
  summaryStats: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around' },
  summaryStat: { alignItems: 'center', gap: spacing.xs },
  summaryValue: { fontSize: 32, fontWeight: '800', letterSpacing: -1 },
  summaryLabel: { fontSize: 12, fontWeight: '600' },
  summaryDivider: { width: 1, height: 60 },

  sectionTitle: { fontSize: 18, fontWeight: '700', marginTop: spacing.md },

  sessionCard: { padding: spacing.base, marginBottom: spacing.md },
  sessionHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.md },
  sessionIconBg: { width: 44, height: 44, borderRadius: radius.lg, alignItems: 'center', justifyContent: 'center' },
  sessionInfo: { flex: 1 },
  sessionType: { fontSize: 16, fontWeight: '700' },
  sessionDay: { fontSize: 13, marginTop: 2 },
  sessionBadge: { paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.full },
  sessionBadgeText: { fontSize: 12, fontWeight: '700' },
  sessionStats: { flexDirection: 'row', gap: spacing.xl },
  sessionStat: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs },
  sessionStatValue: { fontSize: 14, fontWeight: '600' },
  sessionNotes: { fontSize: 13, marginTop: spacing.md, fontStyle: 'italic', lineHeight: 18 },

  // Substitutes
  substitutesSection: { marginTop: spacing.md, paddingTop: spacing.md, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.1)' },
  substitutesTitle: { fontSize: 12, fontWeight: '600', marginBottom: spacing.sm },
  substitutesList: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs },
  substituteChip: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: radius.md, gap: 4 },
  substituteText: { fontSize: 11, fontWeight: '500' },
  substituteTime: { fontSize: 10 },

  // Tip Card
  tipCard: { padding: spacing.md },
  tipText: { fontSize: 13, lineHeight: 18 },

  emptyCard: { padding: spacing.xl, alignItems: 'center', gap: spacing.md },
  emptyText: { fontSize: 14, textAlign: 'center' },
});
