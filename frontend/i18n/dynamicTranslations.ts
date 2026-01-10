/**
 * Tradução de Dados Dinâmicos - Exercícios, Alimentos, etc.
 * Mapeia os nomes em português para outros idiomas
 */

import { SupportedLanguage } from './translations';

// ==================== EXERCÍCIOS ====================
export const exerciseTranslations: Record<string, Record<SupportedLanguage, string>> = {
  // ============ PEITO - DO BACKEND ============
  'Supino na Máquina': { 'pt-BR': 'Supino na Máquina', 'en-US': 'Chest Press Machine', 'es-ES': 'Press de Pecho en Máquina' },
  'Crucifixo na Máquina (Peck Deck)': { 'pt-BR': 'Crucifixo na Máquina (Peck Deck)', 'en-US': 'Pec Deck Machine (Chest Fly)', 'es-ES': 'Aperturas en Máquina (Pec Deck)' },
  'Cross Over (Polia Alta)': { 'pt-BR': 'Cross Over (Polia Alta)', 'en-US': 'Cable Crossover (High Pulley)', 'es-ES': 'Cruce de Poleas (Polea Alta)' },
  'Supino Inclinado com Halteres': { 'pt-BR': 'Supino Inclinado com Halteres', 'en-US': 'Incline Dumbbell Press', 'es-ES': 'Press Inclinado con Mancuernas' },
  
  // ============ COSTAS - DO BACKEND ============
  'Puxada Frontal (Pulley)': { 'pt-BR': 'Puxada Frontal (Pulley)', 'en-US': 'Lat Pulldown', 'es-ES': 'Jalón al Pecho' },
  'Remada na Máquina (Sentado)': { 'pt-BR': 'Remada na Máquina (Sentado)', 'en-US': 'Seated Machine Row', 'es-ES': 'Remo en Máquina (Sentado)' },
  'Remada Baixa (Polia)': { 'pt-BR': 'Remada Baixa (Polia)', 'en-US': 'Seated Cable Row', 'es-ES': 'Remo Bajo en Polea' },
  'Pulldown com Corda (Polia Alta)': { 'pt-BR': 'Pulldown com Corda (Polia Alta)', 'en-US': 'Rope Pulldown (High Pulley)', 'es-ES': 'Jalón con Cuerda (Polea Alta)' },
  
  // ============ OMBROS - DO BACKEND ============
  'Desenvolvimento na Máquina': { 'pt-BR': 'Desenvolvimento na Máquina', 'en-US': 'Machine Shoulder Press', 'es-ES': 'Press de Hombros en Máquina' },
  'Elevação Lateral na Máquina': { 'pt-BR': 'Elevação Lateral na Máquina', 'en-US': 'Machine Lateral Raise', 'es-ES': 'Elevación Lateral en Máquina' },
  'Elevação Lateral com Halteres (Sentado)': { 'pt-BR': 'Elevação Lateral com Halteres (Sentado)', 'en-US': 'Seated Dumbbell Lateral Raise', 'es-ES': 'Elevación Lateral con Mancuernas (Sentado)' },
  'Face Pull (Polia)': { 'pt-BR': 'Face Pull (Polia)', 'en-US': 'Face Pull (Cable)', 'es-ES': 'Face Pull (Polea)' },
  
  // ============ BÍCEPS - DO BACKEND ============
  'Rosca na Máquina': { 'pt-BR': 'Rosca na Máquina', 'en-US': 'Machine Bicep Curl', 'es-ES': 'Curl de Bíceps en Máquina' },
  'Rosca na Polia Baixa': { 'pt-BR': 'Rosca na Polia Baixa', 'en-US': 'Low Cable Curl', 'es-ES': 'Curl en Polea Baja' },
  'Rosca Alternada com Halteres (Sentado)': { 'pt-BR': 'Rosca Alternada com Halteres (Sentado)', 'en-US': 'Seated Alternating Dumbbell Curl', 'es-ES': 'Curl Alternado con Mancuernas (Sentado)' },
  'Rosca Martelo com Halteres (Sentado)': { 'pt-BR': 'Rosca Martelo com Halteres (Sentado)', 'en-US': 'Seated Hammer Curl', 'es-ES': 'Curl Martillo con Mancuernas (Sentado)' },
  
  // ============ TRÍCEPS - DO BACKEND ============
  'Tríceps na Polia (Corda)': { 'pt-BR': 'Tríceps na Polia (Corda)', 'en-US': 'Rope Tricep Pushdown', 'es-ES': 'Extensión de Tríceps con Cuerda' },
  'Tríceps na Polia (Barra Reta)': { 'pt-BR': 'Tríceps na Polia (Barra Reta)', 'en-US': 'Straight Bar Tricep Pushdown', 'es-ES': 'Extensión de Tríceps con Barra Recta' },
  'Tríceps na Máquina': { 'pt-BR': 'Tríceps na Máquina', 'en-US': 'Machine Tricep Extension', 'es-ES': 'Extensión de Tríceps en Máquina' },
  'Tríceps Francês com Halter (Sentado)': { 'pt-BR': 'Tríceps Francês com Halter (Sentado)', 'en-US': 'Seated Dumbbell French Press', 'es-ES': 'Press Francés con Mancuerna (Sentado)' },
  
  // ============ QUADRÍCEPS - DO BACKEND ============
  'Leg Press 45°': { 'pt-BR': 'Leg Press 45°', 'en-US': '45° Leg Press', 'es-ES': 'Prensa de Piernas 45°' },
  'Cadeira Extensora': { 'pt-BR': 'Cadeira Extensora', 'en-US': 'Leg Extension Machine', 'es-ES': 'Extensión de Piernas' },
  'Agachamento no Smith Machine': { 'pt-BR': 'Agachamento no Smith Machine', 'en-US': 'Smith Machine Squat', 'es-ES': 'Sentadilla en Máquina Smith' },
  'Leg Press Horizontal': { 'pt-BR': 'Leg Press Horizontal', 'en-US': 'Horizontal Leg Press', 'es-ES': 'Prensa de Piernas Horizontal' },
  
  // ============ POSTERIOR DE COXA - DO BACKEND ============
  'Mesa Flexora': { 'pt-BR': 'Mesa Flexora', 'en-US': 'Lying Leg Curl', 'es-ES': 'Curl de Piernas Acostado' },
  'Cadeira Flexora (Sentado)': { 'pt-BR': 'Cadeira Flexora (Sentado)', 'en-US': 'Seated Leg Curl', 'es-ES': 'Curl de Piernas Sentado' },
  'Stiff na Máquina Smith': { 'pt-BR': 'Stiff na Máquina Smith', 'en-US': 'Smith Machine Romanian Deadlift', 'es-ES': 'Peso Muerto Rumano en Smith' },
  'Glúteo na Máquina (Kick Back)': { 'pt-BR': 'Glúteo na Máquina (Kick Back)', 'en-US': 'Glute Kickback Machine', 'es-ES': 'Patada de Glúteo en Máquina' },
  
  // ============ PANTURRILHA - DO BACKEND ============
  'Panturrilha no Leg Press': { 'pt-BR': 'Panturrilha no Leg Press', 'en-US': 'Calf Raise on Leg Press', 'es-ES': 'Elevación de Talones en Prensa' },
  'Panturrilha Sentado na Máquina': { 'pt-BR': 'Panturrilha Sentado na Máquina', 'en-US': 'Seated Calf Raise Machine', 'es-ES': 'Elevación de Talones Sentado' },
  'Panturrilha em Pé na Máquina': { 'pt-BR': 'Panturrilha em Pé na Máquina', 'en-US': 'Standing Calf Raise Machine', 'es-ES': 'Elevación de Talones de Pie' },
  
  // ============ ABDÔMEN - DO BACKEND ============
  'Abdominal na Máquina': { 'pt-BR': 'Abdominal na Máquina', 'en-US': 'Machine Crunch', 'es-ES': 'Crunch en Máquina' },
  'Abdominal na Polia Alta (Corda)': { 'pt-BR': 'Abdominal na Polia Alta (Corda)', 'en-US': 'Cable Crunch (Rope)', 'es-ES': 'Crunch en Polea Alta (Cuerda)' },
  'Prancha Isométrica': { 'pt-BR': 'Prancha Isométrica', 'en-US': 'Isometric Plank', 'es-ES': 'Plancha Isométrica' },
  'Elevação de Pernas no Apoio': { 'pt-BR': 'Elevação de Pernas no Apoio', 'en-US': 'Hanging Leg Raise', 'es-ES': 'Elevación de Piernas en Apoyo' },
  
  // ============ VARIAÇÕES ADICIONAIS ============
  'Supino Reto': { 'pt-BR': 'Supino Reto', 'en-US': 'Flat Bench Press', 'es-ES': 'Press de Banca Plano' },
  'Supino Inclinado': { 'pt-BR': 'Supino Inclinado', 'en-US': 'Incline Bench Press', 'es-ES': 'Press de Banca Inclinado' },
  'Supino Declinado': { 'pt-BR': 'Supino Declinado', 'en-US': 'Decline Bench Press', 'es-ES': 'Press de Banca Declinado' },
  'Supino Máquina': { 'pt-BR': 'Supino Máquina', 'en-US': 'Chest Press Machine', 'es-ES': 'Press de Pecho en Máquina' },
  'Voador': { 'pt-BR': 'Voador', 'en-US': 'Pec Deck Fly', 'es-ES': 'Aperturas en Máquina' },
  'Crucifixo': { 'pt-BR': 'Crucifixo', 'en-US': 'Dumbbell Fly', 'es-ES': 'Aperturas con Mancuernas' },
  'Crucifixo Inclinado': { 'pt-BR': 'Crucifixo Inclinado', 'en-US': 'Incline Dumbbell Fly', 'es-ES': 'Aperturas Inclinadas' },
  'Crucifixo Máquina': { 'pt-BR': 'Crucifixo Máquina', 'en-US': 'Machine Fly', 'es-ES': 'Aperturas en Máquina' },
  'Crossover': { 'pt-BR': 'Crossover', 'en-US': 'Cable Crossover', 'es-ES': 'Cruce de Poleas' },
  'Cross Over': { 'pt-BR': 'Cross Over', 'en-US': 'Cable Crossover', 'es-ES': 'Cruce de Poleas' },
  'Flexão de Braços': { 'pt-BR': 'Flexão de Braços', 'en-US': 'Push-ups', 'es-ES': 'Flexiones' },
  'Flexão': { 'pt-BR': 'Flexão', 'en-US': 'Push-ups', 'es-ES': 'Flexiones' },
  'Peck Deck': { 'pt-BR': 'Peck Deck', 'en-US': 'Pec Deck Machine', 'es-ES': 'Máquina Peck Deck' },
  
  'Puxada Frontal': { 'pt-BR': 'Puxada Frontal', 'en-US': 'Lat Pulldown', 'es-ES': 'Jalón al Pecho' },
  'Puxada Aberta': { 'pt-BR': 'Puxada Aberta', 'en-US': 'Wide Grip Pulldown', 'es-ES': 'Jalón Abierto' },
  'Puxada Fechada': { 'pt-BR': 'Puxada Fechada', 'en-US': 'Close Grip Pulldown', 'es-ES': 'Jalón Cerrado' },
  'Puxada Supinada': { 'pt-BR': 'Puxada Supinada', 'en-US': 'Underhand Pulldown', 'es-ES': 'Jalón Supino' },
  'Remada Curvada': { 'pt-BR': 'Remada Curvada', 'en-US': 'Bent Over Row', 'es-ES': 'Remo Inclinado' },
  'Remada Baixa': { 'pt-BR': 'Remada Baixa', 'en-US': 'Seated Cable Row', 'es-ES': 'Remo Sentado' },
  'Remada na Máquina': { 'pt-BR': 'Remada na Máquina', 'en-US': 'Machine Row', 'es-ES': 'Remo en Máquina' },
  'Remada Unilateral': { 'pt-BR': 'Remada Unilateral', 'en-US': 'One-Arm Dumbbell Row', 'es-ES': 'Remo Unilateral' },
  'Pullover': { 'pt-BR': 'Pullover', 'en-US': 'Pullover', 'es-ES': 'Pullover' },
  'Barra Fixa': { 'pt-BR': 'Barra Fixa', 'en-US': 'Pull-ups', 'es-ES': 'Dominadas' },
  'Levantamento Terra': { 'pt-BR': 'Levantamento Terra', 'en-US': 'Deadlift', 'es-ES': 'Peso Muerto' },
  'Remada Cavalinho': { 'pt-BR': 'Remada Cavalinho', 'en-US': 'T-Bar Row', 'es-ES': 'Remo en T' },
  
  'Desenvolvimento': { 'pt-BR': 'Desenvolvimento', 'en-US': 'Shoulder Press', 'es-ES': 'Press Militar' },
  'Desenvolvimento Máquina': { 'pt-BR': 'Desenvolvimento Máquina', 'en-US': 'Machine Shoulder Press', 'es-ES': 'Press de Hombros en Máquina' },
  'Elevação Lateral': { 'pt-BR': 'Elevação Lateral', 'en-US': 'Lateral Raise', 'es-ES': 'Elevación Lateral' },
  'Elevação Frontal': { 'pt-BR': 'Elevação Frontal', 'en-US': 'Front Raise', 'es-ES': 'Elevación Frontal' },
  'Crucifixo Invertido': { 'pt-BR': 'Crucifixo Invertido', 'en-US': 'Reverse Fly', 'es-ES': 'Pájaro' },
  'Encolhimento': { 'pt-BR': 'Encolhimento', 'en-US': 'Shrugs', 'es-ES': 'Encogimientos' },
  'Face Pull': { 'pt-BR': 'Face Pull', 'en-US': 'Face Pull', 'es-ES': 'Face Pull' },
  
  'Rosca Direta': { 'pt-BR': 'Rosca Direta', 'en-US': 'Barbell Curl', 'es-ES': 'Curl con Barra' },
  'Rosca Alternada': { 'pt-BR': 'Rosca Alternada', 'en-US': 'Alternating Dumbbell Curl', 'es-ES': 'Curl Alternado' },
  'Rosca Martelo': { 'pt-BR': 'Rosca Martelo', 'en-US': 'Hammer Curl', 'es-ES': 'Curl Martillo' },
  'Rosca Scott': { 'pt-BR': 'Rosca Scott', 'en-US': 'Preacher Curl', 'es-ES': 'Curl en Banco Scott' },
  'Rosca Concentrada': { 'pt-BR': 'Rosca Concentrada', 'en-US': 'Concentration Curl', 'es-ES': 'Curl Concentrado' },
  'Rosca Cabo': { 'pt-BR': 'Rosca Cabo', 'en-US': 'Cable Curl', 'es-ES': 'Curl en Polea' },
  
  'Tríceps Pulley': { 'pt-BR': 'Tríceps Pulley', 'en-US': 'Tricep Pushdown', 'es-ES': 'Extensión de Tríceps en Polea' },
  'Tríceps Corda': { 'pt-BR': 'Tríceps Corda', 'en-US': 'Rope Pushdown', 'es-ES': 'Extensión con Cuerda' },
  'Tríceps Testa': { 'pt-BR': 'Tríceps Testa', 'en-US': 'Skull Crushers', 'es-ES': 'Press Francés' },
  'Tríceps Coice': { 'pt-BR': 'Tríceps Coice', 'en-US': 'Tricep Kickback', 'es-ES': 'Patada de Tríceps' },
  'Tríceps Máquina': { 'pt-BR': 'Tríceps Máquina', 'en-US': 'Machine Tricep Extension', 'es-ES': 'Extensión de Tríceps en Máquina' },
  'Mergulho': { 'pt-BR': 'Mergulho', 'en-US': 'Dips', 'es-ES': 'Fondos' },
  'Supino Fechado': { 'pt-BR': 'Supino Fechado', 'en-US': 'Close Grip Bench Press', 'es-ES': 'Press Agarre Cerrado' },
  
  'Agachamento': { 'pt-BR': 'Agachamento', 'en-US': 'Squat', 'es-ES': 'Sentadilla' },
  'Agachamento Livre': { 'pt-BR': 'Agachamento Livre', 'en-US': 'Barbell Squat', 'es-ES': 'Sentadilla con Barra' },
  'Leg Press': { 'pt-BR': 'Leg Press', 'en-US': 'Leg Press', 'es-ES': 'Prensa de Piernas' },
  'Cadeira Flexora': { 'pt-BR': 'Cadeira Flexora', 'en-US': 'Seated Leg Curl', 'es-ES': 'Curl de Piernas Sentado' },
  'Stiff': { 'pt-BR': 'Stiff', 'en-US': 'Romanian Deadlift', 'es-ES': 'Peso Muerto Rumano' },
  'Afundo': { 'pt-BR': 'Afundo', 'en-US': 'Lunges', 'es-ES': 'Zancadas' },
  'Passada': { 'pt-BR': 'Passada', 'en-US': 'Walking Lunges', 'es-ES': 'Zancadas Caminando' },
  'Hack Squat': { 'pt-BR': 'Hack Squat', 'en-US': 'Hack Squat', 'es-ES': 'Sentadilla Hack' },
  'Adutora': { 'pt-BR': 'Adutora', 'en-US': 'Hip Adduction', 'es-ES': 'Aducción de Cadera' },
  'Abdutora': { 'pt-BR': 'Abdutora', 'en-US': 'Hip Abduction', 'es-ES': 'Abducción de Cadera' },
  'Panturrilha em Pé': { 'pt-BR': 'Panturrilha em Pé', 'en-US': 'Standing Calf Raise', 'es-ES': 'Elevación de Talones de Pie' },
  'Panturrilha Sentado': { 'pt-BR': 'Panturrilha Sentado', 'en-US': 'Seated Calf Raise', 'es-ES': 'Elevación de Talones Sentado' },
  'Gêmeos': { 'pt-BR': 'Gêmeos', 'en-US': 'Calf Raise', 'es-ES': 'Pantorrillas' },
  
  'Abdominal': { 'pt-BR': 'Abdominal', 'en-US': 'Crunches', 'es-ES': 'Abdominales' },
  'Abdominal Infra': { 'pt-BR': 'Abdominal Infra', 'en-US': 'Reverse Crunches', 'es-ES': 'Abdominales Inferiores' },
  'Prancha': { 'pt-BR': 'Prancha', 'en-US': 'Plank', 'es-ES': 'Plancha' },
  'Prancha Lateral': { 'pt-BR': 'Prancha Lateral', 'en-US': 'Side Plank', 'es-ES': 'Plancha Lateral' },
  'Elevação de Pernas': { 'pt-BR': 'Elevação de Pernas', 'en-US': 'Leg Raises', 'es-ES': 'Elevación de Piernas' },
  'Oblíquo': { 'pt-BR': 'Oblíquo', 'en-US': 'Oblique Crunches', 'es-ES': 'Oblicuos' },
};

