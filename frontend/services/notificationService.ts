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
  cancelNotificationsByType,
  cancelAllNotifications,
  getScheduledNotifications,
  checkNotificationPermissions,
  addNotificationReceivedListener,
  addNotificationResponseReceivedListener,
};
