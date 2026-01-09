/**
 * PDF Export Service - Gerador de PDF para Dietas e Treinos
 * Permite exportar dieta e treino em PDF para compartilhar
 */
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { Platform } from 'react-native';

// Tipos
export interface DietMeal {
  name: string;
  time: string;
  total_calories: number;
  macros: {
    protein: number;
    carbs: number;
    fat: number;
  };
  foods: Array<{
    name: string;
    quantity: string;
    protein: number;
    carbs: number;
    fat: number;
    calories: number;
  }>;
}

export interface DietPlan {
  meals: DietMeal[];
  target_calories: number;
  target_macros: {
    protein: number;
    carbs: number;
    fat: number;
  };
  computed_calories: number;
  computed_macros: {
    protein: number;
    carbs: number;
    fat: number;
  };
}

export interface WorkoutExercise {
  name: string;
  sets: number;
  reps: string;
  rest: string;
  notes?: string;
}

export interface WorkoutDay {
  day: number;
  name: string;
  focus: string;
  exercises: WorkoutExercise[];
}

export interface WorkoutPlan {
  workout_plan: WorkoutDay[];
}

export interface UserProfile {
  name: string;
  age: number;
  weight: number;
  height: number;
  goal: string;
  target_calories: number;
  macros: {
    protein: number;
    carbs: number;
    fat: number;
  };
}

/**
 * Gera o HTML para o PDF da dieta
 */
