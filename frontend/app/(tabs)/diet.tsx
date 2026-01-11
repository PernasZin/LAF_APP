/**
 * LAF Premium Diet Screen
 * ========================
 * Glassmorphism + Gradientes + Animações
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, RefreshControl, Modal, Alert, Dimensions
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import Animated, { FadeInDown, FadeIn } from 'react-native-reanimated';
import { 
  Utensils, Sun, Coffee, Moon, Apple, ChefHat, RefreshCw,
  ChevronRight, Check, X, Flame, Beef, Wheat, Droplets
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { DietSkeleton } from '../../components';
import { useTranslation, translateFood, translateMealName } from '../../i18n';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const { width: SCREEN_WIDTH } = Dimensions.get('window');

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

const MEAL_ICONS: Record<string, any> = {
  'Café da Manhã': { Icon: Sun, color: '#F59E0B' },
  'Lanche Manhã': { Icon: Coffee, color: '#10B981' },
  'Almoço': { Icon: ChefHat, color: '#3B82F6' },
  'Lanche Tarde': { Icon: Apple, color: '#8B5CF6' },
  'Jantar': { Icon: Moon, color: '#6366F1' },
  'Ceia': { Icon: Moon, color: '#EC4899' },
};

const CATEGORY_CONFIG: Record<string, { color: string; Icon: any }> = {
  protein: { color: '#EF4444', Icon: Beef },
  carb: { color: '#F59E0B', Icon: Wheat },
  fat: { color: '#3B82F6', Icon: Droplets },
  fruit: { color: '#EC4899', Icon: Apple },
  vegetable: { color: '#10B981', Icon: Apple },
};

// Glass Card Component
const GlassCard = ({ children, style, isDark, onPress }: any) => {
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
  if (onPress) {
    return <TouchableOpacity onPress={onPress} activeOpacity={0.8} style={[cardStyle, style]}>{children}</TouchableOpacity>;
  }
  return <View style={[cardStyle, style]}>{children}</View>;
};

// Meal Card Component
const MealCard = ({ meal, index, isDark, theme, onFoodPress, language }: any) => {
  const mealConfig = MEAL_ICONS[meal.name] || { Icon: Utensils, color: '#6B7280' };
  const IconComponent = mealConfig.Icon;
  
  return (
    <Animated.View entering={FadeInDown.delay(index * 100).springify()}>
      <GlassCard isDark={isDark} style={styles.mealCard}>
        {/* Meal Header */}
        <View style={styles.mealHeader}>
          <View style={[styles.mealIconBg, { backgroundColor: mealConfig.color + '15' }]}>
            <IconComponent size={22} color={mealConfig.color} strokeWidth={2.5} />
          </View>
          <View style={styles.mealHeaderContent}>
            <Text style={[styles.mealName, { color: theme.text }]}>
              {translateMealName(meal.name, language)}
            </Text>
            <Text style={[styles.mealTime, { color: theme.textTertiary }]}>
              {meal.time || '—'}
            </Text>
          </View>
          <View style={[styles.mealCaloriesBadge, { backgroundColor: mealConfig.color + '15' }]}>
            <Flame size={14} color={mealConfig.color} />
            <Text style={[styles.mealCaloriesText, { color: mealConfig.color }]}>
              {Math.round(meal.calories || 0)} kcal
            </Text>
          </View>
        </View>

        {/* Foods List */}
        <View style={styles.foodsList}>
          {meal.foods?.map((food: any, foodIndex: number) => {
            const catConfig = CATEGORY_CONFIG[food.category] || { color: '#6B7280', Icon: Utensils };
            const CatIcon = catConfig.Icon;
            return (
              <TouchableOpacity
                key={foodIndex}
                style={[styles.foodItem, { borderBottomColor: theme.border }]}
                onPress={() => onFoodPress(food, index, foodIndex)}
                activeOpacity={0.7}
              >
                <View style={[styles.foodCategoryDot, { backgroundColor: catConfig.color }]} />
                <View style={styles.foodContent}>
                  <Text style={[styles.foodName, { color: theme.text }]} numberOfLines={1}>
                    {translateFood(food.name, language)}
                  </Text>
                  <Text style={[styles.foodAmount, { color: theme.textTertiary }]}>
                    {Math.round(food.grams)}g
                  </Text>
                </View>
                <View style={styles.foodMacros}>
                  <Text style={[styles.foodMacroText, { color: theme.textSecondary }]}>
                    P:{Math.round(food.protein || 0)} C:{Math.round(food.carbs || 0)} G:{Math.round(food.fat || 0)}
                  </Text>
                </View>
                <ChevronRight size={16} color={theme.textTertiary} />
              </TouchableOpacity>
            );
          })}
        </View>
      </GlassCard>
    </Animated.View>
  );
};

