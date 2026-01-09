/**
 * i18n - Export central
 */
export { translations, type Translations, type SupportedLanguage } from './translations';
export { useTranslation } from './useTranslation';
export { 
  translateExercise, 
  translateFood, 
  translateMealName, 
  translateWorkoutName,
  translateExerciseNotes,
  exerciseTranslations,
  foodTranslations,
  mealNameTranslations,
  workoutNameTranslations,
} from './dynamicTranslations';
