/**
 * LAF Premium Privacy Screen
 * ===========================
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Modal, TextInput, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { ArrowLeft, Shield, Lock, Eye, Database, Trash2, AlertTriangle, X } from 'lucide-react-native';

import { useSettingsStore } from '../../stores/settingsStore';
import { useAuthStore } from '../../stores/authStore';
import { lightTheme, darkTheme, premiumColors, radius, spacing } from '../../theme/premium';
import { useTranslation } from '../../i18n';
import { config } from '../../config';

const BACKEND_URL = config.BACKEND_URL;

const GlassCard = ({ children, style, isDark }: any) => {
  const cardStyle = {
    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.8)',
    borderWidth: 1,
    borderColor: isDark ? 'rgba(71, 85, 105, 0.3)' : 'rgba(255, 255, 255, 0.5)',
    borderRadius: radius.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: isDark ? 0.3 : 0.08,
    shadowRadius: 16,
    elevation: 8,
  };
  return <View style={[cardStyle, style]}>{children}</View>;
};

const Section = ({ icon: Icon, title, content, isDark, color = premiumColors.primary }: any) => {
  const theme = isDark ? darkTheme : lightTheme;
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <View style={[styles.sectionIconBg, { backgroundColor: color + '15' }]}>
          <Icon size={20} color={color} />
        </View>
        <Text style={[styles.sectionTitle, { color: theme.text }]}>{title}</Text>
      </View>
      <Text style={[styles.sectionContent, { color: theme.textSecondary }]}>{content}</Text>
    </View>
  );
};

export default function PrivacyScreen() {
  const { t } = useTranslation();
  const effectiveTheme = useSettingsStore((state) => state.effectiveTheme);
  const isDark = effectiveTheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;
  
  const userId = useAuthStore((state) => state.userId);
  const logout = useAuthStore((state) => state.logout);
  
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [password, setPassword] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');

  const handleDeleteAccount = async () => {
    if (!password.trim()) {
      setError(t.privacy.passwordRequired || 'Digite sua senha para confirmar');
      return;
    }

    setIsDeleting(true);
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/delete-account`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Limpar dados locais
        await AsyncStorage.clear();
        
        // Fazer logout
        logout();
        
        // Mostrar mensagem de sucesso
        Alert.alert(
          t.privacy.accountDeleted || 'Conta Excluída',
          t.privacy.accountDeletedDesc || 'Sua conta e todos os dados foram excluídos permanentemente.',
          [
            {
              text: 'OK',
              onPress: () => router.replace('/auth/login'),
            },
          ]
        );
      } else {
        setError(data.detail || t.privacy.deleteError || 'Erro ao excluir conta. Verifique sua senha.');
      }
    } catch (err) {
      console.error('Erro ao excluir conta:', err);
      setError(t.privacy.deleteError || 'Erro ao excluir conta. Tente novamente.');
    } finally {
      setIsDeleting(false);
    }
  };

  const openDeleteModal = () => {
    setPassword('');
    setError('');
    setShowDeleteModal(true);
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <LinearGradient
        colors={isDark
          ? ['rgba(16, 185, 129, 0.05)', 'transparent', 'rgba(59, 130, 246, 0.03)']
          : ['rgba(16, 185, 129, 0.08)', 'transparent', 'rgba(59, 130, 246, 0.05)']
        }
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <Animated.View entering={FadeInDown.springify()} style={styles.header}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
              <ArrowLeft size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.headerTitle, { color: theme.text }]}>{t.privacy.title}</Text>
            <View style={{ width: 44 }} />
          </Animated.View>

          {/* Content */}
          <Animated.View entering={FadeInDown.delay(100).springify()}>
            <GlassCard isDark={isDark} style={styles.card}>
              <Section
                icon={Shield}
                title={t.privacy.dataSecurity}
                content={t.privacy.dataSecurityDesc}
                isDark={isDark}
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <Section
                icon={Lock}
                title={t.privacy.protectedAccess}
                content={t.privacy.protectedAccessDesc}
                isDark={isDark}
                color="#3B82F6"
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <Section
                icon={Eye}
                title={t.privacy.transparency}
                content={t.privacy.transparencyDesc}
                isDark={isDark}
                color="#8B5CF6"
              />
              <View style={[styles.divider, { backgroundColor: theme.border }]} />
              <Section
                icon={Database}
                title={t.privacy.localStorage}
                content={t.privacy.localStorageDesc}
                isDark={isDark}
                color="#F59E0B"
              />
            </GlassCard>
          </Animated.View>

          {/* Delete Account */}
          <Animated.View entering={FadeInDown.delay(200).springify()}>
            <TouchableOpacity 
              style={[styles.deleteButton, { borderColor: '#EF4444' }]}
              onPress={openDeleteModal}
            >
              <Trash2 size={18} color="#EF4444" />
              <Text style={styles.deleteButtonText}>{t.privacy.requestDeletion}</Text>
            </TouchableOpacity>
          </Animated.View>
        </ScrollView>
      </SafeAreaView>

      {/* Modal de Confirmação de Exclusão */}
      <Modal
        visible={showDeleteModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowDeleteModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: isDark ? '#1E293B' : '#FFFFFF' }]}>
            {/* Header do Modal */}
            <View style={styles.modalHeader}>
              <View style={styles.warningIconContainer}>
                <AlertTriangle size={32} color="#EF4444" />
              </View>
              <TouchableOpacity 
                style={styles.closeButton}
                onPress={() => setShowDeleteModal(false)}
              >
                <X size={24} color={theme.textSecondary} />
              </TouchableOpacity>
            </View>

            <Text style={[styles.modalTitle, { color: theme.text }]}>
              {t.privacy.deleteAccountTitle || 'Excluir Conta'}
            </Text>
            
            <Text style={[styles.modalDescription, { color: theme.textSecondary }]}>
              {t.privacy.deleteAccountWarning || 'Esta ação é irreversível. Todos os seus dados serão permanentemente excluídos, incluindo:'}
            </Text>

            <View style={styles.deleteList}>
              <Text style={[styles.deleteListItem, { color: theme.textSecondary }]}>• Perfil e configurações</Text>
              <Text style={[styles.deleteListItem, { color: theme.textSecondary }]}>• Histórico de dietas</Text>
              <Text style={[styles.deleteListItem, { color: theme.textSecondary }]}>• Histórico de treinos</Text>
              <Text style={[styles.deleteListItem, { color: theme.textSecondary }]}>• Progresso e medições</Text>
            </View>

            <Text style={[styles.passwordLabel, { color: theme.text }]}>
              {t.privacy.confirmPassword || 'Digite sua senha para confirmar:'}
            </Text>

            <TextInput
              style={[
                styles.passwordInput,
                { 
                  backgroundColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                  color: theme.text,
                  borderColor: error ? '#EF4444' : (isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)'),
                }
              ]}
              placeholder={t.privacy.passwordPlaceholder || 'Sua senha'}
              placeholderTextColor={theme.textTertiary}
              secureTextEntry
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                setError('');
              }}
              editable={!isDeleting}
            />

            {error ? (
              <Text style={styles.errorText}>{error}</Text>
            ) : null}

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.cancelButton, { borderColor: theme.border }]}
                onPress={() => setShowDeleteModal(false)}
                disabled={isDeleting}
              >
                <Text style={[styles.cancelButtonText, { color: theme.text }]}>
                  {t.common.cancel || 'Cancelar'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.confirmDeleteButton, isDeleting && styles.buttonDisabled]}
                onPress={handleDeleteAccount}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <>
                    <Trash2 size={16} color="#FFFFFF" />
                    <Text style={styles.confirmDeleteText}>
                      {t.privacy.confirmDelete || 'Excluir Conta'}
                    </Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollContent: { padding: spacing.lg },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  backButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700' },

  card: { padding: spacing.lg, marginBottom: spacing.lg },
  section: { paddingVertical: spacing.sm },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.sm },
  sectionIconBg: { width: 36, height: 36, borderRadius: radius.md, alignItems: 'center', justifyContent: 'center' },
  sectionTitle: { fontSize: 16, fontWeight: '700' },
  sectionContent: { fontSize: 14, lineHeight: 20, marginLeft: 48 },
  divider: { height: 1, marginVertical: spacing.md },

  deleteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    padding: spacing.base,
    borderRadius: radius.lg,
    borderWidth: 1.5,
  },
  deleteButtonText: { color: '#EF4444', fontSize: 15, fontWeight: '600' },

  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  modalContent: {
    width: '100%',
    maxWidth: 400,
    borderRadius: radius.xl,
    padding: spacing.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  warningIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButton: {
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: '700',
    marginBottom: spacing.sm,
  },
  modalDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  deleteList: {
    marginBottom: spacing.lg,
    paddingLeft: spacing.sm,
  },
  deleteListItem: {
    fontSize: 13,
    lineHeight: 22,
  },
  passwordLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: spacing.sm,
  },
  passwordInput: {
    height: 48,
    borderRadius: radius.md,
    borderWidth: 1,
    paddingHorizontal: spacing.base,
    fontSize: 16,
    marginBottom: spacing.sm,
  },
  errorText: {
    color: '#EF4444',
    fontSize: 13,
    marginBottom: spacing.md,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: spacing.md,
    marginTop: spacing.md,
  },
  cancelButton: {
    flex: 1,
    height: 48,
    borderRadius: radius.md,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButtonText: {
    fontSize: 15,
    fontWeight: '600',
  },
  confirmDeleteButton: {
    flex: 1,
    height: 48,
    borderRadius: radius.md,
    backgroundColor: '#EF4444',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: spacing.sm,
  },
  confirmDeleteText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '600',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
});
