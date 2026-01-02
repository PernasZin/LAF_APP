import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

// Food Database with SEPARATE Categories
interface FoodItem {
  id: string;
  name: string;
}

const FOOD_DATABASE: Record<string, FoodItem[]> = {
  carbs: [
    { id: 'rice', name: 'Arroz' },
    { id: 'brown_rice', name: 'Arroz Integral' },
    { id: 'sweet_potato', name: 'Batata Doce' },
    { id: 'potato', name: 'Batata Inglesa' },
    { id: 'oats', name: 'Aveia' },
    { id: 'pasta', name: 'Macarrão' },
    { id: 'integral_pasta', name: 'Macarrão Integral' },
    { id: 'bread', name: 'Pão' },
    { id: 'integral_bread', name: 'Pão Integral' },
    { id: 'tapioca', name: 'Tapioca' },
    { id: 'cassava', name: 'Mandioca' },
    { id: 'corn', name: 'Milho' },
    { id: 'beans', name: 'Feijão' },
    { id: 'lentils', name: 'Lentilha' },
    { id: 'chickpeas', name: 'Grão de Bico' },
  ],
  proteins: [
    { id: 'chicken', name: 'Frango' },
    { id: 'beef', name: 'Carne Bovina' },
    { id: 'pork', name: 'Carne Suína' },
    { id: 'fish', name: 'Peixe' },
    { id: 'tilapia', name: 'Tilápia' },
    { id: 'salmon', name: 'Salmão' },
    { id: 'tuna', name: 'Atum' },
    { id: 'shrimp', name: 'Camarão' },
    { id: 'eggs', name: 'Ovos' },
    { id: 'egg_whites', name: 'Clara de Ovo' },
    { id: 'greek_yogurt', name: 'Iogurte Grego' },
    { id: 'cottage', name: 'Queijo Cottage' },
    { id: 'turkey', name: 'Peru' },
    { id: 'ham', name: 'Presunto' },
  ],
  fats: [
    { id: 'olive_oil', name: 'Azeite de Oliva' },
    { id: 'coconut_oil', name: 'Óleo de Coco' },
    { id: 'avocado', name: 'Abacate' },
    { id: 'nuts', name: 'Castanhas' },
    { id: 'almonds', name: 'Amêndoas' },
    { id: 'walnuts', name: 'Nozes' },
    { id: 'brazil_nuts', name: 'Castanha do Pará' },
    { id: 'peanuts', name: 'Amendoim' },
    { id: 'peanut_butter', name: 'Pasta de Amendoim' },
    { id: 'seeds', name: 'Sementes (chia, linhaça)' },
    { id: 'butter', name: 'Manteiga' },
    { id: 'cheese', name: 'Queijo' },
    { id: 'cream_cheese', name: 'Cream Cheese' },
    { id: 'heavy_cream', name: 'Creme de Leite' },
  ],
  // ========== FRUTAS - CATEGORIA SEPARADA ==========
  fruits: [
    { id: 'banana', name: 'Banana' },
    { id: 'apple', name: 'Maçã' },
    { id: 'orange', name: 'Laranja' },
    { id: 'berries', name: 'Frutas Vermelhas' },
    { id: 'mango', name: 'Manga' },
    { id: 'papaya', name: 'Mamão' },
    { id: 'watermelon', name: 'Melancia' },
    { id: 'grapes', name: 'Uva' },
    { id: 'pineapple', name: 'Abacaxi' },
    { id: 'melon', name: 'Melão' },
    { id: 'strawberry', name: 'Morango' },
    { id: 'kiwi', name: 'Kiwi' },
  ],
  vegetables: [
    { id: 'broccoli', name: 'Brócolis' },
    { id: 'spinach', name: 'Espinafre' },
    { id: 'lettuce', name: 'Alface' },
    { id: 'tomato', name: 'Tomate' },
    { id: 'carrot', name: 'Cenoura' },
    { id: 'cucumber', name: 'Pepino' },
    { id: 'zucchini', name: 'Abobrinha' },
    { id: 'onion', name: 'Cebola' },
    { id: 'bell_pepper', name: 'Pimentão' },
    { id: 'mushroom', name: 'Cogumelo' },
    { id: 'cabbage', name: 'Repolho' },
    { id: 'green_beans', name: 'Vagem' },
    { id: 'asparagus', name: 'Aspargo' },
  ],
  // ========== SUPLEMENTOS - CATEGORIA SEPARADA ==========
  supplements: [
    { id: 'whey', name: 'Whey Protein' },
    { id: 'creatine', name: 'Creatina' },
    { id: 'bcaa', name: 'BCAA' },
    { id: 'multivitamin', name: 'Multivitamínico' },
    { id: 'caffeine', name: 'Cafeína' },
    { id: 'pre_workout', name: 'Pré-Treino' },
    { id: 'glutamine', name: 'Glutamina' },
    { id: 'omega3', name: 'Ômega 3' },
    { id: 'vitamin_d', name: 'Vitamina D' },
    { id: 'collagen', name: 'Colágeno' },
  ],
};

