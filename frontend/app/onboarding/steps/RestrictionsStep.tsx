import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

interface FoodItem {
  id: string;
  name: string;
}

// ============================================
// ATHLETE DIET-SAFE BASE FOODS ONLY
// Rules:
// - Remove processed foods
// - Remove hard-to-measure items
// - All quantities: multiples of 10g
// ============================================

const FOOD_DATABASE: Record<string, FoodItem[]> = {
  // PROTEÍNAS - Only clean protein sources
  proteins: [
    { id: 'chicken_breast', name: 'Peito de Frango' },
    { id: 'lean_beef', name: 'Carne Bovina (Patinho)' },
    { id: 'eggs', name: 'Ovos Inteiros' },
    { id: 'tilapia', name: 'Tilápia' },
    { id: 'tuna', name: 'Atum' },
    { id: 'salmon', name: 'Salmão' },
  ],
  
  // CARBOIDRATOS - Clean carb sources
  carbs: [
    { id: 'white_rice', name: 'Arroz Branco' },
    { id: 'brown_rice', name: 'Arroz Integral' },
    { id: 'sweet_potato', name: 'Batata Doce' },
    { id: 'potato', name: 'Batata Inglesa' },
    { id: 'oats', name: 'Aveia' },
    { id: 'pasta', name: 'Macarrão' },
    { id: 'bread', name: 'Pão' },
  ],
  
  // GORDURAS - Limited to essentials
  fats: [
    { id: 'olive_oil', name: 'Azeite de Oliva' },
    { id: 'peanut_butter', name: 'Pasta de Amendoim' },
  ],
  
  // FRUTAS - Separate category (avocado is a fruit!)
  fruits: [
    { id: 'banana', name: 'Banana' },
    { id: 'apple', name: 'Maçã' },
    { id: 'orange', name: 'Laranja' },
    { id: 'strawberry', name: 'Morango' },
    { id: 'papaya', name: 'Mamão' },
    { id: 'mango', name: 'Manga' },
    { id: 'watermelon', name: 'Melancia' },
    { id: 'avocado', name: 'Abacate' },  // FRUIT not fat!
  ],
  
  // SUPLEMENTOS - Separate, NOT in meals
  // Never count as protein or replace meals
  supplements: [
    { id: 'creatine', name: 'Creatina' },
    { id: 'multivitamin', name: 'Multivitamínico' },
    { id: 'omega3', name: 'Ômega 3' },
    { id: 'caffeine', name: 'Cafeína' },
  ],
};

const CATEGORIES = [
  { key: 'proteins', label: 'Proteínas', icon: 'fitness-outline', color: '#EF4444', description: 'Fontes limpas de proteína' },
  { key: 'carbs', label: 'Carboidratos', icon: 'leaf-outline', color: '#F59E0B', description: 'Fontes de energia' },
  { key: 'fats', label: 'Gorduras', icon: 'water-outline', color: '#3B82F6', description: 'Gorduras essenciais' },
  { key: 'fruits', label: 'Frutas', icon: 'nutrition-outline', color: '#EC4899', description: 'Micronutrientes e fibras' },
  { key: 'supplements', label: 'Suplementação', icon: 'flask-outline', color: '#8B5CF6', description: 'Não substitui refeições' },
];

const dietaryOptions = [
  'Vegetariano',
  'Sem Lactose',
  'Sem Glúten',
  'Low Carb',
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
        Selecione os alimentos que você gosta. Usamos apenas alimentos base de dieta de atleta.
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
          <Text style={styles.foodTitle}>Alimentos Disponíveis</Text>
          <Text style={styles.selectedCount}>{selectedCount} selecionados</Text>
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

      <View style={styles.infoBox}>
        <Ionicons name="information-circle-outline" size={18} color="#6B7280" />
        <Text style={styles.infoText}>
          Todas as quantidades serão em múltiplos de 10g para facilitar a medição.
        </Text>
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