// ==================== ALIMENTOS ====================
export const foodTranslations: Record<string, Record<SupportedLanguage, string>> = {
  // Proteínas
  'Frango': { 'pt-BR': 'Frango', 'en-US': 'Chicken', 'es-ES': 'Pollo' },
  'Peito de Frango': { 'pt-BR': 'Peito de Frango', 'en-US': 'Chicken Breast', 'es-ES': 'Pechuga de Pollo' },
  'Peito de Frango Grelhado': { 'pt-BR': 'Peito de Frango Grelhado', 'en-US': 'Grilled Chicken Breast', 'es-ES': 'Pechuga de Pollo a la Plancha' },
  'Carne Vermelha': { 'pt-BR': 'Carne Vermelha', 'en-US': 'Beef', 'es-ES': 'Carne de Res' },
  'Patinho': { 'pt-BR': 'Patinho', 'en-US': 'Lean Beef', 'es-ES': 'Carne Magra' },
  'Patinho Moído': { 'pt-BR': 'Patinho Moído', 'en-US': 'Ground Beef', 'es-ES': 'Carne Molida' },
  'Coxão Mole': { 'pt-BR': 'Coxão Mole', 'en-US': 'Top Round Beef', 'es-ES': 'Cuadrada de Res' },
  'Peixe': { 'pt-BR': 'Peixe', 'en-US': 'Fish', 'es-ES': 'Pescado' },
  'Tilápia': { 'pt-BR': 'Tilápia', 'en-US': 'Tilapia', 'es-ES': 'Tilapia' },
  'Salmão': { 'pt-BR': 'Salmão', 'en-US': 'Salmon', 'es-ES': 'Salmón' },
  'Atum': { 'pt-BR': 'Atum', 'en-US': 'Tuna', 'es-ES': 'Atún' },
  'Ovo': { 'pt-BR': 'Ovo', 'en-US': 'Egg', 'es-ES': 'Huevo' },
  'Ovos': { 'pt-BR': 'Ovos', 'en-US': 'Eggs', 'es-ES': 'Huevos' },
  'Ovo Inteiro': { 'pt-BR': 'Ovo Inteiro', 'en-US': 'Whole Egg', 'es-ES': 'Huevo Entero' },
  'Ovos Inteiros': { 'pt-BR': 'Ovos Inteiros', 'en-US': 'Whole Eggs', 'es-ES': 'Huevos Enteros' },
  'Clara de Ovo': { 'pt-BR': 'Clara de Ovo', 'en-US': 'Egg White', 'es-ES': 'Clara de Huevo' },
  'Claras de Ovo': { 'pt-BR': 'Claras de Ovo', 'en-US': 'Egg Whites', 'es-ES': 'Claras de Huevo' },
  'Gema de Ovo': { 'pt-BR': 'Gema de Ovo', 'en-US': 'Egg Yolk', 'es-ES': 'Yema de Huevo' },
  'Omelete': { 'pt-BR': 'Omelete', 'en-US': 'Omelette', 'es-ES': 'Tortilla' },
  'Ovo Cozido': { 'pt-BR': 'Ovo Cozido', 'en-US': 'Boiled Egg', 'es-ES': 'Huevo Cocido' },
  'Ovos Cozidos': { 'pt-BR': 'Ovos Cozidos', 'en-US': 'Boiled Eggs', 'es-ES': 'Huevos Cocidos' },
  'Ovo Mexido': { 'pt-BR': 'Ovo Mexido', 'en-US': 'Scrambled Egg', 'es-ES': 'Huevo Revuelto' },
  'Ovos Mexidos': { 'pt-BR': 'Ovos Mexidos', 'en-US': 'Scrambled Eggs', 'es-ES': 'Huevos Revueltos' },
  'Whey Protein': { 'pt-BR': 'Whey Protein', 'en-US': 'Whey Protein', 'es-ES': 'Proteína de Suero' },
  'Queijo Cottage': { 'pt-BR': 'Queijo Cottage', 'en-US': 'Cottage Cheese', 'es-ES': 'Queso Cottage' },
  'Iogurte Grego': { 'pt-BR': 'Iogurte Grego', 'en-US': 'Greek Yogurt', 'es-ES': 'Yogur Griego' },
  'Iogurte Natural': { 'pt-BR': 'Iogurte Natural', 'en-US': 'Plain Yogurt', 'es-ES': 'Yogur Natural' },
  'Iogurte': { 'pt-BR': 'Iogurte', 'en-US': 'Yogurt', 'es-ES': 'Yogur' },
  'Tofu': { 'pt-BR': 'Tofu', 'en-US': 'Tofu', 'es-ES': 'Tofu' },
  
  // Carnes adicionais
  'Frango Grelhado': { 'pt-BR': 'Frango Grelhado', 'en-US': 'Grilled Chicken', 'es-ES': 'Pollo a la Plancha' },
  'Carne Moída': { 'pt-BR': 'Carne Moída', 'en-US': 'Ground Beef', 'es-ES': 'Carne Molida' },
  'Filé de Frango': { 'pt-BR': 'Filé de Frango', 'en-US': 'Chicken Fillet', 'es-ES': 'Filete de Pollo' },
  'Filé de Peixe': { 'pt-BR': 'Filé de Peixe', 'en-US': 'Fish Fillet', 'es-ES': 'Filete de Pescado' },
  'Camarão': { 'pt-BR': 'Camarão', 'en-US': 'Shrimp', 'es-ES': 'Camarón' },
  'Peru': { 'pt-BR': 'Peru', 'en-US': 'Turkey', 'es-ES': 'Pavo' },
  'Peito de Peru': { 'pt-BR': 'Peito de Peru', 'en-US': 'Turkey Breast', 'es-ES': 'Pechuga de Pavo' },
  'Carne de Porco': { 'pt-BR': 'Carne de Porco', 'en-US': 'Pork', 'es-ES': 'Cerdo' },
  'Lombo': { 'pt-BR': 'Lombo', 'en-US': 'Pork Loin', 'es-ES': 'Lomo de Cerdo' },
  
  // Carboidratos
  'Arroz': { 'pt-BR': 'Arroz', 'en-US': 'Rice', 'es-ES': 'Arroz' },
  'Arroz Branco': { 'pt-BR': 'Arroz Branco', 'en-US': 'White Rice', 'es-ES': 'Arroz Blanco' },
  'Arroz Integral': { 'pt-BR': 'Arroz Integral', 'en-US': 'Brown Rice', 'es-ES': 'Arroz Integral' },
  'Batata Doce': { 'pt-BR': 'Batata Doce', 'en-US': 'Sweet Potato', 'es-ES': 'Batata' },
  'Batata Inglesa': { 'pt-BR': 'Batata Inglesa', 'en-US': 'Potato', 'es-ES': 'Papa' },
  'Macarrão': { 'pt-BR': 'Macarrão', 'en-US': 'Pasta', 'es-ES': 'Pasta' },
  'Macarrão Integral': { 'pt-BR': 'Macarrão Integral', 'en-US': 'Whole Wheat Pasta', 'es-ES': 'Pasta Integral' },
  'Pão': { 'pt-BR': 'Pão', 'en-US': 'Bread', 'es-ES': 'Pan' },
  'Pão Francês': { 'pt-BR': 'Pão Francês', 'en-US': 'French Bread', 'es-ES': 'Pan Francés' },
  'Pão Integral': { 'pt-BR': 'Pão Integral', 'en-US': 'Whole Wheat Bread', 'es-ES': 'Pan Integral' },
  'Pão de Forma': { 'pt-BR': 'Pão de Forma', 'en-US': 'Sliced Bread', 'es-ES': 'Pan de Molde' },
  'Aveia': { 'pt-BR': 'Aveia', 'en-US': 'Oatmeal', 'es-ES': 'Avena' },
  'Tapioca': { 'pt-BR': 'Tapioca', 'en-US': 'Tapioca', 'es-ES': 'Tapioca' },
  'Cuscuz': { 'pt-BR': 'Cuscuz', 'en-US': 'Couscous', 'es-ES': 'Cuscús' },
  'Quinoa': { 'pt-BR': 'Quinoa', 'en-US': 'Quinoa', 'es-ES': 'Quinoa' },
  'Feijão': { 'pt-BR': 'Feijão', 'en-US': 'Beans', 'es-ES': 'Frijoles' },
  'Lentilha': { 'pt-BR': 'Lentilha', 'en-US': 'Lentils', 'es-ES': 'Lentejas' },
  'Grão de Bico': { 'pt-BR': 'Grão de Bico', 'en-US': 'Chickpeas', 'es-ES': 'Garbanzos' },
  'Farofa': { 'pt-BR': 'Farofa', 'en-US': 'Toasted Cassava Flour', 'es-ES': 'Farofa' },
  'Granola': { 'pt-BR': 'Granola', 'en-US': 'Granola', 'es-ES': 'Granola' },
  'Cereal Integral': { 'pt-BR': 'Cereal Integral', 'en-US': 'Whole Grain Cereal', 'es-ES': 'Cereal Integral' },
  'Torrada Integral': { 'pt-BR': 'Torrada Integral', 'en-US': 'Whole Wheat Toast', 'es-ES': 'Tostada Integral' },
  'Milho': { 'pt-BR': 'Milho', 'en-US': 'Corn', 'es-ES': 'Maíz' },
  
  // Frutas
  'Banana': { 'pt-BR': 'Banana', 'en-US': 'Banana', 'es-ES': 'Plátano' },
  'Maçã': { 'pt-BR': 'Maçã', 'en-US': 'Apple', 'es-ES': 'Manzana' },
  'Laranja': { 'pt-BR': 'Laranja', 'en-US': 'Orange', 'es-ES': 'Naranja' },
  'Morango': { 'pt-BR': 'Morango', 'en-US': 'Strawberry', 'es-ES': 'Fresa' },
  'Mamão': { 'pt-BR': 'Mamão', 'en-US': 'Papaya', 'es-ES': 'Papaya' },
  'Melão': { 'pt-BR': 'Melão', 'en-US': 'Melon', 'es-ES': 'Melón' },
  'Melancia': { 'pt-BR': 'Melancia', 'en-US': 'Watermelon', 'es-ES': 'Sandía' },
  'Uva': { 'pt-BR': 'Uva', 'en-US': 'Grape', 'es-ES': 'Uva' },
  'Manga': { 'pt-BR': 'Manga', 'en-US': 'Mango', 'es-ES': 'Mango' },
  'Abacaxi': { 'pt-BR': 'Abacaxi', 'en-US': 'Pineapple', 'es-ES': 'Piña' },
  'Kiwi': { 'pt-BR': 'Kiwi', 'en-US': 'Kiwi', 'es-ES': 'Kiwi' },
  'Pera': { 'pt-BR': 'Pera', 'en-US': 'Pear', 'es-ES': 'Pera' },
  'Pêssego': { 'pt-BR': 'Pêssego', 'en-US': 'Peach', 'es-ES': 'Durazno' },
  
  // Gorduras
  'Azeite': { 'pt-BR': 'Azeite', 'en-US': 'Olive Oil', 'es-ES': 'Aceite de Oliva' },
  'Azeite de Oliva': { 'pt-BR': 'Azeite de Oliva', 'en-US': 'Olive Oil', 'es-ES': 'Aceite de Oliva' },
  'Castanha': { 'pt-BR': 'Castanha', 'en-US': 'Nuts', 'es-ES': 'Nueces' },
  'Castanhas': { 'pt-BR': 'Castanhas', 'en-US': 'Nuts', 'es-ES': 'Nueces' },
  'Castanha do Pará': { 'pt-BR': 'Castanha do Pará', 'en-US': 'Brazil Nuts', 'es-ES': 'Nueces de Brasil' },
  'Castanha de Caju': { 'pt-BR': 'Castanha de Caju', 'en-US': 'Cashews', 'es-ES': 'Anacardos' },
  'Amendoim': { 'pt-BR': 'Amendoim', 'en-US': 'Peanuts', 'es-ES': 'Cacahuetes' },
  'Pasta de Amendoim': { 'pt-BR': 'Pasta de Amendoim', 'en-US': 'Peanut Butter', 'es-ES': 'Mantequilla de Maní' },
  'Amêndoas': { 'pt-BR': 'Amêndoas', 'en-US': 'Almonds', 'es-ES': 'Almendras' },
  'Nozes': { 'pt-BR': 'Nozes', 'en-US': 'Walnuts', 'es-ES': 'Nueces' },
  'Chia': { 'pt-BR': 'Chia', 'en-US': 'Chia Seeds', 'es-ES': 'Semillas de Chía' },
  'Linhaça': { 'pt-BR': 'Linhaça', 'en-US': 'Flaxseed', 'es-ES': 'Linaza' },
  'Abacate': { 'pt-BR': 'Abacate', 'en-US': 'Avocado', 'es-ES': 'Aguacate' },
  'Coco': { 'pt-BR': 'Coco', 'en-US': 'Coconut', 'es-ES': 'Coco' },
  'Óleo de Coco': { 'pt-BR': 'Óleo de Coco', 'en-US': 'Coconut Oil', 'es-ES': 'Aceite de Coco' },
  'Queijo': { 'pt-BR': 'Queijo', 'en-US': 'Cheese', 'es-ES': 'Queso' },
  
  // Laticínios e Proteínas
  'Iogurte Natural': { 'pt-BR': 'Iogurte Natural', 'en-US': 'Natural Yogurt', 'es-ES': 'Yogur Natural' },
  'Leite Integral': { 'pt-BR': 'Leite Integral', 'en-US': 'Whole Milk', 'es-ES': 'Leche Entera' },
  'Leite Desnatado': { 'pt-BR': 'Leite Desnatado', 'en-US': 'Skim Milk', 'es-ES': 'Leche Descremada' },
  'Requeijão Light': { 'pt-BR': 'Requeijão Light', 'en-US': 'Light Cream Cheese', 'es-ES': 'Requesón Light' },
  
  // Extras/Doces
  'Mel': { 'pt-BR': 'Mel', 'en-US': 'Honey', 'es-ES': 'Miel' },
  'Leite Condensado': { 'pt-BR': 'Leite Condensado', 'en-US': 'Condensed Milk', 'es-ES': 'Leche Condensada' },
  'Whey Protein': { 'pt-BR': 'Whey Protein', 'en-US': 'Whey Protein', 'es-ES': 'Proteína Whey' },
  
  // Vegetais
  'Brócolis': { 'pt-BR': 'Brócolis', 'en-US': 'Broccoli', 'es-ES': 'Brócoli' },
  'Espinafre': { 'pt-BR': 'Espinafre', 'en-US': 'Spinach', 'es-ES': 'Espinaca' },
  'Couve': { 'pt-BR': 'Couve', 'en-US': 'Kale', 'es-ES': 'Col Rizada' },
  'Alface': { 'pt-BR': 'Alface', 'en-US': 'Lettuce', 'es-ES': 'Lechuga' },
  'Tomate': { 'pt-BR': 'Tomate', 'en-US': 'Tomato', 'es-ES': 'Tomate' },
  'Pepino': { 'pt-BR': 'Pepino', 'en-US': 'Cucumber', 'es-ES': 'Pepino' },
  'Cenoura': { 'pt-BR': 'Cenoura', 'en-US': 'Carrot', 'es-ES': 'Zanahoria' },
  'Abobrinha': { 'pt-BR': 'Abobrinha', 'en-US': 'Zucchini', 'es-ES': 'Calabacín' },
  'Feijão': { 'pt-BR': 'Feijão', 'en-US': 'Beans', 'es-ES': 'Frijoles' },
  'Lentilha': { 'pt-BR': 'Lentilha', 'en-US': 'Lentils', 'es-ES': 'Lentejas' },
  'Grão de Bico': { 'pt-BR': 'Grão de Bico', 'en-US': 'Chickpeas', 'es-ES': 'Garbanzos' },
  
  // Laticínios
  'Leite': { 'pt-BR': 'Leite', 'en-US': 'Milk', 'es-ES': 'Leche' },
  'Leite Desnatado': { 'pt-BR': 'Leite Desnatado', 'en-US': 'Skim Milk', 'es-ES': 'Leche Desnatada' },
  'Queijo': { 'pt-BR': 'Queijo', 'en-US': 'Cheese', 'es-ES': 'Queso' },
  'Queijo Branco': { 'pt-BR': 'Queijo Branco', 'en-US': 'White Cheese', 'es-ES': 'Queso Blanco' },
  'Requeijão': { 'pt-BR': 'Requeijão', 'en-US': 'Cream Cheese', 'es-ES': 'Queso Crema' },
  'Iogurte': { 'pt-BR': 'Iogurte', 'en-US': 'Yogurt', 'es-ES': 'Yogur' },
};

