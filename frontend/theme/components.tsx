/**
 * LAF Premium UI Components
 * =========================
 * Componentes glassmorphism com animações
 */

import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ViewStyle, TextStyle, Pressable } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  interpolate,
  Extrapolation,
} from 'react-native-reanimated';
import { 
  Home, Utensils, Dumbbell, Activity, TrendingUp, Settings,
  Droplets, Flame, Target, Trophy, ChevronRight, Plus, Minus,
  Check, X, AlertCircle, Info, Zap, Heart, Star
} from 'lucide-react-native';
import { premiumColors, lightTheme, darkTheme, radius, spacing, typography, animations } from './premium';

// ==================== ANIMATED PRESSABLE ====================
interface AnimatedPressableProps {
  children: React.ReactNode;
  onPress?: () => void;
  style?: ViewStyle;
  disabled?: boolean;
  scale?: number;
}

export const AnimatedPressable: React.FC<AnimatedPressableProps> = ({
  children, onPress, style, disabled, scale = 0.97
}) => {
  const pressed = useSharedValue(0);
  
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: interpolate(pressed.value, [0, 1], [1, scale], Extrapolation.CLAMP) }],
    opacity: interpolate(pressed.value, [0, 1], [1, 0.9], Extrapolation.CLAMP),
  }));
  
  return (
    <Pressable
      onPressIn={() => { pressed.value = withSpring(1, animations.spring.snappy); }}
      onPressOut={() => { pressed.value = withSpring(0, animations.spring.gentle); }}
      onPress={onPress}
      disabled={disabled}
    >
      <Animated.View style={[style, animatedStyle]}>
        {children}
      </Animated.View>
    </Pressable>
  );
};

// ==================== GLASS CARD ====================
interface GlassCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  isDark?: boolean;
  intensity?: 'light' | 'medium' | 'strong';
  onPress?: () => void;
  gradient?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children, style, isDark = false, intensity = 'medium', onPress, gradient = false
}) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  const getOpacity = () => {
    switch (intensity) {
      case 'light': return isDark ? 0.5 : 0.6;
      case 'strong': return isDark ? 0.85 : 0.9;
      default: return isDark ? 0.7 : 0.75;
    }
  };
  
  const cardStyle: ViewStyle = {
    backgroundColor: isDark 
      ? `rgba(30, 41, 59, ${getOpacity()})` 
      : `rgba(255, 255, 255, ${getOpacity()})`,
    borderWidth: 1,
    borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
    borderRadius: radius.xl,
    overflow: 'hidden',
    ...theme.shadow,
  };
  
  const content = (
    <View style={[cardStyle, style]}>
      {gradient && (
        <LinearGradient
          colors={['rgba(16, 185, 129, 0.05)', 'rgba(59, 130, 246, 0.05)']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={StyleSheet.absoluteFill}
        />
      )}
      {children}
    </View>
  );
  
  if (onPress) {
    return <AnimatedPressable onPress={onPress}>{content}</AnimatedPressable>;
  }
  
  return content;
};

// ==================== GRADIENT BUTTON ====================
interface GradientButtonProps {
  title: string;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'outline';
  style?: ViewStyle;
}

export const GradientButton: React.FC<GradientButtonProps> = ({
  title, onPress, disabled, loading, icon, size = 'md', variant = 'primary', style
}) => {
  const getHeight = () => {
    switch (size) {
      case 'sm': return 40;
      case 'lg': return 60;
      default: return 52;
    }
  };
  
  const getFontSize = () => {
    switch (size) {
      case 'sm': return 14;
      case 'lg': return 18;
      default: return 16;
    }
  };
  
  if (variant === 'outline') {
    return (
      <AnimatedPressable onPress={onPress} disabled={disabled}>
        <View style={[styles.outlineButton, { height: getHeight() }, style]}>
          <LinearGradient
            colors={[premiumColors.gradient.start, premiumColors.gradient.end]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[StyleSheet.absoluteFill, { opacity: 0.1 }]}
          />
          <View style={styles.buttonContent}>
            {icon}
            <Text style={[styles.outlineButtonText, { fontSize: getFontSize() }]}>{title}</Text>
          </View>
        </View>
      </AnimatedPressable>
    );
  }
  
  return (
    <AnimatedPressable onPress={onPress} disabled={disabled || loading}>
      <LinearGradient
        colors={disabled 
          ? ['#9CA3AF', '#6B7280'] 
          : [premiumColors.gradient.start, premiumColors.gradient.middle, premiumColors.gradient.end]
        }
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={[styles.gradientButton, { height: getHeight() }, style]}
      >
        <View style={styles.buttonContent}>
          {loading ? (
            <Animated.View style={styles.loadingDot} />
          ) : (
            <>
              {icon}
              <Text style={[styles.buttonText, { fontSize: getFontSize() }]}>{title}</Text>
            </>
          )}
        </View>
      </LinearGradient>
    </AnimatedPressable>
  );
};

