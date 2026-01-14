"""
Workout Module - Translations / Traduções / Traducciones
=========================================================
Multilingual support for exercise names and workout UI strings
"""

# Supported languages
LANGUAGES = ['pt', 'en', 'es']
DEFAULT_LANGUAGE = 'pt'

# Exercise name translations
EXERCISE_TRANSLATIONS = {
    # === PEITO / CHEST / PECHO ===
    "Supino Reto na Máquina": {
        "pt": "Supino Reto na Máquina",
        "en": "Machine Flat Bench Press",
        "es": "Press de Banca Plano en Máquina"
    },
    "Supino Inclinado na Máquina": {
        "pt": "Supino Inclinado na Máquina",
        "en": "Machine Incline Bench Press",
        "es": "Press Inclinado en Máquina"
    },
    "Crucifixo na Máquina (Peck Deck)": {
        "pt": "Crucifixo na Máquina (Peck Deck)",
        "en": "Pec Deck Machine Fly",
        "es": "Aperturas en Máquina (Pec Deck)"
    },
    "Cross Over Polia Alta": {
        "pt": "Cross Over Polia Alta",
        "en": "High Cable Crossover",
        "es": "Cruce de Cables Alto"
    },
    "Elevação Lateral Halteres": {
        "pt": "Elevação Lateral Halteres",
        "en": "Dumbbell Lateral Raise",
        "es": "Elevaciones Laterales con Mancuernas"
    },
    
    # === COSTAS / BACK / ESPALDA ===
    "Puxada Frontal Pegada Aberta": {
        "pt": "Puxada Frontal Pegada Aberta",
        "en": "Wide Grip Lat Pulldown",
        "es": "Jalón al Pecho Agarre Ancho"
    },
    "Puxada Pegada Neutra (Triângulo)": {
        "pt": "Puxada Pegada Neutra (Triângulo)",
        "en": "Neutral Grip Lat Pulldown",
        "es": "Jalón Agarre Neutro (Triángulo)"
    },
    "Remada Máquina Pegada Neutra": {
        "pt": "Remada Máquina Pegada Neutra",
        "en": "Machine Row Neutral Grip",
        "es": "Remo en Máquina Agarre Neutro"
    },
    "Remada Máquina Pegada Pronada": {
        "pt": "Remada Máquina Pegada Pronada",
        "en": "Machine Row Overhand Grip",
        "es": "Remo en Máquina Agarre Prono"
    },
    "Voador Invertido (Peck Deck)": {
        "pt": "Voador Invertido (Peck Deck)",
        "en": "Reverse Pec Deck Fly",
        "es": "Aperturas Invertidas (Pec Deck)"
    },
    "Remada Baixa Polia (Triângulo)": {
        "pt": "Remada Baixa Polia (Triângulo)",
        "en": "Seated Cable Row",
        "es": "Remo Bajo en Polea"
    },
    
    # === OMBROS / SHOULDERS / HOMBROS ===
    "Desenvolvimento Máquina": {
        "pt": "Desenvolvimento Máquina",
        "en": "Machine Shoulder Press",
        "es": "Press de Hombros en Máquina"
    },
    "Elevação Lateral Máquina": {
        "pt": "Elevação Lateral Máquina",
        "en": "Machine Lateral Raise",
        "es": "Elevaciones Laterales en Máquina"
    },
    
    # === BÍCEPS / BICEPS / BÍCEPS ===
    "Rosca Direta Barra": {
        "pt": "Rosca Direta Barra",
        "en": "Barbell Curl",
        "es": "Curl con Barra"
    },
    "Rosca Martelo Halteres": {
        "pt": "Rosca Martelo Halteres",
        "en": "Hammer Curl",
        "es": "Curl Martillo"
    },
    "Rosca Alternada Halteres": {
        "pt": "Rosca Alternada Halteres",
        "en": "Alternating Dumbbell Curl",
        "es": "Curl Alternado con Mancuernas"
    },
    "Rosca Scott Máquina": {
        "pt": "Rosca Scott Máquina",
        "en": "Preacher Curl Machine",
        "es": "Curl Scott en Máquina"
    },
    
    # === TRÍCEPS / TRICEPS / TRÍCEPS ===
    "Tríceps Corda (Polia Alta)": {
        "pt": "Tríceps Corda (Polia Alta)",
        "en": "Cable Rope Tricep Pushdown",
        "es": "Extensiones de Tríceps con Cuerda"
    },
    "Tríceps Francês Halter": {
        "pt": "Tríceps Francês Halter",
        "en": "Dumbbell French Press",
        "es": "Press Francés con Mancuerna"
    },
    "Tríceps Barra Reta (Polia Alta)": {
        "pt": "Tríceps Barra Reta (Polia Alta)",
        "en": "Cable Bar Tricep Pushdown",
        "es": "Extensiones de Tríceps con Barra"
    },
    "Tríceps Máquina": {
        "pt": "Tríceps Máquina",
        "en": "Tricep Machine",
        "es": "Tríceps en Máquina"
    },
    
    # === QUADRÍCEPS / QUADS / CUÁDRICEPS ===
    "Leg Press 45°": {
        "pt": "Leg Press 45°",
        "en": "45° Leg Press",
        "es": "Prensa de Piernas 45°"
    },
    "Cadeira Extensora": {
        "pt": "Cadeira Extensora",
        "en": "Leg Extension Machine",
        "es": "Extensión de Piernas"
    },
    "Agachamento no Smith Machine": {
        "pt": "Agachamento no Smith Machine",
        "en": "Smith Machine Squat",
        "es": "Sentadilla en Máquina Smith"
    },
    "Leg Press Horizontal": {
        "pt": "Leg Press Horizontal",
        "en": "Horizontal Leg Press",
        "es": "Prensa de Piernas Horizontal"
    },
    
    # === POSTERIOR / HAMSTRINGS / ISQUIOTIBIALES ===
    "Mesa Flexora": {
        "pt": "Mesa Flexora",
        "en": "Lying Leg Curl",
        "es": "Curl Femoral Acostado"
    },
    "Cadeira Flexora (Sentado)": {
        "pt": "Cadeira Flexora (Sentado)",
        "en": "Seated Leg Curl",
        "es": "Curl Femoral Sentado"
    },
    "Stiff na Máquina Smith": {
        "pt": "Stiff na Máquina Smith",
        "en": "Smith Machine Stiff Leg Deadlift",
        "es": "Peso Muerto Rumano en Smith"
    },
    "Glúteo na Máquina (Kick Back)": {
        "pt": "Glúteo na Máquina (Kick Back)",
        "en": "Glute Kickback Machine",
        "es": "Glúteos en Máquina"
    },
    
    # === PANTURRILHA / CALVES / PANTORRILLAS ===
    "Panturrilha no Leg Press": {
        "pt": "Panturrilha no Leg Press",
        "en": "Calf Press on Leg Press",
        "es": "Gemelos en Prensa"
    },
    "Panturrilha Sentado na Máquina": {
        "pt": "Panturrilha Sentado na Máquina",
        "en": "Seated Calf Raise Machine",
        "es": "Gemelos Sentado en Máquina"
    },
    "Panturrilha em Pé na Máquina": {
        "pt": "Panturrilha em Pé na Máquina",
        "en": "Standing Calf Raise Machine",
        "es": "Gemelos de Pie en Máquina"
    },
    
    # === ABDÔMEN / ABS / ABDOMINALES ===
    "Abdominal na Máquina": {
        "pt": "Abdominal na Máquina",
        "en": "Ab Machine Crunch",
        "es": "Abdominales en Máquina"
    },
    "Abdominal na Polia Alta (Corda)": {
        "pt": "Abdominal na Polia Alta (Corda)",
        "en": "Cable Crunch",
        "es": "Abdominales en Polea Alta"
    },
    "Prancha Isométrica": {
        "pt": "Prancha Isométrica",
        "en": "Plank Hold",
        "es": "Plancha Isométrica"
    },
    "Elevação de Pernas no Apoio": {
        "pt": "Elevação de Pernas no Apoio",
        "en": "Hanging Leg Raise",
        "es": "Elevación de Piernas Colgado"
    },
}

