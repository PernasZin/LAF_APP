"""
Diet Module - Constants and Food Database
==========================================
All food data, restrictions, and configuration constants
"""

# ==================== TOLERÂNCIAS ====================
TOL_PERCENT = 0.05  # ±5%

# ==================== LIMITES DE SEGURANÇA ====================
MIN_FOOD_GRAMS = 10       # Mínimo 10g por alimento
MAX_FOOD_GRAMS = 800      # Máximo 800g por alimento
MAX_CARB_GRAMS = 1200     # Máximo específico para carboidratos
MIN_MEAL_CALORIES = 50    # Mínimo 50kcal por refeição
MIN_DAILY_CALORIES = 800  # Mínimo 800kcal por dia

# ==================== LIMITES GLOBAIS ESPECIAIS ====================
MAX_COTTAGE_TOTAL = 20    # MÁXIMO 20g de cottage na dieta TODA
MAX_AVEIA_TOTAL = 80      # MÁXIMO 80g de aveia na dieta TODA
MAX_IOGURTE_OCORRENCIAS = 1  # Iogurte zero aparece no MÁXIMO 1x por dia

# ==================== MÍNIMOS NECESSÁRIOS ====================
MIN_PROTEINS = 3
MIN_CARBS = 3
MIN_FATS = 2
MIN_FRUITS = 2

# ==================== AUTO-COMPLETE PADRÕES ====================
DEFAULT_PROTEINS = ["frango", "patinho", "ovos", "atum", "cottage", "tilapia"]
DEFAULT_CARBS = ["arroz_branco", "arroz_integral", "batata_doce", "aveia", "macarrao", "feijao", "pao_integral", "lentilha"]
DEFAULT_FATS = ["azeite", "pasta_amendoim", "castanhas", "amendoas", "queijo"]
DEFAULT_FRUITS = ["banana", "maca", "laranja", "morango", "mamao", "melancia"]

# ==================== ALIMENTOS PERMITIDOS EM LANCHES ====================
ALIMENTOS_PERMITIDOS_LANCHE = {
    "maca", "banana", "laranja", "morango", "pera", "kiwi", "mamao", "melancia", "abacaxi", "manga", "uva",  # Frutas
    "castanhas", "amendoas", "nozes", "pasta_amendoim",  # Oleaginosas
    "iogurte_zero", "iogurte_natural",  # Iogurtes
    "pao_integral", "pao", "pao_forma", "aveia", "tapioca",  # Carboidratos leves
    "mel", "granola",  # Doces
    "whey_protein",  # Suplemento
}

# ==================== RESTRIÇÕES ALIMENTARES ====================
RESTRICTION_EXCLUSIONS = {
    # Versões com maiúsculas
    "Vegetariano": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", 
                   "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
    "Sem Lactose": {"cottage", "queijo", "cream_cheese", "manteiga", "iogurte_zero", "iogurte_natural", "whey_protein"},
    "Sem Glúten": {"aveia", "macarrao", "macarrao_integral", "pao", "pao_integral", "pao_forma", "seitan"},
    "Low Carb": {"arroz_branco", "arroz_integral", "batata_doce", "batata", 
                 "macarrao", "pao", "pao_integral", "banana", "manga", "uva"},
    "Diabético": {"mel", "leite_condensado", "granola", "banana", "manga", "uva", 
                  "melancia", "abacaxi", "mamao", "tapioca", "pao", "pao_integral", 
                  "pao_forma", "farofa", "arroz_branco"},
    # Versões lowercase (como vem do frontend)
    "vegetariano": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", 
                   "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
    "sem_lactose": {"cottage", "queijo", "cream_cheese", "manteiga", "iogurte_zero", "iogurte_natural", "whey_protein"},
    "sem_gluten": {"aveia", "macarrao", "macarrao_integral", "pao", "pao_integral", "pao_forma", "seitan"},
    "low_carb": {"arroz_branco", "arroz_integral", "batata_doce", "batata", 
                 "macarrao", "pao", "pao_integral", "banana", "manga", "uva"},
}

# ==================== SUBCATEGORIAS DE ALIMENTOS ====================

