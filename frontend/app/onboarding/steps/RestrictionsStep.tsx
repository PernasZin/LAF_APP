import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { translations, SupportedLanguage } from '../../../i18n/translations';
import { foodTranslations } from '../../../i18n/dynamicTranslations';

interface Props {
  data: any;
  updateData: (data: any) => void;
  language: SupportedLanguage;
}

interface FoodItem {
  id: string;
  namePt: string; // Portuguese name (base)
  selectable: boolean;
}

// ============================================
// BANCO DE DADOS DE ALIMENTOS
// ============================================

// ATLETA: Lista restrita de alimentos limpos
const ATHLETE_FOODS: Record<string, FoodItem[]> = {
  proteins: [
    { id: 'chicken_breast', namePt: 'Peito de Frango', selectable: true },
    { id: 'lean_beef', namePt: 'Patinho', selectable: true },
    { id: 'eggs', namePt: 'Ovos Inteiros', selectable: true },
    { id: 'tilapia', namePt: 'Tilápia', selectable: true },
    { id: 'tuna', namePt: 'Atum', selectable: true },
    { id: 'salmon', namePt: 'Salmão', selectable: true },
    { id: 'greek_yogurt', namePt: 'Iogurte Grego', selectable: true },
  ],
  carbs: [
    { id: 'white_rice', namePt: 'Arroz Branco', selectable: true },
    { id: 'brown_rice', namePt: 'Arroz Integral', selectable: true },
    { id: 'sweet_potato', namePt: 'Batata Doce', selectable: true },
    { id: 'oats', namePt: 'Aveia', selectable: true },
    { id: 'pasta', namePt: 'Macarrão', selectable: true },
    { id: 'whole_pasta', namePt: 'Macarrão Integral', selectable: true },
    { id: 'whole_bread', namePt: 'Pão Integral', selectable: true },
    { id: 'bread_slice', namePt: 'Pão de Forma', selectable: true },
    { id: 'beans', namePt: 'Feijão', selectable: true },
  ],
  fats: [
    { id: 'olive_oil', namePt: 'Azeite de Oliva', selectable: true },
    { id: 'peanut_butter', namePt: 'Pasta de Amendoim', selectable: true },
    { id: 'nuts', namePt: 'Castanha', selectable: true },
    { id: 'almonds', namePt: 'Amêndoas', selectable: true },
  ],
  fruits: [
    { id: 'banana', namePt: 'Banana', selectable: true },
    { id: 'apple', namePt: 'Maçã', selectable: true },
    { id: 'orange', namePt: 'Laranja', selectable: true },
    { id: 'strawberry', namePt: 'Morango', selectable: true },
    { id: 'papaya', namePt: 'Mamão', selectable: true },
    { id: 'mango', namePt: 'Manga', selectable: true },
    { id: 'watermelon', namePt: 'Melancia', selectable: true },
    { id: 'avocado', namePt: 'Abacate', selectable: true },
  ],
  vegetables: [
    { id: 'broccoli', namePt: 'Brócolis', selectable: true },
    { id: 'spinach', namePt: 'Espinafre', selectable: true },
    { id: 'kale', namePt: 'Couve', selectable: true },
    { id: 'lettuce', namePt: 'Alface', selectable: true },
    { id: 'arugula', namePt: 'Rúcula', selectable: true },
    { id: 'cauliflower', namePt: 'Couve-flor', selectable: true },
    { id: 'carrot', namePt: 'Cenoura', selectable: true },
    { id: 'zucchini', namePt: 'Abobrinha', selectable: true },
    { id: 'tomato', namePt: 'Tomate', selectable: true },
    { id: 'cucumber', namePt: 'Pepino', selectable: true },
    { id: 'beetroot', namePt: 'Beterraba', selectable: true },
    { id: 'green_beans', namePt: 'Vagem', selectable: true },
    { id: 'bell_pepper', namePt: 'Pimentão', selectable: true },
  ],
  extras: [
    { id: 'honey', namePt: 'Mel', selectable: true },
    { id: 'condensed_milk', namePt: 'Leite Condensado', selectable: true },
  ],
  supplements: [
    { id: 'creatine', namePt: 'Creatina', selectable: true },
    { id: 'multivitamin', namePt: 'Multivitamínico', selectable: true },
    { id: 'omega3', namePt: 'Ômega 3', selectable: true },
    { id: 'caffeine', namePt: 'Cafeína', selectable: true },
    { id: 'whey', namePt: 'Whey Protein', selectable: true },
  ],
};

