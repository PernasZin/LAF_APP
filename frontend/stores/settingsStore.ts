/**
 * Settings Store - Single Source of Truth para Theme e Privacy
 * Usa Zustand para gerenciamento de estado global
 * SAFE: Handles initialization errors gracefully
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Appearance } from 'react-native';

export type ThemePreference = 'system' | 'light' | 'dark';

export interface PrivacySettings {
  analytics: boolean;
  personalization: boolean;
  notifications: boolean;
}

export type LanguagePreference = 'pt-BR' | 'en-US' | 'es-ES';

export interface UserSettings {
  theme_preference: ThemePreference;
  privacy_analytics: boolean;
  privacy_personalization: boolean;
  privacy_notifications: boolean;
  notifications_enabled: boolean;
  language: LanguagePreference;
}

interface SettingsState {
  // Theme
  themePreference: ThemePreference;
  effectiveTheme: 'light' | 'dark';
  
  // Privacy
  privacyAnalytics: boolean;
  privacyPersonalization: boolean;
  privacyNotifications: boolean;
  
  // Loading state
  isLoading: boolean;
  isHydrated: boolean;
  
  // Actions
  setThemePreference: (theme: ThemePreference) => void;
  setPrivacyAnalytics: (enabled: boolean) => void;
  setPrivacyPersonalization: (enabled: boolean) => void;
  setPrivacyNotifications: (enabled: boolean) => void;
  loadSettings: (settings: UserSettings) => void;
  getEffectiveTheme: () => 'light' | 'dark';
  setHydrated: (hydrated: boolean) => void;
}

const getSystemTheme = (): 'light' | 'dark' => {
  try {
    return Appearance.getColorScheme() || 'light';
  } catch {
    return 'light';
  }
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      // Default values
      themePreference: 'system',
      effectiveTheme: 'light',
      privacyAnalytics: true,
      privacyPersonalization: true,
      privacyNotifications: true,
      isLoading: false,
      isHydrated: false,
      
      setThemePreference: (theme: ThemePreference) => {
        let effective: 'light' | 'dark';
        if (theme === 'system') {
          effective = getSystemTheme();
        } else {
          effective = theme;
        }
        set({ themePreference: theme, effectiveTheme: effective });
      },
      
      setPrivacyAnalytics: (enabled: boolean) => {
        set({ privacyAnalytics: enabled });
      },
      
      setPrivacyPersonalization: (enabled: boolean) => {
        set({ privacyPersonalization: enabled });
      },
      
      setPrivacyNotifications: (enabled: boolean) => {
        set({ privacyNotifications: enabled });
      },
      
      loadSettings: (settings: UserSettings) => {
        let effective: 'light' | 'dark';
        if (settings.theme_preference === 'system') {
          effective = getSystemTheme();
        } else {
          effective = settings.theme_preference;
        }
        
        set({
          themePreference: settings.theme_preference,
          effectiveTheme: effective,
          privacyAnalytics: settings.privacy_analytics,
          privacyPersonalization: settings.privacy_personalization,
          privacyNotifications: settings.privacy_notifications,
        });
      },
      
      getEffectiveTheme: () => {
        const state = get();
        if (state.themePreference === 'system') {
          return getSystemTheme();
        }
        return state.themePreference;
      },
      
      setHydrated: (hydrated: boolean) => {
        set({ isHydrated: hydrated });
      },
    }),
    {
      name: 'laf-settings',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        themePreference: state.themePreference,
        privacyAnalytics: state.privacyAnalytics,
        privacyPersonalization: state.privacyPersonalization,
        privacyNotifications: state.privacyNotifications,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setHydrated(true);
          // Update effective theme after rehydration
          if (state.themePreference === 'system') {
            state.effectiveTheme = getSystemTheme();
          }
        }
      },
    }
  )
);

// Safe listener for system theme changes
try {
  Appearance.addChangeListener(({ colorScheme }) => {
    try {
      const { themePreference } = useSettingsStore.getState();
      if (themePreference === 'system') {
        useSettingsStore.setState({ effectiveTheme: colorScheme || 'light' });
      }
    } catch (e) {
      // Ignore errors during store initialization
    }
  });
} catch (e) {
  // Ignore if Appearance API is not available
}
