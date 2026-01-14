/**
 * LAF Premium Settings Screen
 * ============================
 * Glassmorphism + Gradientes + Animações
 */

import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { router } from 'expo-router';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { 
  User, Utensils, Bell, Shield, FileText, LogOut, 
  ChevronRight, Moon, Sun, Palette, Target, Scale,
  Mail, HelpCircle, Star, ExternalLink, Dumbbell
} from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { useAuthStore } from '../../stores/authStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Glass Card Component
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

// Settings Row Component
const SettingsRow = ({ icon, label, value, onPress, isDark, showArrow = true, isDestructive = false }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  const iconColor = isDestructive ? '#EF4444' : premiumColors.primary;
  
  return (
    <TouchableOpacity 
      style={styles.settingsRow} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.settingsIconBg, { backgroundColor: `${iconColor}15` }]}>
        {React.cloneElement(icon, { size: 20, color: iconColor })}
      </View>
      <View style={styles.settingsContent}>
        <Text style={[styles.settingsLabel, { color: isDestructive ? '#EF4444' : theme.text }]}>
          {label}
        </Text>
        {value && (
          <Text style={[styles.settingsValue, { color: theme.textTertiary }]}>{value}</Text>
        )}
      </View>
      {showArrow && <ChevronRight size={20} color={theme.textTertiary} />}
    </TouchableOpacity>
  );
};