// ==================== NOMES DE REFEIÇÕES ====================
export const mealNameTranslations: Record<string, Record<SupportedLanguage, string>> = {
  'Café da Manhã': { 'pt-BR': 'Café da Manhã', 'en-US': 'Breakfast', 'es-ES': 'Desayuno' },
  'Lanche Manhã': { 'pt-BR': 'Lanche Manhã', 'en-US': 'Morning Snack', 'es-ES': 'Snack de la Mañana' },
  'Lanche da Manhã': { 'pt-BR': 'Lanche da Manhã', 'en-US': 'Morning Snack', 'es-ES': 'Snack de la Mañana' },
  'Almoço': { 'pt-BR': 'Almoço', 'en-US': 'Lunch', 'es-ES': 'Almuerzo' },
  'Lanche Tarde': { 'pt-BR': 'Lanche Tarde', 'en-US': 'Afternoon Snack', 'es-ES': 'Snack de la Tarde' },
  'Lanche da Tarde': { 'pt-BR': 'Lanche da Tarde', 'en-US': 'Afternoon Snack', 'es-ES': 'Snack de la Tarde' },
  'Jantar': { 'pt-BR': 'Jantar', 'en-US': 'Dinner', 'es-ES': 'Cena' },
  'Ceia': { 'pt-BR': 'Ceia', 'en-US': 'Supper', 'es-ES': 'Cena Ligera' },
};

