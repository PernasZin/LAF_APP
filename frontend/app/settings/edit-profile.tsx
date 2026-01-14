/**
 * LAF Premium Edit Profile Screen
 * ================================
 * Apenas: Nome, Email, Objetivo
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ScrollView, Alert, KeyboardAvoidingView, Platform
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, User, Mail, Target, Check } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

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

const GOALS = [
  { id: 'cutting', label: '🔥 Cutting', desc: 'Perder gordura' },
  { id: 'manutencao', label: '⚖️ Manutenção', desc: 'Manter peso' },
  { id: 'bulking', label: '💪 Bulking', desc: 'Ganhar massa' },
];

export default function EditProfileScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [goal, setGoal] = useState('manutencao');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const id = await AsyncStorage.getItem('userId');
      const storedEmail = await AsyncStorage.getItem('userEmail');
      setUserId(id);
      if (storedEmail) setEmail(storedEmail);

      if (id && BACKEND_URL) {
        const response = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
        if (response.ok) {
          const data = await response.json();
          setName(data.name || '');
          setGoal(data.goal || 'manutencao');
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!name.trim()) {
      Alert.alert('Campo obrigatório', 'Preencha o nome.');
      return;
    }

    setSaving(true);
    try {
      const response = await safeFetch(`${BACKEND_URL}/api/user/profile/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          goal,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        await AsyncStorage.setItem('userProfile', JSON.stringify(data));
        if (email.trim()) {
          await AsyncStorage.setItem('userEmail', email.trim());
        }
        Alert.alert('Sucesso', 'Perfil atualizado!', [
          { text: 'OK', onPress: () => router.back() }
        ]);
      } else {
        Alert.alert('Erro', 'Não foi possível salvar');
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <View style={styles.loadingContainer}>
          <Text style={{ color: theme.text }}>Carregando...</Text>
        </View>
      </SafeAreaView>
    );
  }

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
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* Header */}
            <Animated.View entering={FadeInDown.springify()} style={styles.header}>
              <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                <ArrowLeft size={24} color={theme.text} />
              </TouchableOpacity>
              <Text style={[styles.headerTitle, { color: theme.text }]}>Editar Perfil</Text>
              <View style={{ width: 44 }} />
            </Animated.View>

            {/* Name & Email */}
            <Animated.View entering={FadeInDown.delay(100).springify()}>
              <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>INFORMAÇÕES</Text>
              <GlassCard isDark={isDark} style={styles.card}>
                {/* Nome */}
                <View style={styles.inputGroup}>
                  <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>Nome</Text>
                  <View style={[styles.inputContainer, { backgroundColor: theme.input.background, borderColor: theme.input.border }]}>
                    <User size={20} color={theme.textTertiary} />
                    <TextInput
                      style={[styles.input, { color: theme.text }]}
                      value={name}
                      onChangeText={setName}
                      placeholder="Seu nome"
                      placeholderTextColor={theme.input.placeholder}
                    />
                  </View>
                </View>

                {/* Email */}
                <View style={styles.inputGroup}>
                  <Text style={[styles.inputLabel, { color: theme.textSecondary }]}>Email</Text>
                  <View style={[styles.inputContainer, { backgroundColor: theme.input.background, borderColor: theme.input.border }]}>
                    <Mail size={20} color={theme.textTertiary} />
                    <TextInput
                      style={[styles.input, { color: theme.text }]}
                      value={email}
                      onChangeText={setEmail}
                      placeholder="seu@email.com"
                      placeholderTextColor={theme.input.placeholder}
                      keyboardType="email-address"
                      autoCapitalize="none"
                    />
                  </View>
                </View>
              </GlassCard>
            </Animated.View>

            {/* Goal */}
            <Animated.View entering={FadeInDown.delay(200).springify()}>
              <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>OBJETIVO</Text>
              <GlassCard isDark={isDark} style={styles.card}>
                {GOALS.map((g, index) => (
                  <TouchableOpacity
                    key={g.id}
                    style={[
                      styles.optionItem, 
                      { borderBottomColor: theme.border },
                      index === GOALS.length - 1 && { borderBottomWidth: 0 }
                    ]}
                    onPress={() => setGoal(g.id)}
                  >
                    <View style={styles.optionContent}>
                      <Text style={[styles.optionLabel, { color: theme.text }]}>{g.label}</Text>
                      <Text style={[styles.optionDesc, { color: theme.textTertiary }]}>{g.desc}</Text>
                    </View>
                    <View style={[
                      styles.radioOuter,
                      { borderColor: goal === g.id ? premiumColors.primary : theme.border }
                    ]}>
                      {goal === g.id && <View style={[styles.radioInner, { backgroundColor: premiumColors.primary }]} />}
                    </View>
                  </TouchableOpacity>
                ))}
              </GlassCard>
            </Animated.View>

            {/* Save Button */}
            <Animated.View entering={FadeInDown.delay(300).springify()} style={styles.saveContainer}>
              <TouchableOpacity onPress={handleSave} disabled={saving} activeOpacity={0.9}>
                <LinearGradient
                  colors={saving
                    ? ['#9CA3AF', '#6B7280']
                    : [premiumColors.gradient.start, premiumColors.gradient.end]
                  }
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.saveButton}
                >
                  <Check size={20} color="#FFF" />
                  <Text style={styles.saveButtonText}>
                    {saving ? 'Salvando...' : 'Salvar Alterações'}
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>

            <View style={{ height: 40 }} />
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  keyboardView: { flex: 1 },
  scrollContent: { padding: spacing.lg },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },

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

  inputGroup: { marginBottom: spacing.md },
  inputLabel: { fontSize: 13, fontWeight: '600', marginBottom: spacing.xs },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 52,
    borderRadius: radius.lg,
    borderWidth: 1,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  input: { flex: 1, fontSize: 16, fontWeight: '500' },

  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  optionContent: { flex: 1 },
  optionLabel: { fontSize: 16, fontWeight: '600' },
  optionDesc: { fontSize: 13, marginTop: 2 },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  radioInner: { width: 12, height: 12, borderRadius: 6 },

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
