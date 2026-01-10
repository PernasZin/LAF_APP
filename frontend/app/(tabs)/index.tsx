import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Animated, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';
import { HomeSkeleton } from '../../components';
import { useHaptics } from '../../hooks/useHaptics';
import { useTranslation } from '../../i18n';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

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

// ==================== WATER TRACKER COMPONENT ====================
interface WaterTrackerProps {
  weight: number;
  colors: any;
  t: any;
  onUpdate: () => void;
}

function WaterTracker({ weight, colors, t, onUpdate }: WaterTrackerProps) {
  const { lightImpact, successFeedback, warningFeedback } = useHaptics();
  const [waterConsumed, setWaterConsumed] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  
  // Cálculo: 35ml por kg de peso corporal
  const waterGoal = Math.round(weight * 35); // em ml
  const waterGoalLiters = (waterGoal / 1000).toFixed(1);
  const waterConsumedLiters = (waterConsumed / 1000).toFixed(1);
  const progress = Math.min((waterConsumed / waterGoal) * 100, 100);
  const cupsConsumed = Math.floor(waterConsumed / 250);
  const totalCups = Math.ceil(waterGoal / 250);
  
  // Carrega consumo de água do dia
  useEffect(() => {
    loadWaterData();
  }, []);
  
  const loadWaterData = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const key = `water_${today}`;
      const savedData = await AsyncStorage.getItem(key);
      if (savedData) {
        setWaterConsumed(parseInt(savedData, 10));
      } else {
        setWaterConsumed(0);
      }
    } catch (error) {
      console.error('Error loading water data:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const saveWaterData = async (amount: number) => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const key = `water_${today}`;
      await AsyncStorage.setItem(key, amount.toString());
    } catch (error) {
      console.error('Error saving water data:', error);
    }
  };
  
  const addWater = async (ml: number) => {
    lightImpact();
    const newAmount = Math.min(waterConsumed + ml, waterGoal + 1000); // Permite +1L além da meta
    setWaterConsumed(newAmount);
    await saveWaterData(newAmount);
    
    // Feedback de sucesso ao atingir a meta
    if (waterConsumed < waterGoal && newAmount >= waterGoal) {
      successFeedback();
    }
    onUpdate();
  };
  
  const removeWater = async () => {
    if (waterConsumed >= 250) {
      warningFeedback();
      const newAmount = waterConsumed - 250;
      setWaterConsumed(newAmount);
      await saveWaterData(newAmount);
      onUpdate();
    }
  };
  
  const resetWater = async () => {
    warningFeedback();
    setWaterConsumed(0);
    await saveWaterData(0);
    onUpdate();
  };
  
  if (isLoading) {
    return null;
  }
  
  return (
    <View style={[waterStyles.container, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
      {/* Header */}
      <View style={waterStyles.header}>
        <View style={waterStyles.headerLeft}>
          <Ionicons name="water" size={24} color="#3B82F6" />
          <Text style={[waterStyles.title, { color: colors.text }]}>
            {t?.home?.waterTracker || 'Hidratação'}
          </Text>
        </View>
        <TouchableOpacity onPress={resetWater} style={waterStyles.resetButton}>
          <Ionicons name="refresh-outline" size={18} color={colors.textTertiary} />
        </TouchableOpacity>
      </View>
      
      {/* Meta e progresso */}
      <View style={waterStyles.progressSection}>
        <View style={waterStyles.progressInfo}>
          <Text style={[waterStyles.consumed, { color: colors.text }]}>
            {waterConsumedLiters}L
          </Text>
          <Text style={[waterStyles.goal, { color: colors.textSecondary }]}>
            / {waterGoalLiters}L
          </Text>
        </View>
        <Text style={[waterStyles.cups, { color: colors.textTertiary }]}>
          {cupsConsumed} de {totalCups} copos (250ml)
        </Text>
      </View>
      
      {/* Barra de progresso */}
      <View style={[waterStyles.progressBar, { backgroundColor: colors.border }]}>
        <View 
          style={[
            waterStyles.progressFill, 
            { 
              width: `${progress}%`,
              backgroundColor: progress >= 100 ? '#10B981' : '#3B82F6'
            }
          ]} 
        />
      </View>
      
      {/* Visual de copos */}
      <View style={waterStyles.cupsContainer}>
        {Array.from({ length: Math.min(totalCups, 12) }).map((_, index) => (
          <View 
            key={index}
            style={[
              waterStyles.cupIcon,
              {
                backgroundColor: index < cupsConsumed 
                  ? (progress >= 100 ? '#10B981' : '#3B82F6') 
                  : colors.border,
                opacity: index < cupsConsumed ? 1 : 0.3
              }
            ]}
          >
            <Ionicons 
              name="water" 
              size={14} 
              color={index < cupsConsumed ? '#FFFFFF' : colors.textTertiary} 
            />
          </View>
        ))}
        {totalCups > 12 && (
          <Text style={[waterStyles.moreCups, { color: colors.textTertiary }]}>
            +{totalCups - 12}
          </Text>
        )}
      </View>
      
      {/* Botões de ação */}
      <View style={waterStyles.buttonsContainer}>
        <TouchableOpacity 
          style={[waterStyles.subtractButton, { backgroundColor: colors.border }]}
          onPress={removeWater}
          disabled={waterConsumed < 250}
        >
          <Ionicons name="remove" size={20} color={waterConsumed >= 250 ? colors.text : colors.textTertiary} />
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[waterStyles.addButton, { backgroundColor: '#3B82F6' }]}
          onPress={() => addWater(250)}
        >
          <Ionicons name="add" size={22} color="#FFFFFF" />
          <Text style={waterStyles.addButtonText}>250ml</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[waterStyles.addButtonLarge, { backgroundColor: '#2563EB' }]}
          onPress={() => addWater(500)}
        >
          <Ionicons name="add" size={22} color="#FFFFFF" />
          <Text style={waterStyles.addButtonText}>500ml</Text>
        </TouchableOpacity>
      </View>
      
      {/* Mensagem motivacional */}
      {progress >= 100 && (
        <View style={[waterStyles.successBanner, { backgroundColor: '#10B98120' }]}>
          <Ionicons name="checkmark-circle" size={18} color="#10B981" />
          <Text style={[waterStyles.successText, { color: '#10B981' }]}>
            {t?.home?.waterGoalReached || 'Meta de hidratação atingida! 🎉'}
          </Text>
        </View>
      )}
      
      {progress < 50 && waterConsumed > 0 && (
        <Text style={[waterStyles.tipText, { color: colors.textTertiary }]}>
          💧 Beba água regularmente ao longo do dia
        </Text>
      )}
    </View>
  );
}

