import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function DietScreen() {
  const [loading, setLoading] = useState(false);
  const [dietPlan, setDietPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserId();
  }, []);

  useEffect(() => {
    if (userId) {
      loadDiet();
    }
  }, [userId]);

  const loadUserId = async () => {
    try {
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
    } catch (error) {
      console.error('Erro ao carregar userId:', error);
    }
  };

  const loadDiet = async () => {
    if (!userId) return;
    
    try {
      const response = await axios.get(`${BACKEND_URL}/api/diet/${userId}`);
      setDietPlan(response.data);
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Erro ao carregar dieta:', error);
      }
    }
  };

  const generateDiet = async () => {
    if (!userId) return;
    
    setLoading(true);
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/diet/generate?user_id=${userId}`
      );
      setDietPlan(response.data);
    } catch (error) {
      console.error('Erro ao gerar dieta:', error);
      alert('Erro ao gerar dieta. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDiet();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#10B981" />
          <Text style={styles.loadingText}>Gerando seu plano de dieta...</Text>
          <Text style={styles.loadingSubtext}>Isso pode levar alguns segundos</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!dietPlan) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
          <Ionicons name="nutrition-outline" size={80} color="#D1D5DB" />
          <Text style={styles.emptyTitle}>Nenhuma dieta gerada</Text>
          <Text style={styles.emptyText}>
            Gere seu plano alimentar personalizado baseado em seus objetivos
          </Text>
          <TouchableOpacity
            style={styles.generateButton}
            onPress={generateDiet}
            activeOpacity={0.8}
          >
            <Ionicons name="sparkles" size={20} color="#fff" />
            <Text style={styles.generateButtonText}>Gerar Dieta com IA</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Calcula o total real das calorias das refeições
  const totalMealCalories = dietPlan.meals.reduce(
    (sum: number, meal: any) => sum + meal.total_calories,
    0
  );

  // Calcula o total de macros das refeições
  const totalMealMacros = dietPlan.meals.reduce(
    (acc: any, meal: any) => ({
      protein: acc.protein + meal.macros.protein,
      carbs: acc.carbs + meal.macros.carbs,
      fat: acc.fat + meal.macros.fat,
    }),
    { protein: 0, carbs: 0, fat: 0 }
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>Seu Plano de Dieta</Text>
            <Text style={styles.headerSubtitle}>
              {Math.round(dietPlan.target_calories)} kcal/dia
            </Text>
          </View>
          <TouchableOpacity
            style={styles.regenerateButton}
            onPress={generateDiet}
          >
            <Ionicons name="refresh" size={20} color="#10B981" />
          </TouchableOpacity>
        </View>

        {/* Macros Summary */}
        <View style={styles.macrosCard}>
          <Text style={styles.macrosTitle}>Macronutrientes Diários</Text>
          <View style={styles.macrosRow}>
            <MacroItem
              label="Proteína"
              value={`${dietPlan.target_macros.protein}g`}
              color="#3B82F6"
            />
            <MacroItem
              label="Carboidratos"
              value={`${dietPlan.target_macros.carbs}g`}
              color="#F59E0B"
            />
            <MacroItem
              label="Gorduras"
              value={`${dietPlan.target_macros.fat}g`}
              color="#EF4444"
            />
          </View>
        </View>

        {/* Meals */}
        <Text style={styles.mealsTitle}>Refeições do Dia</Text>
        {dietPlan.meals.map((meal: any, index: number) => (
          <MealCard key={meal.id || index} meal={meal} />
        ))}

        {/* Notes */}
        {dietPlan.notes && (
          <View style={styles.notesCard}>
            <Ionicons name="information-circle-outline" size={20} color="#6B7280" />
            <Text style={styles.notesText}>{dietPlan.notes}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function MacroItem({ label, value, color }: any) {
  return (
    <View style={styles.macroItem}>
      <View style={[styles.macroIndicator, { backgroundColor: color }]} />
      <Text style={styles.macroLabel}>{label}</Text>
      <Text style={styles.macroValue}>{value}</Text>
    </View>
  );
}

function MealCard({ meal }: any) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={styles.mealCard}>
      <TouchableOpacity
        style={styles.mealHeader}
        onPress={() => setExpanded(!expanded)}
        activeOpacity={0.7}
      >
        <View style={styles.mealHeaderLeft}>
          <Ionicons name="restaurant-outline" size={24} color="#10B981" />
          <View style={styles.mealInfo}>
            <Text style={styles.mealName}>{meal.name}</Text>
            <Text style={styles.mealTime}>{meal.time}</Text>
          </View>
        </View>
        <View style={styles.mealHeaderRight}>
          <Text style={styles.mealCalories}>{Math.round(meal.total_calories)} kcal</Text>
          <Ionicons
            name={expanded ? 'chevron-up' : 'chevron-down'}
            size={20}
            color="#6B7280"
          />
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.mealDetails}>
          {meal.foods.map((food: any, idx: number) => (
            <View key={idx} style={styles.foodItem}>
              <Text style={styles.foodName}>
                {food.quantity} - {food.name}
              </Text>
              <Text style={styles.foodCalories}>{food.calories} kcal</Text>
            </View>
          ))}
          <View style={styles.mealMacros}>
            <Text style={styles.mealMacrosText}>
              P: {meal.macros.protein}g • C: {meal.macros.carbs}g • G: {meal.macros.fat}g
            </Text>
          </View>
        </View>
      )}
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
    padding: 32,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  emptyText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
  generateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#10B981',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginTop: 24,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  regenerateButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F0FDF4',
    alignItems: 'center',
    justifyContent: 'center',
  },
  macrosCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  macrosTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 12,
  },
  macrosRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  macroItem: {
    flex: 1,
    alignItems: 'center',
  },
  macroIndicator: {
    width: 4,
    height: 32,
    borderRadius: 2,
    marginBottom: 8,
  },
  macroLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  macroValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
  },
  mealsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  mealCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  mealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  mealHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  mealInfo: {
    flex: 1,
  },
  mealName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  mealTime: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  mealHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  mealCalories: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
  },
  mealDetails: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    padding: 16,
  },
  foodItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  foodName: {
    fontSize: 14,
    color: '#374151',
    flex: 1,
  },
  foodCalories: {
    fontSize: 14,
    color: '#6B7280',
  },
  mealMacros: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  mealMacrosText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  notesCard: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  notesText: {
    flex: 1,
    fontSize: 12,
    color: '#92400E',
    lineHeight: 18,
  },
});
