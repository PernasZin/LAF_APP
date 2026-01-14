/**
 * LAF Premium Terms Screen
 * =========================
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, FileText, Scale, AlertTriangle, Heart } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

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

export default function TermsScreen() {
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
            <Text style={[styles.headerTitle, { color: theme.text }]}>{t.terms.title}</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Content */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <GlassCard isDark={isDark} style={styles.card}>
              <View style={styles.section}>
                <View style={styles.sectionHeader}>
                  <FileText size={20} color={premiumColors.primary} />
                  <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.terms.acceptance}</Text>
                </View>
                <Text style={[styles.sectionContent, { color: theme.textSecondary }]}>
                  {t.terms.acceptanceDesc}
                </Text>
              </View>

              <View style={[styles.divider, { backgroundColor: theme.border }]} />

              <View style={styles.section}>
                <View style={styles.sectionHeader}>
                  <Scale size={20} color="#3B82F6" />
                  <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.terms.responsibleUse}</Text>
                </View>
                <Text style={[styles.sectionContent, { color: theme.textSecondary }]}>
                  {t.terms.responsibleUseDesc}
                </Text>
              </View>

              <View style={[styles.divider, { backgroundColor: theme.border }]} />

              <View style={styles.section}>
                <View style={styles.sectionHeader}>
                  <AlertTriangle size={20} color="#F59E0B" />
                  <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.terms.limitations}</Text>
                </View>
                <Text style={[styles.sectionContent, { color: theme.textSecondary }]}>
                  {t.terms.limitationsDesc}
                </Text>
              </View>

              <View style={[styles.divider, { backgroundColor: theme.border }]} />

              <View style={styles.section}>
                <View style={styles.sectionHeader}>
                  <Heart size={20} color="#EC4899" />
                  <Text style={[styles.sectionTitle, { color: theme.text }]}>{t.terms.health}</Text>
                </View>
                <Text style={[styles.sectionContent, { color: theme.textSecondary }]}>
                  {t.terms.healthDesc}
                </Text>
              </View>
            </GlassCard>
          </Animated.View>

          {/* Version */}
          <Animated.View entering={FadeInDown.delay(200).springify()} style={styles.versionContainer}>
            <Text style={[styles.versionText, { color: theme.textTertiary }]}>
              {t.terms.lastUpdate}
            </Text>
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
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  sectionTitle: { fontSize: 16, fontWeight: '700' },
  sectionContent: { fontSize: 14, lineHeight: 22 },
  divider: { height: 1, marginVertical: spacing.md },

  versionContainer: { alignItems: 'center', marginTop: spacing.lg },
  versionText: { fontSize: 12 },
});