const CATEGORIES = [
  { key: 'carbs', label: 'Carboidratos', icon: 'leaf-outline', color: '#F59E0B' },
  { key: 'proteins', label: 'Proteínas', icon: 'fitness-outline', color: '#EF4444' },
  { key: 'fats', label: 'Gorduras', icon: 'water-outline', color: '#3B82F6' },
  { key: 'fruits', label: '🍎 Frutas', icon: 'nutrition-outline', color: '#EC4899' },
  { key: 'vegetables', label: 'Vegetais', icon: 'leaf-outline', color: '#10B981' },
  { key: 'supplements', label: '💊 Suplementação', icon: 'flask-outline', color: '#8B5CF6' },
];

const dietaryOptions = [
  'Vegetariano',
  'Vegano',
  'Sem Lactose',
  'Sem Glúten',
  'Sem Açúcar',
  'Low Carb',
  'Keto',
  'Pescetariano',
];

export default function RestrictionsStep({ data, updateData }: Props) {
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

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Preferências Alimentares</Text>
      <Text style={styles.description}>
        Selecione os alimentos que você gosta para personalizar sua dieta.
      </Text>

      {/* Restrições Dietéticas */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Ionicons name="warning-outline" size={20} color="#F59E0B" />
          <Text style={styles.sectionTitle}>Restrições Dietéticas</Text>
        </View>
        <View style={styles.chipsContainer}>
          {dietaryOptions.map((option) => (
            <TouchableOpacity
              key={option}
              style={[
                styles.chip,
                data.dietary_restrictions?.includes(option) && styles.chipActive,
              ]}
              onPress={() =>
                updateData({
                  dietary_restrictions: toggleItem(
                    data.dietary_restrictions || [],
                    option
                  ),
                })
              }
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.chipText,
                  data.dietary_restrictions?.includes(option) && styles.chipTextActive,
                ]}
              >
                {option}
              </Text>
              {data.dietary_restrictions?.includes(option) && (
                <Ionicons name="checkmark" size={16} color="#10B981" />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Food Preferences by Category */}
      <View style={styles.foodSection}>
        <View style={styles.foodHeader}>
          <Text style={styles.foodTitle}>Alimentos que Você Gosta</Text>
          <Text style={styles.selectedCount}>{selectedCount} selecionados</Text>
        </View>

        {CATEGORIES.map((category) => (
          <View key={category.key} style={styles.category}>
            <View style={[styles.categoryHeader, { backgroundColor: category.color + '15' }]}>
              <Ionicons name={category.icon as any} size={18} color={category.color} />
              <Text style={[styles.categoryTitle, { color: category.color }]}>
                {category.label}
              </Text>
              {(category.key === 'fruits' || category.key === 'supplements') && (
                <View style={[styles.separateBadge, { backgroundColor: category.color }]}>
                  <Text style={styles.separateBadgeText}>SEPARADO</Text>
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
                    {food.name}
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

      <Text style={styles.hint}>
        Você pode pular esta etapa e ajustar depois nas configurações.
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
    marginBottom: 24,
    lineHeight: 24,
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
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  categoryTitle: {
    fontSize: 14,
    fontWeight: '700',
    flex: 1,
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
  hint: {
    fontSize: 13,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 16,
  },
});
