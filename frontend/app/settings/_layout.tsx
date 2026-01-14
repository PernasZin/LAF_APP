/**
 * Settings Layout - Premium
 * ========================
 */

import { Stack } from 'expo-router';
import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme } from '../../theme/premium';

export default function SettingsLayout() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <Stack
      screenOptions={{
        headerShown: false, // Remove all headers - we use custom headers
        contentStyle: { backgroundColor: theme.background },
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="edit-profile" />
      <Stack.Screen name="meal-config" />
      <Stack.Screen name="training-config" />
      <Stack.Screen name="notifications" />
      <Stack.Screen name="privacy" />
      <Stack.Screen name="terms" />
    </Stack>
  );
}
