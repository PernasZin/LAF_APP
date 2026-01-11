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
  Calendar, TrendingUp, Zap
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

// Cardio Session Card
const CardioSessionCard = ({ session, index, isDark, theme }: any) => {
  const typeConfig: any = {
    walking: { icon: Footprints, color: '#10B981', label: 'Caminhada' },
    running: { icon: Activity, color: '#EF4444', label: 'Corrida' },
    cycling: { icon: Activity, color: '#3B82F6', label: 'Ciclismo' },
    hiit: { icon: Zap, color: '#F59E0B', label: 'HIIT' },
    swimming: { icon: Activity, color: '#06B6D4', label: 'Natação' },
  };

  const config = typeConfig[session.type] || typeConfig.walking;
  const IconComponent = config.icon;

  return (
    <Animated.View entering={FadeInDown.delay(index * 100).springify()}>
      <GlassCard isDark={isDark} style={styles.sessionCard}>
        <View style={styles.sessionHeader}>
          <View style={[styles.sessionIconBg, { backgroundColor: config.color + '20' }]}>
            <IconComponent size={22} color={config.color} strokeWidth={2.5} />
          </View>
          <View style={styles.sessionInfo}>
            <Text style={[styles.sessionType, { color: theme.text }]}>{config.label}</Text>
            <Text style={[styles.sessionDay, { color: theme.textTertiary }]}>
              {session.day || `Dia ${index + 1}`}
            </Text>
          </View>
          <View style={[styles.sessionBadge, { backgroundColor: config.color + '15' }]}>
            <Text style={[styles.sessionBadgeText, { color: config.color }]}>
              {session.intensity || 'Moderado'}
            </Text>
          </View>
        </View>

        <View style={styles.sessionStats}>
          <View style={styles.sessionStat}>
            <Clock size={16} color={theme.textTertiary} />
            <Text style={[styles.sessionStatValue, { color: theme.text }]}>
              {session.duration || 30} min
            </Text>
          </View>
          <View style={styles.sessionStat}>
            <Flame size={16} color="#EF4444" />
            <Text style={[styles.sessionStatValue, { color: theme.text }]}>
              {session.calories || 200} kcal
            </Text>
          </View>
          {session.heart_rate && (
            <View style={styles.sessionStat}>
              <Heart size={16} color="#EC4899" />
              <Text style={[styles.sessionStatValue, { color: theme.text }]}>
                {session.heart_rate} bpm
              </Text>
            </View>
          )}
        </View>

        {session.notes && (
          <Text style={[styles.sessionNotes, { color: theme.textSecondary }]}>
            {session.notes}
          </Text>
        )}
      </GlassCard>
    </Animated.View>
  );
};

export default function CardioScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
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

  const totalMinutes = cardioData?.sessions?.reduce((sum: number, s: any) => sum + (s.duration || 0), 0) || 0;
  const totalCalories = cardioData?.sessions?.reduce((sum: number, s: any) => sum + (s.calories || 0), 0) || 0;

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
              <Text style={[styles.headerTitle, { color: theme.text }]}>Cardio</Text>
              <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
                {cardioData?.sessions?.length || 0} sessões por semana
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
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>min/semana</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Flame size={24} color="#EF4444" />
                  <Text style={[styles.summaryValue, { color: theme.text }]}>{totalCalories}</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>kcal/semana</Text>
                </View>
              </View>
            </GlassCard>
          </Animated.View>

          {/* Sessions */}
          <Text style={[styles.sectionTitle, { color: theme.text }]}>Suas Sessões</Text>
          {cardioData?.sessions?.map((session: any, index: number) => (
            <CardioSessionCard
              key={index}
              session={session}
              index={index}
              isDark={isDark}
              theme={theme}
            />
          ))}

          {(!cardioData?.sessions || cardioData.sessions.length === 0) && (
            <GlassCard isDark={isDark} style={styles.emptyCard}>
              <Activity size={48} color={theme.textTertiary} />
              <Text style={[styles.emptyText, { color: theme.textSecondary }]}>
                Nenhuma sessão de cardio planejada
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
  sessionNotes: { fontSize: 13, marginTop: spacing.md, fontStyle: 'italic' },

  emptyCard: { padding: spacing.xl, alignItems: 'center', gap: spacing.md },
  emptyText: { fontSize: 14, textAlign: 'center' },
});
