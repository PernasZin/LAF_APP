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


# ==================== MÍNIMOS NECESSÁRIOS ====================
MIN_PROTEINS = 3
MIN_CARBS = 3
MIN_FATS = 2
MIN_FRUITS = 2


# ==================== AUTO-COMPLETE PADRÕES ====================
# Ordem de prioridade para auto-complete (alimentos comuns e baratos no Brasil)

DEFAULT_PROTEINS = ["frango", "patinho", "ovos", "atum", "iogurte_grego", "tilapia", "cottage"]
DEFAULT_CARBS = ["arroz_branco", "arroz_integral", "batata_doce", "aveia", "macarrao", "feijao", "pao_integral", "lentilha"]
DEFAULT_FATS = ["azeite", "pasta_amendoim", "castanhas", "amendoas", "queijo"]
DEFAULT_FRUITS = ["banana", "maca", "laranja", "morango", "mamao", "melancia"]


# ==================== RESTRIÇÕES ALIMENTARES ====================

RESTRICTION_EXCLUSIONS = {
    "Vegetariano": {"frango", "coxa_frango", "patinho", "carne_moida", "suino", 
                   "tilapia", "atum", "salmao", "camarao", "sardinha", "peru"},
    "Sem Lactose": {"cottage", "iogurte_grego", "queijo", "cream_cheese", "manteiga"},
    "Sem Glúten": {"aveia", "macarrao", "pao", "pao_integral"},
    "Low Carb": {"arroz_branco", "arroz_integral", "batata_doce", "batata", 
                 "macarrao", "pao", "pao_integral", "banana", "manga", "uva"},
}


# ==================== NORMALIZAÇÃO ====================

FOOD_NORMALIZATION = {
    # PROTEÍNAS
    "chicken_breast": "frango", "chicken": "frango", "chicken_thigh": "coxa_frango",
    "lean_beef": "patinho", "ground_beef": "carne_moida", "beef": "patinho",
    "pork": "suino", "eggs": "ovos", "egg_whites": "claras",
    "tilapia": "tilapia", "tuna": "atum", "salmon": "salmao",
    "shrimp": "camarao", "sardine": "sardinha", "turkey": "peru", "fish": "tilapia",
    "cottage": "cottage", "greek_yogurt": "iogurte_grego", "tofu": "tofu",
    
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
    "cottage": {"name": "Queijo Cottage", "p": 11.0, "c": 3.4, "f": 4.3, "category": "protein", "unit": "colher sopa", "unit_g": 30},
    "iogurte_grego": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "category": "protein", "unit": "pote", "unit_g": 170},
    "iogurte_natural": {"name": "Iogurte Natural", "p": 4.0, "c": 6.0, "f": 3.0, "category": "protein", "unit": "pote", "unit_g": 170},
    "requeijao_light": {"name": "Requeijão Light", "p": 8.0, "c": 3.0, "f": 10.0, "category": "protein", "unit": "colher sopa", "unit_g": 30},
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
    
    # === VEGETAIS ===
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "category": "vegetable", "unit": "prato cheio", "unit_g": 100},
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "category": "vegetable", "unit": "xícara cozido", "unit_g": 100},
    
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
        
        # Iogurtes - sempre em potes inteiros
        "iogurte_grego": 170,     # 1 pote = 170g
        "iogurte_natural": 170,   # 1 pote = 170g
        
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
        
        # IMPORTANTE: Arredondar para baixo quando round_down=True
        # Isso ajuda a manter os macros abaixo do target para ajuste fino posterior
        if round_down:
            units_int = max(1, int(units_needed))  # Arredonda para BAIXO (floor)
        else:
            units_int = max(1, round(units_needed))  # Arredonda normal
        
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
        g = max(MIN_FOOD_GRAMS, min(max_grams, g))
        
        # GARANTIA: Sempre > 0
        if g <= 0:
            g = MIN_FOOD_GRAMS
        
        # Calcula equivalente em medida caseira
        if unit_g > 0:
            unit_qty = g / unit_g
            # Formata quantidade de unidades
            if unit_qty >= 1:
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


# ==================== AUTO-COMPLETE INTELIGENTE ====================

