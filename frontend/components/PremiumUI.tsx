/**
 * Premium UI Components
 * =====================
 * Componentes reutilizáveis com animações e efeitos premium
 */

import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Pressable } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withRepeat,
  withSequence,
  interpolate,
  Extrapolate,
  FadeIn,
  FadeInDown,
  FadeInUp,
  ZoomIn,
  SlideInRight,
} from 'react-native-reanimated';
import { premiumColors, radius, spacing } from '../theme/premium';

// ==================== ANIMATED BUTTON ====================
interface AnimatedButtonProps {
  onPress: () => void;
  children: React.ReactNode;
  style?: any;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  disabled?: boolean;
}

export const AnimatedButton = ({ 
  onPress, 
  children, 
  style, 
  variant = 'primary',
  disabled = false 
}: AnimatedButtonProps) => {
  const scale = useSharedValue(1);
  
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    scale.value = withSpring(0.95, { damping: 15, stiffness: 400 });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 15, stiffness: 400 });
  };

  const gradients: Record<string, [string, string]> = {
    primary: [premiumColors.gradient.start, premiumColors.gradient.end],
    secondary: ['#6B7280', '#4B5563'],
    success: ['#10B981', '#059669'],
    danger: ['#EF4444', '#DC2626'],
  };

  return (
    <Animated.View style={[animatedStyle, style]}>
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled}
        style={{ opacity: disabled ? 0.5 : 1 }}
      >
        <LinearGradient
          colors={gradients[variant]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.buttonGradient}
        >
          {children}
        </LinearGradient>
      </Pressable>
    </Animated.View>
  );
};

// ==================== PULSE INDICATOR ====================
interface PulseIndicatorProps {
  color?: string;
  size?: number;
  active?: boolean;
}

export const PulseIndicator = ({ 
  color = premiumColors.primary, 
  size = 12,
  active = true 
}: PulseIndicatorProps) => {
  const pulseScale = useSharedValue(1);
  const pulseOpacity = useSharedValue(0.5);

  useEffect(() => {
    if (active) {
      pulseScale.value = withRepeat(
        withSequence(
          withTiming(1.5, { duration: 1000 }),
          withTiming(1, { duration: 1000 })
        ),
        -1,
        false
      );
      pulseOpacity.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 1000 }),
          withTiming(0.5, { duration: 1000 })
        ),
        -1,
        false
      );
    }
  }, [active]);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulseScale.value }],
    opacity: pulseOpacity.value,
  }));

  if (!active) return null;

  return (
    <View style={[styles.pulseContainer, { width: size * 2, height: size * 2 }]}>
      <Animated.View
        style={[
          styles.pulseRing,
          pulseStyle,
          { 
            width: size * 2, 
            height: size * 2, 
            borderRadius: size,
            backgroundColor: color,
          }
        ]}
      />
      <View
        style={[
          styles.pulseDot,
          { 
            width: size, 
            height: size, 
            borderRadius: size / 2,
            backgroundColor: color,
          }
        ]}
      />
    </View>
  );
};

// ==================== SHIMMER EFFECT ====================
interface ShimmerProps {
  width: number;
  height: number;
  borderRadius?: number;
}

export const Shimmer = ({ width, height, borderRadius = 8 }: ShimmerProps) => {
  const shimmerPosition = useSharedValue(-1);

  useEffect(() => {
    shimmerPosition.value = withRepeat(
      withTiming(1, { duration: 1500 }),
      -1,
      false
    );
  }, []);

  const shimmerStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: interpolate(shimmerPosition.value, [-1, 1], [-width, width]) }],
  }));

  return (
    <View style={[styles.shimmerContainer, { width, height, borderRadius }]}>
      <Animated.View style={[styles.shimmerEffect, shimmerStyle, { height }]} />
    </View>
  );
};

// ==================== PROGRESS RING ====================
interface ProgressRingProps {
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  backgroundColor?: string;
  children?: React.ReactNode;
}

export const ProgressRing = ({ 
  progress, 
  size = 80, 
  strokeWidth = 8,
  color = premiumColors.primary,
  backgroundColor = 'rgba(107, 114, 128, 0.2)',
  children 
}: ProgressRingProps) => {
  const animatedProgress = useSharedValue(0);
  
  useEffect(() => {
    animatedProgress.value = withSpring(Math.min(progress, 100), {
      damping: 15,
      stiffness: 100,
    });
  }, [progress]);

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  const animatedStyle = useAnimatedStyle(() => {
    const strokeDashoffset = circumference - (animatedProgress.value / 100) * circumference;
    return {
      strokeDashoffset,
    };
  });

  return (
    <View style={[styles.progressRingContainer, { width: size, height: size }]}>
      <Animated.View style={StyleSheet.absoluteFill}>
        {/* Background circle */}
        <View
          style={[
            styles.progressRingBg,
            {
              width: size,
              height: size,
              borderRadius: size / 2,
              borderWidth: strokeWidth,
              borderColor: backgroundColor,
            },
          ]}
        />
      </Animated.View>
      {children && (
        <View style={styles.progressRingContent}>
          {children}
        </View>
      )}
    </View>
  );
};

