/**
 * useTranslation Hook
 * Hook for accessing translations based on the current language setting
 */

import { useMemo } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { getTranslations, t as translate, toShortCode, Translations, Language } from '../i18n';

export interface UseTranslationReturn {
  /** Current translations object */
  translations: Translations;
  /** Current language code (pt, en, es) */
  language: Language;
  /** Full language code (pt-BR, en-US, es-ES) */
  languageCode: string;
  /** Translation function with interpolation support */
  t: (path: string, params?: Record<string, string | number>) => string;
}

/**
 * Hook to access translations based on current language setting
 * 
 * @example
 * const { t, translations } = useTranslation();
 * 
 * // Using t function
 * <Text>{t('auth.login')}</Text>
 * <Text>{t('home.greeting', { name: 'John' })}</Text>
 * 
 * // Using translations object directly
 * <Text>{translations.auth.login}</Text>
 */
export function useTranslation(): UseTranslationReturn {
  const languageCode = useSettingsStore((state) => state.language);
  
  const language = useMemo(() => toShortCode(languageCode), [languageCode]);
  
  const translations = useMemo(() => getTranslations(language), [language]);
  
  const t = useMemo(() => {
    return (path: string, params?: Record<string, string | number>) => {
      return translate(language, path, params);
    };
  }, [language]);
  
  return {
    translations,
    language,
    languageCode,
    t,
  };
}

/**
 * Shorthand for getting just the t function
 */
export function useT() {
  const { t } = useTranslation();
  return t;
}

export default useTranslation;
