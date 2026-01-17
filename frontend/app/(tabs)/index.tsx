/**
 * LAF Premium Home Screen
 * =======================
 * Glassmorphism + Animações + Gradientes
 */

import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring, 
  withTiming,
  FadeInDown,
  FadeInRight,
} from 'react-native-reanimated';
import { 
  Flame, Dumbbell, Droplets, Target, Trophy, ChevronRight, 
  Plus, Minus, RefreshCw, Zap, TrendingUp, Calendar,
  User, Bell, Moon
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing, animations } from '../../theme/premium';
import { useTranslation } from '../../i18n';
import { HomeSkeleton } from '../../components';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
import { config } from '../../config';
const BACKEND_URL = config.BACKEND_URL;

// Safe fetch with timeout
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

// ==================== GLASS CARD COMPONENT ====================
const GlassCard = ({ children, style, isDark, onPress, gradient = false }: any) => {
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

  const content = (
    <View style={[cardStyle, style]}>
      {gradient && (
        <LinearGradient
          colors={['rgba(16, 185, 129, 0.05)', 'rgba(59, 130, 246, 0.05)']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={StyleSheet.absoluteFill}
        />
      )}
      {children}
    </View>
  );

  if (onPress) {
    return <TouchableOpacity onPress={onPress} activeOpacity={0.8}>{content}</TouchableOpacity>;
  }
  return content;
};

// ==================== ANIMATED STAT CARD ====================
const StatCard = ({ icon, value, unit, label, color, isDark, delay = 0 }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <Animated.View 
      entering={FadeInDown.delay(delay).springify()}
      style={{ flex: 1 }}
    >
      <GlassCard isDark={isDark} style={styles.statCard}>
        <View style={[styles.statIconContainer, { backgroundColor: `${color}15` }]}>
          {icon}
        </View>
        <Text style={[styles.statValue, { color: theme.text }]}>{value}</Text>
        <Text style={[styles.statUnit, { color: theme.textSecondary }]}>{unit}</Text>
        <Text style={[styles.statLabel, { color: theme.textTertiary }]}>{label}</Text>
      </GlassCard>
    </Animated.View>
  );
};

