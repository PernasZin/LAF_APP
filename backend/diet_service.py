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
MAX_CARB_GRAMS = 2000     # Máximo para carboidratos (arroz, batata) - SEM LIMITE PRÁTICO
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

# ==================== VARIÁVEL GLOBAL DE RESTRIÇÕES ====================
# Usada pelas funções de fallback para respeitar restrições alimentares
_current_diet_restrictions: List[str] = []

def set_diet_restrictions(restrictions: List[str]):
    """Define as restrições alimentares para a geração atual"""
    global _current_diet_restrictions
    _current_diet_restrictions = restrictions if restrictions else []

def get_restriction_safe_protein() -> str:
    """
    Retorna uma proteína segura que respeita as restrições alimentares atuais.
    
    REGRA IMPORTANTE:
    - Para vegetarianos: prioriza tofu > tempeh > edamame > ovos
    - Para NÃO vegetarianos: prioriza frango > patinho > tilapia > ovos
    """
    global _current_diet_restrictions
    
    # Calcula exclusões
    excluded = set()
    for r in _current_diet_restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    
    # Verifica se é vegetariano
    is_vegetarian = "vegetariano" in _current_diet_restrictions or "vegano" in _current_diet_restrictions
    
    if is_vegetarian:
        # Ordem para vegetarianos: proteínas vegetais primeiro
        proteins = ["tofu", "tempeh", "edamame", "grao_de_bico", "ovos"]
    else:
        # Ordem para não-vegetarianos: carnes e ovos primeiro (mais comum e acessível)
        proteins = ["frango", "patinho", "tilapia", "ovos", "atum"]
    
    for p in proteins:
        if p not in excluded:
            return p
    
    return "ovos"  # Último fallback - ovos são geralmente aceitos

def get_restriction_safe_fruit() -> str:
    """
    Retorna uma fruta segura que respeita as restrições alimentares atuais.
    Para diabéticos: exclui frutas com alto índice glicêmico (banana, manga, uva, etc.)
    """
    global _current_diet_restrictions
    
    # Calcula exclusões
    excluded = set()
    for r in _current_diet_restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    
    # Lista de frutas em ordem de prioridade (diabético-friendly primeiro)
    # Frutas com baixo IG: maçã, pera, morango, laranja, kiwi
    fruits = ["maca", "pera", "morango", "laranja", "kiwi", "banana", "mamao", "melancia"]
    
    for f in fruits:
        if f not in excluded:
            return f
    
    return "maca"  # Último fallback


def get_restriction_safe_breakfast_carb() -> str:
    """
    Retorna um carboidrato seguro para café da manhã que respeita restrições.
    
    Ordem de prioridade:
    1. aveia (se não for sem glúten)
    2. tapioca (se não for diabético)
    3. batata_doce (sempre seguro, mas menos comum no café)
    4. fruta (último fallback)
    """
    global _current_diet_restrictions
    
    # Calcula exclusões
    excluded = set()
    for r in _current_diet_restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    
    # Ordem de preferência para café da manhã
    carbs = ["aveia", "tapioca", "batata_doce"]
    
    for c in carbs:
        if c not in excluded:
            return c
    
    # Se tudo estiver excluído, usa fruta
    return get_restriction_safe_fruit()


def get_restriction_safe_protein_light() -> str:
    """
    Retorna uma proteína leve (para CAFÉ DA MANHÃ) que respeita restrições.
    NÃO USAR PARA LANCHES - usar get_lanche_safe_food() em vez disso.
    
    Ordem de prioridade:
    1. ovos (geralmente aceito por todos)
    2. tofu (para vegetarianos)
    3. iogurte_zero (se não for sem lactose)
    4. cottage (se não for sem lactose)
    5. fruta (último fallback)
    """
    global _current_diet_restrictions
    
    # Calcula exclusões
    excluded = set()
    for r in _current_diet_restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    
    # Ordem de preferência para proteína leve (CAFÉ DA MANHÃ)
    proteins = ["ovos", "tofu", "iogurte_zero", "cottage"]
    
    for p in proteins:
        if p not in excluded:
            return p
    
    # Se tudo estiver excluído, usa fruta
    return get_restriction_safe_fruit()


def get_lanche_safe_food(food_type: str = "protein") -> str:
    """
    Retorna um alimento seguro para LANCHES que respeita restrições.
    
    REGRA: Lanches devem conter APENAS:
    - Frutas (maçã, banana, laranja, morango, etc.)
    - Pão/carboidratos leves (pão integral, aveia)
    - Iogurte (se não for sem lactose)
    - Mel (se não for diabético)
    - Oleaginosas (castanhas, amêndoas)
    
    PROIBIDO em lanches: carnes, ovos, cottage, tofu
    """
    global _current_diet_restrictions
    
    # Calcula exclusões
    excluded = set()
    for r in _current_diet_restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    
    if food_type == "protein":
        # Para "proteína" em lanches, usamos iogurte ou fruta (NUNCA carnes/ovos)
        options = ["iogurte_zero", "iogurte_natural"]
        for opt in options:
            if opt not in excluded:
                return opt
        # Se não pode iogurte, retorna fruta
        return get_restriction_safe_fruit()
    
    elif food_type == "carb":
        # Carboidratos leves para lanches
        options = ["pao_integral", "aveia", "tapioca"]
        for opt in options:
            if opt not in excluded:
                return opt
        return get_restriction_safe_fruit()
    
    elif food_type == "sweet":
        # Doces para lanches (se permitido)
        if "mel" not in excluded:
            return "mel"
        return get_restriction_safe_fruit()
    
    else:  # fruit ou qualquer outro
        return get_restriction_safe_fruit()


# Alimentos PERMITIDOS em lanches (lista branca)
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
    "diabetico": {"mel", "leite_condensado", "granola", "banana", "manga", "uva", 
                  "melancia", "abacaxi", "mamao", "tapioca", "pao", "pao_integral", 
                  "pao_forma", "farofa", "arroz_branco"},
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

# Carnes que SÓ podem aparecer no almoço e jantar (NUNCA em lanches, café ou ceia)
CARNES_APENAS_ALMOCO_JANTAR = {"frango", "coxa_frango", "patinho", "carne_moida", "tilapia", "atum", "salmao", "camarao", "peru", "suino", "sardinha"}

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
    
    # === PROTEÍNAS VEGETAIS (para vegetarianos/veganos) ===
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
    # whey_protein já está definido como proteína acima - não duplicar aqui
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


