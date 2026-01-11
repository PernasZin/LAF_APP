/**
 * LAF Premium Tab Bar
 * ====================
 * Tab bar glassmorphism com animações spring
 */

import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  interpolateColor,
} from 'react-native-reanimated';
import { Home, Utensils, Dumbbell, Activity, TrendingUp, Settings } from 'lucide-react-native';
import { premiumColors, lightTheme, darkTheme, animations, radius, spacing } from './premium';

interface TabItem {
  name: string;
  label: string;
  icon: typeof Home;
}

const TABS: TabItem[] = [
  { name: 'index', label: 'Início', icon: Home },
  { name: 'diet', label: 'Dieta', icon: Utensils },
  { name: 'workout', label: 'Treino', icon: Dumbbell },
  { name: 'cardio', label: 'Cardio', icon: Activity },
  { name: 'progress', label: 'Progresso', icon: TrendingUp },
  { name: 'settings', label: 'Config', icon: Settings },
];

interface TabBarProps {
  state: any;
  descriptors: any;
  navigation: any;
  isDark?: boolean;
}

// Individual Tab Item with animations
const TabItem: React.FC<{
  tab: TabItem;
  focused: boolean;
  onPress: () => void;
  isDark: boolean;
}> = ({ tab, focused, onPress, isDark }) => {
  const theme = isDark ? darkTheme : lightTheme;
  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);
  const indicatorWidth = useSharedValue(0);
  const indicatorOpacity = useSharedValue(0);
  
  useEffect(() => {
    if (focused) {
      scale.value = withSpring(1, animations.spring.bouncy);
      translateY.value = withSpring(-2, animations.spring.gentle);
      indicatorWidth.value = withSpring(32, animations.spring.bouncy);
      indicatorOpacity.value = withTiming(1, { duration: 200 });
    } else {
      scale.value = withSpring(0.95, animations.spring.gentle);
      translateY.value = withSpring(0, animations.spring.gentle);
      indicatorWidth.value = withTiming(0, { duration: 200 });
      indicatorOpacity.value = withTiming(0, { duration: 150 });
    }
  }, [focused]);
  
  const iconAnimatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { translateY: translateY.value },
    ],
  }));
  
  const indicatorAnimatedStyle = useAnimatedStyle(() => ({
    width: indicatorWidth.value,
    opacity: indicatorOpacity.value,
  }));
  
  const IconComponent = tab.icon;
  
  return (
    <TouchableOpacity
      onPress={onPress}
      style={styles.tabItem}
      activeOpacity={0.7}
    >
      <Animated.View style={[styles.iconContainer, iconAnimatedStyle]}>
        <IconComponent
          size={24}
          color={focused ? premiumColors.primary : theme.tabBar.inactiveColor}
          strokeWidth={focused ? 2.5 : 2}
        />
      </Animated.View>
      
      <Text style={[
        styles.tabLabel,
        { color: focused ? premiumColors.primary : theme.tabBar.inactiveColor },
        focused && styles.tabLabelActive,
      ]}>
        {tab.label}
      </Text>
      
      {/* Animated indicator dot/line */}
      <Animated.View style={[styles.indicator, indicatorAnimatedStyle]}>
        <LinearGradient
          colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.indicatorGradient}
        />
      </Animated.View>
    </TouchableOpacity>
  );
};

export const PremiumTabBar: React.FC<TabBarProps> = ({
  state,
  descriptors,
  navigation,
  isDark = false,
}) => {
  const insets = useSafeAreaInsets();
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <View style={[
      styles.container,
      { 
        paddingBottom: insets.bottom > 0 ? insets.bottom : spacing.sm,
        backgroundColor: 'transparent',
      }
    ]}>
      {/* Glass background effect */}
      <View style={[
        styles.glassContainer,
        {
          backgroundColor: isDark 
            ? 'rgba(15, 23, 42, 0.85)' 
            : 'rgba(255, 255, 255, 0.85)',
          borderTopColor: isDark 
            ? 'rgba(71, 85, 105, 0.3)' 
            : 'rgba(226, 232, 240, 0.8)',
        }
      ]}>
        {/* Subtle gradient overlay */}
        <LinearGradient
          colors={isDark 
            ? ['rgba(16, 185, 129, 0.03)', 'rgba(59, 130, 246, 0.03)']
            : ['rgba(16, 185, 129, 0.02)', 'rgba(59, 130, 246, 0.02)']
          }
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={StyleSheet.absoluteFill}
        />
        
        <View style={styles.tabsContainer}>
          {state.routes.map((route: any, index: number) => {
            const tab = TABS.find(t => t.name === route.name);
            if (!tab) return null;
            
            const focused = state.index === index;
            
            const onPress = () => {
              const event = navigation.emit({
                type: 'tabPress',
                target: route.key,
                canPreventDefault: true,
              });
              
              if (!focused && !event.defaultPrevented) {
                navigation.navigate(route.name);
              }
            };
            
            return (
              <TabItem
                key={route.key}
                tab={tab}
                focused={focused}
                onPress={onPress}
                isDark={isDark}
              />
            );
          })}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  glassContainer: {
    marginHorizontal: spacing.md,
    marginBottom: spacing.sm,
    borderRadius: radius['2xl'],
    borderTopWidth: 1,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 12,
  },
  tabsContainer: {
    flexDirection: 'row',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.xs,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.sm,
    gap: 4,
  },
  iconContainer: {
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: '600',
    letterSpacing: 0.2,
  },
  tabLabelActive: {
    fontWeight: '700',
  },
  indicator: {
    height: 3,
    borderRadius: 2,
    marginTop: 4,
    overflow: 'hidden',
  },
  indicatorGradient: {
    flex: 1,
    borderRadius: 2,
  },
});

export default PremiumTabBar;
