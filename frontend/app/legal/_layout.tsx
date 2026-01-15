/**
 * Legal Layout - Public Pages
 * ============================
 * Terms and Privacy accessible without authentication
 */

import { Stack } from 'expo-router';
import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme } from '../../theme/premium';

export default function LegalLayout() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: theme.background },
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="terms" />
      <Stack.Screen name="privacy" />
    </Stack>
  );
}
