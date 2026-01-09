/**
 * Export Data Screen
 * Permite exportar dieta e treino em PDF ou JSON
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../../theme/ThemeContext';
import { pdfExportService } from '../../services/PDFExportService';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Safe fetch with timeout
const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);
  
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

export default function ExportDataScreen() {
  const router = useRouter();
  const { colors } = useTheme();
  const styles = createStyles(colors);

  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [exportType, setExportType] = useState<string | null>(null);
  
  const [profile, setProfile] = useState<any>(null);
  const [diet, setDiet] = useState<any>(null);
  const [workout, setWorkout] = useState<any>(null);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);

      if (id && BACKEND_URL) {
        // Carrega perfil
        try {
          const profileRes = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
          if (profileRes.ok) {
            const data = await profileRes.json();
            setProfile(data);
          }
        } catch (e) {
          const cached = await AsyncStorage.getItem('userProfile');
          if (cached) setProfile(JSON.parse(cached));
        }

        // Carrega dieta
        try {
          const dietRes = await safeFetch(`${BACKEND_URL}/api/diet/${id}`);
          if (dietRes.ok) {
            const data = await dietRes.json();
            setDiet(data);
          }
        } catch (e) {
          console.log('Dieta não carregada');
        }

        // Carrega treino
        try {
          const workoutRes = await safeFetch(`${BACKEND_URL}/api/workout/${id}`);
          if (workoutRes.ok) {
            const data = await workoutRes.json();
            setWorkout(data);
          }
        } catch (e) {
          console.log('Treino não carregado');
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportDietPDF = async () => {
    if (!diet || !profile) {
      Alert.alert('Erro', 'Você precisa ter uma dieta gerada para exportar.');
      return;
    }

    setExporting(true);
    setExportType('diet-pdf');
    
    try {
      await pdfExportService.exportDietPDF(diet, profile);
      Alert.alert('✅ Sucesso', 'PDF da dieta gerado e pronto para compartilhar!');
    } catch (error) {
      console.error('Erro ao exportar dieta:', error);
      Alert.alert('Erro', 'Não foi possível gerar o PDF da dieta.');
    } finally {
      setExporting(false);
      setExportType(null);
    }
  };

  const handleExportWorkoutPDF = async () => {
    if (!workout || !profile) {
      Alert.alert('Erro', 'Você precisa ter um treino gerado para exportar.');
      return;
    }

    setExporting(true);
    setExportType('workout-pdf');
    
    try {
      await pdfExportService.exportWorkoutPDF(workout, profile);
      Alert.alert('✅ Sucesso', 'PDF do treino gerado e pronto para compartilhar!');
    } catch (error) {
      console.error('Erro ao exportar treino:', error);
      Alert.alert('Erro', 'Não foi possível gerar o PDF do treino.');
    } finally {
      setExporting(false);
      setExportType(null);
    }
  };

  const handlePrintDiet = async () => {
    if (!diet || !profile) {
      Alert.alert('Erro', 'Você precisa ter uma dieta gerada para imprimir.');
      return;
    }

    setExporting(true);
    setExportType('diet-print');
    
    try {
      await pdfExportService.printDiet(diet, profile);
    } catch (error) {
      console.error('Erro ao imprimir dieta:', error);
      Alert.alert('Erro', 'Não foi possível imprimir a dieta.');
    } finally {
      setExporting(false);
      setExportType(null);
    }
  };

  const handlePrintWorkout = async () => {
    if (!workout || !profile) {
      Alert.alert('Erro', 'Você precisa ter um treino gerado para imprimir.');
      return;
    }

    setExporting(true);
    setExportType('workout-print');
    
    try {
      await pdfExportService.printWorkout(workout, profile);
    } catch (error) {
      console.error('Erro ao imprimir treino:', error);
      Alert.alert('Erro', 'Não foi possível imprimir o treino.');
    } finally {
      setExporting(false);
      setExportType(null);
    }
  };

  const handleExportJSON = async () => {
    if (!userId || !BACKEND_URL) {
      Alert.alert('Erro', 'Não foi possível identificar o usuário.');
      return;
    }

    setExporting(true);
    setExportType('json');
    
    try {
      // Busca todos os dados
      const [profileRes, dietRes, workoutRes, progressRes] = await Promise.all([
        safeFetch(`${BACKEND_URL}/api/user/profile/${userId}`),
        safeFetch(`${BACKEND_URL}/api/diet/${userId}`),
        safeFetch(`${BACKEND_URL}/api/workout/${userId}`),
        safeFetch(`${BACKEND_URL}/api/progress/weight/${userId}?days=365`),
      ]);

      const exportData = {
        exported_at: new Date().toISOString(),
        app_version: '1.0.0',
        profile: profileRes.ok ? await profileRes.json() : null,
        diet: dietRes.ok ? await dietRes.json() : null,
        workout: workoutRes.ok ? await workoutRes.json() : null,
        progress: progressRes.ok ? await progressRes.json() : null,
      };

      // Salva localmente
      await AsyncStorage.setItem('exportedUserData', JSON.stringify(exportData, null, 2));

      Alert.alert(
        '✅ Dados Exportados',
        `Seus dados foram salvos com sucesso!\n\n• Perfil: ${exportData.profile ? '✓' : '✗'}\n• Dieta: ${exportData.diet ? '✓' : '✗'}\n• Treino: ${exportData.workout ? '✓' : '✗'}\n• Progresso: ${exportData.progress ? '✓' : '✗'}\n\nOs dados estão disponíveis no armazenamento do app.`
      );
    } catch (error) {
      console.error('Erro ao exportar JSON:', error);
      Alert.alert('Erro', 'Não foi possível exportar os dados.');
    } finally {
      setExporting(false);
      setExportType(null);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
            Carregando dados...
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
        <Text style={[styles.headerTitle, { color: colors.text }]}>Exportar Dados</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Status Cards */}
        <View style={styles.statusCards}>
          <View style={[styles.statusCard, { backgroundColor: diet ? colors.success + '15' : colors.textTertiary + '15' }]}>
            <Ionicons 
              name={diet ? 'checkmark-circle' : 'close-circle'} 
              size={24} 
              color={diet ? colors.success : colors.textTertiary} 
            />
            <Text style={[styles.statusText, { color: diet ? colors.success : colors.textTertiary }]}>
              Dieta {diet ? 'Disponível' : 'Não gerada'}
            </Text>
          </View>
          <View style={[styles.statusCard, { backgroundColor: workout ? colors.success + '15' : colors.textTertiary + '15' }]}>
            <Ionicons 
              name={workout ? 'checkmark-circle' : 'close-circle'} 
              size={24} 
              color={workout ? colors.success : colors.textTertiary} 
            />
            <Text style={[styles.statusText, { color: workout ? colors.success : colors.textTertiary }]}>
              Treino {workout ? 'Disponível' : 'Não gerado'}
            </Text>
          </View>
        </View>

        {/* PDF Export Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>EXPORTAR PDF</Text>
          <Text style={[styles.sectionDescription, { color: colors.textTertiary }]}>
            Gere PDFs formatados para imprimir ou compartilhar
          </Text>
          
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            {/* Diet PDF */}
            <TouchableOpacity 
              style={styles.exportOption}
              onPress={handleExportDietPDF}
              disabled={!diet || exporting}
              activeOpacity={0.7}
            >
              <View style={[styles.exportIcon, { backgroundColor: '#10B981' + '20' }]}>
                <Ionicons name="nutrition" size={24} color="#10B981" />
              </View>
              <View style={styles.exportContent}>
                <Text style={[styles.exportTitle, { color: colors.text }]}>Exportar Dieta</Text>
                <Text style={[styles.exportDesc, { color: colors.textSecondary }]}>
                  PDF com todas as refeições e macros
                </Text>
              </View>
              {exporting && exportType === 'diet-pdf' ? (
                <ActivityIndicator size="small" color={colors.primary} />
              ) : (
                <Ionicons name="download-outline" size={24} color={diet ? colors.primary : colors.textTertiary} />
              )}
            </TouchableOpacity>

            <View style={[styles.divider, { backgroundColor: colors.border }]} />

            {/* Workout PDF */}
            <TouchableOpacity 
              style={styles.exportOption}
              onPress={handleExportWorkoutPDF}
              disabled={!workout || exporting}
              activeOpacity={0.7}
            >
              <View style={[styles.exportIcon, { backgroundColor: '#3B82F6' + '20' }]}>
                <Ionicons name="barbell" size={24} color="#3B82F6" />
              </View>
              <View style={styles.exportContent}>
                <Text style={[styles.exportTitle, { color: colors.text }]}>Exportar Treino</Text>
                <Text style={[styles.exportDesc, { color: colors.textSecondary }]}>
                  PDF com exercícios e séries
                </Text>
              </View>
              {exporting && exportType === 'workout-pdf' ? (
                <ActivityIndicator size="small" color={colors.primary} />
              ) : (
                <Ionicons name="download-outline" size={24} color={workout ? colors.primary : colors.textTertiary} />
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* Print Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>IMPRIMIR</Text>
          <Text style={[styles.sectionDescription, { color: colors.textTertiary }]}>
            Envie diretamente para uma impressora
          </Text>
          
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <TouchableOpacity 
              style={styles.exportOption}
              onPress={handlePrintDiet}
              disabled={!diet || exporting}
              activeOpacity={0.7}
            >
              <View style={[styles.exportIcon, { backgroundColor: '#F59E0B' + '20' }]}>
                <Ionicons name="print" size={24} color="#F59E0B" />
              </View>
              <View style={styles.exportContent}>
                <Text style={[styles.exportTitle, { color: colors.text }]}>Imprimir Dieta</Text>
                <Text style={[styles.exportDesc, { color: colors.textSecondary }]}>
                  Envia para impressora disponível
                </Text>
              </View>
              {exporting && exportType === 'diet-print' ? (
                <ActivityIndicator size="small" color={colors.primary} />
              ) : (
                <Ionicons name="chevron-forward" size={24} color={diet ? colors.textSecondary : colors.textTertiary} />
              )}
            </TouchableOpacity>

            <View style={[styles.divider, { backgroundColor: colors.border }]} />

            <TouchableOpacity 
              style={styles.exportOption}
              onPress={handlePrintWorkout}
              disabled={!workout || exporting}
              activeOpacity={0.7}
            >
              <View style={[styles.exportIcon, { backgroundColor: '#8B5CF6' + '20' }]}>
                <Ionicons name="print" size={24} color="#8B5CF6" />
              </View>
              <View style={styles.exportContent}>
                <Text style={[styles.exportTitle, { color: colors.text }]}>Imprimir Treino</Text>
                <Text style={[styles.exportDesc, { color: colors.textSecondary }]}>
                  Envia para impressora disponível
                </Text>
              </View>
              {exporting && exportType === 'workout-print' ? (
                <ActivityIndicator size="small" color={colors.primary} />
              ) : (
                <Ionicons name="chevron-forward" size={24} color={workout ? colors.textSecondary : colors.textTertiary} />
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* JSON Export Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>BACKUP COMPLETO</Text>
          <Text style={[styles.sectionDescription, { color: colors.textTertiary }]}>
            Exporte todos os seus dados em formato JSON
          </Text>
          
          <View style={[styles.card, { backgroundColor: colors.backgroundCard, borderColor: colors.border }]}>
            <TouchableOpacity 
              style={styles.exportOption}
              onPress={handleExportJSON}
              disabled={exporting}
              activeOpacity={0.7}
            >
              <View style={[styles.exportIcon, { backgroundColor: '#EC4899' + '20' }]}>
                <Ionicons name="code-slash" size={24} color="#EC4899" />
              </View>
              <View style={styles.exportContent}>
                <Text style={[styles.exportTitle, { color: colors.text }]}>Exportar JSON</Text>
                <Text style={[styles.exportDesc, { color: colors.textSecondary }]}>
                  Backup completo: perfil, dieta, treino, progresso
                </Text>
              </View>
              {exporting && exportType === 'json' ? (
                <ActivityIndicator size="small" color={colors.primary} />
              ) : (
                <Ionicons name="cloud-download-outline" size={24} color={colors.primary} />
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* Info Box */}
        <View style={[styles.infoBox, { backgroundColor: colors.primary + '10' }]}>
          <Ionicons name="information-circle" size={20} color={colors.primary} />
          <Text style={[styles.infoText, { color: colors.text }]}>
            Os PDFs são gerados localmente no seu dispositivo. Você pode compartilhar via 
            WhatsApp, email, ou salvar em seu dispositivo.
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
    gap: 16,
  },
  loadingText: {
    fontSize: 14,
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
  statusCards: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statusCard: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 4,
    marginLeft: 4,
  },
  sectionDescription: {
    fontSize: 13,
    marginBottom: 12,
    marginLeft: 4,
  },
  card: {
    borderRadius: 16,
    borderWidth: 1,
    overflow: 'hidden',
  },
  exportOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    gap: 12,
  },
  exportIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  exportContent: {
    flex: 1,
  },
  exportTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  exportDesc: {
    fontSize: 13,
    marginTop: 2,
  },
  divider: {
    height: 1,
    marginHorizontal: 16,
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  infoText: {
    flex: 1,
    fontSize: 13,
    lineHeight: 20,
  },
});
