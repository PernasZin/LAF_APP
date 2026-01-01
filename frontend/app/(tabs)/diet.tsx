import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

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

export default function DietScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);
  
  const [loading, setLoading] = useState(false);
  const [dietPlan, setDietPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);

  useFocusEffect(
    useCallback(() => {
      loadUserData();
    }, [])
  );

  const loadUserData = async () => {
    try {
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
      
      if (id && BACKEND_URL) {
        try {
          const profileResponse = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
          if (profileResponse.ok) {
            const data = await profileResponse.json();
            setUserProfile(data);
            await AsyncStorage.setItem('userProfile', JSON.stringify(data));
          }
        } catch (err) {
          const profileData = await AsyncStorage.getItem('userProfile');
          if (profileData) {
            setUserProfile(JSON.parse(profileData));
          }
        }
        loadDiet(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const loadDiet = async (uid: string) => {
    if (!uid || !BACKEND_URL) return;
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/diet/${uid}`);
      if (response.ok) {
        const data = await response.json();
        setDietPlan(data);
      }
    } catch (error: any) {
      console.log('Diet not loaded (may not exist yet)');
    }
  };

  const generateDiet = async () => {
    if (!userId || !BACKEND_URL) return;
    setLoading(true);
    try {
      const response = await safeFetch(
        `${BACKEND_URL}/api/diet/generate?user_id=${userId}`,
        { method: 'POST' }
      );
      if (response.ok) {
        const data = await response.json();
        setDietPlan(data);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        alert(`Erro ao gerar dieta: ${errorData.detail || 'Tente novamente'}`);
      }
    } catch (error) {
      console.error('Erro ao gerar dieta:', error);
      alert('Erro de conexão. Verifique sua internet e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.text }]}>Gerando seu plano de dieta...</Text>
          <Text style={[styles.loadingSubtext, { color: colors.textSecondary }]}>Isso pode levar alguns segundos</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!dietPlan) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} colors={[colors.primary]} />}
        >
          <Ionicons name="nutrition-outline" size={80} color={colors.textTertiary} />
          <Text style={[styles.emptyTitle, { color: colors.text }]}>Nenhuma dieta gerada</Text>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
            Gere seu plano alimentar personalizado baseado em seus objetivos
          </Text>
          <TouchableOpacity
            style={[styles.generateButton, { backgroundColor: colors.primary }]}
            onPress={generateDiet}
            activeOpacity={0.8}
          >
            <Ionicons name="sparkles" size={20} color={colors.textInverse} />
            <Text style={[styles.generateButtonText, { color: colors.textInverse }]}>Gerar Dieta com IA</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    );
  }

  const totalMealCalories = dietPlan.meals.reduce((sum: number, meal: any) => sum + meal.total_calories, 0);
  const totalMealMacros = dietPlan.meals.reduce(
    (acc: any, meal: any) => ({
      protein: acc.protein + meal.macros.protein,
      carbs: acc.carbs + meal.macros.carbs,
      fat: acc.fat + meal.macros.fat,
    }),
    { protein: 0, carbs: 0, fat: 0 }
  );
  const targetCalories = userProfile?.target_calories || dietPlan.target_calories;
  const targetMacros = userProfile?.macros || dietPlan.target_macros;
  const caloriesMatch = Math.abs(totalMealCalories - targetCalories) <= 50;
  const proteinMatch = Math.abs(totalMealMacros.protein - targetMacros.protein) <= 10;
  const carbsMatch = Math.abs(totalMealMacros.carbs - targetMacros.carbs) <= 10;
  const fatMatch = Math.abs(totalMealMacros.fat - targetMacros.fat) <= 10;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} colors={[colors.primary]} />}
      >
        <View style={styles.header}>
          <View>
            <Text style={[styles.headerTitle, { color: colors.text }]}>Seu Plano de Dieta</Text>
            <View style={styles.calorieRow}>
              <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
                Total: {Math.round(totalMealCalories)} kcal
              </Text>
              <Ionicons name={caloriesMatch ? "checkmark-circle" : "alert-circle"} size={16} color={caloriesMatch ? colors.success : colors.warning} style={{marginLeft: 6}} />
            </View>
            <Text style={[styles.headerTarget, { color: colors.textTertiary }]}>Meta: {Math.round(targetCalories)} kcal</Text>
          </View>
          <TouchableOpacity style={[styles.regenerateButton, { backgroundColor: colors.primary + '20' }]} onPress={generateDiet}>
            <Ionicons name="refresh" size={20} color={colors.primary} />
          </TouchableOpacity>
        </View>

        <View style={[styles.macrosCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.macrosTitle, { color: colors.textSecondary }]}>Macronutrientes (Total / Meta)</Text>
          <View style={styles.macrosRow}>
            <MacroItem label="Proteína" value={`${Math.round(totalMealMacros.protein)}g`} target={`${Math.round(targetMacros.protein)}g`} color="#3B82F6" match={proteinMatch} colors={colors} />
            <MacroItem label="Carboidratos" value={`${Math.round(totalMealMacros.carbs)}g`} target={`${Math.round(targetMacros.carbs)}g`} color="#F59E0B" match={carbsMatch} colors={colors} />
            <MacroItem label="Gorduras" value={`${Math.round(totalMealMacros.fat)}g`} target={`${Math.round(targetMacros.fat)}g`} color="#EF4444" match={fatMatch} colors={colors} />
          </View>
        </View>

        <Text style={[styles.mealsTitle, { color: colors.text }]}>Refeições do Dia</Text>
        {dietPlan.meals.map((meal: any, index: number) => (
          <MealCard key={meal.id || index} meal={meal} colors={colors} />
        ))}

        {dietPlan.notes && (
          <View style={[styles.notesCard, { backgroundColor: colors.warning + '20' }]}>
            <Ionicons name="information-circle-outline" size={20} color={colors.warning} />
            <Text style={[styles.notesText, { color: colors.text }]}>{dietPlan.notes}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function MacroItem({ label, value, target, color, match, colors }: any) {
  return (
    <View style={macroStyles.macroItem}>
      <View style={[macroStyles.macroIndicator, { backgroundColor: color }]} />
      <Text style={[macroStyles.macroLabel, { color: colors.textSecondary }]}>{label}</Text>
      <View style={macroStyles.macroValueRow}>
        <Text style={[macroStyles.macroValue, { color: colors.text }]}>{value}</Text>
        {match !== undefined && (
          <Ionicons name={match ? "checkmark-circle" : "alert-circle"} size={14} color={match ? colors.success : colors.warning} style={{marginLeft: 4}} />
        )}
      </View>
      {target && <Text style={[macroStyles.macroTarget, { color: colors.textTertiary }]}>Meta: {target}</Text>}
    </View>
  );
}

function MealCard({ meal, colors }: any) {
  const [expanded, setExpanded] = useState(false);
  const cardStyles = createCardStyles(colors);

  return (
    <View style={[cardStyles.mealCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
      <TouchableOpacity style={cardStyles.mealHeader} onPress={() => setExpanded(!expanded)} activeOpacity={0.7}>
        <View style={cardStyles.mealHeaderLeft}>
          <Ionicons name="restaurant-outline" size={24} color={colors.primary} />
          <View style={cardStyles.mealInfo}>
            <Text style={[cardStyles.mealName, { color: colors.text }]}>{meal.name}</Text>
            <Text style={[cardStyles.mealTime, { color: colors.textSecondary }]}>{meal.time}</Text>
          </View>
        </View>
        <View style={cardStyles.mealHeaderRight}>
          <Text style={[cardStyles.mealCalories, { color: colors.primary }]}>{Math.round(meal.total_calories)} kcal</Text>
          <Ionicons name={expanded ? 'chevron-up' : 'chevron-down'} size={20} color={colors.textSecondary} />
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={[cardStyles.mealDetails, { borderTopColor: colors.border }]}>
          {meal.foods.map((food: any, idx: number) => (
            <View key={idx} style={cardStyles.foodItem}>
              <Text style={[cardStyles.foodName, { color: colors.text }]}>{food.quantity} - {food.name}</Text>
              <Text style={[cardStyles.foodCalories, { color: colors.textSecondary }]}>{food.calories} kcal</Text>
            </View>
          ))}
          <View style={[cardStyles.mealMacros, { borderTopColor: colors.border }]}>
            <Text style={[cardStyles.mealMacrosText, { color: colors.textSecondary }]}>
              P: {meal.macros.protein}g • C: {meal.macros.carbs}g • G: {meal.macros.fat}g
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}

const macroStyles = StyleSheet.create({
  macroItem: { flex: 1, alignItems: 'center' },
  macroIndicator: { width: 4, height: 32, borderRadius: 2, marginBottom: 8 },
  macroLabel: { fontSize: 12, marginBottom: 4 },
  macroValue: { fontSize: 16, fontWeight: '700' },
  macroValueRow: { flexDirection: 'row', alignItems: 'center' },
  macroTarget: { fontSize: 11, marginTop: 2 },
});

const createCardStyles = (colors: any) => StyleSheet.create({
  mealCard: { borderRadius: 12, marginBottom: 12, borderWidth: 1 },
  mealHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  mealHeaderLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  mealInfo: { flex: 1 },
  mealName: { fontSize: 16, fontWeight: '600' },
  mealTime: { fontSize: 14, marginTop: 2 },
  mealHeaderRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  mealCalories: { fontSize: 14, fontWeight: '600' },
  mealDetails: { borderTopWidth: 1, padding: 16 },
  foodItem: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8 },
  foodName: { fontSize: 14, flex: 1 },
  foodCalories: { fontSize: 14 },
  mealMacros: { marginTop: 12, paddingTop: 12, borderTopWidth: 1 },
  mealMacrosText: { fontSize: 12, textAlign: 'center' },
});

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  loadingText: { fontSize: 18, fontWeight: '600', marginTop: 16 },
  loadingSubtext: { fontSize: 14, marginTop: 8 },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  emptyTitle: { fontSize: 20, fontWeight: '600', marginTop: 16 },
  emptyText: { fontSize: 14, textAlign: 'center', marginTop: 8, lineHeight: 20 },
  generateButton: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 14, paddingHorizontal: 24, borderRadius: 12, marginTop: 24 },
  generateButtonText: { fontSize: 16, fontWeight: '600' },
  scrollView: { flex: 1 },
  content: { padding: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  headerTitle: { fontSize: 24, fontWeight: '700' },
  headerSubtitle: { fontSize: 14, marginTop: 4 },
  headerTarget: { fontSize: 12, marginTop: 2 },
  calorieRow: { flexDirection: 'row', alignItems: 'center', marginTop: 4 },
  regenerateButton: { width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center' },
  macrosCard: { padding: 16, borderRadius: 12, marginBottom: 16, borderWidth: 1 },
  macrosTitle: { fontSize: 14, fontWeight: '600', marginBottom: 12 },
  macrosRow: { flexDirection: 'row', justifyContent: 'space-between' },
  mealsTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  notesCard: { flexDirection: 'row', gap: 12, padding: 12, borderRadius: 8, marginTop: 8 },
  notesText: { flex: 1, fontSize: 12, lineHeight: 18 },
});