// ==================== NOMES DE TREINOS ====================
export const workoutNameTranslations: Record<string, Record<SupportedLanguage, string>> = {
  'Treino A - Peito/Tríceps': { 'pt-BR': 'Treino A - Peito/Tríceps', 'en-US': 'Workout A - Chest/Triceps', 'es-ES': 'Entreno A - Pecho/Tríceps' },
  'Treino B - Costas/Bíceps': { 'pt-BR': 'Treino B - Costas/Bíceps', 'en-US': 'Workout B - Back/Biceps', 'es-ES': 'Entreno B - Espalda/Bíceps' },
  'Treino C - Pernas': { 'pt-BR': 'Treino C - Pernas', 'en-US': 'Workout C - Legs', 'es-ES': 'Entreno C - Piernas' },
  'Treino D - Ombros/Abdômen': { 'pt-BR': 'Treino D - Ombros/Abdômen', 'en-US': 'Workout D - Shoulders/Abs', 'es-ES': 'Entreno D - Hombros/Abdomen' },
  'Treino A - Superior': { 'pt-BR': 'Treino A - Superior', 'en-US': 'Workout A - Upper Body', 'es-ES': 'Entreno A - Tren Superior' },
  'Treino B - Inferior': { 'pt-BR': 'Treino B - Inferior', 'en-US': 'Workout B - Lower Body', 'es-ES': 'Entreno B - Tren Inferior' },
  'Treino Full Body': { 'pt-BR': 'Treino Full Body', 'en-US': 'Full Body Workout', 'es-ES': 'Entreno Cuerpo Completo' },
  // Focus
  'Peito': { 'pt-BR': 'Peito', 'en-US': 'Chest', 'es-ES': 'Pecho' },
  'Costas': { 'pt-BR': 'Costas', 'en-US': 'Back', 'es-ES': 'Espalda' },
  'Pernas': { 'pt-BR': 'Pernas', 'en-US': 'Legs', 'es-ES': 'Piernas' },
  'Ombros': { 'pt-BR': 'Ombros', 'en-US': 'Shoulders', 'es-ES': 'Hombros' },
  'Bíceps': { 'pt-BR': 'Bíceps', 'en-US': 'Biceps', 'es-ES': 'Bíceps' },
  'Tríceps': { 'pt-BR': 'Tríceps', 'en-US': 'Triceps', 'es-ES': 'Tríceps' },
  'Abdômen': { 'pt-BR': 'Abdômen', 'en-US': 'Abs', 'es-ES': 'Abdomen' },
  'Glúteos': { 'pt-BR': 'Glúteos', 'en-US': 'Glutes', 'es-ES': 'Glúteos' },
  'Panturrilha': { 'pt-BR': 'Panturrilha', 'en-US': 'Calves', 'es-ES': 'Pantorrillas' },
};

