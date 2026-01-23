/**
 * Subscription Success Screen
 * ============================
 * Tela exibida após pagamento bem-sucedido no Stripe
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router, useLocalSearchParams } from 'expo-router';
import { CheckCircle } from 'lucide-react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { useSettingsStore } from '../../stores/settingsStore';
import { useSubscriptionStore } from '../../stores/subscriptionStore';
import { lightTheme, darkTheme, spacing } from '../../theme/premium';

export default function SubscriptionSuccessScreen() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  const { setHasSeenPaywall, setPremiumStatus } = useSubscriptionStore();
  const { session_id } = useLocalSearchParams();
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    const processSuccess = async () => {
      try {
        console.log('🟢 Payment successful! Session ID:', session_id);
        
        // Marcar paywall como visto
        setHasSeenPaywall(true);
        
        // Atualizar status premium
        setPremiumStatus(true);
        
        // Aguardar um pouco para mostrar a mensagem de sucesso
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        setStatus('success');
        
        // Redirecionar para o app principal após 2 segundos
        setTimeout(() => {
          router.replace('/(tabs)');
        }, 2000);
        
      } catch (error) {
        console.error('Error processing success:', error);
        setStatus('error');
        // Redirecionar mesmo em caso de erro
        setTimeout(() => {
          router.replace('/(tabs)');
        }, 3000);
      }
    };

    processSuccess();
  }, [session_id]);

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.content}>
          {status === 'loading' ? (
            <>
              <ActivityIndicator size="large" color="#10B981" />
              <Text style={[styles.title, { color: theme.text }]}>
                Processando pagamento...
              </Text>
            </>
          ) : (
            <>
              <View style={styles.iconContainer}>
                <CheckCircle size={80} color="#10B981" />
              </View>
              <Text style={[styles.title, { color: theme.text }]}>
                Pagamento Confirmado!
              </Text>
              <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
                Sua assinatura foi ativada com sucesso.
              </Text>
              <Text style={[styles.redirect, { color: theme.textTertiary }]}>
                Redirecionando para o app...
              </Text>
            </>
          )}
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
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  redirect: {
    fontSize: 14,
    textAlign: 'center',
    marginTop: spacing.xl,
  },
});
