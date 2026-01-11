/**
 * LAF Premium Design System
 * ===========================
 * Glassmorphism + Gradientes Verde→Azul
 * Inspirado em Apple, Linear, Stripe
 */

// ==================== CORES PREMIUM ====================
export const premiumColors = {
  // Gradiente Principal (Verde → Azul)
  gradient: {
    start: '#10B981',    // Verde Esmeralda
    middle: '#14B8A6',   // Teal
    end: '#3B82F6',      // Azul Elétrico
  },
  
  // Cores Sólidas
  primary: '#10B981',
  secondary: '#3B82F6',
  accent: '#8B5CF6',     // Roxo para destaques especiais
  
  // Glassmorphism
  glass: {
    light: 'rgba(255, 255, 255, 0.7)',
    medium: 'rgba(255, 255, 255, 0.5)',
    strong: 'rgba(255, 255, 255, 0.85)',
    dark: 'rgba(15, 23, 42, 0.8)',
    darkMedium: 'rgba(15, 23, 42, 0.6)',
  },
  
  // Blur intensities
  blur: {
    light: 10,
    medium: 20,
    strong: 40,
  },
};

// ==================== LIGHT THEME ====================
export const lightTheme = {
  // Background com gradiente sutil
  background: '#F8FAFC',
  backgroundGradient: ['#F8FAFC', '#EEF2FF'],
  backgroundCard: 'rgba(255, 255, 255, 0.8)',
  backgroundCardSolid: '#FFFFFF',
  
  // Glass effects
  glassBackground: 'rgba(255, 255, 255, 0.7)',
  glassBorder: 'rgba(255, 255, 255, 0.3)',
  glassBlur: 20,
  
  // Text hierarchy
  text: '#0F172A',
  textSecondary: '#475569',
  textTertiary: '#94A3B8',
  textInverse: '#FFFFFF',
  
  // Borders
  border: 'rgba(226, 232, 240, 0.8)',
  borderLight: 'rgba(241, 245, 249, 0.6)',
  borderAccent: 'rgba(16, 185, 129, 0.3)',
  
  // Shadows (glassmorphism style)
  shadow: {
    color: 'rgba(0, 0, 0, 0.08)',
    offset: { width: 0, height: 4 },
    radius: 24,
    elevation: 8,
  },
  shadowLight: {
    color: 'rgba(0, 0, 0, 0.04)',
    offset: { width: 0, height: 2 },
    radius: 12,
    elevation: 4,
  },
  
  // Status
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Tab Bar
  tabBar: {
    background: 'rgba(255, 255, 255, 0.9)',
    activeColor: '#10B981',
    inactiveColor: '#94A3B8',
    indicatorColor: '#10B981',
  },
  
  // Input
  input: {
    background: 'rgba(241, 245, 249, 0.8)',
    border: 'rgba(226, 232, 240, 0.6)',
    focusBorder: '#10B981',
    text: '#0F172A',
    placeholder: '#94A3B8',
  },
  
  // Overlay
  overlay: 'rgba(15, 23, 42, 0.4)',
  overlayStrong: 'rgba(15, 23, 42, 0.7)',
};

