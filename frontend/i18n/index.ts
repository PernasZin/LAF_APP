/**
 * i18n - Internationalization System for LAF App
 * Re-exports from translations.ts for backwards compatibility
 */

// Export everything from the main translations file
export * from './translations';

// Export the useTranslation hook
export * from './useTranslation';

// Helper functions for translating specific content

import { translations, SupportedLanguage } from './translations';

/**
 * Translate food name based on language
 * Takes food name (in Portuguese) and returns translated name
 */
export function translateFood(foodName: string, language: SupportedLanguage): string {
  // Food translations mapping (Portuguese -> Other languages)
  const foodTranslations: Record<string, Record<SupportedLanguage, string>> = {
    // Proteínas
    'Peito de Frango': { 'pt-BR': 'Peito de Frango', 'en-US': 'Chicken Breast', 'es-ES': 'Pechuga de Pollo' },
    'Coxa de Frango': { 'pt-BR': 'Coxa de Frango', 'en-US': 'Chicken Thigh', 'es-ES': 'Muslo de Pollo' },
    'Patinho (Carne Magra)': { 'pt-BR': 'Patinho (Carne Magra)', 'en-US': 'Lean Beef', 'es-ES': 'Carne Magra' },
    'Carne Moída': { 'pt-BR': 'Carne Moída', 'en-US': 'Ground Beef', 'es-ES': 'Carne Molida' },
    'Carne Suína': { 'pt-BR': 'Carne Suína', 'en-US': 'Pork', 'es-ES': 'Cerdo' },
    'Ovos Inteiros': { 'pt-BR': 'Ovos Inteiros', 'en-US': 'Whole Eggs', 'es-ES': 'Huevos Enteros' },
    'Claras de Ovo': { 'pt-BR': 'Claras de Ovo', 'en-US': 'Egg Whites', 'es-ES': 'Claras de Huevo' },
    'Tilápia': { 'pt-BR': 'Tilápia', 'en-US': 'Tilapia', 'es-ES': 'Tilapia' },
    'Atum': { 'pt-BR': 'Atum', 'en-US': 'Tuna', 'es-ES': 'Atún' },
    'Salmão': { 'pt-BR': 'Salmão', 'en-US': 'Salmon', 'es-ES': 'Salmón' },
    'Camarão': { 'pt-BR': 'Camarão', 'en-US': 'Shrimp', 'es-ES': 'Camarón' },
    'Sardinha': { 'pt-BR': 'Sardinha', 'en-US': 'Sardines', 'es-ES': 'Sardinas' },
    'Peru': { 'pt-BR': 'Peru', 'en-US': 'Turkey', 'es-ES': 'Pavo' },
    'Queijo Cottage': { 'pt-BR': 'Queijo Cottage', 'en-US': 'Cottage Cheese', 'es-ES': 'Queso Cottage' },
    'Iogurte Zero': { 'pt-BR': 'Iogurte Zero', 'en-US': 'Sugar-Free Yogurt', 'es-ES': 'Yogur Sin Azúcar' },
    'Whey Protein': { 'pt-BR': 'Whey Protein', 'en-US': 'Whey Protein', 'es-ES': 'Proteína Whey' },
    'Requeijão Light': { 'pt-BR': 'Requeijão Light', 'en-US': 'Light Cream Cheese', 'es-ES': 'Queso Crema Light' },
    'Tofu': { 'pt-BR': 'Tofu', 'en-US': 'Tofu', 'es-ES': 'Tofu' },
    'Tempeh': { 'pt-BR': 'Tempeh', 'en-US': 'Tempeh', 'es-ES': 'Tempeh' },
    'Seitan': { 'pt-BR': 'Seitan', 'en-US': 'Seitan', 'es-ES': 'Seitán' },
    'Edamame': { 'pt-BR': 'Edamame', 'en-US': 'Edamame', 'es-ES': 'Edamame' },
    'Grão de Bico': { 'pt-BR': 'Grão de Bico', 'en-US': 'Chickpeas', 'es-ES': 'Garbanzos' },
    'Proteína de Ervilha': { 'pt-BR': 'Proteína de Ervilha', 'en-US': 'Pea Protein', 'es-ES': 'Proteína de Guisante' },
    
    // Carboidratos
    'Arroz Branco': { 'pt-BR': 'Arroz Branco', 'en-US': 'White Rice', 'es-ES': 'Arroz Blanco' },
    'Arroz Integral': { 'pt-BR': 'Arroz Integral', 'en-US': 'Brown Rice', 'es-ES': 'Arroz Integral' },
    'Batata Doce': { 'pt-BR': 'Batata Doce', 'en-US': 'Sweet Potato', 'es-ES': 'Batata' },
    'Aveia': { 'pt-BR': 'Aveia', 'en-US': 'Oats', 'es-ES': 'Avena' },
    'Macarrão': { 'pt-BR': 'Macarrão', 'en-US': 'Pasta', 'es-ES': 'Pasta' },
    'Macarrão Integral': { 'pt-BR': 'Macarrão Integral', 'en-US': 'Whole Wheat Pasta', 'es-ES': 'Pasta Integral' },
    'Pão Francês': { 'pt-BR': 'Pão Francês', 'en-US': 'French Bread', 'es-ES': 'Pan Francés' },
    'Pão Integral': { 'pt-BR': 'Pão Integral', 'en-US': 'Whole Wheat Bread', 'es-ES': 'Pan Integral' },
    'Pão de Forma': { 'pt-BR': 'Pão de Forma', 'en-US': 'Sliced Bread', 'es-ES': 'Pan de Molde' },
    'Tapioca': { 'pt-BR': 'Tapioca', 'en-US': 'Tapioca', 'es-ES': 'Tapioca' },
    'Feijão': { 'pt-BR': 'Feijão', 'en-US': 'Beans', 'es-ES': 'Frijoles' },
    'Lentilha': { 'pt-BR': 'Lentilha', 'en-US': 'Lentils', 'es-ES': 'Lentejas' },
    'Farofa': { 'pt-BR': 'Farofa', 'en-US': 'Toasted Cassava Flour', 'es-ES': 'Farofa' },
    'Granola': { 'pt-BR': 'Granola', 'en-US': 'Granola', 'es-ES': 'Granola' },
    
    // Gorduras
    'Azeite de Oliva': { 'pt-BR': 'Azeite de Oliva', 'en-US': 'Olive Oil', 'es-ES': 'Aceite de Oliva' },
    'Pasta de Amendoim': { 'pt-BR': 'Pasta de Amendoim', 'en-US': 'Peanut Butter', 'es-ES': 'Mantequilla de Maní' },
    'Pasta de Amêndoa': { 'pt-BR': 'Pasta de Amêndoa', 'en-US': 'Almond Butter', 'es-ES': 'Mantequilla de Almendra' },
    'Óleo de Coco': { 'pt-BR': 'Óleo de Coco', 'en-US': 'Coconut Oil', 'es-ES': 'Aceite de Coco' },
    'Castanhas': { 'pt-BR': 'Castanhas', 'en-US': 'Cashews', 'es-ES': 'Castañas de Cajú' },
    'Amêndoas': { 'pt-BR': 'Amêndoas', 'en-US': 'Almonds', 'es-ES': 'Almendras' },
    'Nozes': { 'pt-BR': 'Nozes', 'en-US': 'Walnuts', 'es-ES': 'Nueces' },
    'Chia': { 'pt-BR': 'Chia', 'en-US': 'Chia Seeds', 'es-ES': 'Semillas de Chía' },
    'Queijo': { 'pt-BR': 'Queijo', 'en-US': 'Cheese', 'es-ES': 'Queso' },
    
    // Frutas
    'Banana': { 'pt-BR': 'Banana', 'en-US': 'Banana', 'es-ES': 'Plátano' },
    'Maçã': { 'pt-BR': 'Maçã', 'en-US': 'Apple', 'es-ES': 'Manzana' },
    'Laranja': { 'pt-BR': 'Laranja', 'en-US': 'Orange', 'es-ES': 'Naranja' },
    'Morango': { 'pt-BR': 'Morango', 'en-US': 'Strawberry', 'es-ES': 'Fresa' },
    'Mamão': { 'pt-BR': 'Mamão', 'en-US': 'Papaya', 'es-ES': 'Papaya' },
    'Manga': { 'pt-BR': 'Manga', 'en-US': 'Mango', 'es-ES': 'Mango' },
    'Melancia': { 'pt-BR': 'Melancia', 'en-US': 'Watermelon', 'es-ES': 'Sandía' },
    'Abacate': { 'pt-BR': 'Abacate', 'en-US': 'Avocado', 'es-ES': 'Aguacate' },
    'Uva': { 'pt-BR': 'Uva', 'en-US': 'Grapes', 'es-ES': 'Uvas' },
    'Abacaxi': { 'pt-BR': 'Abacaxi', 'en-US': 'Pineapple', 'es-ES': 'Piña' },
    'Melão': { 'pt-BR': 'Melão', 'en-US': 'Melon', 'es-ES': 'Melón' },
    'Kiwi': { 'pt-BR': 'Kiwi', 'en-US': 'Kiwi', 'es-ES': 'Kiwi' },
    'Pera': { 'pt-BR': 'Pera', 'en-US': 'Pear', 'es-ES': 'Pera' },
    'Pêssego': { 'pt-BR': 'Pêssego', 'en-US': 'Peach', 'es-ES': 'Durazno' },
    'Mirtilo': { 'pt-BR': 'Mirtilo', 'en-US': 'Blueberry', 'es-ES': 'Arándano' },
    'Açaí': { 'pt-BR': 'Açaí', 'en-US': 'Açaí', 'es-ES': 'Açaí' },
    
    // Vegetais
    'Salada Verde': { 'pt-BR': 'Salada Verde', 'en-US': 'Green Salad', 'es-ES': 'Ensalada Verde' },
    'Alface': { 'pt-BR': 'Alface', 'en-US': 'Lettuce', 'es-ES': 'Lechuga' },
    'Rúcula': { 'pt-BR': 'Rúcula', 'en-US': 'Arugula', 'es-ES': 'Rúcula' },
    'Espinafre': { 'pt-BR': 'Espinafre', 'en-US': 'Spinach', 'es-ES': 'Espinaca' },
    'Couve': { 'pt-BR': 'Couve', 'en-US': 'Kale', 'es-ES': 'Col Rizada' },
    'Brócolis': { 'pt-BR': 'Brócolis', 'en-US': 'Broccoli', 'es-ES': 'Brócoli' },
    'Couve-flor': { 'pt-BR': 'Couve-flor', 'en-US': 'Cauliflower', 'es-ES': 'Coliflor' },
    'Cenoura': { 'pt-BR': 'Cenoura', 'en-US': 'Carrot', 'es-ES': 'Zanahoria' },
    'Abobrinha': { 'pt-BR': 'Abobrinha', 'en-US': 'Zucchini', 'es-ES': 'Calabacín' },
    'Pepino': { 'pt-BR': 'Pepino', 'en-US': 'Cucumber', 'es-ES': 'Pepino' },
    'Tomate': { 'pt-BR': 'Tomate', 'en-US': 'Tomato', 'es-ES': 'Tomate' },
    'Beterraba': { 'pt-BR': 'Beterraba', 'en-US': 'Beet', 'es-ES': 'Remolacha' },
    'Vagem': { 'pt-BR': 'Vagem', 'en-US': 'Green Beans', 'es-ES': 'Judías Verdes' },
    'Pimentão': { 'pt-BR': 'Pimentão', 'en-US': 'Bell Pepper', 'es-ES': 'Pimiento' },
    
    // Extras
    'Leite Condensado': { 'pt-BR': 'Leite Condensado', 'en-US': 'Condensed Milk', 'es-ES': 'Leche Condensada' },
    'Mel': { 'pt-BR': 'Mel', 'en-US': 'Honey', 'es-ES': 'Miel' },
  };
  
  if (foodName in foodTranslations) {
    return foodTranslations[foodName][language] || foodName;
  }
  
  return foodName;
}

