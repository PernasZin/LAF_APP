/**
 * i18n - Internationalization System
 * Supports: Portuguese (pt), English (en), Spanish (es)
 */

import { pt } from './pt';
import { en } from './en';
import { es } from './es';

export type Language = 'pt' | 'en' | 'es';
export type LanguageCode = 'pt-BR' | 'en-US' | 'es-ES';

export const translations = {
  pt,
  en,
  es,
};

export type Translations = typeof pt;

/**
 * Get translations for a specific language
 */
export function getTranslations(lang: Language | LanguageCode): Translations {
  const langCode = lang.split('-')[0] as Language;
  return translations[langCode] || translations.pt;
}

/**
 * Get a specific translation key with optional interpolation
 */
export function t(
  lang: Language | LanguageCode,
  path: string,
  params?: Record<string, string | number>
): string {
  const langCode = lang.split('-')[0] as Language;
  const trans = translations[langCode] || translations.pt;
  
  // Navigate to the translation
  const keys = path.split('.');
  let result: any = trans;
  
  for (const key of keys) {
    if (result && typeof result === 'object' && key in result) {
      result = result[key];
    } else {
      // Fallback to Portuguese if key not found
      result = translations.pt;
      for (const k of keys) {
        if (result && typeof result === 'object' && k in result) {
          result = result[k];
        } else {
          return path; // Return path if not found in any language
        }
      }
      break;
    }
  }
  
  // Interpolate parameters
  if (typeof result === 'string' && params) {
    Object.entries(params).forEach(([key, value]) => {
      result = result.replace(new RegExp(`{{${key}}}`, 'g'), String(value));
    });
  }
  
  return typeof result === 'string' ? result : path;
}

/**
 * Language names for display
 */
export const languageNames: Record<Language, { native: string; english: string }> = {
  pt: { native: 'Português', english: 'Portuguese' },
  en: { native: 'English', english: 'English' },
  es: { native: 'Español', english: 'Spanish' },
};

/**
 * Language codes mapping
 */
export const languageCodes: Record<Language, LanguageCode> = {
  pt: 'pt-BR',
  en: 'en-US',
  es: 'es-ES',
};

/**
 * Convert language code to short code
 */
export function toShortCode(langCode: LanguageCode | string): Language {
  const short = langCode.split('-')[0];
  if (short === 'pt' || short === 'en' || short === 'es') {
    return short;
  }
  return 'pt'; // Default to Portuguese
}

export { pt, en, es };
