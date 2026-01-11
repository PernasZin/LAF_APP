/**
 * LAF Premium Meal Config Screen
 * ===============================
 * Glassmorphism + Gradientes
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Utensils, Clock, Check, Plus, Minus } from 'lucide-react-native';

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

const MEAL_PRESETS: Record<number, { name: string; time: string }[]> = {
  4: [
    { name: 'Café da Manhã', time: '07:00' },
    { name: 'Almoço', time: '12:00' },
    { name: 'Lanche Tarde', time: '16:00' },
    { name: 'Jantar', time: '20:00' },
  ],
  5: [
    { name: 'Café da Manhã', time: '07:00' },
    { name: 'Lanche Manhã', time: '10:00' },
    { name: 'Almoço', time: '12:30' },
    { name: 'Lanche Tarde', time: '16:00' },
    { name: 'Jantar', time: '19:30' },
  ],
  6: [
    { name: 'Café da Manhã', time: '07:00' },
    { name: 'Lanche Manhã', time: '10:00' },
    { name: 'Almoço', time: '12:30' },
    { name: 'Lanche Tarde', time: '16:00' },
    { name: 'Jantar', time: '19:30' },
    { name: 'Ceia', time: '21:30' },
  ],
};

export default function MealConfigScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [mealCount, setMealCount] = useState(5);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const id = await AsyncStorage.getItem('userId');
    setUserId(id);
    
    if (id) {
      // Busca meal_count das configurações do usuário (user_settings)
      try {
        const response = await fetch(`${BACKEND_URL}/api/user/settings/${id}`);
        if (response.ok) {
          const settings = await response.json();
          setMealCount(settings.meal_count || 6);
        } else {
          // Fallback para profile antigo
          const profile = await AsyncStorage.getItem('userProfile');
          if (profile) {
            const data = JSON.parse(profile);
            setMealCount(data.meal_count || 6);
          }
        }
      } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        // Fallback para profile antigo
        const profile = await AsyncStorage.getItem('userProfile');
        if (profile) {
          const data = JSON.parse(profile);
          setMealCount(data.meal_count || 6);
        }
      }
    }
  };

  const handleSave = async () => {
    if (!userId) return;
    setSaving(true);
    try {
      // 1. Salva meal_count nas configurações do usuário (user_settings)
      const settingsResponse = await fetch(`${BACKEND_URL}/api/user/settings/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meal_count: mealCount }),
      });
      
      if (!settingsResponse.ok) {
        throw new Error('Falha ao salvar configurações');
      }
      
      // 2. Regenera a dieta automaticamente com o novo número de refeições
      const dietResponse = await fetch(`${BACKEND_URL}/api/diet/generate?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (dietResponse.ok) {
        const dietData = await dietResponse.json();
        await AsyncStorage.setItem('userDiet', JSON.stringify(dietData));
      }
      
      Alert.alert('Sucesso', 'Configurações salvas e dieta atualizada!', [{ text: 'OK', onPress: () => router.back() }]);
    } catch (error) {
      console.error('Erro ao salvar:', error);
      Alert.alert('Erro', 'Não foi possível salvar');
    } finally {
      setSaving(false);
    }
  };

  const meals = MEAL_PRESETS[mealCount] || MEAL_PRESETS[5];

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
            <Text style={[styles.headerTitle, { color: theme.text }]}>Refeições</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Meal Count Selector */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>QUANTIDADE DE REFEIÇÕES</Text>
            <GlassCard isDark={isDark} style={styles.card}>
              <View style={styles.countSelector}>
                <TouchableOpacity
                  style={[styles.countBtn, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.5)' : 'rgba(226, 232, 240, 0.8)' }]}
                  onPress={() => setMealCount(Math.max(4, mealCount - 1))}
                  disabled={mealCount <= 4}
                >
                  <Minus size={24} color={mealCount <= 4 ? theme.textTertiary : theme.text} />
                </TouchableOpacity>
                <View style={styles.countDisplay}>
                  <Text style={[styles.countValue, { color: theme.text }]}>{mealCount}</Text>
                  <Text style={[styles.countLabel, { color: theme.textTertiary }]}>refeições/dia</Text>
                </View>
                <TouchableOpacity
                  style={[styles.countBtn, { backgroundColor: isDark ? 'rgba(71, 85, 105, 0.5)' : 'rgba(226, 232, 240, 0.8)' }]}
                  onPress={() => setMealCount(Math.min(6, mealCount + 1))}
                  disabled={mealCount >= 6}
                >
                  <Plus size={24} color={mealCount >= 6 ? theme.textTertiary : theme.text} />
                </TouchableOpacity>
              </View>
            </GlassCard>
          </Animated.View>

          {/* Meal Preview */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>DISTRIBUIÇÃO</Text>
            <GlassCard isDark={isDark} style={styles.card}>
              {meals.map((meal, index) => (
                <View key={index} style={[styles.mealRow, { borderBottomColor: theme.border }]}>
                  <View style={[styles.mealIconBg, { backgroundColor: premiumColors.primary + '15' }]}>
                    <Utensils size={18} color={premiumColors.primary} />
                  </View>
                  <View style={styles.mealInfo}>
                    <Text style={[styles.mealName, { color: theme.text }]}>{meal.name}</Text>
                  </View>
                  <View style={styles.mealTimeContainer}>
                    <Clock size={14} color={theme.textTertiary} />
                    <Text style={[styles.mealTime, { color: theme.textTertiary }]}>{meal.time}</Text>
                  </View>
                </View>
              ))}
            </GlassCard>
          </Animated.View>

          {/* Save Button */}
          <Animated.View entering={FadeInDown.delay(300).springify()} style={styles.saveContainer}>
            <TouchableOpacity onPress={handleSave} disabled={saving} activeOpacity={0.9}>
              <LinearGradient
                colors={saving ? ['#9CA3AF', '#6B7280'] : [premiumColors.gradient.start, premiumColors.gradient.end]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.saveButton}
              >
                <Check size={20} color="#FFF" />
                <Text style={styles.saveButtonText}>{saving ? 'Salvando...' : 'Salvar'}</Text>
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>
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
    marginBottom: spacing.xl,
  },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700' },

  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: spacing.sm,
    marginLeft: spacing.xs,
  },
  card: { padding: spacing.base, marginBottom: spacing.lg },

  countSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  countBtn: {
    width: 56,
    height: 56,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  countDisplay: { alignItems: 'center' },
  countValue: { fontSize: 48, fontWeight: '800', letterSpacing: -2 },
  countLabel: { fontSize: 13, fontWeight: '600', marginTop: 4 },

  mealRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    gap: spacing.md,
  },
  mealIconBg: {
    width: 36,
    height: 36,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mealInfo: { flex: 1 },
  mealName: { fontSize: 15, fontWeight: '600' },
  mealTimeContainer: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  mealTime: { fontSize: 13 },

  saveContainer: { marginTop: spacing.lg },
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
