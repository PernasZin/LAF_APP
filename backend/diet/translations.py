"""
Diet Module - Translations / Traduções / Traducciones
======================================================
Multilingual support for food names and UI strings
"""

# Supported languages
LANGUAGES = ['pt', 'en', 'es']
DEFAULT_LANGUAGE = 'pt'

# Food name translations
FOOD_TRANSLATIONS = {
    # === PROTEÍNAS / PROTEINS / PROTEÍNAS ===
    "frango": {
        "pt": "Peito de Frango",
        "en": "Chicken Breast",
        "es": "Pechuga de Pollo"
    },
    "coxa_frango": {
        "pt": "Coxa de Frango",
        "en": "Chicken Thigh",
        "es": "Muslo de Pollo"
    },
    "patinho": {
        "pt": "Patinho (Carne Magra)",
        "en": "Lean Beef",
        "es": "Carne Magra"
    },
    "carne_moida": {
        "pt": "Carne Moída",
        "en": "Ground Beef",
        "es": "Carne Molida"
    },
    "suino": {
        "pt": "Carne Suína",
        "en": "Pork",
        "es": "Cerdo"
    },
    "ovos": {
        "pt": "Ovos Inteiros",
        "en": "Whole Eggs",
        "es": "Huevos Enteros"
    },
    "claras": {
        "pt": "Claras de Ovo",
        "en": "Egg Whites",
        "es": "Claras de Huevo"
    },
    "tilapia": {
        "pt": "Tilápia",
        "en": "Tilapia",
        "es": "Tilapia"
    },
    "atum": {
        "pt": "Atum",
        "en": "Tuna",
        "es": "Atún"
    },
    "salmao": {
        "pt": "Salmão",
        "en": "Salmon",
        "es": "Salmón"
    },
    "camarao": {
        "pt": "Camarão",
        "en": "Shrimp",
        "es": "Camarón"
    },
    "sardinha": {
        "pt": "Sardinha",
        "en": "Sardines",
        "es": "Sardinas"
    },
    "peru": {
        "pt": "Peru",
        "en": "Turkey",
        "es": "Pavo"
    },
    "cottage": {
        "pt": "Queijo Cottage",
        "en": "Cottage Cheese",
        "es": "Queso Cottage"
    },
    "iogurte_zero": {
        "pt": "Iogurte Zero",
        "en": "Zero Sugar Yogurt",
        "es": "Yogurt Sin Azúcar"
    },
    "whey_protein": {
        "pt": "Whey Protein",
        "en": "Whey Protein",
        "es": "Proteína Whey"
    },
    "requeijao_light": {
        "pt": "Requeijão Light",
        "en": "Light Cream Cheese",
        "es": "Queso Crema Light"
    },
    "tofu": {
        "pt": "Tofu",
        "en": "Tofu",
        "es": "Tofu"
    },
    "tempeh": {
        "pt": "Tempeh",
        "en": "Tempeh",
        "es": "Tempeh"
    },
    "seitan": {
        "pt": "Seitan",
        "en": "Seitan",
        "es": "Seitán"
    },
    "edamame": {
        "pt": "Edamame",
        "en": "Edamame",
        "es": "Edamame"
    },
    "grao_de_bico": {
        "pt": "Grão de Bico",
        "en": "Chickpeas",
        "es": "Garbanzos"
    },
    "proteina_ervilha": {
        "pt": "Proteína de Ervilha",
        "en": "Pea Protein",
        "es": "Proteína de Guisante"
    },
    
    # === CARBOIDRATOS / CARBS / CARBOHIDRATOS ===
    "arroz_branco": {
        "pt": "Arroz Branco",
        "en": "White Rice",
        "es": "Arroz Blanco"
    },
    "arroz_integral": {
        "pt": "Arroz Integral",
        "en": "Brown Rice",
        "es": "Arroz Integral"
    },
    "batata_doce": {
        "pt": "Batata Doce",
        "en": "Sweet Potato",
        "es": "Batata"
    },
    "aveia": {
        "pt": "Aveia",
        "en": "Oats",
        "es": "Avena"
    },
    "macarrao": {
        "pt": "Macarrão",
        "en": "Pasta",
        "es": "Pasta"
    },
    "macarrao_integral": {
        "pt": "Macarrão Integral",
        "en": "Whole Wheat Pasta",
        "es": "Pasta Integral"
    },
    "pao": {
        "pt": "Pão Francês",
        "en": "French Bread",
        "es": "Pan Francés"
    },
    "pao_integral": {
        "pt": "Pão Integral",
        "en": "Whole Wheat Bread",
        "es": "Pan Integral"
    },
    "pao_forma": {
        "pt": "Pão de Forma",
        "en": "Sliced Bread",
        "es": "Pan de Molde"
    },
    "tapioca": {
        "pt": "Tapioca",
        "en": "Tapioca",
        "es": "Tapioca"
    },
    "feijao": {
        "pt": "Feijão",
        "en": "Beans",
        "es": "Frijoles"
    },
    "lentilha": {
        "pt": "Lentilha",
        "en": "Lentils",
        "es": "Lentejas"
    },
    "farofa": {
        "pt": "Farofa",
        "en": "Toasted Cassava Flour",
        "es": "Farofa"
    },
    "granola": {
        "pt": "Granola",
        "en": "Granola",
        "es": "Granola"
    },
    
    # === GORDURAS / FATS / GRASAS ===
    "azeite": {
        "pt": "Azeite de Oliva",
        "en": "Olive Oil",
        "es": "Aceite de Oliva"
    },
    "pasta_amendoim": {
        "pt": "Pasta de Amendoim",
        "en": "Peanut Butter",
        "es": "Mantequilla de Maní"
    },
    "pasta_amendoa": {
        "pt": "Pasta de Amêndoa",
        "en": "Almond Butter",
        "es": "Mantequilla de Almendra"
    },
    "oleo_coco": {
        "pt": "Óleo de Coco",
        "en": "Coconut Oil",
        "es": "Aceite de Coco"
    },
    "castanhas": {
        "pt": "Castanhas",
        "en": "Cashews",
        "es": "Castañas de Cajú"
    },
    "amendoas": {
        "pt": "Amêndoas",
        "en": "Almonds",
        "es": "Almendras"
    },
    "nozes": {
        "pt": "Nozes",
        "en": "Walnuts",
        "es": "Nueces"
    },
    "chia": {
        "pt": "Chia",
        "en": "Chia Seeds",
        "es": "Semillas de Chía"
    },
    "queijo": {
        "pt": "Queijo",
        "en": "Cheese",
        "es": "Queso"
    },
    
    # === FRUTAS / FRUITS / FRUTAS ===
    "banana": {
        "pt": "Banana",
        "en": "Banana",
        "es": "Plátano"
    },
    "maca": {
        "pt": "Maçã",
        "en": "Apple",
        "es": "Manzana"
    },
    "laranja": {
        "pt": "Laranja",
        "en": "Orange",
        "es": "Naranja"
    },
    "morango": {
        "pt": "Morango",
        "en": "Strawberry",
        "es": "Fresa"
    },
    "mamao": {
        "pt": "Mamão",
        "en": "Papaya",
        "es": "Papaya"
    },
    "manga": {
        "pt": "Manga",
        "en": "Mango",
        "es": "Mango"
    },
    "melancia": {
        "pt": "Melancia",
        "en": "Watermelon",
        "es": "Sandía"
    },
    "abacate": {
        "pt": "Abacate",
        "en": "Avocado",
        "es": "Aguacate"
    },
    "uva": {
        "pt": "Uva",
        "en": "Grapes",
        "es": "Uvas"
    },
    "abacaxi": {
        "pt": "Abacaxi",
        "en": "Pineapple",
        "es": "Piña"
    },
    "melao": {
        "pt": "Melão",
        "en": "Melon",
        "es": "Melón"
    },
    "kiwi": {
        "pt": "Kiwi",
        "en": "Kiwi",
        "es": "Kiwi"
    },
    "pera": {
        "pt": "Pera",
        "en": "Pear",
        "es": "Pera"
    },
    "pessego": {
        "pt": "Pêssego",
        "en": "Peach",
        "es": "Durazno"
    },
    "mirtilo": {
        "pt": "Mirtilo",
        "en": "Blueberry",
        "es": "Arándano"
    },
    "acai": {
        "pt": "Açaí",
        "en": "Açaí",
        "es": "Açaí"
    },
    
    # === VEGETAIS / VEGETABLES / VEGETALES ===
    "salada": {
        "pt": "Salada Verde",
        "en": "Green Salad",
        "es": "Ensalada Verde"
    },
    "alface": {
        "pt": "Alface",
        "en": "Lettuce",
        "es": "Lechuga"
    },
    "rucola": {
        "pt": "Rúcula",
        "en": "Arugula",
        "es": "Rúcula"
    },
    "espinafre": {
        "pt": "Espinafre",
        "en": "Spinach",
        "es": "Espinaca"
    },
    "couve": {
        "pt": "Couve",
        "en": "Kale",
        "es": "Col Rizada"
    },
    "brocolis": {
        "pt": "Brócolis",
        "en": "Broccoli",
        "es": "Brócoli"
    },
    "couve_flor": {
        "pt": "Couve-flor",
        "en": "Cauliflower",
        "es": "Coliflor"
    },
    "cenoura": {
        "pt": "Cenoura",
        "en": "Carrot",
        "es": "Zanahoria"
    },
    "abobrinha": {
        "pt": "Abobrinha",
        "en": "Zucchini",
        "es": "Calabacín"
    },
    "pepino": {
        "pt": "Pepino",
        "en": "Cucumber",
        "es": "Pepino"
    },
    "tomate": {
        "pt": "Tomate",
        "en": "Tomato",
        "es": "Tomate"
    },
    "beterraba": {
        "pt": "Beterraba",
        "en": "Beet",
        "es": "Remolacha"
    },
    "vagem": {
        "pt": "Vagem",
        "en": "Green Beans",
        "es": "Judías Verdes"
    },
    "pimentao": {
        "pt": "Pimentão",
        "en": "Bell Pepper",
        "es": "Pimiento"
    },
    
    # === EXTRAS ===
    "leite_condensado": {
        "pt": "Leite Condensado",
        "en": "Condensed Milk",
        "es": "Leche Condensada"
    },
    "mel": {
        "pt": "Mel",
        "en": "Honey",
        "es": "Miel"
    },
}

