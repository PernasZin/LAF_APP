/**
 * LAF - Metodologia e Fontes
 * ==========================
 * Tela que explica a metodologia de cálculo e cita fontes confiáveis.
 * Necessário para conformidade com Apple Guideline 1.4.1
 */

import React from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, Linking
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Info, Calculator, Activity, Utensils, ExternalLink, BookOpen } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';

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

// Fontes confiáveis
const SOURCES = [
  {
    id: 'mifflin',
    title: 'Mifflin-St Jeor Equation',
    description: 'Fórmula para cálculo do metabolismo basal (BMR)',
    url: 'https://pubmed.ncbi.nlm.nih.gov/2305711/',
    source: 'PubMed / American Journal of Clinical Nutrition'
  },
  {
    id: 'who',
    title: 'WHO - Healthy Diet',
    description: 'Diretrizes gerais sobre alimentação saudável',
    url: 'https://www.who.int/news-room/fact-sheets/detail/healthy-diet',
    source: 'World Health Organization'
  },
  {
    id: 'dri',
    title: 'Dietary Reference Intakes',
    description: 'Referências de ingestão de nutrientes',
    url: 'https://www.nationalacademies.org/our-work/dietary-reference-intakes',
    source: 'National Academies of Sciences'
  },
  {
    id: 'usda',
    title: 'USDA FoodData Central',
    description: 'Base de dados nutricionais de alimentos',
    url: 'https://fdc.nal.usda.gov/',
    source: 'U.S. Department of Agriculture'
  },
];

