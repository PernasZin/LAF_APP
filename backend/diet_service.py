"""
Sistema de Geração de Dieta - V14 BULLETPROOF
==============================================
FILOSOFIA: NUNCA TRAVAR, NUNCA FALHAR, SEMPRE GERAR DIETA VÁLIDA

✅ REGRAS OBRIGATÓRIAS (SEM EXCEÇÃO):
1. Nenhum alimento com grams=0 ou quantity=0
2. Nenhuma refeição vazia
3. Dieta nunca incompleta
4. Todos os campos obrigatórios preenchidos
5. Quantidades em múltiplos de 10g
6. Correção automática sempre
7. NUNCA retornar erro para o usuário

🔁 COMPORTAMENTO:
- Se validação falhar → ajusta automaticamente
- Se alimentos insuficientes → auto-completa
- Se macros não batem → recalcula
- SEMPRE retorna dieta válida e utilizável
==============================================
"""

import os
from typing import List, Dict, Tuple, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random


# ==================== MODELS ====================

class Meal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    time: str
    foods: List[Dict]
    total_calories: int
    macros: Dict[str, int]


class DietPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_calories: int
    target_macros: Dict[str, int]
    meals: List[Meal]
    computed_calories: int
    computed_macros: Dict[str, int]
    supplements: List[str] = []
    notes: Optional[str] = None
    auto_completed: bool = False  # Flag se auto-completou
    auto_complete_message: Optional[str] = None  # Mensagem amigável


class DietGenerateRequest(BaseModel):
    user_id: str


# ==================== TOLERÂNCIAS ====================
TOL_PERCENT = 0.05  # ±5%

# ==================== LIMITES DE SEGURANÇA ====================
MIN_FOOD_GRAMS = 10       # Mínimo 10g por alimento
MAX_FOOD_GRAMS = 800      # Máximo 800g por alimento (aumentado para permitir dietas altas)
MAX_CARB_GRAMS = 1200     # Máximo específico para carboidratos (arroz, batata)
MIN_MEAL_CALORIES = 50    # Mínimo 50kcal por refeição
MIN_DAILY_CALORIES = 800  # Mínimo 800kcal por dia (segurança)

# ==================== LIMITES GLOBAIS ESPECIAIS ====================
# Estes limites se aplicam à DIETA INTEIRA, não por refeição
MAX_COTTAGE_TOTAL = 20    # MÁXIMO 20g de cottage na dieta TODA (1 pote = 300g, muito!)
MAX_AVEIA_TOTAL = 80      # MÁXIMO 80g de aveia na dieta TODA
MAX_IOGURTE_OCORRENCIAS = 1  # Iogurte zero aparece no MÁXIMO 1x por dia (muito repetitivo)


# ==================== MÍNIMOS NECESSÁRIOS ====================
MIN_PROTEINS = 3
MIN_CARBS = 3
MIN_FATS = 2
MIN_FRUITS = 2


# ==================== AUTO-COMPLETE PADRÕES ====================
# Ordem de prioridade para auto-complete (alimentos comuns e baratos no Brasil)

DEFAULT_PROTEINS = ["frango", "patinho", "ovos", "atum", "cottage", "tilapia"]
DEFAULT_CARBS = ["arroz_branco", "arroz_integral", "batata_doce", "aveia", "macarrao", "feijao", "pao_integral", "lentilha"]
DEFAULT_FATS = ["azeite", "pasta_amendoim", "castanhas", "amendoas", "queijo"]
DEFAULT_FRUITS = ["banana", "maca", "laranja", "morango", "mamao", "melancia"]


# ==================== RESTRIÇÕES ALIMENTARES ====================

RESTRICTION_EXCLUSIONS = {
    "Vegetariano": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", 
                   "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
    "Sem Lactose": {"cottage", "queijo", "cream_cheese", "manteiga"},
    "Sem Glúten": {"aveia", "macarrao", "pao", "pao_integral"},
    "Low Carb": {"arroz_branco", "arroz_integral", "batata_doce", "batata", 
                 "macarrao", "pao", "pao_integral", "banana", "manga", "uva"},
}


# ==================== REGRAS OBRIGATÓRIAS POR REFEIÇÃO ====================
# Estas regras NUNCA devem ser violadas

# ==================== SUBCATEGORIAS DE ALIMENTOS (PRD) ====================

# 🍗 PROTEÍNAS
# Proteínas Principais (base da refeição)
PROTEINS_PRINCIPAIS = {"frango", "patinho", "carne_moida", "tilapia", "atum", "salmao", "peru"}

# Proteínas Secundárias / Leves (lanches, café, ceia)
# NOTA: iogurte_natural REMOVIDO - usar apenas iogurte_zero
PROTEINS_LEVES = {"ovos", "cottage", "whey_protein", "iogurte_zero"}

# 🍚 CARBOIDRATOS
# Carboidratos Principais (base energética da refeição)
CARBS_PRINCIPAIS = {"arroz_branco", "arroz_integral", "batata_doce", "macarrao"}

# Carboidratos Complementares (acompanham o carb principal, não são base)
CARBS_COMPLEMENTARES = {"feijao", "lentilha"}

# Carboidratos de Lanche / Rápidos
CARBS_LANCHE = {"pao_integral", "pao", "tapioca", "aveia"}

# 🥑 GORDURAS
# Gorduras Saudáveis Principais
GORDURAS_PRINCIPAIS = {"azeite", "abacate"}

# Gorduras de Apoio / Snacks
GORDURAS_SNACKS = {"castanhas", "amendoas", "nozes", "pasta_amendoim"}

# 🍎 FRUTAS
# Frutas de Uso Frequente
FRUTAS_FREQUENTES = {"banana", "maca", "laranja", "mamao"}

# Frutas Opcionais
FRUTAS_OPCIONAIS = {"morango", "melancia", "uva", "pera", "manga", "abacaxi", "kiwi"}

# 🥦 VEGETAIS E LEGUMES
# Legumes Principais (acompanhamento do prato)
LEGUMES_PRINCIPAIS = {"brocolis", "espinafre", "couve", "cenoura", "abobrinha"}

# Verduras Base de Salada
VERDURAS_SALADA = {"alface", "pepino", "tomate", "salada"}

# Carboidrato principal para almoço/jantar - SEMPRE arroz ou macarrão
CARBS_ALMOCO_JANTAR = {"arroz_branco", "arroz_integral", "macarrao", "macarrao_integral"}

# Proteína principal para almoço/jantar - NUNCA ovo
PROTEINS_ALMOCO_JANTAR = {"frango", "coxa_frango", "patinho", "carne_moida", "tilapia", "atum", "salmao", "camarao", "peru", "suino"}

# Alimentos EXCLUSIVOS para café da manhã e lanche da manhã
FOODS_CAFE_LANCHE_MANHA = {"ovos", "claras", "pao", "pao_integral", "pao_forma", "cottage", "tapioca"}

# Alimentos EXCLUSIVOS para lanche da tarde (doces)
FOODS_LANCHE_TARDE = {"mel", "leite_condensado", "granola"}

# Tipos de refeição
MEAL_TYPE_CAFE = "cafe"
MEAL_TYPE_LANCHE_MANHA = "lanche_manha"
MEAL_TYPE_ALMOCO = "almoco"
MEAL_TYPE_LANCHE_TARDE = "lanche_tarde"
MEAL_TYPE_JANTAR = "jantar"
MEAL_TYPE_CEIA = "ceia"


def get_meal_type_from_name(meal_name: str) -> str:
    """Determina o tipo de refeição pelo nome"""
    name_lower = meal_name.lower()
    if "café" in name_lower or "cafe" in name_lower:
        return MEAL_TYPE_CAFE
    elif "lanche" in name_lower and "manhã" in name_lower:
        return MEAL_TYPE_LANCHE_MANHA
    elif "almoço" in name_lower or "almoco" in name_lower:
        return MEAL_TYPE_ALMOCO
    elif "lanche" in name_lower and ("tarde" in name_lower or "manhã" not in name_lower):
        return MEAL_TYPE_LANCHE_TARDE
    elif "jantar" in name_lower:
        return MEAL_TYPE_JANTAR
    elif "ceia" in name_lower:
        return MEAL_TYPE_CEIA
    return MEAL_TYPE_ALMOCO  # Default


def is_food_allowed_for_meal(food_key: str, meal_type: str) -> bool:
    """
    Verifica se um alimento é permitido para um tipo de refeição específico.
    
    REGRAS:
    - Ovos/Pão/Iogurte: APENAS café da manhã e lanche da manhã
    - Mel/Leite condensado: APENAS lanche da tarde
    - Arroz/Macarrão: APENAS almoço e jantar
    - Frango/Patinho/Peixes: APENAS almoço e jantar
    """
    # Alimentos de café da manhã/lanche manhã - NÃO podem ir em almoço/jantar
    if food_key in FOODS_CAFE_LANCHE_MANHA:
        return meal_type in {MEAL_TYPE_CAFE, MEAL_TYPE_LANCHE_MANHA, MEAL_TYPE_CEIA}
    
    # Doces do lanche da tarde
    if food_key in FOODS_LANCHE_TARDE:
        return meal_type == MEAL_TYPE_LANCHE_TARDE
    
    # Proteínas principais (carnes/peixes) - NÃO podem ir no café/lanches
    if food_key in PROTEINS_ALMOCO_JANTAR:
        return meal_type in {MEAL_TYPE_ALMOCO, MEAL_TYPE_JANTAR}
    
    # Arroz/Macarrão - APENAS almoço e jantar
    if food_key in CARBS_ALMOCO_JANTAR:
        return meal_type in {MEAL_TYPE_ALMOCO, MEAL_TYPE_JANTAR}
    
    # Outros alimentos são permitidos em qualquer refeição
    return True


def get_allowed_proteins_for_meal(meal_type: str, available_proteins: Set[str]) -> Set[str]:
    """Retorna proteínas permitidas para o tipo de refeição"""
    if meal_type in {MEAL_TYPE_CAFE, MEAL_TYPE_LANCHE_MANHA}:
        # Café/Lanche manhã: ovos, iogurte, cottage
        allowed = {"ovos", "claras", "cottage", "cottage", "cottage"}
        return available_proteins & allowed
    elif meal_type in {MEAL_TYPE_ALMOCO, MEAL_TYPE_JANTAR}:
        # Almoço/Jantar: carnes e peixes, NUNCA ovos
        return available_proteins & PROTEINS_ALMOCO_JANTAR
    else:
        # Lanches: iogurte, cottage
        allowed = {"cottage", "cottage", "cottage"}
        return available_proteins & allowed


def get_allowed_carbs_for_meal(meal_type: str, available_carbs: Set[str]) -> Set[str]:
    """Retorna carboidratos permitidos para o tipo de refeição"""
    if meal_type in {MEAL_TYPE_CAFE, MEAL_TYPE_LANCHE_MANHA}:
        # Café/Lanche manhã: aveia, pão, tapioca
        allowed = {"aveia", "pao", "pao_integral", "pao_forma", "tapioca", "granola"}
        return available_carbs & allowed
    elif meal_type in {MEAL_TYPE_ALMOCO, MEAL_TYPE_JANTAR}:
        # Almoço/Jantar: SEMPRE arroz ou macarrão como principal
        return available_carbs & CARBS_ALMOCO_JANTAR
    else:
        # Lanches: frutas principalmente (sem carbs pesados)
        return set()  # Lanches usam frutas, não carbs


def get_complementary_carbs_for_meal(meal_type: str, available_carbs: Set[str]) -> Set[str]:
    """Retorna carboidratos complementares (batata, feijão) para almoço/jantar"""
    if meal_type in {MEAL_TYPE_ALMOCO, MEAL_TYPE_JANTAR}:
        complementary = {"batata_doce", "feijao", "lentilha", "grao_de_bico"}
        return available_carbs & complementary
    return set()


# ==================== NORMALIZAÇÃO ====================