# 🍗 PROTEÍNAS
PROTEINS_PRINCIPAIS = {"frango", "patinho", "carne_moida", "tilapia", "atum", "salmao", "peru"}
PROTEINS_LEVES = {"ovos", "cottage", "whey_protein", "iogurte_zero"}

# 🍚 CARBOIDRATOS
CARBS_PRINCIPAIS = {"arroz_branco", "arroz_integral", "batata_doce", "macarrao"}
CARBS_COMPLEMENTARES = {"feijao", "lentilha"}
CARBS_LANCHE = {"pao_integral", "pao", "tapioca", "aveia"}
CARBS_ALMOCO_JANTAR = {"arroz_branco", "arroz_integral", "macarrao", "macarrao_integral"}

# 🥑 GORDURAS
GORDURAS_PRINCIPAIS = {"azeite", "abacate"}
GORDURAS_SNACKS = {"castanhas", "amendoas", "nozes", "pasta_amendoim"}

# 🍎 FRUTAS
FRUTAS_FREQUENTES = {"banana", "maca", "laranja", "mamao"}
FRUTAS_OPCIONAIS = {"morango", "melancia", "uva", "pera", "manga", "abacaxi", "kiwi"}

# 🥦 VEGETAIS E LEGUMES
LEGUMES_PRINCIPAIS = {"brocolis", "espinafre", "couve", "cenoura", "abobrinha"}
VERDURAS_SALADA = {"alface", "pepino", "tomate", "salada"}

# Proteína principal para almoço/jantar - NUNCA ovo
PROTEINS_ALMOCO_JANTAR = {"frango", "coxa_frango", "patinho", "carne_moida", "tilapia", "atum", "salmao", "camarao", "peru", "suino"}

# Carnes que SÓ podem aparecer no almoço e jantar
CARNES_APENAS_ALMOCO_JANTAR = {"frango", "coxa_frango", "patinho", "carne_moida", "tilapia", "atum", "salmao", "camarao", "peru", "suino", "sardinha"}

# Alimentos EXCLUSIVOS para café da manhã e lanche da manhã
FOODS_CAFE_LANCHE_MANHA = {"ovos", "claras", "pao", "pao_integral", "pao_forma", "cottage", "tapioca"}

# Alimentos EXCLUSIVOS para lanche da tarde
FOODS_LANCHE_TARDE = {"mel", "leite_condensado", "granola"}

# Tipos de refeição
MEAL_TYPE_CAFE = "cafe"
MEAL_TYPE_LANCHE_MANHA = "lanche_manha"
MEAL_TYPE_ALMOCO = "almoco"
MEAL_TYPE_LANCHE_TARDE = "lanche_tarde"
MEAL_TYPE_JANTAR = "jantar"
MEAL_TYPE_CEIA = "ceia"

# ==================== BANCO DE ALIMENTOS ====================
# Valores por 100g: p=proteína, c=carboidrato, f=gordura