// GERAL: Lista de alimentos ATIVOS no sistema
const GENERAL_FOODS: Record<string, FoodItem[]> = {
  proteins: [
    { id: 'chicken_breast', namePt: 'Peito de Frango', selectable: true },
    { id: 'lean_beef', namePt: 'Patinho', selectable: true },
    { id: 'eggs', namePt: 'Ovos Inteiros', selectable: true },
    { id: 'tilapia', namePt: 'Tilápia', selectable: true },
    { id: 'tuna', namePt: 'Atum', selectable: true },
    { id: 'salmon', namePt: 'Salmão', selectable: true },
    { id: 'turkey', namePt: 'Peru', selectable: true },
    { id: 'greek_yogurt', namePt: 'Iogurte Grego', selectable: true },
    { id: 'natural_yogurt', namePt: 'Iogurte Natural', selectable: true },
  ],
  carbs: [
    { id: 'white_rice', namePt: 'Arroz Branco', selectable: true },
    { id: 'brown_rice', namePt: 'Arroz Integral', selectable: true },
    { id: 'sweet_potato', namePt: 'Batata Doce', selectable: true },
    { id: 'oats', namePt: 'Aveia', selectable: true },
    { id: 'pasta', namePt: 'Macarrão', selectable: true },
    { id: 'whole_pasta', namePt: 'Macarrão Integral', selectable: true },
    { id: 'bread', namePt: 'Pão Francês', selectable: true },
    { id: 'whole_bread', namePt: 'Pão Integral', selectable: true },
    { id: 'bread_slice', namePt: 'Pão de Forma', selectable: true },
    { id: 'beans', namePt: 'Feijão', selectable: true },
    { id: 'lentils', namePt: 'Lentilha', selectable: true },
    { id: 'tapioca', namePt: 'Tapioca', selectable: true },
    { id: 'farofa', namePt: 'Farofa', selectable: true },
    { id: 'granola', namePt: 'Granola', selectable: true },
  ],
  fats: [
    { id: 'olive_oil', namePt: 'Azeite de Oliva', selectable: true },
    { id: 'peanut_butter', namePt: 'Pasta de Amendoim', selectable: true },
    { id: 'nuts', namePt: 'Castanha', selectable: true },
    { id: 'almonds', namePt: 'Amêndoas', selectable: true },
    { id: 'walnuts', namePt: 'Nozes', selectable: true },
    { id: 'chia', namePt: 'Chia', selectable: true },
  ],
  fruits: [
    { id: 'banana', namePt: 'Banana', selectable: true },
    { id: 'apple', namePt: 'Maçã', selectable: true },
    { id: 'orange', namePt: 'Laranja', selectable: true },
    { id: 'strawberry', namePt: 'Morango', selectable: true },
    { id: 'papaya', namePt: 'Mamão', selectable: true },
    { id: 'mango', namePt: 'Manga', selectable: true },
    { id: 'watermelon', namePt: 'Melancia', selectable: true },
    { id: 'avocado', namePt: 'Abacate', selectable: true },
    { id: 'grape', namePt: 'Uva', selectable: true },
    { id: 'pineapple', namePt: 'Abacaxi', selectable: true },
    { id: 'melon', namePt: 'Melão', selectable: true },
    { id: 'kiwi', namePt: 'Kiwi', selectable: true },
    { id: 'pear', namePt: 'Pera', selectable: true },
    { id: 'peach', namePt: 'Pêssego', selectable: true },
  ],
  vegetables: [
    { id: 'broccoli', namePt: 'Brócolis', selectable: true },
    { id: 'spinach', namePt: 'Espinafre', selectable: true },
    { id: 'kale', namePt: 'Couve', selectable: true },
    { id: 'lettuce', namePt: 'Alface', selectable: true },
    { id: 'arugula', namePt: 'Rúcula', selectable: true },
    { id: 'cauliflower', namePt: 'Couve-flor', selectable: true },
    { id: 'carrot', namePt: 'Cenoura', selectable: true },
    { id: 'zucchini', namePt: 'Abobrinha', selectable: true },
    { id: 'tomato', namePt: 'Tomate', selectable: true },
    { id: 'cucumber', namePt: 'Pepino', selectable: true },
    { id: 'beetroot', namePt: 'Beterraba', selectable: true },
    { id: 'green_beans', namePt: 'Vagem', selectable: true },
    { id: 'bell_pepper', namePt: 'Pimentão', selectable: true },
  ],
  extras: [
    { id: 'honey', namePt: 'Mel', selectable: true },
    { id: 'condensed_milk', namePt: 'Leite Condensado', selectable: true },
  ],
  supplements: [
    { id: 'creatine', namePt: 'Creatina', selectable: true },
    { id: 'multivitamin', namePt: 'Multivitamínico', selectable: true },
    { id: 'omega3', namePt: 'Ômega 3', selectable: true },
    { id: 'caffeine', namePt: 'Cafeína', selectable: true },
    { id: 'vitamin_d', namePt: 'Vitamina D', selectable: true },
    { id: 'vitamin_c', namePt: 'Vitamina C', selectable: true },
    { id: 'zinc', namePt: 'Zinco', selectable: true },
    { id: 'magnesium', namePt: 'Magnésio', selectable: true },
    { id: 'collagen', namePt: 'Colágeno', selectable: true },
    { id: 'whey', namePt: 'Whey Protein', selectable: true },
  ],
};