/**
 * Translate meal name based on language
 */
export function translateMealName(mealName: string, language: SupportedLanguage): string {
  const mealKey = mealName.toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, '_');
  
  const mealTranslations: Record<string, Record<SupportedLanguage, string>> = {
    'cafe_da_manha': { 'pt-BR': 'Café da Manhã', 'en-US': 'Breakfast', 'es-ES': 'Desayuno' },
    'lanche_da_manha': { 'pt-BR': 'Lanche da Manhã', 'en-US': 'Morning Snack', 'es-ES': 'Merienda Mañana' },
    'lanche_manha': { 'pt-BR': 'Lanche Manhã', 'en-US': 'Morning Snack', 'es-ES': 'Merienda Mañana' },
    'almoco': { 'pt-BR': 'Almoço', 'en-US': 'Lunch', 'es-ES': 'Almuerzo' },
    'lanche_da_tarde': { 'pt-BR': 'Lanche da Tarde', 'en-US': 'Afternoon Snack', 'es-ES': 'Merienda Tarde' },
    'lanche_tarde': { 'pt-BR': 'Lanche Tarde', 'en-US': 'Afternoon Snack', 'es-ES': 'Merienda Tarde' },
    'jantar': { 'pt-BR': 'Jantar', 'en-US': 'Dinner', 'es-ES': 'Cena' },
    'ceia': { 'pt-BR': 'Ceia', 'en-US': 'Evening Snack', 'es-ES': 'Cena Ligera' },
  };
  
  if (mealKey in mealTranslations) {
    return mealTranslations[mealKey][language] || mealName;
  }
  
  return mealName;
}