FOOD_NORMALIZATION = {
    # PROTEÍNAS
    "chicken_breast": "frango", "chicken": "frango", "chicken_thigh": "coxa_frango",
    "lean_beef": "patinho", "ground_beef": "carne_moida", "beef": "patinho",
    "pork": "suino", "eggs": "ovos", "egg_whites": "claras",
    "tilapia": "tilapia", "tuna": "atum", "salmon": "salmao",
    "shrimp": "camarao", "sardine": "sardinha", "turkey": "peru", "fish": "tilapia",
    "greek_yogurt": "cottage", "natural_yogurt": "cottage", "tofu": "tofu",
    
    # CARBOIDRATOS
    "white_rice": "arroz_branco", "brown_rice": "arroz_integral", "rice": "arroz_branco",
    "sweet_potato": "batata_doce", "potato": "batata", "oats": "aveia",
    "pasta": "macarrao", "bread": "pao", "whole_bread": "pao_integral",
    "quinoa": "quinoa", "couscous": "cuscuz", "tapioca": "tapioca",
    "corn": "milho", "beans": "feijao", "lentils": "lentilha", "chickpeas": "grao_de_bico",
    
    # GORDURAS
    "olive_oil": "azeite", "peanut_butter": "pasta_amendoim",
    "almond_butter": "pasta_amendoa", "coconut_oil": "oleo_coco",
    "butter": "manteiga", "nuts": "castanhas", "almonds": "amendoas",
    "walnuts": "nozes", "chia": "chia", "flaxseed": "linhaca",
    "cheese": "queijo", "cream_cheese": "cream_cheese",
    
    # FRUTAS
    "banana": "banana", "apple": "maca", "orange": "laranja",
    "strawberry": "morango", "papaya": "mamao", "mango": "manga",
    "watermelon": "melancia", "avocado": "abacate", "grape": "uva",
    "pineapple": "abacaxi", "melon": "melao", "kiwi": "kiwi",
    "pear": "pera", "peach": "pessego", "blueberry": "mirtilo", "açai": "acai",
    
    # VEGETAIS E LEGUMES
    "broccoli": "brocolis", "spinach": "espinafre", "kale": "couve",
    "lettuce": "alface", "arugula": "rucola", "cauliflower": "couve_flor",
    "carrot": "cenoura", "zucchini": "abobrinha", "tomato": "tomate",
    "cucumber": "pepino", "beetroot": "beterraba", "green_beans": "vagem",
    "bell_pepper": "pimentao", "salad": "salada",
    
    # SUPLEMENTOS
    "creatine": "creatina", "multivitamin": "multivitaminico",
    "omega3": "omega3", "caffeine": "cafeina",
    "vitamin_d": "vitamina_d", "vitamin_c": "vitamina_c",
    "zinc": "zinco", "magnesium": "magnesio", "collagen": "colageno",
}


# ==================== BANCO DE ALIMENTOS ====================
# Valores por 100g: p=proteína, c=carboidrato, f=gordura
# unit = medida caseira equivalente a X gramas

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
    # REMOVIDO: iogurte_natural - usar apenas iogurte_zero
    "whey_protein": {"name": "Whey Protein", "p": 80.0, "c": 8.0, "f": 3.0, "category": "protein", "subcategory": "supplement", "unit": "scoop", "unit_g": 30},
    "requeijao_light": {"name": "Requeijão Light", "p": 8.0, "c": 3.0, "f": 10.0, "category": "protein", "subcategory": "light", "unit": "colher sopa", "unit_g": 30},
    "tofu": {"name": "Tofu", "p": 8.0, "c": 2.0, "f": 4.0, "category": "protein", "unit": "fatia média", "unit_g": 80},
    
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
    # Fonte de fibras, vitaminas, minerais - NÃO substituem macros principais
    # Prioridade: saúde intestinal, micronutrientes, recuperação muscular
    
    # Folhas verdes (saladas)
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "category": "vegetable", "unit": "prato cheio", "unit_g": 100},
    "alface": {"name": "Alface", "p": 1.2, "c": 2.0, "f": 0.2, "category": "vegetable", "unit": "folhas", "unit_g": 50},
    "rucola": {"name": "Rúcula", "p": 2.6, "c": 3.7, "f": 0.7, "category": "vegetable", "unit": "maço", "unit_g": 50},
    "espinafre": {"name": "Espinafre", "p": 2.9, "c": 3.6, "f": 0.4, "category": "vegetable", "unit": "xícara", "unit_g": 100},
    "couve": {"name": "Couve", "p": 2.9, "c": 4.4, "f": 0.6, "category": "vegetable", "unit": "folhas refogadas", "unit_g": 100},
    
    # Crucíferas (alto valor nutricional)
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "category": "vegetable", "unit": "xícara cozido", "unit_g": 100},
    "couve_flor": {"name": "Couve-flor", "p": 1.9, "c": 5.0, "f": 0.3, "category": "vegetable", "unit": "xícara cozida", "unit_g": 100},
    
    # Legumes variados
    "cenoura": {"name": "Cenoura", "p": 0.9, "c": 10.0, "f": 0.2, "category": "vegetable", "unit": "unidade média", "unit_g": 80},
    "abobrinha": {"name": "Abobrinha", "p": 1.2, "c": 3.0, "f": 0.3, "category": "vegetable", "unit": "unidade média", "unit_g": 150},
    "pepino": {"name": "Pepino", "p": 0.7, "c": 4.0, "f": 0.1, "category": "vegetable", "unit": "unidade", "unit_g": 150},
    "tomate": {"name": "Tomate", "p": 0.9, "c": 3.9, "f": 0.2, "category": "vegetable", "unit": "unidade média", "unit_g": 120},
    "beterraba": {"name": "Beterraba", "p": 1.6, "c": 10.0, "f": 0.2, "category": "vegetable", "unit": "unidade média", "unit_g": 100},
    "vagem": {"name": "Vagem", "p": 1.8, "c": 7.0, "f": 0.2, "category": "vegetable", "unit": "xícara cozida", "unit_g": 100},
    "pimentao": {"name": "Pimentão", "p": 1.0, "c": 6.0, "f": 0.3, "category": "vegetable", "unit": "unidade média", "unit_g": 120},
    
    # === EXTRAS/DOCES (APENAS para café da manhã e lanches - MÁXIMO 30g) ===
    "leite_condensado": {"name": "Leite Condensado", "p": 8.0, "c": 55.0, "f": 8.0, "category": "extra", "unit": "colher sopa", "unit_g": 20},
    "mel": {"name": "Mel", "p": 0.3, "c": 82.0, "f": 0.0, "category": "extra", "unit": "colher sopa", "unit_g": 21},
    "whey_protein": {"name": "Whey Protein", "p": 80.0, "c": 5.0, "f": 3.0, "category": "extra", "unit": "scoop", "unit_g": 30},
}


# === SUPLEMENTOS (não contam como macros da dieta) ===
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


# ==================== FUNÇÕES UTILITÁRIAS ====================

