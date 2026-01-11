/**
 * LAF Premium Tab Layout
 * ======================
 * Tab bar glassmorphism com animações
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Tabs } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
import { Home, Utensils, Dumbbell, Activity, TrendingUp, Settings } from 'lucide-react-native';
import { useSettingsStore } from '../../stores/settingsStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing, animations } from '../../theme/premium';

// Animated Tab Icon
const TabIcon = ({ Icon, focused, color }: { Icon: any; focused: boolean; color: string }) => {
  const scale = useSharedValue(1);
  
  React.useEffect(() => {
    scale.value = withSpring(focused ? 1.15 : 1, animations.spring.bouncy);
  }, [focused]);
  
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));
  
  return (
    <Animated.View style={animatedStyle}>
      <Icon size={24} color={color} strokeWidth={focused ? 2.5 : 2} />
    </Animated.View>
  );
};

export default function TabLayout() {
  const insets = useSafeAreaInsets();
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: premiumColors.primary,
        tabBarInactiveTintColor: theme.textTertiary,
        tabBarStyle: {
          position: 'absolute',
          bottom: spacing.md,
          left: spacing.md,
          right: spacing.md,
          height: 70,
          backgroundColor: isDark ? 'rgba(15, 23, 42, 0.92)' : 'rgba(255, 255, 255, 0.92)',
          borderRadius: radius['2xl'],
          borderTopWidth: 0,
          paddingBottom: 0,
          paddingHorizontal: spacing.sm,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -4 },
          shadowOpacity: isDark ? 0.3 : 0.1,
          shadowRadius: 16,
          elevation: 20,
          borderWidth: 1,
          borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(226, 232, 240, 0.6)',
        },
        tabBarItemStyle: {
          paddingVertical: spacing.sm,
          height: 70,
        },
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: '600',
          letterSpacing: 0.2,
          marginTop: 2,
        },
        tabBarBackground: () => (
          <View style={StyleSheet.absoluteFill}>
            <LinearGradient
              colors={isDark 
                ? ['rgba(16, 185, 129, 0.03)', 'rgba(59, 130, 246, 0.03)']
                : ['rgba(16, 185, 129, 0.02)', 'rgba(59, 130, 246, 0.02)']
              }
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={[StyleSheet.absoluteFill, { borderRadius: radius['2xl'] }]}
            />
          </View>
        ),
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Início',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon Icon={Home} focused={focused} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="diet"
        options={{
          title: 'Dieta',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon Icon={Utensils} focused={focused} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="workout"
        options={{
          title: 'Treino',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon Icon={Dumbbell} focused={focused} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="cardio"
        options={{
          title: 'Cardio',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon Icon={Activity} focused={focused} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="progress"
        options={{
          title: 'Progresso',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon Icon={TrendingUp} focused={focused} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: 'Config',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon Icon={Settings} focused={focused} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
