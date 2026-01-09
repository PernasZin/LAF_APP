/**
 * Notification Service - Push Notifications Manager
 * Gerencia notificações push para lembretes de refeições e treinos
 */
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuração padrão de notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

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
  workoutTime: { hour: 17, minute: 0 },
  weightReminderDay: 0, // Domingo
  weightReminderTime: { hour: 8, minute: 0 },
};

class NotificationService {
  private settings: NotificationSettings = DEFAULT_SETTINGS;
  private expoPushToken: string | null = null;
  private notificationListener: any = null;
  private responseListener: any = null;

  /**
   * Inicializa o serviço de notificações
   */
  async initialize(): Promise<boolean> {
    try {
      // Carrega configurações salvas
      await this.loadSettings();

      // Se notificações estão desabilitadas, não continua
      if (!this.settings.enabled) {
        console.log('📵 Notificações desabilitadas pelo usuário');
        return false;
      }

      // Solicita permissões
      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        console.log('❌ Permissões de notificação negadas');
        return false;
      }

      // Configura listeners
      this.setupListeners();

      console.log('✅ NotificationService inicializado com sucesso');
      return true;
    } catch (error) {
      console.error('❌ Erro ao inicializar NotificationService:', error);
      return false;
    }
  }

  /**
   * Solicita permissões de notificação
   */
  async requestPermissions(): Promise<boolean> {
    try {
      // Verifica se é um dispositivo físico
      if (!Device.isDevice) {
        console.log('⚠️ Notificações push só funcionam em dispositivos físicos');
        // Em simulador/emulador, retorna true para não bloquear o fluxo
        return true;
      }

      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        return false;
      }

      // Configura canal para Android
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'LAF Notificações',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#10B981',
          sound: 'default',
        });

        await Notifications.setNotificationChannelAsync('meals', {
          name: 'Lembretes de Refeições',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#F59E0B',
        });

        await Notifications.setNotificationChannelAsync('workout', {
          name: 'Lembretes de Treino',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#3B82F6',
        });
      }

      return true;
    } catch (error) {
      console.error('Erro ao solicitar permissões:', error);
      return false;
    }
  }

  /**
   * Configura listeners de notificações
   */
  private setupListeners(): void {
    // Listener para quando notificação é recebida com app em foreground
    this.notificationListener = Notifications.addNotificationReceivedListener(notification => {
      console.log('📬 Notificação recebida:', notification);
    });

    // Listener para quando usuário interage com notificação
    this.responseListener = Notifications.addNotificationResponseReceivedListener(response => {
      console.log('👆 Usuário interagiu com notificação:', response);
      // Aqui podemos navegar para telas específicas baseado no tipo de notificação
    });
  }

  /**
   * Remove listeners
   */
  cleanup(): void {
    if (this.notificationListener) {
      Notifications.removeNotificationSubscription(this.notificationListener);
    }
    if (this.responseListener) {
      Notifications.removeNotificationSubscription(this.responseListener);
    }
  }

  /**
   * Carrega configurações do AsyncStorage
   */
  async loadSettings(): Promise<NotificationSettings> {
    try {
      const saved = await AsyncStorage.getItem(NOTIFICATION_SETTINGS_KEY);
      if (saved) {
        this.settings = { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
      }
      return this.settings;
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      return DEFAULT_SETTINGS;
    }
  }

  /**
   * Salva configurações no AsyncStorage
   */
  async saveSettings(settings: Partial<NotificationSettings>): Promise<void> {
    try {
      this.settings = { ...this.settings, ...settings };
      await AsyncStorage.setItem(NOTIFICATION_SETTINGS_KEY, JSON.stringify(this.settings));
      
      // Reagenda notificações se necessário
      if (settings.enabled !== undefined || settings.mealReminders !== undefined ||
          settings.workoutReminder !== undefined || settings.weightReminder !== undefined) {
        await this.rescheduleAllNotifications();
      }
    } catch (error) {
      console.error('Erro ao salvar configurações:', error);
    }
  }

  /**
   * Agenda notificação de refeição
   */
  async scheduleMealReminder(mealName: string, hour: number, minute: number): Promise<string | null> {
    try {
      if (!this.settings.enabled || !this.settings.mealReminders) {
        return null;
      }

      const identifier = await Notifications.scheduleNotificationAsync({
        content: {
          title: `🍽️ Hora de ${mealName}!`,
          body: `Não esqueça de fazer sua refeição conforme seu plano de dieta.`,
          data: { type: 'meal', meal: mealName },
          sound: 'default',
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.DAILY,
          hour,
          minute,
        },
      });

      console.log(`✅ Lembrete de ${mealName} agendado para ${hour}:${minute.toString().padStart(2, '0')}`);
      return identifier;
    } catch (error) {
      console.error(`Erro ao agendar lembrete de ${mealName}:`, error);
      return null;
    }
  }

  /**
   * Agenda notificação de treino
   */
  async scheduleWorkoutReminder(hour: number, minute: number): Promise<string | null> {
    try {
      if (!this.settings.enabled || !this.settings.workoutReminder) {
        return null;
      }

      const identifier = await Notifications.scheduleNotificationAsync({
        content: {
          title: '💪 Hora do Treino!',
          body: 'Vamos lá! Seu treino está esperando por você.',
          data: { type: 'workout' },
          sound: 'default',
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.DAILY,
          hour,
          minute,
        },
      });

      console.log(`✅ Lembrete de treino agendado para ${hour}:${minute.toString().padStart(2, '0')}`);
      return identifier;
    } catch (error) {
      console.error('Erro ao agendar lembrete de treino:', error);
      return null;
    }
  }

  /**
   * Agenda notificação semanal de registro de peso
   */
  async scheduleWeightReminder(): Promise<string | null> {
    try {
      if (!this.settings.enabled || !this.settings.weightReminder) {
        return null;
      }

      const { weightReminderDay, weightReminderTime } = this.settings;

      const identifier = await Notifications.scheduleNotificationAsync({
        content: {
          title: '⚖️ Registre seu Peso',
          body: 'Hora de registrar seu peso para acompanhar seu progresso!',
          data: { type: 'weight' },
          sound: 'default',
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.WEEKLY,
          weekday: weightReminderDay + 1, // 1-7 (domingo-sábado) no Expo
          hour: weightReminderTime.hour,
          minute: weightReminderTime.minute,
        },
      });

      console.log(`✅ Lembrete de peso agendado para dia ${weightReminderDay} às ${weightReminderTime.hour}:${weightReminderTime.minute.toString().padStart(2, '0')}`);
      return identifier;
    } catch (error) {
      console.error('Erro ao agendar lembrete de peso:', error);
      return null;
    }
  }

  /**
   * Envia notificação imediata (para testes)
   */
  async sendTestNotification(): Promise<void> {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '🎉 LAF Notificações',
          body: 'Suas notificações estão funcionando corretamente!',
          data: { type: 'test' },
        },
        trigger: null, // null = imediato
      });
      console.log('✅ Notificação de teste enviada');
    } catch (error) {
      console.error('Erro ao enviar notificação de teste:', error);
    }
  }

  /**
   * Cancela todas as notificações agendadas
   */
  async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('🗑️ Todas as notificações canceladas');
    } catch (error) {
      console.error('Erro ao cancelar notificações:', error);
    }
  }

  /**
   * Reagenda todas as notificações baseado nas configurações
   */
  async rescheduleAllNotifications(): Promise<void> {
    try {
      // Cancela todas as notificações existentes
      await this.cancelAllNotifications();

      if (!this.settings.enabled) {
        return;
      }

      // Agenda lembretes de refeições
      if (this.settings.mealReminders) {
        const mealTimes = this.settings.mealTimes;
        for (const [mealName, time] of Object.entries(mealTimes)) {
          await this.scheduleMealReminder(mealName, time.hour, time.minute);
        }
      }

      // Agenda lembrete de treino
      if (this.settings.workoutReminder) {
        const { hour, minute } = this.settings.workoutTime;
        await this.scheduleWorkoutReminder(hour, minute);
      }

      // Agenda lembrete de peso semanal
      if (this.settings.weightReminder) {
        await this.scheduleWeightReminder();
      }

      console.log('✅ Todas as notificações reagendadas');
    } catch (error) {
      console.error('Erro ao reagendar notificações:', error);
    }
  }

  /**
   * Retorna lista de notificações agendadas
   */
  async getScheduledNotifications(): Promise<Notifications.NotificationRequest[]> {
    try {
      return await Notifications.getAllScheduledNotificationsAsync();
    } catch (error) {
      console.error('Erro ao obter notificações agendadas:', error);
      return [];
    }
  }

  /**
   * Retorna configurações atuais
   */
  getSettings(): NotificationSettings {
    return this.settings;
  }
}

// Exporta instância única
export const notificationService = new NotificationService();
