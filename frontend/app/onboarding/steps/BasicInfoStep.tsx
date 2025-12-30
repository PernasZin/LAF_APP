import React from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  data: any;
  updateData: (data: any) => void;
}

export default function BasicInfoStep({ data, updateData }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Vamos começar!</Text>
      <Text style={styles.description}>
        Conte-nos um pouco sobre você para personalizarmos seu plano.
      </Text>

      {/* Nome */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>Nome</Text>
        <TextInput
          style={styles.input}
          placeholder="Seu nome"
          value={data.name}
          onChangeText={(text) => updateData({ name: text })}
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {/* Idade */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>Idade</Text>
        <TextInput
          style={styles.input}
          placeholder="Sua idade"
          value={data.age}
          onChangeText={(text) => updateData({ age: text })}
          keyboardType="numeric"
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {/* Sexo */}
      <View style={styles.inputGroup}>
        <Text style={styles.label}>Sexo</Text>
        <View style={styles.optionRow}>
          <TouchableOpacity
            style={[
              styles.optionButton,
              data.sex === 'masculino' && styles.optionButtonActive,
            ]}
            onPress={() => updateData({ sex: 'masculino' })}
            activeOpacity={0.7}
          >
            <Ionicons 
              name="male" 
              size={24} 
              color={data.sex === 'masculino' ? '#10B981' : '#6B7280'}
            />
            <Text
              style={[
                styles.optionText,
                data.sex === 'masculino' && styles.optionTextActive,
              ]}
            >
              Masculino
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.optionButton,
              data.sex === 'feminino' && styles.optionButtonActive,
            ]}
            onPress={() => updateData({ sex: 'feminino' })}
            activeOpacity={0.7}
          >
            <Ionicons 
              name="female" 
              size={24} 
              color={data.sex === 'feminino' ? '#10B981' : '#6B7280'}
            />
            <Text
              style={[
                styles.optionText,
                data.sex === 'feminino' && styles.optionTextActive,
              ]}
            >
              Feminino
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 32,
    lineHeight: 24,
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F9FAFB',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#111827',
  },
  optionRow: {
    flexDirection: 'row',
    gap: 12,
  },
  optionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  optionButtonActive: {
    borderColor: '#10B981',
    backgroundColor: '#F0FDF4',
  },
  optionText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#6B7280',
  },
  optionTextActive: {
    color: '#10B981',
    fontWeight: '600',
  },
});