"""
Sistema de Geração de Dieta - V10 COMPLETO
CORREÇÕES:
1. Valores ARREDONDADOS (calorias inteiras, macros múltiplos de 5g)
2. Respeita preferências alimentares do usuário
3. Categorias separadas (Frutas, Suplementos)
4. Normalização de alimentos duplicados
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
    total_calories: int  # INTEIRO
    macros: Dict[str, int]  # INTEIROS (múltiplos de 5)


class DietPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_calories: int
    target_macros: Dict[str, int]
    meals: List[Meal]
    computed_calories: int
    computed_macros: Dict[str, int]
    notes: Optional[str] = None


class DietGenerateRequest(BaseModel):
    user_id: str


# ==================== TOLERANCES ====================

TOL_P = 5.0  # Tolerância de proteína em g
TOL_C = 5.0  # Tolerância de carbs em g
TOL_F = 3.0  # Tolerância de gordura em g
TOL_CAL = 30.0  # Tolerância de calorias


# ==================== NORMALIZAÇÃO DE ALIMENTOS ====================
# Mapeia alimentos equivalentes para um ID único

FOOD_NORMALIZATION = {
    # Proteínas
    "chicken": "frango",
    "chicken_breast": "frango",
    "peito_de_frango": "frango",
    "beef": "carne_bovina",
    "ground_beef": "carne_bovina",
    "steak": "carne_bovina",
    "fish": "tilapia",
    "tilapia": "tilapia",
    "salmon": "salmao",
    "tuna": "atum",
    "eggs": "ovos",
    "egg_whites": "clara",
    "clara_de_ovo": "clara",
    "whey": "whey",
    "greek_yogurt": "iogurte",
    "cottage": "cottage",
    "turkey": "peru",
    "ham": "presunto",
    "shrimp": "camarao",
    "pork": "suino",
    # Carboidratos
    "rice": "arroz",
    "brown_rice": "arroz",
    "arroz_integral": "arroz",
    "sweet_potato": "batata_doce",
    "batata_doce": "batata_doce",
    "potato": "batata",
    "batata_inglesa": "batata",
    "oats": "aveia",
    "pasta": "macarrao",
    "integral_pasta": "macarrao",
    "bread": "pao",
    "integral_bread": "pao",
    "tapioca": "tapioca",
    "cassava": "mandioca",
    "corn": "milho",
    "beans": "feijao",
    "lentils": "lentilha",
    "chickpeas": "grao_de_bico",
    # Frutas (CATEGORIA SEPARADA)
    "banana": "banana",
    "apple": "maca",
    "orange": "laranja",
    "berries": "frutas_vermelhas",
    "mango": "manga",
    "papaya": "mamao",
    "watermelon": "melancia",
    "grapes": "uva",
    # Gorduras
    "olive_oil": "azeite",
    "coconut_oil": "oleo_coco",
    "avocado": "abacate",
    "nuts": "castanha",
    "almonds": "amendoas",
    "walnuts": "nozes",
    "brazil_nuts": "castanha_para",
    "peanuts": "amendoim",
    "peanut_butter": "pasta_amendoim",
    "seeds": "sementes",
    "butter": "manteiga",
    "cheese": "queijo",
    "cream_cheese": "cream_cheese",
    "heavy_cream": "creme_leite",
    # Vegetais
    "broccoli": "brocolis",
    "spinach": "espinafre",
    "lettuce": "alface",
    "tomato": "tomate",
    "carrot": "cenoura",
    "cucumber": "pepino",
    "zucchini": "abobrinha",
    "onion": "cebola",
    "garlic": "alho",
    "bell_pepper": "pimentao",
    "mushroom": "cogumelo",
    "cabbage": "repolho",
    "green_beans": "vagem",
    "asparagus": "aspargo",
    # Suplementos (CATEGORIA SEPARADA)
    "creatine": "creatina",
    "bcaa": "bcaa",
    "multivitamin": "multivitaminico",
}


def normalize_food(food_id: str) -> str:
    """Normaliza ID de alimento para evitar duplicidades"""
    return FOOD_NORMALIZATION.get(food_id, food_id)


def get_user_preferred_foods(food_preferences: List[str]) -> Set[str]:
    """Retorna conjunto de alimentos normalizados que o usuário prefere"""
    normalized = set()
    for food in food_preferences:
        normalized.add(normalize_food(food))
    return normalized


# ==================== FOOD DATABASE EXPANDIDO ====================

FOODS = {
    # === PROTEÍNAS ===
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "category": "protein"},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "category": "protein"},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "category": "protein"},
    "salmao": {"name": "Salmão", "p": 25.0, "c": 0.0, "f": 13.0, "category": "protein"},
    "atum": {"name": "Atum", "p": 29.0, "c": 0.0, "f": 1.0, "category": "protein"},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "category": "protein"},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "category": "protein"},
    "cottage": {"name": "Queijo Cottage", "p": 11.0, "c": 3.4, "f": 4.3, "category": "protein"},
    "carne_bovina": {"name": "Carne Bovina", "p": 26.0, "c": 0.0, "f": 15.0, "category": "protein"},
    "peru": {"name": "Peru", "p": 29.0, "c": 0.0, "f": 1.0, "category": "protein"},
    "presunto": {"name": "Presunto", "p": 18.0, "c": 1.0, "f": 3.0, "category": "protein"},
    "camarao": {"name": "Camarão", "p": 24.0, "c": 0.0, "f": 0.3, "category": "protein"},
    "suino": {"name": "Carne Suína", "p": 27.0, "c": 0.0, "f": 14.0, "category": "protein"},
    "whey": {"name": "Whey Protein", "p": 80.0, "c": 5.0, "f": 3.0, "category": "supplement"},
    
    # === CARBOIDRATOS ===
    "batata_doce": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "category": "carb"},
    "batata": {"name": "Batata", "p": 2.0, "c": 17.0, "f": 0.1, "category": "carb"},
    "arroz": {"name": "Arroz", "p": 2.6, "c": 28.0, "f": 0.3, "category": "carb"},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "category": "carb"},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5, "category": "carb"},
    "lentilha": {"name": "Lentilha", "p": 9.0, "c": 20.0, "f": 0.4, "category": "carb"},
    "grao_de_bico": {"name": "Grão de Bico", "p": 9.0, "c": 27.0, "f": 2.6, "category": "carb"},
    "macarrao": {"name": "Macarrão", "p": 5.0, "c": 25.0, "f": 1.0, "category": "carb"},
    "pao": {"name": "Pão", "p": 9.0, "c": 49.0, "f": 3.0, "category": "carb"},
    "tapioca": {"name": "Tapioca", "p": 0.2, "c": 22.0, "f": 0.0, "category": "carb"},
    "mandioca": {"name": "Mandioca", "p": 1.4, "c": 38.0, "f": 0.3, "category": "carb"},
    "milho": {"name": "Milho", "p": 3.0, "c": 19.0, "f": 1.0, "category": "carb"},
    
    # === FRUTAS (CATEGORIA SEPARADA) ===
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "category": "fruit"},
    "maca": {"name": "Maçã", "p": 0.3, "c": 14.0, "f": 0.2, "category": "fruit"},
    "laranja": {"name": "Laranja", "p": 0.9, "c": 12.0, "f": 0.1, "category": "fruit"},
    "frutas_vermelhas": {"name": "Frutas Vermelhas", "p": 0.7, "c": 12.0, "f": 0.3, "category": "fruit"},
    "manga": {"name": "Manga", "p": 0.8, "c": 15.0, "f": 0.4, "category": "fruit"},
    "mamao": {"name": "Mamão", "p": 0.5, "c": 11.0, "f": 0.1, "category": "fruit"},
    "melancia": {"name": "Melancia", "p": 0.6, "c": 8.0, "f": 0.2, "category": "fruit"},
    "uva": {"name": "Uva", "p": 0.7, "c": 18.0, "f": 0.2, "category": "fruit"},
    
    # === GORDURAS ===
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat"},
    "oleo_coco": {"name": "Óleo de Coco", "p": 0.0, "c": 0.0, "f": 100.0, "category": "fat"},
    "abacate": {"name": "Abacate", "p": 2.0, "c": 9.0, "f": 15.0, "category": "fat"},
    "castanha": {"name": "Castanhas", "p": 14.0, "c": 12.0, "f": 67.0, "category": "fat"},
    "amendoas": {"name": "Amêndoas", "p": 21.0, "c": 22.0, "f": 49.0, "category": "fat"},
    "nozes": {"name": "Nozes", "p": 15.0, "c": 14.0, "f": 65.0, "category": "fat"},
    "castanha_para": {"name": "Castanha do Pará", "p": 14.0, "c": 12.0, "f": 67.0, "category": "fat"},
    "amendoim": {"name": "Amendoim", "p": 26.0, "c": 16.0, "f": 49.0, "category": "fat"},
    "pasta_amendoim": {"name": "Pasta de Amendoim", "p": 25.0, "c": 20.0, "f": 50.0, "category": "fat"},
    "sementes": {"name": "Sementes", "p": 18.0, "c": 24.0, "f": 42.0, "category": "fat"},
    "manteiga": {"name": "Manteiga", "p": 0.9, "c": 0.1, "f": 81.0, "category": "fat"},
    "queijo": {"name": "Queijo", "p": 25.0, "c": 1.3, "f": 33.0, "category": "fat"},
    "cream_cheese": {"name": "Cream Cheese", "p": 6.0, "c": 4.0, "f": 34.0, "category": "fat"},
    "creme_leite": {"name": "Creme de Leite", "p": 2.0, "c": 3.0, "f": 35.0, "category": "fat"},
    
    # === VEGETAIS ===
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "category": "vegetable"},
    "espinafre": {"name": "Espinafre", "p": 2.9, "c": 3.6, "f": 0.4, "category": "vegetable"},
    "alface": {"name": "Alface", "p": 1.4, "c": 2.9, "f": 0.2, "category": "vegetable"},
    "tomate": {"name": "Tomate", "p": 0.9, "c": 3.9, "f": 0.2, "category": "vegetable"},
    "cenoura": {"name": "Cenoura", "p": 0.9, "c": 10.0, "f": 0.2, "category": "vegetable"},
    "pepino": {"name": "Pepino", "p": 0.7, "c": 3.6, "f": 0.1, "category": "vegetable"},
    "abobrinha": {"name": "Abobrinha", "p": 1.2, "c": 3.1, "f": 0.3, "category": "vegetable"},
    "cebola": {"name": "Cebola", "p": 1.1, "c": 9.0, "f": 0.1, "category": "vegetable"},
    "alho": {"name": "Alho", "p": 6.4, "c": 33.0, "f": 0.5, "category": "vegetable"},
    "pimentao": {"name": "Pimentão", "p": 1.0, "c": 6.0, "f": 0.3, "category": "vegetable"},
    "cogumelo": {"name": "Cogumelo", "p": 3.0, "c": 3.0, "f": 0.3, "category": "vegetable"},
    "repolho": {"name": "Repolho", "p": 1.3, "c": 6.0, "f": 0.1, "category": "vegetable"},
    "vagem": {"name": "Vagem", "p": 1.8, "c": 7.0, "f": 0.1, "category": "vegetable"},
    "aspargo": {"name": "Aspargo", "p": 2.2, "c": 4.0, "f": 0.1, "category": "vegetable"},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "category": "vegetable"},
    
    # === SUPLEMENTOS (CATEGORIA SEPARADA) ===
    "creatina": {"name": "Creatina", "p": 0.0, "c": 0.0, "f": 0.0, "category": "supplement"},
    "bcaa": {"name": "BCAA", "p": 0.0, "c": 0.0, "f": 0.0, "category": "supplement"},
    "multivitaminico": {"name": "Multivitamínico", "p": 0.0, "c": 0.0, "f": 0.0, "category": "supplement"},
}


# ==================== FUNÇÕES AUXILIARES ====================

def round_to_multiple(value: float, multiple: int = 10) -> int:
    """Arredonda para múltiplo de N (default 10)"""
    return int(round(value / multiple) * multiple)


def calc_food(key: str, grams: float) -> Dict:
    """Calcula macros de um alimento com valores ARREDONDADOS"""
    # Arredonda gramas para múltiplo de 5
    g = max(5, round_to_multiple(grams, 5))
    
    if key not in FOODS:
        raise ValueError(f"Alimento '{key}' não encontrado no banco de dados")
    
    f = FOODS[key]
    r = g / 100.0
    
    # Calcula e ARREDONDA para inteiro
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
        "category": f.get("category", "other")
    }


def sum_foods(foods: List[Dict]) -> Tuple[int, int, int, int]:
    """Soma macros de lista de alimentos - retorna INTEIROS"""
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    fv = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return int(p), int(c), int(fv), int(cal)


def clamp(val: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, val))


# ==================== CONSISTÊNCIA ====================

def ensure_consistency(target_cal: float, target_p: float, target_c: float, target_f: float) -> Tuple[int, int, int]:
    """
    Garante que P*4 + C*4 + F*9 = target_cal.
    Retorna macros como INTEIROS múltiplos de 5.
    """
    calc_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    if abs(calc_cal - target_cal) <= 1:
        return round_to_multiple(target_p, 5), round_to_multiple(target_c, 5), round_to_multiple(target_f, 5)
    
    # Ajusta proporcionalmente
    ratio = target_cal / calc_cal
    new_p = target_p * ratio
    new_c = target_c * ratio
    new_f = target_f * ratio
    
    # Arredonda para múltiplos de 5
    final_p = round_to_multiple(new_p, 5)
    final_c = round_to_multiple(new_c, 5)
    final_f = round_to_multiple(new_f, 5)
    
    return final_p, final_c, final_f


# ==================== SELEÇÃO DE ALIMENTOS ====================

def get_available_protein(preferred_foods: Set[str]) -> str:
    """Retorna proteína disponível baseada nas preferências"""
    priority = ["frango", "carne_bovina", "tilapia", "salmao", "atum", "peru", "camarao", "suino"]
    for p in priority:
        if p in preferred_foods or not preferred_foods:
            return p
    return "frango"  # fallback


def get_available_carb(preferred_foods: Set[str]) -> str:
    """Retorna carb disponível baseada nas preferências"""
    priority = ["arroz", "batata_doce", "batata", "macarrao", "aveia"]
    for c in priority:
        if c in preferred_foods or not preferred_foods:
            return c
    return "arroz"


def get_available_fat(preferred_foods: Set[str]) -> str:
    """Retorna gordura disponível baseada nas preferências"""
    priority = ["azeite", "castanha", "amendoas", "pasta_amendoim", "abacate"]
    for f in priority:
        if f in preferred_foods or not preferred_foods:
            return f
    return "azeite"


def get_available_fruit(preferred_foods: Set[str]) -> str:
    """Retorna fruta disponível baseada nas preferências"""
    priority = ["banana", "maca", "laranja", "uva", "mamao"]
    for f in priority:
        if f in preferred_foods or not preferred_foods:
            return f
    return "banana"


# ==================== GERAÇÃO ====================

def generate_base_diet(target_p: int, target_c: int, target_f: int, preferred_foods: Set[str] = None) -> List[Dict]:
    """
    Gera dieta base usando preferências do usuário.
    Todos os valores são ARREDONDADOS.
    """
    if preferred_foods is None:
        preferred_foods = set()
    
    # Seleciona alimentos baseado nas preferências
    main_protein = get_available_protein(preferred_foods)
    main_carb = get_available_carb(preferred_foods)
    main_fat = get_available_fat(preferred_foods)
    main_fruit = get_available_fruit(preferred_foods)
    
    meals = []
    
    # ===== CAFÉ DA MANHÃ (20% P, 25% C, 30% F) =====
    cafe_p = target_p * 0.20
    cafe_c = target_c * 0.25
    cafe_f = target_f * 0.30
    
    ovos_g = clamp(cafe_p / 0.13 * 0.6, 50, 150)
    aveia_g = clamp(cafe_c * 0.3 / 0.66, 20, 80)
    fruit_g = clamp((cafe_c - aveia_g * 0.66) / 0.23, 40, 200)
    
    cafe_foods = [
        calc_food("ovos", ovos_g),
        calc_food("aveia", aveia_g),
        calc_food(main_fruit, fruit_g),
    ]
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": cafe_foods})
    
    # ===== LANCHE MANHÃ (10% P, 5% C, 20% F) =====
    lanche1_p = target_p * 0.10
    lanche1_f = target_f * 0.20
    
    iogurte_g = clamp(lanche1_p / 0.10, 50, 200)
    nut_g = clamp((lanche1_f - iogurte_g * 0.05) / 0.67, 5, 40)
    
    lanche1_foods = [
        calc_food("iogurte", iogurte_g),
        calc_food("castanha", nut_g),
    ]
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": lanche1_foods})
    
    # ===== ALMOÇO (30% P, 35% C, 25% F) =====
    almoco_p = target_p * 0.30
    almoco_c = target_c * 0.35
    almoco_f = target_f * 0.25
    
    protein_g = clamp(almoco_p / (FOODS[main_protein]["p"] / 100), 75, 300)
    carb_g = clamp(almoco_c * 0.6 / (FOODS[main_carb]["c"] / 100), 75, 400)
    feijao_g = clamp(almoco_c * 0.25 / 0.14, 30, 150)
    azeite_g = clamp(almoco_f - protein_g * (FOODS[main_protein]["f"] / 100), 3, 15)
    
    almoco_foods = [
        calc_food(main_protein, protein_g),
        calc_food(main_carb, carb_g),
        calc_food("feijao", feijao_g),
        calc_food("salada", 100),
        calc_food("azeite", azeite_g),
    ]
    meals.append({"name": "Almoço", "time": "12:30", "foods": almoco_foods})
    
    # ===== LANCHE TARDE (15% P, 20% C, 5% F) =====
    lanche2_p = target_p * 0.15
    lanche2_c = target_c * 0.20
    
    batata_g = clamp(lanche2_c / 0.20, 50, 400)
    protein2_g = clamp(lanche2_p / (FOODS[main_protein]["p"] / 100), 50, 200)
    
    lanche2_foods = [
        calc_food("batata_doce", batata_g),
        calc_food(main_protein, protein2_g),
    ]
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": lanche2_foods})
    
    # ===== JANTAR (25% P, 15% C, 20% F) =====
    jantar_p = target_p * 0.25
    jantar_c = target_c * 0.15
    jantar_f = target_f * 0.20
    
    # Usa proteína diferente se possível
    alt_protein = "tilapia" if main_protein != "tilapia" and ("tilapia" in preferred_foods or not preferred_foods) else main_protein
    
    protein3_g = clamp(jantar_p / (FOODS[alt_protein]["p"] / 100), 75, 300)
    carb2_g = clamp(jantar_c / (FOODS[main_carb]["c"] / 100), 50, 250)
    azeite2_g = clamp(jantar_f - protein3_g * (FOODS[alt_protein]["f"] / 100), 3, 15)
    
    jantar_foods = [
        calc_food(alt_protein, protein3_g),
        calc_food(main_carb, carb2_g),
        calc_food("brocolis", 100),
        calc_food("azeite", azeite2_g),
    ]
    meals.append({"name": "Jantar", "time": "19:30", "foods": jantar_foods})
    
    return meals


def fine_tune_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int, max_iter: int = 500) -> List[Dict]:
    """Ajuste fino iterativo com valores ARREDONDADOS."""
    target_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    for _ in range(max_iter):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        gap_cal = target_cal - curr_cal
        
        # Verifica tolerâncias
        if abs(gap_p) <= TOL_P and abs(gap_c) <= TOL_C and abs(gap_f) <= TOL_F and abs(gap_cal) <= TOL_CAL:
            return meals
        
        adjusted = False
        
        # Ajusta o macro com maior gap relativo
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
                for m_idx in [2, 3, 4]:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food.get("category") == "protein" or food["key"] in ["frango", "tilapia", "carne_bovina", "ovos"]:
                            food_key = food["key"]
                            if food_key in FOODS:
                                p_per_100 = FOODS[food_key]["p"]
                                delta = gap / (p_per_100 / 100)
                                new_g = clamp(food["grams"] + delta, 50, 400)
                                if abs(new_g - food["grams"]) >= 10:
                                    meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                    adjusted = True
                                    break
                    if adjusted:
                        break
            
            elif macro == "c" and abs(gap) > TOL_C:
                # Ajusta carboidratos
                for m_idx, key in [(3, "batata_doce"), (2, "arroz"), (4, "arroz"), (0, "aveia")]:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["key"] == key or (food.get("category") == "carb" and food["key"] in FOODS):
                            food_key = food["key"]
                            c_per_100 = FOODS[food_key]["c"]
                            delta = gap / (c_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 20, 500)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food_key, new_g)
                                adjusted = True
                                break
                    if adjusted:
                        break
            
            elif macro == "f" and abs(gap) > TOL_F:
                # Ajusta gorduras (azeite primeiro)
                for m_idx in [2, 4, 1]:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["key"] == "azeite":
                            new_g = clamp(food["grams"] + gap, 1, 20)
                            if abs(new_g - food["grams"]) >= 1:
                                meals[m_idx]["foods"][f_idx] = calc_food("azeite", new_g)
                                adjusted = True
                                break
                    if adjusted:
                        break
                
                # Tenta castanha
                if not adjusted:
                    for f_idx, food in enumerate(meals[1]["foods"]):
                        if food["key"] == "castanha":
                            delta = gap / 0.67
                            new_g = clamp(food["grams"] + delta, 5, 60)
                            if abs(new_g - food["grams"]) >= 3:
                                meals[1]["foods"][f_idx] = calc_food("castanha", new_g)
                                adjusted = True
                                break
        
        if not adjusted:
            break
    
    return meals


# ==================== VALIDAÇÃO ====================

def validate_diet(meals: List[Dict], target_p: int, target_c: int, target_f: int) -> Tuple[bool, str]:
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    target_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    errors = []
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P:{curr_p}g vs {target_p}g")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C:{curr_c}g vs {target_c}g")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F:{curr_f}g vs {target_f}g")
    if abs(curr_cal - target_cal) > TOL_CAL:
        errors.append(f"Cal:{curr_cal} vs {target_cal}")
    
    return len(errors) == 0, "; ".join(errors)


# ==================== SERVICE ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        # Obtém preferências do usuário
        food_preferences = user_profile.get('food_preferences', [])
        preferred_foods = get_user_preferred_foods(food_preferences)
        
        # Garante consistência entre macros e calorias
        adjusted_p, adjusted_c, adjusted_f = ensure_consistency(
            target_calories,
            target_macros["protein"],
            target_macros["carbs"],
            target_macros["fat"]
        )
        
        # Target de calorias INTEIRO
        target_cal_int = int(round(target_calories))
        
        # Gera dieta base com preferências
        meals = generate_base_diet(adjusted_p, adjusted_c, adjusted_f, preferred_foods)
        
        # Fine-tune
        meals = fine_tune_diet(meals, adjusted_p, adjusted_c, adjusted_f, max_iter=500)
        
        # Valida
        is_valid, error = validate_diet(meals, adjusted_p, adjusted_c, adjusted_f)
        
        if not is_valid:
            raise ValueError(f"Impossível fechar macros: {error}")
        
        # Formata resultado com valores INTEIROS
        final_meals = []
        for m in meals:
            mp, mc, mf, mcal = sum_foods(m["foods"])
            final_meals.append(Meal(
                name=m["name"],
                time=m["time"],
                foods=m["foods"],
                total_calories=mcal,  # Já é inteiro
                macros={"protein": mp, "carbs": mc, "fat": mf}  # Já são inteiros
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
            notes=f"Dieta: {total_cal}kcal | P:{total_p}g C:{total_c}g G:{total_f}g"
        )