/**
 * Translate exercise name based on language
 */
export function translateExercise(exerciseName: string, language: SupportedLanguage): string {
  const exerciseTranslations: Record<string, Record<SupportedLanguage, string>> = {
    'Supino Reto na Máquina': { 'pt-BR': 'Supino Reto na Máquina', 'en-US': 'Machine Flat Bench Press', 'es-ES': 'Press de Banca Plano en Máquina' },
    'Supino Inclinado na Máquina': { 'pt-BR': 'Supino Inclinado na Máquina', 'en-US': 'Machine Incline Bench Press', 'es-ES': 'Press Inclinado en Máquina' },
    'Crucifixo na Máquina (Peck Deck)': { 'pt-BR': 'Crucifixo na Máquina (Peck Deck)', 'en-US': 'Pec Deck Machine Fly', 'es-ES': 'Aperturas en Máquina (Pec Deck)' },
    'Cross Over Polia Alta': { 'pt-BR': 'Cross Over Polia Alta', 'en-US': 'High Cable Crossover', 'es-ES': 'Cruce de Cables Alto' },
    'Puxada Frontal Pegada Aberta': { 'pt-BR': 'Puxada Frontal Pegada Aberta', 'en-US': 'Wide Grip Lat Pulldown', 'es-ES': 'Jalón al Pecho Agarre Ancho' },
    'Puxada Pegada Neutra (Triângulo)': { 'pt-BR': 'Puxada Pegada Neutra (Triângulo)', 'en-US': 'Neutral Grip Lat Pulldown', 'es-ES': 'Jalón Agarre Neutro (Triángulo)' },
    'Remada Máquina Pegada Neutra': { 'pt-BR': 'Remada Máquina Pegada Neutra', 'en-US': 'Machine Row Neutral Grip', 'es-ES': 'Remo en Máquina Agarre Neutro' },
    'Remada Baixa Polia (Triângulo)': { 'pt-BR': 'Remada Baixa Polia (Triângulo)', 'en-US': 'Seated Cable Row', 'es-ES': 'Remo Bajo en Polea' },
    'Desenvolvimento Máquina': { 'pt-BR': 'Desenvolvimento Máquina', 'en-US': 'Machine Shoulder Press', 'es-ES': 'Press de Hombros en Máquina' },
    'Elevação Lateral Máquina': { 'pt-BR': 'Elevação Lateral Máquina', 'en-US': 'Machine Lateral Raise', 'es-ES': 'Elevaciones Laterales en Máquina' },
    'Elevação Lateral Halteres': { 'pt-BR': 'Elevação Lateral Halteres', 'en-US': 'Dumbbell Lateral Raise', 'es-ES': 'Elevaciones Laterales con Mancuernas' },
    'Rosca Direta Barra': { 'pt-BR': 'Rosca Direta Barra', 'en-US': 'Barbell Curl', 'es-ES': 'Curl con Barra' },
    'Rosca Martelo Halteres': { 'pt-BR': 'Rosca Martelo Halteres', 'en-US': 'Hammer Curl', 'es-ES': 'Curl Martillo' },
    'Rosca Alternada Halteres': { 'pt-BR': 'Rosca Alternada Halteres', 'en-US': 'Alternating Dumbbell Curl', 'es-ES': 'Curl Alternado con Mancuernas' },
    'Rosca Scott Máquina': { 'pt-BR': 'Rosca Scott Máquina', 'en-US': 'Preacher Curl Machine', 'es-ES': 'Curl Scott en Máquina' },
    'Tríceps Corda (Polia Alta)': { 'pt-BR': 'Tríceps Corda (Polia Alta)', 'en-US': 'Cable Rope Tricep Pushdown', 'es-ES': 'Extensiones de Tríceps con Cuerda' },
    'Tríceps Francês Halter': { 'pt-BR': 'Tríceps Francês Halter', 'en-US': 'Dumbbell French Press', 'es-ES': 'Press Francés con Mancuerna' },
    'Tríceps Barra Reta (Polia Alta)': { 'pt-BR': 'Tríceps Barra Reta (Polia Alta)', 'en-US': 'Cable Bar Tricep Pushdown', 'es-ES': 'Extensiones de Tríceps con Barra' },
    'Tríceps Máquina': { 'pt-BR': 'Tríceps Máquina', 'en-US': 'Tricep Machine', 'es-ES': 'Tríceps en Máquina' },
    'Leg Press 45°': { 'pt-BR': 'Leg Press 45°', 'en-US': '45° Leg Press', 'es-ES': 'Prensa de Piernas 45°' },
    'Cadeira Extensora': { 'pt-BR': 'Cadeira Extensora', 'en-US': 'Leg Extension Machine', 'es-ES': 'Extensión de Piernas' },
    'Agachamento no Smith Machine': { 'pt-BR': 'Agachamento no Smith Machine', 'en-US': 'Smith Machine Squat', 'es-ES': 'Sentadilla en Máquina Smith' },
    'Mesa Flexora': { 'pt-BR': 'Mesa Flexora', 'en-US': 'Lying Leg Curl', 'es-ES': 'Curl Femoral Acostado' },
    'Cadeira Flexora (Sentado)': { 'pt-BR': 'Cadeira Flexora (Sentado)', 'en-US': 'Seated Leg Curl', 'es-ES': 'Curl Femoral Sentado' },
    'Stiff na Máquina Smith': { 'pt-BR': 'Stiff na Máquina Smith', 'en-US': 'Smith Machine Stiff Leg Deadlift', 'es-ES': 'Peso Muerto Rumano en Smith' },
    'Glúteo na Máquina (Kick Back)': { 'pt-BR': 'Glúteo na Máquina (Kick Back)', 'en-US': 'Glute Kickback Machine', 'es-ES': 'Glúteos en Máquina' },
    'Panturrilha no Leg Press': { 'pt-BR': 'Panturrilha no Leg Press', 'en-US': 'Calf Press on Leg Press', 'es-ES': 'Gemelos en Prensa' },
    'Panturrilha Sentado na Máquina': { 'pt-BR': 'Panturrilha Sentado na Máquina', 'en-US': 'Seated Calf Raise Machine', 'es-ES': 'Gemelos Sentado en Máquina' },
    'Panturrilha em Pé na Máquina': { 'pt-BR': 'Panturrilha em Pé na Máquina', 'en-US': 'Standing Calf Raise Machine', 'es-ES': 'Gemelos de Pie en Máquina' },
    'Abdominal na Máquina': { 'pt-BR': 'Abdominal na Máquina', 'en-US': 'Ab Machine Crunch', 'es-ES': 'Abdominales en Máquina' },
    'Abdominal na Polia Alta (Corda)': { 'pt-BR': 'Abdominal na Polia Alta (Corda)', 'en-US': 'Cable Crunch', 'es-ES': 'Abdominales en Polea Alta' },
    'Prancha Isométrica': { 'pt-BR': 'Prancha Isométrica', 'en-US': 'Plank Hold', 'es-ES': 'Plancha Isométrica' },
    'Voador Invertido (Peck Deck)': { 'pt-BR': 'Voador Invertido (Peck Deck)', 'en-US': 'Reverse Pec Deck Fly', 'es-ES': 'Aperturas Invertidas (Pec Deck)' },
  };
  
  if (exerciseName in exerciseTranslations) {
    return exerciseTranslations[exerciseName][language] || exerciseName;
  }
  
  return exerciseName;
}