// ==================== INSTRUÇÕES DOS EXERCÍCIOS ====================
export const exerciseInstructionsTranslations: Record<string, Record<SupportedLanguage, string>> = {
  // ============ PEITO - INSTRUÇÕES DO BACKEND ============
  'Sente com costas apoiadas. Empurre as manoplas para frente até extensão quase completa. Retorne controlado sem bater os pesos.': {
    'pt-BR': 'Sente com costas apoiadas. Empurre as manoplas para frente até extensão quase completa. Retorne controlado sem bater os pesos.',
    'en-US': 'Sit with your back supported. Push the handles forward until near full extension. Return slowly without letting the weights slam.',
    'es-ES': 'Siéntate con la espalda apoyada. Empuja las manijas hacia adelante hasta extensión casi completa. Regresa controlado sin golpear los pesos.'
  },
  'Cotovelos na altura dos ombros. Junte os braços à frente contraindo o peitoral. Abra controlado até sentir leve alongamento.': {
    'pt-BR': 'Cotovelos na altura dos ombros. Junte os braços à frente contraindo o peitoral. Abra controlado até sentir leve alongamento.',
    'en-US': 'Elbows at shoulder height. Bring your arms together in front contracting the chest. Open slowly until you feel a light stretch.',
    'es-ES': 'Codos a la altura de los hombros. Junta los brazos al frente contrayendo el pectoral. Abre controlado hasta sentir un leve estiramiento.'
  },
  'Cabos na posição alta. Dê um passo à frente. Puxe os cabos para baixo e para frente, cruzando na frente do corpo. Volte controlado.': {
    'pt-BR': 'Cabos na posição alta. Dê um passo à frente. Puxe os cabos para baixo e para frente, cruzando na frente do corpo. Volte controlado.',
    'en-US': 'Cables in high position. Step forward. Pull the cables down and forward, crossing in front of your body. Return slowly.',
    'es-ES': 'Cables en posición alta. Da un paso adelante. Tira de los cables hacia abajo y adelante, cruzando frente al cuerpo. Regresa controlado.'
  },
  'Banco a 30°. Halteres ao lado do peito. Empurre para cima sem bater os halteres no topo. Desça controlado até cotovelos a 90°.': {
    'pt-BR': 'Banco a 30°. Halteres ao lado do peito. Empurre para cima sem bater os halteres no topo. Desça controlado até cotovelos a 90°.',
    'en-US': 'Bench at 30°. Dumbbells at chest level. Push up without clanking the dumbbells at the top. Lower slowly until elbows reach 90°.',
    'es-ES': 'Banco a 30°. Mancuernas al lado del pecho. Empuja hacia arriba sin chocar las mancuernas arriba. Baja controlado hasta codos a 90°.'
  },
  
  // ============ COSTAS - INSTRUÇÕES DO BACKEND ============
  'Pegada um pouco mais larga que os ombros. Puxe a barra até a altura do queixo, levando os cotovelos para baixo e para trás. Retorne controlado.': {
    'pt-BR': 'Pegada um pouco mais larga que os ombros. Puxe a barra até a altura do queixo, levando os cotovelos para baixo e para trás. Retorne controlado.',
    'en-US': 'Grip slightly wider than shoulders. Pull the bar to chin height, bringing elbows down and back. Return slowly.',
    'es-ES': 'Agarre un poco más ancho que los hombros. Tira de la barra hasta la altura del mentón, llevando los codos hacia abajo y atrás. Regresa controlado.'
  },
  'Peito apoiado no suporte. Puxe as manoplas em direção ao abdômen, contraindo as escápulas. Retorne estendendo completamente os braços.': {
    'pt-BR': 'Peito apoiado no suporte. Puxe as manoplas em direção ao abdômen, contraindo as escápulas. Retorne estendendo completamente os braços.',
    'en-US': 'Chest supported on the pad. Pull the handles toward your abdomen, squeezing your shoulder blades. Return by fully extending your arms.',
    'es-ES': 'Pecho apoyado en el soporte. Tira de las manijas hacia el abdomen, contrayendo las escápulas. Regresa extendiendo completamente los brazos.'
  },
  'Sente com pernas levemente flexionadas. Puxe o triângulo até o abdômen, mantendo costas retas. Estenda os braços completamente na volta.': {
    'pt-BR': 'Sente com pernas levemente flexionadas. Puxe o triângulo até o abdômen, mantendo costas retas. Estenda os braços completamente na volta.',
    'en-US': 'Sit with legs slightly bent. Pull the handle to your abdomen, keeping your back straight. Fully extend your arms on the return.',
    'es-ES': 'Siéntate con piernas ligeramente flexionadas. Tira del triángulo hasta el abdomen, manteniendo la espalda recta. Extiende los brazos completamente al volver.'
  },
  'Braços estendidos acima. Puxe a corda até a altura das coxas, mantendo cotovelos próximos ao corpo. Retorne controlado.': {
    'pt-BR': 'Braços estendidos acima. Puxe a corda até a altura das coxas, mantendo cotovelos próximos ao corpo. Retorne controlado.',
    'en-US': 'Arms extended overhead. Pull the rope down to thigh level, keeping elbows close to your body. Return slowly.',
    'es-ES': 'Brazos extendidos arriba. Tira de la cuerda hasta la altura de los muslos, manteniendo los codos cerca del cuerpo. Regresa controlado.'
  },
  
  // ============ OMBROS - INSTRUÇÕES DO BACKEND ============
  'Sente com costas totalmente apoiadas. Empurre as manoplas para cima até quase estender os cotovelos. Desça até a altura das orelhas.': {
    'pt-BR': 'Sente com costas totalmente apoiadas. Empurre as manoplas para cima até quase estender os cotovelos. Desça até a altura das orelhas.',
    'en-US': 'Sit with your back fully supported. Push the handles up until your elbows are almost extended. Lower to ear level.',
    'es-ES': 'Siéntate con la espalda totalmente apoyada. Empuja las manijas hacia arriba hasta casi extender los codos. Baja hasta la altura de las orejas.'
  },
  'Cotovelos apoiados nas almofadas. Eleve os braços até a altura dos ombros. Desça controlado sem deixar os pesos baterem.': {
    'pt-BR': 'Cotovelos apoiados nas almofadas. Eleve os braços até a altura dos ombros. Desça controlado sem deixar os pesos baterem.',
    'en-US': 'Elbows resting on the pads. Raise your arms to shoulder height. Lower slowly without letting the weights slam.',
    'es-ES': 'Codos apoyados en las almohadillas. Eleva los brazos hasta la altura de los hombros. Baja controlado sin dejar que los pesos golpeen.'
  },
  'Sente no banco para mais estabilidade. Cotovelos levemente flexionados. Eleve até a altura dos ombros. Desça controlado.': {
    'pt-BR': 'Sente no banco para mais estabilidade. Cotovelos levemente flexionados. Eleve até a altura dos ombros. Desça controlado.',
    'en-US': 'Sit on a bench for more stability. Elbows slightly bent. Raise to shoulder height. Lower slowly.',
    'es-ES': 'Siéntate en el banco para más estabilidad. Codos ligeramente flexionados. Eleva hasta la altura de los hombros. Baja controlado.'
  },
  'Polia na altura do rosto. Puxe a corda em direção ao rosto, abrindo os cotovelos para os lados. Aperte as escápulas no final.': {
    'pt-BR': 'Polia na altura do rosto. Puxe a corda em direção ao rosto, abrindo os cotovelos para os lados. Aperte as escápulas no final.',
    'en-US': 'Cable at face height. Pull the rope toward your face, spreading elbows to the sides. Squeeze shoulder blades at the end.',
    'es-ES': 'Polea a la altura del rostro. Tira de la cuerda hacia la cara, abriendo los codos hacia los lados. Aprieta las escápulas al final.'
  },
  
  // ============ BÍCEPS - INSTRUÇÕES DO BACKEND ============
  'Braços apoiados no suporte. Flexione os cotovelos trazendo as manoplas em direção aos ombros. Desça controlado sem estender completamente.': {
    'pt-BR': 'Braços apoiados no suporte. Flexione os cotovelos trazendo as manoplas em direção aos ombros. Desça controlado sem estender completamente.',
    'en-US': 'Arms supported on the pad. Curl by bringing the handles toward your shoulders. Lower slowly without fully extending.',
    'es-ES': 'Brazos apoyados en el soporte. Flexiona los codos llevando las manijas hacia los hombros. Baja controlado sin extender completamente.'
  },
  'De frente para a polia baixa. Cotovelos fixos ao lado do corpo. Flexione puxando a barra até os ombros. Desça controlado.': {
    'pt-BR': 'De frente para a polia baixa. Cotovelos fixos ao lado do corpo. Flexione puxando a barra até os ombros. Desça controlado.',
    'en-US': 'Facing the low pulley. Elbows fixed at your sides. Curl by pulling the bar to your shoulders. Lower slowly.',
    'es-ES': 'De frente a la polea baja. Codos fijos al lado del cuerpo. Flexiona tirando de la barra hasta los hombros. Baja controlado.'
  },
  'Sente no banco com costas apoiadas. Alterne os braços. Gire o punho (supinação) durante a subida. Desça controlado.': {
    'pt-BR': 'Sente no banco com costas apoiadas. Alterne os braços. Gire o punho (supinação) durante a subida. Desça controlado.',
    'en-US': 'Sit on a bench with back supported. Alternate arms. Rotate your wrist (supination) on the way up. Lower slowly.',
    'es-ES': 'Siéntate en el banco con espalda apoyada. Alterna los brazos. Gira la muñeca (supinación) durante la subida. Baja controlado.'
  },
  'Pegada neutra (palmas voltadas para dentro). Cotovelos fixos. Flexione até contrair o bíceps. Desça controlado.': {
    'pt-BR': 'Pegada neutra (palmas voltadas para dentro). Cotovelos fixos. Flexione até contrair o bíceps. Desça controlado.',
    'en-US': 'Neutral grip (palms facing in). Elbows fixed. Curl until biceps are contracted. Lower slowly.',
    'es-ES': 'Agarre neutro (palmas hacia adentro). Codos fijos. Flexiona hasta contraer el bíceps. Baja controlado.'
  },
  
  // ============ TRÍCEPS - INSTRUÇÕES DO BACKEND ============
  'Cotovelos fixos ao lado do corpo. Estenda os braços completamente, abrindo a corda no final. Retorne até 90° nos cotovelos.': {
    'pt-BR': 'Cotovelos fixos ao lado do corpo. Estenda os braços completamente, abrindo a corda no final. Retorne até 90° nos cotovelos.',
    'en-US': 'Elbows fixed at your sides. Fully extend your arms, spreading the rope at the bottom. Return to 90° at the elbows.',
    'es-ES': 'Codos fijos al lado del cuerpo. Extiende los brazos completamente, abriendo la cuerda al final. Regresa hasta 90° en los codos.'
  },
  'Pegada pronada na barra. Cotovelos fixos. Empurre a barra para baixo até extensão completa. Retorne controlado até 90°.': {
    'pt-BR': 'Pegada pronada na barra. Cotovelos fixos. Empurre a barra para baixo até extensão completa. Retorne controlado até 90°.',
    'en-US': 'Overhand grip on the bar. Elbows fixed. Push the bar down to full extension. Return slowly to 90°.',
    'es-ES': 'Agarre pronado en la barra. Codos fijos. Empuja la barra hacia abajo hasta extensión completa. Regresa controlado hasta 90°.'
  },
  'Sente com costas apoiadas. Empurre as manoplas para baixo estendendo os cotovelos. Retorne controlado sem deixar pesos baterem.': {
    'pt-BR': 'Sente com costas apoiadas. Empurre as manoplas para baixo estendendo os cotovelos. Retorne controlado sem deixar pesos baterem.',
    'en-US': 'Sit with your back supported. Push the handles down by extending your elbows. Return slowly without letting weights slam.',
    'es-ES': 'Siéntate con espalda apoyada. Empuja las manijas hacia abajo extendiendo los codos. Regresa controlado sin dejar golpear los pesos.'
  },
  'Sente no banco. Segure um halter acima da cabeça com as duas mãos. Desça atrás da cabeça. Estenda sem mover os cotovelos.': {
    'pt-BR': 'Sente no banco. Segure um halter acima da cabeça com as duas mãos. Desça atrás da cabeça. Estenda sem mover os cotovelos.',
    'en-US': 'Sit on a bench. Hold a dumbbell overhead with both hands. Lower behind your head. Extend without moving your elbows.',
    'es-ES': 'Siéntate en el banco. Sostén una mancuerna sobre la cabeza con ambas manos. Baja detrás de la cabeza. Extiende sin mover los codos.'
  },
  
  // ============ QUADRÍCEPS - INSTRUÇÕES DO BACKEND ============
  'Pés no centro da plataforma na largura dos ombros. Desça até 90° nos joelhos. Empurre sem travar os joelhos no topo.': {
    'pt-BR': 'Pés no centro da plataforma na largura dos ombros. Desça até 90° nos joelhos. Empurre sem travar os joelhos no topo.',
    'en-US': 'Feet in the center of the platform, shoulder-width apart. Lower to 90° at the knees. Push without locking knees at the top.',
    'es-ES': 'Pies en el centro de la plataforma al ancho de los hombros. Baja hasta 90° en las rodillas. Empuja sin trabar las rodillas arriba.'
  },
  'Ajuste o encosto para joelhos alinhados com o eixo. Estenda as pernas completamente, contraindo no topo. Desça controlado.': {
    'pt-BR': 'Ajuste o encosto para joelhos alinhados com o eixo. Estenda as pernas completamente, contraindo no topo. Desça controlado.',
    'en-US': 'Adjust the backrest so knees align with the pivot. Fully extend your legs, contracting at the top. Lower slowly.',
    'es-ES': 'Ajusta el respaldo para rodillas alineadas con el eje. Extiende las piernas completamente, contrayendo arriba. Baja controlado.'
  },
  'Pés ligeiramente à frente da barra. Desça até coxas paralelas ao chão. Suba empurrando pelos calcanhares. Joelhos alinhados com os pés.': {
    'pt-BR': 'Pés ligeiramente à frente da barra. Desça até coxas paralelas ao chão. Suba empurrando pelos calcanhares. Joelhos alinhados com os pés.',
    'en-US': 'Feet slightly in front of the bar. Lower until thighs are parallel to the floor. Push through your heels. Knees aligned with feet.',
    'es-ES': 'Pies ligeramente delante de la barra. Baja hasta muslos paralelos al suelo. Sube empujando por los talones. Rodillas alineadas con los pies.'
  },
  'Costas totalmente apoiadas. Pés na largura dos ombros. Empurre a plataforma sem travar joelhos. Desça controlado até 90°.': {
    'pt-BR': 'Costas totalmente apoiadas. Pés na largura dos ombros. Empurre a plataforma sem travar joelhos. Desça controlado até 90°.',
    'en-US': 'Back fully supported. Feet shoulder-width apart. Push the platform without locking knees. Lower slowly to 90°.',
    'es-ES': 'Espalda totalmente apoyada. Pies al ancho de los hombros. Empuja la plataforma sin trabar rodillas. Baja controlado hasta 90°.'
  },
  
  // ============ POSTERIOR - INSTRUÇÕES DO BACKEND ============
  'Deite de bruços com joelhos alinhados ao eixo da máquina. Flexione as pernas trazendo os calcanhares em direção aos glúteos. Desça controlado.': {
    'pt-BR': 'Deite de bruços com joelhos alinhados ao eixo da máquina. Flexione as pernas trazendo os calcanhares em direção aos glúteos. Desça controlado.',
    'en-US': 'Lie face down with knees aligned with the machine pivot. Curl your legs bringing heels toward your glutes. Lower slowly.',
    'es-ES': 'Acuéstate boca abajo con rodillas alineadas al eje de la máquina. Flexiona las piernas llevando los talones hacia los glúteos. Baja controlado.'
  },
  'Sente com coxas apoiadas. Flexione as pernas para baixo e para trás. Contraia no final do movimento. Retorne controlado.': {
    'pt-BR': 'Sente com coxas apoiadas. Flexione as pernas para baixo e para trás. Contraia no final do movimento. Retorne controlado.',
    'en-US': 'Sit with thighs supported. Curl your legs down and back. Contract at the end of the movement. Return slowly.',
    'es-ES': 'Siéntate con muslos apoyados. Flexiona las piernas hacia abajo y atrás. Contrae al final del movimiento. Regresa controlado.'
  },
  'Pernas semi-estendidas, pés na largura do quadril. Desça a barra deslizando próximo às coxas até sentir alongamento. Suba contraindo glúteos.': {
    'pt-BR': 'Pernas semi-estendidas, pés na largura do quadril. Desça a barra deslizando próximo às coxas até sentir alongamento. Suba contraindo glúteos.',
    'en-US': 'Legs semi-extended, feet hip-width apart. Lower the bar sliding close to your thighs until you feel a stretch. Rise contracting glutes.',
    'es-ES': 'Piernas semi-extendidas, pies al ancho de la cadera. Baja la barra deslizando cerca de los muslos hasta sentir estiramiento. Sube contrayendo glúteos.'
  },
  'Apoie o pé na plataforma. Empurre para trás estendendo o quadril. Contraia o glúteo no topo. Retorne controlado sem deixar peso bater.': {
    'pt-BR': 'Apoie o pé na plataforma. Empurre para trás estendendo o quadril. Contraia o glúteo no topo. Retorne controlado sem deixar peso bater.',
    'en-US': 'Place your foot on the platform. Push back extending your hip. Contract your glute at the top. Return slowly without letting the weight slam.',
    'es-ES': 'Apoya el pie en la plataforma. Empuja hacia atrás extendiendo la cadera. Contrae el glúteo arriba. Regresa controlado sin dejar golpear el peso.'
  },
  
  // ============ PANTURRILHA - INSTRUÇÕES DO BACKEND ============
  'Apoie apenas a ponta dos pés na plataforma. Empurre estendendo os tornozelos o máximo possível. Desça alongando bem a panturrilha.': {
    'pt-BR': 'Apoie apenas a ponta dos pés na plataforma. Empurre estendendo os tornozelos o máximo possível. Desça alongando bem a panturrilha.',
    'en-US': 'Place only the balls of your feet on the platform. Push by extending your ankles as much as possible. Lower, stretching your calves well.',
    'es-ES': 'Apoya solo la punta de los pies en la plataforma. Empuja extendiendo los tobillos al máximo. Baja estirando bien la pantorrilla.'
  },
  'Joelhos a 90° sob as almofadas. Eleve os calcanhares o máximo possível. Desça controlado até sentir alongamento completo.': {
    'pt-BR': 'Joelhos a 90° sob as almofadas. Eleve os calcanhares o máximo possível. Desça controlado até sentir alongamento completo.',
    'en-US': 'Knees at 90° under the pads. Raise your heels as high as possible. Lower slowly until you feel a full stretch.',
    'es-ES': 'Rodillas a 90° bajo las almohadillas. Eleva los talones lo máximo posible. Baja controlado hasta sentir estiramiento completo.'
  },
  'Ombros sob as almofadas. Eleve nos dedos o máximo possível, contraindo no topo. Desça alongando completamente.': {
    'pt-BR': 'Ombros sob as almofadas. Eleve nos dedos o máximo possível, contraindo no topo. Desça alongando completamente.',
    'en-US': 'Shoulders under the pads. Rise on your toes as high as possible, contracting at the top. Lower, fully stretching.',
    'es-ES': 'Hombros bajo las almohadillas. Elévate en los dedos lo máximo posible, contrayendo arriba. Baja estirando completamente.'
  },
  
  // ============ ABDÔMEN - INSTRUÇÕES DO BACKEND ============
  'Sente e segure as manoplas. Flexione o tronco para frente contraindo o abdômen. Retorne controlado sem soltar a tensão.': {
    'pt-BR': 'Sente e segure as manoplas. Flexione o tronco para frente contraindo o abdômen. Retorne controlado sem soltar a tensão.',
    'en-US': 'Sit and hold the handles. Flex your torso forward contracting your abs. Return slowly without releasing tension.',
    'es-ES': 'Siéntate y sostén las manijas. Flexiona el tronco hacia adelante contrayendo el abdomen. Regresa controlado sin soltar la tensión.'
  },
  'Ajoelhe de costas para a polia. Segure a corda atrás da cabeça. Flexione o tronco em direção ao chão. Retorne controlado.': {
    'pt-BR': 'Ajoelhe de costas para a polia. Segure a corda atrás da cabeça. Flexione o tronco em direção ao chão. Retorne controlado.',
    'en-US': 'Kneel with your back to the pulley. Hold the rope behind your head. Flex your torso toward the floor. Return slowly.',
    'es-ES': 'Arrodíllate de espaldas a la polea. Sostén la cuerda detrás de la cabeza. Flexiona el tronco hacia el suelo. Regresa controlado.'
  },
  'Apoie antebraços e pontas dos pés no chão. Corpo reto da cabeça aos calcanhares. Mantenha o abdômen contraído. Não deixe o quadril subir ou descer.': {
    'pt-BR': 'Apoie antebraços e pontas dos pés no chão. Corpo reto da cabeça aos calcanhares. Mantenha o abdômen contraído. Não deixe o quadril subir ou descer.',
    'en-US': 'Support yourself on forearms and toes. Body straight from head to heels. Keep your abs contracted. Do not let your hips rise or drop.',
    'es-ES': 'Apóyate en antebrazos y puntas de los pies. Cuerpo recto de la cabeza a los talones. Mantén el abdomen contraído. No dejes que la cadera suba o baje.'
  },
  'Costas apoiadas no suporte, braços nos apoios. Eleve as pernas estendidas até 90°. Desça controlado sem balançar o corpo.': {
    'pt-BR': 'Costas apoiadas no suporte, braços nos apoios. Eleve as pernas estendidas até 90°. Desça controlado sem balançar o corpo.',
    'en-US': 'Back against the support, arms on the rests. Raise extended legs to 90°. Lower slowly without swinging your body.',
    'es-ES': 'Espalda apoyada en el soporte, brazos en los apoyos. Eleva las piernas extendidas hasta 90°. Baja controlado sin balancear el cuerpo.'
  },

  // Instruções genéricas
  'Deite no banco, segure a barra na largura dos ombros, desça até o peito e empurre para cima.': {
    'pt-BR': 'Deite no banco, segure a barra na largura dos ombros, desça até o peito e empurre para cima.',
    'en-US': 'Lie on the bench, grip the bar shoulder-width apart, lower to chest level and push up.',
    'es-ES': 'Acuéstate en el banco, agarra la barra al ancho de los hombros, baja hasta el pecho y empuja hacia arriba.'
  },
  'Puxe a barra até a altura do peito, controlando o movimento.': {
    'pt-BR': 'Puxe a barra até a altura do peito, controlando o movimento.',
    'en-US': 'Pull the bar to chest height, controlling the movement.',
    'es-ES': 'Tira de la barra hasta la altura del pecho, controlando el movimiento.'
  },
  'Mantenha as costas retas, puxe os cotovelos para trás.': {
    'pt-BR': 'Mantenha as costas retas, puxe os cotovelos para trás.',
    'en-US': 'Keep your back straight, pull your elbows back.',
    'es-ES': 'Mantén la espalda recta, tira los codos hacia atrás.'
  },
  'Eleve os braços até a linha dos ombros, mantenha uma leve flexão nos cotovelos.': {
    'pt-BR': 'Eleve os braços até a linha dos ombros, mantenha uma leve flexão nos cotovelos.',
    'en-US': 'Raise your arms to shoulder level, keep a slight bend in your elbows.',
    'es-ES': 'Eleva los brazos hasta la línea de los hombros, mantén una ligera flexión en los codos.'
  },
  'Flexione os braços mantendo os cotovelos fixos ao lado do corpo.': {
    'pt-BR': 'Flexione os braços mantendo os cotovelos fixos ao lado do corpo.',
    'en-US': 'Curl your arms keeping your elbows fixed at your sides.',
    'es-ES': 'Flexiona los brazos manteniendo los codos fijos al lado del cuerpo.'
  },
};