// ==================== MACRO PROGRESS BAR ====================
const MacroBar = ({ label, current, target, color, isDark }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  const progress = Math.min((current / target) * 100, 100);
  const progressWidth = useSharedValue(0);
  
  useEffect(() => {
    progressWidth.value = withSpring(progress, animations.spring.gentle);
  }, [progress]);
  
  const animatedStyle = useAnimatedStyle(() => ({
    width: `${progressWidth.value}%`,
  }));
  
  return (
    <View style={styles.macroContainer}>
      <View style={styles.macroHeader}>
        <View style={styles.macroLabelRow}>
          <View style={[styles.macroDot, { backgroundColor: color }]} />
          <Text style={[styles.macroLabel, { color: theme.text }]}>{label}</Text>
        </View>
        <Text style={[styles.macroValue, { color: theme.text }]}>
          {Math.round(current)}<Text style={{ color: theme.textTertiary, fontWeight: '500' }}> / {Math.round(target)}g</Text>
        </Text>
      </View>
      <View style={[styles.macroTrack, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)' }]}>
        <Animated.View style={[styles.macroFill, { backgroundColor: color }, animatedStyle]} />
      </View>
    </View>
  );
};

// ==================== WATER TRACKER PREMIUM ====================
const WaterTracker = ({ weight, isDark, t, onUpdate }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  const [waterConsumed, setWaterConsumed] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  
  const waterGoal = Math.round(weight * 35);
  const waterGoalLiters = (waterGoal / 1000).toFixed(1);
  const waterConsumedLiters = (waterConsumed / 1000).toFixed(1);
  const progress = Math.min((waterConsumed / waterGoal) * 100, 100);
  const cupsConsumed = Math.floor(waterConsumed / 250);
  const totalCups = Math.ceil(waterGoal / 250);
  
  const progressWidth = useSharedValue(0);
  
  useEffect(() => {
    loadWaterData();
  }, []);
  
  useEffect(() => {
    progressWidth.value = withSpring(progress, animations.spring.gentle);
  }, [progress]);
  
  const animatedProgressStyle = useAnimatedStyle(() => ({
    width: `${progressWidth.value}%`,
  }));
  
  const loadWaterData = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const savedData = await AsyncStorage.getItem(`water_${today}`);
      if (savedData) setWaterConsumed(parseInt(savedData, 10));
    } catch (error) {
      console.error('Error loading water:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const saveWaterData = async (amount: number) => {
    const today = new Date().toISOString().split('T')[0];
    await AsyncStorage.setItem(`water_${today}`, amount.toString());
  };
  
  const addWater = async (ml: number) => {
    const newAmount = Math.min(waterConsumed + ml, waterGoal + 1000);
    setWaterConsumed(newAmount);
    await saveWaterData(newAmount);
    onUpdate?.();
  };
  
  const removeWater = async () => {
    if (waterConsumed >= 250) {
      const newAmount = waterConsumed - 250;
      setWaterConsumed(newAmount);
      await saveWaterData(newAmount);
      onUpdate?.();
    }
  };
  
  const resetWater = async () => {
    setWaterConsumed(0);
    await saveWaterData(0);
    onUpdate?.();
  };
  
  if (isLoading) return null;
  
  return (
    <Animated.View entering={FadeInDown.delay(400).springify()}>
      <GlassCard isDark={isDark} gradient style={styles.waterCard}>
        {/* Header */}
        <View style={styles.waterHeader}>
          <View style={styles.waterHeaderLeft}>
            <View style={[styles.waterIconBg, { backgroundColor: '#3B82F615' }]}>
              <Droplets size={22} color="#3B82F6" strokeWidth={2.5} />
            </View>
            <View>
              <Text style={[styles.waterTitle, { color: theme.text }]}>{t.home.waterTracker}</Text>
              <Text style={[styles.waterSubtitle, { color: theme.textTertiary }]}>
                {cupsConsumed} {t.home.ofCups} {totalCups} {t.home.cups}
              </Text>
            </View>
          </View>
          <TouchableOpacity onPress={resetWater} style={styles.resetButton}>
            <RefreshCw size={18} color={theme.textTertiary} />
          </TouchableOpacity>
        </View>
        
        {/* Progress */}
        <View style={styles.waterProgressSection}>
          <View style={styles.waterProgressInfo}>
            <Text style={[styles.waterConsumed, { color: theme.text }]}>{waterConsumedLiters}</Text>
            <Text style={[styles.waterGoalText, { color: theme.textSecondary }]}>/ {waterGoalLiters}L</Text>
          </View>
          <View style={[styles.waterProgressTrack, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)' }]}>
            <Animated.View style={animatedProgressStyle}>
              <LinearGradient
                colors={progress >= 100 ? ['#10B981', '#059669'] : ['#3B82F6', '#2563EB']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.waterProgressFill}
              />
            </Animated.View>
          </View>
        </View>
        
        {/* Buttons */}
        <View style={styles.waterButtons}>
          <TouchableOpacity
            style={[styles.waterMinusBtn, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.5)' : 'rgba(226, 232, 240, 0.8)' }]}
            onPress={removeWater}
            disabled={waterConsumed < 250}
          >
            <Minus size={20} color={waterConsumed >= 250 ? theme.text : theme.textTertiary} />
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.waterAddBtn} onPress={() => addWater(250)}>
            <LinearGradient
              colors={['#3B82F6', '#2563EB']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.waterAddBtnGradient}
            >
              <Plus size={20} color="#FFF" />
              <Text style={styles.waterAddBtnText}>250ml</Text>
            </LinearGradient>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.waterAddBtnLarge} onPress={() => addWater(500)}>
            <LinearGradient
              colors={['#1D4ED8', '#1E40AF']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.waterAddBtnGradient}
            >
              <Plus size={20} color="#FFF" />
              <Text style={styles.waterAddBtnText}>500ml</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
        
        {/* Success Banner */}
        {progress >= 100 && (
          <View style={styles.successBanner}>
            <LinearGradient
              colors={['rgba(16, 185, 129, 0.15)', 'rgba(5, 150, 105, 0.15)']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.successBannerGradient}
            >
              <Zap size={18} color="#10B981" />
              <Text style={styles.successText}>{t.home.waterGoalReached}</Text>
            </LinearGradient>
          </View>
        )}
      </GlassCard>
    </Animated.View>
  );
};

// ==================== GOAL CARD ====================
const GoalCard = ({ goal, tdee, isDark, t }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  const goalConfig: any = {
    cutting: { label: t.home.cutting, icon: TrendingUp, color: '#EF4444', emoji: '🔥' },
    bulking: { label: t.home.bulking, icon: Dumbbell, color: '#10B981', emoji: '💪' },
    manutencao: { label: t.home.maintenance, icon: Target, color: '#3B82F6', emoji: '⚖️' },
  };
  
  const config = goalConfig[goal] || goalConfig.manutencao;
  const IconComponent = config.icon;
  
  return (
    <Animated.View entering={FadeInDown.delay(500).springify()}>
      <GlassCard isDark={isDark} gradient style={styles.goalCard}>
        <View style={styles.goalHeader}>
          <View style={[styles.goalIconBg, { backgroundColor: `${config.color}15` }]}>
            <IconComponent size={24} color={config.color} strokeWidth={2.5} />
          </View>
          <View style={styles.goalContent}>
            <Text style={[styles.goalLabel, { color: theme.text }]}>
              {config.emoji} {config.label}
            </Text>
            <Text style={[styles.goalDesc, { color: theme.textSecondary }]}>
              TDEE: {Math.round(tdee || 0)} kcal/dia
            </Text>
          </View>
          <View style={[styles.goalBadge, { backgroundColor: `${config.color}20` }]}>
            <Text style={[styles.goalBadgeText, { color: config.color }]}>{t.home.active}</Text>
          </View>
        </View>
      </GlassCard>
    </Animated.View>
  );
};

// ==================== MAIN HOME SCREEN ====================
export default function HomeScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();
  
  const [profile, setProfile] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [dayType, setDayType] = useState<'train' | 'rest'>('rest');
  const [todayWorkout, setTodayWorkout] = useState<any>(null);
  const [cycleStatus, setCycleStatus] = useState<any>(null);

  useFocusEffect(
    useCallback(() => {
      loadProfile();
    }, [])
  );

  const loadProfile = async () => {
    try {
      const profileData = await AsyncStorage.getItem('userProfile');
      if (profileData) setProfile(JSON.parse(profileData));
      
      const storedUserId = await AsyncStorage.getItem('userId');
      if (storedUserId) setUserId(storedUserId);
      
      if (storedUserId && BACKEND_URL) {
        try {
          // Carrega perfil
          const response = await safeFetch(`${BACKEND_URL}/api/user/profile/${storedUserId}`);
          if (response.ok) {
            const data = await response.json();
            
            // Carrega dieta para pegar os valores reais
            try {
              const dietResponse = await safeFetch(`${BACKEND_URL}/api/diet/${storedUserId}`);
              if (dietResponse.ok) {
                const dietData = await dietResponse.json();
                // Usa os valores computados da dieta (reais) ao invés dos alvos do perfil
                if (dietData.computed_calories) {
                  data.target_calories = dietData.computed_calories;
                }
                if (dietData.computed_macros) {
                  data.macros = dietData.computed_macros;
                }
              }
            } catch (dietError) {
              console.log('Diet not loaded, using profile targets');
            }
            
            // Carrega status do ciclo de treino
            try {
              const cycleResponse = await safeFetch(`${BACKEND_URL}/api/training-cycle/status/${storedUserId}`);
              if (cycleResponse.ok) {
                const cycleData = await cycleResponse.json();
                setCycleStatus(cycleData);
                setDayType(cycleData.planned_day_type || cycleData.day_type || 'rest');
                
                // Se for dia de treino, carrega o treino de hoje
                if (cycleData.planned_day_type === 'train' || cycleData.day_type === 'train') {
                  try {
                    const workoutResponse = await safeFetch(`${BACKEND_URL}/api/workout/${storedUserId}`);
                    if (workoutResponse.ok) {
                      const workoutData = await workoutResponse.json();
                      // Pega o treino do dia usando o índice do backend
                      const workoutDays = workoutData.days || workoutData.workout_days || [];
                      const todayIndex = cycleData.today_workout_index || 0;
                      if (workoutDays[todayIndex]) {
                        setTodayWorkout({
                          ...workoutDays[todayIndex],
                          // Sobrescreve o nome com o do backend se for PPL
                          name: cycleData.today_workout_name || workoutDays[todayIndex].name
                        });
                      }
                    }
                  } catch (workoutError) {
                    console.log('Workout not loaded');
                  }
                }
              }
            } catch (cycleError) {
              console.log('Cycle status not loaded');
            }
            
            await AsyncStorage.setItem('userProfile', JSON.stringify(data));
            setProfile(data);
          }
        } catch (apiError) {
          console.log('Using local data');
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadProfile();
    setRefreshing(false);
  };

  if (isLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <HomeSkeleton />
      </SafeAreaView>
    );
  }

  if (!profile) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <View style={styles.emptyContainer}>
          <User size={60} color={premiumColors.primary} />
          <Text style={[styles.emptyTitle, { color: theme.text }]}>{t.home.welcome}</Text>
          <Text style={[styles.emptyText, { color: theme.textSecondary }]}>{t.home.completeProfile}</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Background Gradient */}
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
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl 
              refreshing={refreshing} 
              onRefresh={onRefresh} 
              tintColor={premiumColors.primary}
            />
          }
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <View>
              <Text style={[styles.greeting, { color: theme.text }]}>
                {t.home.greeting}, {profile.name?.split(' ')[0]}! 👋
              </Text>
              <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
                {t.home.subtitle}
              </Text>
            </View>
            <TouchableOpacity style={[styles.profileButton, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)' }]}>
              <Bell size={22} color={theme.text} />
            </TouchableOpacity>
          </Animated.View>

          {/* Stats Cards */}
          <View style={styles.statsRow}>
            <StatCard
              icon={<Flame size={26} color="#EF4444" strokeWidth={2.5} />}
              value={Math.round(profile.target_calories || 0)}
              unit="kcal"
              label={t.home.dailyGoal}
              color="#EF4444"
              isDark={isDark}
              delay={100}
            />
            <View style={{ width: spacing.md }} />
            <StatCard
              icon={<Dumbbell size={26} color={premiumColors.primary} strokeWidth={2.5} />}
              value={profile.weekly_training_frequency || 0}
              unit={t.home.workouts}
              label={t.home.perWeek}
              color={premiumColors.primary}
              isDark={isDark}
              delay={200}
            />
          </View>

          {/* Treino de Hoje / Dia de Descanso Card */}
          <Animated.View entering={FadeInDown.delay(300).springify()}>
            <GlassCard isDark={isDark} style={styles.macrosCard}>
              {dayType === 'train' ? (
                <>
                  {/* Dia de Treino */}
                  <View style={styles.macrosHeader}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                      <View style={{ 
                        width: 36, height: 36, borderRadius: 12, 
                        backgroundColor: premiumColors.primary + '20',
                        alignItems: 'center', justifyContent: 'center'
                      }}>
                        <Dumbbell size={20} color={premiumColors.primary} />
                      </View>
                      <View>
                        <Text style={[styles.cardTitle, { color: theme.text }]}>
                          Hoje é dia de TREINO 💪
                        </Text>
                        {cycleStatus?.today_workout_name && (
                          <Text style={{ fontSize: 12, color: premiumColors.primary, fontWeight: '600', marginTop: 2 }}>
                            {cycleStatus.today_workout_name}
                          </Text>
                        )}
                      </View>
                    </View>
                    <TouchableOpacity style={styles.seeAllBtn}>
                      <Text style={[styles.seeAllText, { color: premiumColors.primary }]}>Ver Treino</Text>
                      <ChevronRight size={16} color={premiumColors.primary} />
                    </TouchableOpacity>
                  </View>
                  
                  {/* Status do treino */}
                  {cycleStatus && (
                    <View style={{ 
                      flexDirection: 'row', 
                      alignItems: 'center', 
                      gap: 8, 
                      marginTop: 12,
                      padding: 10,
                      backgroundColor: cycleStatus.workout_status === 'completed' 
                        ? 'rgba(16, 185, 129, 0.1)' 
                        : 'rgba(245, 158, 11, 0.1)',
                      borderRadius: 10
                    }}>
                      <View style={{
                        width: 8, height: 8, borderRadius: 4,
                        backgroundColor: cycleStatus.workout_status === 'completed' ? '#10B981' : '#F59E0B'
                      }} />
                      <Text style={{ 
                        fontSize: 13, 
                        color: cycleStatus.workout_status === 'completed' ? '#10B981' : '#F59E0B',
                        fontWeight: '600'
                      }}>
                        {cycleStatus.workout_status === 'completed' 
                          ? '✅ Treino concluído!' 
                          : cycleStatus.workout_status === 'in_progress'
                            ? '⏱️ Treino em andamento...'
                            : '⏳ Treino pendente'}
                      </Text>
                    </View>
                  )}
                  
                  {/* Info da dieta */}
                  <View style={{ 
                    marginTop: 12, 
                    padding: 12, 
                    backgroundColor: isDark ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.08)',
                    borderRadius: 10
                  }}>
                    <Text style={{ fontSize: 12, color: '#10B981', fontWeight: '600' }}>
                      🍽️ Dieta de treino ativa: {cycleStatus?.diet?.info || '+5% cal, +15% carbs'}
                    </Text>
                  </View>
                  
                  {todayWorkout?.exercises && todayWorkout.exercises.length > 0 && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={[{ fontSize: 13, fontWeight: '600', color: theme.textSecondary, marginBottom: 8 }]}>
                        Exercícios de hoje:
                      </Text>
                      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
                        {todayWorkout.exercises.slice(0, 4).map((ex: any, idx: number) => (
                          <View key={idx} style={{
                            backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.5)',
                            paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8
                          }}>
                            <Text style={{ fontSize: 12, color: theme.textSecondary }}>
                              {ex.name}
                            </Text>
                          </View>
                        ))}
                        {todayWorkout.exercises.length > 4 && (
                          <View style={{
                            backgroundColor: premiumColors.primary + '20',
                            paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8
                          }}>
                            <Text style={{ fontSize: 12, color: premiumColors.primary, fontWeight: '600' }}>
                              +{todayWorkout.exercises.length - 4} mais
                            </Text>
                          </View>
                        )}
                      </View>
                    </View>
                  )}
                </>
              ) : (
                <>
                  {/* Dia de Descanso */}
                  <View style={styles.macrosHeader}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                      <View style={{ 
                        width: 36, height: 36, borderRadius: 12, 
                        backgroundColor: '#6B728020',
                        alignItems: 'center', justifyContent: 'center'
                      }}>
                        <Moon size={20} color="#6B7280" />
                      </View>
                      <Text style={[styles.cardTitle, { color: theme.text }]}>
                        Hoje é dia de DESCANSO 💤
                      </Text>
                    </View>
                  </View>
                  
                  {/* Info da dieta de descanso */}
                  <View style={{ 
                    marginTop: 12, 
                    padding: 12, 
                    backgroundColor: isDark ? 'rgba(107, 114, 128, 0.1)' : 'rgba(107, 114, 128, 0.08)',
                    borderRadius: 10
                  }}>
                    <Text style={{ fontSize: 12, color: '#6B7280', fontWeight: '600' }}>
                      🍽️ Dieta de descanso ativa: {cycleStatus?.diet?.info || '-5% cal, -20% carbs'}
                    </Text>
                  </View>
                  
                  <View style={{ marginTop: 12, alignItems: 'center', paddingVertical: 8 }}>
                    <Text style={{ fontSize: 14, color: theme.textSecondary, textAlign: 'center' }}>
                      Hoje é dia de recuperação muscular.{'\n'}
                      Descanse bem para o próximo treino!
                    </Text>
                  </View>
                  
                  {/* Treino bônus */}
                  {cycleStatus?.workout_status === 'bonus' && (
                    <View style={{ 
                      marginTop: 12, 
                      padding: 12, 
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      borderRadius: 10
                    }}>
                      <Text style={{ fontSize: 13, color: '#10B981', fontWeight: '600' }}>
                        🎉 Treino bônus realizado! Dieta ajustada para treino.
                      </Text>
                    </View>
                  )}
                </>
              )}
                </>
              )}
            </GlassCard>
          </Animated.View>

          {/* Water Tracker */}
          {profile.weight > 0 && (
            <WaterTracker 
              weight={profile.weight} 
              isDark={isDark} 
              t={t}
              onUpdate={() => {}}
            />
          )}

          {/* Goal Card */}
          <GoalCard 
            goal={profile.goal} 
            tdee={profile.tdee} 
            isDark={isDark} 
            t={t}
          />
          
          {/* Bottom Spacing for Tab Bar */}
          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