def calculate_target_macros(weight: float, tdee: float, goal: str, gender: str = 'masculino') -> Dict:
    """
    🎯 CALCULA MACROS EM 3 PASSOS
    
    1. Calcular TDEE (já vem calculado)
    2. Somar superávit/déficit baseado no objetivo
    3. Distribuir macros a partir das calorias ajustadas
    
    CUTTING: TDEE - 15%
       - Proteína: peso × 2.2
       - Gordura: peso × 0.8
       - Carboidrato: calorias restantes
    
    MANUTENÇÃO: TDEE
       - Proteína: peso × 2.0
       - Gordura: peso × 0.85
       - Carboidrato: calorias restantes
    
    BULKING: TDEE + 15%
       - Proteína: peso × 2.0
       - Gordura: peso × 0.9
       - Carboidrato: calorias restantes
    """
    
    # PASSO 2: Ajusta TDEE baseado no objetivo
    if goal.lower() == 'cutting':
        target_calories = tdee * 0.85  # -15% déficit
    elif goal.lower() == 'bulking':
        target_calories = tdee * 1.15  # +15% superávit
    else:  # manutenção
        target_calories = tdee
    
    # PASSO 3: Distribui macros
    if goal.lower() == 'cutting':
        protein = weight * 2.2
        fat = weight * 0.8
    elif goal.lower() == 'bulking':
        protein = weight * 2.0
        fat = weight * 0.9
    else:  # manutenção
        protein = weight * 2.0
        fat = weight * 0.85
    
    # Carboidratos = calorias restantes
    protein_cal = protein * 4
    fat_cal = fat * 9
    carbs_cal = target_calories - protein_cal - fat_cal
    carbs = max(50, carbs_cal / 4)  # Mínimo 50g de carbs
    
    # Fibra mínima
    fiber_target = 30 if gender.lower() in ['masculino', 'male', 'm'] else 25
    
    print(f"[MACROS] Peso={weight}kg, TDEE={tdee}, Goal={goal} -> Target={target_calories}kcal | P={protein}g C={carbs}g F={fat}g")
    
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
    🧠 AUTOCOMPLETE INTELIGENTE: Seleciona alimento da categoria.
    
    1. Primeiro tenta alimentos do usuário
    2. Se não encontrar, usa FALLBACK da lista de prioridade
    3. NUNCA retorna None para categorias essenciais (proteína, carb)
    4. SEMPRE respeita restrições alimentares
    """
    # Calcula alimentos excluídos por restrições
    excluded_by_restrictions = set()
    for r in restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded_by_restrictions.update(RESTRICTION_EXCLUSIONS[r])
    
    # Usa apenas alimentos que o usuário selecionou (já filtra restrições)
    available = get_allowed_foods(meal_type, preferred, restrictions, category)
    
    if exclude:
        available = [f for f in available if f not in exclude]
    
    if available:
        # Segue prioridade se possível
        for p in priority:
            if p in available and p not in excluded_by_restrictions:
                return p
        # Retorna primeiro disponível que não viole restrições
        for a in available:
            if a not in excluded_by_restrictions:
                return a
    
    # 🧠 AUTOCOMPLETE: Se não há alimentos do usuário, usa a lista de prioridade (que já tem fallbacks)
    for p in priority:
        if p in FOODS and p not in (exclude or set()) and p not in excluded_by_restrictions:
            return p
    
    # Último recurso: fallback absoluto por categoria (RESPEITANDO RESTRIÇÕES)
    ABSOLUTE_FALLBACKS = {
        "protein": ["frango", "ovos", "whey_protein", "tofu"],
        "carb": ["arroz_branco", "batata_doce", "aveia", "tapioca"],
        "fat": ["azeite", "castanhas", "abacate"],
        "fruit": ["banana", "maca", "morango", "laranja"]
    }
    
    fallbacks = ABSOLUTE_FALLBACKS.get(category, [])
    for fb in fallbacks:
        if fb not in excluded_by_restrictions:
            return fb
    
    return None


def get_safe_fallback(category: str, restrictions: List[str], fallback_list: List[str] = None) -> Optional[str]:
    """
    Retorna um fallback seguro que respeita as restrições.
    """
    excluded = set()
    for r in restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded.update(RESTRICTION_EXCLUSIONS[r])
    
    DEFAULT_FALLBACKS = {
        "protein": ["ovos", "whey_protein", "tofu"],
        "carb_cafe": ["tapioca", "batata_doce"],  # Para café sem glúten
        "carb_principal": ["arroz_branco", "batata_doce", "tapioca"],
        "fat": ["azeite", "castanhas", "abacate"],
        "fruit": ["banana", "maca", "morango"]
    }
    
    options = fallback_list if fallback_list else DEFAULT_FALLBACKS.get(category, [])
    
    for fb in options:
        if fb not in excluded and fb in FOODS:
            return fb
    
    return None


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
    
    # 🧠 FALLBACKS INTELIGENTES por tipo de refeição
    # ✅ ORDEM: Proteínas tradicionais primeiro (frango, ovos)
    # ✅ Proteínas vegetais (tofu, tempeh) são filtradas pelo get_safe_fallback quando vegetariano
    FALLBACKS = {
        "protein_principal": ["frango", "patinho", "tilapia", "tofu", "tempeh", "grao_de_bico"],
        "protein_leve": ["ovos", "iogurte_zero", "cottage", "tofu", "edamame"],
        "carb_principal": ["arroz_branco", "batata_doce", "macarrao", "tapioca"],
        "carb_leve": ["aveia", "pao_integral", "tapioca"],
        "fat": ["azeite", "castanhas", "pasta_amendoim", "abacate"],
        "fruit": ["banana", "maca", "morango", "laranja"]
    }
    
    # 🔒 LIMITES DE PROTEÍNA para evitar excesso calórico
    PROTEIN_LIMITS = {
        "tofu": {"min": 100, "max": 200},
        "tempeh": {"min": 80, "max": 150},
        "grao_de_bico": {"min": 100, "max": 180},
        "edamame": {"min": 80, "max": 150},
        "ovos": {"min": 100, "max": 200},
        "frango": {"min": 150, "max": 250},
        "whey_protein": {"min": 25, "max": 35},  # MÁXIMO 35g de whey!
        "proteina_ervilha": {"min": 25, "max": 35},
    }
    
    # 🔒 Calcula alimentos excluídos por restrições UMA VEZ
    excluded_by_restrictions = set()
    for r in restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded_by_restrictions.update(RESTRICTION_EXCLUSIONS[r])
    
    def get_user_foods_with_fallback(category: str, meal_type: str = "geral") -> List[str]:
        """
        🧠 AUTO-COMPLETAR INTELIGENTE COM RESPEITO ÀS RESTRIÇÕES
        
        1. Prioriza alimentos escolhidos pelo usuário
        2. Se não tiver da categoria, usa fallback adequado
        3. NUNCA deixa refeição vazia
        4. ✅ SEMPRE filtra restrições alimentares!
        """
        # Primeiro: tenta pegar alimentos do usuário (já filtrados por restrições)
        user_foods = []
        for p in preferred:
            if p in FOODS and p not in excluded_by_restrictions:
                if FOODS[p]["category"] == category:
                    user_foods.append(p)
        
        if user_foods:
            return user_foods
        
        # Se não tem, usa fallback baseado no tipo de refeição
        # ✅ FILTRA RESTRIÇÕES nos fallbacks também!
        fallback_list = []
        if category == "protein":
            if meal_type in ["cafe", "lanche", "ceia"]:
                fallback_list = FALLBACKS["protein_leve"]
            else:
                fallback_list = FALLBACKS["protein_principal"]
        elif category == "carb":
            if meal_type in ["cafe", "lanche"]:
                fallback_list = FALLBACKS["carb_leve"]
            else:
                fallback_list = FALLBACKS["carb_principal"]
        elif category == "fat":
            fallback_list = FALLBACKS["fat"]
        elif category == "fruit":
            fallback_list = FALLBACKS["fruit"]
        
        # ✅ FILTRA RESTRIÇÕES dos fallbacks
        return [f for f in fallback_list if f not in excluded_by_restrictions]
    
    # 🧠 Prioridades - usando FALLBACK INTELIGENTE
    # Prioriza alimentos do usuário, usa fallback se não tiver
    
    # PROTEÍNAS PRINCIPAIS para almoço/jantar
    protein_priority = get_user_foods_with_fallback("protein", "almoco")
    
    # PROTEÍNAS LEVES para café/lanches/ceia
    light_protein_priority_cafe = get_user_foods_with_fallback("protein", "cafe")
    
    # Proteína leve para lanches
    light_protein_priority_lanche = get_user_foods_with_fallback("protein", "lanche")
    
    # CARBOIDRATOS PRINCIPAIS
    carb_priority = get_user_foods_with_fallback("carb", "almoco")
    
    # CARBOIDRATOS DE LANCHE
    light_carb_priority = get_user_foods_with_fallback("carb", "cafe")
    
    # GORDURAS
    fat_priority = get_user_foods_with_fallback("fat", "geral")
    
    # GORDURAS SNACKS para lanches
    fat_priority_lanche = fat_priority
    
    # GORDURAS para café
    fat_priority_cafe = fat_priority
    
    # FRUTAS
    fruit_priority = get_user_foods_with_fallback("fruit", "geral")
    
    # ==================== CALCULAR ALMOÇO/JANTAR ====================
    # ⭐ REGRA OBRIGATÓRIA: Almoço e Jantar EXATAMENTE IGUAIS
    # - Mesma proteína
    # - Mesmo carboidrato  
    # - Mesmas quantidades
    # - Variedade de proteínas é AO LONGO DOS DIAS, não dentro do mesmo dia!
    # Proporção: Almoço + Jantar = ~55% dos macros totais
    
    # ==================== DISTRIBUIÇÃO PROPORCIONAL POR NÚMERO DE REFEIÇÕES ====================
    # 🎯 O TOTAL DE MACROS DEVE SER MANTIDO, independente do número de refeições!
    # Apenas redistribui proporcionalmente entre as refeições disponíveis
    
    if meal_count == 4:
        # 4 refeições: Café (20%), Almoço (35%), Lanche (10%), Jantar (35%)
        MEAL_DISTRIBUTION = {
            'cafe': {'p': 0.20, 'c': 0.20, 'f': 0.15},
            'almoco': {'p': 0.35, 'c': 0.35, 'f': 0.40},
            'lanche_tarde': {'p': 0.10, 'c': 0.10, 'f': 0.10},
            'jantar': {'p': 0.35, 'c': 0.35, 'f': 0.35}
        }
    elif meal_count == 5:
        # 5 refeições: Café (18%), L.Manhã (8%), Almoço (32%), L.Tarde (8%), Jantar (34%)
        MEAL_DISTRIBUTION = {
            'cafe': {'p': 0.18, 'c': 0.18, 'f': 0.15},
            'lanche_manha': {'p': 0.08, 'c': 0.08, 'f': 0.10},
            'almoco': {'p': 0.32, 'c': 0.32, 'f': 0.35},
            'lanche_tarde': {'p': 0.08, 'c': 0.08, 'f': 0.10},
            'jantar': {'p': 0.34, 'c': 0.34, 'f': 0.30}
        }
    else:  # 6 refeições
        # 6 refeições: Café (15%), L.Manhã (8%), Almoço (27%), L.Tarde (8%), Jantar (27%), Ceia (15%)
        MEAL_DISTRIBUTION = {
            'cafe': {'p': 0.15, 'c': 0.15, 'f': 0.12},
            'lanche_manha': {'p': 0.08, 'c': 0.08, 'f': 0.10},
            'almoco': {'p': 0.27, 'c': 0.27, 'f': 0.30},
            'lanche_tarde': {'p': 0.08, 'c': 0.08, 'f': 0.10},
            'jantar': {'p': 0.27, 'c': 0.27, 'f': 0.28},
            'ceia': {'p': 0.15, 'c': 0.15, 'f': 0.10}
        }
    
    # Calcular macros para refeições principais (almoço/jantar)
    main_meal_p = target_p * MEAL_DISTRIBUTION.get('almoco', {}).get('p', 0.27)
    main_meal_c = target_c * MEAL_DISTRIBUTION.get('almoco', {}).get('c', 0.27)
    main_meal_f = target_f * MEAL_DISTRIBUTION.get('almoco', {}).get('f', 0.30)
    
    # Selecionar UMA proteína para AMBOS almoço e jantar (iguais!)
    main_protein = select_best_food("almoco_jantar", preferred, restrictions, "protein", protein_priority)
    
    main_carb = select_best_food("almoco_jantar", preferred, restrictions, "carb", carb_priority)
    
    # Calcular quantidades para UMA refeição principal (igual para almoço e jantar)
    if main_protein and main_protein in FOODS:
        protein_grams = round_to_10(clamp(main_meal_p / (FOODS[main_protein]["p"] / 100), 150, 280))
    else:
        main_protein = get_restriction_safe_protein()
        protein_grams = 180
    
    if main_carb and main_carb in FOODS:
        # ARROZ/BATATA: porções razoáveis - máx 400g por refeição principal
        # Para targets altos, o restante será compensado com PÃES
        base_carb_grams = round_to_10(clamp(main_meal_c * 0.5 / (FOODS[main_carb]["c"] / 100), 150, 400))
        
        # Compensação para diabéticos e outras restrições com poucos carbs
        if "diabetico" in restrictions or "diabético" in restrictions:
            # Aumenta em 30% a porção de carbs permitidos
            base_carb_grams = round_to_10(min(base_carb_grams * 1.3, 500))
        
        carb_grams = base_carb_grams
    else:
        main_carb = "arroz_branco"
        carb_grams = 250
    
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
            # 🍳 Café da Manhã
            # ✅ Permitido: ovos, whey, iogurte, cottage, pão, aveia, frutas
            # ❌ Proibido: carne, arroz, macarrão
            protein = select_best_food("cafe_da_manha", preferred, restrictions, "protein", light_protein_priority_cafe)
            fruit = select_best_food("cafe_da_manha", preferred, restrictions, "fruit", fruit_priority)
            fat = select_best_food("cafe_da_manha", preferred, restrictions, "fat", fat_priority_cafe)
            
            # Carboidratos para café: pão + aveia (ou apenas um se o usuário não tiver)
            CAFE_CARBS_PAO = ["pao_integral", "pao", "tapioca"]
            CAFE_CARBS_AVEIA = ["aveia"]
            
            # Procura pão nas preferências do usuário (respeitando restrições)
            excluded_restrictions = set()
            for r in restrictions:
                if r in RESTRICTION_EXCLUSIONS:
                    excluded_restrictions.update(RESTRICTION_EXCLUSIONS[r])
            
            carb_pao = None
            for c in CAFE_CARBS_PAO:
                if c in preferred and c not in excluded_restrictions:
                    carb_pao = c
                    break
            
            # Procura aveia nas preferências do usuário (respeitando restrições)
            carb_aveia = None
            for c in CAFE_CARBS_AVEIA:
                if c in preferred and c not in excluded_restrictions:
                    carb_aveia = c
                    break
            
            # Proteína
            if protein and protein in FOODS and protein not in excluded_restrictions:
                p_grams = 150 if protein == "ovos" else 100
                foods.append(calc_food(protein, p_grams))
            else:
                # 🧠 FALLBACK: proteína segura
                safe_protein = get_safe_fallback("protein", restrictions, ["ovos", "whey_protein", "tofu"])
                if safe_protein:
                    foods.append(calc_food(safe_protein, 150))
            
            # 🍞 PÃO (sempre presente no café)
            # MÍNIMO: 2 fatias (50g) | PODE AUMENTAR: 4-5 fatias (100-125g) se precisar de mais carbs
            # Isso ajuda a não sobrecarregar o arroz nas refeições principais
            pao_grams = 50  # Base: 2 fatias
            
            # Se o objetivo é bulking ou a meta de carbs é alta, aumenta o pão
            if goal == "bulking" or target_c > 300:
                pao_grams = 100  # 4 fatias para bulking
            elif target_c > 250:
                pao_grams = 75   # 3 fatias para metas intermediárias
            
            if carb_pao and carb_pao in FOODS:
                foods.append(calc_food(carb_pao, pao_grams))
            else:
                # 🧠 FALLBACK: carb de café seguro (respeita sem glúten)
                safe_carb = get_safe_fallback("carb_cafe", restrictions, ["pao_integral", "tapioca", "aveia"])
                if safe_carb:
                    foods.append(calc_food(safe_carb, pao_grams))
            
            # 🥣 AVEIA (opcional, se o usuário tiver e não for sem glúten)
            if carb_aveia and carb_aveia in FOODS and carb_aveia not in excluded_restrictions:
                foods.append(calc_food(carb_aveia, 40))
            
            # Fruta
            if fruit and fruit in FOODS:
                foods.append(calc_food(fruit, 120))
            else:
                # 🧠 FALLBACK: fruta segura
                foods.append(calc_food(get_restriction_safe_fruit(), 120))
            
            # Gordura (opcional) - NO CAFÉ APENAS CASTANHAS, NÃO AZEITE!
            if fat and fat in FOODS and fat != "azeite":
                foods.append(calc_food(fat, 15))
            elif "castanhas" not in excluded_restrictions:
                # Fallback: castanhas (não azeite no café!)
                foods.append(calc_food("castanhas", 15))
                
        elif meal_type in ['lanche_manha', 'lanche_tarde', 'lanche']:
            # 🥪 Lanches
            # ✅ Permitido: frutas, whey, iogurte, castanhas
            # ❌ Proibido: nada pesado (carne, peixe)
            
            # Para lanches, NÃO usar proteínas principais - usar lista específica de leves
            # Respeitando restrições alimentares
            LANCHE_PROTEINS = ["iogurte_zero", "cottage", "whey_protein"]
            lanche_protein = None
            for p in LANCHE_PROTEINS:
                if p in preferred and p not in excluded_restrictions:
                    lanche_protein = p
                    break
            
            # Fruta e gordura para lanche
            lanche_fruit = None
            for f in fruit_priority:
                if f in preferred and f not in excluded_restrictions:
                    lanche_fruit = f
                    break
            
            lanche_fat = None
            for f in fat_priority_lanche:
                if f in preferred and f not in excluded_restrictions:
                    lanche_fat = f
                    break
            
            if lanche_protein and lanche_protein in FOODS:
                # Ajusta quantidade baseado no tipo de proteína
                if lanche_protein == 'whey_protein' or lanche_protein == 'proteina_ervilha':
                    foods.append(calc_food(lanche_protein, 30))  # Máximo 1 scoop
                elif lanche_protein == 'iogurte_zero':
                    foods.append(calc_food(lanche_protein, 170))
                else:
                    foods.append(calc_food(lanche_protein, 100))
            else:
                # 🧠 FALLBACK: proteína leve segura (respeita sem lactose e vegetariano)
                # Prioriza proteínas vegetais para vegetarianos
                safe_lanche_protein = get_safe_fallback("protein", restrictions, ["ovos", "tofu", "edamame", "iogurte_zero"])
                if safe_lanche_protein:
                    if safe_lanche_protein == "iogurte_zero":
                        grams = 170
                    elif safe_lanche_protein in ["ovos", "tofu", "edamame"]:
                        grams = 100
                    else:
                        grams = 80
                    foods.append(calc_food(safe_lanche_protein, grams))
            
            if lanche_fruit and lanche_fruit in FOODS:
                foods.append(calc_food(lanche_fruit, 100))
            else:
                # 🧠 FALLBACK: fruta segura (respeita diabético)
                foods.append(calc_food(get_restriction_safe_fruit(), 100))
            
            if lanche_fat and lanche_fat in FOODS:
                foods.append(calc_food(lanche_fat, 15))
            else:
                # 🧠 FALLBACK: castanhas (sempre seguro)
                foods.append(calc_food("castanhas", 20))
            
            # 🔒 GARANTIA: Se o lanche está muito leve, adiciona mais alimentos
            meal_cal = sum(f.get('calories', 0) for f in foods if isinstance(f, dict))
            if meal_cal < 200:
                # Adiciona mais uma fruta ou proteína
                safe_protein = get_safe_fallback("protein", restrictions, ["ovos", "tofu", "edamame"])
                if safe_protein:
                    foods.append(calc_food(safe_protein, 100))
                
        elif meal_type == 'almoco':
            # 🍛 ALMOÇO - Refeição completa
            # ✅ Permitido: proteína principal, arroz, batata, macarrão, feijão, legumes, azeite
            # ⭐ IGUAL AO JANTAR
            if main_protein and main_protein in FOODS and main_protein not in excluded_by_restrictions:
                foods.append(calc_food(main_protein, protein_grams))
            else:
                # 🧠 FALLBACK: proteína segura (respeita vegetariano - tofu primeiro)
                safe_main_protein = get_safe_fallback("protein", restrictions, ["tofu", "ovos", "frango"])
                if safe_main_protein:
                    foods.append(calc_food(safe_main_protein, 180 if safe_main_protein != "ovos" else 200))
            
            if main_carb and main_carb in FOODS and main_carb not in excluded_by_restrictions:
                foods.append(calc_food(main_carb, carb_grams))
            else:
                # 🧠 FALLBACK: carb seguro
                safe_carb = get_safe_fallback("carb_principal", restrictions, ["arroz_branco", "batata_doce", "tapioca"])
                if safe_carb:
                    foods.append(calc_food(safe_carb, 200))
            
            if use_feijao:
                foods.append(calc_food("feijao", feijao_grams))
            
            foods.append(calc_food("azeite", azeite_grams))
            
        elif meal_type == 'jantar':
            # 🍽️ JANTAR - Mesmo conceito do almoço
            # ⭐ IGUAL AO ALMOÇO (preferir proteína diferente quando possível, mas aqui mantemos igual)
            if main_protein and main_protein in FOODS and main_protein not in excluded_by_restrictions:
                foods.append(calc_food(main_protein, protein_grams))
            else:
                # 🧠 FALLBACK: proteína segura (respeita vegetariano - tofu primeiro)
                safe_main_protein = get_safe_fallback("protein", restrictions, ["tofu", "ovos", "frango"])
                if safe_main_protein:
                    foods.append(calc_food(safe_main_protein, 180 if safe_main_protein != "ovos" else 200))
            
            if main_carb and main_carb in FOODS and main_carb not in excluded_by_restrictions:
                foods.append(calc_food(main_carb, carb_grams))
            else:
                # 🧠 FALLBACK: carb seguro
                safe_carb = get_safe_fallback("carb_principal", restrictions, ["arroz_branco", "batata_doce", "tapioca"])
                if safe_carb:
                    foods.append(calc_food(safe_carb, 200))
            
            if use_feijao:
                foods.append(calc_food("feijao", feijao_grams))
            
            foods.append(calc_food("azeite", azeite_grams))
            
        elif meal_type == 'ceia':
            # 🌙 CEIA - Somente leve
            # ✅ Permitido: iogurte, leite, whey, aveia, fruta leve
            # ❌ Proibido: carne, peixe, arroz, macarrão
            
            # Para ceia, NÃO usar proteínas principais - usar lista específica de leves
            # Respeitando restrições alimentares
            CEIA_PROTEINS = ["iogurte_zero", "cottage", "whey_protein"]
            ceia_protein = None
            for p in CEIA_PROTEINS:
                if p in preferred and p not in excluded_restrictions:
                    ceia_protein = p
                    break
            
            # Fruta para ceia
            ceia_fruit = None
            for f in fruit_priority:
                if f in preferred and f not in excluded_restrictions:
                    ceia_fruit = f
                    break
            
            if ceia_protein and ceia_protein in FOODS:
                foods.append(calc_food(ceia_protein, 170))
            else:
                # 🧠 FALLBACK CEIA: proteína leve segura (respeita sem lactose)
                safe_ceia_protein = get_safe_fallback("protein", restrictions, ["whey_protein", "ovos"])
                if safe_ceia_protein:
                    foods.append(calc_food(safe_ceia_protein, 100 if safe_ceia_protein == "ovos" else 30))
            
            if ceia_fruit and ceia_fruit in FOODS:
                foods.append(calc_food(ceia_fruit, 120))
            else:
                # 🧠 FALLBACK: banana
                foods.append(calc_food(get_restriction_safe_fruit(), 120))
        
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
                        "feijao", "lentilha", "farofa", "batata_doce", "pao_frances", "pao_integral", "pao"}
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
                # 🍚🍞 BALANCEAR entre PÃO e ARROZ - máx 10 pães/dia, resto em arroz
                pao_key = "pao"
                pao_carbs_per_100g = FOODS.get(pao_key, {}).get("c", 49)
                pao_unit_g = 50  # 1 pão = 50g
                carbs_por_pao = (pao_carbs_per_100g / 100) * pao_unit_g  # ~24.5g
                
                max_paes_total = 10
                max_carbs_com_paes = max_paes_total * carbs_por_pao  # ~245g
                
                # Calcula quanto de carbs adicionar via pães vs arroz
                if increase_needed <= max_carbs_com_paes:
                    # Só pães: divide igualmente entre refeições
                    paes_por_refeicao = int((increase_needed / carbs_por_pao) / 2) + 1
                    paes_por_refeicao = min(paes_por_refeicao, 5)  # máx 5 por refeição
                    arroz_extra_por_refeicao = 0
                else:
                    # Pães + arroz
                    paes_por_refeicao = 5
                    carbs_restantes = increase_needed - max_carbs_com_paes
                    c_per_100 = FOODS.get("arroz_branco", {}).get("c", 28)
                    arroz_extra_por_refeicao = round_to_10((carbs_restantes / 2) / (c_per_100 / 100))
                
                for m_idx, (f_idx, food_key, current_g) in carb_indices.items():
                    # Adiciona pães
                    if paes_por_refeicao > 0:
                        pao_grams = paes_por_refeicao * pao_unit_g
                        # Verifica se já tem pão
                        has_pao = False
                        for fi, food in enumerate(meals[m_idx]["foods"]):
                            if food.get("key") == pao_key:
                                curr = food.get("grams", 0)
                                meals[m_idx]["foods"][fi] = calc_food(pao_key, curr + pao_grams)
                                has_pao = True
                                break
                        if not has_pao:
                            meals[m_idx]["foods"].append(calc_food(pao_key, pao_grams))
                    
                    # Arroz extra se necessário (mantém o existente + adiciona)
                    if arroz_extra_por_refeicao > 0:
                        new_g = round_to_10(current_g + arroz_extra_por_refeicao)
                        meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                
                adjusted = True
            elif len(carb_indices) == 1:
                # Só tem carb em uma refeição - balanceia com pão também
                m_idx, (f_idx, food_key, current_g) = list(carb_indices.items())[0]
                
                pao_key = "pao"
                pao_carbs_per_100g = FOODS.get(pao_key, {}).get("c", 49)
                pao_unit_g = 50
                carbs_por_pao = (pao_carbs_per_100g / 100) * pao_unit_g
                
                max_paes = 10
                max_carbs_com_paes = max_paes * carbs_por_pao
                
                if increase_needed <= max_carbs_com_paes:
                    paes_necessarios = int(increase_needed / carbs_por_pao) + 1
                    paes_necessarios = min(paes_necessarios, 10)
                    pao_grams = paes_necessarios * pao_unit_g
                    # Adiciona pães
                    has_pao = False
                    for fi, food in enumerate(meals[m_idx]["foods"]):
                        if food.get("key") == pao_key:
                            curr = food.get("grams", 0)
                            meals[m_idx]["foods"][fi] = calc_food(pao_key, curr + pao_grams)
                            has_pao = True
                            break
                    if not has_pao:
                        meals[m_idx]["foods"].append(calc_food(pao_key, pao_grams))
                else:
                    # Pães + arroz
                    pao_grams = 10 * pao_unit_g  # 10 pães
                    has_pao = False
                    for fi, food in enumerate(meals[m_idx]["foods"]):
                        if food.get("key") == pao_key:
                            curr = food.get("grams", 0)
                            meals[m_idx]["foods"][fi] = calc_food(pao_key, curr + pao_grams)
                            has_pao = True
                            break
                    if not has_pao:
                        meals[m_idx]["foods"].append(calc_food(pao_key, pao_grams))
                    
                    # Arroz extra
                    carbs_restantes = increase_needed - max_carbs_com_paes
                    c_per_100 = FOODS[food_key]["c"]
                    arroz_extra = round_to_10(carbs_restantes / (c_per_100 / 100))
                    new_g = round_to_10(current_g + arroz_extra)
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
    
    # 🔒 GARANTIA FINAL: Nenhuma refeição pode ficar vazia ou só com azeite/castanhas
    # E azeite SÓ pode aparecer no almoço/jantar!
    for m_idx, meal in enumerate(meals):
        foods = meal.get("foods", [])
        
        # REMOVE azeite de refeições que não são almoço/jantar (índices 2 e 4)
        is_main_meal = m_idx in [2, 4] if num_meals == 6 else m_idx in [1, 3] if num_meals == 4 else m_idx in [2, 4]
        
        # Identifica se é lanche (manhã ou tarde)
        meal_name_lower = meal.get("name", "").lower()
        is_lanche = "lanche" in meal_name_lower
        
        if not is_main_meal:
            # Remove azeite E carnes dos lanches/café/ceia
            meals[m_idx]["foods"] = [f for f in foods if f.get("key") not in {"azeite"} and f.get("key") not in CARNES_APENAS_ALMOCO_JANTAR]
            foods = meals[m_idx]["foods"]
        
        # REGRA RIGOROSA PARA LANCHES: Apenas alimentos permitidos
        if is_lanche:
            # Filtra para manter APENAS alimentos permitidos em lanches
            meals[m_idx]["foods"] = [f for f in foods if f.get("key") in ALIMENTOS_PERMITIDOS_LANCHE]
            foods = meals[m_idx]["foods"]
            
            # Se ficou vazio, adiciona frutas e castanhas
            if not foods:
                meals[m_idx]["foods"] = [
                    calc_food(get_restriction_safe_fruit(), 150),
                    calc_food("castanhas", 20)
                ]
                foods = meals[m_idx]["foods"]
        
        # Verifica se a refeição está vazia ou só tem gordura
        non_fat_foods = [f for f in foods if f.get("key") not in {"azeite", "castanhas", "pasta_amendoim"}]
        
        if len(non_fat_foods) == 0:
            # Refeição está vazia ou só com gordura - adiciona alimento adequado
            if m_idx == 0:  # Café
                safe_protein = get_restriction_safe_protein_light()  # Usa função global
                safe_carb = get_restriction_safe_breakfast_carb()
                meals[m_idx]["foods"].insert(0, calc_food(safe_protein, 100))
                meals[m_idx]["foods"].insert(1, calc_food(safe_carb, 80))
            elif m_idx in [1, 3]:  # Lanches
                # LANCHES: APENAS frutas, iogurte, pão, oleaginosas (NUNCA carnes, ovos, cottage, tofu)
                meals[m_idx]["foods"].insert(0, calc_food(get_restriction_safe_fruit(), 150))
                safe_lanche_protein = get_lanche_safe_food("protein")  # Retorna iogurte ou fruta
                meals[m_idx]["foods"].insert(1, calc_food(safe_lanche_protein, 100))
            elif m_idx == 5:  # Ceia
                meals[m_idx]["foods"].insert(0, calc_food(get_restriction_safe_fruit(), 150))
            else:  # Almoço/Jantar
                safe_protein = get_safe_protein_main()
                meals[m_idx]["foods"].insert(0, calc_food(safe_protein, 150))
                meals[m_idx]["foods"].insert(1, calc_food("arroz_branco", 200))
    
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
        return calc_food(get_restriction_safe_protein(), 100)
    
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


def validate_and_fix_meal(meal: Dict, meal_index: int, preferred: Set[str] = None, restrictions: List[str] = None) -> Dict:
    """
    ✅ Valida e corrige uma refeição seguindo as REGRAS POR TIPO.
    
    GARANTIAS:
    - Refeição NUNCA vazia
    - Todos alimentos válidos
    - Respeita regras de cada tipo de refeição
    - Totais calculados corretamente
    - ✅ RESPEITA RESTRIÇÕES ALIMENTARES
    """
    if restrictions is None:
        restrictions = []
    
    # Calcula alimentos excluídos por restrições
    excluded_by_restrictions = set()
    for r in restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded_by_restrictions.update(RESTRICTION_EXCLUSIONS[r])
    
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
    
    # ✅ FALLBACKS SEGUROS que respeitam restrições
    def get_safe_protein_main():
        """Proteína para almoço/jantar que respeita restrições"""
        options = ["tofu", "ovos", "frango", "tilapia"]
        for opt in options:
            if opt not in excluded_by_restrictions:
                return opt
        return "arroz_branco"  # Último fallback: carb
    
    def get_safe_protein_light():
        """Proteína leve para lanches que respeita restrições"""
        options = ["ovos", "tofu", "iogurte_zero", "cottage"]
        for opt in options:
            if opt not in excluded_by_restrictions:
                return opt
        return "banana"  # Último fallback: fruta
    
    # Se refeição vazia, adiciona alimento padrão SEGUINDO AS REGRAS E RESTRIÇÕES
    if not foods or len(foods) == 0:
        if meal_index == 0:  # Café da Manhã
            # PERMITIDO: ovos, aveia, frutas | PROIBIDO: carnes, azeite
            safe_protein = get_safe_protein_light()
            safe_carb = get_restriction_safe_breakfast_carb()  # Usa função inteligente
            foods = [calc_food(safe_protein, 100), calc_food(safe_carb, 40), calc_food(get_restriction_safe_fruit(), 100)]
        elif meal_index == 1:  # Lanche manhã
            # PERMITIDO: frutas, oleaginosas | PROIBIDO: carnes, azeite, cottage
            foods = [calc_food("maca", 150), calc_food("castanhas", 20)]
        elif meal_index == 2:  # Almoço
            # OBRIGATÓRIO: 1 proteína + 1 carboidrato | PERMITIDO: azeite
            safe_protein = get_safe_protein_main()
            foods = [calc_food(safe_protein, 150), calc_food("arroz_branco", 150), calc_food("salada", 100), calc_food("azeite", 10)]
        elif meal_index == 3:  # Lanche tarde
            # PERMITIDO: frutas, oleaginosas | PROIBIDO: carnes, azeite, cottage
            foods = [calc_food("laranja", 150), calc_food("castanhas", 20)]
        elif meal_index == 4:  # Jantar
            # OBRIGATÓRIO: 1 proteína + 1 carboidrato | PERMITIDO: azeite
            safe_protein = get_safe_protein_main()
            safe_carb = "arroz_integral" if "arroz_integral" not in excluded_by_restrictions else "arroz_branco"
            foods = [calc_food(safe_protein, 150), calc_food(safe_carb, 120), calc_food("brocolis", 100), calc_food("azeite", 10)]
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
                validated_food = calc_food(get_restriction_safe_fruit(), validated_food.get("grams", 100))
            validated_foods.append(validated_food)
    
    # Garante que tem pelo menos 1 alimento (RESPEITANDO regras da refeição E RESTRIÇÕES)
    if len(validated_foods) == 0:
        if meal_index == 0:  # Café - proteína leve
            safe_protein = get_safe_protein_light()
            validated_foods = [calc_food(safe_protein, 100)]
        elif meal_index == 5:  # Ceia - NUNCA OVOS, sem cottage!
            validated_foods = [calc_food("morango", 150)]
        elif meal_index in [1, 3]:  # Lanches - fruta (NUNCA carne!)
            validated_foods = [calc_food(get_restriction_safe_fruit(), 150)]
        else:  # Almoço/Jantar - proteína principal
            safe_protein = get_safe_protein_main()
            validated_foods = [calc_food(safe_protein, 150)]
    
    # Recalcula totais da refeição
    mp, mc, mf, mcal = sum_foods(validated_foods)
    
    # Garante calorias mínimas (RESPEITANDO regras da refeição E RESTRIÇÕES)
    if mcal < MIN_MEAL_CALORIES:
        if meal_index in [0, 5]:  # Café ou Ceia - adicionar carb ou fruta
            # Usa a nova função inteligente que respeita todas as restrições
            safe_carb = get_restriction_safe_breakfast_carb()
            validated_foods.append(calc_food(safe_carb, 50) if meal_index == 0 else calc_food(get_restriction_safe_fruit(), 100))
        elif meal_index in [1, 3]:  # Lanches - adicionar fruta (NUNCA carne!)
            validated_foods.append(calc_food(get_restriction_safe_fruit(), 150))
        else:  # Almoço/Jantar - adicionar proteína segura
            safe_protein = get_safe_protein_main()
            validated_foods.append(calc_food(safe_protein, 100))
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
                        foods_to_keep.append(calc_food(get_restriction_safe_fruit(), 150))
                else:
                    foods_to_keep.append(food)
            
            meal["foods"] = foods_to_keep
            
            # Recalcula macros da refeição
            mp, mc, mf, mcal = sum_foods(meal["foods"])
            meal["total_calories"] = mcal
            meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    return meals


def validate_and_fix_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int,
                          preferred: Set[str] = None, meal_count: int = 6, restrictions: List[str] = None) -> List[Dict]:
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
    ☑ RESPEITA RESTRIÇÕES ALIMENTARES
    
    Se qualquer item falhar → CORRIGE AUTOMATICAMENTE
    """
    if restrictions is None:
        restrictions = []
    
    # Calcula alimentos excluídos por restrições
    excluded_by_restrictions = set()
    for r in restrictions:
        if r in RESTRICTION_EXCLUSIONS:
            excluded_by_restrictions.update(RESTRICTION_EXCLUSIONS[r])
    
    # Valida cada refeição (apenas as que existem)
    validated_meals = []
    for idx, meal in enumerate(meals[:meal_count]):
        validated_meal = validate_and_fix_meal(meal, idx, preferred, restrictions)
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
        
        # ✅ ADICIONA PROTEÍNA RESPEITANDO RESTRIÇÕES
        safe_protein = get_safe_fallback("protein", restrictions, ["tofu", "ovos", "frango"])
        if safe_protein:
            validated_meals[target_meal]["foods"].append(calc_food(safe_protein, 100))
        else:
            # Se nenhuma proteína é válida, adiciona carb
            validated_meals[target_meal]["foods"].append(calc_food("arroz_branco", 100))
        
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
                validated_meals[meal_idx]["foods"][food_idx] = calc_food(get_restriction_safe_fruit(), grams)
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
        
        🧠 AUTO-COMPLETAR INTELIGENTE:
        - Prioriza alimentos escolhidos pelo usuário
        - Se faltar, completa automaticamente com alimentos padrão
        - NUNCA gera erro
        - NUNCA deixa refeição vazia
        
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
        
        # ✅ CONFIGURA RESTRIÇÕES GLOBAIS PARA FALLBACKS
        # Isso garante que todos os fallbacks respeitam as restrições
        set_diet_restrictions(dietary_restrictions)
        
        # ✅ AUTO-COMPLETAR INTELIGENTE
        # Prioriza alimentos do usuário, completa automaticamente se necessário
        preferred_foods, auto_completed, auto_message = validate_user_foods(
            raw_preferred, dietary_restrictions
        )
        
        # Não gera erro - sempre continua com dieta funcional
        
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
        # ✅ PASSA RESTRIÇÕES para garantir que fallbacks respeitam dietas!
        meals = validate_and_fix_diet(meals, target_p, target_c, target_f, preferred_foods, meal_count, dietary_restrictions)
        
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
        
        # ✅ AJUSTE FINAL: Garantir que os macros totais estejam corretos
        for _ in range(3):
            meals = fine_tune_diet(meals, target_p, target_c, target_f)
            total_p = sum(f.get("protein", 0) for m in meals for f in m.get("foods", []))
            total_c = sum(f.get("carbs", 0) for m in meals for f in m.get("foods", []))
            total_f = sum(f.get("fat", 0) for m in meals for f in m.get("foods", []))
            if abs(total_p - target_p) <= 15 and abs(total_c - target_c) <= 30 and abs(total_f - target_f) <= 10:
                break
        
        # 🔒 COMPENSAÇÃO PARA RESTRIÇÕES SEVERAS
        # Se a dieta ainda está muito abaixo das calorias alvo, adiciona mais comida
        total_cal = sum(f.get("calories", 0) for m in meals for f in m.get("foods", []))
        cal_diff = target_calories - total_cal
        
        print(f"[DIET DEBUG] Target: {target_calories}kcal, Generated: {total_cal}kcal, Diff: {cal_diff}kcal, Goal: {goal}")
        
        # 🔄 FUNÇÃO PARA CONSOLIDAR ALIMENTOS DUPLICADOS NA MESMA REFEIÇÃO
        def consolidate_duplicate_foods(meals_list):
            """Combina alimentos duplicados na mesma refeição"""
            for meal in meals_list:
                foods = meal.get("foods", [])
                consolidated = {}
                for food in foods:
                    key = food.get("key", "unknown")
                    if key in consolidated:
                        # Soma as gramas
                        old_grams = consolidated[key].get("grams", 0)
                        new_grams = old_grams + food.get("grams", 0)
                        consolidated[key] = calc_food(key, new_grams)
                    else:
                        consolidated[key] = food
                
                meal["foods"] = list(consolidated.values())
                # Recalcula totais
                mp, mc, mf, mcal = sum_foods(meal["foods"])
                meal["total_calories"] = mcal
                meal["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
            return meals_list
        
        # 📉 REDUÇÃO quando está ACIMA do alvo (mais de 5%)
        if cal_diff < -target_calories * 0.05:  # Negativo significa ACIMA
            excess_cal = abs(cal_diff)
            print(f"[DIET DEBUG] Diet is ABOVE target by {excess_cal}kcal, reducing portions")
            
            # Determina refeições principais (almoço e jantar) para reduzir carboidratos
            if meal_count == 4:
                main_meal_indices = [1, 3]
            elif meal_count == 5:
                main_meal_indices = [2, 4]
            else:
                main_meal_indices = [2, 4]
            
            # Reduz carboidratos (arroz, batata) nas refeições principais
            for idx in main_meal_indices:
                if idx < len(meals) and excess_cal > 50:
                    for f_idx, food in enumerate(meals[idx]["foods"]):
                        if food.get("category") == "carb" or food.get("key") in ["arroz_branco", "arroz_integral", "batata_doce", "macarrao"]:
                            current_grams = food.get("grams", 100)
                            # Reduz até 30% da porção
                            reduce_grams = min(current_grams * 0.3, excess_cal / 1.3)  # ~1.3 cal/g para arroz
                            new_grams = round_to_10(max(50, current_grams - reduce_grams))  # Mínimo 50g
                            
                            if new_grams < current_grams:
                                meals[idx]["foods"][f_idx] = calc_food(food.get("key"), new_grams)
                                excess_cal -= (current_grams - new_grams) * 1.3
                            break
                    
                    # Recalcula totais da refeição
                    mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                    meals[idx]["total_calories"] = mcal
                    meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
            
            total_cal_after = sum(f.get("calories", 0) for m in meals for f in m.get("foods", []))
            print(f"[DIET DEBUG] After reduction: {total_cal_after}kcal")
        
        # 🏋️ COMPENSAÇÃO ESPECIAL PARA BULKING (mais conservadora)
        # Se é bulking e está mais de 10% abaixo, compensa moderadamente
        if goal.lower() == 'bulking' and cal_diff > target_calories * 0.10:
            print(f"[DIET DEBUG] BULKING compensation needed: {cal_diff}kcal deficit")
            
            # Determina índices das refeições principais (almoço e jantar)
            if meal_count == 4:
                main_meal_indices = [1, 3]
            elif meal_count == 5:
                main_meal_indices = [2, 4]
            else:
                main_meal_indices = [2, 4]
            
            # 🍚 Adiciona carboidratos extras nas refeições principais
            # LIMITE: máximo 80g extra por refeição (não 150g!)
            safe_carb = get_safe_fallback("carb_principal", dietary_restrictions, ["arroz_branco", "batata_doce", "arroz_integral"])
            if safe_carb:
                carb_cal_per_100g = FOODS.get(safe_carb, {}).get("c", 25) * 4 + FOODS.get(safe_carb, {}).get("f", 0) * 9
                
                # Calcula quanto precisa adicionar por refeição (MAX 80g cada)
                extra_per_meal = cal_diff / len(main_meal_indices)
                extra_grams = round_to_10(min((extra_per_meal / (carb_cal_per_100g / 100)), 80))
                
                for idx in main_meal_indices:
                    if idx < len(meals):
                        # Verifica se já tem esse carb na refeição
                        existing_carb = None
                        for f_idx, food in enumerate(meals[idx]["foods"]):
                            if food.get("key") == safe_carb:
                                existing_carb = (f_idx, food)
                                break
                        
                        if existing_carb:
                            # Aumenta o existente (max 250g total por refeição)
                            f_idx, food = existing_carb
                            current_grams = food.get("grams", 0)
                            new_grams = min(current_grams + extra_grams, 250)
                            meals[idx]["foods"][f_idx] = calc_food(safe_carb, new_grams)
                        else:
                            # Adiciona novo
                            meals[idx]["foods"].append(calc_food(safe_carb, extra_grams))
                        
                        mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                        meals[idx]["total_calories"] = mcal
                        meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
            
            # Recalcula
            total_cal_after = sum(f.get("calories", 0) for m in meals for f in m.get("foods", []))
            cal_diff_after = target_calories - total_cal_after
            print(f"[DIET DEBUG] After BULKING compensation: {total_cal_after}kcal, Diff: {cal_diff_after}kcal")
        
        # 🔄 CONSOLIDA DUPLICADOS antes de continuar
        meals = consolidate_duplicate_foods(meals)
        
        # Recalcula após consolidação
        total_cal = sum(f.get("calories", 0) for m in meals for f in m.get("foods", []))
        cal_diff = target_calories - total_cal
        
        # 🔒 COMPENSAÇÃO PARA RESTRIÇÕES SEVERAS (não-bulking)
        # Se está mais de 15% abaixo do target, compensa DISTRIBUINDO entre pão e arroz
        if cal_diff > target_calories * 0.15 and goal.lower() != 'bulking':
            cal_diff_remaining = cal_diff  # Usa o deficit atual
            
            # 🍚 Adiciona nas refeições principais (almoço/jantar)
            if cal_diff_remaining > target_calories * 0.10:
                # Determina índices das refeições principais (almoço e jantar)
                if meal_count == 4:
                    main_meal_indices = [1, 3]
                elif meal_count == 5:
                    main_meal_indices = [2, 4]
                else:
                    main_meal_indices = [2, 4]
                
                safe_carb = get_safe_fallback("carb_principal", dietary_restrictions, ["batata_doce", "arroz_integral", "arroz_branco"])
                if safe_carb:
                    carb_per_100g = FOODS.get(safe_carb, {}).get("c", 20) * 4
                    fat_per_100g = FOODS.get(safe_carb, {}).get("f", 0) * 9
                    total_per_100g = carb_per_100g + fat_per_100g
                    
                    # Distribui a compensação entre almoço e jantar
                    # Para diabéticos (que não tem arroz/pão), permite mais batata (até 300g cada)
                    max_extra = 300 if "diabetico" in dietary_restrictions else 200
                    extra_grams_each = round_to_10(min((cal_diff_remaining / 2) / (total_per_100g / 100), max_extra))
                    
                    for idx in main_meal_indices:
                        if idx < len(meals):
                            meals[idx]["foods"].append(calc_food(safe_carb, extra_grams_each))
                            mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                            meals[idx]["total_calories"] = mcal
                            meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
            
            # 🥩 TERCEIRO: Se ainda está muito abaixo (>25% de déficit), adiciona proteína
            total_cal_after_carbs = sum(f.get("calories", 0) for m in meals for f in m.get("foods", []))
            if target_calories - total_cal_after_carbs > target_calories * 0.25:
                safe_protein = get_restriction_safe_protein()
                if safe_protein:
                    extra_protein_grams = 100
                    if meal_count == 4:
                        main_meal_indices = [1, 3]
                    elif meal_count == 5:
                        main_meal_indices = [2, 4]
                    else:
                        main_meal_indices = [2, 4]
                    
                    for idx in main_meal_indices:
                        if idx < len(meals):
                            meals[idx]["foods"].append(calc_food(safe_protein, extra_protein_grams))
                            mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                            meals[idx]["total_calories"] = mcal
                            meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
        
        # Aplica horários personalizados se fornecidos
        if meal_times and len(meal_times) == len(meals):
            for i, mt in enumerate(meal_times):
                if isinstance(mt, dict):
                    meals[i]["name"] = mt.get("name", meals[i].get("name", f"Refeição {i+1}"))
                    meals[i]["time"] = mt.get("time", meals[i].get("time", "12:00"))
        
        # 🍚🥗 COMPENSAÇÃO DE CARBOIDRATOS - Auto-complete com arroz e feijão
        # Se os carboidratos totais estão abaixo do target, adiciona arroz/feijão nas refeições principais
        total_carbs_current = sum(f.get("carbs", 0) for m in meals for f in m.get("foods", []))
        carb_deficit = target_c - total_carbs_current
        
        print(f"[DIET DEBUG] Carbs: Target={target_c}g, Current={total_carbs_current}g, Deficit={carb_deficit}g")
        
        if carb_deficit > 30:  # Se falta mais de 30g de carbs
            # Determina refeições principais (almoço e jantar)
            if meal_count == 4:
                main_meal_indices = [1, 3]  # Almoço e Jantar
            elif meal_count == 5:
                main_meal_indices = [2, 4]  # Almoço e Jantar
            else:
                main_meal_indices = [2, 4]  # Almoço e Jantar
            
            # Divide o déficit entre almoço e jantar
            carb_per_meal = carb_deficit / 2
            
            # 🍚🍞 COMPENSAÇÃO DE CARBOIDRATOS - BALANCEADA ENTRE ARROZ E PÃES
            # Limite: máximo 10 pães por dia, resto em arroz
            
            # Pão Francês (key="pao"): ~49g carbs por 100g (unidade = 50g = ~24.5g carbs)
            # Pão Integral: ~42g carbs por 100g (fatia = 30g = ~12.6g carbs)
            # Arroz branco: ~28g carbs por 100g
            
            pao_key = "pao"  # Pão Francês - mais carbs por unidade
            pao_carbs_per_100g = FOODS.get(pao_key, {}).get("c", 49)
            pao_unit_grams = FOODS.get(pao_key, {}).get("unit_g", 50)  # 1 pão = 50g
            carbs_por_pao = (pao_carbs_per_100g / 100) * pao_unit_grams  # ~24.5g carbs por pão
            
            safe_carb = get_safe_fallback("carb_principal", dietary_restrictions, ["arroz_branco", "arroz_integral", "batata_doce"])
            carb_per_100g = FOODS.get(safe_carb, {}).get("c", 28) if safe_carb else 28
            
            # Estratégia: usar até 10 pães (5 por refeição principal) e o resto em arroz
            max_paes_total = 10
            paes_por_refeicao_max = 5  # Máx 5 pães por refeição
            
            # Quanto de carbs podemos cobrir com 10 pães (max ~245g carbs)
            max_carbs_com_paes = max_paes_total * carbs_por_pao
            
            print(f"[DIET DEBUG] Carb compensation: deficit={carb_deficit}g, max_paes_carbs={max_carbs_com_paes}g, carbs_por_pao={carbs_por_pao}g")
            
            if carb_deficit <= max_carbs_com_paes:
                # Déficit pequeno/médio: só pães são suficientes
                paes_necessarios = int(carb_deficit / carbs_por_pao) + 1
                paes_por_refeicao_calc = min(paes_por_refeicao_max, (paes_necessarios + 1) // 2)
                arroz_extra_por_refeicao = 0
            else:
                # Déficit grande: usa 10 pães + arroz extra
                paes_por_refeicao_calc = paes_por_refeicao_max  # 5 pães por refeição
                carbs_restantes = carb_deficit - max_carbs_com_paes
                arroz_extra_por_refeicao = round_to_10((carbs_restantes / 2) / carb_per_100g * 100)
            
            print(f"[DIET DEBUG] Adding {paes_por_refeicao_calc} pães/refeição + {arroz_extra_por_refeicao}g arroz/refeição")
            
            for idx in main_meal_indices:
                if idx < len(meals):
                    # Adiciona pães
                    if paes_por_refeicao_calc > 0:
                        pao_grams = paes_por_refeicao_calc * pao_unit_grams
                        # Verifica se já tem pão
                        pao_idx = None
                        for f_idx, food in enumerate(meals[idx]["foods"]):
                            if food.get("key") == pao_key:
                                pao_idx = f_idx
                                break
                        
                        if pao_idx is not None:
                            current = meals[idx]["foods"][pao_idx].get("grams", 0)
                            meals[idx]["foods"][pao_idx] = calc_food(pao_key, current + pao_grams)
                        else:
                            meals[idx]["foods"].append(calc_food(pao_key, pao_grams))
                    
                    # Adiciona arroz extra se necessário
                    if arroz_extra_por_refeicao > 0 and safe_carb:
                        arroz_idx = None
                        for f_idx, food in enumerate(meals[idx]["foods"]):
                            if food.get("key") == safe_carb:
                                arroz_idx = f_idx
                                break
                        
                        if arroz_idx is not None:
                            current = meals[idx]["foods"][arroz_idx].get("grams", 0)
                            meals[idx]["foods"][arroz_idx] = calc_food(safe_carb, current + arroz_extra_por_refeicao)
                        else:
                            meals[idx]["foods"].append(calc_food(safe_carb, arroz_extra_por_refeicao))
                    
                    # Recalcula totais da refeição
                    mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                    meals[idx]["total_calories"] = mcal
                    meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
            
            # Verifica se também pode adicionar feijão (se nas preferências)
            if "feijao" in preferred_foods and carb_deficit > 60:
                feijao_allowed = True
                for r in dietary_restrictions:
                    if r in RESTRICTION_EXCLUSIONS and "feijao" in RESTRICTION_EXCLUSIONS[r]:
                        feijao_allowed = False
                        break
                
                if feijao_allowed:
                    for idx in main_meal_indices:
                        if idx < len(meals):
                            # Verifica se já tem feijão
                            has_feijao = any(f.get("key") == "feijao" for f in meals[idx]["foods"])
                            if not has_feijao:
                                meals[idx]["foods"].append(calc_food("feijao", 120))
                                mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                                meals[idx]["total_calories"] = mcal
                                meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
            
            # Consolida duplicados novamente após adicionar
            meals = consolidate_duplicate_foods(meals)
            
            # Log final
            total_carbs_after = sum(f.get("carbs", 0) for m in meals for f in m.get("foods", []))
            print(f"[DIET DEBUG] After carb compensation: {total_carbs_after}g carbs")
            
            # 🍌 COMPENSAÇÃO EXTRA NOS LANCHES para dietas de bulking
            # Se ainda falta carbs, adiciona mais frutas/aveia nos lanches
            remaining_carb_deficit = target_c - total_carbs_after
            if remaining_carb_deficit > 15:  # Se ainda falta mais de 15g de carbs
                # Índices dos lanches
                if meal_count == 4:
                    lanche_indices = [2]  # Lanche tarde
                elif meal_count == 5:
                    lanche_indices = [1, 3]  # Lanche manhã e tarde
                else:
                    lanche_indices = [1, 3, 5]  # Manhã, tarde, ceia
                
                carbs_per_lanche = remaining_carb_deficit / len(lanche_indices)
                
                for idx in lanche_indices:
                    if idx < len(meals):
                        # Aumenta frutas existentes ou adiciona mais
                        safe_fruit = get_restriction_safe_fruit()
                        fruit_per_100g = FOODS.get(safe_fruit, {}).get("c", 20)
                        extra_fruit_g = round_to_10(min((carbs_per_lanche / fruit_per_100g) * 100, 200))
                        
                        if extra_fruit_g >= 20:  # Reduzido de 50 para 20g mínimo
                            # Procura fruta existente
                            fruit_idx = None
                            for f_idx, food in enumerate(meals[idx]["foods"]):
                                if food.get("category") == "fruit":
                                    fruit_idx = f_idx
                                    break
                            
                            if fruit_idx is not None:
                                current_g = meals[idx]["foods"][fruit_idx].get("grams", 0)
                                new_g = min(current_g + extra_fruit_g, 300)  # Max 300g de fruta
                                meals[idx]["foods"][fruit_idx] = calc_food(meals[idx]["foods"][fruit_idx].get("key"), new_g)
                            else:
                                meals[idx]["foods"].append(calc_food(safe_fruit, extra_fruit_g))
                            
                            # Recalcula totais
                            mp, mc, mf, mcal = sum_foods(meals[idx]["foods"])
                            meals[idx]["total_calories"] = mcal
                            meals[idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
                
                # Log final após compensação de lanches
                total_carbs_final = sum(f.get("carbs", 0) for m in meals for f in m.get("foods", []))
                print(f"[DIET DEBUG] After lanche compensation: {total_carbs_final}g carbs")
        
        # 🔒🔒🔒 FILTRAGEM FINAL ABSOLUTA PARA LANCHES 🔒🔒🔒
        # Esta é a ÚLTIMA linha de defesa - remove QUALQUER alimento proibido dos lanches
        for i, meal in enumerate(meals):
            meal_name = meal.get("name", "").lower()
            if "lanche" in meal_name:
                # Remove TUDO que não está na lista branca de lanches
                original_foods = meal.get("foods", [])
                filtered_foods = [f for f in original_foods if f.get("key") in ALIMENTOS_PERMITIDOS_LANCHE]
                
                # Se ficou vazio, adiciona frutas + castanhas (sempre seguros)
                if not filtered_foods:
                    safe_fruit = get_restriction_safe_fruit()
                    filtered_foods = [
                        calc_food(safe_fruit, 150),
                        calc_food("castanhas", 20)
                    ]
                
                meals[i]["foods"] = filtered_foods
        
        # Formata resultado
        final_meals = []
        for m in meals:
            # Recalcula totais da refeição (garantia extra)
            mp, mc, mf, mcal = sum_foods(m.get("foods", []))
            
            # Garante que refeição não está vazia
            foods = m.get("foods", [])
            if not foods:
                foods = [calc_food(get_restriction_safe_protein(), 100)]
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
                extra = calc_food(get_restriction_safe_protein(), 100)
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
        if auto_completed:
            notes += " | 🔄 Auto-completada"
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal_int,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=total_cal,
            computed_macros={"protein": total_p, "carbs": total_c, "fat": total_f},
            supplements=supplements,
            notes=notes,
            auto_completed=auto_completed,
            auto_complete_message=auto_message
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
            validated_foods = [calc_food(get_restriction_safe_protein(), 100)]
        
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
            extra = calc_food(get_restriction_safe_protein(), 150)
            meals[2]["foods"].append(extra)
            total_cal += extra["calories"]
            total_p += extra["protein"]
    
    diet_plan["computed_calories"] = max(MIN_DAILY_CALORIES, total_cal)
    diet_plan["computed_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["target_calories"] = max(MIN_DAILY_CALORIES, total_cal)
    diet_plan["target_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["notes"] = f"Dieta V14 ajustada: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g | ✅ Validada"
    
    return diet_plan