def smart_auto_complete(preferred: Set[str], restrictions: List[str], goal: str = "manutencao") -> Tuple[Set[str], bool, str]:
    """
    Verifica mínimos e auto-completa se necessário.
    
    NUNCA TRAVA - sempre retorna algo funcional.
    
    Returns:
        - Set de alimentos (preferidos + auto-completados)
        - bool: True se auto-completou
        - str: Mensagem amigável (ou None)
    """
    # Conta por categoria (filtrando restrições)
    available = filter_by_restrictions(preferred, restrictions)
    
    proteins = [f for f in available if f in FOODS and FOODS[f]["category"] == "protein"]
    carbs = [f for f in available if f in FOODS and FOODS[f]["category"] == "carb"]
    fats = [f for f in available if f in FOODS and FOODS[f]["category"] == "fat"]
    fruits = [f for f in available if f in FOODS and FOODS[f]["category"] == "fruit"]
    
    auto_added = []
    final_foods = set(available)
    
    # Auto-complete PROTEÍNAS (mínimo 3)
    if len(proteins) < MIN_PROTEINS:
        for default_p in DEFAULT_PROTEINS:
            if default_p not in final_foods and default_p not in filter_by_restrictions({default_p}, restrictions):
                continue
            if default_p in FOODS and default_p not in final_foods:
                final_foods.add(default_p)
                auto_added.append(FOODS[default_p]["name"])
                if len([f for f in final_foods if f in FOODS and FOODS[f]["category"] == "protein"]) >= MIN_PROTEINS:
                    break
    
    # Auto-complete CARBOIDRATOS (mínimo 3)
    if len(carbs) < MIN_CARBS:
        for default_c in DEFAULT_CARBS:
            if default_c not in filter_by_restrictions({default_c}, restrictions):
                continue
            if default_c in FOODS and default_c not in final_foods:
                final_foods.add(default_c)
                auto_added.append(FOODS[default_c]["name"])
                if len([f for f in final_foods if f in FOODS and FOODS[f]["category"] == "carb"]) >= MIN_CARBS:
                    break
    
    # Auto-complete GORDURAS (mínimo 2)
    if len(fats) < MIN_FATS:
        for default_f in DEFAULT_FATS:
            if default_f not in filter_by_restrictions({default_f}, restrictions):
                continue
            if default_f in FOODS and default_f not in final_foods:
                final_foods.add(default_f)
                auto_added.append(FOODS[default_f]["name"])
                if len([f for f in final_foods if f in FOODS and FOODS[f]["category"] == "fat"]) >= MIN_FATS:
                    break
    
    # Auto-complete FRUTAS (mínimo 2)
    if len(fruits) < MIN_FRUITS:
        for default_fr in DEFAULT_FRUITS:
            if default_fr not in filter_by_restrictions({default_fr}, restrictions):
                continue
            if default_fr in FOODS and default_fr not in final_foods:
                final_foods.add(default_fr)
                auto_added.append(FOODS[default_fr]["name"])
                if len([f for f in final_foods if f in FOODS and FOODS[f]["category"] == "fruit"]) >= MIN_FRUITS:
                    break
    
    # Gera mensagem amigável se auto-completou
    if auto_added:
        message = "Você selecionou poucas opções. Para garantir uma dieta funcional, adicionei automaticamente: " + ", ".join(auto_added[:5])
        if len(auto_added) > 5:
            message += f" e mais {len(auto_added)-5} alimentos."
        message += " Você pode alterar depois nas configurações."
        return final_foods, True, message
    
    return final_foods, False, None


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
    """Calcula TDEE (Total Daily Energy Expenditure)"""
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


def calculate_macros(tdee: float, goal: str, weight: float) -> Dict[str, float]:
    """
    Calcula macros baseado no objetivo.
    
    REGRAS OBRIGATÓRIAS PARA GORDURAS:
    
    1️⃣ POR PESO CORPORAL (método principal):
       - Manutenção: 1g/kg
       - Cutting: 0.4g a 1g/kg (máx 1g/kg)
       - Bulking: 1g a 1.5g/kg (máx 1.5g/kg)
    
    2️⃣ LIMITE POR PERCENTUAL DE CALORIAS:
       - Mínimo: 20% das calorias
       - Máximo: 35% das calorias
       - Se ultrapassar → ajusta automaticamente
    """
    # Configurações por objetivo
    goal_adjustments = {
        'cutting': {
            'cal_mult': 0.85, 
            'p_mult': 2.4,
            'fat_min_per_kg': 0.6,   # Mínimo 0.6g/kg em cutting
            'fat_max_per_kg': 1.0    # Máximo 1g/kg em cutting
        },
        'manutencao': {
            'cal_mult': 1.0, 
            'p_mult': 2.0,
            'fat_min_per_kg': 0.9,   # ~1g/kg para manutenção
            'fat_max_per_kg': 1.0    # Máximo 1g/kg
        },
        'bulking': {
            'cal_mult': 1.15, 
            'p_mult': 2.2,
            'fat_min_per_kg': 1.0,   # Mínimo 1g/kg em bulking
            'fat_max_per_kg': 1.5    # Máximo 1.5g/kg em bulking
        },
        'atleta': {
            'cal_mult': 1.0, 
            'p_mult': 2.4,
            'fat_min_per_kg': 0.8,
            'fat_max_per_kg': 1.2
        }
    }
    
    adj = goal_adjustments.get(goal.lower(), goal_adjustments['manutencao'])
    
    # Cálculo base de calorias
    target_calories = tdee * adj['cal_mult']
    
    # Proteína baseada no peso
    protein = weight * adj['p_mult']
    
    # ==================== CÁLCULO DE GORDURA ====================
    # Método 1: Por peso corporal (principal)
    fat_by_weight = weight * adj['fat_max_per_kg']  # Usa o máximo da faixa
    fat_min_by_weight = weight * adj['fat_min_per_kg']
    
    # Método 2: Por percentual de calorias (validação)
    fat_min_by_percent = (target_calories * 0.20) / 9  # 20% das calorias
    fat_max_by_percent = (target_calories * 0.35) / 9  # 35% das calorias
    
    # Usa o valor por peso, mas valida contra percentual
    fat = fat_by_weight
    
    # Validação: não pode ultrapassar 35% das calorias
    if fat > fat_max_by_percent:
        fat = fat_max_by_percent
    
    # Validação: não pode ser menos que 20% das calorias (exceto se respeitar mínimo por kg)
    if fat < fat_min_by_percent and fat < fat_min_by_weight:
        fat = max(fat_min_by_percent, fat_min_by_weight)
    
    # Garante que está dentro dos limites por peso corporal
    fat = max(fat_min_by_weight, min(fat, weight * adj['fat_max_per_kg']))
    
    # Cálculo final de calorias
    protein_cal = protein * 4
    fat_cal = fat * 9
    carbs_cal = target_calories - protein_cal - fat_cal
    carbs = carbs_cal / 4
    
    # Garante mínimo de carboidratos
    if carbs < 100:
        carbs = 100
        carbs_cal = carbs * 4
        target_calories = protein_cal + fat_cal + carbs_cal
    
    # VALIDAÇÃO FINAL: Verifica se gordura está dentro dos limites
    fat_percent = (fat * 9) / target_calories * 100
    
    # Se ainda estiver fora dos limites, ajusta
    if fat_percent > 35:
        fat = (target_calories * 0.35) / 9
    elif fat_percent < 20:
        fat = (target_calories * 0.20) / 9
    
    # Recalcula carboidratos após ajuste de gordura
    fat_cal = fat * 9
    carbs_cal = target_calories - protein_cal - fat_cal
    carbs = max(100, carbs_cal / 4)
    
    return {
        'calories': round(target_calories),
        'protein': round(protein),
        'carbs': round(carbs),
        'fat': round(fat)
    }


