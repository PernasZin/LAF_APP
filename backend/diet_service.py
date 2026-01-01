"""
Sistema de Geração de Dieta - ALGORITMO DE FECHAMENTO EXATO V3

ABORDAGEM: Sistema linear simplificado
1. Define pool de alimentos com seus macros
2. Distribui alimentos pelas refeições
3. Calcula quantidades para atingir macros EXATOS
4. Valida antes de retornar

Tolerâncias: P±3g, C±3g, F±2g, Cal±25kcal
"""

import os
from typing import List, Dict, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ==================== MODELS ====================

class Meal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    time: str
    foods: List[Dict]
    total_calories: float
    macros: Dict[str, float]


class DietPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_calories: float
    target_macros: Dict[str, float]
    meals: List[Meal]
    computed_calories: float
    computed_macros: Dict[str, float]
    notes: str = None


class DietGenerateRequest(BaseModel):
    user_id: str


# ==================== TOLERANCES ====================

TOL_P = 3.0
TOL_C = 3.0
TOL_F = 2.0
TOL_CAL = 25.0


# ==================== FOOD DATABASE ====================
# Nutrientes por 100g

FOODS = {
    # PROTEÍNAS
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 75, "max": 300, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 75, "max": 250, "step": 25},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 200, "step": 50},
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 200, "step": 30},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 100, "max": 250, "step": 50},
    
    # CARBOIDRATOS
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "min": 75, "max": 350, "step": 25},
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "min": 75, "max": 400, "step": 25},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "min": 30, "max": 100, "step": 10},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "min": 80, "max": 200, "step": 40},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5, "min": 60, "max": 180, "step": 30},
    
    # GORDURAS
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0, "min": 5, "max": 15, "step": 5},
    "castanha": {"name": "Castanha", "p": 14.0, "c": 12.0, "f": 67.0, "min": 10, "max": 30, "step": 5},
    
    # VEGETAIS
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "min": 80, "max": 150, "step": 25},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "min": 80, "max": 150, "step": 25},
}


def calc(key: str, g: int) -> Dict:
    """Calcula nutrientes para g gramas do alimento"""
    f = FOODS[key]
    ratio = g / 100.0
    return {
        "key": key,
        "name": f["name"],
        "quantity": f"{g}g",
        "grams": g,
        "protein": round(f["p"] * ratio, 2),
        "carbs": round(f["c"] * ratio, 2),
        "fat": round(f["f"] * ratio, 2),
        "calories": round((f["p"]*4 + f["c"]*4 + f["f"]*9) * ratio, 2)
    }


def rnd(val: float, step: int) -> int:
    """Arredonda para múltiplo de step"""
    return max(step, int(round(val / step) * step))


def clamp(val: int, mn: int, mx: int) -> int:
    return max(mn, min(mx, val))


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    """Retorna (P, C, F, Cal) somados"""
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    f = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, f, cal


# ==================== CORE ALGORITHM ====================