/**
 * Translate workout day name based on language
 */
export function translateWorkoutName(dayName: string, language: SupportedLanguage): string {
  const dayTranslations: Record<string, Record<SupportedLanguage, string>> = {
    'Full Body': { 'pt-BR': 'Corpo Inteiro', 'en-US': 'Full Body', 'es-ES': 'Cuerpo Completo' },
    'Upper': { 'pt-BR': 'Superior', 'en-US': 'Upper Body', 'es-ES': 'Tren Superior' },
    'Lower': { 'pt-BR': 'Inferior', 'en-US': 'Lower Body', 'es-ES': 'Tren Inferior' },
    'A - Push': { 'pt-BR': 'A - Empurrar', 'en-US': 'A - Push', 'es-ES': 'A - Empuje' },
    'B - Pull': { 'pt-BR': 'B - Puxar', 'en-US': 'B - Pull', 'es-ES': 'B - Jalón' },
    'C - Legs': { 'pt-BR': 'C - Pernas', 'en-US': 'C - Legs', 'es-ES': 'C - Piernas' },
    'A - Peito/Tríceps': { 'pt-BR': 'A - Peito/Tríceps', 'en-US': 'A - Chest/Triceps', 'es-ES': 'A - Pecho/Tríceps' },
    'B - Costas/Bíceps': { 'pt-BR': 'B - Costas/Bíceps', 'en-US': 'B - Back/Biceps', 'es-ES': 'B - Espalda/Bíceps' },
    'C - Pernas': { 'pt-BR': 'C - Pernas', 'en-US': 'C - Legs', 'es-ES': 'C - Piernas' },
    'D - Ombros/Abdômen': { 'pt-BR': 'D - Ombros/Abdômen', 'en-US': 'D - Shoulders/Abs', 'es-ES': 'D - Hombros/Abdominales' },
  };
  
  // Handle [Adaptação] prefix
  let translated = dayName;
  if (translated.includes('[Adaptação]')) {
    const adaptationText: Record<SupportedLanguage, string> = {
      'pt-BR': '[Adaptação]',
      'en-US': '[Adaptation]',
      'es-ES': '[Adaptación]'
    };
    translated = translated.replace('[Adaptação]', adaptationText[language]);
  }
  
  // Translate the workout name part
  for (const [key, translations] of Object.entries(dayTranslations)) {
    if (translated.includes(key)) {
      translated = translated.replace(key, translations[language]);
    }
  }
  
  return translated;
}

/**
 * Translate workout notes based on language
 */
