/**
 * LAF Premium Notifications Screen
 * =================================
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Bell, Clock, Scale, Utensils, Droplets } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';

const GlassCard = ({ children, style, isDark }: any) => {
  const cardStyle = {
    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
    borderWidth: 1,
    borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
    borderRadius: radius.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: isDark ? 0.3 : 0.08,
    shadowRadius: 16,
    elevation: 8,
  };
  return <View style={[cardStyle, style]}>{children}</View>;
};

const NotificationRow = ({ icon: Icon, label, desc, value, onToggle, isDark, color = premiumColors.primary }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  return (
    <View style={[styles.notifRow, { borderBottomColor: theme.border }]}>
      <View style={[styles.notifIconBg, { backgroundColor: color + '15' }]}>
        <Icon size={20} color={color} />
      </View>
      <View style={styles.notifContent}>
        <Text style={[styles.notifLabel, { color: theme.text }]}>{label}</Text>
        <Text style={[styles.notifDesc, { color: theme.textTertiary }]}>{desc}</Text>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: theme.border, true: premiumColors.primary + '50' }}
        thumbColor={value ? premiumColors.primary : theme.textTertiary}
      />
    </View>
  );
};

export default function NotificationsScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [mealReminders, setMealReminders] = useState(true);
  const [waterReminders, setWaterReminders] = useState(true);
  const [weightReminders, setWeightReminders] = useState(true);
  const [workoutReminders, setWorkoutReminders] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const settings = await AsyncStorage.getItem('notificationSettings');
      if (settings) {
        const data = JSON.parse(settings);
        setMealReminders(data.mealReminders ?? true);
        setWaterReminders(data.waterReminders ?? true);
        setWeightReminders(data.weightReminders ?? true);
        setWorkoutReminders(data.workoutReminders ?? true);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const saveSettings = async (key: string, value: boolean) => {
    try {
      const settings = await AsyncStorage.getItem('notificationSettings');
      const data = settings ? JSON.parse(settings) : {};
      data[key] = value;
      await AsyncStorage.setItem('notificationSettings', JSON.stringify(data));
    } catch (error) {
      console.error('Error saving settings:', error);
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
            <Text style={[styles.headerTitle, { color: theme.text }]}>Notificações</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Notification Settings */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>LEMBRETES</Text>
            <GlassCard isDark={isDark} style={styles.card}>
              <NotificationRow
                icon={Utensils}
                label="Refeições"
                desc="Lembrar de fazer as refeições"
                value={mealReminders}
                onToggle={(v: boolean) => { setMealReminders(v); saveSettings('mealReminders', v); }}
                isDark={isDark}
                color="#F59E0B"
              />
              <NotificationRow
                icon={Droplets}
                label="Hidratar"
                desc="Lembrar de beber água"
                value={waterReminders}
                onToggle={(v: boolean) => { setWaterReminders(v); saveSettings('waterReminders', v); }}
                isDark={isDark}
                color="#3B82F6"
              />
              <NotificationRow
                icon={Scale}
                label="Peso"
                desc="Lembrar de registrar peso"
                value={weightReminders}
                onToggle={(v: boolean) => { setWeightReminders(v); saveSettings('weightReminders', v); }}
                isDark={isDark}
                color="#10B981"
              />
              <NotificationRow
                icon={Clock}
                label="Exercícios"
                desc="Lembrar dos exercícios"
                value={workoutReminders}
                onToggle={(v: boolean) => { setWorkoutReminders(v); saveSettings('workoutReminders', v); }}
                isDark={isDark}
                color="#8B5CF6"
              />
            </GlassCard>
          </Animated.View>

          {/* Info */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <View style={[styles.infoBox, { backgroundColor: premiumColors.primary + '10' }]}>
              <Bell size={18} color={premiumColors.primary} />
              <Text style={[styles.infoText, { color: theme.textSecondary }]}>
                As notificações ajudam você a manter o foco nos seus objetivos.
              </Text>
            </View>
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
  card: { marginBottom: spacing.lg, overflow: 'hidden' },

  notifRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.base,
    borderBottomWidth: 1,
    gap: spacing.md,
  },
  notifIconBg: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  notifContent: { flex: 1 },
  notifLabel: { fontSize: 15, fontWeight: '600' },
  notifDesc: { fontSize: 12, marginTop: 2 },

  infoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    padding: spacing.base,
    borderRadius: radius.lg,
  },
  infoText: { flex: 1, fontSize: 13, lineHeight: 18 },
});
