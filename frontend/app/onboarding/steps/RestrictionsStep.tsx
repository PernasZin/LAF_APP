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
  selectable: boolean; // true = pode selecionar, false = apenas visualização
}

// ============================================
// BANCO DE DADOS DE ALIMENTOS
// ============================================

// ATLETA: Lista restrita de alimentos limpos
const ATHLETE_FOODS: Record<string, FoodItem[]> = {
  proteins: [
    { id: 'chicken_breast', name: 'Peito de Frango', selectable: true },
    { id: 'lean_beef', name: 'Carne Bovina (Patinho)', selectable: true },
    { id: 'eggs', name: 'Ovos Inteiros', selectable: true },
    { id: 'tilapia', name: 'Tilápia', selectable: true },
    { id: 'tuna', name: 'Atum', selectable: true },
    { id: 'salmon', name: 'Salmão', selectable: true },
  ],
  carbs: [
    { id: 'white_rice', name: 'Arroz Branco', selectable: true },
    { id: 'brown_rice', name: 'Arroz Integral', selectable: true },
    { id: 'sweet_potato', name: 'Batata Doce', selectable: true },
    { id: 'potato', name: 'Batata Inglesa', selectable: true },
    { id: 'oats', name: 'Aveia', selectable: true },
    { id: 'pasta', name: 'Macarrão', selectable: true },
    { id: 'bread', name: 'Pão', selectable: true },
  ],
  fats: [
    { id: 'olive_oil', name: 'Azeite de Oliva', selectable: true },
    { id: 'peanut_butter', name: 'Pasta de Amendoim', selectable: true },
  ],
  fruits: [
    { id: 'banana', name: 'Banana', selectable: true },
    { id: 'apple', name: 'Maçã', selectable: true },
    { id: 'orange', name: 'Laranja', selectable: true },
    { id: 'strawberry', name: 'Morango', selectable: true },
    { id: 'papaya', name: 'Mamão', selectable: true },
    { id: 'mango', name: 'Manga', selectable: true },
    { id: 'watermelon', name: 'Melancia', selectable: true },
    { id: 'avocado', name: 'Abacate', selectable: true },
  ],
  supplements: [
    { id: 'creatine', name: 'Creatina', selectable: true },
    { id: 'multivitamin', name: 'Multivitamínico', selectable: true },
    { id: 'omega3', name: 'Ômega 3', selectable: true },
    { id: 'caffeine', name: 'Cafeína', selectable: true },
  ],
};

