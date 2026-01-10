import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { translations, SupportedLanguage } from '../../../i18n/translations';

interface MealConfigStepProps {
  data: any;
  updateData: (data: any) => void;
  language: SupportedLanguage;
}

const DEFAULT_MEAL_TIMES: Record<number, string[]> = {
  4: ['07:00', '12:00', '16:00', '20:00'],
  5: ['07:00', '10:00', '13:00', '16:00', '20:00'],
  6: ['07:00', '10:00', '13:00', '16:00', '19:00', '22:00'],
};

const MEAL_NAMES_PT: Record<number, string[]> = {
  4: ['Café da Manhã', 'Almoço', 'Lanche Tarde', 'Jantar'],
  5: ['Café da Manhã', 'Lanche Manhã', 'Almoço', 'Lanche Tarde', 'Jantar'],
  6: ['Café da Manhã', 'Lanche Manhã', 'Almoço', 'Lanche Tarde', 'Jantar', 'Ceia'],
};

const MEAL_NAMES_EN: Record<number, string[]> = {
  4: ['Breakfast', 'Lunch', 'Afternoon Snack', 'Dinner'],
  5: ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner'],
  6: ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner', 'Supper'],
};

const MEAL_NAMES_ES: Record<number, string[]> = {
  4: ['Desayuno', 'Almuerzo', 'Merienda', 'Cena'],
  5: ['Desayuno', 'Snack Mañana', 'Almuerzo', 'Merienda', 'Cena'],
  6: ['Desayuno', 'Snack Mañana', 'Almuerzo', 'Merienda', 'Cena', 'Colación'],
};

