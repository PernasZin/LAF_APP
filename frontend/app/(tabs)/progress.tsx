import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme/ThemeContext';

export default function ProgressScreen() {
  const { colors } = useTheme();

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.content}>
        <Ionicons name="analytics-outline" size={80} color={colors.textTertiary} />
        <Text style={[styles.title, { color: colors.text }]}>Acompanhamento</Text>
        <Text style={[styles.subtitle, { color: colors.primary }]}>Em breve</Text>
        <Text style={[styles.description, { color: colors.textSecondary }]}>
          Gráficos de progresso e evolução serão implementados em breve
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginTop: 16,
  },
  subtitle: {
    fontSize: 16,
    marginTop: 8,
    fontWeight: '600',
  },
  description: {
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
});
