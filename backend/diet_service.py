"""
Sistema de Geração de Dieta - V11 ATHLETE EDITION
============================================
REGRAS:
1. Apenas alimentos base de dieta de atleta
2. Valores ARREDONDADOS (múltiplos de 10g)
3. Whey é SUPLEMENTO, não proteína de refeição
4. Abacate é FRUTA, não gordura
5. Suplementos não contam como proteína
============================================
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
    supplements: List[str] = []  # Suplementos separados
    notes: Optional[str] = None


class DietGenerateRequest(BaseModel):
    user_id: str


# ==================== TOLERANCES ====================

TOL_P = 25.0   # Tolerância de proteína em g
TOL_C = 50.0   # Tolerância de carbs em g
TOL_F = 25.0   # Tolerância de gordura em g
TOL_CAL = 200.0  # Tolerância de calorias


# ==================== NORMALIZAÇÃO ====================
# Mapeia IDs do frontend para IDs internos

FOOD_NORMALIZATION = {
    # PROTEÍNAS (clean sources only)
    "chicken_breast": "frango",
    "chicken": "frango",
    "chicken_thigh": "coxa_frango",
    "lean_beef": "patinho",
    "ground_beef": "carne_moida",
    "beef": "patinho",
    "pork": "suino",
    "eggs": "ovos",
    "egg_whites": "claras",
    "tilapia": "tilapia",
    "tuna": "atum",
    "salmon": "salmao",
    "shrimp": "camarao",
    "sardine": "sardinha",
    "turkey": "peru",
    "fish": "tilapia",
    "cottage": "cottage",
    "greek_yogurt": "iogurte_grego",
    "tofu": "tofu",
    
    # CARBOIDRATOS
    "white_rice": "arroz_branco",
    "brown_rice": "arroz_integral",
    "rice": "arroz_branco",
    "sweet_potato": "batata_doce",
    "potato": "batata",
    "oats": "aveia",
    "pasta": "macarrao",
    "bread": "pao",
    "whole_bread": "pao_integral",
    "quinoa": "quinoa",
    "couscous": "cuscuz",
    "tapioca": "tapioca",
    "corn": "milho",
    "beans": "feijao",
    "lentils": "lentilha",
    "chickpeas": "grao_de_bico",
    
    # GORDURAS
    "olive_oil": "azeite",
    "peanut_butter": "pasta_amendoim",
    "almond_butter": "pasta_amendoa",
    "coconut_oil": "oleo_coco",
    "butter": "manteiga",
    "nuts": "castanhas",
    "almonds": "amendoas",
    "walnuts": "nozes",
    "chia": "chia",
    "flaxseed": "linhaca",
    "cheese": "queijo",
    "cream_cheese": "cream_cheese",
    
    # FRUTAS (separate category, avocado is fruit!)
    "banana": "banana",
    "apple": "maca",
    "orange": "laranja",
    "strawberry": "morango",
    "papaya": "mamao",
    "mango": "manga",
    "watermelon": "melancia",
    "avocado": "abacate",  # FRUIT not FAT
    "grape": "uva",
    "pineapple": "abacaxi",
    "melon": "melao",
    "kiwi": "kiwi",
    "pear": "pera",
    "peach": "pessego",
    "blueberry": "mirtilo",
    "açai": "acai",
    
    # SUPLEMENTOS (never in meals, never count as protein)
    "creatine": "creatina",
    "multivitamin": "multivitaminico",
    "omega3": "omega3",
    "caffeine": "cafeina",
    "vitamin_d": "vitamina_d",
    "vitamin_c": "vitamina_c",
    "zinc": "zinco",
    "magnesium": "magnesio",
    "collagen": "colageno",
}


def normalize_food(food_id: str) -> str:
    """Normaliza ID de alimento"""
    return FOOD_NORMALIZATION.get(food_id, food_id)


def get_user_preferred_foods(food_preferences: List[str]) -> Set[str]:
    """Retorna conjunto de alimentos normalizados"""
    normalized = set()
    for food in food_preferences:
        normalized.add(normalize_food(food))
    return normalized


# ==================== FOOD DATABASE ====================
# Values per 100g
# ATHLETE FOODS = Restricted list (clean sources)
# GENERAL FOODS = Expanded list (more variety)

FOODS = {
    # === PROTEÍNAS ===
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "category": "protein"},
    "coxa_frango": {"name": "Coxa de Frango", "p": 26.0, "c": 0.0, "f": 8.0, "category": "protein"},
    "patinho": {"name": "Patinho (Carne Magra)", "p": 28.0, "c": 0.0, "f": 6.0, "category": "protein"},
    "carne_moida": {"name": "Carne Moída", "p": 26.0, "c": 0.0, "f": 10.0, "category": "protein"},
    "suino": {"name": "Carne Suína", "p": 27.0, "c": 0.0, "f": 14.0, "category": "protein"},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "category": "protein"},
    "claras": {"name": "Claras de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "category": "protein"},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "category": "protein"},
    "atum": {"name": "Atum", "p": 29.0, "c": 0.0, "f": 1.0, "category": "protein"},
    "salmao": {"name": "Salmão", "p": 25.0, "c": 0.0, "f": 13.0, "category": "protein"},
    "camarao": {"name": "Camarão", "p": 24.0, "c": 0.0, "f": 1.0, "category": "protein"},
    "sardinha": {"name": "Sardinha", "p": 25.0, "c": 0.0, "f": 11.0, "category": "protein"},
    "peru": {"name": "Peru", "p": 29.0, "c": 0.0, "f": 1.0, "category": "protein"},
    "cottage": {"name": "Queijo Cottage", "p": 11.0, "c": 3.4, "f": 4.3, "category": "protein"},
    "iogurte_grego": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "category": "protein"},
    "tofu": {"name": "Tofu", "p": 8.0, "c": 2.0, "f": 4.0, "category": "protein"},
    
    # === CARBOIDRATOS ===
    "arroz_branco": {"name": "Arroz Branco", "p": 2.6, "c": 28.0, "f": 0.3, "category": "carb"},
    "arroz_integral": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "category": "carb"},
    "batata_doce": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "category": "carb"},
    "batata": {"name": "Batata Inglesa", "p": 2.0, "c": 17.0, "f": 0.1, "category": "carb"},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "category": "carb"},
    "macarrao": {"name": "Macarrão", "p": 5.0, "c": 25.0, "f": 1.0, "category": "carb"},
    "pao": {"name": "Pão", "p": 9.0, "c": 49.0, "f": 3.0, "category": "carb"},
    "pao_integral": {"name": "Pão Integral", "p": 10.0, "c": 42.0, "f": 4.0, "category": "carb"},
    "quinoa": {"name": "Quinoa", "p": 4.4, "c": 21.0, "f": 1.9, "category": "carb"},
    "cuscuz": {"name": "Cuscuz", "p": 3.8, "c": 23.0, "f": 0.2, "category": "carb"},
    "tapioca": {"name": "Tapioca", "p": 0.5, "c": 22.0, "f": 0.0, "category": "carb"},
    "milho": {"name": "Milho", "p": 3.2, "c": 19.0, "f": 1.2, "category": "carb"},
    "feijao": {"name": "Feijão", "p": 6.0, "c": 14.0, "f": 0.5, "category": "carb"},
    "lentilha": {"name": "Lentilha", "p": 9.0, "c": 20.0, "f": 0.4, "category": "carb"},
    "grao_de_bico": {"name": "Grão de Bico", "p": 9.0, "c": 27.0, "f": 2.6, "category": "carb"},
    
    # === GORDURAS ===
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat"},
    "pasta_amendoim": {"name": "Pasta de Amendoim", "p": 25.0, "c": 20.0, "f": 50.0, "category": "fat"},
    "pasta_amendoa": {"name": "Pasta de Amêndoa", "p": 21.0, "c": 19.0, "f": 56.0, "category": "fat"},
    "oleo_coco": {"name": "Óleo de Coco", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat"},
    "manteiga": {"name": "Manteiga", "p": 0.9, "c": 0.1, "f": 81.0, "category": "fat"},
    "castanhas": {"name": "Castanhas", "p": 14.0, "c": 30.0, "f": 44.0, "category": "fat"},
    "amendoas": {"name": "Amêndoas", "p": 21.0, "c": 22.0, "f": 49.0, "category": "fat"},
    "nozes": {"name": "Nozes", "p": 15.0, "c": 14.0, "f": 65.0, "category": "fat"},
    "chia": {"name": "Chia", "p": 17.0, "c": 42.0, "f": 31.0, "category": "fat"},
    "linhaca": {"name": "Linhaça", "p": 18.0, "c": 29.0, "f": 42.0, "category": "fat"},
    "queijo": {"name": "Queijo", "p": 23.0, "c": 1.3, "f": 33.0, "category": "fat"},
    "cream_cheese": {"name": "Cream Cheese", "p": 6.0, "c": 4.0, "f": 34.0, "category": "fat"},
    
    # === FRUTAS ===
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "category": "fruit"},
    "maca": {"name": "Maçã", "p": 0.3, "c": 14.0, "f": 0.2, "category": "fruit"},
    "laranja": {"name": "Laranja", "p": 0.9, "c": 12.0, "f": 0.1, "category": "fruit"},
    "morango": {"name": "Morango", "p": 0.7, "c": 8.0, "f": 0.3, "category": "fruit"},
    "mamao": {"name": "Mamão", "p": 0.5, "c": 11.0, "f": 0.1, "category": "fruit"},
    "manga": {"name": "Manga", "p": 0.8, "c": 15.0, "f": 0.4, "category": "fruit"},
    "melancia": {"name": "Melancia", "p": 0.6, "c": 8.0, "f": 0.2, "category": "fruit"},
    "abacate": {"name": "Abacate", "p": 2.0, "c": 9.0, "f": 15.0, "category": "fruit"},
    "uva": {"name": "Uva", "p": 0.7, "c": 18.0, "f": 0.2, "category": "fruit"},
    "abacaxi": {"name": "Abacaxi", "p": 0.5, "c": 13.0, "f": 0.1, "category": "fruit"},
    "melao": {"name": "Melão", "p": 0.8, "c": 8.0, "f": 0.2, "category": "fruit"},
    "kiwi": {"name": "Kiwi", "p": 1.1, "c": 15.0, "f": 0.5, "category": "fruit"},
    "pera": {"name": "Pera", "p": 0.4, "c": 15.0, "f": 0.1, "category": "fruit"},
    "pessego": {"name": "Pêssego", "p": 0.9, "c": 10.0, "f": 0.3, "category": "fruit"},
    "mirtilo": {"name": "Mirtilo", "p": 0.7, "c": 14.0, "f": 0.3, "category": "fruit"},
    "acai": {"name": "Açaí", "p": 1.0, "c": 6.0, "f": 5.0, "category": "fruit"},
    
    # === VEGETAIS (for fiber, low macro impact) ===
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "category": "vegetable"},
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "category": "vegetable"},
}

# Suplementos - NUNCA contam como proteína ou entram nas refeições
SUPPLEMENTS = {
    "creatina": {"name": "Creatina (5g/dia)", "dose": "5g"},
    "multivitaminico": {"name": "Multivitamínico (1/dia)", "dose": "1 cápsula"},
    "omega3": {"name": "Ômega 3 (1-2g/dia)", "dose": "1-2g"},
    "cafeina": {"name": "Cafeína (pré-treino)", "dose": "200mg"},
}


# ==================== FUNÇÕES AUXILIARES ====================

def round_to_10(value: float) -> int:
    """Arredonda para múltiplo de 10 (REGRA OBRIGATÓRIA)"""
    return int(round(value / 10) * 10)


def calc_food(key: str, grams: float) -> Dict:
    """Calcula macros com gramas ARREDONDADOS para múltiplo de 10"""
    # REGRA: todas quantidades múltiplos de 10g
    g = max(10, round_to_10(grams))
    
    if key not in FOODS:
        raise ValueError(f"Alimento '{key}' não encontrado")
    
    f = FOODS[key]
    r = g / 100.0
    
    # Calcula e arredonda
    protein = round(f["p"] * r)
    carbs = round(f["c"] * r)
    fat = round(f["f"] * r)
    calories = round((f["p"]*4 + f["c"]*4 + f["f"]*9) * r)
    
    return {
        "key": key,
        "name": f["name"],
        "quantity": f"{g}g",
        "grams": g,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "calories": calories,
        "category": f["category"]
    }


def sum_foods(foods: List[Dict]) -> Tuple[int, int, int, int]:
    """Soma macros de lista de alimentos"""
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    fv = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return int(p), int(c), int(fv), int(cal)


def clamp(val: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, val))


# ==================== CONSISTÊNCIA ====================

def ensure_consistency(target_cal: float, target_p: float, target_c: float, target_f: float) -> Tuple[int, int, int]:
    """Garante que macros batem com calorias"""
    calc_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    if abs(calc_cal - target_cal) <= 1:
        return round_to_10(target_p), round_to_10(target_c), round_to_10(target_f)
    
    ratio = target_cal / calc_cal
    return round_to_10(target_p * ratio), round_to_10(target_c * ratio), round_to_10(target_f * ratio)


# ==================== SELEÇÃO DE ALIMENTOS ====================

def get_protein(preferred: Set[str]) -> str:
    """Retorna proteína preferida ou fallback"""
    priority = ["frango", "patinho", "tilapia", "salmao", "atum"]
    for p in priority:
        if p in preferred or not preferred:
            return p
    return "frango"


def get_carb(preferred: Set[str]) -> str:
    """Retorna carb preferido"""
    priority = ["arroz_branco", "arroz_integral", "batata_doce", "batata", "macarrao"]
    for c in priority:
        if c in preferred or not preferred:
            return c
    return "arroz_branco"


def get_fruit(preferred: Set[str]) -> str:
    """Retorna fruta preferida"""
    priority = ["banana", "maca", "laranja", "mamao"]
    for f in priority:
        if f in preferred or not preferred:
            return f
    return "banana"


# ==================== GERAÇÃO DE DIETA ====================

def generate_base_diet(target_p: int, target_c: int, target_f: int, preferred: Set[str] = None) -> List[Dict]:
    """Gera dieta base usando apenas alimentos limpos de atleta"""
    if preferred is None:
        preferred = set()
    
    main_protein = get_protein(preferred)
    main_carb = get_carb(preferred)
    main_fruit = get_fruit(preferred)
    
    meals = []
    
    # ===== CAFÉ DA MANHÃ (20% P, 25% C, 30% F) =====
    cafe_p = target_p * 0.20
    cafe_c = target_c * 0.25
    cafe_f = target_f * 0.30
    
    ovos_g = clamp(cafe_p / 0.13 * 0.7, 60, 150)
    aveia_g = clamp(cafe_c * 0.4 / 0.66, 30, 80)
    fruit_g = clamp((cafe_c * 0.5) / 0.23, 50, 150)
    
    cafe_foods = [
        calc_food("ovos", ovos_g),
        calc_food("aveia", aveia_g),
        calc_food(main_fruit, fruit_g),
    ]
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": cafe_foods})
    
    # ===== LANCHE MANHÃ (10% P, 10% C, 15% F) =====
    lanche1_c = target_c * 0.10
    lanche1_f = target_f * 0.15
    
    pao_g = clamp(lanche1_c / 0.49, 20, 60)
    pasta_g = clamp(lanche1_f * 0.5 / 0.50, 10, 30)
    
    lanche1_foods = [
        calc_food("pao", pao_g),
        calc_food("pasta_amendoim", pasta_g),
        calc_food("banana", 100),
    ]
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": lanche1_foods})
    
    # ===== ALMOÇO (30% P, 30% C, 25% F) =====
    almoco_p = target_p * 0.30
    almoco_c = target_c * 0.30
    almoco_f = target_f * 0.25
    
    protein_g = clamp(almoco_p / (FOODS[main_protein]["p"] / 100), 100, 300)
    carb_g = clamp(almoco_c * 0.8 / (FOODS[main_carb]["c"] / 100), 100, 400)
    azeite_g = clamp(almoco_f * 0.5 / 1.0, 5, 15)
    
    almoco_foods = [
        calc_food(main_protein, protein_g),
        calc_food(main_carb, carb_g),
        calc_food("salada", 100),
        calc_food("azeite", azeite_g),
    ]
    meals.append({"name": "Almoço", "time": "12:30", "foods": almoco_foods})
    
    # ===== LANCHE TARDE / PRÉ-TREINO (15% P, 20% C, 10% F) =====
    lanche2_p = target_p * 0.15
    lanche2_c = target_c * 0.20
    
    batata_g = clamp(lanche2_c / 0.20, 100, 400)
    protein2_g = clamp(lanche2_p / (FOODS[main_protein]["p"] / 100), 80, 200)
    
    lanche2_foods = [
        calc_food("batata_doce", batata_g),
        calc_food(main_protein, protein2_g),
    ]
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": lanche2_foods})
    
    # ===== JANTAR (25% P, 15% C, 20% F) =====
    jantar_p = target_p * 0.25
    jantar_c = target_c * 0.15
    jantar_f = target_f * 0.20
    
    # Alterna proteína se possível
    alt_protein = "tilapia" if main_protein != "tilapia" and ("tilapia" in preferred or not preferred) else main_protein
    
    protein3_g = clamp(jantar_p / (FOODS[alt_protein]["p"] / 100), 100, 300)
    carb2_g = clamp(jantar_c / (FOODS[main_carb]["c"] / 100), 80, 250)
    azeite2_g = clamp(jantar_f * 0.4 / 1.0, 5, 15)
    
    jantar_foods = [
        calc_food(alt_protein, protein3_g),
        calc_food(main_carb, carb2_g),
        calc_food("brocolis", 100),
        calc_food("azeite", azeite2_g),
    ]
    meals.append({"name": "Jantar", "time": "19:30", "foods": jantar_foods})
    
    return meals


def fine_tune_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int, max_iter: int = 500) -> List[Dict]:
    """Ajuste fino iterativo"""
    target_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    for _ in range(max_iter):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Verifica tolerâncias
        if abs(gap_p) <= TOL_P and abs(gap_c) <= TOL_C and abs(gap_f) <= TOL_F:
            return meals
        
        adjusted = False
        
        # Ajusta o macro com maior gap
        gaps = [
            ("p", abs(gap_p) / TOL_P if abs(gap_p) > TOL_P else 0, gap_p),
            ("c", abs(gap_c) / TOL_C if abs(gap_c) > TOL_C else 0, gap_c),
            ("f", abs(gap_f) / TOL_F if abs(gap_f) > TOL_F else 0, gap_f),
        ]
        gaps.sort(key=lambda x: x[1], reverse=True)
        
        for macro, _, gap in gaps:
            if adjusted:
                break
            
            if macro == "p" and abs(gap) > TOL_P:
                # Ajusta proteínas
                for m_idx in [2, 3, 4]:  # Almoço, Lanche, Jantar
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["category"] == "protein":
                            food_key = food["key"]
                            p_per_100 = FOODS[food_key]["p"]
                            delta = gap / (p_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 80, 400)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
                    if adjusted:
                        break
            
            elif macro == "c" and abs(gap) > TOL_C:
                # Ajusta carboidratos
                carb_targets = [(3, "batata_doce"), (2, None), (4, None), (0, "aveia")]
                for m_idx, expected_key in carb_targets:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["category"] == "carb":
                            if expected_key is None or food["key"] == expected_key:
                                food_key = food["key"]
                                c_per_100 = FOODS[food_key]["c"]
                                delta = gap / (c_per_100 / 100)
                                new_g = clamp(food["grams"] + delta, 30, 500)
                                if abs(new_g - food["grams"]) >= 10:
                                    meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                    adjusted = True
                                    break
                    if adjusted:
                        break
            
            elif macro == "f" and abs(gap) > TOL_F:
                # Ajusta gorduras (azeite principalmente)
                for m_idx in [2, 4]:  # Almoço, Jantar
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["key"] == "azeite":
                            new_g = clamp(food["grams"] + gap, 5, 25)
                            if abs(new_g - food["grams"]) >= 5:
                                meals[m_idx]["foods"][f_idx] = calc_food("azeite", new_g)
                                adjusted = True
                                break
                    if adjusted:
                        break
                
                # Tenta pasta de amendoim
                if not adjusted:
                    for f_idx, food in enumerate(meals[1]["foods"]):
                        if food["key"] == "pasta_amendoim":
                            delta = gap / 0.50
                            new_g = clamp(food["grams"] + delta, 10, 50)
                            if abs(new_g - food["grams"]) >= 5:
                                meals[1]["foods"][f_idx] = calc_food("pasta_amendoim", new_g)
                                adjusted = True
                                break
        
        if not adjusted:
            break
    
    return meals


def validate_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int) -> Tuple[bool, str]:
    """Valida se dieta atinge os targets"""
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    
    errors = []
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P:{curr_p}g vs {target_p}g")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C:{curr_c}g vs {target_c}g")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F:{curr_f}g vs {target_f}g")
    
    return len(errors) == 0, "; ".join(errors)


def get_user_supplements(food_preferences: List[str]) -> List[str]:
    """Retorna suplementos selecionados pelo usuário"""
    user_supplements = []
    for pref in food_preferences:
        normalized = normalize_food(pref)
        if normalized in SUPPLEMENTS:
            user_supplements.append(SUPPLEMENTS[normalized]["name"])
    return user_supplements


# ==================== SERVICE ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        # Obtém preferências
        food_preferences = user_profile.get('food_preferences', [])
        preferred_foods = get_user_preferred_foods(food_preferences)
        
        # Obtém suplementos separadamente
        supplements = get_user_supplements(food_preferences)
        
        # Garante consistência
        adjusted_p, adjusted_c, adjusted_f = ensure_consistency(
            target_calories,
            target_macros["protein"],
            target_macros["carbs"],
            target_macros["fat"]
        )
        
        target_cal_int = int(round(target_calories))
        
        # Gera dieta
        meals = generate_base_diet(adjusted_p, adjusted_c, adjusted_f, preferred_foods)
        
        # Fine-tune
        meals = fine_tune_diet(meals, adjusted_p, adjusted_c, adjusted_f, max_iter=500)
        
        # Valida
        is_valid, error = validate_diet(meals, adjusted_p, adjusted_c, adjusted_f)
        
        if not is_valid:
            raise ValueError(f"Impossível fechar macros: {error}")
        
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
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal_int,
            target_macros={"protein": adjusted_p, "carbs": adjusted_c, "fat": adjusted_f},
            meals=final_meals,
            computed_calories=total_cal,
            computed_macros={"protein": total_p, "carbs": total_c, "fat": total_f},
            supplements=supplements,
            notes=f"Dieta: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g | Quantidades em múltiplos de 10g"
        )


# ==================== AJUSTE AUTOMÁTICO QUINZENAL ====================

def evaluate_progress(
    goal: str,
    previous_weight: float,
    current_weight: float,
    tolerance_kg: float = 0.3
) -> Dict:
    """
    Avalia progresso com base no objetivo e variação de peso.
    
    Retorna:
    - needs_adjustment: bool
    - adjustment_type: "increase" | "decrease" | None
    - adjustment_percent: float (5-8%)
    - reason: str
    """
    weight_diff = current_weight - previous_weight
    
    result = {
        "needs_adjustment": False,
        "adjustment_type": None,
        "adjustment_percent": 0.0,
        "reason": "Progresso adequado"
    }
    
    if goal == "cutting":
        # CUTTING: Espera perda de peso
        if weight_diff >= -tolerance_kg:
            # Peso não caiu (ou subiu) - precisa reduzir calorias
            result["needs_adjustment"] = True
            result["adjustment_type"] = "decrease"
            # Ajuste de 5-8% baseado no quanto ficou longe do objetivo
            result["adjustment_percent"] = 6.0 if weight_diff >= 0 else 5.0
            result["reason"] = f"Peso não reduziu ({weight_diff:+.1f}kg). Reduzindo calorias."
        else:
            result["reason"] = f"Perda de peso adequada ({weight_diff:.1f}kg)."
    
    elif goal == "bulking":
        # BULKING: Espera ganho de peso
        if weight_diff <= tolerance_kg:
            # Peso não subiu (ou caiu) - precisa aumentar calorias
            result["needs_adjustment"] = True
            result["adjustment_type"] = "increase"
            result["adjustment_percent"] = 6.0 if weight_diff <= 0 else 5.0
            result["reason"] = f"Peso não aumentou ({weight_diff:+.1f}kg). Aumentando calorias."
        else:
            result["reason"] = f"Ganho de peso adequado ({weight_diff:+.1f}kg)."
    
    elif goal == "manutencao":
        # MANUTENÇÃO: Espera estabilidade
        if abs(weight_diff) > 1.0:
            # Variação muito grande
            result["needs_adjustment"] = True
            if weight_diff > 0:
                result["adjustment_type"] = "decrease"
                result["adjustment_percent"] = 5.0
                result["reason"] = f"Peso aumentou demais ({weight_diff:+.1f}kg). Reduzindo calorias."
            else:
                result["adjustment_type"] = "increase"
                result["adjustment_percent"] = 5.0
                result["reason"] = f"Peso diminuiu demais ({weight_diff:.1f}kg). Aumentando calorias."
        else:
            result["reason"] = f"Peso estável ({weight_diff:+.1f}kg)."
    
    return result


def adjust_diet_quantities(
    diet_plan: Dict,
    adjustment_type: str,  # "increase" ou "decrease"
    adjustment_percent: float  # 5-8%
) -> Dict:
    """
    Ajusta quantidades da dieta existente.
    Mantém múltiplos de 10g.
    Não cria novos alimentos, apenas ajusta quantidades.
    """
    if adjustment_type not in ["increase", "decrease"]:
        return diet_plan
    
    multiplier = 1 + (adjustment_percent / 100) if adjustment_type == "increase" else 1 - (adjustment_percent / 100)
    
    meals = diet_plan.get("meals", [])
    
    for meal in meals:
        foods = meal.get("foods", [])
        for food in foods:
            # Obtém quantidade atual em gramas
            current_grams = food.get("grams", 100)
            
            # Calcula nova quantidade
            new_grams = current_grams * multiplier
            
            # Arredonda para múltiplo de 10
            new_grams = max(10, round_to_10(new_grams))
            
            # Atualiza food com novos valores
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
        meal_protein = sum(f.get("protein", 0) for f in foods)
        meal_carbs = sum(f.get("carbs", 0) for f in foods)
        meal_fat = sum(f.get("fat", 0) for f in foods)
        meal_calories = sum(f.get("calories", 0) for f in foods)
        
        meal["total_calories"] = meal_calories
        meal["macros"] = {"protein": meal_protein, "carbs": meal_carbs, "fat": meal_fat}
    
    # Recalcula totais da dieta
    all_foods = [f for m in meals for f in m.get("foods", [])]
    total_p = sum(f.get("protein", 0) for f in all_foods)
    total_c = sum(f.get("carbs", 0) for f in all_foods)
    total_f = sum(f.get("fat", 0) for f in all_foods)
    total_cal = sum(f.get("calories", 0) for f in all_foods)
    
    diet_plan["computed_calories"] = total_cal
    diet_plan["computed_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["target_calories"] = total_cal
    diet_plan["target_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
    diet_plan["notes"] = f"Dieta ajustada: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g | Múltiplos de 10g"
    
    return diet_plan
