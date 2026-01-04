import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';
import { HomeSkeleton } from '../../components';
import { useHaptics } from '../../hooks/useHaptics';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Safe fetch with timeout - prevents blocking UI on iOS
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

export default function HomeScreen() {
  const { colors, isDark } = useTheme();
  const [profile, setProfile] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Carrega perfil quando a tela ganha foco
  useFocusEffect(
    useCallback(() => {
      loadProfile();
    }, [])
  );

  const loadProfile = async () => {
    try {
      // Primeiro tenta carregar do AsyncStorage para UI rápida
      const profileData = await AsyncStorage.getItem('userProfile');
      if (profileData) {
        setProfile(JSON.parse(profileData));
      }
      
      // Depois busca do backend para garantir dados atualizados (Single Source of Truth)
      const userId = await AsyncStorage.getItem('userId');
      if (userId && BACKEND_URL) {
        try {
          const response = await safeFetch(`${BACKEND_URL}/api/user/profile/${userId}`);
          
          if (response.ok) {
            const data = await response.json();
            await AsyncStorage.setItem('userProfile', JSON.stringify(data));
            setProfile(data);
          }
        } catch (apiError: any) {
          // Silent fail - use local data
          console.log('Using local data (backend unavailable):', apiError?.message || 'Unknown error');
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadProfile();
    setRefreshing(false);
  };

  const styles = createStyles(colors);

  // Show loading state
  if (isLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <Ionicons name="fitness" size={60} color={colors.primary} />
          <Text style={[styles.loading, { color: colors.textSecondary }]}>Carregando...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Show welcome message if no profile yet
  if (!profile) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.emptyContainer}>
          <Ionicons name="person-add-outline" size={60} color={colors.primary} />
          <Text style={[styles.emptyTitle, { color: colors.text }]}>Bem-vindo ao LAF!</Text>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>Complete seu perfil para começar</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh} 
            colors={[colors.primary]} 
            tintColor={colors.primary}
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={[styles.greeting, { color: colors.text }]}>Olá, {profile.name}!</Text>
            <Text style={[styles.subtitle, { color: colors.textSecondary }]}>Vamos conquistar seus objetivos</Text>
          </View>
          <TouchableOpacity style={styles.profileButton}>
            <Ionicons name="person-circle-outline" size={40} color={colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={[styles.statsCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Ionicons name="flame" size={28} color="#EF4444" />
            <Text style={[styles.statsValue, { color: colors.text }]}>{Math.round(profile.target_calories || 0)}</Text>
            <Text style={[styles.statsUnit, { color: colors.textSecondary }]}>kcal</Text>
            <Text style={[styles.statsLabel, { color: colors.textTertiary }]}>Meta Diária</Text>
          </View>
          <View style={[styles.statsCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Ionicons name="barbell" size={28} color={colors.primary} />
            <Text style={[styles.statsValue, { color: colors.text }]}>{profile.weekly_training_frequency || 0}</Text>
            <Text style={[styles.statsUnit, { color: colors.textSecondary }]}>x/semana</Text>
            <Text style={[styles.statsLabel, { color: colors.textTertiary }]}>Treino</Text>
          </View>
        </View>

        {/* Macros */}
        <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.cardTitle, { color: colors.text }]}>Distribuição de Macros</Text>
          {profile.macros && (
            <View style={styles.macrosContainer}>
              <MacroItem
                label="Proteínas"
                value={profile.macros.protein || 0}
                color="#3B82F6"
                textColor={colors.text}
                labelColor={colors.textSecondary}
              />
              <MacroItem
                label="Carboidratos"
                value={profile.macros.carbs || 0}
                color="#F59E0B"
                textColor={colors.text}
                labelColor={colors.textSecondary}
              />
              <MacroItem
                label="Gorduras"
                value={profile.macros.fat || 0}
                color="#EF4444"
                textColor={colors.text}
                labelColor={colors.textSecondary}
              />
            </View>
          )}
        </View>

        {/* Goal Card */}
        <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.cardTitle, { color: colors.text }]}>Seu Objetivo</Text>
          <View style={styles.goalContainer}>
            <View style={[styles.goalIcon, { backgroundColor: colors.primary + '20' }]}>
              <Ionicons name="trophy" size={24} color={colors.primary} />
            </View>
            <View style={styles.goalContent}>
              <Text style={[styles.goalLabel, { color: colors.text }]}>
                {profile.goal === 'cutting' && 'Emagrecimento (Cutting)'}
                {profile.goal === 'bulking' && 'Ganho de Massa (Bulking)'}
                {profile.goal === 'manutencao' && 'Manutenção'}
                {profile.goal === 'atleta' && `Atleta - ${profile.competition_phase || 'Prep'}`}
                {!profile.goal && 'Não definido'}
              </Text>
              <Text style={[styles.goalDesc, { color: colors.textSecondary }]}>
                TDEE: {Math.round(profile.tdee || 0)} kcal/dia
              </Text>
            </View>
          </View>
        </View>

        {/* Coming Soon */}
        <View style={[styles.comingSoonCard, { backgroundColor: colors.primary + '15' }]}>
          <Ionicons name="rocket-outline" size={48} color={colors.primary} />
          <Text style={[styles.comingSoonTitle, { color: colors.primary }]}>Em Breve</Text>
          <Text style={[styles.comingSoonText, { color: colors.textSecondary }]}>
            Sistema de dieta personalizada e treinos sob medida com IA
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function MacroItem({ label, value, color, textColor, labelColor }: any) {
  return (
    <View style={macroStyles.macroItem}>
      <View style={[macroStyles.macroIndicator, { backgroundColor: color }]} />
      <View style={macroStyles.macroContent}>
        <Text style={[macroStyles.macroLabel, { color: labelColor }]}>{label}</Text>
        <Text style={[macroStyles.macroValue, { color: textColor }]}>{Math.round(value)}g</Text>
      </View>
    </View>
  );
}

const macroStyles = StyleSheet.create({
  macroItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  macroIndicator: {
    width: 4,
    height: 40,
    borderRadius: 2,
  },
  macroContent: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  macroLabel: {
    fontSize: 16,
    fontWeight: '500',
  },
  macroValue: {
    fontSize: 18,
    fontWeight: '700',
  },
});

const createStyles = (colors: any) => StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loading: {
    marginTop: 16,
    fontSize: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '700',
    marginTop: 16,
  },
  emptyText: {
    fontSize: 16,
    marginTop: 8,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    gap: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 16,
    marginTop: 4,
  },
  profileButton: {
    padding: 4,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  statsCard: {
    flex: 1,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
  },
  statsValue: {
    fontSize: 24,
    fontWeight: '700',
    marginTop: 8,
  },
  statsUnit: {
    fontSize: 14,
  },
  statsLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  card: {
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  macrosContainer: {
    gap: 12,
  },
  goalContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  goalIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  goalContent: {
    flex: 1,
  },
  goalLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  goalDesc: {
    fontSize: 14,
  },
  comingSoonCard: {
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  comingSoonTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginTop: 12,
  },
  comingSoonText: {
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
});