// Settings Toggle Row
const SettingsToggle = ({ icon, label, value, onToggle, isDark }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <View style={styles.settingsRow}>
      <View style={[styles.settingsIconBg, { backgroundColor: `${premiumColors.primary}15` }]}>
        {React.cloneElement(icon, { size: 20, color: premiumColors.primary })}
      </View>
      <View style={styles.settingsContent}>
        <Text style={[styles.settingsLabel, { color: theme.text }]}>{label}</Text>
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

export default function SettingsScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const themePreference = useSettingsStore((state) => state.themePreference);
  const setThemePreference = useSettingsStore((state) => state.setThemePreference);
  const authLogout = useAuthStore((state) => state.logout);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();
  
  const [profile, setProfile] = useState<any>(null);

  useFocusEffect(
    useCallback(() => {
      loadProfile();
    }, [])
  );

  const loadProfile = async () => {
    try {
      const data = await AsyncStorage.getItem('userProfile');
      if (data) setProfile(JSON.parse(data));
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleLogout = () => {
    if (Platform.OS === 'web') {
      // Para web, usar confirm do navegador
      if (window.confirm(t.settings.logoutConfirm)) {
        (async () => {
          await authLogout();
          router.replace('/auth/login');
        })();
      }
    } else {
      // Para mobile, usar Alert nativo
      Alert.alert(
        t.settings.logoutTitle,
        t.settings.logoutConfirm,
        [
          { text: t.settings.cancel, style: 'cancel' },
          {
            text: t.settings.logout,
            style: 'destructive',
            onPress: async () => {
              await authLogout();
              router.replace('/auth/login');
            },
          },
        ]
      );
    }
  };

  const getGoalLabel = (goal: string) => {
    const goals: any = {
      cutting: `🔥 ${t.home.cutting}`,
      bulking: `💪 ${t.home.bulking}`,
      manutencao: `⚖️ ${t.home.maintenance}`,
    };
    return goals[goal] || goal;
  };

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    setThemePreference(newTheme);
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Background Gradient */}
      <LinearGradient
        colors={isDark 
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']
        }
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <Text style={[styles.headerTitle, { color: theme.text }]}>Configurações</Text>
            <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
              Personalize sua experiência
            </Text>
          </Animated.View>

          {/* Profile Card */}
          {profile && (
            <Animated.View entering={FadeInDown.delay(100).springify()}>
              <TouchableOpacity 
                onPress={() => router.push('/settings/edit-profile')}
                activeOpacity={0.9}
              >
                <GlassCard isDark={isDark} style={styles.profileCard}>
                  <LinearGradient
                    colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={styles.profileAvatar}
                  >
                    <Text style={styles.profileInitial}>
                      {profile.name?.charAt(0)?.toUpperCase() || 'U'}
                    </Text>
                  </LinearGradient>
                  <View style={styles.profileInfo}>
                    <Text style={[styles.profileName, { color: theme.text }]}>
                      {profile.name || 'Usuário'}
                    </Text>
                    <Text style={[styles.profileGoal, { color: theme.textSecondary }]}>
                      {getGoalLabel(profile.goal)}
                    </Text>
                  </View>
                  <ChevronRight size={22} color={theme.textTertiary} />
                </GlassCard>
              </TouchableOpacity>
            </Animated.View>
          )}

          {/* Account Section */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>CONTA</Text>
            <GlassCard isDark={isDark} style={styles.settingsCard}>
              <SettingsRow
                icon={<User />}
                label="Editar Perfil"
                value={null}
                onPress={() => router.push('/settings/edit-profile')}
                isDark={isDark}
              />
            </GlassCard>
          </Animated.View>

          {/* Diet Section */}
          <Animated.View entering={FadeInDown.delay(250).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>DIETA</Text>
            <GlassCard isDark={isDark} style={styles.settingsCard}>
              <SettingsRow
                icon={<Utensils />}
                label="Refeições por Dia"
                value={profile?.meal_count ? `${profile.meal_count} refeições` : null}
                onPress={() => router.push('/settings/meal-config')}
                isDark={isDark}
              />
            </GlassCard>
          </Animated.View>

          {/* Training Section */}
          <Animated.View entering={FadeInDown.delay(275).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>TREINO</Text>
            <GlassCard isDark={isDark} style={styles.settingsCard}>
              <SettingsRow
                icon={<Dumbbell />}
                label="Configurar Treino"
                value={profile?.weekly_training_frequency ? `${profile.weekly_training_frequency}x/semana` : null}
                onPress={() => router.push('/settings/training-config')}
                isDark={isDark}
              />
            </GlassCard>
          </Animated.View>

          {/* Preferences Section */}
          <Animated.View entering={FadeInDown.delay(300).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>PREFERÊNCIAS</Text>
            <GlassCard isDark={isDark} style={styles.settingsCard}>
              <SettingsToggle
                icon={isDark ? <Moon /> : <Sun />}
                label="Modo Claro"
                value={!isDark}
                onToggle={toggleTheme}
                isDark={isDark}
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <SettingsRow
                icon={<Bell />}
                label="Notificações"
                onPress={() => router.push('/settings/notifications')}
                isDark={isDark}
              />
            </GlassCard>
          </Animated.View>

          {/* Support Section */}
          <Animated.View entering={FadeInDown.delay(400).springify()}>
            <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>SUPORTE</Text>
            <GlassCard isDark={isDark} style={styles.settingsCard}>
              <SettingsRow
                icon={<Shield />}
                label="Privacidade"
                onPress={() => router.push('/settings/privacy')}
                isDark={isDark}
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <SettingsRow
                icon={<FileText />}
                label="Termos de Uso"
                onPress={() => router.push('/settings/terms')}
                isDark={isDark}
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <SettingsRow
                icon={<HelpCircle />}
                label="Ajuda"
                onPress={() => {}}
                isDark={isDark}
              />
            </GlassCard>
          </Animated.View>

          {/* Logout Section */}
          <Animated.View entering={FadeInDown.delay(500).springify()}>
            <GlassCard isDark={isDark} style={styles.settingsCard}>
              <SettingsRow
                icon={<LogOut />}
                label="Sair da Conta"
                onPress={handleLogout}
                isDark={isDark}
                showArrow={false}
                isDestructive
              />
            </GlassCard>
          </Animated.View>

          {/* Version */}
          <Animated.View entering={FadeInDown.delay(600).springify()} style={styles.versionContainer}>
            <Text style={[styles.versionText, { color: theme.textTertiary }]}>
              LAF v2.0 Premium
            </Text>
            <Text style={[styles.versionSubtext, { color: theme.textTertiary }]}>
              Feito com 💚 para você
            </Text>
          </Animated.View>

          {/* Bottom Spacing */}
          <View style={{ height: 100 }} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg },
  
  // Header
  header: {
    marginBottom: spacing.xl,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: '800',
    letterSpacing: -1,
  },
  headerSubtitle: {
    fontSize: 15,
    marginTop: spacing.xs,
    fontWeight: '500',
  },
  
  // Profile Card
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  profileAvatar: {
    width: 56,
    height: 56,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  profileInitial: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFF',
  },
  profileInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  profileGoal: {
    fontSize: 14,
    marginTop: 2,
  },
  
  // Section
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: spacing.sm,
    marginLeft: spacing.xs,
  },
  
  // Settings Card
  settingsCard: {
    marginBottom: spacing.lg,
    overflow: 'hidden',
  },
  settingsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.base,
    gap: spacing.md,
  },
  settingsIconBg: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingsContent: {
    flex: 1,
  },
  settingsLabel: {
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: -0.2,
  },
  settingsValue: {
    fontSize: 13,
    marginTop: 2,
  },
  divider: {
    height: 1,
    marginHorizontal: spacing.base,
  },
  
  // Version
  versionContainer: {
    alignItems: 'center',
    marginTop: spacing.xl,
    gap: spacing.xs,
  },
  versionText: {
    fontSize: 13,
    fontWeight: '600',
  },
  versionSubtext: {
    fontSize: 12,
  },
});
