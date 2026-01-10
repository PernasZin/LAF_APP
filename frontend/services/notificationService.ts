/**
 * Serviço de Notificações Push
 * 
 * Gerencia:
 * - Registro do dispositivo para push notifications
 * - Agendamento de notificações locais
 * - Lembretes de atualização de peso
 * - Alertas de Peak Week
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuração do handler de notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Tipos de notificação
export type NotificationType = 
  | 'weight_reminder' 
  | 'water_reminder' 
  | 'sodium_reminder'
  | 'general';

interface ScheduledNotification {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  scheduledFor: Date;
}

// Chaves de armazenamento
const STORAGE_KEYS = {
  PUSH_TOKEN: '@push_token',
  NOTIFICATIONS_ENABLED: '@notifications_enabled',
  SCHEDULED_NOTIFICATIONS: '@scheduled_notifications',
  LAST_WEIGHT_REMINDER: '@last_weight_reminder',
};

/**
 * Registra o dispositivo para receber push notifications
 */
export async function registerForPushNotificationsAsync(): Promise<string | null> {
  let token: string | null = null;

  // Verifica se é um dispositivo físico
  if (!Device.isDevice) {
    console.log('Push notifications requerem um dispositivo físico');
    return null;
  }

  // Verifica/solicita permissões
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Permissão para notificações não concedida');
    return null;
  }

  // Obtém o token
  try {
    const tokenData = await Notifications.getExpoPushTokenAsync({
      projectId: process.env.EXPO_PUBLIC_PROJECT_ID,
    });
    token = tokenData.data;
    
    // Salva o token localmente
    await AsyncStorage.setItem(STORAGE_KEYS.PUSH_TOKEN, token);
    
    console.log('Push token:', token);
  } catch (error) {
    console.error('Erro ao obter push token:', error);
  }

  // Configuração específica do Android
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Padrão',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#10B981',
    });

    await Notifications.setNotificationChannelAsync('weight_reminders', {
      name: 'Lembretes de Peso',
      description: 'Lembretes semanais para registrar seu peso',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#3B82F6',
    });

    await Notifications.setNotificationChannelAsync('hydration', {
      name: 'Hidratação',
      description: 'Lembretes de água e sódio',
      importance: Notifications.AndroidImportance.DEFAULT,
      vibrationPattern: [0, 250],
      lightColor: '#06B6D4',
    });
  }

  return token;
}

/**
 * Agenda notificação de lembrete de peso
 */
export async function scheduleWeightReminder(daysFromNow: number = 7): Promise<string | null> {
  try {
    // Cancela lembretes anteriores
    await cancelNotificationsByType('weight_reminder');

    const triggerDate = new Date();
    triggerDate.setDate(triggerDate.getDate() + daysFromNow);
    triggerDate.setHours(9, 0, 0, 0); // 9h da manhã

    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title: '📊 Hora de registrar seu peso!',
        body: 'Já se passou uma semana. Registre seu peso e avalie como foi sua semana.',
        data: { type: 'weight_reminder', action: '/progress' },
        sound: true,
        priority: Notifications.AndroidNotificationPriority.HIGH,
      },
      trigger: {
        date: triggerDate,
        channelId: 'weight_reminders',
      },
    });

    await saveScheduledNotification({
      id,
      type: 'weight_reminder',
      title: 'Lembrete de Peso',
      body: 'Registre seu peso semanal',
      scheduledFor: triggerDate,
    });

    console.log('Lembrete de peso agendado para:', triggerDate);
    return id;
  } catch (error) {
    console.error('Erro ao agendar lembrete de peso:', error);
    return null;
  }
}

/**
 * Agenda notificações de Peak Week
 */