export function translateWorkoutNotes(notes: string, language: SupportedLanguage): string {
  if (!notes) return '';
  
  const notesTranslations: Record<string, Record<SupportedLanguage, string>> = {
    // Adaptation phase
    '🔰 FASE DE ADAPTAÇÃO': { 'pt-BR': '🔰 FASE DE ADAPTAÇÃO', 'en-US': '🔰 ADAPTATION PHASE', 'es-ES': '🔰 FASE DE ADAPTACIÓN' },
    'treinos restantes': { 'pt-BR': 'treinos restantes', 'en-US': 'workouts remaining', 'es-ES': 'entrenos restantes' },
    'ADAPTAÇÃO': { 'pt-BR': 'ADAPTAÇÃO', 'en-US': 'ADAPTATION', 'es-ES': 'ADAPTACIÓN' },
    'Adaptação': { 'pt-BR': 'Adaptação', 'en-US': 'Adaptation', 'es-ES': 'Adaptación' },
    '⚠️ ADAPTAÇÃO - CARGA LEVE!': { 'pt-BR': '⚠️ ADAPTAÇÃO - CARGA LEVE!', 'en-US': '⚠️ ADAPTATION - LIGHT WEIGHT!', 'es-ES': '⚠️ ADAPTACIÓN - ¡CARGA LIGERA!' },
    'FASE DE ADAPTAÇÃO: Técnica acima de carga.': { 'pt-BR': 'FASE DE ADAPTAÇÃO: Técnica acima de carga.', 'en-US': 'ADAPTATION PHASE: Technique over weight.', 'es-ES': 'FASE DE ADAPTACIÓN: Técnica sobre carga.' },
    'Use carga LEVE! Foco 100% na execução correta.': { 'pt-BR': 'Use carga LEVE! Foco 100% na execução correta.', 'en-US': 'Use LIGHT weight! 100% focus on proper form.', 'es-ES': '¡Use carga LIGERA! 100% enfoque en la ejecución correcta.' },
    // Days
    '/semana': { 'pt-BR': '/semana', 'en-US': '/week', 'es-ES': '/semana' },
  };
  
  let translated = notes;
  for (const [key, translations] of Object.entries(notesTranslations)) {
    if (translated.includes(key)) {
      translated = translated.replace(new RegExp(key, 'g'), translations[language]);
    }
  }
  
  return translated;
}

/**
 * Translate exercise focus (muscle target) based on language
 */
