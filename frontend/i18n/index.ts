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
  
  if (dayName in dayTranslations) {
    return dayTranslations[dayName][language] || dayName;
  }
  
  return dayName;
}