export async function schedulePeakWeekNotifications(
  competitionDate: Date,
  currentWeight: number
): Promise<string[]> {
  const notificationIds: string[] = [];

  try {
    // Cancela notificações anteriores de Peak Week
    await cancelNotificationsByType('peak_week_reminder');
    await cancelNotificationsByType('water_reminder');
    await cancelNotificationsByType('sodium_reminder');

    const now = new Date();
    const daysToCompetition = Math.ceil(
      (competitionDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    );

    // Se estiver na Peak Week (7 dias ou menos)
    if (daysToCompetition <= 7 && daysToCompetition > 0) {
      // Notificação matinal diária com protocolo do dia
      for (let day = 0; day < daysToCompetition; day++) {
        const triggerDate = new Date();
        triggerDate.setDate(triggerDate.getDate() + day);
        triggerDate.setHours(7, 0, 0, 0); // 7h da manhã

        const dayNumber = 7 - daysToCompetition + day + 1;
        const protocol = getPeakWeekDayProtocol(dayNumber, currentWeight);

        const id = await Notifications.scheduleNotificationAsync({
          content: {
            title: `🏆 Peak Week - Dia ${dayNumber}`,
            body: `Hoje: ${protocol.water}L água | ${protocol.sodium}mg sódio | ${protocol.carbs}g carbs`,
            data: { type: 'peak_week_reminder', action: '/peak-week', day: dayNumber },
            sound: true,
            priority: Notifications.AndroidNotificationPriority.MAX,
          },
          trigger: {
            date: triggerDate,
            channelId: 'peak_week',
          },
        });

        notificationIds.push(id);
      }

      // Lembretes de água a cada 2 horas (8h às 20h)
      const waterReminders = [8, 10, 12, 14, 16, 18, 20];
      for (const hour of waterReminders) {
        const triggerDate = new Date();
        triggerDate.setHours(hour, 0, 0, 0);

        // Se já passou a hora hoje, agenda para amanhã
        if (triggerDate <= now) {
          triggerDate.setDate(triggerDate.getDate() + 1);
        }

        const id = await Notifications.scheduleNotificationAsync({
          content: {
            title: '💧 Lembrete de Hidratação',
            body: 'Beba água! Mantenha-se hidratado durante a Peak Week.',
            data: { type: 'water_reminder', action: '/peak-week' },
            sound: false,
            priority: Notifications.AndroidNotificationPriority.DEFAULT,
          },
          trigger: {
            date: triggerDate,
            channelId: 'hydration',
          },
        });

        notificationIds.push(id);
      }
    }

    // Notificação 1 dia antes da competição
    if (daysToCompetition === 1) {
      const triggerDate = new Date();
      triggerDate.setHours(20, 0, 0, 0); // 20h

      const id = await Notifications.scheduleNotificationAsync({
        content: {
          title: '🏆 AMANHÃ É O DIA!',
          body: 'Descanse bem, mantenha a calma. Você está pronto! 💪',
          data: { type: 'peak_week_reminder', action: '/peak-week' },
          sound: true,
          priority: Notifications.AndroidNotificationPriority.MAX,
        },
        trigger: {
          date: triggerDate,
          channelId: 'peak_week',
        },
      });

      notificationIds.push(id);
    }

    console.log('Notificações Peak Week agendadas:', notificationIds.length);
    return notificationIds;
  } catch (error) {
    console.error('Erro ao agendar notificações Peak Week:', error);
    return [];
  }
}

/**
 * Agenda lembrete de água/sódio para Peak Week
 */
export async function scheduleWaterSodiumReminder(
  waterTarget: number,
  sodiumTarget: number,
  hoursFromNow: number = 2
): Promise<string | null> {
  try {
    const triggerDate = new Date();
    triggerDate.setHours(triggerDate.getHours() + hoursFromNow);

    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title: '💧🧂 Lembrete Peak Week',
        body: `Meta: ${waterTarget}L água | ${sodiumTarget}mg sódio. Acompanhe seu consumo!`,
        data: { type: 'water_reminder', action: '/peak-week' },
        sound: false,
        priority: Notifications.AndroidNotificationPriority.DEFAULT,
      },
      trigger: {
        date: triggerDate,
        channelId: 'hydration',
      },
    });

    return id;
  } catch (error) {
    console.error('Erro ao agendar lembrete água/sódio:', error);
    return null;
  }
}