// GERAL: Lista de alimentos que REALMENTE aparecem nas dietas geradas
// Removidos: tofu, coxa_frango, carne_moida, suino, claras, camarao, sardinha,
// quinoa, cuscuz, tapioca, milho, grao_de_bico, pasta_amendoa, oleo_coco,
// manteiga, nozes, chia, linhaca, cream_cheese, abacate, uva, abacaxi,
// melao, kiwi, pera, pessego, mirtilo, acai
const GENERAL_FOODS: Record<string, FoodItem[]> = {
  proteins: [
    { id: 'chicken_breast', name: 'Peito de Frango', selectable: true },
    { id: 'lean_beef', name: 'Carne Bovina Magra', selectable: true },
    { id: 'eggs', name: 'Ovos Inteiros', selectable: true },
    { id: 'tilapia', name: 'Tilápia', selectable: true },
    { id: 'tuna', name: 'Atum', selectable: true },
    { id: 'salmon', name: 'Salmão', selectable: true },
    { id: 'turkey', name: 'Peru', selectable: true },
    { id: 'cottage', name: 'Queijo Cottage', selectable: true },
    { id: 'greek_yogurt', name: 'Iogurte Grego', selectable: true },
  ],
  carbs: [
    { id: 'white_rice', name: 'Arroz Branco', selectable: true },
    { id: 'brown_rice', name: 'Arroz Integral', selectable: true },
    { id: 'sweet_potato', name: 'Batata Doce', selectable: true },
    { id: 'potato', name: 'Batata Inglesa', selectable: true },
    { id: 'oats', name: 'Aveia', selectable: true },
    { id: 'pasta', name: 'Macarrão', selectable: true },
    { id: 'whole_bread', name: 'Pão Integral', selectable: true },
    { id: 'beans', name: 'Feijão', selectable: true },
    { id: 'lentils', name: 'Lentilha', selectable: true },
  ],
  fats: [
    { id: 'olive_oil', name: 'Azeite de Oliva', selectable: true },
    { id: 'peanut_butter', name: 'Pasta de Amendoim', selectable: true },
    { id: 'nuts', name: 'Castanhas', selectable: true },
    { id: 'almonds', name: 'Amêndoas', selectable: true },
    { id: 'cheese', name: 'Queijo', selectable: true },
  ],
  fruits: [
    { id: 'banana', name: 'Banana', selectable: true },
    { id: 'apple', name: 'Maçã', selectable: true },
    { id: 'orange', name: 'Laranja', selectable: true },
    { id: 'strawberry', name: 'Morango', selectable: true },
    { id: 'papaya', name: 'Mamão', selectable: true },
    { id: 'watermelon', name: 'Melancia', selectable: true },
  ],
  supplements: [
    { id: 'creatine', name: 'Creatina', selectable: true },
    { id: 'multivitamin', name: 'Multivitamínico', selectable: true },
    { id: 'omega3', name: 'Ômega 3', selectable: true },
    { id: 'caffeine', name: 'Cafeína', selectable: true },
    { id: 'vitamin_d', name: 'Vitamina D', selectable: true },
    { id: 'vitamin_c', name: 'Vitamina C', selectable: true },
    { id: 'zinc', name: 'Zinco', selectable: true },
    { id: 'magnesium', name: 'Magnésio', selectable: true },
    { id: 'collagen', name: 'Colágeno', selectable: true },
  ],
};

const CATEGORIES = [
  { key: 'proteins', label: 'Proteínas', icon: 'fitness-outline', color: '#EF4444', description: 'Fontes de proteína' },
  { key: 'carbs', label: 'Carboidratos', icon: 'leaf-outline', color: '#F59E0B', description: 'Fontes de energia' },
  { key: 'fats', label: 'Gorduras', icon: 'water-outline', color: '#3B82F6', description: 'Gorduras boas' },
  { key: 'fruits', label: 'Frutas', icon: 'nutrition-outline', color: '#EC4899', description: 'Vitaminas e fibras' },
  { key: 'supplements', label: 'Suplementação', icon: 'flask-outline', color: '#8B5CF6', description: 'Não substitui refeições' },
];

const dietaryOptions = [
  'Vegetariano',
  'Sem Lactose',
  'Sem Glúten',
  'Low Carb',
];

export default function RestrictionsStep({ data, updateData }: Props) {
  // Determina se é atleta
  const isAthlete = data.goal === 'atleta';
  
  // Seleciona o banco de dados baseado no objetivo
  const FOOD_DATABASE = isAthlete ? ATHLETE_FOODS : GENERAL_FOODS;

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
  const description = isAthlete
    ? 'Lista restrita de alimentos base para dieta de atleta. Apenas alimentos limpos e de fácil medição.'
    : 'Selecione os alimentos que você gosta. Maior variedade para uma dieta flexível.';

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Preferências Alimentares</Text>
      <Text style={styles.description}>{description}</Text>

      {/* Badge do modo */}
      <View style={[styles.modeBadge, isAthlete ? styles.modeBadgeAthlete : styles.modeBadgeGeneral]}>
        <Ionicons 
          name={isAthlete ? 'trophy' : 'restaurant'} 
          size={16} 
          color={isAthlete ? '#F59E0B' : '#10B981'} 
        />
        <Text style={[styles.modeBadgeText, { color: isAthlete ? '#F59E0B' : '#10B981' }]}>
          {isAthlete ? 'Modo Atleta: Lista Restrita' : 'Modo Flexível: Lista Expandida'}
        </Text>
      </View>

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
          {isAthlete 
            ? 'Dieta de atleta: quantidades em múltiplos de 10g para medição precisa.'
            : 'Você pode ajustar suas preferências depois nas configurações.'
          }
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