# Meal name translations
MEAL_TRANSLATIONS = {
    "cafe_manha": {
        "pt": "Café da Manhã",
        "en": "Breakfast",
        "es": "Desayuno"
    },
    "lanche_manha": {
        "pt": "Lanche da Manhã",
        "en": "Morning Snack",
        "es": "Merienda de la Mañana"
    },
    "almoco": {
        "pt": "Almoço",
        "en": "Lunch",
        "es": "Almuerzo"
    },
    "lanche_tarde": {
        "pt": "Lanche da Tarde",
        "en": "Afternoon Snack",
        "es": "Merienda de la Tarde"
    },
    "jantar": {
        "pt": "Jantar",
        "en": "Dinner",
        "es": "Cena"
    },
    "ceia": {
        "pt": "Ceia",
        "en": "Evening Snack",
        "es": "Cena Ligera"
    },
}

# Unit translations
UNIT_TRANSLATIONS = {
    "filé médio": {
        "pt": "filé médio",
        "en": "medium fillet",
        "es": "filete mediano"
    },
    "coxa média": {
        "pt": "coxa média",
        "en": "medium thigh",
        "es": "muslo mediano"
    },
    "bife médio": {
        "pt": "bife médio",
        "en": "medium steak",
        "es": "bistec mediano"
    },
    "colher sopa cheia": {
        "pt": "colher sopa cheia",
        "en": "heaped tablespoon",
        "es": "cucharada colmada"
    },
    "unidade grande": {
        "pt": "unidade grande",
        "en": "large unit",
        "es": "unidad grande"
    },
    "unidade média": {
        "pt": "unidade média",
        "en": "medium unit",
        "es": "unidad mediana"
    },
    "unidade": {
        "pt": "unidade",
        "en": "unit",
        "es": "unidad"
    },
    "xícara cozida": {
        "pt": "xícara cozida",
        "en": "cooked cup",
        "es": "taza cocida"
    },
    "xícara cozido": {
        "pt": "xícara cozido",
        "en": "cooked cup",
        "es": "taza cocida"
    },
    "xícara": {
        "pt": "xícara",
        "en": "cup",
        "es": "taza"
    },
    "fatia": {
        "pt": "fatia",
        "en": "slice",
        "es": "rebanada"
    },
    "fatia média": {
        "pt": "fatia média",
        "en": "medium slice",
        "es": "rebanada mediana"
    },
    "colher sopa": {
        "pt": "colher sopa",
        "en": "tablespoon",
        "es": "cucharada"
    },
    "concha média": {
        "pt": "concha média",
        "en": "medium ladle",
        "es": "cucharón mediano"
    },
    "lata drenada": {
        "pt": "lata drenada",
        "en": "drained can",
        "es": "lata escurrida"
    },
    "porção média": {
        "pt": "porção média",
        "en": "medium portion",
        "es": "porción mediana"
    },
    "porção": {
        "pt": "porção",
        "en": "portion",
        "es": "porción"
    },
    "fatias finas": {
        "pt": "fatias finas",
        "en": "thin slices",
        "es": "rebanadas finas"
    },
    "garrafa": {
        "pt": "garrafa",
        "en": "bottle",
        "es": "botella"
    },
    "scoop": {
        "pt": "scoop",
        "en": "scoop",
        "es": "medida"
    },
    "unidades": {
        "pt": "unidades",
        "en": "units",
        "es": "unidades"
    },
    "cacho pequeno": {
        "pt": "cacho pequeno",
        "en": "small bunch",
        "es": "racimo pequeño"
    },
    "unidade pequena": {
        "pt": "unidade pequena",
        "en": "small unit",
        "es": "unidad pequeña"
    },
    "metade": {
        "pt": "metade",
        "en": "half",
        "es": "mitad"
    },
    "polpa 100g": {
        "pt": "polpa 100g",
        "en": "100g pulp",
        "es": "pulpa 100g"
    },
    "prato cheio": {
        "pt": "prato cheio",
        "en": "full plate",
        "es": "plato lleno"
    },
    "folhas": {
        "pt": "folhas",
        "en": "leaves",
        "es": "hojas"
    },
    "folhas refogadas": {
        "pt": "folhas refogadas",
        "en": "sautéed leaves",
        "es": "hojas salteadas"
    },
    "maço": {
        "pt": "maço",
        "en": "bunch",
        "es": "manojo"
    },
    "clara": {
        "pt": "clara",
        "en": "white",
        "es": "clara"
    },
    "goma hidratada": {
        "pt": "goma hidratada",
        "en": "hydrated starch",
        "es": "goma hidratada"
    },
}

