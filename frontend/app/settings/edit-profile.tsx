import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Image,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';
import { useTheme } from '../../theme/ThemeContext';
import * as ImagePicker from 'expo-image-picker';
import { Toast } from '../../components';
import { useToast } from '../../hooks/useToast';
import { useHaptics } from '../../hooks/useHaptics';
import DateTimePicker from '@react-native-community/datetimepicker';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// Objetivos disponíveis
const GOALS = [
  { value: 'cutting', label: 'Cutting', description: 'Perda de gordura e definição' },
  { value: 'manutencao', label: 'Manutenção', description: 'Manter peso atual' },
  { value: 'bulking', label: 'Bulking', description: 'Ganho de massa muscular' },
  { value: 'atleta', label: 'Atleta/Competição', description: 'Preparação para campeonato' },
];

const safeFetch = async (url: string, options?: RequestInit) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

export default function EditProfileScreen() {
  const router = useRouter();
  const { colors } = useTheme();
  const { toast, showSuccess, showError, hideToast } = useToast();
  const { lightImpact, mediumImpact, successFeedback, errorFeedback, selectionFeedback } = useHaptics();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  
  // Form state
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('bulking');
  const [originalGoal, setOriginalGoal] = useState('bulking');
  const [profileImage, setProfileImage] = useState<string | null>(null);
  
  // Athlete/Competition state
  const [competitionDate, setCompetitionDate] = useState<Date | null>(null);
  const [showDatePicker, setShowDatePicker] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const id = await AsyncStorage.getItem('userId');
      setUserId(id);
      
      const savedImage = await AsyncStorage.getItem('profileImage');
      if (savedImage) setProfileImage(savedImage);
      
      if (id && BACKEND_URL) {
        try {
          const response = await safeFetch(`${BACKEND_URL}/api/user/profile/${id}`);
          if (response.ok) {
            const data = await response.json();
            setName(data.name || '');
            setGoal(data.goal || 'bulking');
            setOriginalGoal(data.goal || 'bulking');
          }
        } catch (err) {
          const profileData = await AsyncStorage.getItem('userProfile');
          if (profileData) {
            const profile = JSON.parse(profileData);
            setName(profile.name || '');
            setGoal(profile.goal || 'bulking');
            setOriginalGoal(profile.goal || 'bulking');
          }
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permissão Necessária', 'Precisamos de permissão para acessar suas fotos.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        setProfileImage(base64Image);
        await AsyncStorage.setItem('profileImage', base64Image);
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível selecionar a imagem.');
    }
  };

  const handleSave = async () => {
    // Validação
    if (!name.trim()) {
      errorFeedback();
      showError('Nome é obrigatório');
      return;
    }

    // Validação específica para atleta
    if (goal === 'atleta' && !competitionDate) {
      errorFeedback();
      showError('Data do campeonato é obrigatória para atletas');
      return;
    }

    setSaving(true);
    mediumImpact(); // Haptic ao iniciar
    try {
      if (!userId || !BACKEND_URL) throw new Error('Usuário não encontrado');

      // 1. Atualiza perfil com objetivo e data de competição
      const profilePayload: any = {
        name: name.trim(),
        goal: goal,
      };
      
      // Adiciona data de competição se for atleta
      if (goal === 'atleta' && competitionDate) {
        profilePayload.competition_date = competitionDate.toISOString();
      }

      const profileResponse = await safeFetch(`${BACKEND_URL}/api/user/profile/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profilePayload),
      });

      if (!profileResponse.ok) {
        throw new Error('Falha ao atualizar perfil');
      }

      // 2. Se objetivo mudou, recalcula a dieta e dados
      if (goal !== originalGoal) {
        console.log('🔄 Objetivo mudou, recalculando dieta e macros...');
        
        // Deleta dieta existente
        await safeFetch(`${BACKEND_URL}/api/diet/${userId}`, {
          method: 'DELETE',
        });
        
        // Gera nova dieta
        const dietResponse = await safeFetch(`${BACKEND_URL}/api/diet/generate?user_id=${userId}`, {
          method: 'POST',
        });

        if (!dietResponse.ok) {
          console.warn('Aviso: Não foi possível recalcular a dieta');
        } else {
          console.log('✅ Dieta recalculada com sucesso');
        }
      }

      // 3. Atualiza localStorage
      const profileData = await AsyncStorage.getItem('userProfile');
      if (profileData) {
        const profile = JSON.parse(profileData);
        profile.name = name.trim();
        profile.goal = goal;
        await AsyncStorage.setItem('userProfile', JSON.stringify(profile));
      }

      successFeedback(); // Haptic de sucesso
      showSuccess(
        goal !== originalGoal 
          ? 'Perfil atualizado e dieta recalculada!' 
          : 'Perfil atualizado com sucesso!'
      );
      
      // Delay before navigating back
      setTimeout(() => router.back(), 1500);
    } catch (error) {
      console.error('Error saving:', error);
      errorFeedback();
      showError('Não foi possível salvar. Tente novamente.');
    } finally {
      setSaving(false);
    }
  };
  
  // Handle goal selection with haptic
  const handleGoalSelect = (newGoal: string) => {
    selectionFeedback();
    setGoal(newGoal);
  };

  const styles = createStyles(colors);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <KeyboardAvoidingView 
        style={{ flex: 1 }} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          style={styles.scrollView} 
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
        >
          {/* Profile Image */}
          <View style={styles.imageSection}>
            <TouchableOpacity style={styles.imageContainer} onPress={pickImage}>
              {profileImage ? (
                <Image source={{ uri: profileImage }} style={styles.profileImage} />
              ) : (
                <View style={[styles.placeholderImage, { backgroundColor: colors.primaryLight }]}>
                  <Text style={styles.placeholderText}>
                    {name ? name.charAt(0).toUpperCase() : 'U'}
                  </Text>
                </View>
              )}
              <View style={[styles.editBadge, { backgroundColor: colors.primary }]}>
                <Ionicons name="camera" size={16} color="#FFFFFF" />
              </View>
            </TouchableOpacity>
          </View>

          {/* Form */}
          <View style={styles.formSection}>
            {/* Nome */}
            <View style={styles.fieldContainer}>
              <Text style={[styles.label, { color: colors.text }]}>Nome</Text>
              <TextInput
                style={[styles.input, { backgroundColor: colors.inputBackground, borderColor: colors.inputBorder, color: colors.inputText }]}
                value={name}
                onChangeText={setName}
                placeholder="Seu nome"
                placeholderTextColor={colors.inputPlaceholder}
              />
            </View>

            {/* Objetivo */}
            <View style={styles.fieldContainer}>
              <Text style={[styles.label, { color: colors.text }]}>Objetivo</Text>
              <Text style={[styles.sublabel, { color: colors.textSecondary }]}>
                Alterar o objetivo irá recalcular sua dieta
              </Text>
              <View style={styles.goalOptions}>
                {GOALS.map((g) => (
                  <TouchableOpacity
                    key={g.value}
                    style={[
                      styles.goalOption,
                      { 
                        backgroundColor: goal === g.value ? colors.primary + '15' : colors.backgroundCard,
                        borderColor: goal === g.value ? colors.primary : colors.border,
                      }
                    ]}
                    onPress={() => handleGoalSelect(g.value)}
                  >
                    <Text style={[
                      styles.goalLabel, 
                      { color: goal === g.value ? colors.primary : colors.text }
                    ]}>
                      {g.label}
                    </Text>
                    <Text style={[
                      styles.goalDescription, 
                      { color: goal === g.value ? colors.primary : colors.textSecondary }
                    ]}>
                      {g.description}
                    </Text>
                    {goal === g.value && (
                      <Ionicons name="checkmark-circle" size={20} color={colors.primary} style={styles.goalCheck} />
                    )}
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Data do Campeonato - apenas para atletas */}
            {goal === 'atleta' && (
              <View style={styles.fieldContainer}>
                <Text style={[styles.label, { color: colors.text }]}>Data do Campeonato *</Text>
                <Text style={[styles.sublabel, { color: colors.textSecondary }]}>
                  A fase será calculada automaticamente com base nas semanas restantes
                </Text>
                <TouchableOpacity
                  style={[styles.dateButton, { backgroundColor: colors.inputBackground, borderColor: colors.inputBorder }]}
                  onPress={() => setShowDatePicker(true)}
                >
                  <Ionicons name="calendar" size={20} color={colors.primary} />
                  <Text style={[styles.dateText, { color: competitionDate ? colors.text : colors.inputPlaceholder }]}>
                    {competitionDate 
                      ? competitionDate.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
                      : 'Selecionar data do campeonato'}
                  </Text>
                </TouchableOpacity>
                {competitionDate && (
                  <View style={[styles.phaseInfo, { backgroundColor: colors.primary + '15' }]}>
                    <Ionicons name="trophy" size={16} color={colors.primary} />
                    <Text style={[styles.phaseText, { color: colors.primary }]}>
                      {(() => {
                        const now = new Date();
                        const days = Math.ceil((competitionDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
                        const weeks = Math.floor(days / 7);
                        if (days < 0) return 'Pós-Show (Recuperação)';
                        if (weeks < 2) return `Peak Week (${days} dias)`;
                        if (weeks <= 16) return `Pré-Contest (${weeks} semanas)`;
                        return `Off-Season (${weeks} semanas)`;
                      })()}
                    </Text>
                  </View>
                )}
              </View>
            )}
          </View>

          {/* Save Button */}
          <TouchableOpacity
            style={[styles.saveButton, { backgroundColor: colors.primary }, saving && styles.saveButtonDisabled]}
            onPress={handleSave}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.saveButtonText}>Salvar Alterações</Text>
            )}
          </TouchableOpacity>

          {/* Warning if goal changed */}
          {goal !== originalGoal && (
            <View style={[styles.warningBox, { backgroundColor: colors.warning + '15' }]}>
              <Ionicons name="information-circle" size={20} color={colors.warning} />
              <Text style={[styles.warningText, { color: colors.warning }]}>
                Sua dieta será recalculada ao salvar
              </Text>
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>

      {/* Toast notification */}
      <Toast
        visible={toast.visible}
        message={toast.message}
        type={toast.type}
        onHide={hideToast}
      />
    </SafeAreaView>
  );
}

const createStyles = (colors: any) => StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scrollView: { flex: 1 },
  content: { padding: 24 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  imageSection: { alignItems: 'center', marginBottom: 32 },
  imageContainer: { position: 'relative', marginBottom: 12 },
  profileImage: { width: 100, height: 100, borderRadius: 50 },
  placeholderImage: { width: 100, height: 100, borderRadius: 50, justifyContent: 'center', alignItems: 'center' },
  placeholderText: { fontSize: 40, fontWeight: '700', color: '#FFFFFF' },
  editBadge: { position: 'absolute', bottom: 0, right: 0, width: 32, height: 32, borderRadius: 16, justifyContent: 'center', alignItems: 'center', borderWidth: 3, borderColor: colors.background },
  formSection: { marginBottom: 24 },
  fieldContainer: { marginBottom: 20 },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8 },
  sublabel: { fontSize: 12, marginBottom: 12, marginTop: -4 },
  input: { height: 52, borderRadius: 12, borderWidth: 1, paddingHorizontal: 16, fontSize: 16 },
  goalOptions: { gap: 10 },
  goalOption: { padding: 16, borderRadius: 12, borderWidth: 2, flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap' },
  goalLabel: { fontSize: 16, fontWeight: '600', marginRight: 8 },
  goalDescription: { fontSize: 13 },
  goalCheck: { position: 'absolute', right: 16 },
  saveButton: { height: 56, borderRadius: 16, justifyContent: 'center', alignItems: 'center' },
  saveButtonDisabled: { opacity: 0.7 },
  saveButtonText: { color: '#FFFFFF', fontSize: 18, fontWeight: '700' },
  warningBox: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 12, borderRadius: 8, marginTop: 16 },
  warningText: { fontSize: 13, flex: 1 },
});