// ==================== FUNÇÕES HELPER ====================

/**
 * Traduz nome de exercício
 */
export function translateExercise(name: string, language: SupportedLanguage): string {
  return exerciseTranslations[name]?.[language] || name;
}

/**
 * Traduz nome de alimento
 */
export function translateFood(name: string, language: SupportedLanguage): string {
  // Se o idioma é português, retorna o original
  if (language === 'pt-BR') {
    return name;
  }
  
  // Tenta match exato primeiro
  if (foodTranslations[name]?.[language]) {
    return foodTranslations[name][language];
  }
  
  // Normaliza o nome para comparação (remove quantidades como "200g", "100ml")
  const nameWithoutQuantity = name.replace(/\s*\d+\s*(g|ml|kg|l|unidade|unidades|fatia|fatias)?\s*$/i, '').trim();
  
  // Tenta match exato sem quantidade
  if (foodTranslations[nameWithoutQuantity]?.[language]) {
    const quantityMatch = name.match(/\s*(\d+\s*(g|ml|kg|l|unidade|unidades|fatia|fatias)?)\s*$/i);
    const quantity = quantityMatch ? quantityMatch[0] : '';
    return foodTranslations[nameWithoutQuantity][language] + quantity;
  }
  
  // Tenta match com palavras-chave (do maior para menor para evitar substituições parciais incorretas)
  const sortedKeys = Object.keys(foodTranslations).sort((a, b) => b.length - a.length);
  
  for (const key of sortedKeys) {
    const keyLower = key.toLowerCase();
    const nameLower = name.toLowerCase();
    
    // Verifica se o nome começa com a chave (para evitar "Ovo" substituir parte de "Ovos")
    if (nameLower === keyLower || nameLower.startsWith(keyLower + ' ')) {
      const restOfName = name.substring(key.length);
      return foodTranslations[key][language] + restOfName;
    }
  }
  
  return name;
}

