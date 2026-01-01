import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider } from '../theme/ThemeContext';
import { useSettingsStore } from '../stores/settingsStore';
import { getColors } from '../theme/colors';

export default function RootLayout() {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const colors = getColors(effectiveTheme);
  
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
