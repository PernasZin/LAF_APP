/**
 * Theme Context Provider
 * Fornece cores baseadas no tema atual para toda a aplicação
 * SAFE: Handles errors gracefully to prevent app crash on startup
 */
import React, { createContext, useContext, useMemo } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { getColors, ThemeColors } from './colors';

interface ThemeContextType {
  colors: ThemeColors;
  isDark: boolean;
}

// Default light theme colors for fallback
const defaultColors = getColors('light');

const ThemeContext = createContext<ThemeContextType>({
  colors: defaultColors,
  isDark: false,
});

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Safe access to store with fallback
  let effectiveTheme: 'light' | 'dark' = 'light';
  
  try {
    effectiveTheme = useSettingsStore((state) => state.effectiveTheme) || 'light';
  } catch (error) {
    console.log('ThemeProvider: Using default theme (store not ready)');
  }
  
  const value = useMemo(() => ({
    colors: getColors(effectiveTheme),
    isDark: effectiveTheme === 'dark',
  }), [effectiveTheme]);
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  // Always return context - it has defaults now
  return context;
};