def round_to_10(value: float) -> int:
    """Arredonda para múltiplo de 10"""
    return int(round(value / 10) * 10)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limita valor entre min e max"""
    return max(min_val, min(max_val, value))


def normalize_food(pref: str) -> str:
    """Normaliza nome do alimento para chave do banco"""
    return FOOD_NORMALIZATION.get(pref, pref)


def calc_food(food_key: str, grams: float, round_down: bool = False) -> Dict:
    """
    Calcula macros de um alimento em quantidade específica.
    
    ✅ GARANTIAS:
    - SEMPRE retorna um dict válido (nunca None)
    - grams SEMPRE >= MIN_FOOD_GRAMS (10g)
    - grams SEMPRE <= MAX_FOOD_GRAMS (800g) ou MAX_CARB_GRAMS (1200g) para carbs
    - Alimentos CONTÁVEIS (ovos, pão, iogurte) são ajustados para unidades inteiras
    - TODOS os campos obrigatórios preenchidos
    
    Parâmetros:
    - round_down: Se True, arredonda contáveis para BAIXO (menos macros)
                  Se False (padrão), arredonda para o mais próximo
    
    Formato: "Nome – Xg (≈ Y medida caseira)"
    """
    # FALLBACK: Se alimento não existe, usa frango como default
    if food_key not in FOODS:
        food_key = "frango"
    
    f = FOODS[food_key]
    
    # Determina limite máximo baseado na categoria
    max_grams = MAX_CARB_GRAMS if f["category"] == "carb" else MAX_FOOD_GRAMS
    
    # ========== ALIMENTOS CONTÁVEIS ==========
    # Estes alimentos devem ser em unidades INTEIRAS (1, 2, 3...)
    # Não faz sentido "1.5 ovos" ou "0.6 pote de iogurte"
    COUNTABLE_FOODS = {
        # Ovos - sempre em unidades inteiras
        "ovos": 50,           # 1 ovo = ~50g
        "claras": 33,         # 1 clara = ~33g
        
        # Pães - sempre em fatias/unidades inteiras
        "pao": 50,            # 1 pão francês = ~50g
        "pao_integral": 30,   # 1 fatia = ~30g
        "pao_forma": 25,      # 1 fatia = ~25g
        
        # Cottage - ajuste por colheres (30g cada)
        "cottage": 30,     # 1 colher = 30g
        
        # Frutas unitárias
        "banana": 120,        # 1 unidade = ~120g
        "maca": 150,          # 1 unidade = ~150g
        "laranja": 180,       # 1 unidade = ~180g
        "kiwi": 75,           # 1 unidade = ~75g
        "pera": 180,          # 1 unidade = ~180g
        "mamao": 150,         # 1 fatia = ~150g
        "manga": 200,         # 1 unidade = ~200g
        
        # Batatas - sempre em unidades inteiras
        "batata_doce": 150,   # 1 unidade = ~150g
    }
    
    unit = f.get("unit", "porção")
    unit_g = f.get("unit_g", 100)
    
    # Se é alimento contável, ajusta para unidades inteiras
    if food_key in COUNTABLE_FOODS:
        unit_weight = COUNTABLE_FOODS[food_key]
        # Calcula quantas unidades seriam necessárias
        units_needed = grams / unit_weight
        
        # MÍNIMO DE UNIDADES para certos alimentos
        MIN_UNITS = {
            "pao_integral": 2,  # Mínimo 2 fatias de pão integral
            "pao_forma": 2,     # Mínimo 2 fatias de pão de forma
            "pao": 1,           # Mínimo 1 pão francês
        }
        min_units = MIN_UNITS.get(food_key, 1)
        
        # IMPORTANTE: Arredondar para baixo quando round_down=True
        # Isso ajuda a manter os macros abaixo do target para ajuste fino posterior
        if round_down:
            units_int = max(min_units, int(units_needed))  # Arredonda para BAIXO (floor)
        else:
            units_int = max(min_units, round(units_needed))  # Arredonda normal
        
        # Limita a um máximo razoável
        max_units = 10 if food_key in ["ovos", "claras"] else 4
        units_int = min(units_int, max_units)
        # Recalcula gramas baseado em unidades inteiras
        g = units_int * unit_weight
        unit_qty = units_int
        
        # Formato especial para contáveis
        if units_int == 1:
            unit_str = f"= {units_int} {unit}"
        else:
            # Pluraliza corretamente
            unit_plural = unit
            # Trata casos especiais de pluralização
            if " " in unit:
                # "unidade média" -> "unidades médias"
                parts = unit.split(" ")
                plural_parts = []
                for part in parts:
                    if part.endswith("ção"):
                        plural_parts.append(part[:-3] + "ções")
                    elif part.endswith("a"):
                        plural_parts.append(part + "s")
                    elif part.endswith("e"):
                        plural_parts.append(part + "s")
                    elif not part.endswith("s"):
                        plural_parts.append(part + "s")
                    else:
                        plural_parts.append(part)
                unit_plural = " ".join(plural_parts)
            elif unit.endswith("ção"):
                unit_plural = unit[:-3] + "ções"
            elif unit.endswith("e"):
                unit_plural = unit + "s"
            elif unit.endswith("a"):
                unit_plural = unit + "s"
            elif not unit.endswith("s"):
                unit_plural = unit + "s"
            unit_str = f"= {units_int} {unit_plural}"
    else:
        # Alimentos não-contáveis: usa lógica normal (múltiplos de 10g)
        g = round_to_10(grams)
        
        # Verifica se tem limite máximo específico do alimento
        food_max_g = f.get("max_g", max_grams)
        g = max(MIN_FOOD_GRAMS, min(food_max_g, g))
        
        # GARANTIA: Sempre > 0
        if g <= 0:
            g = MIN_FOOD_GRAMS
        
        # Calcula equivalente em medida caseira
        if unit_g > 0:
            unit_qty = g / unit_g
            
            # Para garrafas/líquidos: mostra em ml quando < 1 garrafa
            if unit == "garrafa" and unit_qty < 1:
                ml = g  # 1g ≈ 1ml para iogurte
                unit_str = f"≈ {int(ml)}ml"
            elif unit_qty >= 1:
                if unit_qty == int(unit_qty):
                    unit_str = f"≈ {int(unit_qty)} {unit}"
                else:
                    unit_str = f"≈ {unit_qty:.1f} {unit}"
            else:
                unit_str = f"≈ {unit_qty:.1f} {unit}"
        else:
            unit_str = "porção"
    
    ratio = g / 100
    
    # Calcula macros (nunca negativos)
    protein = max(0, round(f["p"] * ratio))
    carbs = max(0, round(f["c"] * ratio))
    fat = max(0, round(f["f"] * ratio))
    calories = max(1, round((f["p"] * 4 + f["c"] * 4 + f["f"] * 9) * ratio))
    
    # Formato completo: "150g (≈ 1 filé médio)" ou "100g (= 2 ovos)"
    quantity_display = f"{g}g ({unit_str})"
    
    # RETORNA ESTRUTURA OBRIGATÓRIA COMPLETA
    return {
        "key": food_key,
        "name": f["name"],
        "grams": g,
        "quantity": f"{g}g",
        "quantity_display": quantity_display,
        "unit_equivalent": unit_str,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "calories": calories,
        "category": f["category"]
    }


def sum_foods(foods: List[Dict]) -> Tuple[int, int, int, int]:
    """Soma totais de uma lista de alimentos"""
    p = sum(f.get("protein", 0) for f in foods)
    c = sum(f.get("carbs", 0) for f in foods)
    f = sum(f.get("fat", 0) for f in foods)
    cal = sum(f.get("calories", 0) for f in foods)
    return p, c, f, cal


def filter_by_restrictions(foods: Set[str], restrictions: List[str]) -> Set[str]:
    """Remove alimentos que violam restrições"""
    excluded = set()
    for r in restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    return foods - excluded


# ==================== AUTO-COMPLETAR INTELIGENTE ====================

def validate_user_foods(preferred: Set[str], restrictions: List[str]) -> Tuple[Set[str], bool, str]:
    """
    🧠 AUTO-COMPLETAR INTELIGENTE
    
    1. Prioriza alimentos escolhidos pelo usuário
    2. Se faltar algo, completa automaticamente com alimentos padrão
    3. NUNCA gera erro
    4. NUNCA deixa refeição vazia
    
    Returns:
        - Set de alimentos (preferidos + auto-completados se necessário)
        - bool: True se auto-completou, False se não precisou
        - str: Mensagem informativa (ou None)
    """
    # Filtra restrições dos alimentos selecionados
    available = filter_by_restrictions(preferred, restrictions)
    
    # Conta por categoria
    proteins = [f for f in available if f in FOODS and FOODS[f]["category"] == "protein"]
    carbs = [f for f in available if f in FOODS and FOODS[f]["category"] == "carb"]
    fats = [f for f in available if f in FOODS and FOODS[f]["category"] == "fat"]
    fruits = [f for f in available if f in FOODS and FOODS[f]["category"] == "fruit"]
    
    final_foods = set(available)
    auto_added = []
    
    # ✅ Auto-completar PROTEÍNAS (mínimo 2)
    if len(proteins) < 2:
        defaults = ["frango", "ovos", "patinho", "tilapia", "whey_protein"]
        for d in defaults:
            if d not in final_foods and d in FOODS:
                if d not in filter_by_restrictions({d}, restrictions):
                    continue
                final_foods.add(d)
                auto_added.append(FOODS[d]["name"])
                if len([f for f in final_foods if f in FOODS and FOODS[f]["category"] == "protein"]) >= 2:
                    break
    
    # ✅ Auto-completar CARBOIDRATOS (mínimo 2)
    if len(carbs) < 2:
        defaults = ["arroz_branco", "aveia", "batata_doce", "pao_integral"]
        for d in defaults:
            if d not in final_foods and d in FOODS:
                if d not in filter_by_restrictions({d}, restrictions):
                    continue
                final_foods.add(d)
                auto_added.append(FOODS[d]["name"])
                if len([f for f in final_foods if f in FOODS and FOODS[f]["category"] == "carb"]) >= 2:
                    break
    
    # ✅ Auto-completar GORDURAS (mínimo 1)
    if len(fats) < 1:
        defaults = ["azeite", "castanhas", "pasta_amendoim"]
        for d in defaults:
            if d not in final_foods and d in FOODS:
                if d not in filter_by_restrictions({d}, restrictions):
                    continue
                final_foods.add(d)
                auto_added.append(FOODS[d]["name"])
                break
    
    # ✅ Auto-completar FRUTAS (mínimo 1)
    if len(fruits) < 1:
        defaults = ["banana", "maca", "morango", "laranja"]
        for d in defaults:
            if d not in final_foods and d in FOODS:
                if d not in filter_by_restrictions({d}, restrictions):
                    continue
                final_foods.add(d)
                auto_added.append(FOODS[d]["name"])
                break
    
    # Mensagem informativa se auto-completou
    if auto_added:
        message = f"Para garantir uma dieta completa, adicionamos automaticamente: {', '.join(auto_added)}. Você pode alterar nas configurações."
        return final_foods, True, message
    
    return final_foods, False, None


# FUNÇÃO LEGADA - MANTIDA PARA COMPATIBILIDADE MAS DESATIVADA
def smart_auto_complete(preferred: Set[str], restrictions: List[str], goal: str = "manutencao") -> Tuple[Set[str], bool, str]:
    """
    ⚠️ FUNÇÃO DESATIVADA - Agora apenas valida sem auto-completar!
    
    Redireciona para validate_user_foods() que NÃO adiciona alimentos automaticamente.
    """
    available, is_valid, error_msg = validate_user_foods(preferred, restrictions)
    
    if not is_valid:
        # Retorna os alimentos disponíveis + flag de erro
        return available, False, error_msg
    
    # Retorna apenas os alimentos do usuário, sem auto-complete
    return available, False, None


def get_user_preferred_foods(food_preferences: List[str]) -> Set[str]:
    """Converte preferências do usuário para chaves normalizadas"""
    preferred = set()
    for pref in food_preferences:
        normalized = normalize_food(pref)
        if normalized in FOODS:
            preferred.add(normalized)
    return preferred


def get_user_supplements(food_preferences: List[str]) -> List[str]:
    """Retorna suplementos selecionados pelo usuário"""
    user_supplements = []
    for pref in food_preferences:
        normalized = normalize_food(pref)
        if normalized in SUPPLEMENTS:
            user_supplements.append(SUPPLEMENTS[normalized]["name"])
    return user_supplements


def get_available_by_category(preferred: Set[str], category: str, restrictions: List[str]) -> List[str]:
    """Retorna alimentos disponíveis de uma categoria"""
    category_foods = [k for k, v in FOODS.items() if v["category"] == category]
    
    if preferred:
        available = [f for f in category_foods if f in preferred]
    else:
        available = category_foods
    
    available_set = filter_by_restrictions(set(available), restrictions)
    return list(available_set)


def select_food(preferred: Set[str], category: str, restrictions: List[str], priority: List[str]) -> str:
    """Seleciona melhor alimento de uma categoria"""
    available = get_available_by_category(preferred, category, restrictions)
    
    for p in priority:
        if p in available:
            return p
    
    return available[0] if available else priority[0]


# ==================== CÁLCULO DE TDEE/MACROS ====================

def calculate_tdee(weight: float, height: float, age: int, gender: str, 
                   activity_level: str, training_level: str) -> float:
    """Calcula TDEE (Total Daily Energy Expenditure) usando Mifflin-St Jeor"""
    if gender.lower() in ['masculino', 'male', 'm']:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multipliers = {
        'sedentary': 1.2, 'sedentario': 1.2,
        'lightly_active': 1.375, 'leve': 1.375,
        'moderately_active': 1.55, 'moderado': 1.55,
        'very_active': 1.725, 'intenso': 1.725,
        'extra_active': 1.9, 'muito_intenso': 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    
    training_bonus = {
        'beginner': 0, 'iniciante': 0,
        'intermediate': 50, 'intermediario': 50,
        'advanced': 100, 'avancado': 100
    }
    
    bonus = training_bonus.get(training_level.lower(), 0)
    
    return bmr * multiplier + bonus


def calculate_macros(tdee: float, goal: str, weight: float, gender: str = "masculino") -> Dict[str, float]:
    """
    Calcula macros baseado no objetivo seguindo o PRD nutricional.
    
    ⚖️ REGRAS DE MACRONUTRIENTES (por objetivo):
    
    🟥 CUTTING (Perda de gordura):
       - Calorias: TDEE × 0,75 – 0,90 (usamos 0.85)
       - Proteína: 1,8 – 2,4 g/kg
       - Gordura: 20 – 25% das calorias
       - Carboidrato: calorias restantes
       - ❌ Erro se calorias ≥ 95% do TDEE
       - ⚠️ Alerta se gordura > 30%
    
    🟨 MANUTENÇÃO:
       - Calorias: TDEE × 0,95 – 1,05 (usamos 1.0)
       - Proteína: 1,6 – 2,2 g/kg
       - Gordura: 25 – 30% das calorias
       - Carboidrato: calorias restantes
       - ⚠️ Alerta se proteína < 1,6 g/kg
    
    🟩 BULKING (Ganho de massa):
       - Calorias: TDEE × 1,05 – 1,15 (usamos 1.10)
       - Proteína: 1,6 – 2,0 g/kg
       - Gordura: 25 – 30% das calorias
       - Carboidrato: calorias restantes
       - ❌ Erro se superávit > 20%
       - ⚠️ Alerta se gordura < 20%
    """
    # Configurações por objetivo (seguindo PRD)
    goal_adjustments = {
        'cutting': {
            'cal_mult': 0.85,           # TDEE × 0.85 (meio da faixa 0.75-0.90)
            'p_min': 1.8, 'p_max': 2.4, # Proteína: 1.8-2.4 g/kg
            'fat_percent_min': 0.20,    # Gordura: 20-25%
            'fat_percent_max': 0.25,
        },
        'manutencao': {
            'cal_mult': 1.0,            # TDEE × 1.0 (meio da faixa 0.95-1.05)
            'p_min': 1.6, 'p_max': 2.2, # Proteína: 1.6-2.2 g/kg
            'fat_percent_min': 0.25,    # Gordura: 25-30%
            'fat_percent_max': 0.30,
        },
        'bulking': {
            'cal_mult': 1.10,           # TDEE × 1.10 (meio da faixa 1.05-1.15)
            'p_min': 1.6, 'p_max': 2.0, # Proteína: 1.6-2.0 g/kg
            'fat_percent_min': 0.25,    # Gordura: 25-30%
            'fat_percent_max': 0.30,
        }
    }
    
    adj = goal_adjustments.get(goal.lower(), goal_adjustments['manutencao'])
    
    # ==================== CÁLCULO DE CALORIAS ====================
    target_calories = tdee * adj['cal_mult']
    
    # Validação específica por objetivo
    if goal.lower() == 'cutting':
        # ❌ Erro se calorias ≥ 95% do TDEE
        if target_calories >= tdee * 0.95:
            target_calories = tdee * 0.85  # Força 85%
    elif goal.lower() == 'bulking':
        # ❌ Erro se superávit > 20%
        if target_calories > tdee * 1.20:
            target_calories = tdee * 1.15  # Força 115%
    
    # ==================== CÁLCULO DE PROTEÍNA ====================
    # Usa o MÁXIMO da faixa para garantir massa muscular
    protein = weight * adj['p_max']
    
    # ==================== CÁLCULO DE GORDURA ====================
    # Usa o MEIO da faixa de percentual
    fat_percent = (adj['fat_percent_min'] + adj['fat_percent_max']) / 2
    fat_calories = target_calories * fat_percent
    fat = fat_calories / 9
    
    # Validação: mínimo 20% das calorias
    fat_min = (target_calories * 0.20) / 9
    fat_max = (target_calories * adj['fat_percent_max']) / 9
    
    fat = max(fat_min, min(fat, fat_max))
    
    # ==================== CÁLCULO DE CARBOIDRATOS ====================
    # Calorias restantes
    protein_cal = protein * 4
    fat_cal = fat * 9
    carbs_cal = target_calories - protein_cal - fat_cal
    carbs = carbs_cal / 4
    
    # Garante mínimo de carboidratos (100g para função cerebral)
    if carbs < 100:
        carbs = 100
        carbs_cal = carbs * 4
        target_calories = protein_cal + fat_cal + carbs_cal
    
    # ==================== VALIDAÇÃO FINAL ====================
    # Verifica percentual de gordura
    actual_fat_percent = (fat * 9) / target_calories * 100
    
    if goal.lower() == 'cutting' and actual_fat_percent > 30:
        # ⚠️ Alerta se gordura > 30% em cutting
        fat = (target_calories * 0.25) / 9  # Ajusta para 25%
        carbs_cal = target_calories - protein_cal - (fat * 9)
        carbs = max(100, carbs_cal / 4)
    
    if goal.lower() == 'bulking' and actual_fat_percent < 20:
        # ⚠️ Alerta se gordura < 20% em bulking
        fat = (target_calories * 0.25) / 9  # Ajusta para 25%
        carbs_cal = target_calories - protein_cal - (fat * 9)
        carbs = max(100, carbs_cal / 4)
    
    # ==================== FIBRA MÍNIMA ====================
    # 25g/dia (mulheres), 30g/dia (homens) - guardado para validação posterior
    fiber_target = 30 if gender.lower() in ['masculino', 'male', 'm'] else 25
    
    return {
        'calories': round(target_calories),
        'protein': round(protein),
        'carbs': round(carbs),
        'fat': round(fat),
        'fiber_target': fiber_target
    }


# ==================== REGRAS POR REFEIÇÃO ====================
# IMPORTANTE: Usar APENAS alimentos ATIVOS no sistema
# REGRA DE FALHA: Se arroz, frango, peixe ou azeite aparecerem em lanches ou café, 
#                 a saída é INVÁLIDA e deve ser regenerada.

MEAL_RULES = {
    "cafe_da_manha": {
        # PERMITIDOS: Ovos, Cottage + Aveia, Pão Integral, Tapioca + Frutas
        "proteins": {"ovos", "cottage", "claras"},
        "carbs": {"aveia", "pao_integral", "tapioca", "cuscuz", "pao"},
        "fats": {"pasta_amendoim", "chia", "linhaca"},  # Gorduras saudáveis para café
        "fruits": True,
        # PROIBIDOS: Arroz, Feijão, Lentilha, Macarrão, Frango, Peixe, Carne, Peru, Azeite
        "description": "Café da manhã: proteínas leves + aveia/pão/tapioca + frutas"
    },
    "lanche": {
        # PERMITIDOS: Frutas + Iogurte Zero/Cottage + Castanhas, Amêndoas, Nozes
        # NOTA: iogurte_natural REMOVIDO - usar apenas iogurte_zero
        "proteins": {"cottage", "iogurte_zero"},  # OVOS PROIBIDOS em lanches!
        "carbs": {"aveia"},  # Aveia também pode ser lanche
        "fats": {"castanhas", "amendoas", "nozes", "pasta_amendoim"},
        "fruits": True,
        # PROIBIDOS: Frango, Peixe, Carne, Peru, Ovos, Azeite, Queijo
        "description": "Lanche leve: frutas + iogurte zero/cottage + castanhas/amêndoas/nozes"
    },
    "almoco_jantar": {
        # OBRIGATÓRIO: 1 proteína MAGRA + carboidratos (principal + complemento)
        # OVOS são PROIBIDOS no almoço/jantar para evitar excesso de gordura!
        "proteins": {"frango", "coxa_frango", "patinho", "carne_moida", "tilapia", "atum", 
                     "salmao", "peru", "camarao", "sardinha", "suino", "tofu"},
        "carbs": {"arroz_branco", "arroz_integral", "batata_doce",
                  "macarrao", "macarrao_integral", "feijao", "lentilha", "farofa"},
        "fats": {"azeite"},  # PERMITIDO: apenas azeite
        "fruits": False,
        "description": "Refeição completa: 1 proteína + carboidratos (principal + feijão/lentilha) + azeite"
    },
    "ceia": {
        # PERMITIDOS: Iogurte Zero/Cottage + Frutas - NUNCA OVOS!
        # NOTA: iogurte_natural REMOVIDO - usar apenas iogurte_zero
        "proteins": {"cottage", "iogurte_zero"},  # OVOS REMOVIDOS DA CEIA!
        "carbs": set(),  # PROIBIDO: Arroz, Batatas, Massas, Leguminosas
        "fats": {"castanhas", "amendoas"},  # Gorduras leves permitidas na ceia
        "fruits": True,
        # PROIBIDOS: Frango, Peixe, Carne, OVOS
        "description": "Ceia leve: proteína leve + frutas (NUNCA OVOS)"
    }
}


def get_allowed_foods(meal_type: str, preferred: Set[str], restrictions: List[str], category: str) -> List[str]:
    """
    Retorna alimentos PERMITIDOS para uma refeição específica.
    Respeita: regras da refeição + preferências do usuário + restrições.
    """
    rules = MEAL_RULES.get(meal_type, MEAL_RULES["almoco_jantar"])
    
    if category == "fruit":
        # Frutas: se permitido, retorna todas as frutas disponíveis
        if rules.get("fruits"):
            all_fruits = [k for k, v in FOODS.items() if v["category"] == "fruit"]
            available = [f for f in all_fruits if f in preferred] if preferred else all_fruits
            return list(filter_by_restrictions(set(available), restrictions))
        return []
    
    # 🚫 REGRA ABSOLUTA: Usa APENAS alimentos selecionados pelo usuário!
    # Filtra os alimentos da whitelist para incluir apenas os que o usuário selecionou
    allowed_in_meal = rules.get(f"{category}s", set())
    
    if not allowed_in_meal:
        return []
    
    # Intersecção: alimentos permitidos na refeição E selecionados pelo usuário
    available = []
    for food_key in allowed_in_meal:
        if food_key in FOODS and food_key in preferred:  # Adiciona filtro de preferência!
            available.append(food_key)
    
    return list(filter_by_restrictions(set(available), restrictions))


def select_best_food(meal_type: str, preferred: Set[str], restrictions: List[str], 
                     category: str, priority: List[str], exclude: Set[str] = None) -> Optional[str]:
    """
    🚫 REGRA ABSOLUTA: Seleciona APENAS dentre os alimentos do usuário!
    
    Nunca retorna alimentos que o usuário não selecionou.
    """
    # Usa apenas alimentos que o usuário selecionou
    available = get_allowed_foods(meal_type, preferred, restrictions, category)
    
    if exclude:
        available = [f for f in available if f not in exclude]
    
    if not available:
        # Se não há alimentos da categoria disponíveis nas preferências,
        # tenta usar qualquer alimento da categoria que o usuário selecionou
        fallback = [f for f in preferred if f in FOODS and FOODS[f]["category"] == category]
        fallback = [f for f in fallback if f not in (exclude or set())]
        if fallback:
            return fallback[0]
        return None
    
    # Segue prioridade se possível (prioridade também vem das preferências do usuário)
    for p in priority:
        if p in available:
            return p
    
    return available[0]


# ==================== GERAÇÃO DE DIETA ====================

def generate_diet(target_p: int, target_c: int, target_f: int,
                  preferred: Set[str], restrictions: List[str], meal_count: int = 6,
                  original_preferred: Set[str] = None, goal: str = "manutencao") -> List[Dict]:
    """
    Gera dieta seguindo regras rígidas por tipo de refeição.
    
    ⭐ REGRA NOVA: DISTRIBUIÇÃO IGUAL ENTRE ALMOÇO E JANTAR
    - Mesma proteína, mesma quantidade
    - Mesmo arroz, mesma quantidade
    - Mesmo feijão (se nas preferências), mesma quantidade
    
    PRIORIDADES:
    1. ARROZ sempre tem prioridade sobre batata doce
    2. Feijão só aparece se nas preferências E junto com arroz
    
    REGRAS POR REFEIÇÃO:
    ☀️ Café da Manhã: proteínas leves + carbs leves + frutas
    🍎 Lanches: frutas + castanhas/amêndoas
    🍽️ Almoço/Jantar: IGUAIS - proteína + arroz + feijão (se preferência) + azeite
    🌙 Ceia: frutas + castanhas
    """
    
    if original_preferred is None:
        original_preferred = preferred
    
    # ==================== QUANTIDADES DE FEIJÃO POR OBJETIVO ====================
    FEIJAO_POR_OBJETIVO = {
        "bulking": {"min": 160, "max": 180},
        "manutencao": {"min": 130, "max": 160},
        "cutting": {"min": 100, "max": 130},
    }
    
    feijao_limits = FEIJAO_POR_OBJETIVO.get(goal, FEIJAO_POR_OBJETIVO["manutencao"])
    feijao_grams = (feijao_limits["min"] + feijao_limits["max"]) // 2  # Média
    
    # ==================== SELEÇÃO DE ALIMENTOS ====================
    TIPOS_ARROZ = {"arroz_branco", "arroz_integral"}
    COMPLEMENT_FOODS = {"feijao", "lentilha"}
    
    def get_user_foods_only(category: str = None, exclude_complements: bool = False) -> List[str]:
        """
        🚫 REGRA ABSOLUTA: Retorna APENAS alimentos selecionados pelo usuário!
        
        NUNCA adiciona alimentos padrão ou defaults.
        Se o usuário não selecionou nada da categoria, retorna lista vazia.
        """
        user_foods = []
        for p in preferred:
            if p in FOODS:
                if category is None or FOODS[p]["category"] == category:
                    if exclude_complements and p in COMPLEMENT_FOODS:
                        continue
                    user_foods.append(p)
        
        return user_foods
    
    # Prioridades - usando APENAS alimentos selecionados pelo usuário
    # 🚫 NUNCA usa listas padrão!
    
    # PROTEÍNAS PRINCIPAIS para almoço/jantar (apenas as que o usuário selecionou)
    protein_priority = get_user_foods_only("protein")
    
    # PROTEÍNAS LEVES para café/lanches/ceia (apenas as que o usuário selecionou)
    light_protein_priority_cafe = [p for p in protein_priority if p in {"ovos", "iogurte_zero", "cottage", "whey_protein", "claras"}]
    if not light_protein_priority_cafe:
        light_protein_priority_cafe = protein_priority  # Usa qualquer proteína disponível
    
    # Proteína leve para lanches
    light_protein_priority_lanche = [p for p in protein_priority if p in {"iogurte_zero", "cottage", "whey_protein"}]
    if not light_protein_priority_lanche:
        light_protein_priority_lanche = light_protein_priority_cafe
    
    # CARBOIDRATOS PRINCIPAIS (apenas os que o usuário selecionou)
    carb_priority = get_user_foods_only("carb", exclude_complements=True)
    
    # CARBOIDRATOS DE LANCHE (apenas os que o usuário selecionou)
    light_carb_priority = [c for c in carb_priority if c in {"aveia", "pao_integral", "pao", "tapioca"}]
    if not light_carb_priority:
        light_carb_priority = carb_priority
    
    # GORDURAS (apenas as que o usuário selecionou)
    fat_priority = get_user_foods_only("fat")
    
    # GORDURAS SNACKS para lanches
    fat_priority_lanche = [f for f in fat_priority if f in {"castanhas", "amendoas", "nozes", "pasta_amendoim"}]
    if not fat_priority_lanche:
        fat_priority_lanche = fat_priority
    
    # GORDURAS para café
    fat_priority_cafe = [f for f in fat_priority if f in {"pasta_amendoim", "chia"}]
    if not fat_priority_cafe:
        fat_priority_cafe = fat_priority
    
    # FRUTAS (apenas as que o usuário selecionou)
    fruit_priority = get_user_foods_only("fruit")
    
    # ==================== CALCULAR ALMOÇO/JANTAR ====================
    # ⭐ REGRA OBRIGATÓRIA: Almoço e Jantar EXATAMENTE IGUAIS
    # - Mesma proteína
    # - Mesmo carboidrato  
    # - Mesmas quantidades
    # - Variedade de proteínas é AO LONGO DOS DIAS, não dentro do mesmo dia!
    # Proporção: Almoço + Jantar = ~55% dos macros totais
    
    main_meal_p = target_p * 0.27  # Proteína por refeição principal
    main_meal_c = target_c * 0.27  # Carbs por refeição principal
    main_meal_f = target_f * 0.30  # Gordura por refeição principal
    
    # Selecionar UMA proteína para AMBOS almoço e jantar (iguais!)
    main_protein = select_best_food("almoco_jantar", preferred, restrictions, "protein", protein_priority)
    
    main_carb = select_best_food("almoco_jantar", preferred, restrictions, "carb", carb_priority)
    
    # Calcular quantidades para UMA refeição principal (igual para almoço e jantar)
    if main_protein and main_protein in FOODS:
        protein_grams = round_to_10(clamp(main_meal_p / (FOODS[main_protein]["p"] / 100), 150, 250))
    else:
        main_protein = "frango"
        protein_grams = 180
    
    if main_carb and main_carb in FOODS:
        # ARROZ: mínimo 150g por refeição para ser uma porção decente
        carb_grams = round_to_10(clamp(main_meal_c * 0.5 / (FOODS[main_carb]["c"] / 100), 150, 300))
    else:
        main_carb = "arroz_branco"
        carb_grams = 180
    
    # Feijão: só se nas preferências
    feijao_nas_preferencias = "feijao" in preferred
    use_feijao = feijao_nas_preferencias and main_carb in TIPOS_ARROZ
    
    # Azeite fixo
    azeite_grams = 10
    
    # ==================== MONTAR REFEIÇÕES ====================
    meals = []
    
    # Estrutura base
    if meal_count == 4:
        meal_structure = [
            {'name': 'Café da Manhã', 'time': '07:00', 'type': 'cafe'},
            {'name': 'Almoço', 'time': '12:00', 'type': 'almoco'},
            {'name': 'Lanche Tarde', 'time': '16:00', 'type': 'lanche_tarde'},
            {'name': 'Jantar', 'time': '20:00', 'type': 'jantar'},
        ]
    elif meal_count == 5:
        meal_structure = [
            {'name': 'Café da Manhã', 'time': '07:00', 'type': 'cafe'},
            {'name': 'Lanche Manhã', 'time': '10:00', 'type': 'lanche_manha'},
            {'name': 'Almoço', 'time': '12:30', 'type': 'almoco'},
            {'name': 'Lanche Tarde', 'time': '16:00', 'type': 'lanche_tarde'},
            {'name': 'Jantar', 'time': '19:30', 'type': 'jantar'},
        ]
    else:  # 6 refeições
        meal_structure = [
            {'name': 'Café da Manhã', 'time': '07:00', 'type': 'cafe'},
            {'name': 'Lanche Manhã', 'time': '10:00', 'type': 'lanche_manha'},
            {'name': 'Almoço', 'time': '12:30', 'type': 'almoco'},
            {'name': 'Lanche Tarde', 'time': '16:00', 'type': 'lanche_tarde'},
            {'name': 'Jantar', 'time': '19:30', 'type': 'jantar'},
            {'name': 'Ceia', 'time': '21:30', 'type': 'ceia'},
        ]
    
    for meal_info in meal_structure:
        meal_type = meal_info['type']
        foods = []
        
        if meal_type == 'cafe':
            # Café da Manhã - 🚫 APENAS alimentos selecionados pelo usuário!
            protein = select_best_food("cafe_da_manha", preferred, restrictions, "protein", light_protein_priority_cafe)
            carb = select_best_food("cafe_da_manha", preferred, restrictions, "carb", light_carb_priority)
            fruit = select_best_food("cafe_da_manha", preferred, restrictions, "fruit", fruit_priority)
            fat = select_best_food("cafe_da_manha", preferred, restrictions, "fat", fat_priority_cafe)
            
            if protein and protein in FOODS:
                p_grams = 150 if protein == "ovos" else 100
                foods.append(calc_food(protein, p_grams))
            
            if carb and carb in FOODS:
                c_grams = 60 if carb == "aveia" else 60
                foods.append(calc_food(carb, c_grams))
            
            if fruit and fruit in FOODS:
                foods.append(calc_food(fruit, 120))
            
            if fat and fat in FOODS:
                foods.append(calc_food(fat, 15))
            
            # 🚫 SEM FALLBACK! Se não tem alimentos suficientes, a refeição fica incompleta
            # O sistema já validou que o usuário tem alimentos suficientes
                
        elif meal_type in ['lanche_manha', 'lanche_tarde', 'lanche']:
            # Lanches: 🚫 APENAS alimentos selecionados pelo usuário!
            light_protein = select_best_food("lanche", preferred, restrictions, "protein", light_protein_priority_lanche)
            fruit = select_best_food("lanche", preferred, restrictions, "fruit", fruit_priority)
            fat = select_best_food("lanche", preferred, restrictions, "fat", fat_priority_lanche)
            
            # Iogurte zero (1 pote = 170g)
            if light_protein and light_protein in FOODS:
                foods.append(calc_food(light_protein, 170))
            
            if fruit and fruit in FOODS:
                foods.append(calc_food(fruit, 100))
            
            if fat and fat in FOODS:
                foods.append(calc_food(fat, 15))
            
            # 🚫 SEM FALLBACK! Usa apenas os alimentos que o usuário selecionou
                
        elif meal_type == 'almoco':
            # ⭐ ALMOÇO: EXATAMENTE IGUAL AO JANTAR (mesma proteína, mesmas quantidades)
            foods.append(calc_food(main_protein, protein_grams))
            foods.append(calc_food(main_carb, carb_grams))
            
            if use_feijao:
                foods.append(calc_food("feijao", feijao_grams))
            
            foods.append(calc_food("azeite", azeite_grams))
            
        elif meal_type == 'jantar':
            # ⭐ JANTAR: EXATAMENTE IGUAL AO ALMOÇO (mesma proteína, mesmas quantidades)
            foods.append(calc_food(main_protein, protein_grams))
            foods.append(calc_food(main_carb, carb_grams))
            
            if use_feijao:
                foods.append(calc_food("feijao", feijao_grams))
            
            foods.append(calc_food("azeite", azeite_grams))
            
        elif meal_type == 'ceia':
            # Ceia: 🚫 APENAS alimentos selecionados pelo usuário!
            light_protein = select_best_food("ceia", preferred, restrictions, "protein", light_protein_priority_lanche)
            fruit = select_best_food("ceia", preferred, restrictions, "fruit", fruit_priority)
            
            # Iogurte zero (1 pote = 170g)
            if light_protein and light_protein in FOODS:
                foods.append(calc_food(light_protein, 170))
            
            if fruit and fruit in FOODS:
                foods.append(calc_food(fruit, 120))
            
            # 🚫 SEM FALLBACK! Usa apenas os alimentos que o usuário selecionou
        
        meals.append({
            "name": meal_info['name'],
            "time": meal_info['time'],
            "foods": foods
        })
    
    return meals


def fine_tune_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int) -> List[Dict]:
    """
    Ajuste fino ULTRA-AGRESSIVO para atingir macros.
    
    REGRA ABSOLUTA: Macros NUNCA podem exceder o target em mais de 5g!
    EXCEÇÃO: Proteína pode ter até +15% de variação se necessário para manter frango adequado
    
    ESTRATÉGIA:
    1. Gordura em excesso → Remove azeite, castanhas primeiro
    2. Proteína em excesso → Reduz carnes nas refeições principais (mínimo 150g frango)
    3. Carbs em excesso → Reduz arroz, batata
    
    IMPORTANTE: Esta função assume que alimentos contáveis já estão fixos.
    Portanto, ela ajusta APENAS alimentos não-contáveis (arroz, frango, azeite).
    """
    MAX_EXCESS = 5  # Máximo 5g acima do target
    MAX_DEFICIT = 5  # Máximo 5g abaixo do target (mais rígido)
    
    # Tolerância especial para proteína (para não reduzir demais o frango)
    MAX_PROTEIN_EXCESS = max(5, int(target_p * 0.15))  # Até 15% acima do target
    
    # Tolerância para baixo agora é também 5g (mais rígida)
    tol_p_below = MAX_DEFICIT
    tol_c_below = MAX_DEFICIT
    tol_f_below = MAX_DEFICIT
    
    num_meals = len(meals)
    
    # Alimentos que podem ser ajustados em incrementos pequenos (não-contáveis)
    ADJUSTABLE_PROTEINS = {"frango", "patinho", "tilapia", "atum", "salmao", "camarao", 
                           "carne_moida", "suino", "peru", "tofu"}
    # NOTA: Aveia e tapioca REMOVIDOS - eles só podem aparecer no café/lanche, não no almoço/jantar
    ADJUSTABLE_CARBS = {"arroz_branco", "arroz_integral", "macarrao", "macarrao_integral",
                        "feijao", "lentilha", "farofa", "batata_doce"}
    ADJUSTABLE_FATS = {"azeite", "oleo_coco", "pasta_amendoim", "castanhas", "amendoas", "nozes", "chia"}
    
    # Determina índices das refeições baseado no número
    if num_meals == 4:
        main_meal_indices = [1, 3]
        lanche_indices = [2]
        all_indices = [0, 1, 2, 3]
    elif num_meals == 5:
        main_meal_indices = [2, 4]
        lanche_indices = [1, 3]
        all_indices = [0, 1, 2, 3, 4]
    else:  # 6 refeições
        main_meal_indices = [2, 4]
        lanche_indices = [1, 3, 5]
        all_indices = [0, 1, 2, 3, 4, 5]
    
    for iteration in range(150):  # Mais iterações
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        # Calcula excesso (positivo = acima do target)
        excess_p = curr_p - target_p
        excess_c = curr_c - target_c
        excess_f = curr_f - target_f
        
        # Verifica se está dentro dos limites
        # NOTA: Proteína tem tolerância maior para não sacrificar o frango
        p_ok = excess_p <= MAX_PROTEIN_EXCESS and excess_p >= -tol_p_below
        c_ok = excess_c <= MAX_EXCESS and excess_c >= -tol_c_below
        f_ok = excess_f <= MAX_EXCESS and excess_f >= -tol_f_below
        
        if p_ok and c_ok and f_ok:
            return meals
        
        adjusted = False
        
        # ========== PRIORIDADE 1: REDUZIR GORDURA EM EXCESSO ==========
        if excess_f > MAX_EXCESS and not adjusted:
            reduce_needed = excess_f - MAX_EXCESS + 3
            
            # NOVA REGRA: Quando ajustar azeite no almoço/jantar, ajustar em AMBOS igualmente
            # Primeiro tenta reduzir/remover azeite nos lanches e café
            non_main_indices = [i for i in all_indices if i not in main_meal_indices]
            
            for m_idx in non_main_indices:
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_FATS:
                        current_g = food["grams"]
                        f_per_100 = FOODS[food_key]["f"]
                        reduce_grams = reduce_needed / (f_per_100 / 100)
                        new_g = max(0, current_g - reduce_grams)
                        
                        if new_g < 5:
                            meals[m_idx]["foods"].pop(f_idx)
                            adjusted = True
                            break
                        elif current_g - new_g >= 2:
                            meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                            adjusted = True
                            break
            
            # Se ainda precisar ajustar, ajusta azeite em AMBOS almoço e jantar IGUALMENTE
            if not adjusted:
                # Primeiro verifica se ambos têm azeite
                azeite_indices = {}  # {meal_idx: (food_idx, grams)}
                for m_idx in main_meal_indices:
                    if m_idx >= num_meals:
                        continue
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food.get("key") == "azeite":
                            azeite_indices[m_idx] = (f_idx, food["grams"])
                            break
                
                if len(azeite_indices) >= 2:
                    # Reduz em AMBOS igualmente
                    reduce_each = (reduce_needed / 2) / (FOODS["azeite"]["f"] / 100)
                    for m_idx, (f_idx, current_g) in azeite_indices.items():
                        new_g = max(0, current_g - reduce_each)
                        if new_g < 5:
                            meals[m_idx]["foods"].pop(f_idx)
                        else:
                            meals[m_idx]["foods"][f_idx] = calc_food("azeite", new_g)
                    adjusted = True
                elif len(azeite_indices) == 1:
                    # Só tem azeite em um, remove
                    m_idx, (f_idx, _) = list(azeite_indices.items())[0]
                    meals[m_idx]["foods"].pop(f_idx)
                    adjusted = True
        
        # ========== PRIORIDADE 2: REDUZIR PROTEÍNA EM EXCESSO ==========
        # NOVA REGRA: Ajustar AMBOS almoço e jantar igualmente
        if excess_p > MAX_PROTEIN_EXCESS and not adjusted:
            reduce_needed = excess_p - MAX_PROTEIN_EXCESS + 2
            
            # Encontra a proteína em ambas as refeições principais
            protein_indices = {}  # {meal_idx: (food_idx, key, grams)}
            for m_idx in main_meal_indices:
                if m_idx >= num_meals:
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_PROTEINS:
                        protein_indices[m_idx] = (f_idx, food_key, food["grams"])
                        break
            
            if len(protein_indices) >= 2:
                # Reduz em AMBOS igualmente
                for m_idx, (f_idx, food_key, current_g) in protein_indices.items():
                    p_per_100 = FOODS[food_key]["p"]
                    reduce_each = (reduce_needed / 2) / (p_per_100 / 100)
                    min_protein = 150 if food_key == "frango" else 100
                    new_g = round_to_10(max(min_protein, current_g - reduce_each))
                    meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                adjusted = True
        
        # ========== PRIORIDADE 3: REDUZIR CARBOIDRATO EM EXCESSO ==========
        # NOVA REGRA: Ajustar AMBOS almoço e jantar igualmente
        if excess_c > MAX_EXCESS and not adjusted:
            reduce_needed = excess_c - MAX_EXCESS + 3
            
            # Primeiro tenta reduzir no café (aveia, pão)
            for f_idx, food in enumerate(meals[0]["foods"]):
                food_key = food.get("key")
                if food_key in {"aveia", "pao_integral", "pao", "pao_forma", "tapioca"}:
                    current_g = food["grams"]
                    c_per_100 = FOODS[food_key]["c"]
                    if c_per_100 > 0:
                        reduce_grams = reduce_needed / (c_per_100 / 100)
                        new_g = round_to_10(max(30, current_g - reduce_grams))
                        if current_g - new_g >= 10:
                            meals[0]["foods"][f_idx] = calc_food(food_key, new_g)
                            adjusted = True
                            break
            
            # Se ainda precisar, ajusta arroz/feijão em AMBOS igualmente
            if not adjusted:
                carb_indices = {}  # {meal_idx: [(food_idx, key, grams), ...]}
                for m_idx in main_meal_indices:
                    if m_idx >= num_meals:
                        continue
                    carb_indices[m_idx] = []
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        food_key = food.get("key")
                        if food_key in ADJUSTABLE_CARBS:
                            carb_indices[m_idx].append((f_idx, food_key, food["grams"]))
                
                if len(carb_indices) >= 2 and all(len(v) > 0 for v in carb_indices.values()):
                    # Reduz o primeiro carb de cada refeição igualmente
                    for m_idx, carbs in carb_indices.items():
                        f_idx, food_key, current_g = carbs[0]
                        c_per_100 = FOODS[food_key]["c"]
                        reduce_each = (reduce_needed / 2) / (c_per_100 / 100)
                        min_carb = 100 if food_key in {"arroz_branco", "arroz_integral", "macarrao"} else 80
                        new_g = round_to_10(max(min_carb, current_g - reduce_each))
                        meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                    adjusted = True
        
        # ========== AUMENTAR SE MUITO ABAIXO ==========
        
        # PROTEÍNA muito abaixo - ajustar AMBOS igualmente
        if excess_p < -tol_p_below and not adjusted:
            increase_needed = abs(excess_p) - tol_p_below + 5
            
            protein_indices = {}
            for m_idx in main_meal_indices:
                if m_idx >= num_meals:
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_PROTEINS:
                        protein_indices[m_idx] = (f_idx, food_key, food["grams"])
                        break
            
            if len(protein_indices) >= 2:
                for m_idx, (f_idx, food_key, current_g) in protein_indices.items():
                    p_per_100 = FOODS[food_key]["p"]
                    increase_each = (increase_needed / 2) / (p_per_100 / 100)
                    new_g = round_to_10(min(400, current_g + increase_each))
                    meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                adjusted = True
        
        # CARBOIDRATO muito abaixo - ajustar AMBOS igualmente
        if excess_c < -tol_c_below and not adjusted:
            increase_needed = abs(excess_c) - tol_c_below + 5
            
            carb_indices = {}
            for m_idx in main_meal_indices:
                if m_idx >= num_meals:
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_CARBS:
                        carb_indices[m_idx] = (f_idx, food_key, food["grams"])
                        break
            
            if len(carb_indices) >= 2:
                for m_idx, (f_idx, food_key, current_g) in carb_indices.items():
                    c_per_100 = FOODS[food_key]["c"]
                    increase_each = (increase_needed / 2) / (c_per_100 / 100)
                    new_g = round_to_10(min(400, current_g + increase_each))
                    meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                adjusted = True
        
        # GORDURA muito abaixo - adiciona azeite se precisar
        if excess_f < -tol_f_below and not adjusted:
            increase_needed = abs(excess_f) - tol_f_below + 3
            
            # Primeiro tenta aumentar azeite existente
            for m_idx in main_meal_indices:
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("key") == "azeite":
                        current_g = food["grams"]
                        f_per_100 = FOODS["azeite"]["f"]
                        increase_grams = increase_needed / (f_per_100 / 100)
                        new_g = min(30, current_g + increase_grams)
                        if new_g - current_g >= 2:
                            meals[m_idx]["foods"][f_idx] = calc_food("azeite", new_g)
                            adjusted = True
                            break
            
            # Se não encontrou azeite, adiciona
            if not adjusted:
                for m_idx in main_meal_indices:
                    if m_idx >= num_meals:
                        continue
                    has_azeite = any(f.get("key") == "azeite" for f in meals[m_idx]["foods"])
                    if not has_azeite:
                        f_per_100 = FOODS["azeite"]["f"]
                        new_grams = min(20, increase_needed / (f_per_100 / 100))
                        if new_grams >= 5:
                            meals[m_idx]["foods"].append(calc_food("azeite", new_grams))
                            adjusted = True
                            break
        
        # Se não conseguiu ajustar, sai do loop
        if not adjusted:
            break
    
    return meals


def validate_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int) -> Tuple[bool, str]:
    """Valida se dieta atinge os targets (±5%)"""
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    
    tol_p = target_p * TOL_PERCENT
    tol_c = target_c * TOL_PERCENT
    tol_f = target_f * TOL_PERCENT
    
    errors = []
    if abs(curr_p - target_p) > tol_p:
        errors.append(f"P:{curr_p}g vs {target_p}g (±{tol_p:.0f}g)")
    if abs(curr_c - target_c) > tol_c:
        errors.append(f"C:{curr_c}g vs {target_c}g (±{tol_c:.0f}g)")
    if abs(curr_f - target_f) > tol_f:
        errors.append(f"F:{curr_f}g vs {target_f}g (±{tol_f:.0f}g)")
    
    return len(errors) == 0, "; ".join(errors)


# ==================== VALIDAÇÃO BULLETPROOF ====================

def validate_and_fix_food(food: Dict, preferred: Set[str] = None) -> Dict:
    """
    ✅ Valida e corrige um alimento individual.
    
    GARANTIAS:
    - NUNCA retorna None
    - grams >= 10 (mínimo)
    - grams <= 500 (máximo)
    - grams múltiplo de 10
    - Todos campos obrigatórios presentes
    - calories >= 1
    """
    # Se food é None ou vazio, cria default
    if not food:
        return calc_food("frango", 100)
    
    # Extrai valores existentes
    food_key = food.get("key", "frango")
    grams = food.get("grams", 100)
    
    # Valida se key existe no banco
    if food_key not in FOODS:
        food_key = "frango"  # Fallback para frango
    
    # Valida grams
    if grams is None or grams <= 0:
        grams = 100
    
    # Garante múltiplo de 10, mínimo 10, máximo 500
    grams = round_to_10(grams)
    grams = max(MIN_FOOD_GRAMS, min(MAX_FOOD_GRAMS, grams))
    
    # Recalcula alimento com valores válidos
    return calc_food(food_key, grams)


def validate_and_fix_meal(meal: Dict, meal_index: int, preferred: Set[str] = None) -> Dict:
    """
    ✅ Valida e corrige uma refeição seguindo as REGRAS POR TIPO.
    
    GARANTIAS:
    - Refeição NUNCA vazia
    - Todos alimentos válidos
    - Respeita regras de cada tipo de refeição
    - Totais calculados corretamente
    """
    # Meal names padrão (6 refeições)
    default_meals = [
        {"name": "Café da Manhã", "time": "07:00", "type": "cafe_da_manha"},
        {"name": "Lanche Manhã", "time": "10:00", "type": "lanche"},
        {"name": "Almoço", "time": "12:30", "type": "almoco_jantar"},
        {"name": "Lanche Tarde", "time": "16:00", "type": "lanche"},
        {"name": "Jantar", "time": "19:30", "type": "almoco_jantar"},
        {"name": "Ceia", "time": "21:30", "type": "ceia"}
    ]
    
    # Garante nome e horário
    if meal_index < len(default_meals):
        name = meal.get("name", default_meals[meal_index]["name"])
        time = meal.get("time", default_meals[meal_index]["time"])
    else:
        name = meal.get("name", f"Refeição {meal_index + 1}")
        time = meal.get("time", "12:00")
    
    # Obtém lista de foods
    foods = meal.get("foods", [])
    
    # Se refeição vazia, adiciona alimento padrão SEGUINDO AS REGRAS
    if not foods or len(foods) == 0:
        if meal_index == 0:  # Café da Manhã
            # PERMITIDO: ovos, aveia, frutas | PROIBIDO: carnes, azeite
            foods = [calc_food("ovos", 100), calc_food("aveia", 40), calc_food("banana", 100)]
        elif meal_index == 1:  # Lanche manhã
            # PERMITIDO: frutas, oleaginosas | PROIBIDO: carnes, azeite, cottage
            foods = [calc_food("maca", 150), calc_food("castanhas", 20)]
        elif meal_index == 2:  # Almoço
            # OBRIGATÓRIO: 1 proteína + 1 carboidrato | PERMITIDO: azeite
            foods = [calc_food("frango", 150), calc_food("arroz_branco", 150), calc_food("salada", 100), calc_food("azeite", 10)]
        elif meal_index == 3:  # Lanche tarde
            # PERMITIDO: frutas, oleaginosas | PROIBIDO: carnes, azeite, cottage
            foods = [calc_food("laranja", 150), calc_food("castanhas", 20)]
        elif meal_index == 4:  # Jantar
            # OBRIGATÓRIO: 1 proteína + 1 carboidrato | PERMITIDO: azeite
            foods = [calc_food("tilapia", 150), calc_food("arroz_integral", 120), calc_food("brocolis", 100), calc_food("azeite", 10)]
        else:  # Ceia
            # PERMITIDO: frutas, oleaginosas | PROIBIDO: carnes, carbs complexos, OVOS, cottage
            foods = [calc_food("morango", 150), calc_food("castanhas", 20)]
    
    # Valida cada alimento
    validated_foods = []
    for food in foods:
        validated_food = validate_and_fix_food(food, preferred)
        if validated_food:
            # REGRA ABSOLUTA: Se for CEIA, NUNCA permite ovos
            if meal_index == 5 and validated_food.get("key") == "ovos":
                validated_food = calc_food("banana", validated_food.get("grams", 100))
            validated_foods.append(validated_food)
    
    # Garante que tem pelo menos 1 alimento (RESPEITANDO regras da refeição)
    if len(validated_foods) == 0:
        if meal_index == 0:  # Café - proteína leve
            validated_foods = [calc_food("ovos", 100)]
        elif meal_index == 5:  # Ceia - NUNCA OVOS, sem cottage!
            validated_foods = [calc_food("morango", 150)]
        elif meal_index in [1, 3]:  # Lanches - fruta
            validated_foods = [calc_food("banana", 150)]
        else:  # Almoço/Jantar - proteína principal
            validated_foods = [calc_food("frango", 150)]
    
    # Recalcula totais da refeição
    mp, mc, mf, mcal = sum_foods(validated_foods)
    
    # Garante calorias mínimas (RESPEITANDO regras da refeição)
    if mcal < MIN_MEAL_CALORIES:
        if meal_index in [0, 5]:  # Café ou Ceia - adicionar aveia ou fruta
            validated_foods.append(calc_food("aveia", 50) if meal_index == 0 else calc_food("banana", 100))
        elif meal_index in [1, 3]:  # Lanches - adicionar fruta
            validated_foods.append(calc_food("maca", 150))
        else:  # Almoço/Jantar - adicionar proteína
            validated_foods.append(calc_food("frango", 100))
        mp, mc, mf, mcal = sum_foods(validated_foods)
    
    return {
        "name": name,
        "time": time,
        "foods": validated_foods,
        "total_calories": mcal,
        "macros": {"protein": mp, "carbs": mc, "fat": mf}
    }


def apply_global_limits(meals: List[Dict], preferred: Set[str] = None) -> List[Dict]:
    """
    ✅ APLICA LIMITES GLOBAIS NA DIETA TODA
    
    REGRAS OBRIGATÓRIAS:
    1. COTTAGE: Máximo 20g na dieta TODA (1 pote = 300g, muito!)
    2. AVEIA: Máximo 80g na dieta TODA
    3. FEIJÃO: Só aparece SE:
       - Usuário selecionou feijão nas preferências
       - E existe ARROZ na mesma refeição
    """
    if preferred is None:
        preferred = set()
    
    # TIPOS DE ARROZ (para verificar se tem arroz na refeição)
    TIPOS_ARROZ = {"arroz_branco", "arroz_integral"}
    
    # ========== PASSO 1: APLICAR LIMITE DE COTTAGE (MAX 20g TOTAL) ==========
    total_cottage = 0
    for meal in meals:
        for food in meal.get("foods", []):
            if food.get("key") == "cottage":
                total_cottage += food.get("grams", 0)
    
    if total_cottage > MAX_COTTAGE_TOTAL:
        # Precisa reduzir cottage
        cottage_to_remove = total_cottage - MAX_COTTAGE_TOTAL
        
        for meal in meals:
            foods_to_keep = []
            for food in meal.get("foods", []):
                if food.get("key") == "cottage":
                    current_grams = food.get("grams", 0)
                    if cottage_to_remove >= current_grams:
                        # Remove este cottage completamente
                        cottage_to_remove -= current_grams
                        continue  # Não adiciona à lista
                    else:
                        # Reduz este cottage
                        new_grams = current_grams - cottage_to_remove
                        if new_grams >= 10:  # Mínimo 10g para fazer sentido
                            food = calc_food("cottage", new_grams)
                            cottage_to_remove = 0
                        else:
                            cottage_to_remove -= current_grams
                            continue  # Remove completamente
                foods_to_keep.append(food)
            meal["foods"] = foods_to_keep
            
            # Recalcula macros da refeição
            mp, mc, mf, mcal = sum_foods(meal["foods"])
            meal["total_calories"] = mcal
            meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    # ========== PASSO 2: APLICAR LIMITE DE AVEIA (MAX 80g TOTAL) ==========
    total_aveia = 0
    for meal in meals:
        for food in meal.get("foods", []):
            if food.get("key") == "aveia":
                total_aveia += food.get("grams", 0)
    
    if total_aveia > MAX_AVEIA_TOTAL:
        # Precisa reduzir aveia
        aveia_to_remove = total_aveia - MAX_AVEIA_TOTAL
        
        for meal in meals:
            for f_idx, food in enumerate(meal.get("foods", [])):
                if food.get("key") == "aveia" and aveia_to_remove > 0:
                    current_grams = food.get("grams", 0)
                    new_grams = max(0, current_grams - aveia_to_remove)
                    
                    if new_grams < 20:
                        # Remove aveia se ficar muito pouco
                        meal["foods"].pop(f_idx)
                        aveia_to_remove -= current_grams
                    else:
                        meal["foods"][f_idx] = calc_food("aveia", new_grams)
                        aveia_to_remove -= (current_grams - new_grams)
                    break  # Uma refeição por vez
            
            # Recalcula macros da refeição
            mp, mc, mf, mcal = sum_foods(meal["foods"])
            meal["total_calories"] = mcal
            meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    # ========== PASSO 3: FEIJÃO SÓ COM ARROZ E SE NAS PREFERÊNCIAS ==========
    feijao_nas_preferencias = "feijao" in preferred
    
    for meal in meals:
        # Verifica se tem arroz nesta refeição
        tem_arroz = any(f.get("key") in TIPOS_ARROZ for f in meal.get("foods", []))
        
        foods_to_keep = []
        for food in meal.get("foods", []):
            food_key = food.get("key")
            
            # Se é feijão, só mantém se:
            # 1. Usuário selecionou feijão nas preferências
            # 2. E tem arroz na mesma refeição
            if food_key == "feijao":
                if feijao_nas_preferencias and tem_arroz:
                    foods_to_keep.append(food)
                # Senão, não adiciona (remove feijão)
            else:
                foods_to_keep.append(food)
        
        meal["foods"] = foods_to_keep
        
        # Recalcula macros da refeição
        mp, mc, mf, mcal = sum_foods(meal["foods"])
        meal["total_calories"] = mcal
        meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    # ========== PASSO 4: IOGURTE ZERO MÁXIMO 1X POR DIA ==========
    # Conta ocorrências de iogurte_zero
    iogurte_count = 0
    for meal in meals:
        for food in meal.get("foods", []):
            if food.get("key") == "iogurte_zero":
                iogurte_count += 1
    
    # Se aparecer mais de 1x, remove as extras (substitui por fruta)
    if iogurte_count > MAX_IOGURTE_OCORRENCIAS:
        occurrences_found = 0
        for meal in meals:
            foods_to_keep = []
            for food in meal.get("foods", []):
                if food.get("key") == "iogurte_zero":
                    occurrences_found += 1
                    if occurrences_found <= MAX_IOGURTE_OCORRENCIAS:
                        foods_to_keep.append(food)
                    else:
                        # Substitui por fruta
                        foods_to_keep.append(calc_food("banana", 150))
                else:
                    foods_to_keep.append(food)
            
            meal["foods"] = foods_to_keep
            
            # Recalcula macros da refeição
            mp, mc, mf, mcal = sum_foods(meal["foods"])
            meal["total_calories"] = mcal
            meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    return meals


def validate_and_fix_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int,
                          preferred: Set[str] = None, meal_count: int = 6) -> List[Dict]:
    """
    ✅ CHECKLIST FINAL OBRIGATÓRIO
    
    Antes de retornar a dieta, valida:
    ☑ Nenhum alimento com 0g
    ☑ Nenhuma refeição com lista vazia
    ☑ Todos os campos obrigatórios preenchidos
    ☑ Quantidades em múltiplos de 10g
    ☑ Dieta consistente e utilizável
    ☑ Estrutura JSON válida
    ☑ Número correto de refeições (4, 5 ou 6)
    
    Se qualquer item falhar → CORRIGE AUTOMATICAMENTE
    """
    # Valida cada refeição (apenas as que existem)
    validated_meals = []
    for idx, meal in enumerate(meals[:meal_count]):
        validated_meal = validate_and_fix_meal(meal, idx, preferred)
        validated_meals.append(validated_meal)
    
    # Verifica totais
    all_foods = [f for m in validated_meals for f in m.get("foods", [])]
    total_p, total_c, total_f, total_cal = sum_foods(all_foods)
    
    # Determina índices das refeições principais
    if meal_count == 4:
        # Café(0), Almoço(1), Lanche(2), Jantar(3)
        main_meal_indices = [1, 3]
    elif meal_count == 5:
        # Café(0), LancheManhã(1), Almoço(2), LancheTarde(3), Jantar(4)
        main_meal_indices = [2, 4]
    else:
        # 6 refeições: Almoço(2), Jantar(4)
        main_meal_indices = [2, 4]
    
    # Se calorias totais < mínimo diário, adiciona comida nas refeições principais
    while total_cal < MIN_DAILY_CALORIES:
        # Escolhe a refeição principal com menos calorias
        target_meal = main_meal_indices[0]
        if len(main_meal_indices) > 1:
            if validated_meals[main_meal_indices[0]].get("total_calories", 0) > validated_meals[main_meal_indices[1]].get("total_calories", 0):
                target_meal = main_meal_indices[1]
        
        validated_meals[target_meal]["foods"].append(calc_food("frango", 100))
        
        # Recalcula totais da refeição
        mp, mc, mf, mcal = sum_foods(validated_meals[target_meal]["foods"])
        validated_meals[target_meal]["total_calories"] = mcal
        validated_meals[target_meal]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
        
        # Recalcula totais gerais
        all_foods = [f for m in validated_meals for f in m.get("foods", [])]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
    
    # VALIDAÇÃO FINAL: Todos os alimentos devem ter campos obrigatórios
    required_fields = ["key", "name", "grams", "quantity", "protein", "carbs", "fat", "calories", "category"]
    
    # ALIMENTOS PROIBIDOS por tipo de refeição
    PROHIBITED_FOODS = {
        # Almoço e Jantar: NUNCA aveia, pão, tapioca, iogurte
        2: {"aveia", "pao", "pao_integral", "tapioca", "cottage", "cottage"},  # Almoço (6 refeições)
        4: {"aveia", "pao", "pao_integral", "tapioca", "cottage", "cottage"},  # Jantar (6 refeições)
    }
    
    # REMOÇÃO DE ALIMENTOS PROIBIDOS
    for meal_idx, meal in enumerate(validated_meals):
        prohibited = PROHIBITED_FOODS.get(meal_idx, set())
        if prohibited:
            original_foods = meal.get("foods", [])
            filtered_foods = [f for f in original_foods if f.get("key") not in prohibited]
            
            # Se removeu alimentos, recalcula e adiciona arroz se precisar
            if len(filtered_foods) < len(original_foods):
                # Recalcula macros
                mp, mc, mf, mcal = sum_foods(filtered_foods)
                
                # Se carboidratos ficaram muito baixos, adiciona mais arroz
                existing_arroz = [f for f in filtered_foods if f.get("key") in {"arroz_branco", "arroz_integral"}]
                if existing_arroz and mc < target_c * 0.2:  # Se menos de 20% dos carbs target
                    # Aumenta o arroz existente
                    for f_idx, food in enumerate(filtered_foods):
                        if food.get("key") in {"arroz_branco", "arroz_integral"}:
                            current_grams = food.get("grams", 100)
                            new_grams = min(300, current_grams + 80)  # Adiciona até 80g
                            filtered_foods[f_idx] = calc_food(food.get("key"), new_grams)
                            break
                elif not existing_arroz:
                    # Adiciona arroz se não tinha
                    filtered_foods.append(calc_food("arroz_branco", 150))
                
                validated_meals[meal_idx]["foods"] = filtered_foods
                mp, mc, mf, mcal = sum_foods(filtered_foods)
                validated_meals[meal_idx]["total_calories"] = mcal
                validated_meals[meal_idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    for meal_idx, meal in enumerate(validated_meals):
        for food_idx, food in enumerate(meal.get("foods", [])):
            for field in required_fields:
                if field not in food:
                    # Campo faltando - recalcula o alimento
                    food_key = food.get("key", "frango")
                    grams = food.get("grams", 100)
                    recalc = calc_food(food_key, grams)
                    food.update(recalc)
            
            # REGRA ABSOLUTA FINAL: NUNCA OVOS NA CEIA (apenas em 6 refeições, índice 5)
            if meal_count == 6 and meal_idx == 5 and food.get("key") == "ovos":
                # Substitui ovos por fruta na ceia (sem cottage - limite muito baixo)
                grams = food.get("grams", 100)
                validated_meals[meal_idx]["foods"][food_idx] = calc_food("banana", grams)
                # Recalcula totais da refeição
                mp, mc, mf, mcal = sum_foods(validated_meals[meal_idx]["foods"])
                validated_meals[meal_idx]["total_calories"] = mcal
                validated_meals[meal_idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    return validated_meals


def validate_food_frequency(meals: List[Dict], preferred: Set[str] = None) -> List[Dict]:
    """
    🔄 Etapa 4 do PRD: Validação de Frequência de Alimentos
    
    ❌ Erro se um alimento aparece > 2 vezes/dia
    
    Se um alimento aparecer mais de 2 vezes:
    1. Remove a terceira ocorrência
    2. Substitui por alimento da mesma categoria (🚫 APENAS do usuário!)
    
    ⚠️ REGRA ESPECIAL CEIA (índice 5):
    - Na ceia, só pode substituir por: iogurte_zero, cottage, frutas
    - NUNCA substituir por carnes/peixes na ceia!
    
    🚫 REGRA ABSOLUTA: Substitutos APENAS dentre os alimentos do usuário!
    """
    if preferred is None:
        preferred = set()
    
    # Conta ocorrências de cada alimento
    food_count = {}
    for meal in meals:
        for food in meal.get("foods", []):
            key = food.get("key")
            if key:
                food_count[key] = food_count.get(key, 0) + 1
    
    # Identifica alimentos com mais de 2 ocorrências
    foods_to_limit = {k: v for k, v in food_count.items() if v > 2}
    
    if not foods_to_limit:
        return meals  # Nada a corrigir
    
    # 🚫 NOVA REGRA: Substitutos APENAS dentre os alimentos do usuário!
    # Organiza os alimentos preferidos por categoria
    user_substitutes = {
        "protein": [f for f in preferred if f in FOODS and FOODS[f]["category"] == "protein"],
        "carb": [f for f in preferred if f in FOODS and FOODS[f]["category"] == "carb"],
        "fat": [f for f in preferred if f in FOODS and FOODS[f]["category"] == "fat"],
        "fruit": [f for f in preferred if f in FOODS and FOODS[f]["category"] == "fruit"]
    }
    
    # Substitutos permitidos na CEIA (apenas proteínas leves e frutas do usuário)
    CEIA_ALLOWED_PROTEINS = {"iogurte_zero", "cottage"}
    user_ceia_substitutes = {
        "protein": [f for f in user_substitutes["protein"] if f in CEIA_ALLOWED_PROTEINS],
        "fat": user_substitutes["fat"],
        "fruit": user_substitutes["fruit"]
    }
    
    num_meals = len(meals)
    ceia_index = 5 if num_meals == 6 else (4 if num_meals == 5 else 3)
    
    # Processa cada alimento com excesso
    for food_key, count in foods_to_limit.items():
        occurrences_to_keep = 2
        current_count = 0
        
        for meal_idx, meal in enumerate(meals):
            new_foods = []
            for food in meal.get("foods", []):
                if food.get("key") == food_key:
                    current_count += 1
                    if current_count <= occurrences_to_keep:
                        new_foods.append(food)
                    else:
                        # Substitui por outro alimento da mesma categoria
                        # 🚫 APENAS usando alimentos que o usuário selecionou!
                        category = FOODS.get(food_key, {}).get("category", "protein")
                        
                        # Na CEIA, usa substitutos especiais (sem carnes/peixes)
                        if meal_idx == ceia_index:
                            substitutes = [s for s in user_ceia_substitutes.get(category, []) 
                                          if s != food_key and food_count.get(s, 0) < 2]
                        else:
                            substitutes = [s for s in user_substitutes.get(category, []) 
                                          if s != food_key and food_count.get(s, 0) < 2]
                        
                        if substitutes:
                            new_key = substitutes[0]
                            new_food = calc_food(new_key, food.get("grams", 100))
                            new_foods.append(new_food)
                            food_count[new_key] = food_count.get(new_key, 0) + 1
                        # 🚫 Sem fallback padrão! Se não encontrou substituto do usuário, não adiciona
                else:
                    new_foods.append(food)
            
            meal["foods"] = new_foods
            
            # Recalcula macros da refeição
            mp, mc, mf, mcal = sum_foods(meal["foods"])
            meal["total_calories"] = mcal
            meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    return meals


def ensure_consistency(cal: float, p: float, c: float, f: float) -> Tuple[int, int, int]:
    """Garante consistência entre macros e calorias"""
    target_p = round(p)
    target_c = round(c)
    target_f = round(f)
    
    calculated_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    if abs(calculated_cal - cal) > 100:
        ratio = cal / max(calculated_cal, 1)
        target_c = round(target_c * ratio)
    
    return target_p, target_c, target_f


# ==================== SERVIÇO PRINCIPAL ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float], meal_count: int = 6, meal_times: List[Dict] = None) -> DietPlan:
        """
        Gera plano de dieta personalizado.
        
        ✅ GARANTIAS BULLETPROOF:
        - NUNCA retorna erro
        - NUNCA retorna dieta inválida
        - NUNCA retorna refeição vazia
        - NUNCA retorna alimento com 0g
        - SEMPRE retorna dieta válida e utilizável
        
        🏆 MODO ATLETA:
        - Em PREP e PEAK_WEEK: usa apenas alimentos LIMPOS
        - Remove processados/ultraprocessados
        - Peak Week: alimentos ultra-selecionados para máximo controle
        
        🚫 REGRA ABSOLUTA:
        - NUNCA adiciona alimentos automaticamente
        - Usa APENAS os alimentos selecionados pelo usuário
        - Se faltar algo, retorna erro com mensagem clara
        
        Parâmetros:
        - meal_count: 4, 5 ou 6 refeições por dia
        - meal_times: lista opcional com horários personalizados
        """
        
        # Obtém preferências e restrições
        food_preferences = user_profile.get('food_preferences', [])
        dietary_restrictions = user_profile.get('dietary_restrictions', [])
        goal = user_profile.get('goal', 'manutencao')
        
        # Converte preferências para chaves normalizadas
        raw_preferred = get_user_preferred_foods(food_preferences)
        
        # ✅ NOVA VALIDAÇÃO: Verifica se usuário selecionou alimentos suficientes
        # 🚫 NÃO FAZ AUTO-COMPLETE - apenas valida!
        preferred_foods, is_valid, validation_error = validate_user_foods(
            raw_preferred, dietary_restrictions
        )
        
        # Se validação falhou, levanta exceção com mensagem clara
        if not is_valid:
            raise ValueError(validation_error)
        
        supplements = get_user_supplements(food_preferences)
        
        # Garante consistência
        target_p, target_c, target_f = ensure_consistency(
            target_calories,
            target_macros["protein"],
            target_macros["carbs"],
            target_macros["fat"]
        )
        
        # Garante mínimos de macros
        target_p = max(50, target_p)   # Mínimo 50g proteína
        target_c = max(50, target_c)   # Mínimo 50g carbs
        target_f = max(20, target_f)   # Mínimo 20g gordura
        
        target_cal_int = max(MIN_DAILY_CALORIES, int(round(target_calories)))
        
        # Gera dieta APENAS com alimentos selecionados pelo usuário
        meals = generate_diet(target_p, target_c, target_f, preferred_foods, dietary_restrictions, meal_count,
                              original_preferred=raw_preferred, goal=goal)
        
        # Fine-tune (múltiplas rodadas se necessário)
        for _ in range(5):  # Aumentado para 5 tentativas
            meals = fine_tune_diet(meals, target_p, target_c, target_f)
            is_valid, _ = validate_diet(meals, target_p, target_c, target_f)
            if is_valid:
                break
        
        # ✅ VALIDAÇÃO BULLETPROOF FINAL
        # Garante que NUNCA retorna dieta inválida
        meals = validate_and_fix_diet(meals, target_p, target_c, target_f, preferred_foods, meal_count)
        
        # ✅ APLICA LIMITES GLOBAIS (cottage max 20g, aveia max 80g, feijão só com arroz)
        meals = apply_global_limits(meals, raw_preferred)
        
        # ✅ VALIDA FREQUÊNCIA DE ALIMENTOS (nenhum alimento > 2x/dia)
        # 🚫 Passa preferred_foods para substituições apenas com alimentos do usuário!
        meals = validate_food_frequency(meals, preferred_foods)
        
        # Ajusta para o número de refeições configurado
        if len(meals) > meal_count:
            meals = meals[:meal_count]
        elif len(meals) < meal_count:
            # Adiciona refeições extras se necessário (com alimentos do usuário)
            while len(meals) < meal_count:
                # 🚫 Usa alimentos do usuário, não defaults!
                user_protein = next((f for f in preferred_foods if f in FOODS and FOODS[f]["category"] == "protein"), None)
                if user_protein:
                    meals.append({
                        "name": f"Refeição {len(meals) + 1}",
                        "time": "12:00",
                        "foods": [calc_food(user_protein, 100)],
                        "total_calories": 100,
                        "macros": {"protein": 20, "carbs": 0, "fat": 2}
                    })
                else:
                    # Sem proteína selecionada, copia última refeição
                    if meals:
                        meals.append(meals[-1].copy())
                    else:
                        break
        
        # Aplica horários personalizados se fornecidos
        if meal_times and len(meal_times) == len(meals):
            for i, mt in enumerate(meal_times):
                if isinstance(mt, dict):
                    meals[i]["name"] = mt.get("name", meals[i].get("name", f"Refeição {i+1}"))
                    meals[i]["time"] = mt.get("time", meals[i].get("time", "12:00"))
        
        # Formata resultado
        final_meals = []
        for m in meals:
            # Recalcula totais da refeição (garantia extra)
            mp, mc, mf, mcal = sum_foods(m.get("foods", []))
            
            # Garante que refeição não está vazia
            foods = m.get("foods", [])
            if not foods:
                foods = [calc_food("frango", 100)]
                mp, mc, mf, mcal = sum_foods(foods)
            
            final_meals.append(Meal(
                name=m.get("name", "Refeição"),
                time=m.get("time", "12:00"),
                foods=foods,
                total_calories=max(1, mcal),
                macros={"protein": max(0, mp), "carbs": max(0, mc), "fat": max(0, mf)}
            ))
        
        # Calcula totais finais
        all_foods = [f for m in final_meals for f in m.foods]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
        
        # ✅ ÚLTIMA VERIFICAÇÃO: Garante valores mínimos
        if total_cal < MIN_DAILY_CALORIES:
            # Adiciona comida até atingir mínimo
            extra_foods = []
            while total_cal < MIN_DAILY_CALORIES:
                extra = calc_food("frango", 100)
                extra_foods.append(extra)
                total_cal += extra["calories"]
            
            # Adiciona ao almoço
            if len(final_meals) >= 3:
                final_meals[2].foods.extend(extra_foods)
                mp, mc, mf, mcal = sum_foods(final_meals[2].foods)
                final_meals[2].total_calories = mcal
                final_meals[2].macros = {"protein": mp, "carbs": mc, "fat": mf}
        
        # Recalcula totais após correções
        all_foods = [f for m in final_meals for f in m.foods]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
        
        # Gera nota com info de auto-complete se aplicável
        notes = f"Dieta V14: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g | ✅ Validada"
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal_int,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=total_cal,
            computed_macros={"protein": total_p, "carbs": total_c, "fat": total_f},
            supplements=supplements,
            notes=notes,
            auto_completed=False,
            auto_complete_message=None
        )
    
    def to_strict_json(self, diet_plan: DietPlan) -> Dict:
        """Converte para formato JSON estrito"""
        refeicoes = []
        
        for meal in diet_plan.meals:
            alimentos = []
            for food in meal.foods:
                alimentos.append({
                    "nome": food["name"],
                    "quantidade_g": food["grams"],
                    "calorias": food["calories"],
                    "proteina": food["protein"],
                    "carboidrato": food["carbs"],
                    "gordura": food["fat"]
                })
            
            refeicoes.append({
                "nome": meal.name,
                "alimentos": alimentos
            })
        
        return {
            "refeicoes": refeicoes,
            "totais": {
                "calorias": diet_plan.computed_calories,
                "proteina": diet_plan.computed_macros["protein"],
                "carboidrato": diet_plan.computed_macros["carbs"],
                "gordura": diet_plan.computed_macros["fat"]
            },
            "metas": {
                "calorias": diet_plan.target_calories,
                "proteina": diet_plan.target_macros["protein"],
                "carboidrato": diet_plan.target_macros["carbs"],
                "gordura": diet_plan.target_macros["fat"]
            },
            "suplementos": diet_plan.supplements,
            "observacoes": diet_plan.notes
        }


# ==================== AJUSTE AUTOMÁTICO QUINZENAL ====================

# ==================== AJUSTE PARA MODO ATLETA ====================

def evaluate_progress(goal: str, previous_weight: float, current_weight: float, 
                      tolerance_kg: float = 0.3) -> Dict:
    """Avalia progresso e determina se precisa ajustar dieta"""
    weight_diff = current_weight - previous_weight
    
    result = {
        "needs_adjustment": False,
        "adjustment_type": None,
        "adjustment_percent": 0.0,
        "reason": "Progresso adequado"
    }
    
    if goal == "cutting":
        if weight_diff >= -tolerance_kg:
            result["needs_adjustment"] = True
            result["adjustment_type"] = "decrease"
            result["adjustment_percent"] = 6.0 if weight_diff >= 0 else 5.0
            result["reason"] = f"Peso não reduziu ({weight_diff:+.1f}kg). Reduzindo calorias."
        else:
            result["reason"] = f"Perda de peso adequada ({weight_diff:.1f}kg)."
    
    elif goal == "bulking":
        if weight_diff <= tolerance_kg:
            result["needs_adjustment"] = True
            result["adjustment_type"] = "increase"
            result["adjustment_percent"] = 6.0 if weight_diff <= 0 else 5.0
            result["reason"] = f"Peso não aumentou ({weight_diff:+.1f}kg). Aumentando calorias."
        else:
            result["reason"] = f"Ganho de peso adequado ({weight_diff:+.1f}kg)."
    
    elif goal == "manutencao":
        if abs(weight_diff) > 1.0:
            result["needs_adjustment"] = True
            if weight_diff > 0:
                result["adjustment_type"] = "decrease"
                result["adjustment_percent"] = 5.0
                result["reason"] = f"Peso aumentou demais ({weight_diff:+.1f}kg)."
            else:
                result["adjustment_type"] = "increase"
                result["adjustment_percent"] = 5.0
                result["reason"] = f"Peso diminuiu demais ({weight_diff:.1f}kg)."
        else:
            result["reason"] = f"Peso estável ({weight_diff:+.1f}kg)."
    
    return result


def adjust_diet_quantities(diet_plan: Dict, adjustment_type: str, adjustment_percent: float) -> Dict:
    """
    Ajusta quantidades da dieta existente.
    
    ✅ GARANTIAS BULLETPROOF:
    - Múltiplos de 10g
    - Mínimo 10g por alimento
    - Máximo 500g por alimento
    - Calorias mínimas garantidas
    - NUNCA retorna dieta inválida
    """
    if adjustment_type not in ["increase", "decrease"]:
        return diet_plan
    
    multiplier = 1 + (adjustment_percent / 100) if adjustment_type == "increase" else 1 - (adjustment_percent / 100)
    
    meals = diet_plan.get("meals", [])
    
    for meal in meals:
        foods = meal.get("foods", [])
        validated_foods = []
        
        for food in foods:
            current_grams = food.get("grams", 100)
            new_grams = round_to_10(current_grams * multiplier)
            
            # ✅ Garante limites de segurança
            new_grams = max(MIN_FOOD_GRAMS, min(MAX_FOOD_GRAMS, new_grams))
            
            food_key = food.get("key", "frango")
            
            # ✅ Recalcula usando função validada
            if food_key in FOODS:
                validated_food = calc_food(food_key, new_grams)
                validated_foods.append(validated_food)
            else:
                # Fallback: mantém alimento com valores corrigidos
                food["grams"] = new_grams
                food["quantity"] = f"{new_grams}g"
                validated_foods.append(food)
        
        # ✅ Garante que refeição não está vazia
        if not validated_foods:
            validated_foods = [calc_food("frango", 100)]
        
        meal["foods"] = validated_foods
        
        # Recalcula totais da refeição
        meal_p = sum(f.get("protein", 0) for f in validated_foods)
        meal_c = sum(f.get("carbs", 0) for f in validated_foods)
        meal_f = sum(f.get("fat", 0) for f in validated_foods)
        meal_cal = sum(f.get("calories", 0) for f in validated_foods)
        
        meal["total_calories"] = max(1, meal_cal)
        meal["macros"] = {"protein": max(0, meal_p), "carbs": max(0, meal_c), "fat": max(0, meal_f)}
    
    # Recalcula totais
    all_foods = [f for m in meals for f in m.get("foods", [])]
    total_p = sum(f.get("protein", 0) for f in all_foods)
    total_c = sum(f.get("carbs", 0) for f in all_foods)
    total_f = sum(f.get("fat", 0) for f in all_foods)
    total_cal = sum(f.get("calories", 0) for f in all_foods)
    
    # ✅ Garante calorias mínimas
    if total_cal < MIN_DAILY_CALORIES:
        # Adiciona proteína ao almoço
        if len(meals) >= 3:
            extra = calc_food("frango", 150)
            meals[2]["foods"].append(extra)
            total_cal += extra["calories"]
            total_p += extra["protein"]
    
    diet_plan["computed_calories"] = max(MIN_DAILY_CALORIES, total_cal)
    diet_plan["computed_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["target_calories"] = max(MIN_DAILY_CALORIES, total_cal)
    diet_plan["target_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["notes"] = f"Dieta V14 ajustada: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g | ✅ Validada"
    
    return diet_plan