export function translateExerciseFocus(focus: string, language: SupportedLanguage): string {
  const focusTranslations: Record<string, Record<SupportedLanguage, string>> = {
    // Chest
    'Peitoral Médio': { 'pt-BR': 'Peitoral Médio', 'en-US': 'Mid Chest', 'es-ES': 'Pectoral Medio' },
    'Peitoral Médio - Adução': { 'pt-BR': 'Peitoral Médio - Adução', 'en-US': 'Mid Chest - Adduction', 'es-ES': 'Pectoral Medio - Aducción' },
    'Peitoral Superior': { 'pt-BR': 'Peitoral Superior', 'en-US': 'Upper Chest', 'es-ES': 'Pectoral Superior' },
    'Peitoral Inferior': { 'pt-BR': 'Peitoral Inferior', 'en-US': 'Lower Chest', 'es-ES': 'Pectoral Inferior' },
    'Peito': { 'pt-BR': 'Peito', 'en-US': 'Chest', 'es-ES': 'Pecho' },
    // Back
    'Dorsal': { 'pt-BR': 'Dorsal', 'en-US': 'Lats', 'es-ES': 'Dorsales' },
    'Dorsais': { 'pt-BR': 'Dorsais', 'en-US': 'Lats', 'es-ES': 'Dorsales' },
    'Dorsal (Largura)': { 'pt-BR': 'Dorsal (Largura)', 'en-US': 'Lats (Width)', 'es-ES': 'Dorsal (Ancho)' },
    'Dorsal (Espessura)': { 'pt-BR': 'Dorsal (Espessura)', 'en-US': 'Lats (Thickness)', 'es-ES': 'Dorsal (Grosor)' },
    'Dorsal Médio (Espessura)': { 'pt-BR': 'Dorsal Médio (Espessura)', 'en-US': 'Mid Lats (Thickness)', 'es-ES': 'Dorsal Medio (Grosor)' },
    'Dorsal Inferior': { 'pt-BR': 'Dorsal Inferior', 'en-US': 'Lower Lats', 'es-ES': 'Dorsal Inferior' },
    'Costas Média': { 'pt-BR': 'Costas Média', 'en-US': 'Mid Back', 'es-ES': 'Espalda Media' },
    'Costas Superior': { 'pt-BR': 'Costas Superior', 'en-US': 'Upper Back', 'es-ES': 'Espalda Superior' },
    'Costas Inferior': { 'pt-BR': 'Costas Inferior', 'en-US': 'Lower Back', 'es-ES': 'Espalda Baja' },
    'Trapézio': { 'pt-BR': 'Trapézio', 'en-US': 'Traps', 'es-ES': 'Trapecios' },
    'Trapézio Superior': { 'pt-BR': 'Trapézio Superior', 'en-US': 'Upper Traps', 'es-ES': 'Trapecios Superiores' },
    'Trapézio Médio': { 'pt-BR': 'Trapézio Médio', 'en-US': 'Mid Traps', 'es-ES': 'Trapecios Medios' },
    'Trapézio/Romboides': { 'pt-BR': 'Trapézio/Romboides', 'en-US': 'Traps/Rhomboids', 'es-ES': 'Trapecios/Romboides' },
    'Lombar': { 'pt-BR': 'Lombar', 'en-US': 'Lower Back', 'es-ES': 'Lumbar' },
    'Romboides': { 'pt-BR': 'Romboides', 'en-US': 'Rhomboids', 'es-ES': 'Romboides' },
    // Shoulders
    'Deltóide Anterior': { 'pt-BR': 'Deltóide Anterior', 'en-US': 'Front Delt', 'es-ES': 'Deltoides Anterior' },
    'Deltóide Anterior/Médio': { 'pt-BR': 'Deltóide Anterior/Médio', 'en-US': 'Front/Side Delt', 'es-ES': 'Deltoides Anterior/Medio' },
    'Deltóide Lateral': { 'pt-BR': 'Deltóide Lateral', 'en-US': 'Side Delt', 'es-ES': 'Deltoides Lateral' },
    'Deltóide Posterior': { 'pt-BR': 'Deltóide Posterior', 'en-US': 'Rear Delt', 'es-ES': 'Deltoides Posterior' },
    'Ombros': { 'pt-BR': 'Ombros', 'en-US': 'Shoulders', 'es-ES': 'Hombros' },
    'Ombro Frontal': { 'pt-BR': 'Ombro Frontal', 'en-US': 'Front Shoulder', 'es-ES': 'Hombro Frontal' },
    // Arms - Biceps
    'Bíceps': { 'pt-BR': 'Bíceps', 'en-US': 'Biceps', 'es-ES': 'Bíceps' },
    'Bíceps Completo': { 'pt-BR': 'Bíceps Completo', 'en-US': 'Full Biceps', 'es-ES': 'Bíceps Completo' },
    'Bíceps (Cabeça Longa)': { 'pt-BR': 'Bíceps (Cabeça Longa)', 'en-US': 'Biceps (Long Head)', 'es-ES': 'Bíceps (Cabeza Larga)' },
    'Bíceps (Cabeça Curta/Pico)': { 'pt-BR': 'Bíceps (Cabeça Curta/Pico)', 'en-US': 'Biceps (Short Head/Peak)', 'es-ES': 'Bíceps (Cabeza Corta/Pico)' },
    'Cabeça Curta': { 'pt-BR': 'Cabeça Curta', 'en-US': 'Short Head', 'es-ES': 'Cabeza Corta' },
    'Cabeça Longa': { 'pt-BR': 'Cabeça Longa', 'en-US': 'Long Head', 'es-ES': 'Cabeza Larga' },
    'Braquial': { 'pt-BR': 'Braquial', 'en-US': 'Brachialis', 'es-ES': 'Braquial' },
    'Braquiorradial': { 'pt-BR': 'Braquiorradial', 'en-US': 'Brachioradialis', 'es-ES': 'Braquiorradial' },
    'Braquial/Braquiorradial': { 'pt-BR': 'Braquial/Braquiorradial', 'en-US': 'Brachialis/Brachioradialis', 'es-ES': 'Braquial/Braquiorradial' },
    // Arms - Triceps
    'Tríceps': { 'pt-BR': 'Tríceps', 'en-US': 'Triceps', 'es-ES': 'Tríceps' },
    'Tríceps Geral': { 'pt-BR': 'Tríceps Geral', 'en-US': 'Full Triceps', 'es-ES': 'Tríceps General' },
    'Tríceps Completo': { 'pt-BR': 'Tríceps Completo', 'en-US': 'Full Triceps', 'es-ES': 'Tríceps Completo' },
    'Cabeça Lateral': { 'pt-BR': 'Cabeça Lateral', 'en-US': 'Lateral Head', 'es-ES': 'Cabeza Lateral' },
    'Cabeça Medial': { 'pt-BR': 'Cabeça Medial', 'en-US': 'Medial Head', 'es-ES': 'Cabeza Medial' },
    // Forearms
    'Antebraço': { 'pt-BR': 'Antebraço', 'en-US': 'Forearm', 'es-ES': 'Antebrazo' },
    'Antebraços': { 'pt-BR': 'Antebraços', 'en-US': 'Forearms', 'es-ES': 'Antebrazos' },
    'Flexores do Punho': { 'pt-BR': 'Flexores do Punho', 'en-US': 'Wrist Flexors', 'es-ES': 'Flexores de Muñeca' },
    'Extensores do Punho': { 'pt-BR': 'Extensores do Punho', 'en-US': 'Wrist Extensors', 'es-ES': 'Extensores de Muñeca' },
    // Legs - Quadriceps
    'Quadríceps': { 'pt-BR': 'Quadríceps', 'en-US': 'Quads', 'es-ES': 'Cuádriceps' },
    'Quadríceps Geral': { 'pt-BR': 'Quadríceps Geral', 'en-US': 'Full Quads', 'es-ES': 'Cuádriceps General' },
    'Vasto Lateral': { 'pt-BR': 'Vasto Lateral', 'en-US': 'Outer Quad', 'es-ES': 'Vasto Lateral' },
    'Vasto Medial': { 'pt-BR': 'Vasto Medial', 'en-US': 'Inner Quad', 'es-ES': 'Vasto Medial' },
    'Reto Femoral': { 'pt-BR': 'Reto Femoral', 'en-US': 'Rectus Femoris', 'es-ES': 'Recto Femoral' },
    // Legs - Hamstrings
    'Posterior': { 'pt-BR': 'Posterior', 'en-US': 'Hamstrings', 'es-ES': 'Isquiotibiales' },
    'Posterior de Coxa': { 'pt-BR': 'Posterior de Coxa', 'en-US': 'Hamstrings', 'es-ES': 'Isquiotibiales' },
    'Isquiotibiais': { 'pt-BR': 'Isquiotibiais', 'en-US': 'Hamstrings', 'es-ES': 'Isquiotibiales' },
    'Bíceps Femoral': { 'pt-BR': 'Bíceps Femoral', 'en-US': 'Bicep Femoris', 'es-ES': 'Bíceps Femoral' },
    // Legs - Glutes
    'Glúteos': { 'pt-BR': 'Glúteos', 'en-US': 'Glutes', 'es-ES': 'Glúteos' },
    'Glúteo Máximo': { 'pt-BR': 'Glúteo Máximo', 'en-US': 'Gluteus Maximus', 'es-ES': 'Glúteo Mayor' },
    'Glúteo Médio': { 'pt-BR': 'Glúteo Médio', 'en-US': 'Gluteus Medius', 'es-ES': 'Glúteo Medio' },
    // Legs - Calves
    'Panturrilha': { 'pt-BR': 'Panturrilha', 'en-US': 'Calves', 'es-ES': 'Gemelos' },
    'Panturrilhas': { 'pt-BR': 'Panturrilhas', 'en-US': 'Calves', 'es-ES': 'Gemelos' },
    'Gastrocnêmio': { 'pt-BR': 'Gastrocnêmio', 'en-US': 'Gastrocnemius', 'es-ES': 'Gastrocnemio' },
    'Sóleo': { 'pt-BR': 'Sóleo', 'en-US': 'Soleus', 'es-ES': 'Sóleo' },
    // Legs - Adductors/Abductors
    'Adutores': { 'pt-BR': 'Adutores', 'en-US': 'Adductors', 'es-ES': 'Aductores' },
    'Abdutores': { 'pt-BR': 'Abdutores', 'en-US': 'Abductors', 'es-ES': 'Abductores' },
    // Core
    'Abdômen': { 'pt-BR': 'Abdômen', 'en-US': 'Abs', 'es-ES': 'Abdominales' },
    'Abdominal': { 'pt-BR': 'Abdominal', 'en-US': 'Abs', 'es-ES': 'Abdominales' },
    'Reto Abdominal': { 'pt-BR': 'Reto Abdominal', 'en-US': 'Rectus Abdominis', 'es-ES': 'Recto Abdominal' },
    'Oblíquos': { 'pt-BR': 'Oblíquos', 'en-US': 'Obliques', 'es-ES': 'Oblicuos' },
    'Oblíquo Externo': { 'pt-BR': 'Oblíquo Externo', 'en-US': 'External Obliques', 'es-ES': 'Oblicuo Externo' },
    'Oblíquo Interno': { 'pt-BR': 'Oblíquo Interno', 'en-US': 'Internal Obliques', 'es-ES': 'Oblicuo Interno' },
    'Core': { 'pt-BR': 'Core', 'en-US': 'Core', 'es-ES': 'Core' },
    'Transverso': { 'pt-BR': 'Transverso', 'en-US': 'Transverse', 'es-ES': 'Transverso' },
    // Full body
    'Corpo Inteiro': { 'pt-BR': 'Corpo Inteiro', 'en-US': 'Full Body', 'es-ES': 'Cuerpo Completo' },
    'Composto': { 'pt-BR': 'Composto', 'en-US': 'Compound', 'es-ES': 'Compuesto' },
  };
  
  if (focus in focusTranslations) {
    return focusTranslations[focus][language] || focus;
  }
  
  return focus;
}

