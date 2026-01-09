/**
 * Notification Settings Screen
 * Configurações detalhadas de notificações push com seleção de horários
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
  Modal,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useTheme } from '../../theme/ThemeContext';
import { useTranslation } from '../../i18n';
import { notificationService, NotificationSettings, DEFAULT_MEAL_TIMES } from '../../services/NotificationService';

// Dias da semana com tradução
const WEEK_DAYS_KEYS = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'] as const;

export default function NotificationsSettingsScreen() {
  const router = useRouter();
  const { colors } = useTheme();
  const { t } = useTranslation();
  const styles = createStyles(colors);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  
  // Time Picker State
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [editingTime, setEditingTime] = useState<{
    type: 'meal' | 'workout' | 'weight';
    mealKey?: string;
    currentHour: number;
    currentMinute: number;
  } | null>(null);
  
  // Day Picker for weight reminder
  const [showDayPicker, setShowDayPicker] = useState(false);

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
      Alert.alert(t.common.error, 'Não foi possível carregar as configurações');
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
      Alert.alert(t.common.error, 'Não foi possível salvar a configuração');
    } finally {
      setSaving(false);
    }
  };

  const updateMealTime = async (mealKey: string, hour: number, minute: number) => {
    if (!settings) return;

    setSaving(true);
    try {
      const newMealTimes = {
        ...settings.mealTimes,
        [mealKey]: { hour, minute }
      };
      const newSettings = { ...settings, mealTimes: newMealTimes };
      setSettings(newSettings);
      await notificationService.saveSettings({ mealTimes: newMealTimes });
    } catch (error) {
      console.error('Erro ao salvar horário:', error);
    } finally {
      setSaving(false);
    }
  };

  const updateWorkoutTime = async (hour: number, minute: number) => {
    if (!settings) return;

    setSaving(true);
    try {
      const workoutTime = { hour, minute };
      const newSettings = { ...settings, workoutTime };
      setSettings(newSettings);
      await notificationService.saveSettings({ workoutTime });
    } catch (error) {
      console.error('Erro ao salvar horário:', error);
    } finally {
      setSaving(false);
    }
  };

  const updateWeightReminderTime = async (hour: number, minute: number) => {
    if (!settings) return;

    setSaving(true);
    try {
      const weightReminderTime = { hour, minute };
      const newSettings = { ...settings, weightReminderTime };
      setSettings(newSettings);
      await notificationService.saveSettings({ weightReminderTime });
    } catch (error) {
      console.error('Erro ao salvar horário:', error);
    } finally {
      setSaving(false);
    }
  };

  const updateWeightReminderDay = async (day: number) => {
    if (!settings) return;

    setSaving(true);
    try {
      const newSettings = { ...settings, weightReminderDay: day };
      setSettings(newSettings);
      await notificationService.saveSettings({ weightReminderDay: day });
      setShowDayPicker(false);
    } catch (error) {
      console.error('Erro ao salvar dia:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      await notificationService.sendTestNotification();
      Alert.alert('✅ ' + t.common.success, 'Notificação de teste enviada!');
    } catch (error) {
      Alert.alert(t.common.error, 'Não foi possível enviar a notificação de teste');
    }
  };

  const formatTime = (hour: number, minute: number): string => {
    return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
  };

  const openTimePicker = (type: 'meal' | 'workout' | 'weight', mealKey?: string) => {
    if (!settings) return;
    
    let currentHour = 12;
    let currentMinute = 0;
    
    if (type === 'meal' && mealKey) {
      const time = settings.mealTimes[mealKey as keyof typeof settings.mealTimes];
      if (time) {
        currentHour = time.hour;
        currentMinute = time.minute;
      }
    } else if (type === 'workout') {
      currentHour = settings.workoutTime.hour;
      currentMinute = settings.workoutTime.minute;
    } else if (type === 'weight') {
      currentHour = settings.weightReminderTime.hour;
      currentMinute = settings.weightReminderTime.minute;
    }
    
    setEditingTime({ type, mealKey, currentHour, currentMinute });
    setShowTimePicker(true);
  };

  const handleTimeChange = (event: any, selectedDate?: Date) => {
    if (Platform.OS === 'android') {
      setShowTimePicker(false);
    }
    
    if (event.type === 'dismissed' || !selectedDate || !editingTime) {
      setShowTimePicker(false);
      return;
    }
    
    const hour = selectedDate.getHours();
    const minute = selectedDate.getMinutes();
    
    if (editingTime.type === 'meal' && editingTime.mealKey) {
      updateMealTime(editingTime.mealKey, hour, minute);
    } else if (editingTime.type === 'workout') {
      updateWorkoutTime(hour, minute);
    } else if (editingTime.type === 'weight') {
      updateWeightReminderTime(hour, minute);
    }
    
    if (Platform.OS === 'ios') {
      // iOS keeps picker open
    } else {
      setShowTimePicker(false);
    }
  };

  const getMealLabel = (mealKey: string): string => {
    const mealMap: Record<string, keyof typeof t.meals> = {
      'Café da Manhã': 'breakfast',
      'Lanche Manhã': 'morningSnack',
      'Almoço': 'lunch',
      'Lanche Tarde': 'afternoonSnack',
      'Jantar': 'dinner',
      'Ceia': 'supper',
    };
    return t.meals[mealMap[mealKey] || 'breakfast'] || mealKey;
  };

  const getWeekDayLabel = (dayIndex: number): string => {
    const key = WEEK_DAYS_KEYS[dayIndex];
    return t.weekDays[key] || '';
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
            {t.common.error}
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
        <Text style={[styles.headerTitle, { color: colors.text }]}>{t.notificationSettings.title}</Text>
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
              <Text style={[styles.settingTitle, { color: colors.text }]}>{t.notificationSettings.enableAll}</Text>
              <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                {t.notificationSettings.enableAllDesc}
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
          style={[styles.testButton, { backgroundColor: colors.primary, opacity: settings.enabled ? 1 : 0.5 }]}
          onPress={handleTestNotification}
          disabled={!settings.enabled}
          activeOpacity={0.8}
        >
          <Ionicons name="send" size={20} color="#FFF" />
          <Text style={styles.testButtonText}>{t.notificationSettings.sendTest}</Text>
        </TouchableOpacity>

        {/* Meal Reminders */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
            {t.notificationSettings.mealReminders.toUpperCase()}
          </Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.settingRow}>
              <View style={styles.settingIcon}>
                <Ionicons name="restaurant" size={22} color="#F59E0B" />
              </View>
              <View style={styles.settingContent}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>{t.notificationSettings.mealRemindersTitle}</Text>
                <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                  {t.notificationSettings.mealRemindersDesc}
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
                  {t.notificationSettings.mealTimes}
                </Text>
                {Object.entries(settings.mealTimes).map(([meal, time]) => (
                  <TouchableOpacity 
                    key={meal} 
                    style={styles.mealTimeRow}
                    onPress={() => openTimePicker('meal', meal)}
                    activeOpacity={0.7}
                  >
                    <Text style={[styles.mealName, { color: colors.text }]}>{getMealLabel(meal)}</Text>
                    <View style={styles.timeButton}>
                      <Text style={[styles.mealTime, { color: colors.primary }]}>
                        {formatTime(time.hour, time.minute)}
                      </Text>
                      <Ionicons name="time-outline" size={18} color={colors.primary} />
                    </View>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>
        </View>

        {/* Workout Reminder */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
            {t.notificationSettings.workoutReminder.toUpperCase()}
          </Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.settingRow}>
              <View style={styles.settingIcon}>
                <Ionicons name="barbell" size={22} color="#3B82F6" />
              </View>
              <View style={styles.settingContent}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>{t.notificationSettings.workoutReminderTitle}</Text>
                <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                  {t.notificationSettings.workoutReminderDesc}
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
                <TouchableOpacity 
                  style={styles.timeRow}
                  onPress={() => openTimePicker('workout')}
                  activeOpacity={0.7}
                >
                  <Text style={[styles.timeLabel, { color: colors.textSecondary }]}>{t.notificationSettings.time}:</Text>
                  <View style={styles.timeButton}>
                    <Text style={[styles.timeValue, { color: colors.primary }]}>
                      {formatTime(settings.workoutTime.hour, settings.workoutTime.minute)}
                    </Text>
                    <Ionicons name="time-outline" size={18} color={colors.primary} />
                  </View>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>

        {/* Weight Reminder */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
            {t.notificationSettings.weightReminder.toUpperCase()}
          </Text>
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <View style={styles.settingRow}>
              <View style={styles.settingIcon}>
                <Ionicons name="scale" size={22} color="#10B981" />
              </View>
              <View style={styles.settingContent}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>{t.notificationSettings.weightReminderTitle}</Text>
                <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                  {t.notificationSettings.weightReminderDesc}
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
                  <TouchableOpacity 
                    style={styles.timeRow}
                    onPress={() => setShowDayPicker(true)}
                    activeOpacity={0.7}
                  >
                    <Text style={[styles.timeLabel, { color: colors.textSecondary }]}>{t.notificationSettings.day}:</Text>
                    <View style={styles.timeButton}>
                      <Text style={[styles.timeValue, { color: colors.primary }]}>
                        {getWeekDayLabel(settings.weightReminderDay)}
                      </Text>
                      <Ionicons name="chevron-down" size={18} color={colors.primary} />
                    </View>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.timeRow}
                    onPress={() => openTimePicker('weight')}
                    activeOpacity={0.7}
                  >
                    <Text style={[styles.timeLabel, { color: colors.textSecondary }]}>{t.notificationSettings.time}:</Text>
                    <View style={styles.timeButton}>
                      <Text style={[styles.timeValue, { color: colors.primary }]}>
                        {formatTime(settings.weightReminderTime.hour, settings.weightReminderTime.minute)}
                      </Text>
                      <Ionicons name="time-outline" size={18} color={colors.primary} />
                    </View>
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>

        {/* Info Box */}
        <View style={[styles.infoBox, { backgroundColor: colors.primary + '15' }]}>
          <Ionicons name="information-circle" size={20} color={colors.primary} />
          <Text style={[styles.infoText, { color: colors.text }]}>
            {t.notificationSettings.infoText}
          </Text>
        </View>
      </ScrollView>

      {/* Time Picker Modal (iOS) */}
      {Platform.OS === 'ios' && showTimePicker && editingTime && (
        <Modal
          visible={showTimePicker}
          transparent
          animationType="slide"
          onRequestClose={() => setShowTimePicker(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={[styles.pickerModal, { backgroundColor: colors.background }]}>
              <View style={styles.pickerHeader}>
                <TouchableOpacity onPress={() => setShowTimePicker(false)}>
                  <Text style={[styles.pickerCancel, { color: colors.error }]}>{t.common.cancel}</Text>
                </TouchableOpacity>
                <Text style={[styles.pickerTitle, { color: colors.text }]}>
                  {editingTime.type === 'meal' ? getMealLabel(editingTime.mealKey || '') : 
                   editingTime.type === 'workout' ? t.notificationSettings.workoutReminderTitle : 
                   t.notificationSettings.weightReminderTitle}
                </Text>
                <TouchableOpacity onPress={() => setShowTimePicker(false)}>
                  <Text style={[styles.pickerDone, { color: colors.primary }]}>{t.common.done}</Text>
                </TouchableOpacity>
              </View>
              <DateTimePicker
                value={new Date(2000, 0, 1, editingTime.currentHour, editingTime.currentMinute)}
                mode="time"
                display="spinner"
                onChange={handleTimeChange}
                textColor={colors.text}
              />
            </View>
          </View>
        </Modal>
      )}

      {/* Time Picker (Android) */}
      {Platform.OS === 'android' && showTimePicker && editingTime && (
        <DateTimePicker
          value={new Date(2000, 0, 1, editingTime.currentHour, editingTime.currentMinute)}
          mode="time"
          display="default"
          onChange={handleTimeChange}
        />
      )}

      {/* Day Picker Modal */}
      <Modal
        visible={showDayPicker}
        transparent
        animationType="slide"
        onRequestClose={() => setShowDayPicker(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.dayPickerModal, { backgroundColor: colors.background }]}>
            <View style={styles.pickerHeader}>
              <TouchableOpacity onPress={() => setShowDayPicker(false)}>
                <Text style={[styles.pickerCancel, { color: colors.error }]}>{t.common.cancel}</Text>
              </TouchableOpacity>
              <Text style={[styles.pickerTitle, { color: colors.text }]}>{t.notificationSettings.day}</Text>
              <View style={{ width: 60 }} />
            </View>
            <ScrollView style={styles.dayList}>
              {WEEK_DAYS_KEYS.map((key, index) => (
                <TouchableOpacity
                  key={key}
                  style={[
                    styles.dayOption,
                    settings?.weightReminderDay === index && { backgroundColor: colors.primary + '15' }
                  ]}
                  onPress={() => updateWeightReminderDay(index)}
                >
                  <Text style={[
                    styles.dayOptionText,
                    { color: settings?.weightReminderDay === index ? colors.primary : colors.text }
                  ]}>
                    {t.weekDays[key]}
                  </Text>
                  {settings?.weightReminderDay === index && (
                    <Ionicons name="checkmark" size={22} color={colors.primary} />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>
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
    paddingVertical: 12,
    borderBottomWidth: 0.5,
    borderBottomColor: colors.border,
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
    paddingVertical: 8,
  },
  timeLabel: {
    fontSize: 14,
  },
  timeValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  timeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.primary + '10',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
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
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  pickerModal: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: 20,
  },
  dayPickerModal: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '50%',
  },
  pickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  pickerTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  pickerCancel: {
    fontSize: 16,
  },
  pickerDone: {
    fontSize: 16,
    fontWeight: '600',
  },
  dayList: {
    padding: 8,
  },
  dayOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginVertical: 2,
  },
  dayOptionText: {
    fontSize: 16,
  },
});