// Additional supplement translations
const supplementTranslations: Record<string, Record<SupportedLanguage, string>> = {
  'Creatina': { 'pt-BR': 'Creatina', 'en-US': 'Creatine', 'es-ES': 'Creatina' },
  'Multivitamínico': { 'pt-BR': 'Multivitamínico', 'en-US': 'Multivitamin', 'es-ES': 'Multivitamínico' },
  'Ômega 3': { 'pt-BR': 'Ômega 3', 'en-US': 'Omega 3', 'es-ES': 'Omega 3' },
  'Cafeína': { 'pt-BR': 'Cafeína', 'en-US': 'Caffeine', 'es-ES': 'Cafeína' },
  'Vitamina D': { 'pt-BR': 'Vitamina D', 'en-US': 'Vitamin D', 'es-ES': 'Vitamina D' },
  'Vitamina C': { 'pt-BR': 'Vitamina C', 'en-US': 'Vitamin C', 'es-ES': 'Vitamina C' },
  'Zinco': { 'pt-BR': 'Zinco', 'en-US': 'Zinc', 'es-ES': 'Zinc' },
  'Magnésio': { 'pt-BR': 'Magnésio', 'en-US': 'Magnesium', 'es-ES': 'Magnesio' },
  'Colágeno': { 'pt-BR': 'Colágeno', 'en-US': 'Collagen', 'es-ES': 'Colágeno' },
};

// Helper function to translate food names
const translateFoodName = (namePt: string, language: SupportedLanguage): string => {
  // Check food translations first
  if (foodTranslations[namePt]?.[language]) {
    return foodTranslations[namePt][language];
  }
  // Check supplement translations
  if (supplementTranslations[namePt]?.[language]) {
    return supplementTranslations[namePt][language];
  }
  // Return Portuguese name as fallback
  return namePt;
};