export default function MethodologyScreen() {
  const { t, language } = useTranslation();
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const openLink = (url: string) => {
    Linking.openURL(url).catch(() => {
      console.error('Could not open URL:', url);
    });
  };

  // Textos traduzidos
  const texts = {
    'pt-BR': {
      title: 'Metodologia e Fontes',
      intro: 'Este app fornece estimativas baseadas em fórmulas científicas e referências públicas. O conteúdo é informativo e educacional. Não substitui acompanhamento profissional.',
      disclaimer: 'Aviso: Consulte um profissional de saúde antes de iniciar mudanças alimentares ou de exercícios.',
      bmrTitle: 'Cálculo do Metabolismo Basal (BMR)',
      bmrDesc: 'Utilizamos a equação Mifflin-St Jeor, considerada uma das mais precisas para estimar o metabolismo basal em adultos saudáveis.',
      tdeeTitle: 'Gasto Energético Total (TDEE)',
      tdeeDesc: 'O TDEE é calculado multiplicando o BMR por um fator de atividade física, com ajustes para frequência de treino e cardio informados.',
      macrosTitle: 'Distribuição de Macronutrientes',
      macrosDesc: 'As sugestões de macros seguem diretrizes gerais de nutrição esportiva, ajustadas ao objetivo informado (ganho muscular, definição ou manutenção).',
      sourcesTitle: 'Fontes e Referências',
      sourcesDesc: 'As estimativas são baseadas nas seguintes fontes públicas e revisadas:',
    },
    'en-US': {
      title: 'Methodology & Sources',
      intro: 'This app provides estimates based on scientific formulas and public references. The content is informational and educational. It does not replace professional guidance.',
      disclaimer: 'Notice: Consult a healthcare professional before starting dietary or exercise changes.',
      bmrTitle: 'Basal Metabolic Rate (BMR) Calculation',
      bmrDesc: 'We use the Mifflin-St Jeor equation, considered one of the most accurate for estimating basal metabolism in healthy adults.',
      tdeeTitle: 'Total Daily Energy Expenditure (TDEE)',
      tdeeDesc: 'TDEE is calculated by multiplying BMR by a physical activity factor, with adjustments for training frequency and cardio reported.',
      macrosTitle: 'Macronutrient Distribution',
      macrosDesc: 'Macro suggestions follow general sports nutrition guidelines, adjusted to the stated goal (muscle gain, definition, or maintenance).',
      sourcesTitle: 'Sources & References',
      sourcesDesc: 'Estimates are based on the following public and peer-reviewed sources:',
    },
    'es-ES': {
      title: 'Metodología y Fuentes',
      intro: 'Esta app proporciona estimaciones basadas en fórmulas científicas y referencias públicas. El contenido es informativo y educativo. No sustituye el acompañamiento profesional.',
      disclaimer: 'Aviso: Consulte a un profesional de la salud antes de iniciar cambios alimentarios o de ejercicios.',
      bmrTitle: 'Cálculo del Metabolismo Basal (BMR)',
      bmrDesc: 'Utilizamos la ecuación Mifflin-St Jeor, considerada una de las más precisas para estimar el metabolismo basal en adultos sanos.',
      tdeeTitle: 'Gasto Energético Total (TDEE)',
      tdeeDesc: 'El TDEE se calcula multiplicando el BMR por un factor de actividad física, con ajustes para la frecuencia de entrenamiento y cardio informados.',
      macrosTitle: 'Distribución de Macronutrientes',
      macrosDesc: 'Las sugerencias de macros siguen directrices generales de nutrición deportiva, ajustadas al objetivo informado (ganancia muscular, definición o mantenimiento).',
      sourcesTitle: 'Fuentes y Referencias',
      sourcesDesc: 'Las estimaciones se basan en las siguientes fuentes públicas y revisadas:',
    },
  };

  const lang = (language as keyof typeof texts) || 'pt-BR';
  const txt = texts[lang] || texts['pt-BR'];

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']}
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
            <Text style={[styles.headerTitle, { color: theme.text }]}>{txt.title}</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Intro Card */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <GlassCard isDark={isDark} style={styles.introCard}>
              <View style={styles.introHeader}>
                <View style={[styles.introIconBg, { backgroundColor: premiumColors.primary + '15' }]}>
                  <BookOpen size={24} color={premiumColors.primary} />
                </View>
                <Text style={[styles.introTitle, { color: theme.text }]}>
                  {language === 'en-US' ? 'About Our Calculations' : language === 'es-ES' ? 'Sobre Nuestros Cálculos' : 'Sobre Nossos Cálculos'}
                </Text>
              </View>
              <Text style={[styles.introText, { color: theme.textSecondary }]}>
                {txt.intro}
              </Text>
              <View style={[styles.disclaimerBox, { backgroundColor: '#F59E0B15' }]}>
                <Info size={16} color="#F59E0B" />
                <Text style={[styles.disclaimerText, { color: '#F59E0B' }]}>
                  {txt.disclaimer}
                </Text>
              </View>
            </GlassCard>
          </Animated.View>

          {/* BMR Section */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <View style={styles.sectionHeader}>
              <Calculator size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{txt.bmrTitle}</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.sectionCard}>
              <Text style={[styles.sectionText, { color: theme.textSecondary }]}>
                {txt.bmrDesc}
              </Text>
              <View style={[styles.formulaBox, { backgroundColor: isDark ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.08)' }]}>
                <Text style={[styles.formulaLabel, { color: premiumColors.primary }]}>
                  {language === 'en-US' ? 'Men' : language === 'es-ES' ? 'Hombres' : 'Homens'}:
                </Text>
                <Text style={[styles.formulaText, { color: theme.text }]}>
                  BMR = 10×peso + 6.25×altura - 5×idade + 5
                </Text>
                <Text style={[styles.formulaLabel, { color: premiumColors.primary, marginTop: 8 }]}>
                  {language === 'en-US' ? 'Women' : language === 'es-ES' ? 'Mujeres' : 'Mulheres'}:
                </Text>
                <Text style={[styles.formulaText, { color: theme.text }]}>
                  BMR = 10×peso + 6.25×altura - 5×idade - 161
                </Text>
              </View>
            </GlassCard>
          </Animated.View>

          {/* TDEE Section */}
          <Animated.View entering={FadeInDown.delay(300).springify()}>
            <View style={styles.sectionHeader}>
              <Activity size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{txt.tdeeTitle}</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.sectionCard}>
              <Text style={[styles.sectionText, { color: theme.textSecondary }]}>
                {txt.tdeeDesc}
              </Text>
              <View style={[styles.formulaBox, { backgroundColor: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.08)' }]}>
                <Text style={[styles.formulaText, { color: theme.text }]}>
                  TDEE = BMR × {language === 'en-US' ? 'Activity Factor' : language === 'es-ES' ? 'Factor de Actividad' : 'Fator de Atividade'}
                </Text>
              </View>
            </GlassCard>
          </Animated.View>

          {/* Macros Section */}
          <Animated.View entering={FadeInDown.delay(400).springify()}>
            <View style={styles.sectionHeader}>
              <Utensils size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{txt.macrosTitle}</Text>
            </View>
            <GlassCard isDark={isDark} style={styles.sectionCard}>
              <Text style={[styles.sectionText, { color: theme.textSecondary }]}>
                {txt.macrosDesc}
              </Text>
            </GlassCard>
          </Animated.View>

          {/* Sources Section */}
          <Animated.View entering={FadeInDown.delay(500).springify()}>
            <View style={styles.sectionHeader}>
              <ExternalLink size={18} color={premiumColors.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{txt.sourcesTitle}</Text>
            </View>
            <Text style={[styles.sourcesIntro, { color: theme.textSecondary }]}>
              {txt.sourcesDesc}
            </Text>
            <GlassCard isDark={isDark} style={styles.sourcesCard}>
              {SOURCES.map((source, index) => (
                <TouchableOpacity
                  key={source.id}
                  style={[
                    styles.sourceItem,
                    { borderBottomColor: theme.border },
                    index === SOURCES.length - 1 && { borderBottomWidth: 0 }
                  ]}
                  onPress={() => openLink(source.url)}
                  activeOpacity={0.7}
                >
                  <View style={styles.sourceContent}>
                    <Text style={[styles.sourceTitle, { color: theme.text }]}>{source.title}</Text>
                    <Text style={[styles.sourceDesc, { color: theme.textTertiary }]}>{source.description}</Text>
                    <Text style={[styles.sourceOrigin, { color: premiumColors.primary }]}>{source.source}</Text>
                  </View>
                  <ExternalLink size={18} color={theme.textTertiary} />
                </TouchableOpacity>
              ))}
            </GlassCard>
          </Animated.View>

          <View style={{ height: 40 }} />
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

  introCard: { padding: spacing.lg, marginBottom: spacing.lg },
  introHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.md },
  introIconBg: {
    width: 44,
    height: 44,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  introTitle: { fontSize: 18, fontWeight: '700', flex: 1 },
  introText: { fontSize: 14, lineHeight: 22, marginBottom: spacing.md },
  
  disclaimerBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: spacing.md,
    borderRadius: radius.lg,
    gap: spacing.sm,
  },
  disclaimerText: { fontSize: 13, lineHeight: 18, flex: 1 },

  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  sectionTitle: { fontSize: 16, fontWeight: '700' },
  sectionCard: { padding: spacing.lg, marginBottom: spacing.sm },
  sectionText: { fontSize: 14, lineHeight: 22 },

  formulaBox: {
    padding: spacing.md,
    borderRadius: radius.lg,
    marginTop: spacing.md,
  },
  formulaLabel: { fontSize: 12, fontWeight: '600', marginBottom: 4 },
  formulaText: { fontSize: 13, fontFamily: 'monospace' },

  sourcesIntro: { fontSize: 14, marginBottom: spacing.md },
  sourcesCard: { padding: 0 },
  sourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg,
    borderBottomWidth: 1,
  },
  sourceContent: { flex: 1, marginRight: spacing.md },
  sourceTitle: { fontSize: 15, fontWeight: '600', marginBottom: 4 },
  sourceDesc: { fontSize: 13, marginBottom: 4 },
  sourceOrigin: { fontSize: 12, fontWeight: '500' },
});
