/**
 * Notification Settings Screen
 * Configurações detalhadas de notificações push
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useTheme } from '../../theme/ThemeContext';
import { notificationService, NotificationSettings, DEFAULT_MEAL_TIMES } from '../../services/NotificationService';

// Dias da semana
const WEEK_DAYS = [
  { value: 0, label: 'Domingo' },
  { value: 1, label: 'Segunda' },
  { value: 2, label: 'Terça' },
  { value: 3, label: 'Quarta' },
  { value: 4, label: 'Quinta' },
  { value: 5, label: 'Sexta' },
  { value: 6, label: 'Sábado' },
];

export default function NotificationsSettingsScreen() {
  const router = useRouter();
  const { colors } = useTheme();
  const styles = createStyles(colors);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<NotificationSettings | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const loaded = await notificationService.loadSettings();
      setSettings(loaded);
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      Alert.alert('Erro', 'Não foi possível carregar as configurações');
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: keyof NotificationSettings, value: any) => {
    if (!settings) return;

    setSaving(true);
    try {
      const newSettings = { ...settings, [key]: value };
      setSettings(newSettings);
      await notificationService.saveSettings({ [key]: value });
    } catch (error) {
      console.error('Erro ao salvar configuração:', error);
      Alert.alert('Erro', 'Não foi possível salvar a configuração');
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      await notificationService.sendTestNotification();
      Alert.alert('✅ Sucesso', 'Notificação de teste enviada!');
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível enviar a notificação de teste');
    }
  };

  const formatTime = (hour: number, minute: number): string => {
    return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  if (!settings) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <Text style={[styles.errorText, { color: colors.error }]}>
            Erro ao carregar configurações
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>Notificações</Text>
        {saving && <ActivityIndicator size="small" color={colors.primary} />}
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Master Toggle */}
        <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <View style={styles.settingRow}>
            <View style={styles.settingIcon}>
              <Ionicons name="notifications" size={24} color={colors.primary} />
            </View>
            <View style={styles.settingContent}>
              <Text style={[styles.settingTitle, { color: colors.text }]}>Ativar Notificações</Text>
              <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                Habilita todas as notificações do app
              </Text>
            </View>
            <Switch
              value={settings.enabled}
              onValueChange={(value) => updateSetting('enabled', value)}
              trackColor={{ false: colors.toggleInactive, true: colors.toggleActive }}
              thumbColor={colors.toggleThumb}
            />
          </View>
        </View>

        {/* Test Button */}
        <TouchableOpacity 
          style={[styles.testButton, { backgroundColor: colors.primary }]}
          onPress={handleTestNotification}
          disabled={!settings.enabled}
          activeOpacity={0.8}
        >
          <Ionicons name="send" size={20} color="#FFF" />
          <Text style={styles.testButtonText}>Enviar Notificação de Teste</Text>
        </TouchableOpacity>

        {/* Meal Reminders */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>LEMBRETES DE REFEIÇÕES</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.settingRow}>
              <View style={styles.settingIcon}>
                <Ionicons name="restaurant" size={22} color="#F59E0B" />
              </View>
              <View style={styles.settingContent}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>Lembretes de Refeições</Text>
                <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                  Receba lembretes nos horários das suas refeições
                </Text>
              </View>
              <Switch
                value={settings.mealReminders}
                onValueChange={(value) => updateSetting('mealReminders', value)}
                trackColor={{ false: colors.toggleInactive, true: colors.toggleActive }}
                thumbColor={colors.toggleThumb}
                disabled={!settings.enabled}
              />
            </View>

            {settings.mealReminders && settings.enabled && (
              <View style={styles.mealTimesContainer}>
                <View style={[styles.divider, { backgroundColor: colors.border }]} />
                <Text style={[styles.subSectionTitle, { color: colors.textSecondary }]}>
                  Horários das Refeições
                </Text>
                {Object.entries(settings.mealTimes).map(([meal, time]) => (
                  <View key={meal} style={styles.mealTimeRow}>
                    <Text style={[styles.mealName, { color: colors.text }]}>{meal}</Text>
                    <Text style={[styles.mealTime, { color: colors.primary }]}>
                      {formatTime(time.hour, time.minute)}
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        </View>

        {/* Workout Reminder */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>LEMBRETE DE TREINO</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.settingRow}>
              <View style={styles.settingIcon}>
                <Ionicons name="barbell" size={22} color="#3B82F6" />
              </View>
              <View style={styles.settingContent}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>Lembrete de Treino</Text>
                <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                  Lembrete diário para treinar
                </Text>
              </View>
              <Switch
                value={settings.workoutReminder}
                onValueChange={(value) => updateSetting('workoutReminder', value)}
                trackColor={{ false: colors.toggleInactive, true: colors.toggleActive }}
                thumbColor={colors.toggleThumb}
                disabled={!settings.enabled}
              />
            </View>

            {settings.workoutReminder && settings.enabled && (
              <>
                <View style={[styles.divider, { backgroundColor: colors.border }]} />
                <View style={styles.timeRow}>
                  <Text style={[styles.timeLabel, { color: colors.textSecondary }]}>Horário:</Text>
                  <Text style={[styles.timeValue, { color: colors.primary }]}>
                    {formatTime(settings.workoutTime.hour, settings.workoutTime.minute)}
                  </Text>
                </View>
              </>
            )}
          </View>
        </View>

        {/* Weight Reminder */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>LEMBRETE DE PESO</Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.settingRow}>
              <View style={styles.settingIcon}>
                <Ionicons name="scale" size={22} color="#10B981" />
              </View>
              <View style={styles.settingContent}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>Lembrete Semanal</Text>
                <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                  Lembre-se de registrar seu peso
                </Text>
              </View>
              <Switch
                value={settings.weightReminder}
                onValueChange={(value) => updateSetting('weightReminder', value)}
                trackColor={{ false: colors.toggleInactive, true: colors.toggleActive }}
                thumbColor={colors.toggleThumb}
                disabled={!settings.enabled}
              />
            </View>

            {settings.weightReminder && settings.enabled && (
              <>
                <View style={[styles.divider, { backgroundColor: colors.border }]} />
                <View style={styles.weightReminderInfo}>
                  <View style={styles.timeRow}>
                    <Text style={[styles.timeLabel, { color: colors.textSecondary }]}>Dia:</Text>
                    <Text style={[styles.timeValue, { color: colors.primary }]}>
                      {WEEK_DAYS.find(d => d.value === settings.weightReminderDay)?.label || 'Domingo'}
                    </Text>
                  </View>
                  <View style={styles.timeRow}>
                    <Text style={[styles.timeLabel, { color: colors.textSecondary }]}>Horário:</Text>
                    <Text style={[styles.timeValue, { color: colors.primary }]}>
                      {formatTime(settings.weightReminderTime.hour, settings.weightReminderTime.minute)}
                    </Text>
                  </View>
                </View>
              </>
            )}
          </View>
        </View>

        {/* Info Box */}
        <View style={[styles.infoBox, { backgroundColor: colors.primary + '15' }]}>
          <Ionicons name="information-circle" size={20} color={colors.primary} />
          <Text style={[styles.infoText, { color: colors.text }]}>
            As notificações push funcionam mesmo com o app fechado. Certifique-se de permitir 
            notificações nas configurações do seu dispositivo.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const createStyles = (colors: any) => StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    gap: 16,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    flex: 1,
    fontSize: 20,
    fontWeight: '700',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingTop: 0,
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 12,
    marginLeft: 4,
  },
  card: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingIcon: {
    width: 40,
    alignItems: 'center',
  },
  settingContent: {
    flex: 1,
    marginRight: 12,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  settingDescription: {
    fontSize: 13,
    marginTop: 2,
    lineHeight: 18,
  },
  divider: {
    height: 1,
    marginVertical: 16,
  },
  subSectionTitle: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 12,
  },
  mealTimesContainer: {
    marginTop: 8,
  },
  mealTimeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  mealName: {
    fontSize: 14,
  },
  mealTime: {
    fontSize: 14,
    fontWeight: '600',
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  timeLabel: {
    fontSize: 14,
  },
  timeValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  weightReminderInfo: {
    gap: 8,
  },
  testButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 14,
    borderRadius: 12,
    marginTop: 16,
  },
  testButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    padding: 16,
    borderRadius: 12,
    marginTop: 24,
    marginBottom: 16,
  },
  infoText: {
    flex: 1,
    fontSize: 13,
    lineHeight: 20,
  },
});