/**
 * Translate food portion units based on language
 */
export function translateFoodPortion(portion: string, language: SupportedLanguage): string {
  if (!portion) return '';
  
  const portionTranslations: Record<string, Record<SupportedLanguage, string>> = {
    // Units - order matters! More specific first
    'unidades grandes': { 'pt-BR': 'unidades grandes', 'en-US': 'large units', 'es-ES': 'unidades grandes' },
    'unidade grande': { 'pt-BR': 'unidade grande', 'en-US': 'large unit', 'es-ES': 'unidad grande' },
    'unidades médias': { 'pt-BR': 'unidades médias', 'en-US': 'medium units', 'es-ES': 'unidades medianas' },
    'unidade média': { 'pt-BR': 'unidade média', 'en-US': 'medium unit', 'es-ES': 'unidad mediana' },
    'unidades pequenas': { 'pt-BR': 'unidades pequenas', 'en-US': 'small units', 'es-ES': 'unidades pequeñas' },
    'unidade pequena': { 'pt-BR': 'unidade pequena', 'en-US': 'small unit', 'es-ES': 'unidad pequeña' },
    'unidades': { 'pt-BR': 'unidades', 'en-US': 'units', 'es-ES': 'unidades' },
    'unidade': { 'pt-BR': 'unidade', 'en-US': 'unit', 'es-ES': 'unidad' },
    // Slices
    'fatias finas': { 'pt-BR': 'fatias finas', 'en-US': 'thin slices', 'es-ES': 'rebanadas finas' },
    'fatia fina': { 'pt-BR': 'fatia fina', 'en-US': 'thin slice', 'es-ES': 'rebanada fina' },
    'fatias grossas': { 'pt-BR': 'fatias grossas', 'en-US': 'thick slices', 'es-ES': 'rebanadas gruesas' },
    'fatia grossa': { 'pt-BR': 'fatia grossa', 'en-US': 'thick slice', 'es-ES': 'rebanada gruesa' },
    'fatias': { 'pt-BR': 'fatias', 'en-US': 'slices', 'es-ES': 'rebanadas' },
    'fatia': { 'pt-BR': 'fatia', 'en-US': 'slice', 'es-ES': 'rebanada' },
    // Scoops/Spoons
    'colheres de sopa': { 'pt-BR': 'colheres de sopa', 'en-US': 'tablespoons', 'es-ES': 'cucharadas' },
    'colher de sopa': { 'pt-BR': 'colher de sopa', 'en-US': 'tablespoon', 'es-ES': 'cucharada' },
    'colheres de chá': { 'pt-BR': 'colheres de chá', 'en-US': 'teaspoons', 'es-ES': 'cucharaditas' },
    'colher de chá': { 'pt-BR': 'colher de chá', 'en-US': 'teaspoon', 'es-ES': 'cucharadita' },
    'colheres': { 'pt-BR': 'colheres', 'en-US': 'spoons', 'es-ES': 'cucharas' },
    'colher': { 'pt-BR': 'colher', 'en-US': 'spoon', 'es-ES': 'cuchara' },
    'scoops': { 'pt-BR': 'scoops', 'en-US': 'scoops', 'es-ES': 'medidas' },
    'scoop': { 'pt-BR': 'scoop', 'en-US': 'scoop', 'es-ES': 'medida' },
    // Cups/Glass
    'copos': { 'pt-BR': 'copos', 'en-US': 'glasses', 'es-ES': 'vasos' },
    'copo': { 'pt-BR': 'copo', 'en-US': 'glass', 'es-ES': 'vaso' },
    'xícaras': { 'pt-BR': 'xícaras', 'en-US': 'cups', 'es-ES': 'tazas' },
    'xícara': { 'pt-BR': 'xícara', 'en-US': 'cup', 'es-ES': 'taza' },
    // Eggs
    'ovos inteiros': { 'pt-BR': 'ovos inteiros', 'en-US': 'whole eggs', 'es-ES': 'huevos enteros' },
    'ovo inteiro': { 'pt-BR': 'ovo inteiro', 'en-US': 'whole egg', 'es-ES': 'huevo entero' },
    'ovos': { 'pt-BR': 'ovos', 'en-US': 'eggs', 'es-ES': 'huevos' },
    'ovo': { 'pt-BR': 'ovo', 'en-US': 'egg', 'es-ES': 'huevo' },
    // Portions
    'porção pequena': { 'pt-BR': 'porção pequena', 'en-US': 'small serving', 'es-ES': 'porción pequeña' },
    'porção média': { 'pt-BR': 'porção média', 'en-US': 'medium serving', 'es-ES': 'porción mediana' },
    'porção grande': { 'pt-BR': 'porção grande', 'en-US': 'large serving', 'es-ES': 'porción grande' },
    'porções': { 'pt-BR': 'porções', 'en-US': 'servings', 'es-ES': 'porciones' },
    'porção': { 'pt-BR': 'porção', 'en-US': 'serving', 'es-ES': 'porción' },
    // Fillets
    'filé médio': { 'pt-BR': 'filé médio', 'en-US': 'medium fillet', 'es-ES': 'filete mediano' },
    'filé grande': { 'pt-BR': 'filé grande', 'en-US': 'large fillet', 'es-ES': 'filete grande' },
    'filés': { 'pt-BR': 'filés', 'en-US': 'fillets', 'es-ES': 'filetes' },
    'filé': { 'pt-BR': 'filé', 'en-US': 'fillet', 'es-ES': 'filete' },
    // Pieces
    'pedaços': { 'pt-BR': 'pedaços', 'en-US': 'pieces', 'es-ES': 'trozos' },
    'pedaço': { 'pt-BR': 'pedaço', 'en-US': 'piece', 'es-ES': 'trozo' },
    // Pots
    'potes': { 'pt-BR': 'potes', 'en-US': 'containers', 'es-ES': 'envases' },
    'pote': { 'pt-BR': 'pote', 'en-US': 'container', 'es-ES': 'envase' },
    // Additional common ones
    'grande': { 'pt-BR': 'grande', 'en-US': 'large', 'es-ES': 'grande' },
    'médio': { 'pt-BR': 'médio', 'en-US': 'medium', 'es-ES': 'mediano' },
    'média': { 'pt-BR': 'média', 'en-US': 'medium', 'es-ES': 'mediana' },
    'pequeno': { 'pt-BR': 'pequeno', 'en-US': 'small', 'es-ES': 'pequeño' },
    'pequena': { 'pt-BR': 'pequena', 'en-US': 'small', 'es-ES': 'pequeña' },
  };
  
  let translated = portion;
  
  // Apply translations in order (more specific first)
  for (const [key, translations] of Object.entries(portionTranslations)) {
    const regex = new RegExp(key, 'gi');
    if (regex.test(translated)) {
      translated = translated.replace(regex, translations[language]);
    }
  }
  
  return translated;
}

