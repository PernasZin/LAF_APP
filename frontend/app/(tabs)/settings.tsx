import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Linking,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { useFocusEffect, useRouter } from 'expo-router';
import { useSettingsStore, ThemePreference } from '../../stores/settingsStore';
import { useTheme } from '../../theme/ThemeContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function SettingsScreen() {
  const router = useRouter();
  const { colors, isDark } = useTheme();
  const [profile, setProfile] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Settings store
  const {
    themePreference,
    privacyAnalytics,
    privacyPersonalization,
    privacyNotifications,
    setThemePreference,
    setPrivacyAnalytics,
    setPrivacyPersonalization,
    setPrivacyNotifications,
  } = useSettingsStore();

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  const loadData = async () => {
    try {
      setLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
      
      if (id && BACKEND_URL) {
        // Load profile
        try {
          const profileRes = await axios.get(`${BACKEND_URL}/api/user/profile/${id}`);
          setProfile(profileRes.data);
        } catch (err) {
          const profileData = await AsyncStorage.getItem('userProfile');
          if (profileData) setProfile(JSON.parse(profileData));
        }
        
        // Load settings from backend
        try {
          const settingsRes = await axios.get(`${BACKEND_URL}/api/user/settings/${id}`);
          const { theme_preference, privacy_analytics, privacy_personalization, privacy_notifications } = settingsRes.data;
          setThemePreference(theme_preference || 'system');
          setPrivacyAnalytics(privacy_analytics ?? true);
          setPrivacyPersonalization(privacy_personalization ?? true);
          setPrivacyNotifications(privacy_notifications ?? true);
        } catch (err) {
          // Use local defaults if backend fails
        }
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettingsToBackend = async (settings: any) => {
    if (!userId || !BACKEND_URL) return;
    
    setSaving(true);
    try {
      await axios.patch(`${BACKEND_URL}/api/user/settings/${userId}`, settings);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleThemeChange = async (theme: ThemePreference) => {
    setThemePreference(theme);
    await saveSettingsToBackend({ theme_preference: theme });
  };

  const handlePrivacyToggle = async (
    setting: 'analytics' | 'personalization' | 'notifications',
    value: boolean
  ) => {
    switch (setting) {
      case 'analytics':
        setPrivacyAnalytics(value);
        await saveSettingsToBackend({ privacy_analytics: value });
        break;
      case 'personalization':
        setPrivacyPersonalization(value);
        await saveSettingsToBackend({ privacy_personalization: value });
        break;
      case 'notifications':
        setPrivacyNotifications(value);
        await saveSettingsToBackend({ privacy_notifications: value });
        break;
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Sair da Conta',
      'Tem certeza que deseja sair? Seus dados locais serão removidos.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sair',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.multiRemove(['userId', 'userProfile', 'hasCompletedOnboarding']);
            router.replace('/onboarding');
          },
        },
      ]
    );
  };

  const openPrivacyPolicy = () => {
    Linking.openURL('https://lafapp.com/privacy');
  };

  const openTermsOfUse = () => {
    Linking.openURL('https://lafapp.com/terms');
  };

  const styles = createStyles(colors);

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Configurações</Text>
          {saving && <ActivityIndicator size="small" color={colors.primary} />}
        </View>

        {/* Account Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>CONTA</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.profileInfo}>
              <View style={[styles.avatar, { backgroundColor: colors.primaryLight }]}>
                <Text style={styles.avatarText}>
                  {profile?.name?.charAt(0)?.toUpperCase() || 'U'}
                </Text>
              </View>
              <View style={styles.profileDetails}>
                <Text style={[styles.profileName, { color: colors.text }]}>
                  {profile?.name || 'Usuário'}
                </Text>
                <Text style={[styles.profileMeta, { color: colors.textSecondary }]}>
                  {profile?.goal === 'bulking' ? 'Ganho de Massa' :
                   profile?.goal === 'cutting' ? 'Perda de Gordura' :
                   profile?.goal === 'atleta' ? 'Atleta/Competição' : 'Manutenção'}
                </Text>
              </View>
            </View>
            
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
              <Ionicons name="log-out-outline" size={20} color={colors.error} />
              <Text style={[styles.logoutText, { color: colors.error }]}>Sair da Conta</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Appearance Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>APARÊNCIA</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Tema</Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              Escolha como o app deve aparecer
            </Text>
            
            <View style={styles.themeOptions}>
              <ThemeOption
                label="Sistema"
                icon="phone-portrait-outline"
                selected={themePreference === 'system'}
                onPress={() => handleThemeChange('system')}
                colors={colors}
              />
              <ThemeOption
                label="Claro"
                icon="sunny-outline"
                selected={themePreference === 'light'}
                onPress={() => handleThemeChange('light')}
                colors={colors}
              />
              <ThemeOption
                label="Escuro"
                icon="moon-outline"
                selected={themePreference === 'dark'}
                onPress={() => handleThemeChange('dark')}
                colors={colors}
              />
            </View>
          </View>
        </View>

        {/* Privacy Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>PRIVACIDADE E DADOS</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <PrivacyToggle
              label="Analytics"
              description="Permite coleta anônima de dados de uso para melhorar o app"
              value={privacyAnalytics}
              onToggle={(v) => handlePrivacyToggle('analytics', v)}
              colors={colors}
            />
            
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <PrivacyToggle
              label="Personalização com IA"
              description="Usa IA para gerar dietas e treinos personalizados"
              value={privacyPersonalization}
              onToggle={(v) => handlePrivacyToggle('personalization', v)}
              colors={colors}
            />
            
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <PrivacyToggle
              label="Notificações"
              description="Receba lembretes de refeições e treinos"
              value={privacyNotifications}
              onToggle={(v) => handlePrivacyToggle('notifications', v)}
              colors={colors}
            />
          </View>
        </View>

        {/* Legal Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>LEGAL</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <TouchableOpacity style={styles.legalItem} onPress={openPrivacyPolicy}>
              <View style={styles.legalItemContent}>
                <Ionicons name="shield-checkmark-outline" size={20} color={colors.primary} />
                <Text style={[styles.legalText, { color: colors.text }]}>Política de Privacidade</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
            
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <TouchableOpacity style={styles.legalItem} onPress={openTermsOfUse}>
              <View style={styles.legalItemContent}>
                <Ionicons name="document-text-outline" size={20} color={colors.primary} />
                <Text style={[styles.legalText, { color: colors.text }]}>Termos de Uso</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* App Info */}
        <View style={styles.appInfo}>
          <Text style={[styles.appVersion, { color: colors.textTertiary }]}>LAF v1.0.0</Text>
          <Text style={[styles.appCopyright, { color: colors.textTertiary }]}>© 2025 LAF App</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// Theme Option Component
function ThemeOption({ label, icon, selected, onPress, colors }: any) {
  return (
    <TouchableOpacity
      style={[
        themeOptionStyles.container,
        {
          backgroundColor: selected ? colors.primary + '15' : colors.backgroundSecondary,
          borderColor: selected ? colors.primary : colors.border,
        },
      ]}
      onPress={onPress}
    >
      <Ionicons
        name={icon}
        size={24}
        color={selected ? colors.primary : colors.textSecondary}
      />
      <Text
        style={[
          themeOptionStyles.label,
          { color: selected ? colors.primary : colors.text },
        ]}
      >
        {label}
      </Text>
      {selected && (
        <Ionicons name="checkmark-circle" size={18} color={colors.primary} />
      )}
    </TouchableOpacity>
  );
}

const themeOptionStyles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 12,
    borderWidth: 2,
    marginHorizontal: 4,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 6,
    marginBottom: 4,
  },
});