/**
 * Cancela notificações por tipo
 */
export async function cancelNotificationsByType(type: NotificationType): Promise<void> {
  try {
    const scheduled = await Notifications.getAllScheduledNotificationsAsync();
    
    for (const notification of scheduled) {
      if (notification.content.data?.type === type) {
        await Notifications.cancelScheduledNotificationAsync(notification.identifier);
      }
    }
  } catch (error) {
    console.error('Erro ao cancelar notificações:', error);
  }
}

/**
 * Cancela todas as notificações agendadas
 */
export async function cancelAllNotifications(): Promise<void> {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
    await AsyncStorage.removeItem(STORAGE_KEYS.SCHEDULED_NOTIFICATIONS);
  } catch (error) {
    console.error('Erro ao cancelar todas as notificações:', error);
  }
}

/**
 * Retorna todas as notificações agendadas
 */
export async function getScheduledNotifications(): Promise<Notifications.NotificationRequest[]> {
  return await Notifications.getAllScheduledNotificationsAsync();
}

/**
 * Salva notificação agendada no storage
 */
async function saveScheduledNotification(notification: ScheduledNotification): Promise<void> {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEYS.SCHEDULED_NOTIFICATIONS);
    const notifications: ScheduledNotification[] = existing ? JSON.parse(existing) : [];
    
    notifications.push(notification);
    
    await AsyncStorage.setItem(
      STORAGE_KEYS.SCHEDULED_NOTIFICATIONS,
      JSON.stringify(notifications)
    );
  } catch (error) {
    console.error('Erro ao salvar notificação:', error);
  }
}

/**
 * Retorna protocolo do dia da Peak Week
 */
function getPeakWeekDayProtocol(day: number, weight: number): { water: number; sodium: number; carbs: number } {
  const protocols: { [key: number]: { water: number; sodium: number; carbsPerKg: number } } = {
    1: { water: 5.0, sodium: 2000, carbsPerKg: 1.0 },
    2: { water: 4.5, sodium: 1700, carbsPerKg: 0.8 },
    3: { water: 4.0, sodium: 1400, carbsPerKg: 0.6 },
    4: { water: 3.5, sodium: 1000, carbsPerKg: 2.0 },
    5: { water: 3.0, sodium: 800, carbsPerKg: 3.0 },
    6: { water: 2.5, sodium: 600, carbsPerKg: 4.0 },
    7: { water: 2.0, sodium: 500, carbsPerKg: 2.0 },
  };

  const protocol = protocols[day] || protocols[1];
  return {
    water: protocol.water,
    sodium: protocol.sodium,
    carbs: Math.round(protocol.carbsPerKg * weight),
  };
}

/**
 * Verifica e atualiza o status das notificações
 */
export async function checkNotificationPermissions(): Promise<boolean> {
  const { status } = await Notifications.getPermissionsAsync();
  return status === 'granted';
}

/**
 * Adiciona listener para notificações recebidas
 */
export function addNotificationReceivedListener(
  callback: (notification: Notifications.Notification) => void
): Notifications.Subscription {
  return Notifications.addNotificationReceivedListener(callback);
}

/**
 * Adiciona listener para quando o usuário interage com a notificação
 */
export function addNotificationResponseReceivedListener(
  callback: (response: Notifications.NotificationResponse) => void
): Notifications.Subscription {
  return Notifications.addNotificationResponseReceivedListener(callback);
}

export default {
  registerForPushNotificationsAsync,
  scheduleWeightReminder,
  schedulePeakWeekNotifications,
  scheduleWaterSodiumReminder,
  cancelNotificationsByType,
  cancelAllNotifications,
  getScheduledNotifications,
  checkNotificationPermissions,
  addNotificationReceivedListener,
  addNotificationResponseReceivedListener,
};
