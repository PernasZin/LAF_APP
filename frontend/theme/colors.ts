/**
 * LAF Theme Colors
 * Sistema de cores para Light e Dark mode - Visual Moderno e Clean
 */

export const lightColors = {
  // Primary - Verde Esmeralda mais vibrante
  primary: '#10B981',
  primaryLight: '#34D399',
  primaryDark: '#059669',
  
  // Background - Tons mais suaves
  background: '#FAFBFC',
  backgroundSecondary: '#F3F4F6',
  backgroundCard: '#FFFFFF',
  
  // Text - Hierarquia clara
  text: '#1F2937',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',
  
  // Borders - Mais sutis
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  
  // Status - Cores mais modernas
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Tab Bar
  tabBarBackground: '#FFFFFF',
  tabBarActive: '#10B981',
  tabBarInactive: '#9CA3AF',
  
  // Input - Campos mais elegantes
  inputBackground: '#F9FAFB',
  inputBorder: '#E5E7EB',
  inputText: '#1F2937',
  inputPlaceholder: '#9CA3AF',
  
  // Toggle
  toggleActive: '#10B981',
  toggleInactive: '#E5E7EB',
  toggleThumb: '#FFFFFF',
  
  // Extras para visual premium
  cardShadow: 'rgba(0, 0, 0, 0.04)',
  overlay: 'rgba(0, 0, 0, 0.5)',
};

export const darkColors = {
  // Primary - Verde vibrante que funciona no escuro
  primary: '#10B981',
  primaryLight: '#34D399',
  primaryDark: '#059669',
  
  // Background - Tons de cinza escuro modernos
  background: '#0F172A',
  backgroundSecondary: '#1E293B',
  backgroundCard: '#1E293B',
  
  // Text - Alto contraste
  text: '#F8FAFC',
  textSecondary: '#CBD5E1',
  textTertiary: '#94A3B8',
  textInverse: '#0F172A',
  
  // Borders - Visíveis mas sutis
  border: '#334155',
  borderLight: '#475569',
  
  // Status
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Tab Bar
  tabBarBackground: '#1E293B',
  tabBarActive: '#10B981',
  tabBarInactive: '#94A3B8',
  
  // Input
  inputBackground: '#334155',
  inputBorder: '#475569',
  inputText: '#F8FAFC',
  inputPlaceholder: '#94A3B8',
  
  // Toggle
  toggleActive: '#10B981',
  toggleInactive: '#475569',
  toggleThumb: '#FFFFFF',
  
  // Extras
  cardShadow: 'rgba(0, 0, 0, 0.3)',
  overlay: 'rgba(0, 0, 0, 0.7)',
};

export type ThemeColors = typeof lightColors;

export const getColors = (theme: 'light' | 'dark'): ThemeColors => {
  return theme === 'dark' ? darkColors : lightColors;
};
