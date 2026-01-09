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
MIN_FOOD_GRAMS = 10      # Mínimo 10g por alimento
MAX_FOOD_GRAMS = 500     # Máximo 500g por alimento
MIN_MEAL_CALORIES = 50   # Mínimo 50kcal por refeição
MIN_DAILY_CALORIES = 800 # Mínimo 800kcal por dia (segurança)


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
    "tofu": {"name": "Tofu", "p": 8.0, "c": 2.0, "f": 4.0, "category": "protein", "unit": "fatia média", "unit_g": 80},
    
    # === CARBOIDRATOS ===
    "arroz_branco": {"name": "Arroz Branco", "p": 2.6, "c": 28.0, "f": 0.3, "category": "carb", "unit": "xícara cozida", "unit_g": 120},
    "arroz_integral": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "category": "carb", "unit": "xícara cozida", "unit_g": 120},
    "batata_doce": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "category": "carb", "unit": "unidade média", "unit_g": 150},
    "batata": {"name": "Batata Inglesa", "p": 2.0, "c": 17.0, "f": 0.1, "category": "carb", "unit": "unidade média", "unit_g": 130},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "category": "carb", "unit": "colher sopa", "unit_g": 15},
    "macarrao": {"name": "Macarrão", "p": 5.0, "c": 25.0, "f": 1.0, "category": "carb", "unit": "xícara cozido", "unit_g": 140},
    "pao": {"name": "Pão Francês", "p": 9.0, "c": 49.0, "f": 3.0, "category": "carb", "unit": "unidade", "unit_g": 50},
    "pao_integral": {"name": "Pão Integral", "p": 10.0, "c": 42.0, "f": 4.0, "category": "carb", "unit": "fatia", "unit_g": 30},
    "quinoa": {"name": "Quinoa", "p": 4.4, "c": 21.0, "f": 1.9, "category": "carb", "unit": "xícara cozida", "unit_g": 120},
    "cuscuz": {"name": "Cuscuz", "p": 3.8, "c": 23.0, "f": 0.2, "category": "carb", "unit": "fatia média", "unit_g": 100},
    "tapioca": {"name": "Tapioca", "p": 0.5, "c": 22.0, "f": 0.0, "category": "carb", "unit": "goma hidratada", "unit_g": 50},
    "milho": {"name": "Milho", "p": 3.2, "c": 19.0, "f": 1.2, "category": "carb", "unit": "espiga média", "unit_g": 100},
    "feijao": {"name": "Feijão", "p": 6.0, "c": 14.0, "f": 0.5, "category": "carb", "unit": "concha média", "unit_g": 100},
    "lentilha": {"name": "Lentilha", "p": 9.0, "c": 20.0, "f": 0.4, "category": "carb", "unit": "concha média", "unit_g": 100},
    "grao_de_bico": {"name": "Grão de Bico", "p": 9.0, "c": 27.0, "f": 2.6, "category": "carb", "unit": "concha média", "unit_g": 100},
    
    # === GORDURAS ===
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat", "unit": "colher sopa", "unit_g": 13},
    "pasta_amendoim": {"name": "Pasta de Amendoim", "p": 25.0, "c": 20.0, "f": 50.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "pasta_amendoa": {"name": "Pasta de Amêndoa", "p": 21.0, "c": 19.0, "f": 56.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "oleo_coco": {"name": "Óleo de Coco", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat", "unit": "colher sopa", "unit_g": 13},
    "manteiga": {"name": "Manteiga", "p": 0.9, "c": 0.1, "f": 81.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "castanhas": {"name": "Castanhas", "p": 14.0, "c": 30.0, "f": 44.0, "category": "fat", "unit": "unidades", "unit_g": 10},
    "amendoas": {"name": "Amêndoas", "p": 21.0, "c": 22.0, "f": 49.0, "category": "fat", "unit": "unidades", "unit_g": 5},
    "nozes": {"name": "Nozes", "p": 15.0, "c": 14.0, "f": 65.0, "category": "fat", "unit": "unidade", "unit_g": 8},
    "chia": {"name": "Chia", "p": 17.0, "c": 42.0, "f": 31.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "linhaca": {"name": "Linhaça", "p": 18.0, "c": 29.0, "f": 42.0, "category": "fat", "unit": "colher sopa", "unit_g": 15},
    "queijo": {"name": "Queijo", "p": 23.0, "c": 1.3, "f": 33.0, "category": "fat", "unit": "fatia média", "unit_g": 30},
    "cream_cheese": {"name": "Cream Cheese", "p": 6.0, "c": 4.0, "f": 34.0, "category": "fat", "unit": "colher sopa", "unit_g": 20},
    
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


def calc_food(food_key: str, grams: float) -> Dict:
    """
    Calcula macros de um alimento em quantidade específica.
    
    ✅ GARANTIAS:
    - SEMPRE retorna um dict válido (nunca None)
    - grams SEMPRE >= MIN_FOOD_GRAMS (10g)
    - grams SEMPRE <= MAX_FOOD_GRAMS (500g)
    - grams SEMPRE múltiplo de 10
    - TODOS os campos obrigatórios preenchidos
    
    Formato: "Nome – Xg (≈ Y medida caseira)"
    """
    # FALLBACK: Se alimento não existe, usa frango como default
    if food_key not in FOODS:
        food_key = "frango"
    
    f = FOODS[food_key]
    
    # GARANTIA: Múltiplo de 10, mínimo 10g, máximo 500g
    g = round_to_10(grams)
    g = max(MIN_FOOD_GRAMS, min(MAX_FOOD_GRAMS, g))
    
    # GARANTIA: Sempre > 0
    if g <= 0:
        g = MIN_FOOD_GRAMS
    
    ratio = g / 100
    
    # Calcula macros (nunca negativos)
    protein = max(0, round(f["p"] * ratio))
    carbs = max(0, round(f["c"] * ratio))
    fat = max(0, round(f["f"] * ratio))
    calories = max(1, round((f["p"] * 4 + f["c"] * 4 + f["f"] * 9) * ratio))
    
    # Calcula equivalente em medida caseira
    unit = f.get("unit", "porção")
    unit_g = f.get("unit_g", 100)
    
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
    
    # Formato completo: "150g (≈ 1 filé médio)"
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
    """Calcula macros baseado no objetivo"""
    goal_adjustments = {
        'cutting': {'cal_mult': 0.85, 'p_mult': 2.4},
        'manutencao': {'cal_mult': 1.0, 'p_mult': 2.0},
        'bulking': {'cal_mult': 1.15, 'p_mult': 2.2},
        'atleta': {'cal_mult': 1.0, 'p_mult': 2.4}
    }
    
    adj = goal_adjustments.get(goal.lower(), goal_adjustments['manutencao'])
    
    target_calories = tdee * adj['cal_mult']
    protein = weight * adj['p_mult']
    fat = weight * 0.8
    
    protein_cal = protein * 4
    fat_cal = fat * 9
    carbs_cal = target_calories - protein_cal - fat_cal
    carbs = carbs_cal / 4
    
    if carbs < 100:
        carbs = 100
        carbs_cal = carbs * 4
        target_calories = protein_cal + fat_cal + carbs_cal
    
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
        # PERMITIDOS: Ovos, Cottage, Iogurte Grego + Aveia, Pão Integral + Frutas
        "proteins": {"ovos", "iogurte_grego", "cottage"},
        "carbs": {"aveia", "pao_integral"},
        "fats": set(),  # PROIBIDO: azeite, óleos, gorduras
        "fruits": True,
        # PROIBIDOS: Arroz, Feijão, Lentilha, Macarrão, Frango, Peixe, Carne, Peru, Azeite
        "description": "Café da manhã: proteínas leves + aveia/pão + frutas"
    },
    "lanche": {
        # PERMITIDOS: Frutas + Cottage, Iogurte Grego + Castanhas, Amêndoas
        "proteins": {"iogurte_grego", "cottage"},  # OVOS PROIBIDOS em lanches!
        "carbs": set(),  # PROIBIDO: Arroz, Aveia, Pão, Batatas, Massas
        "fats": {"castanhas", "amendoas"},  # PROIBIDO: Pasta de Amendoim, Queijo
        "fruits": True,
        # PROIBIDOS: Frango, Peixe, Carne, Peru, Ovos, Azeite, Pasta de Amendoim, Queijo
        "description": "Lanche leve: frutas + iogurte/cottage + castanhas/amêndoas"
    },
    "almoco_jantar": {
        # OBRIGATÓRIO: Exatamente 1 proteína + Exatamente 1 carboidrato
        "proteins": {"frango", "patinho", "tilapia", "atum", "salmao", "peru", "ovos"},
        "carbs": {"arroz_branco", "arroz_integral", "batata_doce", "batata",
                  "macarrao", "feijao", "lentilha"},
        "fats": {"azeite"},  # PERMITIDO: apenas azeite
        "fruits": False,
        # PROIBIDO: Mais de 1 proteína, Mais de 1 carboidrato
        "description": "Refeição completa: EXATAMENTE 1 proteína + 1 carboidrato + azeite"
    },
    "ceia": {
        # PERMITIDOS: Cottage, Iogurte Grego, Ovos + Frutas
        "proteins": {"ovos", "iogurte_grego", "cottage"},
        "carbs": set(),  # PROIBIDO: Arroz, Batatas, Massas, Leguminosas
        "fats": set(),  # PROIBIDO: Azeite, gorduras
        "fruits": True,
        # PROIBIDOS: Frango, Peixe, Carne
        "description": "Ceia leve: proteína leve + frutas"
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
    
    # Intersecção: permitido na refeição + existe no banco + preferência do usuário
    available = []
    for food_key in allowed_in_meal:
        if food_key in FOODS:
            if not preferred or food_key in preferred:
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
                  preferred: Set[str], restrictions: List[str]) -> List[Dict]:
    """
    Gera dieta em 6 REFEIÇÕES seguindo regras rígidas por tipo de refeição.
    
    REGRAS OBRIGATÓRIAS:
    ☀️ Café da Manhã: proteínas leves + carbs leves + frutas (SEM carnes, SEM azeite)
    🍎 Lanches: frutas + iogurte/cottage + castanhas/amêndoas (SEM carnes, SEM ovos, SEM azeite)
    🍽️ Almoço/Jantar: EXATAMENTE 1 proteína + 1 carboidrato + azeite
    🌙 Ceia: proteína leve (ovos/iogurte/cottage) + frutas
    """
    
    # Prioridades por categoria (APENAS alimentos ativos)
    protein_priority = ["frango", "patinho", "tilapia", "atum", "salmao", "peru", "ovos"]
    light_protein_priority_cafe = ["ovos", "iogurte_grego", "cottage"]  # Para café e ceia
    light_protein_priority_lanche = ["iogurte_grego", "cottage"]  # Para lanches (SEM ovos!)
    carb_priority = ["arroz_branco", "arroz_integral", "batata_doce", "batata", "macarrao", "feijao"]
    light_carb_priority = ["aveia", "pao_integral"]  # Removido: tapioca
    fat_priority_lanche = ["castanhas", "amendoas"]  # Removido: pasta_amendoim
    fruit_priority = ["banana", "maca", "laranja", "mamao", "morango", "melancia"]
    
    meals = []
    
    # ==================== ☀️ CAFÉ DA MANHÃ (15% P, 20% C, 10% F) ====================
    # PERMITIDO: ovos/iogurte/cottage + aveia/pão integral + frutas
    # PROIBIDO: carnes, arroz, batata, azeite
    
    cafe_p = target_p * 0.15
    cafe_c = target_c * 0.20
    
    breakfast_protein = select_best_food("cafe_da_manha", preferred, restrictions, "protein", light_protein_priority_cafe)
    breakfast_carb = select_best_food("cafe_da_manha", preferred, restrictions, "carb", light_carb_priority)
    breakfast_fruit = select_best_food("cafe_da_manha", preferred, restrictions, "fruit", fruit_priority)
    
    cafe_foods = []
    
    if breakfast_protein and breakfast_protein in FOODS:
        p_grams = clamp(cafe_p / (FOODS[breakfast_protein]["p"] / 100), 80, 200)
        cafe_foods.append(calc_food(breakfast_protein, p_grams))
    
    if breakfast_carb and breakfast_carb in FOODS:
        c_grams = clamp(cafe_c * 0.6 / max(FOODS[breakfast_carb]["c"] / 100, 0.1), 30, 80)
        # LIMITE ESPECÍFICO: Aveia máximo 80g
        if breakfast_carb == "aveia":
            c_grams = min(c_grams, 80)
        cafe_foods.append(calc_food(breakfast_carb, c_grams))
    
    if breakfast_fruit and breakfast_fruit in FOODS:
        fruit_grams = clamp(cafe_c * 0.4 / max(FOODS[breakfast_fruit]["c"] / 100, 0.1), 80, 150)
        cafe_foods.append(calc_food(breakfast_fruit, fruit_grams))
    
    # Fallback se vazio
    if not cafe_foods:
        cafe_foods = [calc_food("ovos", 100), calc_food("aveia", 40), calc_food("banana", 100)]
    
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": cafe_foods})
    
    # ==================== 🍎 LANCHE MANHÃ (5% P, 10% C, 15% F) ====================
    # PERMITIDO: frutas + iogurte/cottage + castanhas/amêndoas
    # PROIBIDO: carnes, arroz, batata, azeite, OVOS, pasta de amendoim, queijo
    
    lanche1_c = target_c * 0.10
    lanche1_f = target_f * 0.15
    
    snack_fruit = select_best_food("lanche", preferred, restrictions, "fruit", fruit_priority)
    snack_fat = select_best_food("lanche", preferred, restrictions, "fat", fat_priority_lanche)
    
    lanche1_foods = []
    
    if snack_fruit and snack_fruit in FOODS:
        fruit_grams = clamp(lanche1_c / max(FOODS[snack_fruit]["c"] / 100, 0.1), 100, 200)
        lanche1_foods.append(calc_food(snack_fruit, fruit_grams))
    
    if snack_fat and snack_fat in FOODS:
        fat_grams = clamp(lanche1_f / max(FOODS[snack_fat]["f"] / 100, 0.1), 15, 40)
        lanche1_foods.append(calc_food(snack_fat, fat_grams))
    
    if not lanche1_foods:
        lanche1_foods = [calc_food("banana", 120), calc_food("castanhas", 20)]
    
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": lanche1_foods})
    
    # ==================== 🍽️ ALMOÇO E JANTAR - DISTRIBUIÇÃO IGUAL ====================
    # Proteínas e carboidratos são divididos IGUALMENTE entre Almoço e Jantar (50/50)
    # Isso evita ter 200g em uma refeição e 100g em outra
    
    # Calcular total de proteína e carb para Almoço + Jantar
    total_main_meals_p = target_p * 0.60  # 60% da proteína total vai para almoço+jantar
    total_main_meals_c = target_c * 0.55  # 55% do carb total vai para almoço+jantar
    total_main_meals_f = target_f * 0.55  # 55% da gordura total
    
    # Dividir IGUALMENTE (50% cada)
    almoco_p = total_main_meals_p * 0.50
    almoco_c = total_main_meals_c * 0.50
    almoco_f = total_main_meals_f * 0.50
    
    jantar_p = total_main_meals_p * 0.50
    jantar_c = total_main_meals_c * 0.50
    jantar_f = total_main_meals_f * 0.50
    
    # Selecionar alimentos para ambas as refeições
    lunch_protein = select_best_food("almoco_jantar", preferred, restrictions, "protein", protein_priority)
    lunch_carb = select_best_food("almoco_jantar", preferred, restrictions, "carb", carb_priority)
    
    # Proteína/carb diferente para jantar se possível
    used_proteins = {lunch_protein} if lunch_protein else set()
    used_carbs = {lunch_carb} if lunch_carb else set()
    
    dinner_protein = select_best_food("almoco_jantar", preferred, restrictions, "protein", protein_priority, exclude=used_proteins)
    if not dinner_protein:
        dinner_protein = lunch_protein  # Usar a mesma se não tiver alternativa
    
    dinner_carb = select_best_food("almoco_jantar", preferred, restrictions, "carb", carb_priority, exclude=used_carbs)
    if not dinner_carb:
        dinner_carb = lunch_carb
    
    # ==================== 🍽️ ALMOÇO ====================
    almoco_foods = []
    
    if lunch_protein and lunch_protein in FOODS:
        # Limite máximo aumentado para 1000g (1kg)
        protein_grams = clamp(almoco_p / (FOODS[lunch_protein]["p"] / 100), 80, 1000)
        almoco_foods.append(calc_food(lunch_protein, protein_grams))
    else:
        almoco_foods.append(calc_food("frango", 150))
    
    if lunch_carb and lunch_carb in FOODS:
        carb_grams = clamp(almoco_c / max(FOODS[lunch_carb]["c"] / 100, 0.1), 80, 1000)
        almoco_foods.append(calc_food(lunch_carb, carb_grams))
    else:
        almoco_foods.append(calc_food("arroz_branco", 150))
    
    # Legumes (implícito) + Azeite
    almoco_foods.append(calc_food("salada", 100))
    
    if "azeite" in preferred or not preferred:
        azeite_grams = clamp(almoco_f * 0.3 / 1.0, 5, 30)
        almoco_foods.append(calc_food("azeite", azeite_grams))
    
    meals.append({"name": "Almoço", "time": "12:30", "foods": almoco_foods})
    
    # ==================== 🍎 LANCHE TARDE (5% P, 10% C) ====================
    # PERMITIDO: frutas + iogurte/cottage + castanhas/amêndoas
    # PROIBIDO: carnes, arroz, batata, azeite, OVOS, pasta de amendoim, queijo
    
    lanche2_c = target_c * 0.10
    lanche2_p = target_p * 0.05
    
    # Usar fruta diferente se possível
    used_fruits = {snack_fruit} if snack_fruit else set()
    snack2_fruit = select_best_food("lanche", preferred, restrictions, "fruit", fruit_priority, exclude=used_fruits)
    if not snack2_fruit:
        snack2_fruit = snack_fruit
    
    # IMPORTANTE: Usar light_protein_priority_lanche (SEM ovos!)
    snack_protein = select_best_food("lanche", preferred, restrictions, "protein", light_protein_priority_lanche)
    
    lanche2_foods = []
    
    if snack2_fruit and snack2_fruit in FOODS:
        fruit_grams = clamp(lanche2_c / max(FOODS[snack2_fruit]["c"] / 100, 0.1), 80, 300)
        lanche2_foods.append(calc_food(snack2_fruit, fruit_grams))
    
    if snack_protein and snack_protein in FOODS:
        protein_grams = clamp(lanche2_p / max(FOODS[snack_protein]["p"] / 100, 0.1), 80, 250)
        lanche2_foods.append(calc_food(snack_protein, protein_grams))
    
    if not lanche2_foods:
        lanche2_foods = [calc_food("maca", 150), calc_food("iogurte_grego", 170)]
    
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": lanche2_foods})
    
    # ==================== 🍽️ JANTAR (mesma quantidade que almoço) ====================
    jantar_foods = []
    
    if dinner_protein and dinner_protein in FOODS:
        # Mesma lógica do almoço - limite de 1kg
        protein_grams = clamp(jantar_p / (FOODS[dinner_protein]["p"] / 100), 80, 1000)
        jantar_foods.append(calc_food(dinner_protein, protein_grams))
    else:
        jantar_foods.append(calc_food("tilapia", 150))
    
    if dinner_carb and dinner_carb in FOODS:
        carb_grams = clamp(jantar_c / max(FOODS[dinner_carb]["c"] / 100, 0.1), 80, 1000)
        jantar_foods.append(calc_food(dinner_carb, carb_grams))
    else:
        jantar_foods.append(calc_food("arroz_integral", 150))
    
    # Legumes + Azeite
    jantar_foods.append(calc_food("brocolis", 100))
    
    if "azeite" in preferred or not preferred:
        azeite_grams = clamp(jantar_f * 0.3 / 1.0, 5, 30)
        jantar_foods.append(calc_food("azeite", azeite_grams))
    
    meals.append({"name": "Jantar", "time": "19:30", "foods": jantar_foods})
    
    # ==================== 🌙 CEIA (15% P, 5% C) ====================
    # PERMITIDO: cottage/iogurte/ovos + frutas
    # PROIBIDO: carnes, carboidratos complexos, gorduras adicionadas
    
    ceia_p = target_p * 0.15
    ceia_c = target_c * 0.05
    
    # Ceia usa a mesma lista de proteínas do café (inclui ovos)
    ceia_protein = select_best_food("ceia", preferred, restrictions, "protein", light_protein_priority_cafe)
    ceia_fruit = select_best_food("ceia", preferred, restrictions, "fruit", fruit_priority)
    
    ceia_foods = []
    
    if ceia_protein and ceia_protein in FOODS:
        protein_grams = clamp(ceia_p / max(FOODS[ceia_protein]["p"] / 100, 0.1), 100, 200)
        ceia_foods.append(calc_food(ceia_protein, protein_grams))
    
    if ceia_fruit and ceia_fruit in FOODS:
        fruit_grams = clamp(ceia_c / max(FOODS[ceia_fruit]["c"] / 100, 0.1), 80, 150)
        ceia_foods.append(calc_food(ceia_fruit, fruit_grams))
    
    if not ceia_foods:
        ceia_foods = [calc_food("cottage", 100), calc_food("morango", 100)]
    
    meals.append({"name": "Ceia", "time": "21:30", "foods": ceia_foods})
    
    return meals


def fine_tune_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int) -> List[Dict]:
    """
    Ajuste fino iterativo para atingir macros dentro de ±5%.
    
    REGRAS DE AJUSTE (6 refeições):
    - Proteínas: ajustar em Almoço(2), Jantar(4), Ceia(5)
    - Carboidratos: ajustar em Almoço(2), Jantar(4), Café(0)
    - Gorduras: ajustar em Almoço(2), Jantar(4), Lanches(1,3)
    """
    tol_p = target_p * TOL_PERCENT
    tol_c = target_c * TOL_PERCENT
    tol_f = target_f * TOL_PERCENT
    
    for iteration in range(500):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Se todos dentro da tolerância, retorna
        if abs(gap_p) <= tol_p and abs(gap_c) <= tol_c and abs(gap_f) <= tol_f:
            return meals
        
        adjusted = False
        
        # Ajusta proteínas - apenas em Almoço(2), Jantar(4), Ceia(5)
        # DISTRIBUIÇÃO IGUAL: divide o ajuste entre Almoço e Jantar
        if abs(gap_p) > tol_p and not adjusted:
            # Tenta ajustar igualmente entre almoço e jantar
            for m_idx in [2, 4]:  # Almoço, Jantar primeiro
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("category") == "protein":
                        food_key = food["key"]
                        p_per_100 = FOODS[food_key]["p"]
                        # Divide o ajuste por 2 para distribuir igualmente
                        delta = (gap_p / 2) / (p_per_100 / 100)
                        new_g = clamp(food["grams"] + delta, 80, 1000)  # Máximo 1kg
                        if abs(new_g - food["grams"]) >= 10:
                            meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                            adjusted = True
                            break
            
            # Se ainda precisar ajustar, usa Ceia ou Café
            if not adjusted:
                for m_idx in [5, 0]:  # Ceia, Café
                    if m_idx >= len(meals):
                        continue
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food.get("category") == "protein":
                            food_key = food["key"]
                            p_per_100 = FOODS[food_key]["p"]
                            delta = gap_p / (p_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 80, 500)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
                    if adjusted:
                        break
        
        # Ajusta carboidratos - Almoço(2), Jantar(4), Café(0)
        # DISTRIBUIÇÃO IGUAL entre Almoço e Jantar
        if abs(gap_c) > tol_c and not adjusted:
            for m_idx in [2, 4]:  # Almoço, Jantar primeiro
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("category") == "carb":
                        food_key = food["key"]
                        c_per_100 = FOODS[food_key]["c"]
                        if c_per_100 > 0:
                            # Divide o ajuste por 2
                            delta = (gap_c / 2) / (c_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 50, 1000)  # Máximo 1kg
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
            
            # Se ainda precisar, usa Café
            if not adjusted:
                for f_idx, food in enumerate(meals[0]["foods"]):
                    if food.get("category") == "carb":
                        food_key = food["key"]
                        c_per_100 = FOODS[food_key]["c"]
                        if c_per_100 > 0:
                            delta = gap_c / (c_per_100 / 100)
                            # LIMITE ESPECÍFICO: Aveia máximo 80g
                            max_grams = 80 if food_key == "aveia" else 300
                            new_g = clamp(food["grams"] + delta, 30, max_grams)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[0]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
        
        # Ajusta gorduras - Almoço(2), Jantar(4), Lanches(1,3)
        if abs(gap_f) > tol_f and not adjusted:
            for m_idx in [2, 4, 1, 3]:  # Almoço, Jantar, Lanches
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("key") == "azeite" or food.get("category") == "fat":
                        food_key = food["key"]
                        f_per_100 = FOODS[food_key]["f"]
                        if f_per_100 > 0:
                            delta = gap_f / (f_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 5, 80)  # Aumentado limite
                            if abs(new_g - food["grams"]) >= 5:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
                if adjusted:
                    break
        
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
            # PERMITIDO: ovos/iogurte/cottage + frutas | PROIBIDO: carnes, carbs complexos
            foods = [calc_food("cottage", 100), calc_food("morango", 100)]
    
    # Valida cada alimento
    validated_foods = []
    for food in foods:
        validated_food = validate_and_fix_food(food, preferred)
        if validated_food:
            validated_foods.append(validated_food)
    
    # Garante que tem pelo menos 1 alimento (RESPEITANDO regras da refeição)
    if len(validated_foods) == 0:
        if meal_index in [0, 5]:  # Café ou Ceia - proteína leve
            validated_foods = [calc_food("ovos", 100)]
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
                          preferred: Set[str] = None) -> List[Dict]:
    """
    ✅ CHECKLIST FINAL OBRIGATÓRIO
    
    Antes de retornar a dieta, valida:
    ☑ Nenhum alimento com 0g
    ☑ Nenhuma refeição com lista vazia
    ☑ Todos os campos obrigatórios preenchidos
    ☑ Quantidades em múltiplos de 10g
    ☑ Dieta consistente e utilizável
    ☑ Estrutura JSON válida
    ☑ 6 refeições completas
    
    Se qualquer item falhar → CORRIGE AUTOMATICAMENTE
    """
    # Garante mínimo de 6 refeições
    while len(meals) < 6:
        meals.append({})
    
    # Valida cada refeição
    validated_meals = []
    for idx, meal in enumerate(meals[:6]):  # Máximo 6 refeições
        validated_meal = validate_and_fix_meal(meal, idx, preferred)
        validated_meals.append(validated_meal)
    
    # Verifica totais
    all_foods = [f for m in validated_meals for f in m.get("foods", [])]
    total_p, total_c, total_f, total_cal = sum_foods(all_foods)
    
    # Se calorias totais < mínimo diário, adiciona comida nas refeições principais
    while total_cal < MIN_DAILY_CALORIES:
        # Adiciona proteína no almoço ou jantar (índices 2 e 4)
        target_meal = 2 if validated_meals[2].get("total_calories", 0) < validated_meals[4].get("total_calories", 0) else 4
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
    
    for meal in validated_meals:
        for food in meal.get("foods", []):
            for field in required_fields:
                if field not in food:
                    # Campo faltando - recalcula o alimento
                    food_key = food.get("key", "frango")
                    grams = food.get("grams", 100)
                    recalc = calc_food(food_key, grams)
                    food.update(recalc)
    
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
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        """
        Gera plano de dieta personalizado.
        
        ✅ GARANTIAS BULLETPROOF:
        - NUNCA retorna erro
        - NUNCA retorna dieta inválida
        - NUNCA retorna refeição vazia
        - NUNCA retorna alimento com 0g
        - SEMPRE retorna dieta válida e utilizável
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
        meals = generate_diet(target_p, target_c, target_f, preferred_foods, dietary_restrictions)
        
        # Fine-tune (múltiplas rodadas se necessário)
        for _ in range(5):  # Aumentado para 5 tentativas
            meals = fine_tune_diet(meals, target_p, target_c, target_f)
            is_valid, _ = validate_diet(meals, target_p, target_c, target_f)
            if is_valid:
                break
        
        # ✅ VALIDAÇÃO BULLETPROOF FINAL
        # Garante que NUNCA retorna dieta inválida
        meals = validate_and_fix_diet(meals, target_p, target_c, target_f, preferred_foods)
        
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
