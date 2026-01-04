import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

/**
 * Hook para feedback tátil (vibração) em ações importantes
 * Funciona apenas em dispositivos físicos (iOS/Android)
 */
export const useHaptics = () => {
  // Vibração leve - para seleções e toggles
  const lightImpact = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  };

  // Vibração média - para ações de confirmação
  const mediumImpact = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  };

  // Vibração forte - para ações importantes
  const heavyImpact = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }
  };

  // Feedback de sucesso - para ações completadas
  const successFeedback = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  };

  // Feedback de erro - para erros e falhas
  const errorFeedback = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  };

  // Feedback de aviso - para alertas
  const warningFeedback = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    }
  };

  // Seleção - para mudanças de seleção (tabs, checkboxes)
  const selectionFeedback = async () => {
    if (Platform.OS !== 'web') {
      await Haptics.selectionAsync();
    }
  };

  return {
    lightImpact,
    mediumImpact,
    heavyImpact,
    successFeedback,
    errorFeedback,
    warningFeedback,
    selectionFeedback,
  };
};

export default useHaptics;