# Restriction translations
RESTRICTION_TRANSLATIONS = {
    "vegetariano": {
        "pt": "Vegetariano",
        "en": "Vegetarian",
        "es": "Vegetariano"
    },
    "vegano": {
        "pt": "Vegano",
        "en": "Vegan",
        "es": "Vegano"
    },
    "sem_lactose": {
        "pt": "Sem Lactose",
        "en": "Lactose Free",
        "es": "Sin Lactosa"
    },
    "sem_gluten": {
        "pt": "Sem Glúten",
        "en": "Gluten Free",
        "es": "Sin Gluten"
    },
    "diabetico": {
        "pt": "Diabético",
        "en": "Diabetic",
        "es": "Diabético"
    },
    "low_carb": {
        "pt": "Low Carb",
        "en": "Low Carb",
        "es": "Bajo en Carbohidratos"
    },
}

# Supplement translations
SUPPLEMENT_TRANSLATIONS = {
    "creatina": {
        "pt": "Creatina (5g/dia)",
        "en": "Creatine (5g/day)",
        "es": "Creatina (5g/día)"
    },
    "multivitaminico": {
        "pt": "Multivitamínico",
        "en": "Multivitamin",
        "es": "Multivitamínico"
    },
    "omega3": {
        "pt": "Ômega 3",
        "en": "Omega 3",
        "es": "Omega 3"
    },
    "cafeina": {
        "pt": "Cafeína",
        "en": "Caffeine",
        "es": "Cafeína"
    },
    "vitamina_d": {
        "pt": "Vitamina D",
        "en": "Vitamin D",
        "es": "Vitamina D"
    },
    "vitamina_c": {
        "pt": "Vitamina C",
        "en": "Vitamin C",
        "es": "Vitamina C"
    },
    "zinco": {
        "pt": "Zinco",
        "en": "Zinc",
        "es": "Zinc"
    },
    "magnesio": {
        "pt": "Magnésio",
        "en": "Magnesium",
        "es": "Magnesio"
    },
    "colageno": {
        "pt": "Colágeno",
        "en": "Collagen",
        "es": "Colágeno"
    },
}