export default function RestrictionsStep({ data, updateData, language }: Props) {
  const t = translations[language].onboarding;
  
  // Determina se é atleta
  const isAthlete = data.goal === 'atleta';
  
  // Seleciona o banco de dados baseado no objetivo
  const FOOD_DATABASE = isAthlete ? ATHLETE_FOODS : GENERAL_FOODS;

  // Categories with translations
  const CATEGORIES = [
    { key: 'proteins', label: t.proteins, icon: 'fitness-outline', color: '#EF4444', description: t.proteinsDesc },
    { key: 'carbs', label: t.carbs, icon: 'leaf-outline', color: '#F59E0B', description: t.carbsDesc },
    { key: 'fats', label: t.fats, icon: 'water-outline', color: '#3B82F6', description: t.fatsDesc },
    { key: 'fruits', label: t.fruits, icon: 'nutrition-outline', color: '#EC4899', description: t.fruitsDesc },
    { key: 'supplements', label: t.supplements, icon: 'flask-outline', color: '#8B5CF6', description: t.supplementsDesc },
  ];

  const dietaryOptions = [
    { key: 'Vegetariano', label: t.vegetarian },
    { key: 'Sem Lactose', label: t.lactoseFree },
    { key: 'Sem Glúten', label: t.glutenFree },
    { key: 'Low Carb', label: t.lowCarb },
  ];

  const toggleItem = (array: string[], item: string) => {
    if (array.includes(item)) {
      return array.filter((i) => i !== item);
    } else {
      return [...array, item];
    }
  };

  const isFoodSelected = (foodId: string) => {
    return data.food_preferences?.includes(foodId) || false;
  };

  const toggleFood = (foodId: string) => {
    const currentPrefs = data.food_preferences || [];
    updateData({
      food_preferences: toggleItem(currentPrefs, foodId),
    });
  };

  const selectedCount = data.food_preferences?.length || 0;

  // Descrição dinâmica baseada no objetivo
  const description = isAthlete ? t.foodPreferencesDescAthlete : t.foodPreferencesDescGeneral;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t.foodPreferences}</Text>
      <Text style={styles.description}>{description}</Text>

      {/* Badge do modo */}
      <View style={[styles.modeBadge, isAthlete ? styles.modeBadgeAthlete : styles.modeBadgeGeneral]}>
        <Ionicons 
          name={isAthlete ? 'trophy' : 'restaurant'} 
          size={16} 
          color={isAthlete ? '#F59E0B' : '#10B981'} 
        />
        <Text style={[styles.modeBadgeText, { color: isAthlete ? '#F59E0B' : '#10B981' }]}>
          {isAthlete ? t.athleteMode : t.flexibleMode}
        </Text>
      </View>

      {/* Restrições Dietéticas */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Ionicons name="warning-outline" size={20} color="#F59E0B" />
          <Text style={styles.sectionTitle}>{t.dietaryRestrictions}</Text>
        </View>
        <View style={styles.chipsContainer}>
          {dietaryOptions.map((option) => (
            <TouchableOpacity
              key={option.key}
              style={[
                styles.chip,
                data.dietary_restrictions?.includes(option.key) && styles.chipActive,
              ]}
              onPress={() =>
                updateData({
                  dietary_restrictions: toggleItem(
                    data.dietary_restrictions || [],
                    option.key
                  ),
                })
              }
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.chipText,
                  data.dietary_restrictions?.includes(option.key) && styles.chipTextActive,
                ]}
              >
                {option.label}
              </Text>
              {data.dietary_restrictions?.includes(option.key) && (
                <Ionicons name="checkmark" size={16} color="#10B981" />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Food Preferences by Category */}
      <View style={styles.foodSection}>
        <View style={styles.foodHeader}>
          <Text style={styles.foodTitle}>{t.availableFoods}</Text>
          <Text style={styles.selectedCount}>{selectedCount} {t.selected}</Text>
        </View>

        {CATEGORIES.map((category) => (
          <View key={category.key} style={styles.category}>
            <View style={[styles.categoryHeader, { backgroundColor: category.color + '15' }]}>
              <Ionicons name={category.icon as any} size={18} color={category.color} />
              <View style={styles.categoryTitleContainer}>
                <Text style={[styles.categoryTitle, { color: category.color }]}>
                  {category.label}
                </Text>
                <Text style={styles.categoryDescription}>{category.description}</Text>
              </View>
              {category.key === 'supplements' && (
                <View style={[styles.separateBadge, { backgroundColor: category.color }]}>
                  <Text style={styles.separateBadgeText}>{t.separate}</Text>
                </View>
              )}
            </View>
            <View style={styles.foodGrid}>
              {FOOD_DATABASE[category.key].map((food) => (
                <TouchableOpacity
                  key={food.id}
                  style={[
                    styles.foodChip,
                    isFoodSelected(food.id) && styles.foodChipActive,
                    isFoodSelected(food.id) && { borderColor: category.color },
                  ]}
                  onPress={() => toggleFood(food.id)}
                  activeOpacity={0.7}
                >
                  <Text
                    style={[
                      styles.foodChipText,
                      isFoodSelected(food.id) && styles.foodChipTextActive,
                      isFoodSelected(food.id) && { color: category.color },
                    ]}
                  >
                    {translateFoodName(food.namePt, language)}
                  </Text>
                  {isFoodSelected(food.id) && (
                    <Ionicons name="checkmark-circle" size={14} color={category.color} />
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ))}
      </View>

      <View style={styles.infoBox}>
        <Ionicons name="information-circle-outline" size={18} color="#6B7280" />
        <Text style={styles.infoText}>
          {isAthlete ? t.athleteInfoBox : t.generalInfoBox}
        </Text>
      </View>

      <Text style={styles.hint}>
        {t.skipHint}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 12,
    lineHeight: 24,
  },
  modeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginBottom: 20,
  },
  modeBadgeAthlete: {
    backgroundColor: '#FEF3C7',
  },
  modeBadgeGeneral: {
    backgroundColor: '#D1FAE5',
  },
  modeBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  chipActive: {
    borderColor: '#10B981',
    backgroundColor: '#F0FDF4',
  },
  chipText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6B7280',
  },
  chipTextActive: {
    color: '#10B981',
    fontWeight: '600',
  },
  foodSection: {
    flex: 1,
  },
  foodHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  foodTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  selectedCount: {
    fontSize: 13,
    color: '#10B981',
    fontWeight: '600',
  },
  category: {
    marginBottom: 16,
  },
  categoryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  categoryTitleContainer: {
    flex: 1,
  },
  categoryTitle: {
    fontSize: 14,
    fontWeight: '700',
  },
  categoryDescription: {
    fontSize: 11,
    color: '#6B7280',
    marginTop: 2,
  },
  separateBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  separateBadgeText: {
    color: '#fff',
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  foodGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  foodChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#E5E7EB',
    backgroundColor: '#fff',
  },
  foodChipActive: {
    backgroundColor: '#F0FDF4',
  },
  foodChipText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6B7280',
  },
  foodChipTextActive: {
    fontWeight: '600',
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#6B7280',
  },
  hint: {
    fontSize: 13,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 16,
  },
});
