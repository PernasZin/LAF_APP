import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Modal,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../../theme/ThemeContext';
import { getColors } from '../../theme/colors';
import { translations, SupportedLanguage } from '../../i18n/translations';
import { safeFetch } from '../../utils/networkUtils';
import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

// Horários padrão por número de refeições
const DEFAULT_MEAL_TIMES: Record<number, { name: string; time: string }[]> = {
  4: [
    { name: 'Café da Manhã', time: '07:00' },
    { name: 'Almoço', time: '12:00' },
    { name: 'Lanche', time: '16:00' },
    { name: 'Jantar', time: '20:00' },
  ],
  5: [
    { name: 'Café da Manhã', time: '07:00' },
    { name: 'Lanche Manhã', time: '10:00' },
    { name: 'Almoço', time: '12:30' },
    { name: 'Lanche Tarde', time: '16:00' },
    { name: 'Jantar', time: '19:30' },
  ],
  6: [
    { name: 'Café da Manhã', time: '07:00' },
    { name: 'Lanche Manhã', time: '10:00' },
    { name: 'Almoço', time: '12:30' },
    { name: 'Lanche Tarde', time: '16:00' },
    { name: 'Jantar', time: '19:30' },
    { name: 'Ceia', time: '21:30' },
  ],
};

// Nomes das refeições em inglês
const MEAL_NAMES_EN: Record<number, string[]> = {
  4: ['Breakfast', 'Lunch', 'Snack', 'Dinner'],
  5: ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner'],
  6: ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner', 'Supper'],
};

// Nomes das refeições em espanhol
const MEAL_NAMES_ES: Record<number, string[]> = {
  4: ['Desayuno', 'Almuerzo', 'Merienda', 'Cena'],
  5: ['Desayuno', 'Snack Mañana', 'Almuerzo', 'Merienda', 'Cena'],
  6: ['Desayuno', 'Snack Mañana', 'Almuerzo', 'Merienda', 'Cena', 'Cena Ligera'],
};

interface MealTime {
  name: string;
  time: string;
}

