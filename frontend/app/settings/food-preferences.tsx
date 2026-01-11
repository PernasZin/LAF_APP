/**
 * LAF Premium Food Preferences Screen
 * ====================================
 * Seleção de alimentos preferidos para dieta
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Check, Beef, Fish, Egg, Wheat, Apple, Droplets } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const GlassCard = ({ children, style, isDark }: any) => {
  const cardStyle = {
    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
    borderWidth: 1,
    borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
    borderRadius: radius.xl,
    overflow: 'hidden' as const,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: isDark ? 0.3 : 0.08,
    shadowRadius: 16,
    elevation: 8,
  };
  return <View style={[cardStyle, style]}>{children}</View>;
};

// Alimentos disponíveis organizados por categoria
const FOOD_CATEGORIES = {
  proteins: {
    title: 'Proteínas',
    icon: Beef,
    color: '#EF4444',
    items: [
      { key: 'frango', name: 'Frango' },
      { key: 'patinho', name: 'Patinho' },
      { key: 'ovo', name: 'Ovos' },
      { key: 'peixe', name: 'Peixe (Tilápia)' },
      { key: 'atum', name: 'Atum' },
      { key: 'carne_moida', name: 'Carne Moída' },
      { key: 'peito_peru', name: 'Peito de Peru' },
      { key: 'queijo_cottage', name: 'Queijo Cottage' },
      { key: 'whey', name: 'Whey Protein' },
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
      { key: 'batata_inglesa', name: 'Batata Inglesa' },
      { key: 'macarrao', name: 'Macarrão' },
      { key: 'aveia', name: 'Aveia' },
      { key: 'pao_integral', name: 'Pão Integral' },
      { key: 'tapioca', name: 'Tapioca' },
      { key: 'mandioca', name: 'Mandioca' },
    ],
  },
  fats: {
    title: 'Gorduras',
    icon: Droplets,
    color: '#3B82F6',
    items: [
      { key: 'azeite', name: 'Azeite de Oliva' },
      { key: 'castanha', name: 'Castanhas' },
      { key: 'amendoim', name: 'Amendoim' },
      { key: 'abacate', name: 'Abacate' },
      { key: 'pasta_amendoim', name: 'Pasta de Amendoim' },
      { key: 'oleo_coco', name: 'Óleo de Coco' },
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
    ],
  },
};

export default function FoodPreferencesScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [selectedFoods, setSelectedFoods] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const id = await AsyncStorage.getItem('userId');
    setUserId(id);
    
    // Carregar preferências salvas
    if (id && BACKEND_URL) {
      try {
        const response = await fetch(`${BACKEND_URL}/api/user/profile/${id}`);
        if (response.ok) {
          const data = await response.json();
          setSelectedFoods(data.food_preferences || []);
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
      }
    }
  };

  const toggleFood = (key: string) => {
    setSelectedFoods(prev => 
      prev.includes(key) 
        ? prev.filter(k => k !== key) 
        : [...prev, key]
    );
  };

  const handleSave = async () => {
    if (!userId) return;
    setSaving(true);
    try {
      // 1. Salva as preferências alimentares
      const response = await fetch(`${BACKEND_URL}/api/user/profile/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ food_preferences: selectedFoods }),
      });
      if (response.ok) {
        const data = await response.json();
        await AsyncStorage.setItem('userProfile', JSON.stringify(data));
        
        // 2. Regenera a dieta automaticamente com as novas preferências
        const dietResponse = await fetch(`${BACKEND_URL}/api/diet/generate?user_id=${userId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        
        if (dietResponse.ok) {
          const dietData = await dietResponse.json();
          await AsyncStorage.setItem('userDiet', JSON.stringify(dietData));
        }
        
        Alert.alert('Sucesso', 'Preferências salvas e dieta atualizada!', [{ text: 'OK', onPress: () => router.back() }]);
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível salvar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']
        }
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
              <ArrowLeft size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.headerTitle, { color: theme.text }]}>Preferências</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
            Selecione os alimentos que você prefere na sua dieta
          </Text>

          {/* Food Categories */}
          {Object.entries(FOOD_CATEGORIES).map(([categoryKey, category], catIndex) => {
            const CategoryIcon = category.icon;
            return (
              <Animated.View key={categoryKey} entering={FadeInDown.delay(catIndex * 100).springify()}>
                <View style={styles.categoryHeader}>
                  <CategoryIcon size={18} color={category.color} />
                  <Text style={[styles.categoryTitle, { color: theme.text }]}>{category.title}</Text>
                </View>
                <GlassCard isDark={isDark} style={styles.card}>
                  <View style={styles.foodsGrid}>
                    {category.items.map((food) => {
                      const isSelected = selectedFoods.includes(food.key);
                      return (
                        <TouchableOpacity
                          key={food.key}
                          style={[
                            styles.foodChip,
                            {
                              backgroundColor: isSelected 
                                ? `${category.color}15` 
                                : isDark ? 'rgba(51, 65, 85, 0.5)' : 'rgba(241, 245, 249, 0.8)',
                              borderColor: isSelected ? category.color : theme.border,
                            }
                          ]}
                          onPress={() => toggleFood(food.key)}
                        >
                          <Text style={[
                            styles.foodLabel,
                            { color: isSelected ? category.color : theme.text }
                          ]}>
                            {food.name}
                          </Text>
                          {isSelected && (
                            <View style={[styles.checkMark, { backgroundColor: category.color }]}>
                              <Check size={10} color="#FFF" strokeWidth={3} />
                            </View>
                          )}
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </GlassCard>
              </Animated.View>
            );
          })}

          {/* Save Button */}
          <Animated.View entering={FadeInDown.delay(400).springify()} style={styles.saveContainer}>
            <TouchableOpacity onPress={handleSave} disabled={saving} activeOpacity={0.9}>
              <LinearGradient
                colors={saving ? ['#9CA3AF', '#6B7280'] : [premiumColors.gradient.start, premiumColors.gradient.end]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.saveButton}
              >
                <Check size={20} color="#FFF" />
                <Text style={styles.saveButtonText}>{saving ? 'Salvando...' : 'Salvar Preferências'}</Text>
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>

          <View style={{ height: 40 }} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700' },

  subtitle: { 
    fontSize: 14, 
    marginBottom: spacing.xl,
    textAlign: 'center',
  },

  categoryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  categoryTitle: { fontSize: 16, fontWeight: '700' },

  card: { padding: spacing.base, marginBottom: spacing.sm },

  foodsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  foodChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1.5,
    gap: spacing.xs,
  },
  foodLabel: { fontSize: 13, fontWeight: '600' },
  checkMark: {
    width: 16,
    height: 16,
    borderRadius: radius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },

  saveContainer: { marginTop: spacing.xl },
  saveButton: {
    height: 56,
    borderRadius: radius.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  saveButtonText: { color: '#FFF', fontSize: 17, fontWeight: '700' },
});