const waterStyles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  title: {
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  resetButton: {
    padding: 4,
  },
  progressSection: {
    marginBottom: 10,
  },
  progressInfo: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  consumed: {
    fontSize: 32,
    fontWeight: '800',
    letterSpacing: -1,
  },
  goal: {
    fontSize: 18,
    fontWeight: '500',
    marginLeft: 4,
  },
  cups: {
    fontSize: 13,
    marginTop: 2,
  },
  progressBar: {
    height: 10,
    borderRadius: 5,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressFill: {
    height: '100%',
    borderRadius: 5,
  },
  cupsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 14,
  },
  cupIcon: {
    width: 26,
    height: 26,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  moreCups: {
    fontSize: 12,
    fontWeight: '600',
    alignSelf: 'center',
    marginLeft: 4,
  },
  buttonsContainer: {
    flexDirection: 'row',
    gap: 10,
  },
  subtractButton: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addButton: {
    flex: 1,
    flexDirection: 'row',
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
  },
  addButtonLarge: {
    flex: 1,
    flexDirection: 'row',
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  successBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    padding: 10,
    borderRadius: 10,
    marginTop: 12,
  },
  successText: {
    fontSize: 14,
    fontWeight: '600',
  },
  tipText: {
    fontSize: 12,
    textAlign: 'center',
    marginTop: 10,
  },
});