// ==================== STAT CARD ====================
interface StatCardProps {
  icon: React.ReactNode;
  value: string | number;
  unit?: string;
  label: string;
  color?: string;
  isDark?: boolean;
  onPress?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  icon, value, unit, label, color = premiumColors.primary, isDark = false, onPress
}) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <GlassCard isDark={isDark} onPress={onPress} style={styles.statCard}>
      <View style={[styles.statIconContainer, { backgroundColor: `${color}15` }]}>
        {icon}
      </View>
      <View style={styles.statContent}>
        <View style={styles.statValueRow}>
          <Text style={[styles.statValue, { color: theme.text }]}>{value}</Text>
          {unit && <Text style={[styles.statUnit, { color: theme.textSecondary }]}>{unit}</Text>}
        </View>
        <Text style={[styles.statLabel, { color: theme.textTertiary }]}>{label}</Text>
      </View>
    </GlassCard>
  );
};

// ==================== PROGRESS RING ====================
interface ProgressRingProps {
  progress: number; // 0-100
  size?: number;
  strokeWidth?: number;
  color?: string;
  backgroundColor?: string;
  children?: React.ReactNode;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  progress, size = 120, strokeWidth = 10, color, backgroundColor, children
}) => {
  const animatedProgress = useSharedValue(0);
  const radius_val = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius_val;
  
  useEffect(() => {
    animatedProgress.value = withTiming(progress, { duration: 800 });
  }, [progress]);
  
  const animatedStyle = useAnimatedStyle(() => ({
    strokeDashoffset: circumference - (circumference * animatedProgress.value) / 100,
  }));
  
  return (
    <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
      <Animated.View style={StyleSheet.absoluteFill}>
        {/* Background ring */}
        <View style={[styles.ringBackground, { 
          width: size, 
          height: size, 
          borderRadius: size / 2,
          borderWidth: strokeWidth,
          borderColor: backgroundColor || 'rgba(226, 232, 240, 0.5)',
        }]} />
      </Animated.View>
      <View style={{ position: 'absolute' }}>
        {children}
      </View>
    </View>
  );
};

// ==================== MACRO BAR ====================
interface MacroBarProps {
  label: string;
  current: number;
  target: number;
  color: string;
  isDark?: boolean;
}

export const MacroBar: React.FC<MacroBarProps> = ({
  label, current, target, color, isDark = false
}) => {
  const theme = isDark ? darkTheme : lightTheme;
  const progress = Math.min((current / target) * 100, 100);
  const animatedWidth = useSharedValue(0);
  
  useEffect(() => {
    animatedWidth.value = withSpring(progress, animations.spring.gentle);
  }, [progress]);
  
  const animatedStyle = useAnimatedStyle(() => ({
    width: `${animatedWidth.value}%`,
  }));
  
  return (
    <View style={styles.macroBarContainer}>
      <View style={styles.macroBarHeader}>
        <View style={styles.macroBarLabelRow}>
          <View style={[styles.macroDot, { backgroundColor: color }]} />
          <Text style={[styles.macroBarLabel, { color: theme.text }]}>{label}</Text>
        </View>
        <Text style={[styles.macroBarValue, { color: theme.text }]}>
          {Math.round(current)}
          <Text style={{ color: theme.textTertiary }}> / {Math.round(target)}g</Text>
        </Text>
      </View>
      <View style={[styles.macroBarTrack, { backgroundColor: theme.border }]}>
        <Animated.View style={[styles.macroBarFill, { backgroundColor: color }, animatedStyle]} />
      </View>
    </View>
  );
};