/**
 * Traduz nome de refeição
 */
export function translateMealName(name: string, language: SupportedLanguage): string {
  return mealNameTranslations[name]?.[language] || name;
}

/**
 * Traduz nome de treino
 */
export function translateWorkoutName(name: string, language: SupportedLanguage): string {
  // Tenta match exato
  if (workoutNameTranslations[name]?.[language]) {
    return workoutNameTranslations[name][language];
  }
  
  // Tenta substituir partes do nome
  let translated = name;
  for (const [key, translations] of Object.entries(workoutNameTranslations)) {
    if (translated.includes(key)) {
      translated = translated.replace(key, translations[language]);
    }
  }
  
  return translated;
}

/**
 * Traduz instruções de exercício
 */
export function translateExerciseNotes(notes: string, language: SupportedLanguage): string {
  if (!notes) return '';
  
  // Se português, retorna original
  if (language === 'pt-BR') return notes;
  
  // Tenta match exato primeiro
  if (exerciseInstructionsTranslations[notes]?.[language]) {
    return exerciseInstructionsTranslations[notes][language];
  }
  
  // Dicionário de termos comuns em instruções
  const instructionTerms: Record<string, Record<SupportedLanguage, string>> = {
    // Movimentos básicos
    'mantenha': { 'pt-BR': 'mantenha', 'en-US': 'keep', 'es-ES': 'mantén' },
    'Mantenha': { 'pt-BR': 'Mantenha', 'en-US': 'Keep', 'es-ES': 'Mantén' },
    'segure': { 'pt-BR': 'segure', 'en-US': 'hold', 'es-ES': 'sostén' },
    'Segure': { 'pt-BR': 'Segure', 'en-US': 'Hold', 'es-ES': 'Sostén' },
    'contraia': { 'pt-BR': 'contraia', 'en-US': 'contract', 'es-ES': 'contrae' },
    'Contraia': { 'pt-BR': 'Contraia', 'en-US': 'Contract', 'es-ES': 'Contrae' },
    'desça': { 'pt-BR': 'desça', 'en-US': 'lower', 'es-ES': 'baja' },
    'Desça': { 'pt-BR': 'Desça', 'en-US': 'Lower', 'es-ES': 'Baja' },
    'suba': { 'pt-BR': 'suba', 'en-US': 'raise', 'es-ES': 'sube' },
    'Suba': { 'pt-BR': 'Suba', 'en-US': 'Raise', 'es-ES': 'Sube' },
    'empurre': { 'pt-BR': 'empurre', 'en-US': 'push', 'es-ES': 'empuja' },
    'Empurre': { 'pt-BR': 'Empurre', 'en-US': 'Push', 'es-ES': 'Empuja' },
    'puxe': { 'pt-BR': 'puxe', 'en-US': 'pull', 'es-ES': 'tira' },
    'Puxe': { 'pt-BR': 'Puxe', 'en-US': 'Pull', 'es-ES': 'Tira' },
    'estenda': { 'pt-BR': 'estenda', 'en-US': 'extend', 'es-ES': 'extiende' },
    'Estenda': { 'pt-BR': 'Estenda', 'en-US': 'Extend', 'es-ES': 'Extiende' },
    'flexione': { 'pt-BR': 'flexione', 'en-US': 'flex', 'es-ES': 'flexiona' },
    'Flexione': { 'pt-BR': 'Flexione', 'en-US': 'Flex', 'es-ES': 'Flexiona' },
    'expire': { 'pt-BR': 'expire', 'en-US': 'exhale', 'es-ES': 'exhala' },
    'Expire': { 'pt-BR': 'Expire', 'en-US': 'Exhale', 'es-ES': 'Exhala' },
    'inspire': { 'pt-BR': 'inspire', 'en-US': 'inhale', 'es-ES': 'inhala' },
    'Inspire': { 'pt-BR': 'Inspire', 'en-US': 'Inhale', 'es-ES': 'Inhala' },
    'respire': { 'pt-BR': 'respire', 'en-US': 'breathe', 'es-ES': 'respira' },
    'Respire': { 'pt-BR': 'Respire', 'en-US': 'Breathe', 'es-ES': 'Respira' },
    
    // Partes do corpo
    'costas': { 'pt-BR': 'costas', 'en-US': 'back', 'es-ES': 'espalda' },
    'peito': { 'pt-BR': 'peito', 'en-US': 'chest', 'es-ES': 'pecho' },
    'ombros': { 'pt-BR': 'ombros', 'en-US': 'shoulders', 'es-ES': 'hombros' },
    'braços': { 'pt-BR': 'braços', 'en-US': 'arms', 'es-ES': 'brazos' },
    'pernas': { 'pt-BR': 'pernas', 'en-US': 'legs', 'es-ES': 'piernas' },
    'joelhos': { 'pt-BR': 'joelhos', 'en-US': 'knees', 'es-ES': 'rodillas' },
    'cotovelos': { 'pt-BR': 'cotovelos', 'en-US': 'elbows', 'es-ES': 'codos' },
    'quadril': { 'pt-BR': 'quadril', 'en-US': 'hips', 'es-ES': 'cadera' },
    'abdômen': { 'pt-BR': 'abdômen', 'en-US': 'core', 'es-ES': 'abdomen' },
    'glúteos': { 'pt-BR': 'glúteos', 'en-US': 'glutes', 'es-ES': 'glúteos' },
    'coluna': { 'pt-BR': 'coluna', 'en-US': 'spine', 'es-ES': 'columna' },
    
    // Posições e descrições
    'reto': { 'pt-BR': 'reto', 'en-US': 'straight', 'es-ES': 'recto' },
    'reta': { 'pt-BR': 'reta', 'en-US': 'straight', 'es-ES': 'recta' },
    'retas': { 'pt-BR': 'retas', 'en-US': 'straight', 'es-ES': 'rectas' },
    'controlado': { 'pt-BR': 'controlado', 'en-US': 'controlled', 'es-ES': 'controlado' },
    'lentamente': { 'pt-BR': 'lentamente', 'en-US': 'slowly', 'es-ES': 'lentamente' },
    'devagar': { 'pt-BR': 'devagar', 'en-US': 'slowly', 'es-ES': 'despacio' },
    'movimento': { 'pt-BR': 'movimento', 'en-US': 'movement', 'es-ES': 'movimiento' },
    'posição inicial': { 'pt-BR': 'posição inicial', 'en-US': 'starting position', 'es-ES': 'posición inicial' },
    'posição': { 'pt-BR': 'posição', 'en-US': 'position', 'es-ES': 'posición' },
    'repetição': { 'pt-BR': 'repetição', 'en-US': 'rep', 'es-ES': 'repetición' },
    'repetições': { 'pt-BR': 'repetições', 'en-US': 'reps', 'es-ES': 'repeticiones' },
    'série': { 'pt-BR': 'série', 'en-US': 'set', 'es-ES': 'serie' },
    'séries': { 'pt-BR': 'séries', 'en-US': 'sets', 'es-ES': 'series' },
    'contração': { 'pt-BR': 'contração', 'en-US': 'contraction', 'es-ES': 'contracción' },
    'máxima': { 'pt-BR': 'máxima', 'en-US': 'maximum', 'es-ES': 'máxima' },
    'força': { 'pt-BR': 'força', 'en-US': 'strength', 'es-ES': 'fuerza' },
    
    // Equipamentos
    'barra': { 'pt-BR': 'barra', 'en-US': 'bar', 'es-ES': 'barra' },
    'halter': { 'pt-BR': 'halter', 'en-US': 'dumbbell', 'es-ES': 'mancuerna' },
    'halteres': { 'pt-BR': 'halteres', 'en-US': 'dumbbells', 'es-ES': 'mancuernas' },
    'banco': { 'pt-BR': 'banco', 'en-US': 'bench', 'es-ES': 'banco' },
    'cabo': { 'pt-BR': 'cabo', 'en-US': 'cable', 'es-ES': 'cable' },
    'polia': { 'pt-BR': 'polia', 'en-US': 'pulley', 'es-ES': 'polea' },
    'máquina': { 'pt-BR': 'máquina', 'en-US': 'machine', 'es-ES': 'máquina' },
    
    // Frases comuns
    'com os pés na largura dos ombros': { 'pt-BR': 'com os pés na largura dos ombros', 'en-US': 'with feet shoulder-width apart', 'es-ES': 'con los pies a la anchura de los hombros' },
    'mantendo a coluna reta': { 'pt-BR': 'mantendo a coluna reta', 'en-US': 'keeping your spine straight', 'es-ES': 'manteniendo la columna recta' },
    'controle o movimento': { 'pt-BR': 'controle o movimento', 'en-US': 'control the movement', 'es-ES': 'controla el movimiento' },
    'não use impulso': { 'pt-BR': 'não use impulso', 'en-US': 'do not use momentum', 'es-ES': 'no uses impulso' },
    'sem impulso': { 'pt-BR': 'sem impulso', 'en-US': 'without momentum', 'es-ES': 'sin impulso' },
    'volte à posição inicial': { 'pt-BR': 'volte à posição inicial', 'en-US': 'return to the starting position', 'es-ES': 'vuelve a la posición inicial' },
  };
  
  // Traduz os termos encontrados
  let translated = notes;
  
  // Ordena as chaves por tamanho (maior para menor) para evitar substituições parciais
  const sortedKeys = Object.keys(instructionTerms).sort((a, b) => b.length - a.length);
  
  for (const key of sortedKeys) {
    if (translated.toLowerCase().includes(key.toLowerCase())) {
      // Usa regex para substituição case-insensitive mas preservando a estrutura original
      const regex = new RegExp(key, 'gi');
      translated = translated.replace(regex, instructionTerms[key][language]);
    }
  }
  
  return translated;
}
