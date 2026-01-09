/**
 * Hook de Tradução - useTranslation
 * Fornece traduções baseadas no idioma selecionado
 */
import { useMemo } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { translations, Translations, SupportedLanguage } from './translations';

export function useTranslation() {
  const language = useSettingsStore((state) => state.language) as SupportedLanguage;
  
  const t = useMemo(() => {
    return translations[language] || translations['pt-BR'];
  }, [language]);
  
  // Função helper para traduzir com fallback
  const translate = (key: string): string => {
    const keys = key.split('.');
    let result: any = t;
    
    for (const k of keys) {
      if (result && typeof result === 'object' && k in result) {
        result = result[k];
      } else {
        // Fallback para pt-BR se não encontrar
        result = translations['pt-BR'];
        for (const fallbackKey of keys) {
          if (result && typeof result === 'object' && fallbackKey in result) {
            result = result[fallbackKey];
          } else {
            return key; // Retorna a chave se não encontrar
          }
        }
        break;
      }
    }
    
    return typeof result === 'string' ? result : key;
  };
  
  return {
    t,
    language,
    translate,
  };
}

export type { Translations, SupportedLanguage };