export default function HomeScreen() {
  const { colors, isDark } = useTheme();
  const { t } = useTranslation();
  const { lightImpact, successFeedback } = useHaptics();
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
    lightImpact(); // Haptic feedback ao iniciar refresh
    await loadProfile();
    successFeedback(); // Haptic feedback ao completar
    setRefreshing(false);
  };

  const styles = createStyles(colors);

  // Show skeleton loading state
  if (isLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <HomeSkeleton />
      </SafeAreaView>
    );
  }

  // Show welcome message if no profile yet
  if (!profile) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.emptyContainer}>
          <Ionicons name="person-add-outline" size={60} color={colors.primary} />
          <Text style={[styles.emptyTitle, { color: colors.text }]}>{t.home.greeting} LAF!</Text>
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
            <Text style={[styles.greeting, { color: colors.text }]}>{t.home.greeting}, {profile.name}!</Text>
            <Text style={[styles.subtitle, { color: colors.textSecondary }]}>{t.home.subtitle}</Text>
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
            <Text style={[styles.statsLabel, { color: colors.textTertiary }]}>{t.home.dailyGoal}</Text>
          </View>
          <View style={[styles.statsCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Ionicons name="barbell" size={28} color={colors.primary} />
            <Text style={[styles.statsValue, { color: colors.text }]}>{profile.weekly_training_frequency || 0}</Text>
            <Text style={[styles.statsUnit, { color: colors.textSecondary }]}>{t.home.weeklyFrequency}</Text>
            <Text style={[styles.statsLabel, { color: colors.textTertiary }]}>{t.home.training}</Text>
          </View>
        </View>

        {/* Macros */}
        <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.cardTitle, { color: colors.text }]}>{t.home.macrosDistribution}</Text>
          {profile.macros && (
            <View style={styles.macrosContainer}>
              <MacroItem
                label={t.home.protein}
                value={profile.macros.protein || 0}
                color="#3B82F6"
                textColor={colors.text}
                labelColor={colors.textSecondary}
              />
              <MacroItem
                label={t.home.carbs}
                value={profile.macros.carbs || 0}
                color="#F59E0B"
                textColor={colors.text}
                labelColor={colors.textSecondary}
              />
              <MacroItem
                label={t.home.fat}
                value={profile.macros.fat || 0}
                color="#EF4444"
                textColor={colors.text}
                labelColor={colors.textSecondary}
              />
            </View>
          )}
        </View>

        {/* Water Tracker - Sistema de Hidratação por kg */}
        {profile.weight && profile.weight > 0 && (
          <WaterTracker 
            weight={profile.weight} 
            colors={colors} 
            t={t}
            onUpdate={() => {}}
          />
        )}

        {/* Goal Card */}
        <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.cardTitle, { color: colors.text }]}>{t.home.yourGoal}</Text>
          <View style={styles.goalContainer}>
            <View style={[styles.goalIcon, { backgroundColor: colors.primary + '20' }]}>
              <Ionicons name="trophy" size={24} color={colors.primary} />
            </View>
            <View style={styles.goalContent}>
              <Text style={[styles.goalLabel, { color: colors.text }]}>
                {profile.goal === 'cutting' && t.home.cutting}
                {profile.goal === 'bulking' && t.home.bulking}
                {profile.goal === 'manutencao' && t.home.maintenance}
                {!profile.goal && 'Não definido'}
              </Text>
              <Text style={[styles.goalDesc, { color: colors.textSecondary }]}>
                {t.home.tdee}: {Math.round(profile.tdee || 0)} kcal/dia
              </Text>
            </View>
          </View>
        </View>

        {/* Coming Soon */}
        <View style={[styles.comingSoonCard, { backgroundColor: colors.primary + '15' }]}>
          <Ionicons name="rocket-outline" size={48} color={colors.primary} />
          <Text style={[styles.comingSoonTitle, { color: colors.primary }]}>{t.home.comingSoon}</Text>
          <Text style={[styles.comingSoonText, { color: colors.textSecondary }]}>
            {t.home.comingSoonText}
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
    gap: 14,
  },
  macroIndicator: {
    width: 5,
    height: 44,
    borderRadius: 3,
  },
  macroContent: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  macroLabel: {
    fontSize: 15,
    fontWeight: '600',
  },
  macroValue: {
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: -0.3,
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
    padding: 20,
    gap: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  greeting: {
    fontSize: 26,
    fontWeight: '800',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 15,
    marginTop: 4,
    opacity: 0.8,
  },
  profileButton: {
    padding: 4,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 14,
  },
  statsCard: {
    flex: 1,
    padding: 18,
    borderRadius: 20,
    alignItems: 'center',
    borderWidth: 1,
  },
  statsValue: {
    fontSize: 28,
    fontWeight: '800',
    marginTop: 10,
    letterSpacing: -0.5,
  },
  statsUnit: {
    fontSize: 13,
    fontWeight: '500',
    opacity: 0.7,
  },
  statsLabel: {
    fontSize: 11,
    marginTop: 6,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  card: {
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: '700',
    marginBottom: 16,
    letterSpacing: -0.3,
  },
  macrosContainer: {
    gap: 14,
  },
  goalContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  goalIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  goalContent: {
    flex: 1,
  },
  goalLabel: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  goalDesc: {
    fontSize: 14,
    opacity: 0.7,
  },
  comingSoonCard: {
    padding: 32,
    borderRadius: 20,
    alignItems: 'center',
    marginTop: 4,
  },
  comingSoonTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginTop: 14,
  },
  comingSoonText: {
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 22,
    opacity: 0.8,
  },
});
