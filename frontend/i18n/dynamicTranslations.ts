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
  'Pão Integral': { 'pt-BR': 'Pão Integral', 'en-US': 'Whole Wheat Bread', 'es-ES': 'Pan Integral' },
  'Aveia': { 'pt-BR': 'Aveia', 'en-US': 'Oatmeal', 'es-ES': 'Avena' },
  'Tapioca': { 'pt-BR': 'Tapioca', 'en-US': 'Tapioca', 'es-ES': 'Tapioca' },
  'Mandioca': { 'pt-BR': 'Mandioca', 'en-US': 'Cassava', 'es-ES': 'Yuca' },
  'Inhame': { 'pt-BR': 'Inhame', 'en-US': 'Yam', 'es-ES': 'Ñame' },
  'Cuscuz': { 'pt-BR': 'Cuscuz', 'en-US': 'Couscous', 'es-ES': 'Cuscús' },
  'Quinoa': { 'pt-BR': 'Quinoa', 'en-US': 'Quinoa', 'es-ES': 'Quinoa' },
  'Banana': { 'pt-BR': 'Banana', 'en-US': 'Banana', 'es-ES': 'Plátano' },
  'Maçã': { 'pt-BR': 'Maçã', 'en-US': 'Apple', 'es-ES': 'Manzana' },
  'Laranja': { 'pt-BR': 'Laranja', 'en-US': 'Orange', 'es-ES': 'Naranja' },
  'Morango': { 'pt-BR': 'Morango', 'en-US': 'Strawberry', 'es-ES': 'Fresa' },
  'Mamão': { 'pt-BR': 'Mamão', 'en-US': 'Papaya', 'es-ES': 'Papaya' },
  'Melão': { 'pt-BR': 'Melão', 'en-US': 'Melon', 'es-ES': 'Melón' },
  'Melancia': { 'pt-BR': 'Melancia', 'en-US': 'Watermelon', 'es-ES': 'Sandía' },
  'Uva': { 'pt-BR': 'Uva', 'en-US': 'Grape', 'es-ES': 'Uva' },
  'Manga': { 'pt-BR': 'Manga', 'en-US': 'Mango', 'es-ES': 'Mango' },
  
  // Gorduras
  'Azeite': { 'pt-BR': 'Azeite', 'en-US': 'Olive Oil', 'es-ES': 'Aceite de Oliva' },
  'Azeite de Oliva': { 'pt-BR': 'Azeite de Oliva', 'en-US': 'Olive Oil', 'es-ES': 'Aceite de Oliva' },
  'Castanha': { 'pt-BR': 'Castanha', 'en-US': 'Nuts', 'es-ES': 'Nueces' },
  'Castanha do Pará': { 'pt-BR': 'Castanha do Pará', 'en-US': 'Brazil Nuts', 'es-ES': 'Nueces de Brasil' },
  'Castanha de Caju': { 'pt-BR': 'Castanha de Caju', 'en-US': 'Cashews', 'es-ES': 'Anacardos' },
  'Amendoim': { 'pt-BR': 'Amendoim', 'en-US': 'Peanuts', 'es-ES': 'Cacahuetes' },
  'Pasta de Amendoim': { 'pt-BR': 'Pasta de Amendoim', 'en-US': 'Peanut Butter', 'es-ES': 'Mantequilla de Maní' },
  'Amêndoas': { 'pt-BR': 'Amêndoas', 'en-US': 'Almonds', 'es-ES': 'Almendras' },
  'Nozes': { 'pt-BR': 'Nozes', 'en-US': 'Walnuts', 'es-ES': 'Nueces' },
  'Abacate': { 'pt-BR': 'Abacate', 'en-US': 'Avocado', 'es-ES': 'Aguacate' },
  'Coco': { 'pt-BR': 'Coco', 'en-US': 'Coconut', 'es-ES': 'Coco' },
  'Óleo de Coco': { 'pt-BR': 'Óleo de Coco', 'en-US': 'Coconut Oil', 'es-ES': 'Aceite de Coco' },
  
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
  'Estenda os braços completamente, contraia o tríceps no topo do movimento.': {
    'pt-BR': 'Estenda os braços completamente, contraia o tríceps no topo do movimento.',
    'en-US': 'Fully extend your arms, squeeze the triceps at the top of the movement.',
    'es-ES': 'Extiende los brazos completamente, contrae el tríceps en la parte superior del movimiento.'
  },
  'Desça até as coxas ficarem paralelas ao chão, mantenha os joelhos alinhados com os pés.': {
    'pt-BR': 'Desça até as coxas ficarem paralelas ao chão, mantenha os joelhos alinhados com os pés.',
    'en-US': 'Lower until your thighs are parallel to the floor, keep your knees aligned with your feet.',
    'es-ES': 'Baja hasta que los muslos estén paralelos al suelo, mantén las rodillas alineadas con los pies.'
  },
  'Empurre a plataforma controlando a descida, não trave os joelhos.': {
    'pt-BR': 'Empurre a plataforma controlando a descida, não trave os joelhos.',
    'en-US': 'Push the platform while controlling the descent, don\'t lock your knees.',
    'es-ES': 'Empuja la plataforma controlando el descenso, no bloquees las rodillas.'
  },
  'Estenda as pernas completamente, contraia o quadríceps no topo.': {
    'pt-BR': 'Estenda as pernas completamente, contraia o quadríceps no topo.',
    'en-US': 'Fully extend your legs, squeeze the quadriceps at the top.',
    'es-ES': 'Extiende las piernas completamente, contrae el cuádriceps en la parte superior.'
  },
  'Flexione as pernas até onde conseguir, contraia os isquiotibiais.': {
    'pt-BR': 'Flexione as pernas até onde conseguir, contraia os isquiotibiais.',
    'en-US': 'Curl your legs as far as you can, squeeze the hamstrings.',
    'es-ES': 'Flexiona las piernas lo más que puedas, contrae los isquiotibiales.'
  },
  'Mantenha o core contraído durante todo o movimento.': {
    'pt-BR': 'Mantenha o core contraído durante todo o movimento.',
    'en-US': 'Keep your core engaged throughout the movement.',
    'es-ES': 'Mantén el core contraído durante todo el movimiento.'
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