export default function MealConfigScreen() {
  const router = useRouter();
  const { theme } = useTheme();
  const colors = getColors(theme);
  
  const [language, setLanguage] = useState<SupportedLanguage>('pt-BR');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  
  const [mealCount, setMealCount] = useState(6);
  const [mealTimes, setMealTimes] = useState<MealTime[]>(DEFAULT_MEAL_TIMES[6]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [tempHour, setTempHour] = useState('07');
  const [tempMinute, setTempMinute] = useState('00');
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const t = translations[language];

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const [id, lang, savedConfig] = await Promise.all([
        AsyncStorage.getItem('userId'),
        AsyncStorage.getItem('language'),
        AsyncStorage.getItem('mealConfig'),
      ]);
      
      setUserId(id);
      if (lang) setLanguage(lang as SupportedLanguage);
      
      if (savedConfig) {
        const config = JSON.parse(savedConfig);
        setMealCount(config.mealCount || 6);
        setMealTimes(config.mealTimes || DEFAULT_MEAL_TIMES[config.mealCount || 6]);
      }
      
      // Também carrega do backend se disponível
      if (id && BACKEND_URL) {
        try {
          const response = await safeFetch(`${BACKEND_URL}/api/user/settings/${id}`);
          if (response.ok) {
            const data = await response.json();
            if (data.meal_count) {
              setMealCount(data.meal_count);
              if (data.meal_times && data.meal_times.length > 0) {
                setMealTimes(data.meal_times);
              } else {
                setMealTimes(DEFAULT_MEAL_TIMES[data.meal_count]);
              }
            }
          }
        } catch (err) {
          console.log('Backend não disponível, usando config local');
        }
      }
    } catch (error) {
      console.error('Erro ao carregar config:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMealName = (index: number): string => {
    if (language === 'en-US') {
      return MEAL_NAMES_EN[mealCount]?.[index] || `Meal ${index + 1}`;
    } else if (language === 'es-ES') {
      return MEAL_NAMES_ES[mealCount]?.[index] || `Comida ${index + 1}`;
    }
    return DEFAULT_MEAL_TIMES[mealCount]?.[index]?.name || `Refeição ${index + 1}`;
  };

  const handleMealCountChange = (count: number) => {
    setMealCount(count);
    const defaultTimes = DEFAULT_MEAL_TIMES[count].map((meal, index) => ({
      name: getMealNameForCount(count, index),
      time: meal.time,
    }));
    setMealTimes(defaultTimes);
    setValidationError(null);
  };

  const getMealNameForCount = (count: number, index: number): string => {
    if (language === 'en-US') {
      return MEAL_NAMES_EN[count]?.[index] || `Meal ${index + 1}`;
    } else if (language === 'es-ES') {
      return MEAL_NAMES_ES[count]?.[index] || `Comida ${index + 1}`;
    }
    return DEFAULT_MEAL_TIMES[count]?.[index]?.name || `Refeição ${index + 1}`;
  };

  const openTimePicker = (index: number) => {
    const currentTime = mealTimes[index].time;
    const [hour, minute] = currentTime.split(':');
    setTempHour(hour);
    setTempMinute(minute);
    setEditingIndex(index);
    setShowTimePicker(true);
  };

  const handleTimeConfirm = () => {
    if (editingIndex === null) return;
    
    const newTime = `${tempHour.padStart(2, '0')}:${tempMinute.padStart(2, '0')}`;
    const newMealTimes = [...mealTimes];
    newMealTimes[editingIndex] = {
      ...newMealTimes[editingIndex],
      time: newTime,
    };
    
    setMealTimes(newMealTimes);
    setShowTimePicker(false);
    setEditingIndex(null);
    validateTimes(newMealTimes);
  };

  const validateTimes = (times: MealTime[]): boolean => {
    // Verifica duplicados
    const timeStrings = times.map(t => t.time);
    const uniqueTimes = new Set(timeStrings);
    if (uniqueTimes.size !== timeStrings.length) {
      const errorMsg = language === 'en-US' 
        ? 'Duplicate times are not allowed'
        : language === 'es-ES'
        ? 'No se permiten horarios duplicados'
        : 'Horários duplicados não são permitidos';
      setValidationError(errorMsg);
      return false;
    }
    
    // Verifica ordem cronológica
    const timeInMinutes = times.map(t => {
      const [h, m] = t.time.split(':').map(Number);
      return h * 60 + m;
    });
    
    for (let i = 1; i < timeInMinutes.length; i++) {
      if (timeInMinutes[i] <= timeInMinutes[i - 1]) {
        const errorMsg = language === 'en-US'
          ? 'Meal times must be in chronological order'
          : language === 'es-ES'
          ? 'Los horarios deben seguir orden cronológico'
          : 'Os horários devem seguir ordem cronológica';
        setValidationError(errorMsg);
        return false;
      }
    }
    
    setValidationError(null);
    return true;
  };

  const handleSave = async () => {
    if (!validateTimes(mealTimes)) {
      return;
    }
    
    setSaving(true);
    try {
      const config = {
        mealCount,
        mealTimes: mealTimes.map((m, i) => ({
          name: getMealName(i),
          time: m.time,
        })),
      };
      
      // Salva localmente
      await AsyncStorage.setItem('mealConfig', JSON.stringify(config));
      
      // Salva no backend
      if (userId && BACKEND_URL) {
        try {
          await safeFetch(`${BACKEND_URL}/api/user/settings/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              meal_count: mealCount,
              meal_times: config.mealTimes,
            }),
          });
        } catch (err) {
          console.log('Erro ao salvar no backend:', err);
        }
      }
      
      const successMsg = language === 'en-US'
        ? 'Settings saved! Your diet will be regenerated.'
        : language === 'es-ES'
        ? '¡Configuración guardada! Tu dieta será regenerada.'
        : 'Configurações salvas! Sua dieta será regenerada.';
      
      Alert.alert(
        language === 'en-US' ? 'Success' : language === 'es-ES' ? 'Éxito' : 'Sucesso',
        successMsg,
        [{ text: 'OK', onPress: () => router.back() }]
      );
    } catch (error) {
      console.error('Erro ao salvar:', error);
      Alert.alert('Erro', 'Não foi possível salvar as configurações');
    } finally {
      setSaving(false);
    }
  };

  const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
  const minutes = ['00', '15', '30', '45'];

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['bottom']}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>
          {language === 'en-US' ? 'Meal Configuration' : 
           language === 'es-ES' ? 'Configuración de Comidas' : 
           'Configuração de Refeições'}
        </Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Seleção de quantidade de refeições */}
        <View style={[styles.section, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            {language === 'en-US' ? 'Number of Meals' :
             language === 'es-ES' ? 'Número de Comidas' :
             'Número de Refeições'}
          </Text>
          <Text style={[styles.sectionDesc, { color: colors.textSecondary }]}>
            {language === 'en-US' ? 'Select how many meals per day' :
             language === 'es-ES' ? 'Selecciona cuántas comidas por día' :
             'Selecione quantas refeições por dia'}
          </Text>
          
          <View style={styles.mealCountContainer}>
            {[4, 5, 6].map((count) => (
              <TouchableOpacity
                key={count}
                style={[
                  styles.mealCountButton,
                  { 
                    backgroundColor: mealCount === count ? colors.primary : colors.backgroundSecondary,
                    borderColor: mealCount === count ? colors.primary : colors.border,
                  }
                ]}
                onPress={() => handleMealCountChange(count)}
              >
                <Text style={[
                  styles.mealCountText,
                  { color: mealCount === count ? '#FFFFFF' : colors.text }
                ]}>
                  {count}
                </Text>
                <Text style={[
                  styles.mealCountLabel,
                  { color: mealCount === count ? '#FFFFFF' : colors.textSecondary }
                ]}>
                  {language === 'en-US' ? 'meals' : language === 'es-ES' ? 'comidas' : 'refeições'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Lista de horários */}
        <View style={[styles.section, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            {language === 'en-US' ? 'Meal Times' :
             language === 'es-ES' ? 'Horarios de Comidas' :
             'Horários das Refeições'}
          </Text>
          <Text style={[styles.sectionDesc, { color: colors.textSecondary }]}>
            {language === 'en-US' ? 'Tap to edit each time' :
             language === 'es-ES' ? 'Toca para editar cada horario' :
             'Toque para editar cada horário'}
          </Text>

          {mealTimes.map((meal, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.mealTimeRow, { borderBottomColor: colors.border }]}
              onPress={() => openTimePicker(index)}
            >
              <View style={styles.mealTimeLeft}>
                <View style={[styles.mealIcon, { backgroundColor: colors.primary + '20' }]}>
                  <Ionicons 
                    name={index === 0 ? 'sunny' : index === mealTimes.length - 1 ? 'moon' : 'restaurant'} 
                    size={20} 
                    color={colors.primary} 
                  />
                </View>
                <Text style={[styles.mealName, { color: colors.text }]}>
                  {getMealName(index)}
                </Text>
              </View>
              <View style={styles.mealTimeRight}>
                <Text style={[styles.mealTime, { color: colors.primary }]}>
                  {meal.time}
                </Text>
                <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Erro de validação */}
        {validationError && (
          <View style={[styles.errorContainer, { backgroundColor: colors.error + '15' }]}>
            <Ionicons name="warning" size={20} color={colors.error} />
            <Text style={[styles.errorText, { color: colors.error }]}>
              {validationError}
            </Text>
          </View>
        )}

        {/* Info sobre distribuição */}
        <View style={[styles.infoContainer, { backgroundColor: colors.info + '15' }]}>
          <Ionicons name="information-circle" size={20} color={colors.info} />
          <Text style={[styles.infoText, { color: colors.info }]}>
            {language === 'en-US' 
              ? 'Calories and macros will be automatically distributed among meals.'
              : language === 'es-ES'
              ? 'Las calorías y macros se distribuirán automáticamente entre las comidas.'
              : 'As calorias e macros serão distribuídas automaticamente entre as refeições.'}
          </Text>
        </View>

        {/* Botão Salvar */}
        <TouchableOpacity
          style={[
            styles.saveButton,
            { backgroundColor: validationError ? colors.textTertiary : colors.primary }
          ]}
          onPress={handleSave}
          disabled={!!validationError || saving}
        >
          {saving ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.saveButtonText}>
              {language === 'en-US' ? 'Save Configuration' :
               language === 'es-ES' ? 'Guardar Configuración' :
               'Salvar Configuração'}
            </Text>
          )}
        </TouchableOpacity>

        <View style={{ height: 40 }} />
      </ScrollView>

      {/* Modal de seleção de horário */}
      <Modal
        visible={showTimePicker}
        transparent
        animationType="fade"
        onRequestClose={() => setShowTimePicker(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.backgroundCard }]}>
            <Text style={[styles.modalTitle, { color: colors.text }]}>
              {language === 'en-US' ? 'Select Time' :
               language === 'es-ES' ? 'Seleccionar Hora' :
               'Selecionar Horário'}
            </Text>
            
            <View style={styles.timePickerContainer}>
              {/* Hora */}
              <View style={styles.pickerColumn}>
                <Text style={[styles.pickerLabel, { color: colors.textSecondary }]}>
                  {language === 'en-US' ? 'Hour' : language === 'es-ES' ? 'Hora' : 'Hora'}
                </Text>
                <ScrollView style={styles.pickerScroll} showsVerticalScrollIndicator={false}>
                  {hours.map((hour) => (
                    <TouchableOpacity
                      key={hour}
                      style={[
                        styles.pickerItem,
                        tempHour === hour && { backgroundColor: colors.primary + '20' }
                      ]}
                      onPress={() => setTempHour(hour)}
                    >
                      <Text style={[
                        styles.pickerItemText,
                        { color: tempHour === hour ? colors.primary : colors.text }
                      ]}>
                        {hour}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>
              
              <Text style={[styles.timeSeparator, { color: colors.text }]}>:</Text>
              
              {/* Minuto */}
              <View style={styles.pickerColumn}>
                <Text style={[styles.pickerLabel, { color: colors.textSecondary }]}>
                  {language === 'en-US' ? 'Minute' : language === 'es-ES' ? 'Minuto' : 'Minuto'}
                </Text>
                <ScrollView style={styles.pickerScroll} showsVerticalScrollIndicator={false}>
                  {minutes.map((minute) => (
                    <TouchableOpacity
                      key={minute}
                      style={[
                        styles.pickerItem,
                        tempMinute === minute && { backgroundColor: colors.primary + '20' }
                      ]}
                      onPress={() => setTempMinute(minute)}
                    >
                      <Text style={[
                        styles.pickerItemText,
                        { color: tempMinute === minute ? colors.primary : colors.text }
                      ]}>
                        {minute}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, { backgroundColor: colors.backgroundSecondary }]}
                onPress={() => setShowTimePicker(false)}
              >
                <Text style={[styles.modalButtonText, { color: colors.text }]}>
                  {language === 'en-US' ? 'Cancel' : language === 'es-ES' ? 'Cancelar' : 'Cancelar'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, { backgroundColor: colors.primary }]}
                onPress={handleTimeConfirm}
              >
                <Text style={[styles.modalButtonText, { color: '#FFFFFF' }]}>
                  {language === 'en-US' ? 'Confirm' : language === 'es-ES' ? 'Confirmar' : 'Confirmar'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
  },
  sectionDesc: {
    fontSize: 14,
    marginBottom: 16,
  },
  mealCountContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  mealCountButton: {
    flex: 1,
    paddingVertical: 20,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
  },
  mealCountText: {
    fontSize: 28,
    fontWeight: '800',
  },
  mealCountLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  mealTimeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    borderBottomWidth: 1,
  },
  mealTimeLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  mealIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mealName: {
    fontSize: 16,
    fontWeight: '600',
  },
  mealTimeRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  mealTime: {
    fontSize: 18,
    fontWeight: '700',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 14,
    borderRadius: 12,
    marginBottom: 16,
  },
  errorText: {
    flex: 1,
    fontSize: 14,
    fontWeight: '500',
  },
  infoContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    padding: 14,
    borderRadius: 12,
    marginBottom: 20,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  saveButton: {
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: '85%',
    borderRadius: 20,
    padding: 24,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 20,
  },
  timePickerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  pickerColumn: {
    alignItems: 'center',
  },
  pickerLabel: {
    fontSize: 12,
    marginBottom: 8,
  },
  pickerScroll: {
    height: 160,
    width: 70,
  },
  pickerItem: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginVertical: 2,
  },
  pickerItemText: {
    fontSize: 20,
    fontWeight: '600',
    textAlign: 'center',
  },
  timeSeparator: {
    fontSize: 32,
    fontWeight: '700',
    marginHorizontal: 16,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  modalButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
});
