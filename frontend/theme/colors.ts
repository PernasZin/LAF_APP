/**
 * LAF Theme Colors
 * Sistema de cores para Light e Dark mode
 */

export const lightColors = {
  // Primary
  primary: '#10B981',
  primaryLight: '#34D399',
  primaryDark: '#059669',
  
  // Background
  background: '#FFFFFF',
  backgroundSecondary: '#F9FAFB',
  backgroundCard: '#FFFFFF',
  
  // Text
  text: '#111827',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',
  
  // Borders
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  
  // Status
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Tab Bar
  tabBarBackground: '#FFFFFF',
  tabBarActive: '#10B981',
  tabBarInactive: '#9CA3AF',
  
  // Input
  inputBackground: '#F9FAFB',
  inputBorder: '#E5E7EB',
  inputText: '#111827',
  inputPlaceholder: '#9CA3AF',
  
  // Toggle
  toggleActive: '#10B981',
  toggleInactive: '#E5E7EB',
  toggleThumb: '#FFFFFF',
};

export const darkColors = {
  // Primary
  primary: '#10B981',
  primaryLight: '#34D399',
  primaryDark: '#059669',
  
  // Background
  background: '#111827',
  backgroundSecondary: '#1F2937',
  backgroundCard: '#1F2937',
  
  // Text
  text: '#F9FAFB',
  textSecondary: '#D1D5DB',
  textTertiary: '#9CA3AF',
  textInverse: '#111827',
  
  // Borders
  border: '#374151',
  borderLight: '#4B5563',
  
  // Status
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Tab Bar
  tabBarBackground: '#1F2937',
  tabBarActive: '#10B981',
  tabBarInactive: '#9CA3AF',
  
  // Input
  inputBackground: '#374151',
  inputBorder: '#4B5563',
  inputText: '#F9FAFB',
  inputPlaceholder: '#9CA3AF',
  
  // Toggle
  toggleActive: '#10B981',
  toggleInactive: '#4B5563',
  toggleThumb: '#FFFFFF',
};

export type ThemeColors = typeof lightColors;

export const getColors = (theme: 'light' | 'dark'): ThemeColors => {
  return theme === 'dark' ? darkColors : lightColors;
};
