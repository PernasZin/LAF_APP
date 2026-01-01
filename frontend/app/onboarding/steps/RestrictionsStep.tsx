import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

// Food Database with Macro Categories
interface FoodItem {
  id: string;
  name: string;
  macro_type: 'carb' | 'protein' | 'fat' | 'other';
}

const FOOD_DATABASE: Record<string, FoodItem[]> = {
  carbs: [
    { id: 'rice', name: 'Arroz', macro_type: 'carb' },
    { id: 'brown_rice', name: 'Arroz Integral', macro_type: 'carb' },
    { id: 'sweet_potato', name: 'Batata Doce', macro_type: 'carb' },
    { id: 'potato', name: 'Batata Inglesa', macro_type: 'carb' },
    { id: 'oats', name: 'Aveia', macro_type: 'carb' },
    { id: 'pasta', name: 'Macarrão', macro_type: 'carb' },
    { id: 'integral_pasta', name: 'Macarrão Integral', macro_type: 'carb' },
    { id: 'bread', name: 'Pão', macro_type: 'carb' },
    { id: 'integral_bread', name: 'Pão Integral', macro_type: 'carb' },
    { id: 'tapioca', name: 'Tapioca', macro_type: 'carb' },
    { id: 'cassava', name: 'Mandioca', macro_type: 'carb' },
    { id: 'corn', name: 'Milho', macro_type: 'carb' },
    { id: 'beans', name: 'Feijão', macro_type: 'carb' },
    { id: 'lentils', name: 'Lentilha', macro_type: 'carb' },
    { id: 'chickpeas', name: 'Grão de Bico', macro_type: 'carb' },
    { id: 'banana', name: 'Banana', macro_type: 'carb' },
    { id: 'apple', name: 'Maçã', macro_type: 'carb' },
    { id: 'orange', name: 'Laranja', macro_type: 'carb' },
    { id: 'berries', name: 'Frutas Vermelhas', macro_type: 'carb' },
    { id: 'mango', name: 'Manga', macro_type: 'carb' },
    { id: 'papaya', name: 'Mamão', macro_type: 'carb' },
    { id: 'watermelon', name: 'Melancia', macro_type: 'carb' },
    { id: 'grapes', name: 'Uva', macro_type: 'carb' },
  ],
  proteins: [
    { id: 'chicken', name: 'Frango', macro_type: 'protein' },
    { id: 'chicken_breast', name: 'Peito de Frango', macro_type: 'protein' },
    { id: 'beef', name: 'Carne Bovina', macro_type: 'protein' },
    { id: 'ground_beef', name: 'Carne Moída', macro_type: 'protein' },
    { id: 'steak', name: 'Filé Mignon', macro_type: 'protein' },
    { id: 'pork', name: 'Carne Suína', macro_type: 'protein' },
    { id: 'fish', name: 'Peixe', macro_type: 'protein' },
    { id: 'tilapia', name: 'Tilápia', macro_type: 'protein' },
    { id: 'salmon', name: 'Salmão', macro_type: 'protein' },
    { id: 'tuna', name: 'Atum', macro_type: 'protein' },
    { id: 'shrimp', name: 'Camarão', macro_type: 'protein' },
    { id: 'eggs', name: 'Ovos', macro_type: 'protein' },
    { id: 'egg_whites', name: 'Clara de Ovo', macro_type: 'protein' },
    { id: 'whey', name: 'Whey Protein', macro_type: 'protein' },
    { id: 'greek_yogurt', name: 'Iogurte Grego', macro_type: 'protein' },
    { id: 'cottage', name: 'Queijo Cottage', macro_type: 'protein' },
    { id: 'turkey', name: 'Peru', macro_type: 'protein' },
    { id: 'ham', name: 'Presunto', macro_type: 'protein' },
  ],
  fats: [
    { id: 'olive_oil', name: 'Azeite de Oliva', macro_type: 'fat' },
    { id: 'coconut_oil', name: 'Óleo de Coco', macro_type: 'fat' },
    { id: 'avocado', name: 'Abacate', macro_type: 'fat' },
    { id: 'nuts', name: 'Castanhas', macro_type: 'fat' },
    { id: 'almonds', name: 'Amêndoas', macro_type: 'fat' },
    { id: 'walnuts', name: 'Nozes', macro_type: 'fat' },
    { id: 'brazil_nuts', name: 'Castanha do Pará', macro_type: 'fat' },
    { id: 'peanuts', name: 'Amendoim', macro_type: 'fat' },
    { id: 'peanut_butter', name: 'Pasta de Amendoim', macro_type: 'fat' },
    { id: 'seeds', name: 'Sementes (chia, linhaça)', macro_type: 'fat' },
    { id: 'butter', name: 'Manteiga', macro_type: 'fat' },
    { id: 'cheese', name: 'Queijo', macro_type: 'fat' },
    { id: 'cream_cheese', name: 'Cream Cheese', macro_type: 'fat' },
    { id: 'heavy_cream', name: 'Creme de Leite', macro_type: 'fat' },
  ],
  other: [
    { id: 'broccoli', name: 'Brócolis', macro_type: 'other' },
    { id: 'spinach', name: 'Espinafre', macro_type: 'other' },
    { id: 'lettuce', name: 'Alface', macro_type: 'other' },
    { id: 'tomato', name: 'Tomate', macro_type: 'other' },
    { id: 'carrot', name: 'Cenoura', macro_type: 'other' },
    { id: 'cucumber', name: 'Pepino', macro_type: 'other' },
    { id: 'zucchini', name: 'Abobrinha', macro_type: 'other' },
    { id: 'onion', name: 'Cebola', macro_type: 'other' },
    { id: 'garlic', name: 'Alho', macro_type: 'other' },
    { id: 'bell_pepper', name: 'Pimentão', macro_type: 'other' },
    { id: 'mushroom', name: 'Cogumelo', macro_type: 'other' },
    { id: 'cabbage', name: 'Repolho', macro_type: 'other' },
    { id: 'green_beans', name: 'Vagem', macro_type: 'other' },
    { id: 'asparagus', name: 'Aspargo', macro_type: 'other' },
    { id: 'creatine', name: 'Creatina', macro_type: 'other' },
    { id: 'bcaa', name: 'BCAA', macro_type: 'other' },
    { id: 'multivitamin', name: 'Multivitamínico', macro_type: 'other' },
  ],
};

const CATEGORIES = [
  { key: 'carbs', label: 'Carboidratos', icon: 'leaf-outline', color: '#F59E0B' },
  { key: 'proteins', label: 'Proteínas', icon: 'fitness-outline', color: '#EF4444' },
  { key: 'fats', label: 'Gorduras', icon: 'water-outline', color: '#3B82F6' },
  { key: 'other', label: 'Vegetais e Suplementos', icon: 'nutrition-outline', color: '#10B981' },
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
