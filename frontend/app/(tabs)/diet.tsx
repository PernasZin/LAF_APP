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
  ChevronRight, Check, X, Flame, Beef, Wheat, Droplets, AlertCircle
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { DietSkeleton } from '../../components';
import { useTranslation, translateFood, translateMealName, translateFoodPortion } from '../../i18n';

import { config } from '../../config';
const BACKEND_URL = config.BACKEND_URL;
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
              {Math.round(meal.total_calories || meal.calories || meal.foods?.reduce((s: number, f: any) => s + (f.calories || 0), 0) || 0)} kcal
            </Text>
          </View>
        </View>

        {/* Foods List */}
        <View style={styles.foodsList}>
          {meal.foods?.map((food: any, foodIndex: number) => {
            const catConfig = CATEGORY_CONFIG[food.category] || { color: '#6B7280', Icon: Utensils };
            const CatIcon = catConfig.Icon;
            
            // Traduzir porção
            const portionText = food.quantity_display || food.unit_equivalent 
              ? `${Math.round(food.grams)}g ${translateFoodPortion(food.unit_equivalent || '', language)}` 
              : `${Math.round(food.grams)}g`;
            
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
                    {portionText}
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
  const [generating, setGenerating] = useState(false);

  // Substitution modal
  const [substitutionModal, setSubstitutionModal] = useState(false);
  const [selectedFood, setSelectedFood] = useState<any>(null);
  const [selectedMealIndex, setSelectedMealIndex] = useState(-1);
  const [selectedFoodIndex, setSelectedFoodIndex] = useState(-1);
  const [substitutes, setSubstitutes] = useState<any[]>([]);
  const [loadingSubstitutes, setLoadingSubstitutes] = useState(false);

  useFocusEffect(
    useCallback(() => {
      console.log('🍽️ Diet screen focused - reloading data...');
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

  // Função para GERAR nova dieta
  const handleGenerateDiet = async () => {
    if (!userId || !BACKEND_URL) {
      Alert.alert('Erro', 'Usuário não identificado');
      return;
    }

    setGenerating(true);
    try {
      const response = await safeFetch(
        `${BACKEND_URL}/api/diet/generate?user_id=${userId}`,
        { method: 'POST' }
      );

      if (response.ok) {
        const data = await response.json();
        setDietPlan(data);
        Alert.alert('Sucesso!', 'Sua dieta foi gerada com sucesso!');
      } else {
        const errorData = await response.json().catch(() => ({}));
        Alert.alert('Erro', errorData.detail || 'Não foi possível gerar a dieta');
      }
    } catch (error) {
      console.error('Error generating diet:', error);
      Alert.alert('Erro', 'Falha na conexão. Tente novamente.');
    } finally {
      setGenerating(false);
    }
  };

  const handleFoodPress = async (food: any, mealIndex: number, foodIndex: number) => {
    setSelectedFood(food);
    setSelectedMealIndex(mealIndex);
    setSelectedFoodIndex(foodIndex);
    setSubstitutionModal(true);
    setLoadingSubstitutes(true);

    try {
      if (userId && BACKEND_URL && food.key) {
        const response = await safeFetch(
          `${BACKEND_URL}/api/diet/${userId}/substitutes/${food.key}`
        );
        if (response.ok) {
          const data = await response.json();
          setSubstitutes(data.substitutes || []);
        } else {
          setSubstitutes([]);
        }
      }
    } catch (error) {
      console.error('Error loading substitutes:', error);
      setSubstitutes([]);
    } finally {
      setLoadingSubstitutes(false);
    }
  };

  const handleSubstitute = async (substitute: any) => {
    try {
      if (userId && BACKEND_URL) {
        const response = await safeFetch(
          `${BACKEND_URL}/api/diet/${userId}/substitute`,
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              meal_index: selectedMealIndex,
              food_index: selectedFoodIndex,
              new_food_key: substitute.key 
            }),
          }
        );
        if (response.ok) {
          setSubstitutionModal(false);
          await loadUserData();
          Alert.alert('Sucesso', 'Alimento substituído com sucesso!');
        } else {
          Alert.alert('Erro', 'Não foi possível substituir o alimento');
        }
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível substituir o alimento');
    }
  };

  // Calculate totals from foods (more reliable)
  const totalCalories = dietPlan?.computed_calories || dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + (m.calories || m.total_calories || m.foods?.reduce((s: number, f: any) => s + (f.calories || 0), 0) || 0), 0) || 0;
  const totalProtein = dietPlan?.computed_macros?.protein || dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + (m.foods?.reduce((s: number, f: any) => s + (f.protein || 0), 0) || 0), 0) || 0;
  const totalCarbs = dietPlan?.computed_macros?.carbs || dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + (m.foods?.reduce((s: number, f: any) => s + (f.carbs || 0), 0) || 0), 0) || 0;
  const totalFat = dietPlan?.computed_macros?.fat || dietPlan?.meals?.reduce((sum: number, m: any) => 
    sum + (m.foods?.reduce((s: number, f: any) => s + (f.fat || 0), 0) || 0), 0) || 0;

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
              <Text style={[styles.headerTitle, { color: theme.text }]}>{t.diet.title}</Text>
              <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
                {dietPlan?.meals?.length || 0} {t.diet.mealsPlanned}
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
              <View style={styles.summaryHeader}>
                <Flame size={20} color={premiumColors.primary} />
                <Text style={[styles.summaryTitle, { color: theme.text }]}>{t.diet.daySummary}</Text>
              </View>
              <View style={styles.summaryStats}>
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: theme.text }]}>{Math.round(totalCalories)}</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>kcal</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: '#3B82F6' }]}>{Math.round(totalProtein)}g</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>{t.home.protein}</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: '#F59E0B' }]}>{Math.round(totalCarbs)}g</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>{t.home.carbs}</Text>
                </View>
                <View style={[styles.summaryDivider, { backgroundColor: theme.border }]} />
                <View style={styles.summaryStat}>
                  <Text style={[styles.summaryValue, { color: '#EF4444' }]}>{Math.round(totalFat)}g</Text>
                  <Text style={[styles.summaryLabel, { color: theme.textTertiary }]}>{t.home.fat}</Text>
                </View>
              </View>
            </GlassCard>
          </Animated.View>

          {/* Meals */}
          {dietPlan?.meals?.length > 0 ? (
            <>
              {dietPlan.meals.map((meal: any, index: number) => (
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
            </>
          ) : (
            /* Estado Vazio - Sem Dieta */
            <Animated.View entering={FadeInDown.delay(200).springify()}>
              <GlassCard isDark={isDark} style={styles.emptyStateCard}>
                <View style={styles.emptyStateContent}>
                  <View style={[styles.emptyIconBg, { backgroundColor: premiumColors.primary + '15' }]}>
                    <Utensils size={40} color={premiumColors.primary} strokeWidth={1.5} />
                  </View>
                  <Text style={[styles.emptyTitle, { color: theme.text }]}>
                    Nenhuma dieta gerada
                  </Text>
                  <Text style={[styles.emptyDescription, { color: theme.textSecondary }]}>
                    Gere sua dieta personalizada baseada no seu perfil e objetivos
                  </Text>
                  <TouchableOpacity
                    style={[styles.generateButton, { opacity: generating ? 0.7 : 1 }]}
                    onPress={handleGenerateDiet}
                    disabled={generating}
                  >
                    <LinearGradient
                      colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                      style={styles.generateButtonGradient}
                    >
                      {generating ? (
                        <ActivityIndicator size="small" color="#FFF" />
                      ) : (
                        <>
                          <ChefHat size={20} color="#FFF" strokeWidth={2} />
                          <Text style={styles.generateButtonText}>Gerar Minha Dieta</Text>
                        </>
                      )}
                    </LinearGradient>
                  </TouchableOpacity>
                </View>
              </GlassCard>
            </Animated.View>
          )}

          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>

      {/* Substitution Modal - Premium Design */}
      <Modal visible={substitutionModal} transparent animationType="slide">
        <View style={[styles.modalOverlay, { backgroundColor: 'rgba(0,0,0,0.6)' }]}>
          <View style={[styles.modalContent, { backgroundColor: theme.backgroundCardSolid }]}>
            {/* Header */}
            <View style={styles.modalHeader}>
              <View style={styles.modalHeaderLeft}>
                <View style={[styles.modalIconBg, { backgroundColor: premiumColors.primary + '15' }]}>
                  <RefreshCw size={20} color={premiumColors.primary} />
                </View>
                <View>
                  <Text style={[styles.modalTitle, { color: theme.text }]}>Substituir Alimento</Text>
                  <Text style={[styles.modalSubtitle, { color: theme.textSecondary }]}>
                    Escolha uma opção equivalente
                  </Text>
                </View>
              </View>
              <TouchableOpacity 
                onPress={() => setSubstitutionModal(false)} 
                style={[styles.modalCloseBtn, { backgroundColor: theme.border }]}
              >
                <X size={20} color={theme.text} />
              </TouchableOpacity>
            </View>
            
            {/* Current Food Banner */}
            {selectedFood && (
              <View style={[styles.currentFoodCard, { backgroundColor: isDark ? 'rgba(239, 68, 68, 0.1)' : 'rgba(239, 68, 68, 0.08)' }]}>
                <Text style={[styles.currentFoodLabel, { color: '#EF4444' }]}>ALIMENTO ATUAL</Text>
                <Text style={[styles.currentFoodName, { color: theme.text }]}>
                  {translateFood(selectedFood.name, language)}
                </Text>
                <View style={styles.currentFoodInfo}>
                  <Text style={[styles.currentFoodGrams, { color: theme.textSecondary }]}>
                    {selectedFood.unit_equivalent 
                      ? `${Math.round(selectedFood.grams)}g ${selectedFood.unit_equivalent}` 
                      : `${Math.round(selectedFood.grams)}g`}
                  </Text>
                  <View style={styles.currentFoodMacrosRow}>
                    <View style={[styles.macroChip, { backgroundColor: '#3B82F6' + '20' }]}>
                      <Text style={[styles.macroChipText, { color: '#3B82F6' }]}>P {Math.round(selectedFood.protein || 0)}g</Text>
                    </View>
                    <View style={[styles.macroChip, { backgroundColor: '#F59E0B' + '20' }]}>
                      <Text style={[styles.macroChipText, { color: '#F59E0B' }]}>C {Math.round(selectedFood.carbs || 0)}g</Text>
                    </View>
                    <View style={[styles.macroChip, { backgroundColor: '#10B981' + '20' }]}>
                      <Text style={[styles.macroChipText, { color: '#10B981' }]}>G {Math.round(selectedFood.fat || 0)}g</Text>
                    </View>
                  </View>
                </View>
              </View>
            )}

            {/* Substitutes List */}
            <Text style={[styles.substitutesLabel, { color: theme.textSecondary }]}>
              OPÇÕES DE SUBSTITUIÇÃO
            </Text>
            
            {loadingSubstitutes ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={premiumColors.primary} />
                <Text style={[styles.loadingText, { color: theme.textSecondary }]}>
                  Buscando alternativas...
                </Text>
              </View>
            ) : substitutes.length === 0 ? (
              <View style={styles.emptySubstitutes}>
                <AlertCircle size={40} color={theme.textTertiary} />
                <Text style={[styles.emptySubstitutesText, { color: theme.textSecondary }]}>
                  Nenhuma substituição disponível para este alimento
                </Text>
              </View>
            ) : (
              <ScrollView style={styles.substitutesList} showsVerticalScrollIndicator={false}>
                {substitutes.map((sub, idx) => (
                  <TouchableOpacity
                    key={idx}
                    style={[
                      styles.substituteCard, 
                      { 
                        backgroundColor: isDark ? 'rgba(16, 185, 129, 0.08)' : 'rgba(16, 185, 129, 0.05)',
                        borderColor: premiumColors.primary + '30'
                      }
                    ]}
                    onPress={() => handleSubstitute(sub)}
                    activeOpacity={0.7}
                  >
                    <View style={styles.substituteCardContent}>
                      <View style={styles.substituteCardHeader}>
                        <Text style={[styles.substituteCardName, { color: theme.text }]}>
                          {translateFood(sub.name, language)}
                        </Text>
                        <View style={[styles.substituteCalorieBadge, { backgroundColor: premiumColors.primary }]}>
                          <Text style={styles.substituteCalorieText}>{Math.round(sub.calories || 0)} kcal</Text>
                        </View>
                      </View>
                      <Text style={[styles.substituteCardGrams, { color: theme.textTertiary }]}>
                        {sub.unit_equivalent 
                          ? `${Math.round(sub.grams)}g ${sub.unit_equivalent}` 
                          : `${Math.round(sub.grams)}g`}
                      </Text>
                      <View style={styles.substituteCardMacros}>
                        <Text style={[styles.substituteCardMacro, { color: '#3B82F6' }]}>P {Math.round(sub.protein || 0)}g</Text>
                        <Text style={styles.macroSeparator}>•</Text>
                        <Text style={[styles.substituteCardMacro, { color: '#F59E0B' }]}>C {Math.round(sub.carbs || 0)}g</Text>
                        <Text style={styles.macroSeparator}>•</Text>
                        <Text style={[styles.substituteCardMacro, { color: '#10B981' }]}>G {Math.round(sub.fat || 0)}g</Text>
                      </View>
                    </View>
                    <View style={[styles.substituteSelectBtn, { backgroundColor: premiumColors.primary }]}>
                      <Check size={16} color="#FFF" strokeWidth={3} />
                    </View>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}
            
            {/* Cancel Button */}
            <TouchableOpacity 
              style={[styles.modalCancelBtn, { borderColor: theme.border }]}
              onPress={() => setSubstitutionModal(false)}
            >
              <Text style={[styles.modalCancelText, { color: theme.textSecondary }]}>Cancelar</Text>
            </TouchableOpacity>
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
  selectedFoodMacros: { fontSize: 13, textAlign: 'center', marginTop: 4 },
  substitutesList: { maxHeight: 350 },
  substituteItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  substituteContent: { flex: 1 },
  substituteName: { fontSize: 15, fontWeight: '600' },
  substituteGrams: { fontSize: 13, marginTop: 2 },
  substituteMacros: { fontSize: 12, marginTop: 2 },
  substituteCheck: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: spacing.md,
  },
  emptySubstitutes: {
    paddingVertical: spacing.xl,
    alignItems: 'center',
    gap: spacing.md,
  },
  emptySubstitutesText: {
    fontSize: 14,
    textAlign: 'center',
  },
  
  // Modal Premium Styles
  modalHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  modalIconBg: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  modalCloseBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  currentFoodCard: {
    padding: spacing.md,
    borderRadius: radius.lg,
    marginBottom: spacing.lg,
  },
  currentFoodLabel: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  currentFoodName: {
    fontSize: 16,
    fontWeight: '700',
  },
  currentFoodInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  currentFoodGrams: {
    fontSize: 14,
  },
  currentFoodMacrosRow: {
    flexDirection: 'row',
    gap: 6,
  },
  macroChip: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: radius.md,
  },
  macroChipText: {
    fontSize: 11,
    fontWeight: '600',
  },
  substitutesLabel: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
    gap: spacing.md,
  },
  loadingText: {
    fontSize: 14,
  },
  substituteCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1,
    marginBottom: spacing.sm,
  },
  substituteCardContent: {
    flex: 1,
  },
  substituteCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  substituteCardName: {
    fontSize: 15,
    fontWeight: '600',
    flex: 1,
  },
  substituteCalorieBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: radius.md,
    marginLeft: spacing.sm,
  },
  substituteCalorieText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#FFF',
  },
  substituteCardGrams: {
    fontSize: 12,
    marginBottom: 4,
  },
  substituteCardMacros: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  substituteCardMacro: {
    fontSize: 12,
    fontWeight: '600',
  },
  macroSeparator: {
    marginHorizontal: 4,
    color: '#9CA3AF',
  },
  substituteSelectBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: spacing.md,
  },
  modalCancelBtn: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1,
    marginTop: spacing.md,
  },
  modalCancelText: {
    fontSize: 14,
    fontWeight: '600',
  },

  // Empty State Styles
  emptyStateCard: { padding: spacing.xl },
  emptyStateContent: { alignItems: 'center', gap: spacing.md },
  emptyIconBg: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  emptyTitle: { fontSize: 20, fontWeight: '700', textAlign: 'center' },
  emptyDescription: { 
    fontSize: 14, 
    textAlign: 'center', 
    lineHeight: 20,
    paddingHorizontal: spacing.lg,
  },
  generateButton: { 
    marginTop: spacing.md,
    borderRadius: radius.xl,
    overflow: 'hidden',
  },
  generateButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
  },
  generateButtonText: { 
    color: '#FFF', 
    fontSize: 16, 
    fontWeight: '700',
  },
  regenerateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.lg,
    marginTop: spacing.sm,
  },
  regenerateButtonText: { fontSize: 14, fontWeight: '600' },
});
