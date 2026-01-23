/**
 * LAF Premium Privacy Screen
 * ===========================
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Modal, TextInput, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Shield, Lock, Eye, Database, Trash2, AlertTriangle, X } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { useAuthStore } from '../../stores/authStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';
import { config } from '../../config';

const BACKEND_URL = config.BACKEND_URL;

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

const Section = ({ icon: Icon, title, content, isDark, color = premiumColors.primary }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <View style={[styles.sectionIconBg, { backgroundColor: color + '15' }]}>
          <Icon size={20} color={color} />
        </View>
        <Text style={[styles.sectionTitle, { color: theme.text }]}>{title}</Text>
      </View>
      <Text style={[styles.sectionContent, { color: theme.textSecondary }]}>{content}</Text>
    </View>
  );
};

export default function PrivacyScreen() {
  const { t } = useTranslation();
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

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
            <Text style={[styles.headerTitle, { color: theme.text }]}>{t.privacy.title}</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Content */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <GlassCard isDark={isDark} style={styles.card}>
              <Section
                icon={Shield}
                title={t.privacy.dataSecurity}
                content={t.privacy.dataSecurityDesc}
                isDark={isDark}
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <Section
                icon={Lock}
                title={t.privacy.protectedAccess}
                content={t.privacy.protectedAccessDesc}
                isDark={isDark}
                color="#3B82F6"
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <Section
                icon={Eye}
                title={t.privacy.transparency}
                content={t.privacy.transparencyDesc}
                isDark={isDark}
                color="#8B5CF6"
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <Section
                icon={Database}
                title={t.privacy.localStorage}
                content={t.privacy.localStorageDesc}
                isDark={isDark}
                color="#F59E0B"
              />
            </GlassCard>
          </Animated.View>

          {/* Delete Account */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <TouchableOpacity style={[styles.deleteButton, { borderColor: '#EF4444' }]}>
              <Trash2 size={18} color="#EF4444" />
              <Text style={styles.deleteButtonText}>{t.privacy.requestDeletion}</Text>
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

  card: { padding: spacing.lg, marginBottom: spacing.lg },
  section: { paddingVertical: spacing.sm },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.sm },
  sectionIconBg: { width: 36, height: 36, borderRadius: radius.md, alignItems: 'center', justifyContent: 'center' },
  sectionTitle: { fontSize: 16, fontWeight: '700' },
  sectionContent: { fontSize: 14, lineHeight: 20, marginLeft: 48 },
  divider: { height: 1, marginVertical: spacing.md },

  deleteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    padding: spacing.base,
    borderRadius: radius.lg,
    borderWidth: 1.5,
  },
  deleteButtonText: { color: '#EF4444', fontSize: 15, fontWeight: '600' },
});