export default function MealConfigStep({ data, updateData, language }: MealConfigStepProps) {
  const [mealCount, setMealCount] = useState<number>(data.meal_count || 5);
  const [mealTimes, setMealTimes] = useState<string[]>(
    data.meal_times || DEFAULT_MEAL_TIMES[5]
  );

  const t = translations[language];

  const getMealNames = (count: number) => {
    if (language === 'en-US') return MEAL_NAMES_EN[count];
    if (language === 'es-ES') return MEAL_NAMES_ES[count];
    return MEAL_NAMES_PT[count];
  };

  const handleMealCountChange = (count: number) => {
    setMealCount(count);
    setMealTimes(DEFAULT_MEAL_TIMES[count]);
    updateData({
      meal_count: count,
      meal_times: DEFAULT_MEAL_TIMES[count],
    });
  };

  useEffect(() => {
    // Inicializa com valores padrão se não existirem
    if (!data.meal_count) {
      updateData({
        meal_count: 5,
        meal_times: DEFAULT_MEAL_TIMES[5],
      });
    }
  }, []);

  const getTitle = () => {
    if (language === 'en-US') return 'Meal Plan';
    if (language === 'es-ES') return 'Plan de Comidas';
    return 'Plano de Refeições';
  };

  const getSubtitle = () => {
    if (language === 'en-US') return 'How many meals do you prefer per day?';
    if (language === 'es-ES') return '¿Cuántas comidas prefieres al día?';
    return 'Quantas refeições você prefere fazer por dia?';
  };

  const getDescription = () => {
    if (language === 'en-US') return 'Your diet will be divided into the selected number of meals';
    if (language === 'es-ES') return 'Tu dieta se dividirá en el número de comidas seleccionadas';
    return 'Sua dieta será dividida no número de refeições selecionadas';
  };

  const getMealLabel = (count: number) => {
    if (language === 'en-US') return `${count} meals`;
    if (language === 'es-ES') return `${count} comidas`;
    return `${count} refeições`;
  };

  const getMealDescription = (count: number) => {
    const descriptions: Record<number, Record<string, string>> = {
      4: {
        'pt-BR': 'Ideal para quem tem uma rotina mais corrida',
        'en-US': 'Ideal for those with a busy routine',
        'es-ES': 'Ideal para quienes tienen una rutina agitada',
      },
      5: {
        'pt-BR': 'Padrão recomendado para a maioria',
        'en-US': 'Recommended standard for most people',
        'es-ES': 'Estándar recomendado para la mayoría',
      },
      6: {
        'pt-BR': 'Melhor para atletas e ganho de massa',
        'en-US': 'Best for athletes and muscle gain',
        'es-ES': 'Mejor para atletas y ganancia muscular',
      },
    };
    return descriptions[count][language] || descriptions[count]['pt-BR'];
  };

  const getPreviewTitle = () => {
    if (language === 'en-US') return 'Your meal schedule:';
    if (language === 'es-ES') return 'Tu horario de comidas:';
    return 'Seu horário de refeições:';
  };

  const mealNames = getMealNames(mealCount);

  return (
    <View style={styles.container}>
      {/* Title */}
      <Text style={styles.title}>{getTitle()}</Text>
      <Text style={styles.subtitle}>{getSubtitle()}</Text>

      {/* Meal Count Options */}
      <View style={styles.optionsContainer}>
        {[4, 5, 6].map((count) => (
          <TouchableOpacity
            key={count}
            style={[
              styles.option,
              mealCount === count && styles.optionSelected,
            ]}
            onPress={() => handleMealCountChange(count)}
          >
            <View style={[
              styles.optionNumber,
              mealCount === count && styles.optionNumberSelected,
            ]}>
              <Text style={[
                styles.optionNumberText,
                mealCount === count && styles.optionNumberTextSelected,
              ]}>
                {count}
              </Text>
            </View>
            <View style={styles.optionContent}>
              <Text style={[
                styles.optionLabel,
                mealCount === count && styles.optionLabelSelected,
              ]}>
                {getMealLabel(count)}
              </Text>
              <Text style={[
                styles.optionDescription,
                mealCount === count && styles.optionDescriptionSelected,
              ]}>
                {getMealDescription(count)}
              </Text>
            </View>
            {mealCount === count && (
              <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* Description */}
      <View style={styles.infoCard}>
        <Ionicons name="information-circle" size={20} color="#3B82F6" />
        <Text style={styles.infoText}>{getDescription()}</Text>
      </View>

      {/* Preview */}
      <Text style={styles.previewTitle}>{getPreviewTitle()}</Text>
      <View style={styles.previewContainer}>
        {mealNames.map((name, index) => (
          <View key={index} style={styles.previewItem}>
            <View style={styles.previewIconContainer}>
              <Ionicons 
                name={getIconForMeal(index, mealCount)} 
                size={18} 
                color="#10B981" 
              />
            </View>
            <Text style={styles.previewMealName}>{name}</Text>
            <Text style={styles.previewTime}>{mealTimes[index]}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

function getIconForMeal(index: number, total: number): any {
  if (index === 0) return 'sunny-outline'; // Café
  if (index === total - 1 && total === 6) return 'bed-outline'; // Ceia
  if (index === total - 1) return 'moon-outline'; // Jantar
  if (index === Math.floor(total / 2)) return 'restaurant-outline'; // Almoço
  return 'nutrition-outline'; // Lanches
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 24,
    lineHeight: 22,
  },
  optionsContainer: {
    gap: 12,
    marginBottom: 20,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
    gap: 14,
  },
  optionSelected: {
    borderColor: '#10B981',
    backgroundColor: '#F0FDF4',
  },
  optionNumber: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  optionNumberSelected: {
    backgroundColor: '#10B981',
  },
  optionNumberText: {
    fontSize: 20,
    fontWeight: '800',
    color: '#6B7280',
  },
  optionNumberTextSelected: {
    color: '#FFFFFF',
  },
  optionContent: {
    flex: 1,
  },
  optionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 2,
  },
  optionLabelSelected: {
    color: '#059669',
  },
  optionDescription: {
    fontSize: 13,
    color: '#9CA3AF',
  },
  optionDescriptionSelected: {
    color: '#6B7280',
  },
  infoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    backgroundColor: '#EFF6FF',
    borderRadius: 12,
    gap: 10,
    marginBottom: 24,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#1D4ED8',
    lineHeight: 20,
  },
  previewTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  previewContainer: {
    backgroundColor: '#F9FAFB',
    borderRadius: 16,
    padding: 16,
    gap: 12,
  },
  previewItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  previewIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#D1FAE5',
    alignItems: 'center',
    justifyContent: 'center',
  },
  previewMealName: {
    flex: 1,
    fontSize: 15,
    fontWeight: '500',
    color: '#374151',
  },
  previewTime: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
  },
});