def generate_exact_diet(target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Gera dieta que atinge EXATAMENTE os macros targets.
    
    ESTRATÉGIA:
    1. Usa alimentos "puros" para cada macro principal
    2. Calcula quantidades base proporcionais
    3. Ajusta com closers (clara, batata, azeite)
    4. Itera até convergir
    """
    
    # Distribuição alvo por refeição (proporção)
    meal_ratios = [0.20, 0.10, 0.30, 0.15, 0.25]  # Café, Lanche1, Almoço, Lanche2, Jantar
    
    # PASSO 1: Calcula contribuição base de cada fonte principal
    # Vamos usar: frango/tilápia (P), arroz/batata (C), azeite (F)
    
    # Proteína: precisa de ~X gramas de frango (31g P/100g)
    frango_needed = (target_p * 0.6) / 0.31  # 60% da proteína de frango
    tilapia_needed = (target_p * 0.25) / 0.26  # 25% da proteína de tilápia
    # Resto vem de ovos, iogurte, etc.
    
    # Carbs: precisa de ~X gramas de arroz (23g C/100g) + batata (20g C/100g)
    arroz_needed = (target_c * 0.40) / 0.23  # 40% dos carbs de arroz
    batata_needed = (target_c * 0.30) / 0.20  # 30% dos carbs de batata
    # Resto vem de aveia, banana, feijão
    
    # Gordura: precisa de ~X gramas de azeite (100g F/100g)
    # Mas azeite é limitado a 15g por refeição (45g total)
    azeite_total = min(target_f * 0.35, 45)  # Max 35% de gordura ou 45g total
    azeite_needed = azeite_total / 1.0
    # Resto vem de frango, ovos, castanha
    
    # PASSO 2: Distribui nas refeições com arredondamento
    
    meals = []
    
    # ===== CAFÉ DA MANHÃ (20%) =====
    cafe_foods = []
    # Ovos: contribui P, F
    ovos_g = clamp(rnd(100, 50), 50, 150)  # 1-3 ovos
    cafe_foods.append(calc("ovos", ovos_g))
    
    # Aveia: contribui C, P
    aveia_g = clamp(rnd(50, 10), 30, 80)
    cafe_foods.append(calc("aveia", aveia_g))
    
    # Banana: contribui C
    banana_g = clamp(rnd(100, 40), 80, 160)
    cafe_foods.append(calc("banana", banana_g))
    
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": cafe_foods})
    
    # ===== LANCHE MANHÃ (10%) =====
    lanche1_foods = []
    # Iogurte: contribui P
    iogurte_g = clamp(rnd(150, 50), 100, 200)
    lanche1_foods.append(calc("iogurte", iogurte_g))
    
    # Castanha: contribui F
    castanha_g = clamp(rnd(15, 5), 10, 25)
    lanche1_foods.append(calc("castanha", castanha_g))
    
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": lanche1_foods})
    
    # ===== ALMOÇO (30%) =====
    almoco_foods = []
    # Frango: principal fonte de P
    frango_almoco = clamp(rnd(frango_needed * 0.5, 25), 100, 250)
    almoco_foods.append(calc("frango", frango_almoco))
    
    # Arroz: principal fonte de C
    arroz_almoco = clamp(rnd(arroz_needed * 0.5, 25), 100, 275)
    almoco_foods.append(calc("arroz", arroz_almoco))
    
    # Feijão
    feijao_g = clamp(rnd(90, 30), 60, 150)
    almoco_foods.append(calc("feijao", feijao_g))
    
    # Salada
    almoco_foods.append(calc("salada", 100))
    
    # Azeite
    azeite_almoco = clamp(rnd(azeite_needed * 0.35, 5), 5, 15)
    almoco_foods.append(calc("azeite", azeite_almoco))
    
    meals.append({"name": "Almoço", "time": "12:30", "foods": almoco_foods})
    
    # ===== LANCHE TARDE (15%) =====
    lanche2_foods = []
    # Batata: fonte de C
    batata_lanche = clamp(rnd(batata_needed * 0.5, 25), 100, 300)
    lanche2_foods.append(calc("batata", batata_lanche))
    
    # Frango
    frango_lanche = clamp(rnd(frango_needed * 0.25, 25), 75, 175)
    lanche2_foods.append(calc("frango", frango_lanche))
    
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": lanche2_foods})
    
    # ===== JANTAR (25%) =====
    jantar_foods = []
    # Tilápia: fonte de P
    tilapia_jantar = clamp(rnd(tilapia_needed, 25), 100, 225)
    jantar_foods.append(calc("tilapia", tilapia_jantar))
    
    # Arroz
    arroz_jantar = clamp(rnd(arroz_needed * 0.35, 25), 75, 225)
    jantar_foods.append(calc("arroz", arroz_jantar))
    
    # Brócolis
    jantar_foods.append(calc("brocolis", 100))
    
    # Azeite
    azeite_jantar = clamp(rnd(azeite_needed * 0.35, 5), 5, 15)
    jantar_foods.append(calc("azeite", azeite_jantar))
    
    meals.append({"name": "Jantar", "time": "19:30", "foods": jantar_foods})
    
    # ===== PASSO 3: AJUSTE ITERATIVO =====
    meals = adjust_to_targets(meals, target_p, target_c, target_f, target_cal)
    
    return meals


def adjust_to_targets(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Ajusta quantidades iterativamente para atingir targets.
    Usa alimentos específicos para cada macro.
    """
    
    for iteration in range(100):
        # Calcula totais atuais
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        # Verifica tolerâncias
        if (abs(curr_p - target_p) <= TOL_P and 
            abs(curr_c - target_c) <= TOL_C and 
            abs(curr_f - target_f) <= TOL_F and
            abs(curr_cal - target_cal) <= TOL_CAL):
            return meals
        
        # Calcula gaps
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Ajusta um macro por vez, priorizando maior gap relativo
        adjusted = False
        
        # PROTEÍNA - ajusta frango ou clara
        if abs(gap_p) > TOL_P and not adjusted:
            # Ajusta frango no almoço (índice 2, alimento 0)
            for meal_idx in [2, 3]:  # Almoço, Lanche tarde
                for food_idx, food in enumerate(meals[meal_idx]["foods"]):
                    if food["key"] == "frango":
                        info = FOODS["frango"]
                        curr_g = food["grams"]
                        # Calcula delta: gap_p / (31g P/100g)
                        delta_g = (gap_p / 0.31)
                        new_g = clamp(rnd(curr_g + delta_g, info["step"]), info["min"], info["max"])
                        if new_g != curr_g:
                            meals[meal_idx]["foods"][food_idx] = calc("frango", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
            
            # Se não ajustou frango, adiciona clara no café
            if not adjusted and gap_p > 5:
                # Adiciona clara no café da manhã
                clara_exists = False
                for food_idx, food in enumerate(meals[0]["foods"]):
                    if food["key"] == "clara":
                        info = FOODS["clara"]
                        curr_g = food["grams"]
                        delta_g = (gap_p / 0.11)
                        new_g = clamp(rnd(curr_g + delta_g, info["step"]), info["min"], info["max"])
                        if new_g != curr_g:
                            meals[0]["foods"][food_idx] = calc("clara", new_g)
                            adjusted = True
                        clara_exists = True
                        break
                
                if not clara_exists:
                    clara_g = clamp(rnd(gap_p / 0.11, 30), 30, 150)
                    meals[0]["foods"].append(calc("clara", clara_g))
                    adjusted = True
        
        # CARBOIDRATO - ajusta arroz ou batata
        if abs(gap_c) > TOL_C and not adjusted:
            for meal_idx in [2, 4, 3]:  # Almoço, Jantar, Lanche
                for food_idx, food in enumerate(meals[meal_idx]["foods"]):
                    if food["key"] in ["arroz", "batata"]:
                        key = food["key"]
                        info = FOODS[key]
                        curr_g = food["grams"]
                        c_per_g = info["c"] / 100
                        delta_g = gap_c / c_per_g
                        new_g = clamp(rnd(curr_g + delta_g, info["step"]), info["min"], info["max"])
                        if new_g != curr_g:
                            meals[meal_idx]["foods"][food_idx] = calc(key, new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # GORDURA - ajusta azeite ou castanha
        if abs(gap_f) > TOL_F and not adjusted:
            for meal_idx in [2, 4, 1]:  # Almoço, Jantar, Lanche1
                for food_idx, food in enumerate(meals[meal_idx]["foods"]):
                    if food["key"] == "azeite":
                        info = FOODS["azeite"]
                        curr_g = food["grams"]
                        delta_g = gap_f / 1.0  # 100g F / 100g
                        new_g = clamp(rnd(curr_g + delta_g, info["step"]), info["min"], info["max"])
                        if new_g != curr_g:
                            meals[meal_idx]["foods"][food_idx] = calc("azeite", new_g)
                            adjusted = True
                            break
                    elif food["key"] == "castanha":
                        info = FOODS["castanha"]
                        curr_g = food["grams"]
                        delta_g = gap_f / 0.67  # 67g F / 100g
                        new_g = clamp(rnd(curr_g + delta_g, info["step"]), info["min"], info["max"])
                        if new_g != curr_g:
                            meals[meal_idx]["foods"][food_idx] = calc("castanha", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        if not adjusted:
            # Não conseguiu ajustar nenhum macro, sai do loop
            break
    
    return meals


# ==================== VALIDATION ====================

def validate_diet(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> Tuple[bool, str]:
    """Valida se dieta está dentro das tolerâncias"""
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    
    errors = []
    
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P: {curr_p:.1f}g vs {target_p}g (diff {abs(curr_p - target_p):.1f}g)")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C: {curr_c:.1f}g vs {target_c}g (diff {abs(curr_c - target_c):.1f}g)")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F: {curr_f:.1f}g vs {target_f}g (diff {abs(curr_f - target_f):.1f}g)")
    if abs(curr_cal - target_cal) > TOL_CAL:
        errors.append(f"Cal: {curr_cal:.1f} vs {target_cal} (diff {abs(curr_cal - target_cal):.1f})")
    
    if errors:
        return False, "; ".join(errors)
    return True, ""


# ==================== MAIN SERVICE ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        """
        Gera plano de dieta com GARANTIA de integridade.
        Levanta ValueError se impossível atingir tolerâncias.
        """
        target_p = round(target_macros["protein"], 1)
        target_c = round(target_macros["carbs"], 1)
        target_f = round(target_macros["fat"], 1)
        target_cal = round(target_calories, 0)
        
        # Gera dieta
        meals_data = generate_exact_diet(target_p, target_c, target_f, target_cal)
        
        # Valida
        is_valid, error = validate_diet(meals_data, target_p, target_c, target_f, target_cal)
        
        if not is_valid:
            raise ValueError(f"Impossível fechar macros: {error}")
        
        # Converte para Meal objects
        final_meals = []
        for meal_data in meals_data:
            mp, mc, mf, mcal = sum_foods(meal_data["foods"])
            meal = Meal(
                name=meal_data["name"],
                time=meal_data["time"],
                foods=meal_data["foods"],
                total_calories=round(mcal, 2),
                macros={"protein": round(mp, 2), "carbs": round(mc, 2), "fat": round(mf, 2)}
            )
            final_meals.append(meal)
        
        # Calcula totais finais
        all_foods = [f for m in meals_data for f in m["foods"]]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=round(total_cal, 2),
            computed_macros={
                "protein": round(total_p, 2),
                "carbs": round(total_c, 2),
                "fat": round(total_f, 2)
            },
            notes=f"Dieta: {int(total_cal)}kcal | P:{int(total_p)}g C:{int(total_c)}g G:{int(total_f)}g"
        )