// ==================== ANIMATED COUNTER ====================
interface AnimatedCounterProps {
  value: number;
  suffix?: string;
  prefix?: string;
  style?: any;
  duration?: number;
}

export const AnimatedCounter = ({ 
  value, 
  suffix = '', 
  prefix = '',
  style,
  duration = 1000 
}: AnimatedCounterProps) => {
  const animatedValue = useSharedValue(0);
  const [displayValue, setDisplayValue] = React.useState(0);

  useEffect(() => {
    animatedValue.value = withTiming(value, { duration });
  }, [value]);

  useEffect(() => {
    const interval = setInterval(() => {
      const currentValue = Math.round(animatedValue.value);
      setDisplayValue(currentValue);
      if (currentValue === value) {
        clearInterval(interval);
      }
    }, 16);
    return () => clearInterval(interval);
  }, [value]);

  return (
    <Text style={style}>
      {prefix}{displayValue}{suffix}
    </Text>
  );
};

// ==================== FLOATING ACTION BUTTON ====================
interface FABProps {
  onPress: () => void;
  icon: React.ReactNode;
  color?: string;
}

export const FloatingActionButton = ({ onPress, icon, color = premiumColors.primary }: FABProps) => {
  const scale = useSharedValue(1);
  const rotate = useSharedValue(0);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { rotate: `${rotate.value}deg` },
    ],
  }));

  const handlePress = () => {
    scale.value = withSequence(
      withSpring(0.9, { damping: 10 }),
      withSpring(1, { damping: 10 })
    );
    rotate.value = withSequence(
      withTiming(15, { duration: 100 }),
      withTiming(-15, { duration: 100 }),
      withTiming(0, { duration: 100 })
    );
    onPress();
  };

  return (
    <Animated.View style={[styles.fab, animatedStyle]}>
      <TouchableOpacity onPress={handlePress} activeOpacity={0.8}>
        <LinearGradient
          colors={[color, color + 'DD']}
          style={styles.fabGradient}
        >
          {icon}
        </LinearGradient>
      </TouchableOpacity>
    </Animated.View>
  );
};

// ==================== SUCCESS CHECKMARK ====================
export const SuccessCheckmark = ({ size = 60, color = '#10B981' }: { size?: number; color?: string }) => {
  return (
    <Animated.View 
      entering={ZoomIn.springify().damping(12)}
      style={[styles.successContainer, { width: size, height: size }]}
    >
      <LinearGradient
        colors={[color, color + 'CC']}
        style={[styles.successGradient, { width: size, height: size, borderRadius: size / 2 }]}
      >
        <Text style={{ fontSize: size * 0.5, color: '#FFF' }}>✓</Text>
      </LinearGradient>
    </Animated.View>
  );
};

// ==================== BADGE ====================
interface BadgeProps {
  text: string;
  color?: string;
  textColor?: string;
  size?: 'small' | 'medium' | 'large';
  animated?: boolean;
}

export const Badge = ({ 
  text, 
  color = premiumColors.primary + '20', 
  textColor = premiumColors.primary,
  size = 'medium',
  animated = false
}: BadgeProps) => {
  const sizeStyles = {
    small: { paddingHorizontal: 8, paddingVertical: 4, fontSize: 10 },
    medium: { paddingHorizontal: 12, paddingVertical: 6, fontSize: 12 },
    large: { paddingHorizontal: 16, paddingVertical: 8, fontSize: 14 },
  };

  const content = (
    <View style={[styles.badge, { backgroundColor: color, ...sizeStyles[size] }]}>
      <Text style={[styles.badgeText, { color: textColor, fontSize: sizeStyles[size].fontSize }]}>
        {text}
      </Text>
    </View>
  );

  if (animated) {
    return (
      <Animated.View entering={FadeIn.delay(200)}>
        {content}
      </Animated.View>
    );
  }

  return content;
};

// ==================== STYLES ====================
const styles = StyleSheet.create({
  buttonGradient: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 8,
  },
  pulseContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  pulseRing: {
    position: 'absolute',
  },
  pulseDot: {
    position: 'absolute',
  },
  shimmerContainer: {
    backgroundColor: 'rgba(107, 114, 128, 0.2)',
    overflow: 'hidden',
  },
  shimmerEffect: {
    width: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  progressRingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressRingBg: {
    position: 'absolute',
  },
  progressRingContent: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  fab: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  fabGradient: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  successContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  successGradient: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  badge: {
    borderRadius: radius.full,
    alignSelf: 'flex-start',
  },
  badgeText: {
    fontWeight: '600',
  },
});

export default {
  AnimatedButton,
  PulseIndicator,
  Shimmer,
  ProgressRing,
  AnimatedCounter,
  FloatingActionButton,
  SuccessCheckmark,
  Badge,
};
