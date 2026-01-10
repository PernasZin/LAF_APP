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
import { useHaptics } from '../../hooks/useHaptics';
import { useTranslation, translateFood, translateMealName } from '../../i18n';

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

// Meal type icons and colors
const MEAL_CONFIG: Record<string, { icon: string; emoji: string; color: string }> = {
  'Café da Manhã': { icon: 'sunny-outline', emoji: '☀️', color: '#F59E0B' },
  'Lanche Manhã': { icon: 'cafe-outline', emoji: '🍎', color: '#10B981' },
  'Almoço': { icon: 'restaurant-outline', emoji: '🍽️', color: '#3B82F6' },
  'Lanche Tarde': { icon: 'nutrition-outline', emoji: '🍎', color: '#8B5CF6' },
  'Jantar': { icon: 'moon-outline', emoji: '🌙', color: '#6366F1' },
  'Ceia': { icon: 'bed-outline', emoji: '🌙', color: '#EC4899' },
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
  const { t, language } = useTranslation();
  const styles = createStyles(colors);
  const { toast, showSuccess, showError, hideToast } = useToast();
  const { lightImpact, successFeedback, errorFeedback, selectionFeedback } = useHaptics();
  
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
      } else if (response.status === 404) {
        // Dieta não existe - tenta gerar automaticamente
        console.log('Dieta não encontrada, gerando automaticamente...');
        setDietPlan(null);
        // Gera nova dieta automaticamente
        try {
          const genResponse = await safeFetch(
            `${BACKEND_URL}/api/diet/generate?user_id=${uid}`,
            { method: 'POST' }
          );
          if (genResponse.ok) {
            const newDiet = await genResponse.json();
            setDietPlan(newDiet);
            console.log('✅ Nova dieta gerada automaticamente');
          }
        } catch (genErr) {
          console.log('Erro ao gerar dieta automaticamente:', genErr);
        }
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
    selectionFeedback(); // Haptic ao iniciar
    
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
        successFeedback(); // Haptic de sucesso
        showSuccess('Alimento substituído com sucesso!');
      } else {
        const error = await response.json().catch(() => ({}));
        errorFeedback(); // Haptic de erro
        showError(error.detail || 'Não foi possível substituir o alimento.');
      }
    } catch (error) {
      console.error('Erro ao substituir:', error);
      errorFeedback(); // Haptic de erro
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
          <View style={{ flex: 1 }}>
            <Text style={[styles.headerTitle, { color: colors.text }]}>{t.diet.title}</Text>
            <Text style={[styles.headerSubtitle, { color: colors.textSecondary }]}>
              {Math.round(totalMealCalories)} / {Math.round(targetCalories)} kcal
            </Text>
          </View>
          {/* Athlete Phase Badge */}
          {userProfile?.athlete_mode && (
            <AthletePhaseBadge 
              phase={userProfile.competition_phase || userProfile.last_competition_phase} 
              colors={colors}
            />
          )}
        </View>

        {/* Macros Summary */}
        <View style={[styles.macrosCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.macrosRow}>
            <MacroItem 
              label={t.home.protein} 
              current={totalMealMacros.protein} 
              target={targetMacros.protein} 
              color="#EF4444" 
              colors={colors} 
            />
            <MacroItem 
              label={t.home.carbs} 
              current={totalMealMacros.carbs} 
              target={targetMacros.carbs} 
              color="#F59E0B" 
              colors={colors} 
            />
            <MacroItem 
              label={t.home.fat} 
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
            {t.diet.tapToSubstitute}
          </Text>
        </View>

        {/* Athlete Mode - Next Adjustment Card */}
        {userProfile?.athlete_mode && (
          <AthleteAdjustmentCard colors={colors} userProfile={userProfile} />
        )}

        {/* Meals */}
        <Text style={[styles.mealsTitle, { color: colors.text }]}>{t.diet.mealsOfDay}</Text>
        {dietPlan.meals.map((meal: any, mealIndex: number) => (
          <MealCard 
            key={meal.id || mealIndex} 
            meal={meal} 
            mealIndex={mealIndex}
            colors={colors} 
            onFoodPress={openSubstitution}
            language={language}
          />
        ))}

        {/* Supplements */}
        {dietPlan.supplements && dietPlan.supplements.length > 0 && (
          <View style={[styles.supplementsCard, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.supplementsHeader}>
              <Ionicons name="flask-outline" size={20} color="#8B5CF6" />
              <Text style={[styles.supplementsTitle, { color: colors.text }]}>{t.diet.supplements}</Text>
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
              <Text style={[styles.modalTitle, { color: colors.text }]}>{t.diet.substituteFood}</Text>
              <TouchableOpacity onPress={() => setSubstitutionModal(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            {selectedFood && (
              <View style={[styles.currentFoodBox, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
                <Text style={[styles.currentFoodLabel, { color: colors.textSecondary }]}>{t.diet.currentFood}:</Text>
                <Text style={[styles.currentFoodName, { color: colors.text }]}>{translateFood(selectedFood.name, language)}</Text>
                <Text style={[styles.currentFoodMacros, { color: colors.textSecondary }]}>
                  {selectedFood.quantity} • P:{selectedFood.protein}g C:{selectedFood.carbs}g G:{selectedFood.fat}g
                </Text>
                <View style={[styles.categoryBadge, { backgroundColor: CATEGORY_COLORS[selectedFood.category] + '20' }]}>
                  <Text style={[styles.categoryBadgeText, { color: CATEGORY_COLORS[selectedFood.category] }]}>
                    {t.diet.categories[selectedFood.category as keyof typeof t.diet.categories] || CATEGORY_LABELS[selectedFood.category]}
                  </Text>
                </View>
              </View>
            )}

            <Text style={[styles.substitutesLabel, { color: colors.text }]}>
              {t.diet.chooseSubstitute}:
            </Text>

            {loadingSubstitutes ? (
              <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 20 }} />
            ) : substitutes.length === 0 ? (
              <Text style={[styles.noSubstitutes, { color: colors.textSecondary }]}>
                {t.diet.noSubstitutes}
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
                      <Text style={[styles.substituteName, { color: colors.text }]}>{translateFood(sub.name, language)}</Text>
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

      {/* Toast notification */}
      <Toast
        visible={toast.visible}
        message={toast.message}
        type={toast.type}
        onHide={hideToast}
      />
    </SafeAreaView>
  );
}

// ==================== ATHLETE ADJUSTMENT CARD ====================
function AthleteAdjustmentCard({ colors, userProfile }: any) {
  const [lastWeightRecord, setLastWeightRecord] = useState<any>(null);
  
  useEffect(() => {
    loadLastWeight();
  }, [userProfile]);
  
  const loadLastWeight = async () => {
    try {
      const userId = userProfile?.id;
      if (!userId) return;
      
      const response = await safeFetch(`${BACKEND_URL}/api/progress/weight/${userId}?days=30`);
      if (response.ok) {
        const data = await response.json();
        if (data.history && data.history.length > 0) {
          const lastRecord = data.history[data.history.length - 1];
          setLastWeightRecord(lastRecord);
        }
      }
    } catch (error) {
      console.log('Could not load weight history');
    }
  };
  
  // Calcular próximo ajuste
  const calculateNextAdjustment = () => {
    if (!lastWeightRecord?.recorded_at) {
      return { canRecord: true, daysRemaining: 0, nextDate: 'Agora' };
    }
    
    const lastDate = new Date(lastWeightRecord.recorded_at);
    const nextDate = new Date(lastDate);
    nextDate.setDate(nextDate.getDate() + 14);
    
    const now = new Date();
    const diffTime = nextDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 0) {
      return { canRecord: true, daysRemaining: 0, nextDate: 'Agora' };
    }
    
    return {
      canRecord: false,
      daysRemaining: diffDays,
      nextDate: nextDate.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    };
  };
  
  const adjustment = calculateNextAdjustment();
  const phase = userProfile?.competition_phase || userProfile?.last_competition_phase || 'off_season';
  
  const PHASE_INFO: Record<string, { label: string; color: string; icon: string }> = {
    'off_season': { label: 'Off-Season', color: '#10B981', icon: 'leaf-outline' },
    'pre_prep': { label: 'Pré-Prep', color: '#F59E0B', icon: 'trending-up-outline' },
    'prep': { label: 'Preparação', color: '#EF4444', icon: 'flame-outline' },
    'peak_week': { label: 'Peak Week', color: '#8B5CF6', icon: 'flash-outline' },
    'post_show': { label: 'Pós-Show', color: '#3B82F6', icon: 'heart-outline' },
  };
  
  const phaseInfo = PHASE_INFO[phase] || PHASE_INFO['off_season'];
  
  return (
    <View style={[athleteCardStyles.container, { backgroundColor: colors.backgroundCard, borderColor: phaseInfo.color + '50' }]}>
      <View style={athleteCardStyles.header}>
        <View style={[athleteCardStyles.phaseIcon, { backgroundColor: phaseInfo.color + '20' }]}>
          <Ionicons name={phaseInfo.icon as any} size={20} color={phaseInfo.color} />
        </View>
        <View style={athleteCardStyles.headerText}>
          <Text style={[athleteCardStyles.title, { color: colors.text }]}>Modo Atleta</Text>
          <Text style={[athleteCardStyles.phase, { color: phaseInfo.color }]}>{phaseInfo.label}</Text>
        </View>
        <View style={[athleteCardStyles.badge, { backgroundColor: phaseInfo.color }]}>
          <Text style={athleteCardStyles.badgeText}>ATIVO</Text>
        </View>
      </View>
      
      <View style={[athleteCardStyles.divider, { backgroundColor: colors.border }]} />
      
      <View style={athleteCardStyles.adjustmentInfo}>
        <Ionicons name="calendar-outline" size={18} color={colors.textSecondary} />
        <View style={athleteCardStyles.adjustmentTextContainer}>
          <Text style={[athleteCardStyles.adjustmentLabel, { color: colors.textSecondary }]}>
            Próximo ajuste automático:
          </Text>
          {adjustment.canRecord ? (
            <Text style={[athleteCardStyles.adjustmentValue, { color: colors.success }]}>
              Disponível agora!
            </Text>
          ) : (
            <Text style={[athleteCardStyles.adjustmentValue, { color: colors.text }]}>
              Em {adjustment.daysRemaining} dias ({adjustment.nextDate})
            </Text>
          )}
        </View>
      </View>
      
      <Text style={[athleteCardStyles.hint, { color: colors.textTertiary }]}>
        💡 Registre seu peso na aba Progresso para ajuste automático da dieta
      </Text>
    </View>
  );
}

const athleteCardStyles = StyleSheet.create({
  container: { borderRadius: 16, padding: 16, marginBottom: 16, borderWidth: 1.5 },
  header: { flexDirection: 'row', alignItems: 'center' },
  phaseIcon: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  headerText: { flex: 1, marginLeft: 12 },
  title: { fontSize: 14, fontWeight: '600' },
  phase: { fontSize: 16, fontWeight: '700', marginTop: 2 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  badgeText: { color: '#fff', fontSize: 10, fontWeight: '700' },
  divider: { height: 1, marginVertical: 12 },
  adjustmentInfo: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  adjustmentTextContainer: { flex: 1 },
  adjustmentLabel: { fontSize: 12 },
  adjustmentValue: { fontSize: 14, fontWeight: '600', marginTop: 2 },
  hint: { fontSize: 11, marginTop: 12, lineHeight: 16 },
});

// ==================== ATHLETE PHASE BADGE (COMPACT) ====================
function AthletePhaseBadge({ phase, colors }: { phase: string; colors: any }) {
  const PHASE_BADGE_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
    'off_season': { label: 'OFF', color: '#10B981', icon: 'leaf' },
    'pre_prep': { label: 'PRÉ', color: '#F59E0B', icon: 'trending-up' },
    'prep': { label: 'PREP', color: '#EF4444', icon: 'flame' },
    'peak_week': { label: 'PEAK', color: '#8B5CF6', icon: 'flash' },
    'post_show': { label: 'PÓS', color: '#3B82F6', icon: 'heart' },
  };

  const config = PHASE_BADGE_CONFIG[phase] || PHASE_BADGE_CONFIG['prep'];

  return (
    <View style={[phaseBadgeStyles.container, { backgroundColor: config.color + '15', borderColor: config.color }]}>
      <Ionicons name={config.icon as any} size={14} color={config.color} />
      <Text style={[phaseBadgeStyles.label, { color: config.color }]}>{config.label}</Text>
    </View>
  );
}

const phaseBadgeStyles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1.5,
  },
  label: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
});

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

function MealCard({ meal, mealIndex, colors, onFoodPress, language }: any) {
  const [expanded, setExpanded] = useState(true);
  const cardStyles = createCardStyles(colors);
  
  // Get meal config for icon/color
  const mealConfig = MEAL_CONFIG[meal.name] || { icon: 'restaurant-outline', emoji: '🍽️', color: colors.primary };
  
  // Translate meal name
  const translatedMealName = translateMealName(meal.name, language);

  return (
    <View style={[cardStyles.mealCard, { backgroundColor: colors.backgroundCard, borderColor: mealConfig.color + '30' }]}>
      <TouchableOpacity style={cardStyles.mealHeader} onPress={() => setExpanded(!expanded)} activeOpacity={0.7}>
        <View style={cardStyles.mealHeaderLeft}>
          <View style={[cardStyles.mealIconContainer, { backgroundColor: mealConfig.color + '20' }]}>
            <Text style={cardStyles.mealEmoji}>{mealConfig.emoji}</Text>
          </View>
          <View style={cardStyles.mealInfo}>
            <Text style={[cardStyles.mealName, { color: colors.text }]}>{translatedMealName}</Text>
            <Text style={[cardStyles.mealTime, { color: colors.textSecondary }]}>⏰ {meal.time}</Text>
          </View>
        </View>
        <View style={cardStyles.mealHeaderRight}>
          <Text style={[cardStyles.mealCalories, { color: mealConfig.color }]}>{Math.round(meal.total_calories)} kcal</Text>
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
                  <Text style={[cardStyles.foodName, { color: colors.text }]}>{translateFood(food.name, language)}</Text>
                  <Text style={[cardStyles.foodQuantity, { color: colors.textSecondary }]}>
                    {food.quantity_display || food.quantity}
                  </Text>
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
  mealCard: { borderRadius: 16, marginBottom: 12, borderWidth: 1.5 },
  mealHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  mealHeaderLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  mealIconContainer: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  mealEmoji: { fontSize: 22 },
  mealInfo: { flex: 1 },
  mealName: { fontSize: 16, fontWeight: '700' },
  mealTime: { fontSize: 13, marginTop: 2 },
  mealHeaderRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  mealCalories: { fontSize: 15, fontWeight: '700' },
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
