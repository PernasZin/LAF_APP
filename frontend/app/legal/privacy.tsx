/**
 * Privacy Policy - Public Page
 * =============================
 * Accessible without authentication
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import { ArrowLeft, Shield } from 'lucide-react-native';
import Animated, { FadeInDown } from 'react-native-reanimated';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

export default function PublicPrivacyScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  const { t } = useTranslation();

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(59, 130, 246, 0.05)', 'transparent']
          : ['rgba(59, 130, 246, 0.08)', 'transparent']
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
            <View style={[styles.iconBg, { backgroundColor: '#3B82F6' + '20' }]}>
              <Shield size={20} color="#3B82F6" />
            </View>
            <Text style={[styles.headerTitle, { color: theme.text }]}>{t.settings.privacy}</Text>
          </View>
          <View style={{ width: 44 }} />
        </Animated.View>

        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <View style={[styles.card, { backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)' }]}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>1. {t.legal?.dataCollectionTitle || 'Coleta de Dados'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.dataCollectionText || 'Coletamos informações que você fornece diretamente, como dados de perfil, peso, altura, objetivos fitness e preferências alimentares.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>2. {t.legal?.dataUseTitle || 'Uso dos Dados'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.dataUseText || 'Seus dados são usados para personalizar planos de dieta e treino, melhorar nossos serviços e fornecer suporte.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>3. {t.legal?.dataSharingTitle || 'Compartilhamento'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.dataSharingText || 'Não vendemos seus dados pessoais. Podemos compartilhar dados anonimizados para fins de pesquisa e melhoria do serviço.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>4. {t.legal?.securityTitle || 'Segurança'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.securityText || 'Implementamos medidas de segurança para proteger seus dados contra acesso não autorizado.'}
              </Text>

              <Text style={[styles.sectionTitle, { color: theme.text }]}>5. {t.legal?.rightsTitle || 'Seus Direitos'}</Text>
              <Text style={[styles.paragraph, { color: theme.textSecondary }]}>
                {t.legal?.rightsText || 'Você tem direito de acessar, corrigir ou excluir seus dados pessoais a qualquer momento através das configurações do aplicativo.'}
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