// ==================== TAB BAR ICON ====================
interface TabIconProps {
  name: 'home' | 'diet' | 'workout' | 'cardio' | 'progress' | 'settings';
  focused: boolean;
  color: string;
  size?: number;
}

export const TabIcon: React.FC<TabIconProps> = ({ name, focused, color, size = 24 }) => {
  const scale = useSharedValue(focused ? 1 : 0.9);
  
  useEffect(() => {
    scale.value = withSpring(focused ? 1.1 : 1, animations.spring.bouncy);
  }, [focused]);
  
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));
  
  const icons = {
    home: Home,
    diet: Utensils,
    workout: Dumbbell,
    cardio: Activity,
    progress: TrendingUp,
    settings: Settings,
  };
  
  const IconComponent = icons[name];
  
  return (
    <Animated.View style={animatedStyle}>
      <IconComponent 
        size={size} 
        color={color} 
        strokeWidth={focused ? 2.5 : 2}
      />
    </Animated.View>
  );
};

// ==================== QUICK ACTION BUTTON ====================
interface QuickActionProps {
  icon: React.ReactNode;
  label: string;
  color?: string;
  isDark?: boolean;
  onPress?: () => void;
}

export const QuickAction: React.FC<QuickActionProps> = ({
  icon, label, color = premiumColors.primary, isDark = false, onPress
}) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <AnimatedPressable onPress={onPress} style={styles.quickAction}>
      <View style={[styles.quickActionIcon, { backgroundColor: `${color}15` }]}>
        {icon}
      </View>
      <Text style={[styles.quickActionLabel, { color: theme.textSecondary }]}>{label}</Text>
    </AnimatedPressable>
  );
};

// ==================== SECTION HEADER ====================
interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: { label: string; onPress: () => void };
  isDark?: boolean;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title, subtitle, action, isDark = false
}) => {
  const theme = isDark ? darkTheme : lightTheme;
  
  return (
    <View style={styles.sectionHeader}>
      <View>
        <Text style={[styles.sectionTitle, { color: theme.text }]}>{title}</Text>
        {subtitle && (
          <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>{subtitle}</Text>
        )}
      </View>
      {action && (
        <TouchableOpacity onPress={action.onPress} style={styles.sectionAction}>
          <Text style={[styles.sectionActionText, { color: premiumColors.primary }]}>{action.label}</Text>
          <ChevronRight size={16} color={premiumColors.primary} />
        </TouchableOpacity>
      )}
    </View>
  );
};

// ==================== STYLES ====================
const styles = StyleSheet.create({
  // Gradient Button
  gradientButton: {
    borderRadius: radius.lg,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: premiumColors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  outlineButton: {
    borderRadius: radius.lg,
    borderWidth: 2,
    borderColor: premiumColors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  outlineButtonText: {
    color: premiumColors.primary,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  loadingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FFFFFF',
  },
  
  // Stat Card
  statCard: {
    flex: 1,
    padding: spacing.base,
    gap: spacing.md,
  },
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statContent: {
    gap: 4,
  },
  statValueRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 4,
  },
  statValue: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -1,
  },
  statUnit: {
    fontSize: 14,
    fontWeight: '500',
  },
  statLabel: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  
  // Progress Ring
  ringBackground: {
    position: 'absolute',
  },
  
  // Macro Bar
  macroBarContainer: {
    gap: 8,
  },
  macroBarHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  macroBarLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  macroDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  macroBarLabel: {
    fontSize: 15,
    fontWeight: '600',
  },
  macroBarValue: {
    fontSize: 15,
    fontWeight: '700',
  },
  macroBarTrack: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  macroBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  
  // Quick Action
  quickAction: {
    alignItems: 'center',
    gap: 8,
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  quickActionLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  
  // Section Header
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: -0.5,
  },
  sectionSubtitle: {
    fontSize: 13,
    marginTop: 2,
  },
  sectionAction: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
  },
  sectionActionText: {
    fontSize: 14,
    fontWeight: '600',
  },
});

// Export Lucide icons for convenience
export {
  Home, Utensils, Dumbbell, Activity, TrendingUp, Settings,
  Droplets, Flame, Target, Trophy, ChevronRight, Plus, Minus,
  Check, X, AlertCircle, Info, Zap, Heart, Star
};
