import { Stack } from 'expo-router';
import { useTheme } from '../../theme/ThemeContext';

export default function SettingsLayout() {
  const { colors } = useTheme();
  
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.background },
        headerTintColor: colors.text,
        headerTitleStyle: { fontWeight: '600' },
        headerShadowVisible: false,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen 
        name="edit-profile" 
        options={{ 
          title: 'Editar Perfil',
          presentation: 'modal',
        }} 
      />
      <Stack.Screen 
        name="terms" 
        options={{ 
          title: 'Termos de Uso',
          presentation: 'modal',
        }} 
      />
      <Stack.Screen 
        name="privacy-policy" 
        options={{ 
          title: 'Política de Privacidade',
          presentation: 'modal',
        }} 
      />
    </Stack>
  );
}