# Muscle group translations
MUSCLE_GROUP_TRANSLATIONS = {
    "peito": {
        "pt": "Peito",
        "en": "Chest",
        "es": "Pecho"
    },
    "costas": {
        "pt": "Costas",
        "en": "Back",
        "es": "Espalda"
    },
    "ombros": {
        "pt": "Ombros",
        "en": "Shoulders",
        "es": "Hombros"
    },
    "biceps": {
        "pt": "Bíceps",
        "en": "Biceps",
        "es": "Bíceps"
    },
    "triceps": {
        "pt": "Tríceps",
        "en": "Triceps",
        "es": "Tríceps"
    },
    "quadriceps": {
        "pt": "Quadríceps",
        "en": "Quadriceps",
        "es": "Cuádriceps"
    },
    "posterior": {
        "pt": "Posterior de Coxa",
        "en": "Hamstrings",
        "es": "Isquiotibiales"
    },
    "panturrilha": {
        "pt": "Panturrilha",
        "en": "Calves",
        "es": "Pantorrillas"
    },
    "abdomen": {
        "pt": "Abdômen",
        "en": "Abs",
        "es": "Abdominales"
    },
}

# Workout day name translations
WORKOUT_DAY_TRANSLATIONS = {
    "Full Body": {
        "pt": "Corpo Inteiro",
        "en": "Full Body",
        "es": "Cuerpo Completo"
    },
    "Upper": {
        "pt": "Superior",
        "en": "Upper Body",
        "es": "Tren Superior"
    },
    "Lower": {
        "pt": "Inferior",
        "en": "Lower Body",
        "es": "Tren Inferior"
    },
    "A - Push": {
        "pt": "A - Empurrar",
        "en": "A - Push",
        "es": "A - Empuje"
    },
    "B - Pull": {
        "pt": "B - Puxar",
        "en": "B - Pull",
        "es": "B - Jalón"
    },
    "C - Legs": {
        "pt": "C - Pernas",
        "en": "C - Legs",
        "es": "C - Piernas"
    },
    "A - Peito/Tríceps": {
        "pt": "A - Peito/Tríceps",
        "en": "A - Chest/Triceps",
        "es": "A - Pecho/Tríceps"
    },
    "B - Costas/Bíceps": {
        "pt": "B - Costas/Bíceps",
        "en": "B - Back/Biceps",
        "es": "B - Espalda/Bíceps"
    },
    "C - Pernas": {
        "pt": "C - Pernas",
        "en": "C - Legs",
        "es": "C - Piernas"
    },
    "D - Ombros/Abdômen": {
        "pt": "D - Ombros/Abdômen",
        "en": "D - Shoulders/Abs",
        "es": "D - Hombros/Abdominales"
    },
}