function generateDietHTML(diet: DietPlan, profile: UserProfile): string {
  const today = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  const goalLabel = {
    cutting: 'Emagrecimento (Cutting)',
    bulking: 'Ganho de Massa (Bulking)',
    manutencao: 'Manutenção',
    atleta: 'Atleta/Competição',
  }[profile.goal] || profile.goal;

  let mealsHTML = '';
  diet.meals.forEach((meal) => {
    let foodsHTML = '';
    meal.foods.forEach((food) => {
      foodsHTML += `
        <tr>
          <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">${food.name}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">${food.quantity}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">${food.protein}g</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">${food.carbs}g</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">${food.fat}g</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">${food.calories} kcal</td>
        </tr>
      `;
    });

    mealsHTML += `
      <div style="margin-bottom: 24px; break-inside: avoid;">
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 12px 16px; border-radius: 8px 8px 0 0;">
          <h3 style="margin: 0; font-size: 16px;">🍽️ ${meal.name} - ${meal.time}</h3>
          <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">
            ${Math.round(meal.total_calories)} kcal | P: ${meal.macros.protein}g | C: ${meal.macros.carbs}g | G: ${meal.macros.fat}g
          </p>
        </div>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; border-top: none;">
          <thead>
            <tr style="background: #f9fafb;">
              <th style="padding: 10px 12px; text-align: left; font-size: 12px; color: #6b7280;">Alimento</th>
              <th style="padding: 10px 12px; text-align: center; font-size: 12px; color: #6b7280;">Qtd</th>
              <th style="padding: 10px 12px; text-align: center; font-size: 12px; color: #6b7280;">Prot</th>
              <th style="padding: 10px 12px; text-align: center; font-size: 12px; color: #6b7280;">Carb</th>
              <th style="padding: 10px 12px; text-align: center; font-size: 12px; color: #6b7280;">Gord</th>
              <th style="padding: 10px 12px; text-align: center; font-size: 12px; color: #6b7280;">Kcal</th>
            </tr>
          </thead>
          <tbody>
            ${foodsHTML}
          </tbody>
        </table>
      </div>
    `;
  });

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
          padding: 20px;
          color: #111827;
          line-height: 1.5;
        }
        @page { margin: 15mm; }
      </style>
    </head>
    <body>
      <!-- Header -->
      <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #10B981;">
        <h1 style="font-size: 28px; color: #10B981; margin-bottom: 8px;">🥗 Plano de Dieta LAF</h1>
        <p style="color: #6b7280; font-size: 14px;">Gerado em ${today}</p>
      </div>

      <!-- User Info Card -->
      <div style="background: #f9fafb; border-radius: 12px; padding: 20px; margin-bottom: 30px; border: 1px solid #e5e7eb;">
        <h2 style="font-size: 18px; margin-bottom: 16px; color: #111827;">📊 Resumo do Perfil</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
          <div style="flex: 1; min-width: 120px;">
            <p style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Nome</p>
            <p style="font-size: 16px; font-weight: 600;">${profile.name}</p>
          </div>
          <div style="flex: 1; min-width: 120px;">
            <p style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Objetivo</p>
            <p style="font-size: 16px; font-weight: 600;">${goalLabel}</p>
          </div>
          <div style="flex: 1; min-width: 120px;">
            <p style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Meta Calórica</p>
            <p style="font-size: 16px; font-weight: 600; color: #EF4444;">${Math.round(profile.target_calories)} kcal</p>
          </div>
        </div>
        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
          <h3 style="font-size: 14px; margin-bottom: 12px; color: #374151;">Metas de Macros Diários</h3>
          <div style="display: flex; gap: 16px;">
            <div style="flex: 1; background: #EEF2FF; padding: 12px; border-radius: 8px; text-align: center;">
              <p style="font-size: 20px; font-weight: 700; color: #4F46E5;">${Math.round(profile.macros.protein)}g</p>
              <p style="font-size: 11px; color: #6366F1;">Proteína</p>
            </div>
            <div style="flex: 1; background: #FEF3C7; padding: 12px; border-radius: 8px; text-align: center;">
              <p style="font-size: 20px; font-weight: 700; color: #D97706;">${Math.round(profile.macros.carbs)}g</p>
              <p style="font-size: 11px; color: #F59E0B;">Carboidratos</p>
            </div>
            <div style="flex: 1; background: #FEE2E2; padding: 12px; border-radius: 8px; text-align: center;">
              <p style="font-size: 20px; font-weight: 700; color: #DC2626;">${Math.round(profile.macros.fat)}g</p>
              <p style="font-size: 11px; color: #EF4444;">Gorduras</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Meals -->
      <h2 style="font-size: 20px; margin-bottom: 20px; color: #111827;">🍴 Refeições do Dia</h2>
      ${mealsHTML}

      <!-- Footer -->
      <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
        <p style="color: #9ca3af; font-size: 12px;">Gerado pelo app LAF - Seu assistente de dieta e treino</p>
        <p style="color: #9ca3af; font-size: 11px; margin-top: 4px;">© ${new Date().getFullYear()} LAF App</p>
      </div>
    </body>
    </html>
  `;
}

/**
 * Gera o HTML para o PDF do treino
 */
function generateWorkoutHTML(workout: WorkoutPlan, profile: UserProfile): string {
  const today = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  let workoutsHTML = '';
  workout.workout_plan.forEach((day) => {
    let exercisesHTML = '';
    day.exercises.forEach((exercise, index) => {
      exercisesHTML += `
        <tr>
          <td style="padding: 10px 12px; border-bottom: 1px solid #eee; font-weight: 500;">${index + 1}. ${exercise.name}</td>
          <td style="padding: 10px 12px; border-bottom: 1px solid #eee; text-align: center;">${exercise.sets}</td>
          <td style="padding: 10px 12px; border-bottom: 1px solid #eee; text-align: center;">${exercise.reps}</td>
          <td style="padding: 10px 12px; border-bottom: 1px solid #eee; text-align: center;">${exercise.rest}</td>
          <td style="padding: 10px 12px; border-bottom: 1px solid #eee; color: #6b7280; font-size: 12px;">${exercise.notes || '-'}</td>
        </tr>
      `;
    });

    workoutsHTML += `
      <div style="margin-bottom: 30px; break-inside: avoid;">
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: white; padding: 14px 18px; border-radius: 10px 10px 0 0;">
          <h3 style="margin: 0; font-size: 18px;">💪 Treino ${day.day} - ${day.name}</h3>
          <p style="margin: 6px 0 0 0; font-size: 13px; opacity: 0.9;">Foco: ${day.focus} | ${day.exercises.length} exercícios</p>
        </div>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; border-top: none;">
          <thead>
            <tr style="background: #f9fafb;">
              <th style="padding: 12px; text-align: left; font-size: 12px; color: #6b7280; width: 35%;">Exercício</th>
              <th style="padding: 12px; text-align: center; font-size: 12px; color: #6b7280; width: 12%;">Séries</th>
              <th style="padding: 12px; text-align: center; font-size: 12px; color: #6b7280; width: 15%;">Reps</th>
              <th style="padding: 12px; text-align: center; font-size: 12px; color: #6b7280; width: 13%;">Descanso</th>
              <th style="padding: 12px; text-align: left; font-size: 12px; color: #6b7280; width: 25%;">Notas</th>
            </tr>
          </thead>
          <tbody>
            ${exercisesHTML}
          </tbody>
        </table>
      </div>
    `;
  });

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
          padding: 20px;
          color: #111827;
          line-height: 1.5;
        }
        @page { margin: 15mm; }
      </style>
    </head>
    <body>
      <!-- Header -->
      <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #3B82F6;">
        <h1 style="font-size: 28px; color: #3B82F6; margin-bottom: 8px;">💪 Plano de Treino LAF</h1>
        <p style="color: #6b7280; font-size: 14px;">Gerado em ${today}</p>
      </div>

      <!-- User Info -->
      <div style="background: #f9fafb; border-radius: 12px; padding: 20px; margin-bottom: 30px; border: 1px solid #e5e7eb;">
        <h2 style="font-size: 18px; margin-bottom: 12px; color: #111827;">👤 Informações</h2>
        <p style="font-size: 14px; color: #374151;"><strong>Atleta:</strong> ${profile.name}</p>
        <p style="font-size: 14px; color: #374151; margin-top: 6px;"><strong>Total de Treinos:</strong> ${workout.workout_plan.length} por semana</p>
      </div>

      <!-- Workouts -->
      <h2 style="font-size: 20px; margin-bottom: 20px; color: #111827;">📋 Treinos da Semana</h2>
      ${workoutsHTML}

      <!-- Tips -->
      <div style="background: #FEF3C7; border-radius: 12px; padding: 16px; margin-top: 20px; border: 1px solid #FCD34D;">
        <h3 style="font-size: 14px; color: #92400E; margin-bottom: 8px;">💡 Dicas Importantes</h3>
        <ul style="font-size: 12px; color: #78350F; padding-left: 20px;">
          <li style="margin-bottom: 4px;">Sempre faça aquecimento de 5-10 minutos antes de iniciar</li>
          <li style="margin-bottom: 4px;">Mantenha-se hidratado durante todo o treino</li>
          <li style="margin-bottom: 4px;">Respeite o tempo de descanso entre as séries</li>
          <li>Se sentir dor aguda, pare o exercício imediatamente</li>
        </ul>
      </div>

      <!-- Footer -->
      <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
        <p style="color: #9ca3af; font-size: 12px;">Gerado pelo app LAF - Seu assistente de dieta e treino</p>
        <p style="color: #9ca3af; font-size: 11px; margin-top: 4px;">© ${new Date().getFullYear()} LAF App</p>
      </div>
    </body>
    </html>
  `;
}

