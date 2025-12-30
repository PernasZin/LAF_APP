import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

export default function RestrictionsStep({ data, updateData }: Props) {
  const dietaryOptions = [
    'Vegetariano',
    'Vegano',
    'Sem Lactose',
    'Sem Glúten',
    'Sem Açúcar',
    'Low Carb',
  ];

  const foodPreferences = [
    'Frango',
    'Carne Vermelha',
    'Peixe',
    'Ovos',
    'Arroz',
    'Batata Doce',
    'Aveia',
    'Frutas',
  ];

  const toggleItem = (array: string[], item: string) => {
    if (array.includes(item)) {
      return array.filter((i) => i !== item);
    } else {
      return [...array, item];
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Preferências Alimentares</Text>
      <Text style={styles.description}>
        Essas informações nos ajudam a personalizar seu plano de dieta.
      </Text>

      {/* Restrições Dietéticas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Restrições Dietéticas</Text>
        <View style={styles.chipsContainer}>
          {dietaryOptions.map((option) => (
            <TouchableOpacity
              key={option}
              style={[
                styles.chip,
                data.dietary_restrictions.includes(option) && styles.chipActive,
              ]}
              onPress={() =>
                updateData({
                  dietary_restrictions: toggleItem(
                    data.dietary_restrictions,
                    option
                  ),
                })
              }
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.chipText,
                  data.dietary_restrictions.includes(option) &&
                    styles.chipTextActive,
                ]}
              >
                {option}
              </Text>
              {data.dietary_restrictions.includes(option) && (
                <Ionicons name="checkmark" size={16} color="#10B981" />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Alimentos Preferidos */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Alimentos que Você Gosta</Text>
        <View style={styles.chipsContainer}>
          {foodPreferences.map((food) => (
            <TouchableOpacity
              key={food}
              style={[
                styles.chip,
                data.food_preferences.includes(food) && styles.chipActive,
              ]}
              onPress={() =>
                updateData({
                  food_preferences: toggleItem(data.food_preferences, food),
                })
              }
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.chipText,
                  data.food_preferences.includes(food) && styles.chipTextActive,
                ]}
              >
                {food}
              </Text>
              {data.food_preferences.includes(food) && (
                <Ionicons name="checkmark" size={16} color="#10B981" />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <Text style={styles.hint}>
        Você pode pular esta etapa e adicionar depois no seu perfil.
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
    marginBottom: 32,
    lineHeight: 24,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
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
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  chipActive: {
    borderColor: '#10B981',
    backgroundColor: '#F0FDF4',
  },
  chipText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280',
  },
  chipTextActive: {
    color: '#10B981',
    fontWeight: '600',
  },
  hint: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 16,
  },
});