# Focus area translations
FOCUS_TRANSLATIONS = {
    "Peitoral Médio": {
        "pt": "Peitoral Médio",
        "en": "Mid Chest",
        "es": "Pectoral Medio"
    },
    "Peitoral Superior": {
        "pt": "Peitoral Superior",
        "en": "Upper Chest",
        "es": "Pectoral Superior"
    },
    "Peitoral Médio - Adução": {
        "pt": "Peitoral Médio - Adução",
        "en": "Mid Chest - Adduction",
        "es": "Pectoral Medio - Aducción"
    },
    "Peitoral Inferior": {
        "pt": "Peitoral Inferior",
        "en": "Lower Chest",
        "es": "Pectoral Inferior"
    },
    "Deltóide Lateral": {
        "pt": "Deltóide Lateral",
        "en": "Lateral Deltoid",
        "es": "Deltoides Lateral"
    },
    "Dorsal (Largura)": {
        "pt": "Dorsal (Largura)",
        "en": "Lats (Width)",
        "es": "Dorsal (Anchura)"
    },
    "Dorsal (Espessura)": {
        "pt": "Dorsal (Espessura)",
        "en": "Lats (Thickness)",
        "es": "Dorsal (Grosor)"
    },
    "Deltóide Posterior": {
        "pt": "Deltóide Posterior",
        "en": "Rear Deltoid",
        "es": "Deltoides Posterior"
    },
    "Deltóide Anterior": {
        "pt": "Deltóide Anterior",
        "en": "Front Deltoid",
        "es": "Deltoides Anterior"
    },
}

