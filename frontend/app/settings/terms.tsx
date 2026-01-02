import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../../theme/ThemeContext';

export default function TermsScreen() {
  const { colors } = useTheme();
  const styles = createStyles(colors);

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Termos de Uso</Text>
        <Text style={styles.lastUpdate}>Última atualização: Janeiro 2025</Text>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>1. Aceitação dos Termos</Text>
          <Text style={styles.paragraph}>
            Ao acessar e usar o aplicativo LAF, você concorda em cumprir e estar vinculado a estes Termos de Uso. Se você não concordar com qualquer parte destes termos, não poderá acessar o aplicativo.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>2. Uso do Serviço</Text>
          <Text style={styles.paragraph}>
            O LAF é um aplicativo de orientação nutricional e fitness que fornece sugestões de dietas e treinos personalizados. As informações fornecidas são apenas para fins educacionais e informativos.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>3. Isenção de Responsabilidade Médica</Text>
          <Text style={styles.paragraph}>
            O conteúdo do LAF não substitui aconselhamento médico, diagnóstico ou tratamento profissional. Sempre consulte um médico ou profissional de saúde qualificado antes de iniciar qualquer programa de dieta ou exercício.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>4. Conta do Usuário</Text>
          <Text style={styles.paragraph}>
            Você é responsável por manter a confidencialidade de sua conta e por todas as atividades que ocorram sob sua conta. Você concorda em notificar-nos imediatamente sobre qualquer uso não autorizado.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>5. Propriedade Intelectual</Text>
          <Text style={styles.paragraph}>
            Todo o conteúdo, recursos e funcionalidades do aplicativo são de propriedade do LAF e estão protegidos por leis de direitos autorais, marcas registradas e outras leis de propriedade intelectual.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>6. Modificações</Text>
          <Text style={styles.paragraph}>
            Reservamo-nos o direito de modificar ou descontinuar o serviço a qualquer momento, com ou sem aviso prévio. Não seremos responsáveis perante você ou terceiros por qualquer modificação, suspensão ou descontinuação do serviço.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>7. Contato</Text>
          <Text style={styles.paragraph}>
            Para dúvidas sobre estes Termos de Uso, entre em contato conosco pelo email: suporte@lafapp.com
          </Text>
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
