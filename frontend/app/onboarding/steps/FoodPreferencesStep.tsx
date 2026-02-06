/**
 * Premium Food Preferences Step - Seleção de alimentos
 * Com suporte completo a i18n (PT/EN/ES)
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { Check, Beef, Wheat, Apple, Droplets, Leaf, Milk, Pill, Activity } from 'lucide-react-native';
import { premiumColors, radius, spacing } from '../../../theme/premium';
import { useSettingsStore } from '../../../stores/settingsStore';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface Props {
  formData: any;
  updateFormData: (data: any) => void;
  theme: any;
  isDark: boolean;
}

// Traduções de alimentos
const FOOD_TRANSLATIONS: Record<string, Record<string, string>> = {
  // Proteínas
  frango: { pt: 'Frango', en: 'Chicken', es: 'Pollo' },
  patinho: { pt: 'Patinho', en: 'Lean Beef', es: 'Carne Magra' },
  carne_moida: { pt: 'Carne Moída', en: 'Ground Beef', es: 'Carne Molida' },
  ovos: { pt: 'Ovos', en: 'Eggs', es: 'Huevos' },
  tilapia: { pt: 'Tilápia', en: 'Tilapia', es: 'Tilapia' },
  atum: { pt: 'Atum', en: 'Tuna', es: 'Atún' },
  salmao: { pt: 'Salmão', en: 'Salmon', es: 'Salmón' },
  peru: { pt: 'Peru', en: 'Turkey', es: 'Pavo' },
  cottage: { pt: 'Queijo Cottage', en: 'Cottage Cheese', es: 'Queso Cottage' },
  iogurte_zero: { pt: 'Iogurte Zero', en: 'Sugar-Free Yogurt', es: 'Yogur Sin Azúcar' },
  tofu: { pt: 'Tofu', en: 'Tofu', es: 'Tofu' },
  tempeh: { pt: 'Tempeh', en: 'Tempeh', es: 'Tempeh' },
  edamame: { pt: 'Edamame', en: 'Edamame', es: 'Edamame' },
  whey_protein: { pt: 'Whey Protein', en: 'Whey Protein', es: 'Proteína Whey' },
  
  // Carboidratos
  arroz_branco: { pt: 'Arroz Branco', en: 'White Rice', es: 'Arroz Blanco' },
  arroz_integral: { pt: 'Arroz Integral', en: 'Brown Rice', es: 'Arroz Integral' },
  batata_doce: { pt: 'Batata Doce', en: 'Sweet Potato', es: 'Batata' },
  aveia: { pt: 'Aveia', en: 'Oats', es: 'Avena' },
  macarrao: { pt: 'Macarrão', en: 'Pasta', es: 'Pasta' },
  pao_integral: { pt: 'Pão Integral', en: 'Whole Wheat Bread', es: 'Pan Integral' },
  tapioca: { pt: 'Tapioca', en: 'Tapioca', es: 'Tapioca' },
  feijao: { pt: 'Feijão', en: 'Beans', es: 'Frijoles' },
  lentilha: { pt: 'Lentilha', en: 'Lentils', es: 'Lentejas' },
  granola: { pt: 'Granola', en: 'Granola', es: 'Granola' },
  
  // Gorduras
  azeite: { pt: 'Azeite', en: 'Olive Oil', es: 'Aceite de Oliva' },
  pasta_amendoim: { pt: 'Pasta de Amendoim', en: 'Peanut Butter', es: 'Mantequilla de Maní' },
  castanhas: { pt: 'Castanhas', en: 'Cashews', es: 'Castañas' },
  amendoas: { pt: 'Amêndoas', en: 'Almonds', es: 'Almendras' },
  nozes: { pt: 'Nozes', en: 'Walnuts', es: 'Nueces' },
  abacate: { pt: 'Abacate', en: 'Avocado', es: 'Aguacate' },
  queijo: { pt: 'Queijo', en: 'Cheese', es: 'Queso' },
  
  // Frutas
  banana: { pt: 'Banana', en: 'Banana', es: 'Plátano' },
  maca: { pt: 'Maçã', en: 'Apple', es: 'Manzana' },
  laranja: { pt: 'Laranja', en: 'Orange', es: 'Naranja' },
  morango: { pt: 'Morango', en: 'Strawberry', es: 'Fresa' },
  mamao: { pt: 'Mamão', en: 'Papaya', es: 'Papaya' },
  melancia: { pt: 'Melancia', en: 'Watermelon', es: 'Sandía' },
  uva: { pt: 'Uva', en: 'Grapes', es: 'Uvas' },
  abacaxi: { pt: 'Abacaxi', en: 'Pineapple', es: 'Piña' },
  kiwi: { pt: 'Kiwi', en: 'Kiwi', es: 'Kiwi' },
  
  // Vegetais
  brocolis: { pt: 'Brócolis', en: 'Broccoli', es: 'Brócoli' },
  espinafre: { pt: 'Espinafre', en: 'Spinach', es: 'Espinaca' },
  couve: { pt: 'Couve', en: 'Kale', es: 'Col Rizada' },
  cenoura: { pt: 'Cenoura', en: 'Carrot', es: 'Zanahoria' },
  abobrinha: { pt: 'Abobrinha', en: 'Zucchini', es: 'Calabacín' },
  tomate: { pt: 'Tomate', en: 'Tomato', es: 'Tomate' },
  salada: { pt: 'Salada', en: 'Salad', es: 'Ensalada' },
};

// Traduções de restrições
const RESTRICTION_TRANSLATIONS: Record<string, Record<string, string>> = {
  vegetariano: { pt: 'Vegetariano', en: 'Vegetarian', es: 'Vegetariano' },
  vegano: { pt: 'Vegano', en: 'Vegan', es: 'Vegano' },
  sem_lactose: { pt: 'Sem Lactose', en: 'Lactose Free', es: 'Sin Lactosa' },
  sem_gluten: { pt: 'Sem Glúten', en: 'Gluten Free', es: 'Sin Gluten' },
};

// Traduções de categorias
const CATEGORY_TRANSLATIONS: Record<string, Record<string, string>> = {
  proteins: { pt: 'Proteínas', en: 'Proteins', es: 'Proteínas' },
  carbs: { pt: 'Carboidratos', en: 'Carbohydrates', es: 'Carbohidratos' },
  fats: { pt: 'Gorduras', en: 'Fats', es: 'Grasas' },
  fruits: { pt: 'Frutas', en: 'Fruits', es: 'Frutas' },
  vegetables: { pt: 'Vegetais', en: 'Vegetables', es: 'Vegetales' },
};

// Traduções de textos da tela
const UI_TRANSLATIONS: Record<string, Record<string, string>> = {
  dietaryRestrictions: { pt: 'Restrições Alimentares', en: 'Dietary Restrictions', es: 'Restricciones Alimentarias' },
  selectRestrictions: { pt: 'Selecione se tiver alguma restrição', en: 'Select if you have any restrictions', es: 'Selecciona si tienes alguna restricción' },
  preferredFoods: { pt: 'Alimentos Preferidos', en: 'Preferred Foods', es: 'Alimentos Preferidos' },
  selectFoods: { pt: 'Selecione os alimentos que você gosta', en: 'Select the foods you like', es: 'Selecciona los alimentos que te gustan' },
};

// Categorias de alimentos
const FOOD_CATEGORIES = {
  proteins: {
    icon: Beef,
    color: '#EF4444',
    items: ['frango', 'patinho', 'carne_moida', 'ovos', 'tilapia', 'atum', 'salmao', 'peru', 'cottage', 'iogurte_zero', 'tofu', 'tempeh', 'edamame', 'whey_protein'],
  },
  carbs: {
    icon: Wheat,
    color: '#F59E0B',
    items: ['arroz_branco', 'arroz_integral', 'batata_doce', 'aveia', 'macarrao', 'pao_integral', 'tapioca', 'feijao', 'lentilha', 'granola'],
  },
  fats: {
    icon: Droplets,
    color: '#8B5CF6',
    items: ['azeite', 'pasta_amendoim', 'castanhas', 'amendoas', 'nozes', 'abacate', 'queijo'],
  },
  fruits: {
    icon: Apple,
    color: '#22C55E',
    items: ['banana', 'maca', 'laranja', 'morango', 'mamao', 'melancia', 'uva', 'abacaxi', 'kiwi'],
  },
  vegetables: {
    icon: Leaf,
    color: '#10B981',
    items: ['brocolis', 'espinafre', 'couve', 'cenoura', 'abobrinha', 'tomate', 'salada'],
  },
};

// Restrições
const RESTRICTIONS = [
  { value: 'vegetariano', icon: Leaf, color: '#22C55E' },
  { value: 'vegano', icon: Leaf, color: '#10B981' },
  { value: 'sem_lactose', icon: Milk, color: '#3B82F6' },
  { value: 'sem_gluten', icon: Wheat, color: '#F59E0B' },
];

export default function FoodPreferencesStep({ formData, updateFormData, theme, isDark }: Props) {
  const languageCode = useSettingsStore((state) => state.language) as SupportedLanguage;
  // Converter 'pt-BR' -> 'pt', 'en-US' -> 'en', 'es-ES' -> 'es'
  const lang = languageCode.split('-')[0] as 'pt' | 'en' | 'es';
  
  const selectedFoods = formData.food_preferences || [];
  const restrictions = formData.dietary_restrictions || [];

  const getFoodName = (key: string): string => {
    return FOOD_TRANSLATIONS[key]?.[lang] || FOOD_TRANSLATIONS[key]?.pt || key;
  };

  const getRestrictionName = (key: string): string => {
    return RESTRICTION_TRANSLATIONS[key]?.[lang] || RESTRICTION_TRANSLATIONS[key]?.pt || key;
  };

  const getCategoryName = (key: string): string => {
    return CATEGORY_TRANSLATIONS[key]?.[lang] || CATEGORY_TRANSLATIONS[key]?.pt || key;
  };

  const getUIText = (key: string): string => {
    return UI_TRANSLATIONS[key]?.[lang] || UI_TRANSLATIONS[key]?.pt || key;
  };

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
      {/* Restrições Alimentares */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
        {getUIText('dietaryRestrictions')}
      </Text>
      <Text style={[styles.sectionDesc, { color: theme.textTertiary }]}>
        {getUIText('selectRestrictions')}
      </Text>
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
                {getRestrictionName(item.value)}
              </Text>
              {isSelected && (
                <Check size={14} color={item.color} strokeWidth={3} />
              )}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Alimentos Preferidos */}
      <Text style={[styles.sectionTitle, { color: theme.textSecondary, marginTop: spacing.xl }]}>
        {getUIText('preferredFoods')}
      </Text>
      <Text style={[styles.sectionDesc, { color: theme.textTertiary }]}>
        {getUIText('selectFoods')}
      </Text>

      {Object.entries(FOOD_CATEGORIES).map(([categoryKey, category]) => {
        const CategoryIcon = category.icon;
        return (
          <View key={categoryKey} style={styles.categorySection}>
            <View style={styles.categoryHeader}>
              <CategoryIcon size={16} color={category.color} />
              <Text style={[styles.categoryTitle, { color: theme.text }]}>
                {getCategoryName(categoryKey)}
              </Text>
            </View>
            <View style={styles.foodsGrid}>
              {category.items.map((foodKey) => {
                const isSelected = selectedFoods.includes(foodKey);
                return (
                  <TouchableOpacity
                    key={foodKey}
                    style={[
                      styles.foodChip,
                      {
                        backgroundColor: isSelected
                          ? `${category.color}15`
                          : isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.8)',
                        borderColor: isSelected ? category.color : theme.border,
                      }
                    ]}
                    onPress={() => toggleFood(foodKey)}
                  >
                    <Text style={[
                      styles.foodLabel,
                      { color: isSelected ? category.color : theme.text }
                    ]}>
                      {getFoodName(foodKey)}
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
  container: { 
    paddingTop: spacing.lg,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: spacing.xs,
  },
  sectionDesc: {
    fontSize: 14,
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
    fontSize: 13,
    fontWeight: '600',
  },
  categorySection: {
    marginTop: spacing.lg,
  },
  categoryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  categoryTitle: {
    fontSize: 15,
    fontWeight: '700',
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
    fontSize: 13,
    fontWeight: '500',
  },
});
