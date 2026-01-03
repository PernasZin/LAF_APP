import React, { useEffect, useState, useCallback } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, RefreshControl, Modal, Alert 
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../theme/ThemeContext';
import { Toast, DietSkeleton } from '../../components';
import { useToast } from '../../hooks/useToast';

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

// Category labels in Portuguese
const CATEGORY_LABELS: Record<string, string> = {
  protein: 'Proteína',
  carb: 'Carboidrato',
  fat: 'Gordura',
  fruit: 'Fruta',
  vegetable: 'Vegetal',
};

const CATEGORY_COLORS: Record<string, string> = {
  protein: '#EF4444',
  carb: '#F59E0B',
  fat: '#3B82F6',
  fruit: '#EC4899',
  vegetable: '#10B981',
};

export default function DietScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);
  const { toast, showSuccess, showError, hideToast } = useToast();
  
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [dietPlan, setDietPlan] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  
  // Substitution modal state
  const [substitutionModal, setSubstitutionModal] = useState(false);
  const [selectedFood, setSelectedFood] = useState<any>(null);
  const [selectedMealIndex, setSelectedMealIndex] = useState<number>(-1);
  const [selectedFoodIndex, setSelectedFoodIndex] = useState<number>(-1);
  const [substitutes, setSubstitutes] = useState<any[]>([]);
  const [loadingSubstitutes, setLoadingSubstitutes] = useState(false);
  const [substituting, setSubstituting] = useState(false);

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
        await loadDiet(id);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setInitialLoading(false);
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
    
    // Se já tem dieta, não permite regenerar
    if (dietPlan) {
      Alert.alert(
        'Dieta Existente',
        'Você já possui uma dieta gerada. Para alterar, use a substituição de alimentos.',
        [{ text: 'OK' }]
      );
      return;
    }
    
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
        Alert.alert('Erro', `Erro ao gerar dieta: ${errorData.detail || 'Tente novamente'}`);
      }
    } catch (error) {
      console.error('Erro ao gerar dieta:', error);
      Alert.alert('Erro', 'Erro de conexão. Verifique sua internet e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  // Open substitution modal
  const openSubstitution = async (food: any, mealIndex: number, foodIndex: number) => {
    // Só permite substituição de categorias válidas
    if (!['protein', 'carb', 'fat', 'fruit'].includes(food.category)) {
      Alert.alert('Info', 'Este alimento não pode ser substituído (vegetais/saladas são fixos).');
      return;
    }
    
    setSelectedFood(food);
    setSelectedMealIndex(mealIndex);
    setSelectedFoodIndex(foodIndex);
    setSubstitutionModal(true);
    setLoadingSubstitutes(true);
    
    try {
      const response = await safeFetch(
        `${BACKEND_URL}/api/diet/${dietPlan.id}/substitutes/${food.key}`
      );
      if (response.ok) {
        const data = await response.json();
        setSubstitutes(data.substitutes || []);
      } else {
        setSubstitutes([]);
      }
    } catch (error) {
      console.error('Erro ao carregar substitutos:', error);
      setSubstitutes([]);
    } finally {
      setLoadingSubstitutes(false);
    }
  };

  // Perform substitution
  const performSubstitution = async (newFoodKey: string) => {
    if (!dietPlan || selectedMealIndex < 0 || selectedFoodIndex < 0) return;
    
    setSubstituting(true);
    
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/diet/${dietPlan.id}/substitute`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          meal_index: selectedMealIndex,
          food_index: selectedFoodIndex,
          new_food_key: newFoodKey,
        }),
      });
      
      if (response.ok) {
        const updatedDiet = await response.json();
        setDietPlan(updatedDiet);
        setSubstitutionModal(false);
        showSuccess('Alimento substituído com sucesso!');
      } else {
        const error = await response.json().catch(() => ({}));
        showError(error.detail || 'Não foi possível substituir o alimento.');
      }
    } catch (error) {
      console.error('Erro ao substituir:', error);
      showError('Erro de conexão ao substituir alimento.');
    } finally {
      setSubstituting(false);
    }
  };

  // Show skeleton while loading initially
  if (initialLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <DietSkeleton />
      </SafeAreaView>
    );
  }

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
            <Text style={[styles.generateButtonText, { color: colors.textInverse }]}>Gerar Minha Dieta</Text>
          </TouchableOpacity>
          <Text style={[styles.infoText, { color: colors.textTertiary }]}>
            A dieta será gerada uma única vez.{'\n'}Depois, ajuste via substituição de alimentos.
          </Text>
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
            <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
              {Math.round(totalMealCalories)} / {Math.round(targetCalories)} kcal
            </Text>
          </View>
        </View>

        {/* Macros Summary */}
        <View style={[styles.macrosCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.macrosRow}>
            <MacroItem 
              label="Proteína" 
              current={totalMealMacros.protein} 
              target={targetMacros.protein} 
              color="#EF4444" 
              colors={colors} 
            />
            <MacroItem 
              label="Carboidratos" 
              current={totalMealMacros.carbs} 
              target={targetMacros.carbs} 
              color="#F59E0B" 
              colors={colors} 
            />
            <MacroItem 
              label="Gorduras" 
              current={totalMealMacros.fat} 
              target={targetMacros.fat} 
              color="#3B82F6" 
              colors={colors} 
            />
          </View>
        </View>

        {/* Info about substitution */}
        <View style={[styles.infoBox, { backgroundColor: colors.primary + '15' }]}>
          <Ionicons name="swap-horizontal" size={18} color={colors.primary} />
          <Text style={[styles.infoBoxText, { color: colors.text }]}>
            Toque em um alimento para substituir
          </Text>
        </View>

        {/* Meals */}
        <Text style={[styles.mealsTitle, { color: colors.text }]}>Refeições do Dia</Text>
        {dietPlan.meals.map((meal: any, mealIndex: number) => (
          <MealCard 
            key={meal.id || mealIndex} 
            meal={meal} 
            mealIndex={mealIndex}
            colors={colors} 
            onFoodPress={openSubstitution}
          />
        ))}

        {/* Supplements */}
        {dietPlan.supplements && dietPlan.supplements.length > 0 && (
          <View style={[styles.supplementsCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.supplementsHeader}>
              <Ionicons name="flask-outline" size={20} color="#8B5CF6" />
              <Text style={[styles.supplementsTitle, { color: colors.text }]}>Suplementação</Text>
            </View>
            {dietPlan.supplements.map((supplement: string, idx: number) => (
              <Text key={idx} style={[styles.supplementItem, { color: colors.textSecondary }]}>
                • {supplement}
              </Text>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Substitution Modal */}
      <Modal
        visible={substitutionModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setSubstitutionModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.background }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>Substituir Alimento</Text>
              <TouchableOpacity onPress={() => setSubstitutionModal(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            {selectedFood && (
              <View style={[styles.currentFoodBox, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                <Text style={[styles.currentFoodLabel, { color: colors.textSecondary }]}>Alimento atual:</Text>
                <Text style={[styles.currentFoodName, { color: colors.text }]}>{selectedFood.name}</Text>
                <Text style={[styles.currentFoodMacros, { color: colors.textSecondary }]}>
                  {selectedFood.quantity} • P:{selectedFood.protein}g C:{selectedFood.carbs}g G:{selectedFood.fat}g
                </Text>
                <View style={[styles.categoryBadge, { backgroundColor: CATEGORY_COLORS[selectedFood.category] + '20' }]}>
                  <Text style={[styles.categoryBadgeText, { color: CATEGORY_COLORS[selectedFood.category] }]}>
                    {CATEGORY_LABELS[selectedFood.category]}
                  </Text>
                </View>
              </View>
            )}

            <Text style={[styles.substitutesLabel, { color: colors.text }]}>
              Escolha um substituto:
            </Text>

            {loadingSubstitutes ? (
              <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 20 }} />
            ) : substitutes.length === 0 ? (
              <Text style={[styles.noSubstitutes, { color: colors.textSecondary }]}>
                Nenhum substituto disponível para este alimento.
              </Text>
            ) : (
              <ScrollView style={styles.substitutesList}>
                {substitutes.map((sub, idx) => (
                  <TouchableOpacity
                    key={idx}
                    style={[styles.substituteItem, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}
                    onPress={() => performSubstitution(sub.key)}
                    disabled={substituting}
                    activeOpacity={0.7}
                  >
                    <View style={styles.substituteInfo}>
                      <Text style={[styles.substituteName, { color: colors.text }]}>{sub.name}</Text>
                      <Text style={[styles.substituteQuantity, { color: colors.primary }]}>{sub.quantity}</Text>
                    </View>
                    <Text style={[styles.substituteMacros, { color: colors.textSecondary }]}>
                      P:{sub.protein}g • C:{sub.carbs}g • G:{sub.fat}g • {sub.calories}kcal
                    </Text>
                    {substituting && (
                      <ActivityIndicator size="small" color={colors.primary} style={{ position: 'absolute', right: 16 }} />
                    )}
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

function MacroItem({ label, current, target, color, colors }: any) {
  const percentage = Math.min(100, (current / target) * 100);
  const isOnTarget = Math.abs(current - target) <= target * 0.1;
  
  return (
    <View style={macroStyles.macroItem}>
      <View style={[macroStyles.macroIndicator, { backgroundColor: color }]} />
      <Text style={[macroStyles.macroLabel, { color: colors.textSecondary }]}>{label}</Text>
      <Text style={[macroStyles.macroValue, { color: colors.text }]}>{Math.round(current)}g</Text>
      <Text style={[macroStyles.macroTarget, { color: colors.textTertiary }]}>/ {Math.round(target)}g</Text>
      <View style={[macroStyles.progressBar, { backgroundColor: colors.border }]}>
        <View style={[macroStyles.progressFill, { width: `${percentage}%`, backgroundColor: isOnTarget ? color : colors.warning }]} />
      </View>
    </View>
  );
}

function MealCard({ meal, mealIndex, colors, onFoodPress }: any) {
  const [expanded, setExpanded] = useState(true);
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
          {meal.foods.map((food: any, foodIndex: number) => (
            <TouchableOpacity 
              key={foodIndex} 
              style={cardStyles.foodItem}
              onPress={() => onFoodPress(food, mealIndex, foodIndex)}
              activeOpacity={0.7}
            >
              <View style={cardStyles.foodMain}>
                <View style={[cardStyles.foodCategoryDot, { backgroundColor: CATEGORY_COLORS[food.category] || '#9CA3AF' }]} />
                <View style={cardStyles.foodTextContainer}>
                  <Text style={[cardStyles.foodName, { color: colors.text }]}>{food.name}</Text>
                  <Text style={[cardStyles.foodQuantity, { color: colors.textSecondary }]}>{food.quantity}</Text>
                </View>
              </View>
              <View style={cardStyles.foodRight}>
                <Text style={[cardStyles.foodMacros, { color: colors.textTertiary }]}>
                  P:{food.protein}g C:{food.carbs}g G:{food.fat}g
                </Text>
                {['protein', 'carb', 'fat', 'fruit'].includes(food.category) && (
                  <Ionicons name="swap-horizontal-outline" size={16} color={colors.primary} style={{ marginLeft: 8 }} />
                )}
              </View>
            </TouchableOpacity>
          ))}
          <View style={[cardStyles.mealMacros, { borderTopColor: colors.border }]}>
            <Text style={[cardStyles.mealMacrosText, { color: colors.textSecondary }]}>
              Total: P:{meal.macros.protein}g • C:{meal.macros.carbs}g • G:{meal.macros.fat}g
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}

const macroStyles = StyleSheet.create({
  macroItem: { flex: 1, alignItems: 'center' },
  macroIndicator: { width: 4, height: 24, borderRadius: 2, marginBottom: 6 },
  macroLabel: { fontSize: 11, marginBottom: 2 },
  macroValue: { fontSize: 16, fontWeight: '700' },
  macroTarget: { fontSize: 11, marginTop: 1 },
  progressBar: { width: '80%', height: 4, borderRadius: 2, marginTop: 6 },
  progressFill: { height: '100%', borderRadius: 2 },
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
  mealDetails: { borderTopWidth: 1, paddingHorizontal: 16, paddingBottom: 16 },
  foodItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: colors.border },
  foodMain: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  foodCategoryDot: { width: 8, height: 8, borderRadius: 4, marginRight: 10 },
  foodTextContainer: { flex: 1 },
  foodName: { fontSize: 14, fontWeight: '500' },
  foodQuantity: { fontSize: 12, marginTop: 2 },
  foodRight: { flexDirection: 'row', alignItems: 'center' },
  foodMacros: { fontSize: 11 },
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
  infoText: { fontSize: 12, textAlign: 'center', marginTop: 16, lineHeight: 18 },
  scrollView: { flex: 1 },
  content: { padding: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  headerTitle: { fontSize: 24, fontWeight: '700' },
  headerSubtitle: { fontSize: 16, marginTop: 4 },
  macrosCard: { padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1 },
  macrosRow: { flexDirection: 'row', justifyContent: 'space-between' },
  infoBox: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 12, borderRadius: 8, marginBottom: 16 },
  infoBoxText: { fontSize: 13, flex: 1 },
  mealsTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  supplementsCard: { padding: 16, borderRadius: 12, marginTop: 8, borderWidth: 1 },
  supplementsHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
  supplementsTitle: { fontSize: 16, fontWeight: '600' },
  supplementItem: { fontSize: 14, paddingVertical: 4 },
  // Modal styles
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20, maxHeight: '80%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  currentFoodBox: { padding: 16, borderRadius: 12, marginBottom: 16, borderWidth: 1 },
  currentFoodLabel: { fontSize: 12, marginBottom: 4 },
  currentFoodName: { fontSize: 18, fontWeight: '600' },
  currentFoodMacros: { fontSize: 13, marginTop: 4 },
  categoryBadge: { alignSelf: 'flex-start', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, marginTop: 8 },
  categoryBadgeText: { fontSize: 12, fontWeight: '600' },
  substitutesLabel: { fontSize: 16, fontWeight: '600', marginBottom: 12 },
  noSubstitutes: { fontSize: 14, textAlign: 'center', marginTop: 20 },
  substitutesList: { maxHeight: 300 },
  substituteItem: { padding: 16, borderRadius: 12, marginBottom: 8, borderWidth: 1 },
  substituteInfo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  substituteName: { fontSize: 16, fontWeight: '600' },
  substituteQuantity: { fontSize: 14, fontWeight: '600' },
  substituteMacros: { fontSize: 12, marginTop: 4 },
});
