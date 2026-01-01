"""
Sistema de Geração de Dieta - FECHAMENTO EXATO V6

ESTRATÉGIA SIMPLIFICADA:
1. Calcular diretamente as quantidades necessárias de cada alimento
2. Usar proporções matemáticas corretas
3. Ajuste fino iterativo para fechar tolerâncias
"""

import os
from typing import List, Dict, Tuple, Optional
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
    notes: Optional[str] = None


class DietGenerateRequest(BaseModel):
    user_id: str


# ==================== TOLERANCES ====================

TOL_P = 3.0
TOL_C = 3.0
TOL_F = 2.0
TOL_CAL = 25.0


# ==================== FOOD DATABASE ====================

FOODS = {
    # PROTEÍNAS - limites ampliados para bulking
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 250, "step": 30},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 75, "max": 350, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 75, "max": 300, "step": 25},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 200, "step": 50},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 100, "max": 250, "step": 50},
    
    # CARBOIDRATOS - limites ampliados para alto volume calórico
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "min": 75, "max": 500, "step": 25},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "min": 75, "max": 450, "step": 25},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "min": 80, "max": 240, "step": 40},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "min": 30, "max": 100, "step": 10},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5, "min": 60, "max": 180, "step": 30},
    
    # GORDURAS - azeite limitado a 15g por refeição (max 45g total)
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0, "min": 5, "max": 15, "step": 5},
    "castanha": {"name": "Castanha", "p": 14.0, "c": 12.0, "f": 67.0, "min": 10, "max": 30, "step": 5},
    
    # VEGETAIS
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "min": 80, "max": 150, "step": 25},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "min": 80, "max": 150, "step": 25},
}


def calc(key: str, g: int) -> Dict:
    f = FOODS[key]
    r = g / 100.0
    return {
        "key": key, "name": f["name"], "quantity": f"{g}g", "grams": g,
        "protein": round(f["p"] * r, 2),
        "carbs": round(f["c"] * r, 2),
        "fat": round(f["f"] * r, 2),
        "calories": round((f["p"]*4 + f["c"]*4 + f["f"]*9) * r, 2)
    }


def rnd(val: float, step: int) -> int:
    return max(step, int(round(val / step) * step))


def clamp(val: int, mn: int, mx: int) -> int:
    return max(mn, min(mx, val))


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    fv = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, fv, cal


# ==================== SIMPLIFIED BUILD ====================

