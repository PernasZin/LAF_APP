/**
 * Subscription Cancel Screen
 * ============================
 * Tela exibida quando usuário cancela o pagamento no Stripe
 */

import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { XCircle, ArrowLeft } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, spacing, radius } from '../../theme/premium';

export default function SubscriptionCancelScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const handleGoBack = () => {
    router.replace('/paywall');
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.content}>
          <View style={styles.iconContainer}>
            <XCircle size={80} color="#EF4444" />
          </View>
          
          <Text style={[styles.title, { color: theme.text }]}>
            Pagamento Cancelado
          </Text>
          
          <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
            Você cancelou o processo de pagamento. Não se preocupe, você pode tentar novamente quando quiser.
          </Text>

          <TouchableOpacity
            onPress={handleGoBack}
            style={[styles.button, { backgroundColor: '#EAB308' }]}
            activeOpacity={0.7}
          >
            <ArrowLeft size={20} color="#FFF" />
            <Text style={styles.buttonText}>Voltar e Tentar Novamente</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  iconContainer: {
    marginBottom: spacing.xl,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: spacing.xl,
    lineHeight: 24,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    borderRadius: radius.lg,
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