# UI strings translations
UI_TRANSLATIONS = {
    "sets": {
        "pt": "séries",
        "en": "sets",
        "es": "series"
    },
    "reps": {
        "pt": "repetições",
        "en": "reps",
        "es": "repeticiones"
    },
    "rest": {
        "pt": "descanso",
        "en": "rest",
        "es": "descanso"
    },
    "duration": {
        "pt": "duração",
        "en": "duration",
        "es": "duración"
    },
    "minutes": {
        "pt": "minutos",
        "en": "minutes",
        "es": "minutos"
    },
    "seconds": {
        "pt": "segundos",
        "en": "seconds",
        "es": "segundos"
    },
}


def get_exercise_name(exercise_name: str, language: str = 'pt') -> str:
    """Get translated exercise name"""
    if exercise_name in EXERCISE_TRANSLATIONS:
        return EXERCISE_TRANSLATIONS[exercise_name].get(language, EXERCISE_TRANSLATIONS[exercise_name]['pt'])
    return exercise_name


def get_muscle_group_name(muscle: str, language: str = 'pt') -> str:
    """Get translated muscle group name"""
    if muscle in MUSCLE_GROUP_TRANSLATIONS:
        return MUSCLE_GROUP_TRANSLATIONS[muscle].get(language, MUSCLE_GROUP_TRANSLATIONS[muscle]['pt'])
    return muscle


def get_workout_day_name(day_name: str, language: str = 'pt') -> str:
    """Get translated workout day name"""
    if day_name in WORKOUT_DAY_TRANSLATIONS:
        return WORKOUT_DAY_TRANSLATIONS[day_name].get(language, WORKOUT_DAY_TRANSLATIONS[day_name]['pt'])
    return day_name


def get_focus_name(focus: str, language: str = 'pt') -> str:
    """Get translated focus area name"""
    if focus in FOCUS_TRANSLATIONS:
        return FOCUS_TRANSLATIONS[focus].get(language, FOCUS_TRANSLATIONS[focus]['pt'])
    return focus


def translate_exercise(exercise: dict, language: str = 'pt') -> dict:
    """Translate an exercise dict"""
    translated = exercise.copy()
    
    if 'name' in exercise:
        translated['name'] = get_exercise_name(exercise['name'], language)
    
    if 'muscle_group' in exercise:
        translated['muscle_group'] = get_muscle_group_name(exercise['muscle_group'], language)
    
    if 'focus' in exercise and exercise['focus']:
        translated['focus'] = get_focus_name(exercise['focus'], language)
    
    return translated


def translate_workout_day(workout_day: dict, language: str = 'pt') -> dict:
    """Translate a workout day dict"""
    translated = workout_day.copy()
    
    if 'name' in workout_day:
        translated['name'] = get_workout_day_name(workout_day['name'], language)
    
    if 'exercises' in workout_day:
        translated['exercises'] = [translate_exercise(e, language) for e in workout_day['exercises']]
    
    return translated


def translate_workout_plan(workout_plan: dict, language: str = 'pt') -> dict:
    """Translate entire workout plan"""
    translated = workout_plan.copy()
    
    if 'workout_days' in workout_plan:
        translated['workout_days'] = [translate_workout_day(d, language) for d in workout_plan['workout_days']]
    
    return translated