def build_diet(target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Constrói dieta de forma simples e direta.
    """
    
    # Escala base para targets
    # Template base (aproximadamente 2000kcal, 150P, 200C, 60F)
    
    # Fatores de escala
    scale_p = target_p / 150.0
    scale_c = target_c / 200.0
    scale_f = target_f / 60.0
    scale_cal = target_cal / 2000.0
    
    # CAFÉ DA MANHÃ
    ovos_g = clamp(rnd(100 * scale_p, 50), 50, 150)
    aveia_g = clamp(rnd(40 * scale_c, 10), 30, 70)
    banana_g = clamp(rnd(100 * scale_c, 40), 80, 160)
    
    cafe = {"name": "Café da Manhã", "time": "07:00", "foods": [
        calc("ovos", ovos_g),
        calc("aveia", aveia_g),
        calc("banana", banana_g),
    ]}
    
    # LANCHE MANHÃ
    iogurte_g = clamp(rnd(150 * scale_p, 50), 100, 200)
    castanha_g = clamp(rnd(15 * scale_f, 5), 10, 25)
    
    lanche1 = {"name": "Lanche Manhã", "time": "10:00", "foods": [
        calc("iogurte", iogurte_g),
        calc("castanha", castanha_g),
    ]}
    
    # ALMOÇO
    frango_almoco = clamp(rnd(120 * scale_p, 25), 100, 200)
    arroz_almoco = clamp(rnd(150 * scale_c, 25), 125, 250)
    feijao_g = clamp(rnd(80 * scale_c, 30), 60, 120)
    azeite_almoco = clamp(rnd(10 * scale_f, 5), 5, 15)
    
    almoco = {"name": "Almoço", "time": "12:30", "foods": [
        calc("frango", frango_almoco),
        calc("arroz", arroz_almoco),
        calc("feijao", feijao_g),
        calc("salada", 100),
        calc("azeite", azeite_almoco),
    ]}
    
    # LANCHE TARDE
    batata_g = clamp(rnd(150 * scale_c, 25), 100, 300)
    frango_lanche = clamp(rnd(80 * scale_p, 25), 75, 150)
    
    lanche2 = {"name": "Lanche Tarde", "time": "16:00", "foods": [
        calc("batata", batata_g),
        calc("frango", frango_lanche),
    ]}
    
    # JANTAR
    tilapia_g = clamp(rnd(120 * scale_p, 25), 100, 175)
    arroz_jantar = clamp(rnd(100 * scale_c, 25), 75, 200)
    azeite_jantar = clamp(rnd(10 * scale_f, 5), 5, 15)
    
    jantar = {"name": "Jantar", "time": "19:30", "foods": [
        calc("tilapia", tilapia_g),
        calc("arroz", arroz_jantar),
        calc("brocolis", 100),
        calc("azeite", azeite_jantar),
    ]}
    
    return [cafe, lanche1, almoco, lanche2, jantar]


def fine_tune(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Ajuste fino para atingir tolerâncias estritas.
    Prioriza ajustes que afetam menos outros macros.
    """
    
    for iteration in range(200):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        # Check tolerances
        p_ok = abs(curr_p - target_p) <= TOL_P
        c_ok = abs(curr_c - target_c) <= TOL_C
        f_ok = abs(curr_f - target_f) <= TOL_F
        cal_ok = abs(curr_cal - target_cal) <= TOL_CAL
        
        if p_ok and c_ok and f_ok and cal_ok:
            return meals
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        adjusted = False
        
        # 1. PROTEÍNA: usar frango (mais puro) ou tilápia
        if not p_ok and not adjusted:
            # Frango: 31g P, 0g C, 3.6g F por 100g
            target_food = "frango"
            for m_idx in [2, 3]:  # Almoço, Lanche
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == target_food:
                        info = FOODS[target_food]
                        # Calcula ajuste: gap_p / 0.31 = gramas
                        delta = int(gap_p / 0.31)
                        delta = rnd(delta, info["step"]) if delta > 0 else -rnd(abs(delta), info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc(target_food, new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
            
            # Se frango no limite, tenta tilápia
            if not adjusted:
                for f_idx, food in enumerate(meals[4]["foods"]):
                    if food["key"] == "tilapia":
                        info = FOODS["tilapia"]
                        delta = int(gap_p / 0.26)
                        delta = rnd(delta, info["step"]) if delta > 0 else -rnd(abs(delta), info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[4]["foods"][f_idx] = calc("tilapia", new_g)
                            adjusted = True
                            break
        
        # 2. GORDURA: usar azeite (puro) ou castanha
        if not f_ok and not adjusted:
            # Azeite: 0g P, 0g C, 100g F por 100g
            for m_idx in [2, 4]:  # Almoço, Jantar
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "azeite":
                        info = FOODS["azeite"]
                        delta = int(gap_f)  # 1g azeite = 1g F
                        delta = rnd(delta, info["step"]) if delta > 0 else -rnd(abs(delta), info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("azeite", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
            
            # Se azeite no limite, tenta castanha
            if not adjusted:
                for f_idx, food in enumerate(meals[1]["foods"]):
                    if food["key"] == "castanha":
                        info = FOODS["castanha"]
                        delta = int(gap_f / 0.67)
                        delta = rnd(delta, info["step"]) if delta > 0 else -rnd(abs(delta), info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[1]["foods"][f_idx] = calc("castanha", new_g)
                            adjusted = True
                            break
        
        # 3. CARBOIDRATOS: usar batata ou arroz (mais puros em C)
        if not c_ok and not adjusted:
            # Batata: 1.6g P, 20g C, 0.1g F por 100g
            # Arroz: 2.6g P, 23g C, 0.9g F por 100g
            for m_idx, key in [(3, "batata"), (2, "arroz"), (4, "arroz")]:
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == key:
                        info = FOODS[key]
                        c_per_100 = info["c"]
                        delta = int(gap_c / (c_per_100 / 100))
                        delta = rnd(delta, info["step"]) if delta > 0 else -rnd(abs(delta), info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc(key, new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        if not adjusted:
            # Não conseguiu ajustar mais - sai do loop
            break
    
    return meals


def validate(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> Tuple[bool, str]:
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    
    errors = []
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P:{curr_p:.1f}g vs {target_p}g")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C:{curr_c:.1f}g vs {target_c}g")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F:{curr_f:.1f}g vs {target_f}g")
    if abs(curr_cal - target_cal) > TOL_CAL:
        errors.append(f"Cal:{curr_cal:.1f} vs {target_cal}")
    
    return len(errors) == 0, "; ".join(errors)


# ==================== MAIN SERVICE ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        target_p = round(target_macros["protein"], 1)
        target_c = round(target_macros["carbs"], 1)
        target_f = round(target_macros["fat"], 1)
        target_cal = round(target_calories, 0)
        
        meals = build_diet(target_p, target_c, target_f, target_cal)
        meals = fine_tune(meals, target_p, target_c, target_f, target_cal)
        
        is_valid, error = validate(meals, target_p, target_c, target_f, target_cal)
        if not is_valid:
            raise ValueError(f"Impossível fechar macros: {error}")
        
        final_meals = []
        for m in meals:
            mp, mc, mf, mcal = sum_foods(m["foods"])
            meal = Meal(
                name=m["name"], time=m["time"], foods=m["foods"],
                total_calories=round(mcal, 2),
                macros={"protein": round(mp, 2), "carbs": round(mc, 2), "fat": round(mf, 2)}
            )
            final_meals.append(meal)
        
        all_foods = [f for m in meals for f in m["foods"]]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=round(total_cal, 2),
            computed_macros={"protein": round(total_p, 2), "carbs": round(total_c, 2), "fat": round(total_f, 2)},
            notes=f"Dieta: {int(total_cal)}kcal | P:{int(total_p)}g C:{int(total_c)}g G:{int(total_f)}g"
        )