export default function DietScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t, language } = useTranslation();

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [dietPlan, setDietPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);

  // Substitution modal
  const [substitutionModal, setSubstitutionModal] = useState(false);
  const [selectedFood, setSelectedFood] = useState<any>(null);
  const [selectedMealIndex, setSelectedMealIndex] = useState(-1);
  const [selectedFoodIndex, setSelectedFoodIndex] = useState(-1);
  const [substitutes, setSubstitutes] = useState<any[]>([]);
  const [loadingSubstitutes, setLoadingSubstitutes] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadUserData();
    }, [])
  );

  const loadUserData = async () => {
    try {
      setInitialLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        const [profileRes, dietRes] = await Promise.all([
          safeFetch(`${BACKEND_URL}/api/user/profile/${id}`),
          safeFetch(`${BACKEND_URL}/api/diet/${id}`),
        ]);

        if (profileRes.ok) {
          const data = await profileRes.json();
          setUserProfile(data);
        }
        if (dietRes.ok) {
          const data = await dietRes.json();
          setDietPlan(data);
        }
      }
    } catch (error) {
      console.error('Error loading diet:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  const handleFoodPress = async (food: any, mealIndex: number, foodIndex: number) => {
    setSelectedFood(food);
    setSelectedMealIndex(mealIndex);
    setSelectedFoodIndex(foodIndex);
    setSubstitutionModal(true);
    setLoadingSubstitutes(true);

    try {
      if (userId && BACKEND_URL) {
        const response = await safeFetch(
          `${BACKEND_URL}/api/diet/${userId}/substitutes/${mealIndex}/${foodIndex}`
        );
        if (response.ok) {
          const data = await response.json();
          setSubstitutes(data.substitutes || []);
        }
      }
    } catch (error) {
      console.error('Error loading substitutes:', error);
    } finally {
      setLoadingSubstitutes(false);
    }
  };

  const handleSubstitute = async (substitute: any) => {
    try {
      if (userId && BACKEND_URL) {
        const response = await safeFetch(
          `${BACKEND_URL}/api/diet/${userId}/substitute/${selectedMealIndex}/${selectedFoodIndex}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_food_id: substitute.id }),
          }
        );
        if (response.ok) {
          setSubstitutionModal(false);
          await loadUserData();
        }
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível substituir o alimento');
    }
  };

  // Calculate totals
  const totalCalories = dietPlan?.meals?.reduce((sum: number, m: any) => sum + (m.calories || 0), 0) || 0;
  const totalProtein = dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + m.foods?.reduce((s: number, f: any) => s + (f.protein || 0), 0), 0) || 0;
  const totalCarbs = dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + m.foods?.reduce((s: number, f: any) => s + (f.carbs || 0), 0), 0) || 0;
  const totalFat = dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + m.foods?.reduce((s: number, f: any) => s + (f.fat || 0), 0), 0) || 0;

  if (initialLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <DietSkeleton />
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
              <Text style={[styles.headerTitle, { color: theme.text }]}>Sua Dieta</Text>
              <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
                {dietPlan?.meals?.length || 0} refeições planejadas
              </Text>
            </View>
            <TouchableOpacity 
              style={[styles.refreshButton, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.8)' }]}
              onPress={onRefresh}
            >
              <RefreshCw size={20} color={theme.text} />
            </TouchableOpacity>
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
              <View style={styles.summaryHeader}>
                <Flame size={20} color={premiumColors.primary} />
                <Text style={[styles.summaryTitle, { color: theme.text }]}>Resumo do Dia</Text>
              </View>
              <View style={styles.summaryStats}>
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: theme.text }]}>{Math.round(totalCalories)}</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>kcal</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: '#3B82F6' }]}>{Math.round(totalProtein)}g</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>Proteína</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: '#F59E0B' }]}>{Math.round(totalCarbs)}g</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>Carbs</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: '#EF4444' }]}>{Math.round(totalFat)}g</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>Gordura</Text>
                </View>
              </View>
            </GlassCard>
          </Animated.View>

          {/* Meals */}
          {dietPlan?.meals?.map((meal: any, index: number) => (
            <MealCard
              key={index}
              meal={meal}
              index={index}
              isDark={isDark}
              theme={theme}
              onFoodPress={handleFoodPress}
              language={language}
            />
          ))}

          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>

      {/* Substitution Modal */}
      <Modal visible={substitutionModal} transparent animationType="slide">
        <View style={[styles.modalOverlay, { backgroundColor: theme.overlay }]}>
          <View style={[styles.modalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: theme.text }]}>Substituir Alimento</Text>
              <TouchableOpacity onPress={() => setSubstitutionModal(false)}>
                <X size={24} color={theme.text} />
              </TouchableOpacity>
            </View>
            
            {selectedFood && (
              <View style={[styles.selectedFoodBanner, { backgroundColor: premiumColors.primary + '15' }]}>
                <Text style={[styles.selectedFoodText, { color: theme.text }]}>
                  {translateFood(selectedFood.name, language)} ({Math.round(selectedFood.grams)}g)
                </Text>
              </View>
            )}

            {loadingSubstitutes ? (
              <ActivityIndicator size="large" color={premiumColors.primary} style={{ marginVertical: 40 }} />
            ) : (
              <ScrollView style={styles.substitutesList}>
                {substitutes.map((sub, idx) => (
                  <TouchableOpacity
                    key={idx}
                    style={[styles.substituteItem, { borderBottomColor: theme.border }]}
                    onPress={() => handleSubstitute(sub)}
                  >
                    <View style={styles.substituteContent}>
                      <Text style={[styles.substituteName, { color: theme.text }]}>
                        {translateFood(sub.name, language)}
                      </Text>
                      <Text style={[styles.substituteGrams, { color: theme.textTertiary }]}>
                        {Math.round(sub.grams)}g
                      </Text>
                    </View>
                    <Check size={20} color={premiumColors.primary} />
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg, gap: spacing.lg },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  headerTitle: { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
  refreshButton: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },

  summaryCard: { padding: spacing.lg },
  summaryHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.md },
  summaryTitle: { fontSize: 16, fontWeight: '700' },
  summaryStats: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  summaryStat: { alignItems: 'center', flex: 1 },
  summaryValue: { fontSize: 22, fontWeight: '800', letterSpacing: -0.5 },
  summaryLabel: { fontSize: 11, fontWeight: '600', marginTop: 2 },
  summaryDivider: { width: 1, height: 36 },

  mealCard: { marginBottom: spacing.md },
  mealHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.base,
    gap: spacing.md,
  },
  mealIconBg: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mealHeaderContent: { flex: 1 },
  mealName: { fontSize: 16, fontWeight: '700', letterSpacing: -0.3 },
  mealTime: { fontSize: 13, marginTop: 2 },
  mealCaloriesBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
  },
  mealCaloriesText: { fontSize: 13, fontWeight: '700' },

  foodsList: { paddingHorizontal: spacing.base },
  foodItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    gap: spacing.md,
  },
  foodCategoryDot: { width: 8, height: 8, borderRadius: 4 },
  foodContent: { flex: 1 },
  foodName: { fontSize: 15, fontWeight: '600' },
  foodAmount: { fontSize: 13, marginTop: 2 },
  foodMacros: {},
  foodMacroText: { fontSize: 11, fontWeight: '500' },

  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  modalContent: {
    borderTopLeftRadius: radius['2xl'],
    borderTopRightRadius: radius['2xl'],
    maxHeight: '70%',
    padding: spacing.lg,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  selectedFoodBanner: {
    padding: spacing.md,
    borderRadius: radius.lg,
    marginBottom: spacing.lg,
  },
  selectedFoodText: { fontSize: 15, fontWeight: '600', textAlign: 'center' },
  substitutesList: { maxHeight: 300 },
  substituteItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  substituteContent: {},
  substituteName: { fontSize: 15, fontWeight: '600' },
  substituteGrams: { fontSize: 13, marginTop: 2 },
});
