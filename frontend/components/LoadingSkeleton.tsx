import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, ViewStyle } from 'react-native';
import { useSettingsStore } from '../stores/settingsStore';
import { lightTheme, darkTheme } from '../theme/premium';

// Hook para obter cores do tema
const useThemeColors = () => {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  return {
    colors: {
      border: theme.border,
      backgroundCard: theme.backgroundCard,
    }
  };
};

interface SkeletonProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = 20,
  borderRadius = 8,
  style,
}) => {
  const { colors } = useThemeColors();
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 0.7,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );
    animation.start();
    return () => animation.stop();
  }, []);

  return (
    <Animated.View
      style={[
        {
          width,
          height,
          borderRadius,
          backgroundColor: colors.border,
          opacity,
        },
        style,
      ]}
    />
  );
};

// Card skeleton para listas
export const CardSkeleton: React.FC<{ style?: ViewStyle }> = ({ style }) => {
  const { colors } = useThemeColors();
  
  return (
    <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }, style]}>
      <View style={styles.cardHeader}>
        <Skeleton width={120} height={18} />
        <Skeleton width={60} height={14} />
      </View>
      <View style={styles.cardBody}>
        <Skeleton width="80%" height={14} style={{ marginBottom: 8 }} />
        <Skeleton width="60%" height={14} />
      </View>
    </View>
  );
};

// Skeleton para tela de dieta
export const DietSkeleton: React.FC = () => {
  const { colors } = useThemeColors();
  
  return (
    <View style={styles.container}>
      {/* Header skeleton */}
      <View style={[styles.headerSkeleton, { backgroundColor: colors.backgroundCard }]}>
        <Skeleton width={180} height={24} style={{ marginBottom: 12 }} />
        <View style={styles.macrosRow}>
          <Skeleton width={70} height={40} borderRadius={12} />
          <Skeleton width={70} height={40} borderRadius={12} />
          <Skeleton width={70} height={40} borderRadius={12} />
        </View>
      </View>
      
      {/* Meal cards skeleton */}
      {[1, 2, 3].map((i) => (
        <CardSkeleton key={i} style={{ marginBottom: 12 }} />
      ))}
    </View>
  );
};

// Skeleton para tela de treino
export const WorkoutSkeleton: React.FC = () => {
  const { colors } = useThemeColors();
  
  return (
    <View style={styles.container}>
      {/* Tabs skeleton */}
      <View style={styles.tabsRow}>
        <Skeleton width={80} height={36} borderRadius={18} />
        <Skeleton width={80} height={36} borderRadius={18} />
        <Skeleton width={80} height={36} borderRadius={18} />
      </View>
      
      {/* Exercise cards skeleton */}
      {[1, 2, 3, 4].map((i) => (
        <CardSkeleton key={i} style={{ marginBottom: 12 }} />
      ))}
    </View>
  );
};

// Skeleton para tela de progresso
export const ProgressSkeleton: React.FC = () => {
  const { colors } = useThemeColors();
  
  return (
    <View style={styles.container}>
      {/* Stats card skeleton */}
      <View style={[styles.statsCard, { backgroundColor: colors.backgroundCard }]}>
        <Skeleton width={100} height={16} style={{ marginBottom: 8 }} />
        <Skeleton width={80} height={32} />
      </View>
      
      {/* Chart skeleton */}
      <View style={[styles.chartSkeleton, { backgroundColor: colors.backgroundCard }]}>
        <Skeleton width="100%" height={180} borderRadius={12} />
      </View>
      
      {/* History skeleton */}
      <Skeleton width={120} height={18} style={{ marginBottom: 12, marginTop: 16 }} />
      {[1, 2, 3].map((i) => (
        <View key={i} style={[styles.historyItem, { backgroundColor: colors.backgroundCard }]}>
          <Skeleton width={60} height={14} />
          <Skeleton width={50} height={18} />
        </View>
      ))}
    </View>
  );
};

// Skeleton para tela Home
export const HomeSkeleton: React.FC = () => {
  const { colors } = useThemeColors();
  
  return (
    <View style={styles.container}>
      {/* Header skeleton */}
      <View style={styles.homeHeader}>
        <View>
          <Skeleton width={180} height={28} style={{ marginBottom: 8 }} />
          <Skeleton width={220} height={16} />
        </View>
        <Skeleton width={40} height={40} borderRadius={20} />
      </View>
      
      {/* Stats cards skeleton */}
      <View style={styles.homeStatsRow}>
        <View style={[styles.homeStatsCard, { backgroundColor: colors.backgroundCard }]}>
          <Skeleton width={28} height={28} borderRadius={14} style={{ marginBottom: 8 }} />
          <Skeleton width={60} height={24} style={{ marginBottom: 4 }} />
          <Skeleton width={40} height={14} />
        </View>
        <View style={[styles.homeStatsCard, { backgroundColor: colors.backgroundCard }]}>
          <Skeleton width={28} height={28} borderRadius={14} style={{ marginBottom: 8 }} />
          <Skeleton width={40} height={24} style={{ marginBottom: 4 }} />
          <Skeleton width={50} height={14} />
        </View>
      </View>
      
      {/* Macros card skeleton */}
      <View style={[styles.homeCard, { backgroundColor: colors.backgroundCard }]}>
        <Skeleton width={160} height={18} style={{ marginBottom: 16 }} />
        {[1, 2, 3].map((i) => (
          <View key={i} style={styles.homeMacroRow}>
            <Skeleton width={4} height={40} borderRadius={2} />
            <Skeleton width={100} height={16} />
            <Skeleton width={50} height={18} />
          </View>
        ))}
      </View>
      
      {/* Goal card skeleton */}
      <View style={[styles.homeCard, { backgroundColor: colors.backgroundCard }]}>
        <Skeleton width={120} height={18} style={{ marginBottom: 16 }} />
        <View style={styles.homeGoalRow}>
          <Skeleton width={56} height={56} borderRadius={28} />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Skeleton width={180} height={16} style={{ marginBottom: 8 }} />
            <Skeleton width={140} height={14} />
          </View>
        </View>
      </View>
    </View>
  );
};

// Skeleton para tela de Cardio
export const CardioSkeleton: React.FC = () => {
  const { colors } = useThemeColors();
  
  return (
    <View style={styles.container}>
      {/* Header skeleton */}
      <View style={[styles.statsCard, { backgroundColor: colors.backgroundCard }]}>
        <Skeleton width={150} height={20} style={{ marginBottom: 12 }} />
        <Skeleton width={100} height={32} />
      </View>
      
      {/* Session cards skeleton */}
      {[1, 2, 3].map((i) => (
        <CardSkeleton key={i} style={{ marginBottom: 12 }} />
      ))}
    </View>
  );
};


const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  card: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardBody: {},
  headerSkeleton: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  macrosRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  tabsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 20,
  },
  statsCard: {
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    marginBottom: 16,
  },
  chartSkeleton: {
    padding: 16,
    borderRadius: 16,
  },
  historyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  // Home skeleton styles
  homeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  homeStatsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  homeStatsCard: {
    flex: 1,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  homeCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  homeMacroRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  homeGoalRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});

export default Skeleton;
