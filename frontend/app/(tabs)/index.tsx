import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function HomeScreen() {
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
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(`${BACKEND_URL}/api/user/profile/${userId}`, {
            signal: controller.signal,
          });
          
          clearTimeout(timeoutId);
          
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

  // Show loading state
  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Ionicons name="fitness" size={60} color="#10B981" />
          <Text style={styles.loading}>Carregando...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Show welcome message if no profile yet
  if (!profile) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyContainer}>
          <Ionicons name="person-add-outline" size={60} color="#10B981" />
          <Text style={styles.emptyTitle}>Bem-vindo ao LAF!</Text>
          <Text style={styles.emptyText}>Complete seu perfil para começar</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#10B981']} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Olá, {profile.name}!</Text>
            <Text style={styles.subtitle}>Vamos conquistar seus objetivos</Text>
          </View>
          <TouchableOpacity style={styles.profileButton}>
            <Ionicons name="person-circle-outline" size={40} color="#10B981" />
          </TouchableOpacity>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <StatsCard
            icon="flame"
            label="Meta Diária"
            value={`${Math.round(profile.target_calories || 0)}`}
            unit="kcal"
            color="#EF4444"
          />
          <StatsCard
            icon="barbell"
            label="Treino"
            value={profile.weekly_training_frequency || 0}
            unit="x/semana"
            color="#10B981"
          />
        </View>

        {/* Macros */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Distribuição de Macros</Text>
          {profile.macros && (
            <View style={styles.macrosContainer}>
              <MacroItem
                label="Proteínas"
                value={profile.macros.protein || 0}
                color="#3B82F6"
              />
              <MacroItem
                label="Carboidratos"
                value={profile.macros.carbs || 0}
                color="#F59E0B"
              />
              <MacroItem
                label="Gorduras"
                value={profile.macros.fat || 0}
                color="#EF4444"
              />
            </View>
          )}
        </View>

        {/* Goal Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Seu Objetivo</Text>
          <View style={styles.goalContainer}>
            <View style={styles.goalIcon}>
              <Ionicons name="trophy" size={24} color="#10B981" />
            </View>
            <View style={styles.goalContent}>
              <Text style={styles.goalLabel}>
                {profile.goal === 'cutting' && 'Emagrecimento (Cutting)'}
                {profile.goal === 'bulking' && 'Ganho de Massa (Bulking)'}
                {profile.goal === 'manutencao' && 'Manutenção'}
                {profile.goal === 'atleta' && 'Atleta/Competição'}
                {!profile.goal && 'Não definido'}
              </Text>
              <Text style={styles.goalDesc}>
                TDEE: {Math.round(profile.tdee || 0)} kcal/dia
              </Text>
            </View>
          </View>
        </View>

        {/* Coming Soon */}
        <View style={styles.comingSoonCard}>
          <Ionicons name="rocket-outline" size={48} color="#10B981" />
          <Text style={styles.comingSoonTitle}>Em Breve</Text>
          <Text style={styles.comingSoonText}>
            Sistema de dieta personalizada e treinos sob medida com IA
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function StatsCard({ icon, label, value, unit, color }: any) {
  return (
    <View style={styles.statsCard}>
      <Ionicons name={icon} size={28} color={color} />
      <Text style={styles.statsValue}>{value}</Text>
      <Text style={styles.statsUnit}>{unit}</Text>
      <Text style={styles.statsLabel}>{label}</Text>
    </View>
  );
}

function MacroItem({ label, value, color }: any) {
  return (
    <View style={styles.macroItem}>
      <View style={[styles.macroIndicator, { backgroundColor: color }]} />
      <View style={styles.macroContent}>
        <Text style={styles.macroLabel}>{label}</Text>
        <Text style={styles.macroValue}>{Math.round(value)}g</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loading: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
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
    color: '#111827',
    marginTop: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
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
    color: '#111827',
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
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
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  statsValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginTop: 8,
  },
  statsUnit: {
    fontSize: 14,
    color: '#6B7280',
  },
  statsLabel: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  macrosContainer: {
    gap: 12,
  },
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
    color: '#374151',
    fontWeight: '500',
  },
  macroValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
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
    backgroundColor: '#F0FDF4',
    alignItems: 'center',
    justifyContent: 'center',
  },
  goalContent: {
    flex: 1,
  },
  goalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  goalDesc: {
    fontSize: 14,
    color: '#6B7280',
  },
  comingSoonCard: {
    backgroundColor: '#F0FDF4',
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  comingSoonTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#10B981',
    marginTop: 12,
  },
  comingSoonText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
});