// Privacy Toggle Component
function PrivacyToggle({ label, description, value, onToggle, colors }: any) {
  return (
    <View style={privacyStyles.container}>
      <View style={privacyStyles.textContainer}>
        <Text style={[privacyStyles.label, { color: colors.text }]}>{label}</Text>
        <Text style={[privacyStyles.description, { color: colors.textSecondary }]}>
          {description}
        </Text>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: colors.toggleInactive, true: colors.toggleActive }}
        thumbColor={colors.toggleThumb}
      />
    </View>
  );
}

const privacyStyles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  textContainer: {
    flex: 1,
    marginRight: 12,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
  },
  description: {
    fontSize: 13,
    marginTop: 2,
    lineHeight: 18,
  },
});

const createStyles = (colors: any) => StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 12,
    marginLeft: 4,
  },
  card: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
  },
  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  profileDetails: {
    marginLeft: 16,
    flex: 1,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '700',
  },
  profileMeta: {
    fontSize: 14,
    marginTop: 2,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 13,
    marginBottom: 16,
  },
  themeOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  divider: {
    height: 1,
    marginVertical: 4,
  },
  legalItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
  },
  legalItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legalText: {
    fontSize: 16,
    marginLeft: 12,
  },
  appInfo: {
    alignItems: 'center',
    marginTop: 16,
  },
  appVersion: {
    fontSize: 14,
  },
  appCopyright: {
    fontSize: 12,
    marginTop: 4,
  },
});