// ==================== DARK THEME ====================
export const darkTheme = {
  // Background
  background: '#0F172A',
  backgroundGradient: ['#0F172A', '#1E1B4B'],
  backgroundCard: 'rgba(30, 41, 59, 0.8)',
  backgroundCardSolid: '#1E293B',
  
  // Glass effects (dark mode)
  glassBackground: 'rgba(30, 41, 59, 0.7)',
  glassBorder: 'rgba(71, 85, 105, 0.3)',
  glassBlur: 20,
  
  // Text hierarchy
  text: '#F8FAFC',
  textSecondary: '#CBD5E1',
  textTertiary: '#64748B',
  textInverse: '#0F172A',
  
  // Borders
  border: 'rgba(51, 65, 85, 0.8)',
  borderLight: 'rgba(71, 85, 105, 0.5)',
  borderAccent: 'rgba(16, 185, 129, 0.4)',
  
  // Shadows
  shadow: {
    color: 'rgba(0, 0, 0, 0.3)',
    offset: { width: 0, height: 4 },
    radius: 24,
    elevation: 8,
  },
  shadowLight: {
    color: 'rgba(0, 0, 0, 0.2)',
    offset: { width: 0, height: 2 },
    radius: 12,
    elevation: 4,
  },
  
  // Status
  success: '#34D399',
  warning: '#FBBF24',
  error: '#F87171',
  info: '#60A5FA',
  
  // Tab Bar
  tabBar: {
    background: 'rgba(15, 23, 42, 0.95)',
    activeColor: '#34D399',
    inactiveColor: '#64748B',
    indicatorColor: '#34D399',
  },
  
  // Input
  input: {
    background: 'rgba(51, 65, 85, 0.6)',
    border: 'rgba(71, 85, 105, 0.5)',
    focusBorder: '#34D399',
    text: '#F8FAFC',
    placeholder: '#64748B',
  },
  
  // Overlay
  overlay: 'rgba(0, 0, 0, 0.5)',
  overlayStrong: 'rgba(0, 0, 0, 0.8)',
};

// ==================== TYPOGRAPHY ====================
export const typography = {
  // Font weights
  weights: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  
  // Font sizes com line height
  sizes: {
    xs: { fontSize: 11, lineHeight: 14 },
    sm: { fontSize: 13, lineHeight: 18 },
    base: { fontSize: 15, lineHeight: 22 },
    md: { fontSize: 17, lineHeight: 24 },
    lg: { fontSize: 20, lineHeight: 28 },
    xl: { fontSize: 24, lineHeight: 32 },
    '2xl': { fontSize: 30, lineHeight: 38 },
    '3xl': { fontSize: 36, lineHeight: 44 },
    '4xl': { fontSize: 48, lineHeight: 56 },
  },
  
  // Letter spacing
  tracking: {
    tighter: -0.8,
    tight: -0.4,
    normal: 0,
    wide: 0.4,
    wider: 0.8,
  },
};

// ==================== SPACING ====================
export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 20,
  xl: 24,
  '2xl': 32,
  '3xl': 40,
  '4xl': 48,
  '5xl': 64,
};

// ==================== BORDER RADIUS ====================
export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  '2xl': 24,
  '3xl': 32,
  full: 9999,
};

// ==================== ANIMATIONS ====================
export const animations = {
  // Timing
  duration: {
    fast: 150,
    normal: 250,
    slow: 400,
    slower: 600,
  },
  
  // Spring configs para Reanimated
  spring: {
    gentle: { damping: 20, stiffness: 150 },
    bouncy: { damping: 12, stiffness: 180 },
    snappy: { damping: 18, stiffness: 300 },
    smooth: { damping: 25, stiffness: 120 },
  },
  
  // Easing
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  },
};

// ==================== HELPER FUNCTIONS ====================
export const getTheme = (isDark: boolean) => isDark ? darkTheme : lightTheme;

export const createGradientColors = (opacity: number = 1) => [
  `rgba(16, 185, 129, ${opacity})`,  // Verde
  `rgba(20, 184, 166, ${opacity})`,  // Teal
  `rgba(59, 130, 246, ${opacity})`,  // Azul
];

// Glass card style generator
export const createGlassStyle = (isDark: boolean) => ({
  backgroundColor: isDark ? darkTheme.glassBackground : lightTheme.glassBackground,
  borderWidth: 1,
  borderColor: isDark ? darkTheme.glassBorder : lightTheme.glassBorder,
  borderRadius: radius.xl,
  ...(isDark ? darkTheme.shadow : lightTheme.shadow),
});

export type PremiumTheme = typeof lightTheme;
