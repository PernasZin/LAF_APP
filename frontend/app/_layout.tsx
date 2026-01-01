import React from 'react';
import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider } from '../theme/ThemeContext';
import { getColors } from '../theme/colors';

export default function RootLayout() {
  // Use default light theme colors - safe for startup
  const colors = getColors('light');
  
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: colors.background },
          }}
        />
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