def get_food_name(food_key: str, language: str = 'pt') -> str:
    """Get translated food name"""
    if food_key in FOOD_TRANSLATIONS:
        return FOOD_TRANSLATIONS[food_key].get(language, FOOD_TRANSLATIONS[food_key]['pt'])
    return food_key


def get_meal_name(meal_key: str, language: str = 'pt') -> str:
    """Get translated meal name"""
    if meal_key in MEAL_TRANSLATIONS:
        return MEAL_TRANSLATIONS[meal_key].get(language, MEAL_TRANSLATIONS[meal_key]['pt'])
    return meal_key


def get_unit_name(unit: str, language: str = 'pt') -> str:
    """Get translated unit name"""
    if unit in UNIT_TRANSLATIONS:
        return UNIT_TRANSLATIONS[unit].get(language, UNIT_TRANSLATIONS[unit]['pt'])
    return unit


def get_restriction_name(restriction_key: str, language: str = 'pt') -> str:
    """Get translated restriction name"""
    if restriction_key in RESTRICTION_TRANSLATIONS:
        return RESTRICTION_TRANSLATIONS[restriction_key].get(language, RESTRICTION_TRANSLATIONS[restriction_key]['pt'])
    return restriction_key


def get_supplement_name(supplement_key: str, language: str = 'pt') -> str:
    """Get translated supplement name"""
    if supplement_key in SUPPLEMENT_TRANSLATIONS:
        return SUPPLEMENT_TRANSLATIONS[supplement_key].get(language, SUPPLEMENT_TRANSLATIONS[supplement_key]['pt'])
    return supplement_key


