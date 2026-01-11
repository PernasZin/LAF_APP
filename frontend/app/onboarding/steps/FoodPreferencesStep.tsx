/**
 * Premium Food Preferences Step - Seleção de alimentos
 * Categorias: Proteínas, Carboidratos, Gorduras, Frutas, Vegetais/Legumes, Alimentos, Suplementos
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Check, Beef, Wheat, Apple, Droplets, Leaf, Milk, AlertTriangle, Pill, Salad, Cookie } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

// Restrições alimentares
const RESTRICTIONS = [
  { value: 'vegetariano', label: 'Vegetariano', icon: Leaf, color: '#22C55E' },
  { value: 'vegano', label: 'Vegano', icon: Leaf, color: '#10B981' },
  { value: 'sem_lactose', label: 'Sem Lactose', icon: Milk, color: '#3B82F6' },
  { value: 'sem_gluten', label: 'Sem Glúten', icon: Wheat, color: '#F59E0B' },
  { value: 'sem_frutos_mar', label: 'Sem Frutos do Mar', icon: AlertTriangle, color: '#06B6D4' },
];

// Alimentos disponíveis organizados por categoria
const FOOD_CATEGORIES = {
  proteins: {
    title: 'Proteínas',
    icon: Beef,
    color: '#EF4444',
    items: [
      { key: 'frango', name: 'Frango' },
      { key: 'patinho', name: 'Patinho/Carne Moída' },
      { key: 'ovo', name: 'Ovos' },
      { key: 'peixe', name: 'Peixe (Tilápia)' },
      { key: 'atum', name: 'Atum' },
      { key: 'peito_peru', name: 'Peito de Peru' },
      { key: 'iogurte', name: 'Iogurte' },
    ],
  },
  carbs: {
    title: 'Carboidratos',
    icon: Wheat,
    color: '#F59E0B',
    items: [
      { key: 'arroz_branco', name: 'Arroz Branco' },
      { key: 'arroz_integral', name: 'Arroz Integral' },
      { key: 'batata_doce', name: 'Batata Doce' },
      { key: 'macarrao', name: 'Macarrão' },
      { key: 'aveia', name: 'Aveia' },
      { key: 'pao_integral', name: 'Pão Integral' },
      { key: 'tapioca', name: 'Tapioca' },
      { key: 'granola', name: 'Granola' },
      { key: 'feijao', name: 'Feijão' },
    ],
  },
  fats: {
    title: 'Gorduras',
    icon: Droplets,
    color: '#3B82F6',
    items: [
      { key: 'azeite', name: 'Azeite de Oliva' },
      { key: 'castanha', name: 'Castanhas' },
      { key: 'abacate', name: 'Abacate' },
      { key: 'pasta_amendoim', name: 'Pasta de Amendoim' },
    ],
  },
  fruits: {
    title: 'Frutas',
    icon: Apple,
    color: '#10B981',
    items: [
      { key: 'banana', name: 'Banana' },
      { key: 'maca', name: 'Maçã' },
      { key: 'laranja', name: 'Laranja' },
      { key: 'morango', name: 'Morango' },
      { key: 'mamao', name: 'Mamão' },
      { key: 'melancia', name: 'Melancia' },
      { key: 'uva', name: 'Uva' },
      { key: 'pera', name: 'Pera' },
      { key: 'manga', name: 'Manga' },
      { key: 'abacaxi', name: 'Abacaxi' },
    ],
  },
  vegetables: {
    title: 'Vegetais e Legumes',
    icon: Salad,
    color: '#84CC16',
    items: [
      { key: 'brocolis', name: 'Brócolis' },
      { key: 'espinafre', name: 'Espinafre' },
      { key: 'cenoura', name: 'Cenoura' },
      { key: 'abobrinha', name: 'Abobrinha' },
      { key: 'tomate', name: 'Tomate' },
      { key: 'alface', name: 'Alface' },
      { key: 'pepino', name: 'Pepino' },
    ],
  },
  foods: {
    title: 'Alimentos',
    icon: Cookie,
    color: '#EC4899',
    items: [
      { key: 'mel', name: 'Mel' },
      { key: 'leite_condensado', name: 'Leite Condensado' },
    ],
  },
  supplements: {
    title: 'Suplementos',
    icon: Pill,
    color: '#8B5CF6',
    items: [
      { key: 'whey', name: 'Whey Protein' },
      { key: 'creatina', name: 'Creatina' },
      { key: 'multivitaminico', name: 'Multivitamínico' },
      { key: 'cafeina', name: 'Cafeína' },
      { key: 'bcaa', name: 'BCAA' },
      { key: 'omega3', name: 'Ômega 3' },
    ],
  },
};

export default function FoodPreferencesStep({ formData, updateFormData, theme, isDark }: Props) {
  const selectedFoods = formData.food_preferences || [];
  const restrictions = formData.dietary_restrictions || [];

  const toggleFood = (key: string) => {
    const updated = selectedFoods.includes(key)
      ? selectedFoods.filter((k: string) => k !== key)
      : [...selectedFoods, key];
    updateFormData({ food_preferences: updated });
  };

  const toggleRestriction = (value: string) => {
    const updated = restrictions.includes(value)
      ? restrictions.filter((r: string) => r !== value)
      : [...restrictions, value];
    updateFormData({ dietary_restrictions: updated });
  };

  return (
    <View style={styles.container}>
      {/* Restrições */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>Restrições Alimentares</Text>
      <View style={styles.restrictionsGrid}>
        {RESTRICTIONS.map((item) => {
          const isSelected = restrictions.includes(item.value);
          const Icon = item.icon;
          return (
            <TouchableOpacity
              key={item.value}
              style={[
                styles.restrictionChip,
                {
                  backgroundColor: isSelected ? `${item.color}15` : isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)',
                  borderColor: isSelected ? item.color : theme.border,
                }
              ]}
              onPress={() => toggleRestriction(item.value)}
            >
              <Icon size={16} color={isSelected ? item.color : theme.textTertiary} />
              <Text style={[styles.restrictionLabel, { color: isSelected ? item.color : theme.text }]}>
                {item.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Alimentos Preferidos */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary, marginTop: spacing.xl }]}>
        Alimentos Preferidos
      </Text>
      <Text style={[styles.sectionDesc, { color: theme.textTertiary }]}>
        Selecione os alimentos que você gosta
      </Text>

      {Object.entries(FOOD_CATEGORIES).map(([categoryKey, category]) => {
        const CategoryIcon = category.icon;
        return (
          <View key={categoryKey} style={styles.categorySection}>
            <View style={styles.categoryHeader}>
              <CategoryIcon size={16} color={category.color} />
              <Text style={[styles.categoryTitle, { color: theme.text }]}>{category.title}</Text>
            </View>
            <View style={styles.foodsGrid}>
              {category.items.map((food) => {
                const isSelected = selectedFoods.includes(food.key);
                return (
                  <TouchableOpacity
                    key={food.key}
                    style={[
                      styles.foodChip,
                      {
                        backgroundColor: isSelected ? `${category.color}15` : isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)',
                        borderColor: isSelected ? category.color : theme.border,
                      }
                    ]}
                    onPress={() => toggleFood(food.key)}
                  >
                    <Text style={[styles.foodLabel, { color: isSelected ? category.color : theme.text }]}>
                      {food.name}
                    </Text>
                    {isSelected && (
                      <Check size={14} color={category.color} strokeWidth={3} />
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingTop: spacing.lg },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
  },
  sectionDesc: {
    fontSize: 13,
    marginBottom: spacing.md,
  },
  restrictionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  restrictionChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    gap: spacing.xs,
  },
  restrictionLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  categorySection: {
    marginTop: spacing.md,
  },
  categoryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  categoryTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  foodsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  foodChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: spacing.sm,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: 4,
  },
  foodLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
});