/**
 * Translate workout day/muscle group name
 */
export function translateWorkoutDayName(name: string, language: SupportedLanguage): string {
  const dayTranslations: Record<string, Record<SupportedLanguage, string>> = {
    // Muscle groups
    'Peito': { 'pt-BR': 'Peito', 'en-US': 'Chest', 'es-ES': 'Pecho' },
    'Costas': { 'pt-BR': 'Costas', 'en-US': 'Back', 'es-ES': 'Espalda' },
    'Ombros': { 'pt-BR': 'Ombros', 'en-US': 'Shoulders', 'es-ES': 'Hombros' },
    'Pernas': { 'pt-BR': 'Pernas', 'en-US': 'Legs', 'es-ES': 'Piernas' },
    'Bíceps': { 'pt-BR': 'Bíceps', 'en-US': 'Biceps', 'es-ES': 'Bíceps' },
    'Tríceps': { 'pt-BR': 'Tríceps', 'en-US': 'Triceps', 'es-ES': 'Tríceps' },
    'Braços': { 'pt-BR': 'Braços', 'en-US': 'Arms', 'es-ES': 'Brazos' },
    'Abdômen': { 'pt-BR': 'Abdômen', 'en-US': 'Abs', 'es-ES': 'Abdominales' },
    'Glúteos': { 'pt-BR': 'Glúteos', 'en-US': 'Glutes', 'es-ES': 'Glúteos' },
    'Panturrilha': { 'pt-BR': 'Panturrilha', 'en-US': 'Calves', 'es-ES': 'Gemelos' },
    // Combinations
    'Peito e Tríceps': { 'pt-BR': 'Peito e Tríceps', 'en-US': 'Chest & Triceps', 'es-ES': 'Pecho y Tríceps' },
    'Costas e Bíceps': { 'pt-BR': 'Costas e Bíceps', 'en-US': 'Back & Biceps', 'es-ES': 'Espalda y Bíceps' },
    'Ombros e Braços': { 'pt-BR': 'Ombros e Braços', 'en-US': 'Shoulders & Arms', 'es-ES': 'Hombros y Brazos' },
    'Pernas e Glúteos': { 'pt-BR': 'Pernas e Glúteos', 'en-US': 'Legs & Glutes', 'es-ES': 'Piernas y Glúteos' },
    // Workout labels
    'Treino A': { 'pt-BR': 'Treino A', 'en-US': 'Workout A', 'es-ES': 'Entreno A' },
    'Treino B': { 'pt-BR': 'Treino B', 'en-US': 'Workout B', 'es-ES': 'Entreno B' },
    'Treino C': { 'pt-BR': 'Treino C', 'en-US': 'Workout C', 'es-ES': 'Entreno C' },
    'Treino D': { 'pt-BR': 'Treino D', 'en-US': 'Workout D', 'es-ES': 'Entreno D' },
    'Treino E': { 'pt-BR': 'Treino E', 'en-US': 'Workout E', 'es-ES': 'Entreno E' },
    'Treino F': { 'pt-BR': 'Treino F', 'en-US': 'Workout F', 'es-ES': 'Entreno F' },
    // Full day names
    'Treino A - Peito': { 'pt-BR': 'Treino A - Peito', 'en-US': 'Workout A - Chest', 'es-ES': 'Entreno A - Pecho' },
    'Treino B - Costas': { 'pt-BR': 'Treino B - Costas', 'en-US': 'Workout B - Back', 'es-ES': 'Entreno B - Espalda' },
    'Treino C - Pernas': { 'pt-BR': 'Treino C - Pernas', 'en-US': 'Workout C - Legs', 'es-ES': 'Entreno C - Piernas' },
    'Treino D - Ombros': { 'pt-BR': 'Treino D - Ombros', 'en-US': 'Workout D - Shoulders', 'es-ES': 'Entreno D - Hombros' },
    'Treino E - Braços': { 'pt-BR': 'Treino E - Braços', 'en-US': 'Workout E - Arms', 'es-ES': 'Entreno E - Brazos' },
  };
  
  // Exact match
  if (name in dayTranslations) {
    return dayTranslations[name][language];
  }
  
  // Try to translate parts
  let translated = name;
  for (const [key, translations] of Object.entries(dayTranslations)) {
    if (translated.includes(key)) {
      translated = translated.replace(key, translations[language]);
    }
  }
  
  return translated;
}
