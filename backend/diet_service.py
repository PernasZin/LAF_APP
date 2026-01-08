"""
Sistema de Geração de Dieta - V13 SMART AUTO-COMPLETE
======================================================
FILOSOFIA: NUNCA TRAVAR, SEMPRE GERAR

REGRAS:
1. Se faltar alimentos, AUTO-COMPLETE com opções padrão
2. NUNCA retorne erro por falta de opções
3. Seja amigável e explique o que foi adicionado
4. Calorias 95-105% do alvo, Macros ±5%
5. Quantidades em múltiplos de 10g
======================================================
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
    """Calcula macros de um alimento em quantidade específica"""
    if food_key not in FOODS:
        return None
    
    f = FOODS[food_key]
    g = round_to_10(grams)
    ratio = g / 100
    
    protein = round(f["p"] * ratio)
    carbs = round(f["c"] * ratio)
    fat = round(f["f"] * ratio)
    calories = round((f["p"] * 4 + f["c"] * 4 + f["f"] * 9) * ratio)
    
    return {
        "key": food_key,
        "name": f["name"],
        "grams": g,
        "quantity": f"{g}g",
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


# ==================== GERAÇÃO DE DIETA ====================

def generate_diet(target_p: int, target_c: int, target_f: int,
                  preferred: Set[str], restrictions: List[str]) -> List[Dict]:
    """
    Gera dieta usando APENAS alimentos selecionados pelo usuário.
    Distribui em 5 refeições balanceadas.
    """
    # Seleciona alimentos principais
    protein_priority = ["frango", "patinho", "tilapia", "atum", "salmao", "ovos", "peru"]
    carb_priority = ["arroz_branco", "arroz_integral", "batata_doce", "batata", "aveia", "macarrao"]
    fat_priority = ["azeite", "pasta_amendoim", "castanhas", "amendoas"]
    fruit_priority = ["banana", "maca", "laranja", "mamao", "morango"]
    
    main_protein = select_food(preferred, "protein", restrictions, protein_priority)
    main_carb = select_food(preferred, "carb", restrictions, carb_priority)
    main_fat = select_food(preferred, "fat", restrictions, fat_priority)
    main_fruit = select_food(preferred, "fruit", restrictions, fruit_priority)
    
    # Proteína alternativa
    alt_proteins = get_available_by_category(preferred, "protein", restrictions)
    alt_protein = main_protein
    for p in alt_proteins:
        if p != main_protein:
            alt_protein = p
            break
    
    # Carb alternativo
    alt_carbs = get_available_by_category(preferred, "carb", restrictions)
    alt_carb = main_carb
    for c in alt_carbs:
        if c != main_carb:
            alt_carb = c
            break
    
    meals = []
    
    # ===== CAFÉ DA MANHÃ (20% P, 25% C, 30% F) =====
    cafe_p = target_p * 0.20
    cafe_c = target_c * 0.25
    cafe_f = target_f * 0.30
    
    breakfast_protein = "ovos" if "ovos" in preferred or not preferred else main_protein
    breakfast_carb = "aveia" if ("aveia" in preferred or not preferred) and "Sem Glúten" not in restrictions else alt_carb
    
    p_grams = clamp(cafe_p / (FOODS[breakfast_protein]["p"] / 100), 80, 200)
    c_grams = clamp(cafe_c * 0.5 / max(FOODS[breakfast_carb]["c"] / 100, 0.1), 30, 100)
    fruit_grams = clamp(cafe_c * 0.4 / max(FOODS[main_fruit]["c"] / 100, 0.1), 50, 150)
    
    cafe_foods = [
        calc_food(breakfast_protein, p_grams),
        calc_food(breakfast_carb, c_grams),
        calc_food(main_fruit, fruit_grams),
    ]
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": [f for f in cafe_foods if f]})
    
    # ===== LANCHE MANHÃ (10% P, 10% C, 15% F) =====
    lanche1_c = target_c * 0.10
    lanche1_f = target_f * 0.15
    
    snack_carb = main_fruit
    fat_grams = clamp(lanche1_f / max(FOODS[main_fat]["f"] / 100, 0.1), 10, 40)
    snack_grams = clamp(lanche1_c / max(FOODS[snack_carb]["c"] / 100, 0.1), 50, 150)
    
    lanche1_foods = [
        calc_food(snack_carb, snack_grams),
        calc_food(main_fat, fat_grams),
    ]
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": [f for f in lanche1_foods if f]})
    
    # ===== ALMOÇO (30% P, 30% C, 25% F) =====
    almoco_p = target_p * 0.30
    almoco_c = target_c * 0.30
    almoco_f = target_f * 0.25
    
    protein_grams = clamp(almoco_p / (FOODS[main_protein]["p"] / 100), 100, 350)
    carb_grams = clamp(almoco_c * 0.9 / max(FOODS[main_carb]["c"] / 100, 0.1), 100, 400)
    azeite_grams = clamp(almoco_f * 0.4 / 1.0, 5, 20)
    
    almoco_foods = [
        calc_food(main_protein, protein_grams),
        calc_food(main_carb, carb_grams),
        calc_food("salada", 100),
        calc_food("azeite", azeite_grams),
    ]
    meals.append({"name": "Almoço", "time": "12:30", "foods": [f for f in almoco_foods if f]})
    
    # ===== LANCHE TARDE (15% P, 20% C, 10% F) =====
    lanche2_p = target_p * 0.15
    lanche2_c = target_c * 0.20
    
    pre_carb = "batata_doce" if ("batata_doce" in preferred or not preferred) else alt_carb
    
    batata_grams = clamp(lanche2_c / max(FOODS[pre_carb]["c"] / 100, 0.1), 100, 400)
    protein2_grams = clamp(lanche2_p / (FOODS[main_protein]["p"] / 100), 80, 200)
    
    lanche2_foods = [
        calc_food(pre_carb, batata_grams),
        calc_food(main_protein, protein2_grams),
    ]
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": [f for f in lanche2_foods if f]})
    
    # ===== JANTAR (25% P, 15% C, 20% F) =====
    jantar_p = target_p * 0.25
    jantar_c = target_c * 0.15
    jantar_f = target_f * 0.20
    
    protein3_grams = clamp(jantar_p / (FOODS[alt_protein]["p"] / 100), 100, 300)
    carb2_grams = clamp(jantar_c / max(FOODS[main_carb]["c"] / 100, 0.1), 80, 250)
    azeite2_grams = clamp(jantar_f * 0.35 / 1.0, 5, 15)
    
    jantar_foods = [
        calc_food(alt_protein, protein3_grams),
        calc_food(main_carb, carb2_grams),
        calc_food("brocolis", 100),
        calc_food("azeite", azeite2_grams),
    ]
    meals.append({"name": "Jantar", "time": "19:30", "foods": [f for f in jantar_foods if f]})
    
    return meals


def fine_tune_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int) -> List[Dict]:
    """
    Ajuste fino iterativo para atingir macros dentro de ±5%.
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
        
        # Ajusta proteínas
        if abs(gap_p) > tol_p and not adjusted:
            for m_idx in [2, 3, 4]:  # Almoço, Lanche, Jantar
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("category") == "protein":
                        food_key = food["key"]
                        p_per_100 = FOODS[food_key]["p"]
                        delta = gap_p / (p_per_100 / 100)
                        new_g = clamp(food["grams"] + delta, 80, 400)
                        if abs(new_g - food["grams"]) >= 10:
                            meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # Ajusta carboidratos
        if abs(gap_c) > tol_c and not adjusted:
            for m_idx in [3, 2, 4, 0]:
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("category") == "carb":
                        food_key = food["key"]
                        c_per_100 = FOODS[food_key]["c"]
                        if c_per_100 > 0:
                            delta = gap_c / (c_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 30, 500)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
                if adjusted:
                    break
        
        # Ajusta gorduras
        if abs(gap_f) > tol_f and not adjusted:
            for m_idx in [2, 4, 1]:
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food.get("key") == "azeite" or food.get("category") == "fat":
                        food_key = food["key"]
                        f_per_100 = FOODS[food_key]["f"]
                        if f_per_100 > 0:
                            delta = gap_f / (f_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 5, 50)
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
        
        NUNCA TRAVA - usa auto-complete se faltar opções.
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
        
        target_cal_int = int(round(target_calories))
        
        # Gera dieta com alimentos auto-completados se necessário
        meals = generate_diet(target_p, target_c, target_f, preferred_foods, dietary_restrictions)
        
        # Fine-tune (múltiplas rodadas se necessário)
        for _ in range(3):
            meals = fine_tune_diet(meals, target_p, target_c, target_f)
            is_valid, _ = validate_diet(meals, target_p, target_c, target_f)
            if is_valid:
                break
        
        # Formata resultado
        final_meals = []
        for m in meals:
            mp, mc, mf, mcal = sum_foods(m["foods"])
            final_meals.append(Meal(
                name=m["name"],
                time=m["time"],
                foods=m["foods"],
                total_calories=mcal,
                macros={"protein": mp, "carbs": mc, "fat": mf}
            ))
        
        all_foods = [f for m in meals for f in m["foods"]]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
        
        # Gera nota com info de auto-complete se aplicável
        notes = f"Dieta: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g | Múltiplos de 10g"
        
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
    """Ajusta quantidades da dieta existente mantendo múltiplos de 10g"""
    if adjustment_type not in ["increase", "decrease"]:
        return diet_plan
    
    multiplier = 1 + (adjustment_percent / 100) if adjustment_type == "increase" else 1 - (adjustment_percent / 100)
    
    meals = diet_plan.get("meals", [])
    
    for meal in meals:
        foods = meal.get("foods", [])
        for food in foods:
            current_grams = food.get("grams", 100)
            new_grams = max(10, round_to_10(current_grams * multiplier))
            
            food_key = food.get("key")
            if food_key and food_key in FOODS:
                food_data = FOODS[food_key]
                ratio = new_grams / 100
                
                food["grams"] = new_grams
                food["quantity"] = f"{new_grams}g"
                food["protein"] = round(food_data["p"] * ratio)
                food["carbs"] = round(food_data["c"] * ratio)
                food["fat"] = round(food_data["f"] * ratio)
                food["calories"] = round((food_data["p"]*4 + food_data["c"]*4 + food_data["f"]*9) * ratio)
        
        # Recalcula totais da refeição
        meal_p = sum(f.get("protein", 0) for f in foods)
        meal_c = sum(f.get("carbs", 0) for f in foods)
        meal_f = sum(f.get("fat", 0) for f in foods)
        meal_cal = sum(f.get("calories", 0) for f in foods)
        
        meal["total_calories"] = meal_cal
        meal["macros"] = {"protein": meal_p, "carbs": meal_c, "fat": meal_f}
    
    # Recalcula totais
    all_foods = [f for m in meals for f in m.get("foods", [])]
    total_p = sum(f.get("protein", 0) for f in all_foods)
    total_c = sum(f.get("carbs", 0) for f in all_foods)
    total_f = sum(f.get("fat", 0) for f in all_foods)
    total_cal = sum(f.get("calories", 0) for f in all_foods)
    
    diet_plan["computed_calories"] = total_cal
    diet_plan["computed_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["target_calories"] = total_cal
    diet_plan["target_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["notes"] = f"Dieta ajustada: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g"
    
    return diet_plan
