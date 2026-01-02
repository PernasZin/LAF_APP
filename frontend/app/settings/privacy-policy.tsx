import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../../theme/ThemeContext';

export default function PrivacyPolicyScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Política de Privacidade</Text>
        <Text style={styles.lastUpdate}>Última atualização: Janeiro 2025</Text>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>1. Informações que Coletamos</Text>
          <Text style={styles.paragraph}>
            Coletamos informações que você nos fornece diretamente, incluindo:
          </Text>
          <View style={styles.bulletList}>
            <Text style={styles.bulletItem}>• Dados pessoais (nome, idade, sexo)</Text>
            <Text style={styles.bulletItem}>• Dados físicos (peso, altura, percentual de gordura)</Text>
            <Text style={styles.bulletItem}>• Objetivos de fitness e preferências alimentares</Text>
            <Text style={styles.bulletItem}>• Histórico de treinos e dietas</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>2. Como Usamos suas Informações</Text>
          <Text style={styles.paragraph}>
            Utilizamos as informações coletadas para:
          </Text>
          <View style={styles.bulletList}>
            <Text style={styles.bulletItem}>• Personalizar dietas e treinos com IA</Text>
            <Text style={styles.bulletItem}>• Calcular métricas como TDEE e macros</Text>
            <Text style={styles.bulletItem}>• Melhorar nossos serviços e algoritmos</Text>
            <Text style={styles.bulletItem}>• Enviar notificações sobre seu progresso</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>3. Compartilhamento de Dados</Text>
          <Text style={styles.paragraph}>
            Não vendemos, alugamos ou compartilhamos suas informações pessoais com terceiros para fins de marketing. Podemos compartilhar dados apenas:
          </Text>
          <View style={styles.bulletList}>
            <Text style={styles.bulletItem}>• Com provedores de serviço que nos ajudam a operar o app</Text>
            <Text style={styles.bulletItem}>• Para cumprir obrigações legais</Text>
            <Text style={styles.bulletItem}>• Com seu consentimento explícito</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>4. Segurança dos Dados</Text>
          <Text style={styles.paragraph}>
            Implementamos medidas de segurança técnicas e organizacionais para proteger suas informações pessoais contra acesso não autorizado, alteração, divulgação ou destruição.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>5. Seus Direitos</Text>
          <Text style={styles.paragraph}>
            Você tem direito a:
          </Text>
          <View style={styles.bulletList}>
            <Text style={styles.bulletItem}>• Acessar seus dados pessoais</Text>
            <Text style={styles.bulletItem}>• Corrigir dados incorretos</Text>
            <Text style={styles.bulletItem}>• Solicitar exclusão de seus dados</Text>
            <Text style={styles.bulletItem}>• Exportar seus dados</Text>
            <Text style={styles.bulletItem}>• Desativar personalização com IA</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>6. Retenção de Dados</Text>
          <Text style={styles.paragraph}>
            Mantemos suas informações pelo tempo necessário para fornecer nossos serviços ou conforme exigido por lei. Você pode solicitar a exclusão de sua conta a qualquer momento.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>7. Alterações nesta Política</Text>
          <Text style={styles.paragraph}>
            Podemos atualizar esta política periodicamente. Notificaremos sobre alterações significativas através do aplicativo ou por email.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>8. Contato</Text>
          <Text style={styles.paragraph}>
            Para questões sobre privacidade, entre em contato:
          </Text>
          <Text style={[styles.paragraph, styles.contactEmail]}>privacidade@lafapp.com</Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>© 2025 LAF App. Todos os direitos reservados.</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const createStyles = (colors: any) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 24,
    paddingBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 8,
  },
  lastUpdate: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 12,
  },
  paragraph: {
    fontSize: 15,
    lineHeight: 24,
    color: colors.textSecondary,
  },
  bulletList: {
    marginTop: 8,
    marginLeft: 8,
  },
  bulletItem: {
    fontSize: 15,
    lineHeight: 26,
    color: colors.textSecondary,
  },
  contactEmail: {
    color: colors.primary,
    fontWeight: '600',
    marginTop: 8,
  },
  footer: {
    marginTop: 24,
    paddingTop: 24,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 13,
    color: colors.textTertiary,
  },
});
