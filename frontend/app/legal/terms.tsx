/**
 * Terms of Use - Public Page
 * ==========================
 * Accessible without authentication
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import { ArrowLeft, FileText } from 'lucide-react-native';
import Animated, { FadeInDown } from 'react-native-reanimated';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

export default function PublicTermsScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent']
          : ['rgba(16, 185, 129, 0.08)', 'transparent']
        }
        locations={[0, 0.5]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <Animated.View entering={FadeInDown.springify()} style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <ArrowLeft size={24} color={theme.text} />
          </TouchableOpacity>
          <View style={styles.headerContent}>
            <View style={[styles.iconBg, { backgroundColor: premiumColors.primary + '20' }]}>
              <FileText size={20} color={premiumColors.primary} />
            </View>
            <Text style={[styles.headerTitle, { color: theme.text }]}>{t.settings.termsOfUse}</Text>
          </View>
          <View style={{ width: 44 }} />
        </Animated.View>

        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <View style={[styles.card, { backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)' }]}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>1. {t.legal?.acceptanceTitle || 'Aceitação dos Termos'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.acceptanceText || 'Ao usar o aplicativo LAF, você concorda com estes Termos de Uso. Se não concordar, não utilize o aplicativo.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>2. {t.legal?.serviceTitle || 'Uso do Serviço'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.serviceText || 'O LAF é um aplicativo que oferece sugestões de alimentação e exercícios. As informações fornecidas são de caráter informativo e não substituem orientação profissional.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>3. {t.legal?.accountTitle || 'Conta do Usuário'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.accountText || 'Você é responsável por manter a confidencialidade de sua conta e senha.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>4. {t.legal?.changesTitle || 'Alterações'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.changesText || 'Reservamos o direito de modificar estes termos a qualquer momento. Alterações serão comunicadas através do aplicativo.'}
              </Text>

              <Text style={[styles.lastUpdate, { color: theme.textTertiary }]}>
                {t.legal?.lastUpdate || 'Última atualização'}: Janeiro 2025
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  headerContent: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  iconBg: { width: 36, height: 36, borderRadius: radius.lg, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  scrollContent: { padding: spacing.lg },
  card: {
    borderRadius: radius.xl,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', marginTop: spacing.lg, marginBottom: spacing.sm },
  paragraph: { fontSize: 14, lineHeight: 22 },
  lastUpdate: { fontSize: 12, marginTop: spacing.xl, textAlign: 'center' },
});