// ==================== STYLES ====================
const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollView: { flex: 1 },
  scrollContent: { padding: spacing.lg, gap: spacing.lg },
  
  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -0.8,
  },
  subtitle: {
    fontSize: 15,
    marginTop: 4,
    fontWeight: '500',
  },
  profileButton: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  
  // Stats
  statsRow: {
    flexDirection: 'row',
  },
  statCard: {
    padding: spacing.base,
    alignItems: 'center',
    gap: spacing.sm,
  },
  statIconContainer: {
    width: 52,
    height: 52,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statValue: {
    fontSize: 32,
    fontWeight: '800',
    letterSpacing: -1,
  },
  statUnit: {
    fontSize: 13,
    fontWeight: '600',
    marginTop: -4,
  },
  statLabel: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  
  // Macros Card
  macrosCard: {
    padding: spacing.lg,
  },
  macrosHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.base,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: -0.4,
  },
  seeAllBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
  },
  seeAllText: {
    fontSize: 14,
    fontWeight: '600',
  },
  macrosContent: {
    gap: spacing.md,
  },
  
  // Macro Bar
  macroContainer: {
    gap: 8,
  },
  macroHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  macroLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  macroDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  macroLabel: {
    fontSize: 15,
    fontWeight: '600',
  },
  macroValue: {
    fontSize: 15,
    fontWeight: '700',
  },
  macroTrack: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  macroFill: {
    height: '100%',
    borderRadius: 4,
  },
  
  // Water Tracker
  waterCard: {
    padding: spacing.lg,
  },
  waterHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.base,
  },
  waterHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  waterIconBg: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  waterTitle: {
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  waterSubtitle: {
    fontSize: 13,
    marginTop: 2,
  },
  resetButton: {
    padding: spacing.sm,
  },
  waterProgressSection: {
    marginBottom: spacing.base,
  },
  waterProgressInfo: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: spacing.sm,
  },
  waterConsumed: {
    fontSize: 36,
    fontWeight: '800',
    letterSpacing: -1,
  },
  waterGoalText: {
    fontSize: 18,
    fontWeight: '500',
    marginLeft: 4,
  },
  waterProgressTrack: {
    height: 10,
    borderRadius: 5,
    overflow: 'hidden',
  },
  waterProgressFill: {
    height: '100%',
    borderRadius: 5,
  },
  waterButtons: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  waterMinusBtn: {
    width: 48,
    height: 48,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  waterAddBtn: {
    flex: 1,
    height: 48,
    borderRadius: radius.lg,
    overflow: 'hidden',
  },
  waterAddBtnLarge: {
    flex: 1,
    height: 48,
    borderRadius: radius.lg,
    overflow: 'hidden',
  },
  waterAddBtnGradient: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  waterAddBtnText: {
    color: '#FFF',
    fontSize: 15,
    fontWeight: '700',
  },
  successBanner: {
    marginTop: spacing.md,
    borderRadius: radius.lg,
    overflow: 'hidden',
  },
  successBannerGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: spacing.md,
  },
  successText: {
    color: '#10B981',
    fontSize: 14,
    fontWeight: '700',
  },
  
  // Goal Card
  goalCard: {
    padding: spacing.lg,
  },
  goalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  goalIconBg: {
    width: 52,
    height: 52,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  goalContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  goalLabel: {
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  goalDesc: {
    fontSize: 14,
    marginTop: 2,
  },
  goalBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
  },
  goalBadgeText: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  
  // Empty State
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    gap: spacing.md,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '700',
  },
  emptyText: {
    fontSize: 16,
  },
});
