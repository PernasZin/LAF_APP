import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  ActivityIndicator,
  Image,
  BackHandler,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect, useRouter } from 'expo-router';
import { useSettingsStore, ThemePreference, LanguagePreference } from '../../stores/settingsStore';
import { useAuthStore } from '../../stores/authStore';
import { useTheme } from '../../theme/ThemeContext';
import { useTranslation } from '../../i18n';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Safe fetch with timeout - prevents blocking UI
const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);
  
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

// Language options
const LANGUAGES: { value: LanguagePreference; label: string; flag: string }[] = [
  { value: 'pt-BR', label: 'Português (Brasil)', flag: '🇧🇷' },
  { value: 'en-US', label: 'English (US)', flag: '🇺🇸' },
  { value: 'es-ES', label: 'Español', flag: '🇪🇸' },
];

export default function SettingsScreen() {
  const router = useRouter();
  const { colors, isDark } = useTheme();
  const { t } = useTranslation();
  const [profile, setProfile] = useState<any>(null);
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Settings store
  const {
    themePreference,
    privacyAnalytics,
    privacyPersonalization,
    privacyNotifications,
    notificationsEnabled,
    language,
    setThemePreference,
    setPrivacyAnalytics,
    setPrivacyPersonalization,
    setPrivacyNotifications,
    setNotificationsEnabled,
    setLanguage,
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
      
      // Load profile image
      const savedImage = await AsyncStorage.getItem('profileImage');
      if (savedImage) {
        setProfileImage(savedImage);
      }
      
      if (id && BACKEND_URL) {
        // Load profile - non-blocking
        try {
          const profileRes = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
          if (profileRes.ok) {
            const data = await profileRes.json();
            setProfile(data);
          }
        } catch (err) {
          const profileData = await AsyncStorage.getItem('userProfile');
          if (profileData) setProfile(JSON.parse(profileData));
        }
        
        // Load settings from backend - non-blocking
        try {
          const settingsRes = await safeFetch(`${BACKEND_URL}/api/user/settings/${id}`);
          if (settingsRes.ok) {
            const { theme_preference, privacy_analytics, privacy_personalization, privacy_notifications } = await settingsRes.json();
            setThemePreference(theme_preference || 'system');
            setPrivacyAnalytics(privacy_analytics ?? true);
            setPrivacyPersonalization(privacy_personalization ?? true);
            setPrivacyNotifications(privacy_notifications ?? true);
          }
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
      await safeFetch(`${BACKEND_URL}/api/user/settings/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
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

  const handleNotificationsToggle = async (value: boolean) => {
    setNotificationsEnabled(value);
    // Save to local storage (estrutura para futura integração push)
    await AsyncStorage.setItem('notificationsEnabled', JSON.stringify(value));
  };

  const handleLanguageChange = (lang: LanguagePreference) => {
    setLanguage(lang);
    // Agora a tradução funciona automaticamente via i18n
  };

  const handleLogout = async () => {
    console.log('🔐 LOGOUT: Botão clicado');
    
    try {
      // 1. Limpa AsyncStorage PRIMEIRO
      await AsyncStorage.clear();
      console.log('🔐 LOGOUT: AsyncStorage limpo');
      
      // 2. Reset AuthStore
      useAuthStore.setState({
        isAuthenticated: false,
        userId: null,
        accessToken: null,
        isInitialized: true,
      });
      console.log('🔐 LOGOUT: AuthStore resetado');
      
      // 3. Reset SettingsStore
      useSettingsStore.setState({
        themePreference: 'system',
        effectiveTheme: 'light',
        privacyAnalytics: true,
        privacyPersonalization: true,
        privacyNotifications: true,
        notificationsEnabled: true,
        language: 'pt-BR',
        isHydrated: false,
      });
      console.log('🔐 LOGOUT: SettingsStore resetado');
      
      // 4. Navega para login
      router.replace('/auth/login');
      console.log('🔐 LOGOUT: Navegação executada');
      
    } catch (error) {
      console.error('🔐 LOGOUT: Erro:', error);
      // Mesmo com erro, força navegação
      router.replace('/auth/login');
    }
  };

  const navigateToEditProfile = () => {
    router.push('/settings/edit-profile');
  };

  const navigateToTerms = () => {
    router.push('/settings/terms');
  };

  const navigateToPrivacyPolicy = () => {
    router.push('/settings/privacy-policy');
  };

  const handleExportData = async () => {
    try {
      if (!userId || !BACKEND_URL) {
        Alert.alert('Erro', 'Não foi possível exportar os dados. Usuário não identificado.');
        return;
      }
      
      setSaving(true);
      
      // Busca todos os dados do usuário
      const [profileRes, dietRes, workoutRes, progressRes] = await Promise.all([
        safeFetch(`${BACKEND_URL}/api/user/profile/${userId}`),
        safeFetch(`${BACKEND_URL}/api/diet/${userId}`),
        safeFetch(`${BACKEND_URL}/api/workout/${userId}`),
        safeFetch(`${BACKEND_URL}/api/progress/weight/${userId}?days=365`),
      ]);
      
      const exportData = {
        exported_at: new Date().toISOString(),
        profile: profileRes.ok ? await profileRes.json() : null,
        diet: dietRes.ok ? await dietRes.json() : null,
        workout: workoutRes.ok ? await workoutRes.json() : null,
        progress: progressRes.ok ? await progressRes.json() : null,
      };
      
      // Salva os dados exportados localmente
      const exportJson = JSON.stringify(exportData, null, 2);
      await AsyncStorage.setItem('exportedUserData', exportJson);
      
      Alert.alert(
        '✅ Dados Exportados',
        `Seus dados foram salvos com sucesso!\n\nPerfil: ${exportData.profile ? '✓' : '✗'}\nDieta: ${exportData.diet ? '✓' : '✗'}\nTreino: ${exportData.workout ? '✓' : '✗'}\nProgresso: ${exportData.progress ? '✓' : '✗'}`,
        [{ text: 'OK' }]
      );
      
    } catch (error) {
      console.error('Export error:', error);
      Alert.alert('Erro', 'Não foi possível exportar os dados. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };

  const handleClearCache = async () => {
    Alert.alert(
      '🗑️ Limpar Cache',
      'Isso irá remover dados temporários armazenados no dispositivo. Seus dados na nuvem não serão afetados.\n\nDeseja continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Limpar',
          style: 'destructive',
          onPress: async () => {
            try {
              setSaving(true);
              
              // Remove apenas dados de cache (não o userId nem authToken)
              const keysToKeep = ['userId', 'authToken', 'userProfile'];
              const allKeys = await AsyncStorage.getAllKeys();
              const keysToRemove = allKeys.filter(key => !keysToKeep.includes(key));
              
              await AsyncStorage.multiRemove(keysToRemove);
              
              Alert.alert('✅ Cache Limpo', 'Os dados em cache foram removidos com sucesso.');
            } catch (error) {
              console.error('Clear cache error:', error);
              Alert.alert('Erro', 'Não foi possível limpar o cache.');
            } finally {
              setSaving(false);
            }
          }
        }
      ]
    );
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
          <Text style={[styles.headerTitle, { color: colors.text }]}>{t.settings.title}</Text>
          {saving && <ActivityIndicator size="small" color={colors.primary} />}
        </View>

        {/* Account Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>{t.settings.account.toUpperCase()}</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <TouchableOpacity style={styles.profileRow} onPress={navigateToEditProfile}>
              <View style={styles.profileInfo}>
                {profileImage ? (
                  <Image source={{ uri: profileImage }} style={styles.avatarImage} />
                ) : (
                  <View style={[styles.avatar, { backgroundColor: colors.primaryLight }]}>
                    <Text style={styles.avatarText}>
                      {profile?.name?.charAt(0)?.toUpperCase() || 'U'}
                    </Text>
                  </View>
                )}
                <View style={styles.profileDetails}>
                  <Text style={[styles.profileName, { color: colors.text }]}>
                    {profile?.name || 'Usuário'}
                  </Text>
                  <Text style={[styles.profileMeta, { color: colors.textSecondary }]}>
                    {profile?.goal === 'bulking' ? t.home.bulking :
                     profile?.goal === 'cutting' ? t.home.cutting : t.home.maintenance}
                  </Text>
                </View>
              </View>
              <View style={styles.editProfileArrow}>
                <Text style={[styles.editText, { color: colors.primary }]}>{t.settings.editProfile}</Text>
                <Ionicons name="chevron-forward" size={20} color={colors.primary} />
              </View>
            </TouchableOpacity>
            
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
              <Ionicons name="log-out-outline" size={20} color={colors.error} />
              <Text style={[styles.logoutText, { color: colors.error }]}>{t.settings.logout}</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>{t.settings.notifications.toUpperCase()}</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <SettingToggle
              icon="notifications-outline"
              label={t.settings.enableNotifications}
              description={t.settings.notificationsDesc}
              value={notificationsEnabled}
              onToggle={handleNotificationsToggle}
              colors={colors}
            />
            
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <TouchableOpacity style={styles.legalItem} onPress={() => router.push('/settings/notifications')}>
              <View style={styles.legalItemContent}>
                <Ionicons name="settings-outline" size={20} color={colors.primary} />
                <View style={{ flex: 1, marginLeft: 12 }}>
                  <Text style={[styles.legalText, { color: colors.text }]}>{t.settings.configureReminders}</Text>
                  <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                    {t.settings.remindersDesc}
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Diet Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
            {language === 'en-US' ? 'DIET' : language === 'es-ES' ? 'DIETA' : 'DIETA'}
          </Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <TouchableOpacity style={styles.legalItem} onPress={() => router.push('/settings/meal-config')}>
              <View style={styles.legalItemContent}>
                <Ionicons name="restaurant-outline" size={20} color={colors.primary} />
                <View style={{ flex: 1, marginLeft: 12 }}>
                  <Text style={[styles.legalText, { color: colors.text }]}>
                    {language === 'en-US' ? 'Meal Configuration' : 
                     language === 'es-ES' ? 'Configuración de Comidas' : 
                     'Configuração de Refeições'}
                  </Text>
                  <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                    {language === 'en-US' ? 'Number of meals and times' : 
                     language === 'es-ES' ? 'Número de comidas y horarios' : 
                     'Quantidade de refeições e horários'}
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Appearance Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>{t.settings.appearance.toUpperCase()}</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <Text style={[styles.settingLabel, { color: colors.text }]}>{t.settings.theme}</Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              {t.settings.themeDesc}
            </Text>
            
            <View style={styles.themeOptions}>
              <ThemeOption
                label={t.settings.system}
                icon="phone-portrait-outline"
                selected={themePreference === 'system'}
                onPress={() => handleThemeChange('system')}
                colors={colors}
              />
              <ThemeOption
                label={t.settings.light}
                icon="sunny-outline"
                selected={themePreference === 'light'}
                onPress={() => handleThemeChange('light')}
                colors={colors}
              />
              <ThemeOption
                label={t.settings.dark}
                icon="moon-outline"
                selected={themePreference === 'dark'}
                onPress={() => handleThemeChange('dark')}
                colors={colors}
              />
            </View>
          </View>
        </View>

        {/* Language Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>{t.settings.language.toUpperCase()}</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            {LANGUAGES.map((lang, index) => (
              <React.Fragment key={lang.value}>
                {index > 0 && <View style={[styles.divider, { backgroundColor: colors.border }]} />}
                <LanguageOption
                  flag={lang.flag}
                  label={lang.label}
                  selected={language === lang.value}
                  onPress={() => handleLanguageChange(lang.value)}
                  colors={colors}
                />
              </React.Fragment>
            ))}
          </View>
        </View>

        {/* Data Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>{t.settings.data.toUpperCase()}</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            
            <TouchableOpacity style={styles.legalItem} onPress={handleClearCache}>
              <View style={styles.legalItemContent}>
                <Ionicons name="trash-outline" size={20} color={colors.warning} />
                <View style={{ flex: 1, marginLeft: 12 }}>
                  <Text style={[styles.legalText, { color: colors.text }]}>{t.settings.clearCache}</Text>
                  <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                    {t.settings.clearCacheDesc}
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Legal Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>{t.settings.legal.toUpperCase()}</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <TouchableOpacity style={styles.legalItem} onPress={navigateToPrivacyPolicy}>
              <View style={styles.legalItemContent}>
                <Ionicons name="shield-checkmark-outline" size={20} color={colors.primary} />
                <Text style={[styles.legalText, { color: colors.text }]}>{t.settings.privacy}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
            
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <TouchableOpacity style={styles.legalItem} onPress={navigateToTerms}>
              <View style={styles.legalItemContent}>
                <Ionicons name="document-text-outline" size={20} color={colors.primary} />
                <Text style={[styles.legalText, { color: colors.text }]}>{t.settings.terms}</Text>
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

// Language Option Component
function LanguageOption({ flag, label, selected, onPress, colors }: any) {
  return (
    <TouchableOpacity style={languageStyles.container} onPress={onPress}>
      <View style={languageStyles.content}>
        <Text style={languageStyles.flag}>{flag}</Text>
        <Text style={[languageStyles.label, { color: colors.text }]}>{label}</Text>
      </View>
      {selected && (
        <Ionicons name="checkmark-circle" size={22} color={colors.primary} />
      )}
    </TouchableOpacity>
  );
}

const languageStyles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  flag: {
    fontSize: 24,
    marginRight: 12,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
  },
});

// Setting Toggle Component
function SettingToggle({ icon, label, description, value, onToggle, colors }: any) {
  return (
    <View style={settingToggleStyles.container}>
      <View style={settingToggleStyles.iconContainer}>
        <Ionicons name={icon} size={22} color={colors.primary} />
      </View>
      <View style={settingToggleStyles.textContainer}>
        <Text style={[settingToggleStyles.label, { color: colors.text }]}>{label}</Text>
        <Text style={[settingToggleStyles.description, { color: colors.textSecondary }]}>
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

const settingToggleStyles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  iconContainer: {
    width: 36,
    alignItems: 'center',
    marginRight: 8,
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
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 16,
  },
  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarImage: {
    width: 56,
    height: 56,
    borderRadius: 28,
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
  editProfileArrow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  editText: {
    fontSize: 14,
    fontWeight: '600',
    marginRight: 4,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    marginTop: 8,
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