class PDFExportService {
  /**
   * Exporta a dieta como PDF
   */
  async exportDietPDF(diet: DietPlan, profile: UserProfile): Promise<boolean> {
    try {
      const html = generateDietHTML(diet, profile);
      
      const { uri } = await Print.printToFileAsync({
        html,
        base64: false,
      });

      // Renomeia o arquivo para ter um nome mais amigável
      const newUri = `${FileSystem.documentDirectory}LAF_Dieta_${profile.name.replace(/\s/g, '_')}.pdf`;
      
      try {
        await FileSystem.moveAsync({ from: uri, to: newUri });
      } catch {
        // Se falhar ao mover, usa o URI original
        return await this.sharePDF(uri);
      }

      return await this.sharePDF(newUri);
    } catch (error) {
      console.error('Erro ao exportar dieta PDF:', error);
      throw error;
    }
  }

  /**
   * Exporta o treino como PDF
   */
  async exportWorkoutPDF(workout: WorkoutPlan, profile: UserProfile): Promise<boolean> {
    try {
      const html = generateWorkoutHTML(workout, profile);
      
      const { uri } = await Print.printToFileAsync({
        html,
        base64: false,
      });

      // Renomeia o arquivo
      const newUri = `${FileSystem.documentDirectory}LAF_Treino_${profile.name.replace(/\s/g, '_')}.pdf`;
      
      try {
        await FileSystem.moveAsync({ from: uri, to: newUri });
      } catch {
        return await this.sharePDF(uri);
      }

      return await this.sharePDF(newUri);
    } catch (error) {
      console.error('Erro ao exportar treino PDF:', error);
      throw error;
    }
  }

  /**
   * Compartilha o PDF gerado
   */
  private async sharePDF(uri: string): Promise<boolean> {
    try {
      const isAvailable = await Sharing.isAvailableAsync();
      
      if (!isAvailable) {
        console.log('Compartilhamento não disponível nesta plataforma');
        return false;
      }

      await Sharing.shareAsync(uri, {
        mimeType: 'application/pdf',
        dialogTitle: 'Compartilhar PDF',
        UTI: 'com.adobe.pdf',
      });

      return true;
    } catch (error) {
      console.error('Erro ao compartilhar PDF:', error);
      throw error;
    }
  }

  /**
   * Imprime a dieta diretamente
   */
  async printDiet(diet: DietPlan, profile: UserProfile): Promise<void> {
    try {
      const html = generateDietHTML(diet, profile);
      await Print.printAsync({ html });
    } catch (error) {
      console.error('Erro ao imprimir dieta:', error);
      throw error;
    }
  }

  /**
   * Imprime o treino diretamente
   */
  async printWorkout(workout: WorkoutPlan, profile: UserProfile): Promise<void> {
    try {
      const html = generateWorkoutHTML(workout, profile);
      await Print.printAsync({ html });
    } catch (error) {
      console.error('Erro ao imprimir treino:', error);
      throw error;
    }
  }
}

// Exporta instância única
export const pdfExportService = new PDFExportService();
