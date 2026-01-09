import React, { useState } from 'react';
import {
  View, Text, StyleSheet, TextInput, TouchableOpacity,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, Modal, Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, Link } from 'expo-router';
import { useAuthStore } from '../../stores/authStore';
import { useSettingsStore } from '../../stores/settingsStore';
import { useTranslation } from '../../i18n';
import { SupportedLanguage } from '../../i18n/translations';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Language options with flags
const LANGUAGES = [
  { code: 'pt-BR' as SupportedLanguage, label: 'Português', flag: '🇧🇷' },
  { code: 'en-US' as SupportedLanguage, label: 'English', flag: '🇺🇸' },
  { code: 'es-ES' as SupportedLanguage, label: 'Español', flag: '🇪🇸' },
];

export default function LoginScreen() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const { t } = useTranslation();
  
  // Language settings
  const language = useSettingsStore((s) => s.language) as SupportedLanguage;
  const setLanguage = useSettingsStore((s) => s.setLanguage);
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  
  const currentLang = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectLanguage = (langCode: SupportedLanguage) => {
    setLanguage(langCode);
    setShowLanguageModal(false);
  };

  const handleLogin = async () => {
    if (!email.trim() || !password) {
      setError(t.common.error);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });
      
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.detail || t.common.error);
      
      // Save to AuthStore (SINGLE SOURCE OF TRUTH)
      await login(data.user_id, data.access_token, data.profile_completed);
      
      // AuthGuard will handle redirect
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          
          {/* Language Selector - Top Right */}
          <TouchableOpacity 
            style={styles.languageButton} 
            onPress={() => setShowLanguageModal(true)}
          >
            <Text style={styles.languageFlag}>{currentLang.flag}</Text>
            <Text style={styles.languageText}>{currentLang.label}</Text>
            <Ionicons name="chevron-down" size={16} color="#6B7280" />
          </TouchableOpacity>
          
          <View style={styles.header}>
            <View style={styles.logo}><Ionicons name="fitness" size={60} color="#10B981" /></View>
            <Text style={styles.title}>LAF</Text>
            <Text style={styles.subtitle}>{t.auth.enterAccount}</Text>
          </View>

          {error && (
            <View style={styles.errorBox}>
              <Ionicons name="alert-circle" size={20} color="#EF4444" />
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <View style={styles.form}>
            <Text style={styles.label}>{t.auth.email}</Text>
            <View style={styles.inputBox}>
              <Ionicons name="mail-outline" size={20} color="#9CA3AF" />
              <TextInput
                style={styles.input}
                value={email}
                onChangeText={setEmail}
                placeholder="seu@email.com"
                placeholderTextColor="#9CA3AF"
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <Text style={styles.label}>{t.auth.password}</Text>
            <View style={styles.inputBox}>
              <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" />
              <TextInput
                style={styles.input}
                value={password}
                onChangeText={setPassword}
                placeholder="********"
                placeholderTextColor="#9CA3AF"
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20} color="#9CA3AF" />
              </TouchableOpacity>
            </View>

            <TouchableOpacity style={[styles.button, loading && styles.buttonDisabled]} onPress={handleLogin} disabled={loading}>
              {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>{t.auth.login}</Text>}
            </TouchableOpacity>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>{t.auth.noAccount}</Text>
            <Link href="/auth/signup" asChild>
              <TouchableOpacity><Text style={styles.link}>{t.auth.createAccount}</Text></TouchableOpacity>
            </Link>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
      
      {/* Language Selection Modal */}
      <Modal
        visible={showLanguageModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowLanguageModal(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setShowLanguageModal(false)}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{t.settings.language}</Text>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.languageOption,
                  language === lang.code && styles.languageOptionActive
                ]}
                onPress={() => handleSelectLanguage(lang.code)}
              >
                <Text style={styles.languageOptionFlag}>{lang.flag}</Text>
                <Text style={[
                  styles.languageOptionText,
                  language === lang.code && styles.languageOptionTextActive
                ]}>
                  {lang.label}
                </Text>
                {language === lang.code && (
                  <Ionicons name="checkmark-circle" size={22} color="#10B981" />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </Pressable>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { flexGrow: 1, padding: 24, justifyContent: 'center' },
  // Language selector button
  languageButton: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    alignSelf: 'flex-end',
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 6,
    marginBottom: 16,
  },
  languageFlag: { fontSize: 18 },
  languageText: { fontSize: 14, fontWeight: '500', color: '#374151' },
  header: { alignItems: 'center', marginBottom: 32 },
  logo: { width: 100, height: 100, borderRadius: 50, backgroundColor: '#F0FDF4', justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  title: { fontSize: 36, fontWeight: '700', color: '#10B981' },
  subtitle: { fontSize: 16, color: '#6B7280', marginTop: 8 },
  errorBox: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FEF2F2', borderRadius: 12, padding: 12, marginBottom: 16, gap: 8 },
  errorText: { color: '#EF4444', fontSize: 14, flex: 1 },
  form: { marginBottom: 32 },
  label: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 8, marginTop: 16 },
  inputBox: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F9FAFB', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB', paddingHorizontal: 16, height: 52 },
  input: { flex: 1, fontSize: 16, color: '#111827', marginLeft: 12 },
  button: { backgroundColor: '#10B981', height: 56, borderRadius: 12, justifyContent: 'center', alignItems: 'center', marginTop: 24 },
  buttonDisabled: { backgroundColor: '#9CA3AF' },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  footer: { flexDirection: 'row', justifyContent: 'center', gap: 8 },
  footerText: { fontSize: 14, color: '#6B7280' },
  link: { fontSize: 14, fontWeight: '600', color: '#10B981' },
  // Modal styles
  modalOverlay: { 
    flex: 1, 
    backgroundColor: 'rgba(0,0,0,0.5)', 
    justifyContent: 'center', 
    alignItems: 'center',
    padding: 24,
  },
  modalContent: { 
    backgroundColor: '#fff', 
    borderRadius: 16, 
    padding: 20,
    width: '100%',
    maxWidth: 300,
  },
  modalTitle: { 
    fontSize: 18, 
    fontWeight: '700', 
    color: '#111827', 
    marginBottom: 16,
    textAlign: 'center',
  },
  languageOption: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderRadius: 12,
    marginBottom: 8,
    backgroundColor: '#F9FAFB',
    gap: 12,
  },
  languageOptionActive: { 
    backgroundColor: '#F0FDF4',
    borderWidth: 2,
    borderColor: '#10B981',
  },
  languageOptionFlag: { fontSize: 24 },
  languageOptionText: { 
    flex: 1, 
    fontSize: 16, 
    fontWeight: '500', 
    color: '#374151' 
  },
  languageOptionTextActive: { 
    color: '#10B981', 
    fontWeight: '600' 
  },
});