FOODS = {
    # === PROTEÍNAS ===
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "category": "protein", "unit": "filé médio", "unit_g": 150},
    "coxa_frango": {"name": "Coxa de Frango", "p": 26.0, "c": 0.0, "f": 8.0, "category": "protein", "unit": "coxa média", "unit_g": 100},
    "patinho": {"name": "Patinho (Carne Magra)", "p": 28.0, "c": 0.0, "f": 6.0, "category": "protein", "unit": "bife médio", "unit_g": 120},
    "carne_moida": {"name": "Carne Moída", "p": 26.0, "c": 0.0, "f": 10.0, "category": "protein", "unit": "colher sopa cheia", "unit_g": 30},
    "suino": {"name": "Carne Suína", "p": 27.0, "c": 0.0, "f": 14.0, "category": "protein", "unit": "bife médio", "unit_g": 120},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "category": "protein", "unit": "unidade grande", "unit_g": 50},
    "claras": {"name": "Claras de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "category": "protein", "unit": "clara", "unit_g": 33},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "category": "protein", "unit": "filé médio", "unit_g": 120},
    "atum": {"name": "Atum", "p": 29.0, "c": 0.0, "f": 1.0, "category": "protein", "unit": "lata drenada", "unit_g": 120},
    "salmao": {"name": "Salmão", "p": 25.0, "c": 0.0, "f": 13.0, "category": "protein", "unit": "filé médio", "unit_g": 150},
    "camarao": {"name": "Camarão", "p": 24.0, "c": 0.0, "f": 1.0, "category": "protein", "unit": "porção média", "unit_g": 100},
    "sardinha": {"name": "Sardinha", "p": 25.0, "c": 0.0, "f": 11.0, "category": "protein", "unit": "lata drenada", "unit_g": 90},
    "peru": {"name": "Peru", "p": 29.0, "c": 0.0, "f": 1.0, "category": "protein", "unit": "fatias finas", "unit_g": 50},
    "cottage": {"name": "Queijo Cottage", "p": 11.0, "c": 3.4, "f": 4.3, "category": "protein", "subcategory": "light", "unit": "colher sopa", "unit_g": 30},
    "iogurte_zero": {"name": "Iogurte Zero", "p": 10.0, "c": 4.0, "f": 0.5, "category": "protein", "subcategory": "light", "unit": "garrafa", "unit_g": 1150, "max_g": 500},
    "whey_protein": {"name": "Whey Protein", "p": 80.0, "c": 8.0, "f": 3.0, "category": "protein", "subcategory": "supplement", "unit": "scoop", "unit_g": 30},
    "requeijao_light": {"name": "Requeijão Light", "p": 8.0, "c": 3.0, "f": 10.0, "category": "protein", "subcategory": "light", "unit": "colher sopa", "unit_g": 30},
    "tofu": {"name": "Tofu", "p": 8.0, "c": 2.0, "f": 4.0, "category": "protein", "unit": "fatia média", "unit_g": 80},
    
    # === PROTEÍNAS VEGETAIS ===
    "tempeh": {"name": "Tempeh", "p": 19.0, "c": 9.0, "f": 11.0, "category": "protein", "subcategory": "vegetal", "unit": "fatia média", "unit_g": 100},
    "seitan": {"name": "Seitan", "p": 25.0, "c": 4.0, "f": 2.0, "category": "protein", "subcategory": "vegetal", "unit": "porção", "unit_g": 100},
    "edamame": {"name": "Edamame", "p": 11.0, "c": 10.0, "f": 5.0, "category": "protein", "subcategory": "vegetal", "unit": "xícara", "unit_g": 100},
    "grao_de_bico": {"name": "Grão de Bico", "p": 9.0, "c": 27.0, "f": 3.0, "category": "protein", "subcategory": "vegetal", "unit": "concha média", "unit_g": 100},
    "proteina_ervilha": {"name": "Proteína de Ervilha", "p": 80.0, "c": 4.0, "f": 2.0, "category": "protein", "subcategory": "supplement_vegetal", "unit": "scoop", "unit_g": 30},
    
    # === CARBOIDRATOS ===
    "arroz_branco": {"name": "Arroz Branco", "p": 2.6, "c": 28.0, "f": 0.3, "category": "carb", "unit": "xícara cozida", "unit_g": 120},
    "arroz_integral": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "category": "carb", "unit": "xícara cozida", "unit_g": 120},
    "batata_doce": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "category": "carb", "unit": "unidade média", "unit_g": 150},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "category": "carb", "unit": "colher sopa", "unit_g": 15},
    "macarrao": {"name": "Macarrão", "p": 5.0, "c": 25.0, "f": 1.0, "category": "carb", "unit": "xícara cozido", "unit_g": 140},
    "macarrao_integral": {"name": "Macarrão Integral", "p": 6.0, "c": 26.0, "f": 1.5, "category": "carb", "unit": "xícara cozido", "unit_g": 140},
    "pao": {"name": "Pão Francês", "p": 9.0, "c": 49.0, "f": 3.0, "category": "carb", "unit": "unidade", "unit_g": 50},
    "pao_integral": {"name": "Pão Integral", "p": 10.0, "c": 42.0, "f": 4.0, "category": "carb", "unit": "fatia", "unit_g": 30},
    "pao_forma": {"name": "Pão de Forma", "p": 8.0, "c": 46.0, "f": 3.5, "category": "carb", "unit": "fatia", "unit_g": 25},
    "tapioca": {"name": "Tapioca", "p": 0.5, "c": 22.0, "f": 0.0, "category": "carb", "unit": "goma hidratada", "unit_g": 50},
    "feijao": {"name": "Feijão", "p": 6.0, "c": 14.0, "f": 0.5, "category": "carb", "unit": "concha média", "unit_g": 100},
    "lentilha": {"name": "Lentilha", "p": 9.0, "c": 20.0, "f": 0.4, "category": "carb", "unit": "concha média", "unit_g": 100},
    "farofa": {"name": "Farofa", "p": 1.5, "c": 46.0, "f": 2.0, "category": "carb", "unit": "colher sopa", "unit_g": 20},
    "granola": {"name": "Granola", "p": 10.0, "c": 64.0, "f": 15.0, "category": "carb", "unit": "xícara", "unit_g": 40},
    
    # === GORDURAS ===
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat", "unit": "colher sopa", "unit_g": 13},
    "pasta_amendoim": {"name": "Pasta de Amendoim", "p": 25.0, "c": 20.0, "f": 50.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "pasta_amendoa": {"name": "Pasta de Amêndoa", "p": 21.0, "c": 19.0, "f": 56.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "oleo_coco": {"name": "Óleo de Coco", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat", "unit": "colher sopa", "unit_g": 13},
    "castanhas": {"name": "Castanhas", "p": 14.0, "c": 30.0, "f": 44.0, "category": "fat", "unit": "unidades", "unit_g": 10},
    "amendoas": {"name": "Amêndoas", "p": 21.0, "c": 22.0, "f": 49.0, "category": "fat", "unit": "unidades", "unit_g": 5},
    "nozes": {"name": "Nozes", "p": 15.0, "c": 14.0, "f": 65.0, "category": "fat", "unit": "unidade", "unit_g": 8},
    "chia": {"name": "Chia", "p": 17.0, "c": 42.0, "f": 31.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "queijo": {"name": "Queijo", "p": 23.0, "c": 1.3, "f": 33.0, "category": "fat", "unit": "fatia média", "unit_g": 30},
    
    # === FRUTAS ===
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "category": "fruit", "unit": "unidade média", "unit_g": 120},
    "maca": {"name": "Maçã", "p": 0.3, "c": 14.0, "f": 0.2, "category": "fruit", "unit": "unidade média", "unit_g": 150},
    "laranja": {"name": "Laranja", "p": 0.9, "c": 12.0, "f": 0.1, "category": "fruit", "unit": "unidade média", "unit_g": 180},
    "morango": {"name": "Morango", "p": 0.7, "c": 8.0, "f": 0.3, "category": "fruit", "unit": "xícara", "unit_g": 150},
    "mamao": {"name": "Mamão", "p": 0.5, "c": 11.0, "f": 0.1, "category": "fruit", "unit": "fatia média", "unit_g": 150},
    "manga": {"name": "Manga", "p": 0.8, "c": 15.0, "f": 0.4, "category": "fruit", "unit": "unidade pequena", "unit_g": 200},
    "melancia": {"name": "Melancia", "p": 0.6, "c": 8.0, "f": 0.2, "category": "fruit", "unit": "fatia média", "unit_g": 200},
    "abacate": {"name": "Abacate", "p": 2.0, "c": 9.0, "f": 15.0, "category": "fruit", "unit": "metade", "unit_g": 100},
    "uva": {"name": "Uva", "p": 0.7, "c": 18.0, "f": 0.2, "category": "fruit", "unit": "cacho pequeno", "unit_g": 100},
    "abacaxi": {"name": "Abacaxi", "p": 0.5, "c": 13.0, "f": 0.1, "category": "fruit", "unit": "fatia média", "unit_g": 100},
    "melao": {"name": "Melão", "p": 0.8, "c": 8.0, "f": 0.2, "category": "fruit", "unit": "fatia média", "unit_g": 150},
    "kiwi": {"name": "Kiwi", "p": 1.1, "c": 15.0, "f": 0.5, "category": "fruit", "unit": "unidade", "unit_g": 75},
    "pera": {"name": "Pera", "p": 0.4, "c": 15.0, "f": 0.1, "category": "fruit", "unit": "unidade média", "unit_g": 180},
    "pessego": {"name": "Pêssego", "p": 0.9, "c": 10.0, "f": 0.3, "category": "fruit", "unit": "unidade média", "unit_g": 150},
    "mirtilo": {"name": "Mirtilo", "p": 0.7, "c": 14.0, "f": 0.3, "category": "fruit", "unit": "xícara", "unit_g": 150},
    "acai": {"name": "Açaí", "p": 1.0, "c": 6.0, "f": 5.0, "category": "fruit", "unit": "polpa 100g", "unit_g": 100},
    
    # === VEGETAIS E LEGUMES ===
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "category": "vegetable", "unit": "prato cheio", "unit_g": 100},
    "alface": {"name": "Alface", "p": 1.2, "c": 2.0, "f": 0.2, "category": "vegetable", "unit": "folhas", "unit_g": 50},
    "rucola": {"name": "Rúcula", "p": 2.6, "c": 3.7, "f": 0.7, "category": "vegetable", "unit": "maço", "unit_g": 50},
    "espinafre": {"name": "Espinafre", "p": 2.9, "c": 3.6, "f": 0.4, "category": "vegetable", "unit": "xícara", "unit_g": 100},
    "couve": {"name": "Couve", "p": 2.9, "c": 4.4, "f": 0.6, "category": "vegetable", "unit": "folhas refogadas", "unit_g": 100},
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "category": "vegetable", "unit": "xícara cozido", "unit_g": 100},
    "couve_flor": {"name": "Couve-flor", "p": 1.9, "c": 5.0, "f": 0.3, "category": "vegetable", "unit": "xícara cozida", "unit_g": 100},
    "cenoura": {"name": "Cenoura", "p": 0.9, "c": 10.0, "f": 0.2, "category": "vegetable", "unit": "unidade média", "unit_g": 80},
    "abobrinha": {"name": "Abobrinha", "p": 1.2, "c": 3.0, "f": 0.3, "category": "vegetable", "unit": "unidade média", "unit_g": 150},
    "pepino": {"name": "Pepino", "p": 0.7, "c": 4.0, "f": 0.1, "category": "vegetable", "unit": "unidade", "unit_g": 150},
    "tomate": {"name": "Tomate", "p": 0.9, "c": 3.9, "f": 0.2, "category": "vegetable", "unit": "unidade média", "unit_g": 120},
    "beterraba": {"name": "Beterraba", "p": 1.6, "c": 10.0, "f": 0.2, "category": "vegetable", "unit": "unidade média", "unit_g": 100},
    "vagem": {"name": "Vagem", "p": 1.8, "c": 7.0, "f": 0.2, "category": "vegetable", "unit": "xícara cozida", "unit_g": 100},
    "pimentao": {"name": "Pimentão", "p": 1.0, "c": 6.0, "f": 0.3, "category": "vegetable", "unit": "unidade média", "unit_g": 120},
    
    # === EXTRAS/DOCES ===
    "leite_condensado": {"name": "Leite Condensado", "p": 8.0, "c": 55.0, "f": 8.0, "category": "extra", "unit": "colher sopa", "unit_g": 20},
    "mel": {"name": "Mel", "p": 0.3, "c": 82.0, "f": 0.0, "category": "extra", "unit": "colher sopa", "unit_g": 21},
}

# === SUPLEMENTOS ===
SUPPLEMENTS = {
    "creatina": {"name": "Creatina (5g/dia)"},
    "multivitaminico": {"name": "Multivitamínico"},
    "omega3": {"name": "Ômega 3"},
    "cafeina": {"name": "Cafeína"},
    "vitamina_d": {"name": "Vitamina D"},
    "vitamina_c": {"name": "Vitamina C"},
    "zinco": {"name": "Zinco"},
    "magnesio": {"name": "Magnésio"},
    "colageno": {"name": "Colágeno"},
}