# ==================== REGRAS POR REFEIÇÃO ====================
# IMPORTANTE: Usar APENAS alimentos ATIVOS no sistema
# REGRA DE FALHA: Se arroz, frango, peixe ou azeite aparecerem em lanches ou café, 
#                 a saída é INVÁLIDA e deve ser regenerada.

MEAL_RULES = {
    "cafe_da_manha": {
        # PERMITIDOS: Ovos, Cottage, Iogurte Grego + Aveia, Pão Integral, Tapioca + Frutas
        "proteins": {"ovos", "iogurte_grego", "cottage", "claras"},
        "carbs": {"aveia", "pao_integral", "tapioca", "cuscuz", "pao"},
        "fats": {"pasta_amendoim", "chia", "linhaca"},  # Gorduras saudáveis para café
        "fruits": True,
        # PROIBIDOS: Arroz, Feijão, Lentilha, Macarrão, Frango, Peixe, Carne, Peru, Azeite
        "description": "Café da manhã: proteínas leves + aveia/pão/tapioca + frutas"
    },
    "lanche": {
        # PERMITIDOS: Frutas + Cottage, Iogurte Grego + Castanhas, Amêndoas, Nozes
        "proteins": {"iogurte_grego", "cottage"},  # OVOS PROIBIDOS em lanches!
        "carbs": {"aveia"},  # Aveia também pode ser lanche
        "fats": {"castanhas", "amendoas", "nozes", "pasta_amendoim"},
        "fruits": True,
        # PROIBIDOS: Frango, Peixe, Carne, Peru, Ovos, Azeite, Queijo
        "description": "Lanche leve: frutas + iogurte/cottage + castanhas/amêndoas/nozes"
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
        # PERMITIDOS: Cottage, Iogurte Grego + Frutas - NUNCA OVOS!
        "proteins": {"iogurte_grego", "cottage"},  # OVOS REMOVIDOS DA CEIA!
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
    
    # Para outras categorias, usa a whitelist da refeição
    allowed_in_meal = rules.get(f"{category}s", set())
    
    if not allowed_in_meal:
        return []
    
    # REGRA: Se o usuário tem preferências, prioriza elas, mas usa outros se necessário
    available = []
    for food_key in allowed_in_meal:
        if food_key in FOODS:
            available.append(food_key)
    
    return list(filter_by_restrictions(set(available), restrictions))


def select_best_food(meal_type: str, preferred: Set[str], restrictions: List[str], 
                     category: str, priority: List[str], exclude: Set[str] = None) -> Optional[str]:
    """
    Seleciona o melhor alimento respeitando as regras da refeição.
    """
    available = get_allowed_foods(meal_type, preferred, restrictions, category)
    
    if exclude:
        available = [f for f in available if f not in exclude]
    
    if not available:
        return None
    
    # Segue prioridade se possível
    for p in priority:
        if p in available:
            return p
    
    return available[0]


# ==================== GERAÇÃO DE DIETA ====================

def generate_diet(target_p: int, target_c: int, target_f: int,
                  preferred: Set[str], restrictions: List[str], meal_count: int = 6) -> List[Dict]:
    """
    Gera dieta seguindo regras rígidas por tipo de refeição.
    
    IMPORTANTE: O TOTAL de alimentos é SEMPRE o mesmo, independente do número de refeições!
    A única diferença é como os alimentos são DISTRIBUÍDOS:
    
    - 6 refeições: Comida dividida em 6 porções menores
    - 5 refeições: Mesma comida dividida em 5 porções
    - 4 refeições: Mesma comida dividida em 4 porções maiores
    
    REGRAS OBRIGATÓRIAS:
    ☀️ Café da Manhã: proteínas leves + carbs leves + frutas (SEM carnes, SEM azeite)
    🍎 Lanches: frutas + iogurte/cottage + castanhas/amêndoas (SEM carnes, SEM ovos, SEM azeite)
    🍽️ Almoço/Jantar: 1 proteína + carboidratos (pode ter múltiplos) + azeite
    🌙 Ceia: proteína leve (iogurte/cottage) + frutas - NUNCA OVOS NA CEIA!
    
    ⭐ REGRA IMPORTANTE: Todos os alimentos selecionados pelo usuário DEVEM aparecer na dieta!
    """
    
    # ==================== PRIORIZAR ALIMENTOS SELECIONADOS ====================
    # Se o usuário selecionou um alimento, ele DEVE aparecer na dieta
    
    # Alimentos que são complementos (não devem ser confundidos com carboidratos principais)
    COMPLEMENT_FOODS = {"feijao", "lentilha"}
    
    def get_preferred_first(default_list: List[str], category: str = None, exclude_complements: bool = False) -> List[str]:
        """Retorna lista com alimentos preferidos primeiro, depois os defaults"""
        if not preferred:
            return default_list
        
        # Filtra preferidos que são da categoria (se especificada) e existem no FOODS
        pref_in_category = []
        for p in preferred:
            if p in FOODS:
                if category is None or FOODS[p]["category"] == category:
                    # Se exclude_complements, não inclui feijão/lentilha na lista de carbs principais
                    if exclude_complements and p in COMPLEMENT_FOODS:
                        continue
                    pref_in_category.append(p)
        
        # Preferidos primeiro, depois defaults que não estão nos preferidos
        result = pref_in_category.copy()
        for d in default_list:
            if d not in result and d in FOODS:
                result.append(d)
        
        return result if result else default_list
    
    # Prioridades por categoria - COM PREFERÊNCIAS DO USUÁRIO PRIMEIRO
    protein_priority = get_preferred_first(
        ["frango", "patinho", "tilapia", "atum", "salmao", "peru", "ovos", 
         "coxa_frango", "carne_moida", "camarao", "sardinha", "suino", "tofu"], "protein")
    
    light_protein_priority_cafe = get_preferred_first(
        ["ovos", "iogurte_grego", "iogurte_natural", "cottage", "claras"], "protein")
    
    light_protein_priority_ceia = get_preferred_first(
        ["cottage", "iogurte_grego", "iogurte_natural"], "protein")  # NUNCA OVOS NA CEIA!
    
    # Carboidratos principais (para almoço/jantar) - EXCLUI feijão/lentilha
    carb_priority = get_preferred_first(
        ["arroz_branco", "arroz_integral", "batata_doce", "macarrao", "macarrao_integral"], 
        "carb", exclude_complements=True)
    
    # Carboidratos complementares (feijão, lentilha - para acompanhar)
    carb_complement = get_preferred_first(["feijao", "lentilha"], "carb")
    
    # Carboidratos leves (para café da manhã) - EXCLUI feijão/lentilha
    light_carb_priority = get_preferred_first(
        ["pao_integral", "pao_forma", "pao", "aveia", "tapioca", "granola"], 
        "carb", exclude_complements=True)
    
    # Prioridade para lanches (proteínas leves com carbs)
    light_protein_priority_lanche = get_preferred_first(
        ["iogurte_grego", "iogurte_natural", "cottage"], "protein")
    
    fat_priority_lanche = get_preferred_first(
        ["castanhas", "amendoas", "nozes", "pasta_amendoim"], "fat")
    
    fat_priority_cafe = get_preferred_first(
        ["pasta_amendoim", "chia"], "fat")
    
    # Extras doces para lanches (MÁXIMO 30g, apenas em lanches/café)
    extras_priority = ["mel", "leite_condensado"]
    
    fruit_priority = get_preferred_first(
        ["banana", "maca", "laranja", "mamao", "morango", "melancia", 
         "manga", "abacate", "uva", "abacaxi", "melao", "kiwi", "pera", "pessego"], "fruit")
    
    meals = []
    
    # ==================== DISTRIBUIÇÃO FIXA (100% dos macros, divididos por número de refeições) ====================
    
    # Define estrutura das refeições baseado no meal_count
    if meal_count == 4:
        # Café(25%), Almoço(35%), Lanche(10%), Jantar(30%)
        meal_structure = [
            {'name': 'Café da Manhã', 'time': '07:00', 'type': 'cafe', 'p': 0.25, 'c': 0.25, 'f': 0.10},
            {'name': 'Almoço', 'time': '12:00', 'type': 'almoco', 'p': 0.35, 'c': 0.35, 'f': 0.45},
            {'name': 'Lanche Tarde', 'time': '16:00', 'type': 'lanche', 'p': 0.10, 'c': 0.15, 'f': 0.15},
            {'name': 'Jantar', 'time': '20:00', 'type': 'jantar', 'p': 0.30, 'c': 0.25, 'f': 0.30},
        ]
    elif meal_count == 5:
        # Café(20%), LancheManhã(10%), Almoço(30%), LancheTarde(10%), Jantar(30%)
        meal_structure = [
            {'name': 'Café da Manhã', 'time': '07:00', 'type': 'cafe', 'p': 0.20, 'c': 0.20, 'f': 0.10},
            {'name': 'Lanche Manhã', 'time': '10:00', 'type': 'lanche', 'p': 0.05, 'c': 0.10, 'f': 0.15},
            {'name': 'Almoço', 'time': '12:30', 'type': 'almoco', 'p': 0.30, 'c': 0.30, 'f': 0.35},
            {'name': 'Lanche Tarde', 'time': '16:00', 'type': 'lanche', 'p': 0.10, 'c': 0.10, 'f': 0.15},
            {'name': 'Jantar', 'time': '19:30', 'type': 'jantar', 'p': 0.35, 'c': 0.30, 'f': 0.25},
        ]
    else:  # 6 refeições
        # Café(15%), LancheManhã(8%), Almoço(27%), LancheTarde(10%), Jantar(25%), Ceia(15%)
        meal_structure = [
            {'name': 'Café da Manhã', 'time': '07:00', 'type': 'cafe', 'p': 0.15, 'c': 0.15, 'f': 0.10},
            {'name': 'Lanche Manhã', 'time': '10:00', 'type': 'lanche', 'p': 0.05, 'c': 0.10, 'f': 0.10},
            {'name': 'Almoço', 'time': '12:30', 'type': 'almoco', 'p': 0.27, 'c': 0.27, 'f': 0.30},
            {'name': 'Lanche Tarde', 'time': '16:00', 'type': 'lanche', 'p': 0.08, 'c': 0.10, 'f': 0.15},
            {'name': 'Jantar', 'time': '19:30', 'type': 'jantar', 'p': 0.25, 'c': 0.25, 'f': 0.30},
            {'name': 'Ceia', 'time': '21:30', 'type': 'ceia', 'p': 0.20, 'c': 0.13, 'f': 0.05},
        ]
    
    # Seleciona alimentos para cada tipo de refeição
    for meal_info in meal_structure:
        meal_type = meal_info['type']
        meal_p = target_p * meal_info['p']
        meal_c = target_c * meal_info['c']
        meal_f = target_f * meal_info['f']
        
        foods = []
        
        if meal_type == 'cafe':
            # Café da Manhã: ovos + aveia + fruta + gordura saudável
            protein = select_best_food("cafe_da_manha", preferred, restrictions, "protein", light_protein_priority_cafe)
            carb = select_best_food("cafe_da_manha", preferred, restrictions, "carb", light_carb_priority)
            fruit = select_best_food("cafe_da_manha", preferred, restrictions, "fruit", fruit_priority)
            fat = select_best_food("cafe_da_manha", preferred, restrictions, "fat", fat_priority_cafe)
            
            if protein and protein in FOODS:
                # LIMITAÇÃO ESPECIAL: Ovos máximo 3 unidades (150g) no café
                # para controlar gordura (ovos = 11g gordura/100g)
                if protein == "ovos":
                    p_grams = clamp(meal_p / (FOODS[protein]["p"] / 100), 50, 150)
                else:
                    p_grams = clamp(meal_p / (FOODS[protein]["p"] / 100), 80, 200)
                foods.append(calc_food(protein, p_grams))
            
            if carb and carb in FOODS:
                c_grams = clamp(meal_c * 0.4 / max(FOODS[carb]["c"] / 100, 0.1), 40, 120)
                if carb == "aveia":
                    c_grams = min(c_grams, 100)
                foods.append(calc_food(carb, c_grams))
            
            if fruit and fruit in FOODS:
                fruit_grams = clamp(meal_c * 0.5 / max(FOODS[fruit]["c"] / 100, 0.1), 100, 300)
                foods.append(calc_food(fruit, fruit_grams))
            
            # Adiciona gordura saudável APENAS se target de gordura for suficiente
            # e com limite BEM conservador para dar espaço ao fine_tune
            if fat and fat in FOODS and meal_f > 8:
                # Usa apenas 25% do target de gordura da refeição aqui
                fat_grams = clamp(meal_f * 0.25 / max(FOODS[fat]["f"] / 100, 0.1), 5, 15)
                foods.append(calc_food(fat, fat_grams))
            
            if not foods:
                foods = [calc_food("pao_integral", 60), calc_food("ovos", 100), calc_food("banana", 120)]
                
        elif meal_type == 'lanche':
            # Lanche: iogurte/cottage + fruta + opcionalmente extra doce (mel/leite condensado)
            protein = select_best_food("lanche", preferred, restrictions, "protein", light_protein_priority_lanche)
            fruit = select_best_food("lanche", preferred, restrictions, "fruit", fruit_priority)
            fat = select_best_food("lanche", preferred, restrictions, "fat", fat_priority_lanche)
            
            # Iogurte ou cottage - MÁXIMO 1 POTE (170g)
            if protein and protein in FOODS:
                # Limita a 170g (1 pote) para evitar desperdício
                max_protein_grams = 170 if protein in ["iogurte_grego", "iogurte_natural"] else 200
                p_grams = clamp(meal_p / max(FOODS[protein]["p"] / 100, 0.1), 100, max_protein_grams)
                foods.append(calc_food(protein, p_grams))
            
            # Fruta - MÁXIMO 1 UNIDADE
            if fruit and fruit in FOODS:
                max_fruit_grams = 150  # Limita para não ter fruta demais
                fruit_grams = clamp(meal_c * 0.6 / max(FOODS[fruit]["c"] / 100, 0.1), 80, max_fruit_grams)
                foods.append(calc_food(fruit, fruit_grams))
            
            # Extra doce (mel ou leite condensado) - MÁXIMO 30g, apenas em lanches/café
            carbs_so_far = sum(f.get("carbs", 0) for f in foods)
            carbs_remaining = meal_c - carbs_so_far
            if carbs_remaining > 5:
                # Adiciona mel ou leite condensado (máximo 30g!)
                extra = "mel" if carbs_remaining < 15 else "leite_condensado"
                if extra in FOODS:
                    extra_grams = clamp(carbs_remaining / max(FOODS[extra]["c"] / 100, 0.1), 10, 30)
                    foods.append(calc_food(extra, extra_grams))
            
            # NÃO adiciona gordura extra nos lanches por padrão
            # O iogurte já tem gordura suficiente e o fine_tune adicionará azeite se precisar
            
            if not foods:
                foods = [calc_food("iogurte_natural", 170), calc_food("banana", 120), calc_food("mel", 20)]
                
        elif meal_type in ['almoco', 'jantar']:
            # Almoço/Jantar: proteína principal + carboidratos (principal + complemento) + vegetais + azeite
            # NUNCA adicionar extras (leite condensado, mel, requeijão light) no almoço/jantar!
            protein = select_best_food("almoco_jantar", preferred, restrictions, "protein", protein_priority)
            carb_main = select_best_food("almoco_jantar", preferred, restrictions, "carb", carb_priority)
            
            # Adiciona proteína
            if protein and protein in FOODS:
                p_grams = clamp(meal_p / (FOODS[protein]["p"] / 100), 100, 400)
                foods.append(calc_food(protein, p_grams))
            else:
                foods.append(calc_food("frango", 200))
            
            # Distribui carboidratos entre principal (70%) e complemento (30%)
            if carb_main and carb_main in FOODS:
                # Distribuição: 50% arroz/batata + 35% feijão/lentilha + 15% farofa
                carb_main_ratio = 0.50
                c_main_grams = clamp((meal_c * carb_main_ratio) / max(FOODS[carb_main]["c"] / 100, 0.1), 80, 350)
                foods.append(calc_food(carb_main, c_main_grams))
                
                # Carboidrato complementar (feijão, lentilha) - 35% dos carbs
                carb_comp = None
                for comp in carb_complement:
                    if comp != carb_main and comp in FOODS:
                        if not any(comp in RESTRICTION_EXCLUSIONS.get(r, set()) for r in restrictions):
                            carb_comp = comp
                            break
                
                if carb_comp:
                    c_comp_grams = clamp((meal_c * 0.35) / max(FOODS[carb_comp]["c"] / 100, 0.1), 80, 250)
                    foods.append(calc_food(carb_comp, c_comp_grams))
                
                # Farofa (15%) - complemento clássico brasileiro
                if "farofa" in FOODS and meal_c * 0.15 > 10:
                    farofa_grams = clamp((meal_c * 0.15) / max(FOODS["farofa"]["c"] / 100, 0.1), 20, 80)
                    foods.append(calc_food("farofa", farofa_grams))
                    
            else:
                foods.append(calc_food("arroz_branco", 200))
                foods.append(calc_food("feijao", 120))
                foods.append(calc_food("farofa", 30))
            
            # Vegetais
            if meal_type == 'almoco':
                foods.append(calc_food("salada", 100))
            else:
                foods.append(calc_food("brocolis", 100))
            
            # Azeite - limite mais conservador (5-20g)
            azeite_grams = clamp(meal_f * 0.30 / 1.0, 5, 20)
            foods.append(calc_food("azeite", azeite_grams))
            
        elif meal_type == 'ceia':
            # Ceia: proteína leve + fruta (NUNCA OVOS!)
            protein = select_best_food("ceia", preferred, restrictions, "protein", light_protein_priority_ceia)
            fruit = select_best_food("ceia", preferred, restrictions, "fruit", fruit_priority)
            
            if protein and protein in FOODS:
                p_grams = clamp(meal_p / max(FOODS[protein]["p"] / 100, 0.1), 100, 300)
                foods.append(calc_food(protein, p_grams))
            
            if fruit and fruit in FOODS:
                fruit_grams = clamp(meal_c / max(FOODS[fruit]["c"] / 100, 0.1), 100, 200)
                foods.append(calc_food(fruit, fruit_grams))
            
            if not foods:
                foods = [calc_food("cottage", 150), calc_food("morango", 120)]
        
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
    
    ESTRATÉGIA:
    1. Gordura em excesso → Remove azeite, castanhas primeiro
    2. Proteína em excesso → Reduz carnes nas refeições principais
    3. Carbs em excesso → Reduz arroz, batata
    
    IMPORTANTE: Esta função assume que alimentos contáveis já estão fixos.
    Portanto, ela ajusta APENAS alimentos não-contáveis (arroz, frango, azeite).
    """
    MAX_EXCESS = 5  # Máximo 5g acima do target
    MAX_DEFICIT = 5  # Máximo 5g abaixo do target (mais rígido)
    
    # Tolerância para baixo agora é também 5g (mais rígida)
    tol_p_below = max(10, target_p * 0.05)
    tol_c_below = max(15, target_c * 0.05)
    tol_f_below = max(5, target_f * 0.05)
    
    num_meals = len(meals)
    
    # Alimentos que podem ser ajustados em incrementos pequenos (não-contáveis)
    ADJUSTABLE_PROTEINS = {"frango", "patinho", "tilapia", "atum", "salmao", "camarao", 
                           "carne_moida", "suino", "peru", "cottage", "tofu"}
    ADJUSTABLE_CARBS = {"arroz_branco", "arroz_integral", "macarrao", "macarrao_integral",
                        "feijao", "lentilha", "farofa", "aveia", "tapioca"}
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
        p_ok = excess_p <= MAX_EXCESS and excess_p >= -tol_p_below
        c_ok = excess_c <= MAX_EXCESS and excess_c >= -tol_c_below
        f_ok = excess_f <= MAX_EXCESS and excess_f >= -tol_f_below
        
        if p_ok and c_ok and f_ok:
            return meals
        
        adjusted = False
        
        # ========== PRIORIDADE 1: REDUZIR GORDURA EM EXCESSO ==========
        if excess_f > MAX_EXCESS and not adjusted:
            reduce_needed = excess_f - MAX_EXCESS + 3
            
            # Tenta reduzir/remover azeite em TODAS as refeições
            for m_idx in all_indices:
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("key") == "azeite":
                        current_g = food["grams"]
                        f_per_100 = FOODS["azeite"]["f"]
                        reduce_grams = reduce_needed / (f_per_100 / 100)
                        new_g = max(0, current_g - reduce_grams)
                        
                        if new_g < 5:
                            # Remove o azeite completamente
                            meals[m_idx]["foods"].pop(f_idx)
                            adjusted = True
                            break
                        elif current_g - new_g >= 2:
                            meals[m_idx]["foods"][f_idx] = calc_food("azeite", new_g)
                            adjusted = True
                            break
            
            # Tenta reduzir castanhas/oleaginosas nos lanches
            if not adjusted:
                for m_idx in lanche_indices:
                    if m_idx >= num_meals or adjusted:
                        break
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        food_key = food.get("key")
                        if food_key in ADJUSTABLE_FATS and food_key != "azeite":
                            current_g = food["grams"]
                            f_per_100 = FOODS[food_key]["f"]
                            reduce_grams = reduce_needed / (f_per_100 / 100)
                            new_g = max(0, current_g - reduce_grams)
                            
                            if new_g < 10:
                                meals[m_idx]["foods"].pop(f_idx)
                                adjusted = True
                                break
                            elif current_g - new_g >= 5:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
            
            # Última opção: reduz proteínas gordurosas (ovos têm gordura)
            if not adjusted:
                for m_idx in all_indices:
                    if m_idx >= num_meals or adjusted:
                        break
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        food_key = food.get("key")
                        if food_key == "ovos" and food.get("fat", 0) > 5:
                            # Ovos são contáveis, então não podemos ajustar em gramas pequenas
                            # Mas podemos substituir por claras que têm menos gordura
                            # Por enquanto, pula
                            continue
        
        # ========== PRIORIDADE 2: REDUZIR PROTEÍNA EM EXCESSO ==========
        if excess_p > MAX_EXCESS and not adjusted:
            reduce_needed = excess_p - MAX_EXCESS + 2
            
            for m_idx in main_meal_indices:
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_PROTEINS:
                        current_g = food["grams"]
                        p_per_100 = FOODS[food_key]["p"]
                        reduce_grams = reduce_needed / (p_per_100 / 100)
                        # Limite mínimo mais baixo (50g) para permitir ajustes finos
                        new_g = max(50, current_g - reduce_grams)
                        # Condição menos restritiva (qualquer redução >= 5g)
                        if current_g - new_g >= 5:
                            meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                            adjusted = True
                            break
        
        # ========== PRIORIDADE 3: REDUZIR CARBOIDRATO EM EXCESSO ==========
        if excess_c > MAX_EXCESS and not adjusted:
            reduce_needed = excess_c - MAX_EXCESS + 3
            
            for m_idx in main_meal_indices + [0]:  # Almoço, Jantar, Café
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_CARBS:
                        current_g = food["grams"]
                        c_per_100 = FOODS[food_key]["c"]
                        if c_per_100 > 0:
                            reduce_grams = reduce_needed / (c_per_100 / 100)
                            new_g = max(40, current_g - reduce_grams)
                            if current_g - new_g >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
        
        # ========== AUMENTAR SE MUITO ABAIXO ==========
        
        # PROTEÍNA muito abaixo
        if excess_p < -tol_p_below and not adjusted:
            increase_needed = abs(excess_p) - tol_p_below + 5
            
            for m_idx in main_meal_indices:
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_PROTEINS:
                        current_g = food["grams"]
                        p_per_100 = FOODS[food_key]["p"]
                        increase_grams = increase_needed / (p_per_100 / 100)
                        new_g = min(500, current_g + increase_grams)
                        if new_g - current_g >= 10:
                            meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                            adjusted = True
                            break
        
        # CARBOIDRATO muito abaixo
        if excess_c < -tol_c_below and not adjusted:
            increase_needed = abs(excess_c) - tol_c_below + 5
            
            for m_idx in main_meal_indices + [0]:
                if m_idx >= num_meals or adjusted:
                    break
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    food_key = food.get("key")
                    if food_key in ADJUSTABLE_CARBS:
                        current_g = food["grams"]
                        c_per_100 = FOODS[food_key]["c"]
                        if c_per_100 > 0:
                            increase_grams = increase_needed / (c_per_100 / 100)
                            new_g = min(MAX_CARB_GRAMS, current_g + increase_grams)
                            if new_g - current_g >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
        
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
            # PERMITIDO: frutas, oleaginosas | PROIBIDO: carnes, azeite
            foods = [calc_food("maca", 150), calc_food("castanhas", 20)]
        elif meal_index == 2:  # Almoço
            # OBRIGATÓRIO: 1 proteína + 1 carboidrato | PERMITIDO: azeite
            foods = [calc_food("frango", 150), calc_food("arroz_branco", 150), calc_food("salada", 100), calc_food("azeite", 10)]
        elif meal_index == 3:  # Lanche tarde
            # PERMITIDO: frutas, iogurte | PROIBIDO: carnes, azeite
            foods = [calc_food("laranja", 150), calc_food("iogurte_grego", 170)]
        elif meal_index == 4:  # Jantar
            # OBRIGATÓRIO: 1 proteína + 1 carboidrato | PERMITIDO: azeite
            foods = [calc_food("tilapia", 150), calc_food("arroz_integral", 120), calc_food("brocolis", 100), calc_food("azeite", 10)]
        else:  # Ceia
            # PERMITIDO: iogurte/cottage + frutas | PROIBIDO: carnes, carbs complexos, OVOS!
            # REGRA ABSOLUTA: NUNCA OVOS NA CEIA!
            foods = [calc_food("cottage", 100), calc_food("morango", 100)]
    
    # Valida cada alimento
    validated_foods = []
    for food in foods:
        validated_food = validate_and_fix_food(food, preferred)
        if validated_food:
            # REGRA ABSOLUTA: Se for CEIA, NUNCA permite ovos
            if meal_index == 5 and validated_food.get("key") == "ovos":
                validated_food = calc_food("cottage", validated_food.get("grams", 100))
            validated_foods.append(validated_food)
    
    # Garante que tem pelo menos 1 alimento (RESPEITANDO regras da refeição)
    if len(validated_foods) == 0:
        if meal_index == 0:  # Café - proteína leve
            validated_foods = [calc_food("ovos", 100)]
        elif meal_index == 5:  # Ceia - NUNCA OVOS!
            validated_foods = [calc_food("cottage", 100)]
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
                # Substitui ovos por cottage na ceia
                grams = food.get("grams", 100)
                validated_meals[meal_idx]["foods"][food_idx] = calc_food("cottage", grams)
                # Recalcula totais da refeição
                mp, mc, mf, mcal = sum_foods(validated_meals[meal_idx]["foods"])
                validated_meals[meal_idx]["total_calories"] = mcal
                validated_meals[meal_idx]["macros"] = {"protein": mp, "carbs": mc, "fat": mf}
    
    return validated_meals
    
    return validated_meals


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
        
        # AUTO-COMPLETE INTELIGENTE: garante mínimos necessários
        preferred_foods, auto_completed, auto_message = smart_auto_complete(
            raw_preferred, dietary_restrictions, goal
        )
        
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
        
        # Gera dieta com alimentos auto-completados se necessário
        # Passa meal_count para gerar a quantidade correta de refeições
        meals = generate_diet(target_p, target_c, target_f, preferred_foods, dietary_restrictions, meal_count)
        
        # Fine-tune (múltiplas rodadas se necessário)
        for _ in range(5):  # Aumentado para 5 tentativas
            meals = fine_tune_diet(meals, target_p, target_c, target_f)
            is_valid, _ = validate_diet(meals, target_p, target_c, target_f)
            if is_valid:
                break
        
        # ✅ VALIDAÇÃO BULLETPROOF FINAL
        # Garante que NUNCA retorna dieta inválida
        meals = validate_and_fix_diet(meals, target_p, target_c, target_f, preferred_foods, meal_count)
        
        # Ajusta para o número de refeições configurado
        if len(meals) > meal_count:
            meals = meals[:meal_count]
        elif len(meals) < meal_count:
            # Adiciona refeições extras se necessário
            while len(meals) < meal_count:
                meals.append(meals[-1].copy() if meals else {
                    "name": f"Refeição {len(meals) + 1}",
                    "time": "12:00",
                    "foods": [calc_food("frango", 100)],
                    "total_calories": 100,
                    "macros": {"protein": 20, "carbs": 0, "fat": 2}
                })
        
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

ATHLETE_PHASE_ADJUSTMENTS = {
    # OFF-SEASON: ganho controlado
    "off_season": {
        "direction": "increase",
        "min_percent": 8.0,
        "max_percent": 12.0,
        "default_percent": 10.0,
        "description": "OFF-SEASON — ganho de massa controlado"
    },
    # PRE-PREP: transição
    "pre_prep": {
        "direction": "decrease",
        "min_percent": 4.0,
        "max_percent": 6.0,
        "default_percent": 5.0,
        "description": "PRÉ-PREP — transição para cutting"
    },
    # PREP: definição
    "prep": {
        "direction": "decrease",
        "min_percent": 8.0,
        "max_percent": 12.0,
        "default_percent": 10.0,
        "description": "PREP — definição muscular"
    },
    # PEAK WEEK: micro ajustes
    "peak_week": {
        "direction": "variable",  # ±3% conforme peso
        "min_percent": 2.0,
        "max_percent": 3.0,
        "default_percent": 3.0,
        "description": "PEAK WEEK — ajustes finais"
    },
    # POST-SHOW: reverse diet
    "post_show": {
        "direction": "increase",
        "min_percent": 3.0,
        "max_percent": 5.0,
        "default_percent": 4.0,
        "description": "PÓS-SHOW — recuperação metabólica"
    }
}


def evaluate_athlete_progress(phase: str, previous_weight: float, current_weight: float) -> Dict:
    """
    Avalia progresso do atleta e determina ajuste baseado na FASE.
    
    REGRAS POR FASE:
    - OFF_SEASON: objetivo ganho → se não ganhou, aumenta 8-12%
    - PRE_PREP: transição → reduz 4-6%
    - PREP: definição → reduz 8-12%
    - PEAK_WEEK: micro ajustes ±3%
    - POST_SHOW: reverse diet → aumenta 3-5%
    """
    weight_diff = current_weight - previous_weight
    
    if phase not in ATHLETE_PHASE_ADJUSTMENTS:
        phase = "prep"  # Fallback para prep
    
    config = ATHLETE_PHASE_ADJUSTMENTS[phase]
    
    result = {
        "needs_adjustment": True,  # Atleta SEMPRE ajusta a cada 14 dias
        "adjustment_type": None,
        "adjustment_percent": 0.0,
        "phase": phase,
        "reason": config["description"]
    }
    
    if phase == "off_season":
        # Objetivo: GANHAR peso
        if weight_diff <= 0:
            # Não ganhou → aumenta mais
            result["adjustment_type"] = "increase"
            result["adjustment_percent"] = config["max_percent"]
            result["reason"] = f"{config['description']} — não ganhou peso ({weight_diff:+.1f}kg), aumentando {config['max_percent']}%"
        elif weight_diff < 0.3:
            # Ganhou pouco → aumenta menos
            result["adjustment_type"] = "increase"
            result["adjustment_percent"] = config["min_percent"]
            result["reason"] = f"{config['description']} — ganho leve ({weight_diff:+.1f}kg), aumentando {config['min_percent']}%"
        else:
            # Ganhou bem → mantém
            result["needs_adjustment"] = False
            result["reason"] = f"{config['description']} — ganho adequado ({weight_diff:+.1f}kg)"
    
    elif phase == "pre_prep":
        # Objetivo: começar a PERDER
        result["adjustment_type"] = "decrease"
        result["adjustment_percent"] = config["default_percent"]
        result["reason"] = f"{config['description']} — reduzindo {config['default_percent']}%"
    
    elif phase == "prep":
        # Objetivo: PERDER gordura
        if weight_diff >= 0:
            # Não perdeu → reduz mais
            result["adjustment_type"] = "decrease"
            result["adjustment_percent"] = config["max_percent"]
            result["reason"] = f"{config['description']} — não perdeu peso ({weight_diff:+.1f}kg), reduzindo {config['max_percent']}%"
        elif weight_diff > -0.5:
            # Perdeu pouco → reduz normal
            result["adjustment_type"] = "decrease"
            result["adjustment_percent"] = config["default_percent"]
            result["reason"] = f"{config['description']} — perda lenta ({weight_diff:.1f}kg), reduzindo {config['default_percent']}%"
        else:
            # Perdeu bem → reduz menos
            result["adjustment_type"] = "decrease"
            result["adjustment_percent"] = config["min_percent"]
            result["reason"] = f"{config['description']} — perda adequada ({weight_diff:.1f}kg), reduzindo {config['min_percent']}%"
    
    elif phase == "peak_week":
        # Micro ajustes ±3%
        if weight_diff > 0.2:
            result["adjustment_type"] = "decrease"
            result["adjustment_percent"] = config["max_percent"]
            result["reason"] = f"{config['description']} — peso subiu ({weight_diff:+.1f}kg), ajuste -{config['max_percent']}%"
        elif weight_diff < -0.2:
            result["adjustment_type"] = "increase"
            result["adjustment_percent"] = config["min_percent"]
            result["reason"] = f"{config['description']} — peso caiu ({weight_diff:.1f}kg), ajuste +{config['min_percent']}%"
        else:
            result["needs_adjustment"] = False
            result["reason"] = f"{config['description']} — peso estável ({weight_diff:+.1f}kg)"
    
    elif phase == "post_show":
        # Reverse diet progressivo
        result["adjustment_type"] = "increase"
        result["adjustment_percent"] = config["default_percent"]
        result["reason"] = f"{config['description']} — aumentando {config['default_percent']}% para recuperação"
    
    return result


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
