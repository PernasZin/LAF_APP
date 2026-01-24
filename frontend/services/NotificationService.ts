/**
 * Notification Service - Local Notification Settings Manager
 * Gerencia configurações de notificações localmente (sem push notifications)
 * 
 * NOTA: Push Notifications foram desabilitadas temporariamente porque
 * o Provisioning Profile não suporta essa capability. O serviço ainda
 * permite ao usuário configurar seus horários preferidos.
 */
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Tipos de notificação
export type NotificationType = 'meal' | 'workout' | 'weight' | 'custom';

// Horários padrão das refeições
export const DEFAULT_MEAL_TIMES = {
  'Café da Manhã': { hour: 7, minute: 0 },
  'Lanche Manhã': { hour: 10, minute: 0 },
  'Almoço': { hour: 12, minute: 30 },
  'Lanche Tarde': { hour: 16, minute: 0 },
  'Jantar': { hour: 19, minute: 30 },
  'Ceia': { hour: 21, minute: 30 },
};

// Storage keys
const NOTIFICATION_SETTINGS_KEY = 'notification_settings';
const SCHEDULED_NOTIFICATIONS_KEY = 'scheduled_notifications';

export interface NotificationSettings {
  enabled: boolean;
  mealReminders: boolean;
  workoutReminder: boolean;
  weightReminder: boolean;
  mealTimes: typeof DEFAULT_MEAL_TIMES;
  workoutTime: { hour: number; minute: number };
  weightReminderDay: number; // 0-6 (domingo-sábado)
  weightReminderTime: { hour: number; minute: number };
}

const DEFAULT_SETTINGS: NotificationSettings = {
  enabled: true,
  mealReminders: true,
  workoutReminder: true,
  weightReminder: true,
  mealTimes: DEFAULT_MEAL_TIMES,
  workoutTime: { hour: 18, minute: 0 },
  weightReminderDay: 0, // Domingo
  weightReminderTime: { hour: 8, minute: 0 },
};

/**
 * Notification Service - Versão Local
 * Gerencia apenas configurações de notificações sem push notifications
 */
class NotificationService {
  private settings: NotificationSettings = DEFAULT_SETTINGS;
  private isInitialized = false;

  /**
   * Inicializa o serviço de notificações
   */
  async initialize(): Promise<boolean> {
    if (this.isInitialized) return true;

    try {
      // Carrega configurações salvas
      const savedSettings = await AsyncStorage.getItem(NOTIFICATION_SETTINGS_KEY);
      if (savedSettings) {
        this.settings = { ...DEFAULT_SETTINGS, ...JSON.parse(savedSettings) };
      }

      this.isInitialized = true;
      console.log('NotificationService inicializado (modo local)');
      return true;
    } catch (error) {
      console.error('Erro ao inicializar NotificationService:', error);
      return false;
    }
  }

  /**
   * Retorna as configurações atuais
   */
  getSettings(): NotificationSettings {
    return { ...this.settings };
  }

  /**
   * Atualiza as configurações de notificação
   */
  async updateSettings(newSettings: Partial<NotificationSettings>): Promise<void> {
    try {
      this.settings = { ...this.settings, ...newSettings };
      await AsyncStorage.setItem(NOTIFICATION_SETTINGS_KEY, JSON.stringify(this.settings));
      console.log('Configurações de notificação atualizadas');
    } catch (error) {
      console.error('Erro ao salvar configurações:', error);
    }
  }

  /**
   * Limpa listeners (no-op nesta versão)
   */
  cleanup(): void {
    console.log('NotificationService cleanup');
  }

  /**
   * Agenda lembrete de refeição (no-op - retorna ID fake)
   */
  async scheduleMealReminder(
    mealName: string,
    time: { hour: number; minute: number }
  ): Promise<string | null> {
    console.log(`[Mock] Lembrete de refeição configurado: ${mealName} às ${time.hour}:${time.minute}`);
    return `meal_${mealName}_${Date.now()}`;
  }

  /**
   * Agenda lembrete de treino (no-op - retorna ID fake)
   */
  async scheduleWorkoutReminder(
    time: { hour: number; minute: number }
  ): Promise<string | null> {
    console.log(`[Mock] Lembrete de treino configurado: ${time.hour}:${time.minute}`);
    return `workout_${Date.now()}`;
  }

  /**
   * Agenda lembrete de pesagem (no-op - retorna ID fake)
   */
  async scheduleWeightReminder(
    dayOfWeek: number,
    time: { hour: number; minute: number }
  ): Promise<string | null> {
    console.log(`[Mock] Lembrete de pesagem configurado: dia ${dayOfWeek} às ${time.hour}:${time.minute}`);
    return `weight_${Date.now()}`;
  }

  /**
   * Envia notificação local imediata (no-op)
   */
  async sendLocalNotification(
    title: string,
    body: string,
    data?: Record<string, unknown>
  ): Promise<void> {
    console.log(`[Mock] Notificação local: ${title} - ${body}`);
  }

  /**
   * Cancela todas as notificações (no-op)
   */
  async cancelAllNotifications(): Promise<void> {
    console.log('[Mock] Todas notificações canceladas');
  }

  /**
   * Reagenda todas as notificações baseado nas configurações
   */
  async rescheduleAllNotifications(): Promise<void> {
    if (!this.settings.enabled) {
      await this.cancelAllNotifications();
      return;
    }

    console.log('[Mock] Notificações reagendadas baseado nas configurações');
  }

  /**
   * Obtém notificações agendadas (retorna array vazio)
   */
  async getScheduledNotifications(): Promise<any[]> {
    return [];
  }

  /**
   * Verifica se notificações estão habilitadas
   */
  areNotificationsEnabled(): boolean {
    return this.settings.enabled;
  }

  /**
   * Habilita/desabilita notificações
   */
  async setNotificationsEnabled(enabled: boolean): Promise<void> {
    await this.updateSettings({ enabled });
    if (!enabled) {
      await this.cancelAllNotifications();
    } else {
      await this.rescheduleAllNotifications();
    }
  }
}

// Singleton instance
export const notificationService = new NotificationService();
export default notificationService;