def translate_food_item(food: dict, language: str = 'pt') -> dict:
    """Translate a food item dict"""
    translated = food.copy()
    
    if 'key' in food:
        translated['name'] = get_food_name(food['key'], language)
    
    if 'unit' in food:
        translated['unit'] = get_unit_name(food['unit'], language)
    
    return translated


def translate_meal(meal: dict, language: str = 'pt') -> dict:
    """Translate a meal dict including all foods"""
    translated = meal.copy()
    
    # Translate meal name based on content
    meal_name_lower = meal.get('name', '').lower()
    if 'café' in meal_name_lower or 'cafe' in meal_name_lower or 'manhã' in meal_name_lower:
        if 'lanche' in meal_name_lower:
            translated['name'] = get_meal_name('lanche_manha', language)
        else:
            translated['name'] = get_meal_name('cafe_manha', language)
    elif 'almoço' in meal_name_lower or 'almoco' in meal_name_lower:
        translated['name'] = get_meal_name('almoco', language)
    elif 'lanche' in meal_name_lower and 'tarde' in meal_name_lower:
        translated['name'] = get_meal_name('lanche_tarde', language)
    elif 'jantar' in meal_name_lower:
        translated['name'] = get_meal_name('jantar', language)
    elif 'ceia' in meal_name_lower:
        translated['name'] = get_meal_name('ceia', language)
    
    # Translate foods
    if 'foods' in meal:
        translated['foods'] = [translate_food_item(f, language) for f in meal['foods']]
    
    return translated


def translate_diet(diet: dict, language: str = 'pt') -> dict:
    """Translate entire diet response"""
    translated = diet.copy()
    
    if 'meals' in diet:
        translated['meals'] = [translate_meal(m, language) for m in diet['meals']]
    
    if 'supplements' in diet:
        translated['supplements'] = [get_supplement_name(s, language) for s in diet['supplements']]
    
    return translated
