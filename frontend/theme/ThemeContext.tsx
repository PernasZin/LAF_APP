/**
 * Theme Context Provider
 * Fornece cores baseadas no tema atual para toda a aplicação
 */
import React, { createContext, useContext, useMemo } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { getColors, ThemeColors } from './colors';

interface ThemeContextType {
  colors: ThemeColors;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  
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
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
