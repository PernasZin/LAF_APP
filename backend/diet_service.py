"""
Sistema de Geração de Dieta - FECHAMENTO MATEMÁTICO V5

CORREÇÃO: Cálculos de gramas corrigidos
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
# Nutrientes por 100g

FOODS = {
    # PROTEÍNAS
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 250, "step": 30},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 50, "max": 300, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 50, "max": 250, "step": 25},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 200, "step": 50},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 100, "max": 250, "step": 50},
    
    # CARBOIDRATOS
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "min": 50, "max": 500, "step": 25},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "min": 50, "max": 400, "step": 25},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "min": 80, "max": 240, "step": 40},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "min": 30, "max": 100, "step": 10},
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
    r = g / 100.0
    return {
        "key": key,
        "name": f["name"],
        "quantity": f"{g}g",
        "grams": g,
        "protein": round(f["p"] * r, 2),
        "carbs": round(f["c"] * r, 2),
        "fat": round(f["f"] * r, 2),
        "calories": round((f["p"]*4 + f["c"]*4 + f["f"]*9) * r, 2)
    }


def rnd(val: float, step: int) -> int:
    """Arredonda para múltiplo de step"""
    return max(step, int(round(val / step) * step))


def clamp(val: int, mn: int, mx: int) -> int:
    return max(mn, min(mx, val))


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    f_val = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, f_val, cal


def grams_for_macro(target_macro: float, macro_per_100g: float) -> float:
    """Calcula gramas necessárias para atingir quantidade de macro"""
    if macro_per_100g == 0:
        return 0
    return (target_macro / macro_per_100g) * 100


# ==================== CORE ALGORITHM ====================

def build_diet(target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Constrói dieta distribuindo macros entre alimentos.
    """
    
    # PROTEÍNA: distribuir entre frango, tilápia, ovos, iogurte
    # frango: 31g P/100g, tilápia: 26g P/100g, ovos: 13g P/100g, iogurte: 10g P/100g
    
    p_frango = target_p * 0.40  # 40% da P de frango
    p_tilapia = target_p * 0.25  # 25% de tilápia
    p_ovos = target_p * 0.15  # 15% de ovos
    p_iogurte = target_p * 0.10  # 10% de iogurte
    # Clara para ajuste fino: 10%
    
    frango_g = rnd(grams_for_macro(p_frango, 31.0), 25)
    tilapia_g = rnd(grams_for_macro(p_tilapia, 26.0), 25)
    ovos_g = rnd(grams_for_macro(p_ovos, 13.0), 50)
    iogurte_g = rnd(grams_for_macro(p_iogurte, 10.0), 50)
    
    # Aplica limites
    frango_g = clamp(frango_g, 100, 275)
    tilapia_g = clamp(tilapia_g, 75, 200)
    ovos_g = clamp(ovos_g, 50, 150)
    iogurte_g = clamp(iogurte_g, 100, 200)
    
    # Calcula P atual
    p_atual = (frango_g * 31 + tilapia_g * 26 + ovos_g * 13 + iogurte_g * 10) / 100
    p_gap = target_p - p_atual
    
    # Clara para ajuste
    clara_g = 0
    if p_gap > 5:
        clara_g = clamp(rnd(grams_for_macro(p_gap, 11.0), 30), 30, 200)
    
    # GORDURA: azeite(100g F/100g), castanha(67g F/100g), ovos já contam
    f_ovos = (ovos_g * 11) / 100  # ovos têm 11g F/100g
    f_remaining = target_f - f_ovos
    
    # Máximo 30g azeite total, 25g castanha
    castanha_g = clamp(rnd(min(15, grams_for_macro(f_remaining * 0.25, 67.0)), 5), 10, 25)
    f_castanha = (castanha_g * 67) / 100
    
    azeite_total = clamp(rnd(grams_for_macro(f_remaining - f_castanha, 100.0), 5), 15, 30)
    
    # CARBOIDRATOS: calcular para fechar calorias
    # Cal = P*4 + C*4 + F*9
    p_final = p_atual + (clara_g * 11 / 100)
    f_final = f_ovos + f_castanha + azeite_total
    
    # C = (Cal - P*4 - F*9) / 4
    c_needed = (target_cal - p_final * 4 - f_final * 9) / 4
    c_needed = max(100, c_needed)  # Mínimo 100g
    
    # Distribuir carbs: arroz(23), batata(20), aveia(66), banana(23), feijão(14)
    c_arroz = c_needed * 0.35
    c_batata = c_needed * 0.30
    c_aveia = c_needed * 0.12
    c_banana = c_needed * 0.12
    c_feijao = c_needed * 0.11
    
    arroz_g = clamp(rnd(grams_for_macro(c_arroz, 23.0), 25), 100, 350)
    batata_g = clamp(rnd(grams_for_macro(c_batata, 20.0), 25), 100, 400)
    aveia_g = clamp(rnd(grams_for_macro(c_aveia, 66.0), 10), 30, 80)
    banana_g = clamp(rnd(grams_for_macro(c_banana, 23.0), 40), 80, 160)
    feijao_g = clamp(rnd(grams_for_macro(c_feijao, 14.0), 30), 60, 150)
    
    # Divide frango
    frango_almoco = clamp(rnd(frango_g * 0.55, 25), 75, 200)
    frango_lanche = clamp(frango_g - frango_almoco, 50, 150)
    
    # Divide arroz
    arroz_almoco = clamp(rnd(arroz_g * 0.55, 25), 75, 225)
    arroz_jantar = clamp(arroz_g - arroz_almoco, 50, 175)
    
    # Divide azeite (3 refeições)
    azeite_almoco = clamp(rnd(azeite_total * 0.4, 5), 5, 15)
    azeite_jantar = clamp(rnd(azeite_total * 0.4, 5), 5, 15)
    
    # ===== MONTA REFEIÇÕES =====
    
    meals = []
    
    # CAFÉ
    cafe = {"name": "Café da Manhã", "time": "07:00", "foods": []}
    cafe["foods"].append(calc("ovos", ovos_g))
    cafe["foods"].append(calc("aveia", aveia_g))
    cafe["foods"].append(calc("banana", banana_g))
    if clara_g > 0:
        cafe["foods"].append(calc("clara", clara_g))
    meals.append(cafe)
    
    # LANCHE 1
    lanche1 = {"name": "Lanche Manhã", "time": "10:00", "foods": []}
    lanche1["foods"].append(calc("iogurte", iogurte_g))
    lanche1["foods"].append(calc("castanha", castanha_g))
    meals.append(lanche1)
    
    # ALMOÇO
    almoco = {"name": "Almoço", "time": "12:30", "foods": []}
    almoco["foods"].append(calc("frango", frango_almoco))
    almoco["foods"].append(calc("arroz", arroz_almoco))
    almoco["foods"].append(calc("feijao", feijao_g))
    almoco["foods"].append(calc("salada", 100))
    almoco["foods"].append(calc("azeite", azeite_almoco))
    meals.append(almoco)
    
    # LANCHE 2
    lanche2 = {"name": "Lanche Tarde", "time": "16:00", "foods": []}
    lanche2["foods"].append(calc("batata", batata_g))
    lanche2["foods"].append(calc("frango", frango_lanche))
    meals.append(lanche2)
    
    # JANTAR
    jantar = {"name": "Jantar", "time": "19:30", "foods": []}
    jantar["foods"].append(calc("tilapia", tilapia_g))
    jantar["foods"].append(calc("arroz", arroz_jantar))
    jantar["foods"].append(calc("brocolis", 100))
    jantar["foods"].append(calc("azeite", azeite_jantar))
    meals.append(jantar)
    
    return meals


def fine_tune(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """Ajuste fino iterativo"""
    
    for iteration in range(100):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        # Verifica tolerâncias
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
        
        # PROTEÍNA
        if not p_ok and not adjusted:
            for m_idx in [2, 3]:  # Almoço, Lanche
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "frango":
                        info = FOODS["frango"]
                        # gap_p / (31g P/100g) = gramas necessárias
                        delta = rnd(grams_for_macro(gap_p, 31.0), info["step"])
                        if gap_p < 0:
                            delta = -abs(delta)
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("frango", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
            
            # Tenta clara se frango não resolveu
            if not adjusted and abs(gap_p) > TOL_P:
                # Procura clara no café
                clara_exists = False
                for f_idx, food in enumerate(meals[0]["foods"]):
                    if food["key"] == "clara":
                        clara_exists = True
                        info = FOODS["clara"]
                        delta = rnd(grams_for_macro(gap_p, 11.0), info["step"])
                        if gap_p < 0:
                            delta = -abs(delta)
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[0]["foods"][f_idx] = calc("clara", new_g)
                            adjusted = True
                        break
                
                if not clara_exists and gap_p > 5:
                    clara_g = clamp(rnd(grams_for_macro(gap_p, 11.0), 30), 30, 150)
                    meals[0]["foods"].append(calc("clara", clara_g))
                    adjusted = True
        
        # GORDURA
        if not f_ok and not adjusted:
            for m_idx in [2, 4]:  # Almoço, Jantar
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "azeite":
                        info = FOODS["azeite"]
                        delta = rnd(grams_for_macro(gap_f, 100.0), info["step"])
                        if gap_f < 0:
                            delta = -abs(delta)
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("azeite", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # CARBOIDRATOS
        if not c_ok and not adjusted:
            for m_idx in [2, 4, 3]:  # Almoço, Jantar, Lanche
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] in ["arroz", "batata"]:
                        key = food["key"]
                        info = FOODS[key]
                        c_per_100 = info["c"]
                        delta = rnd(grams_for_macro(gap_c, c_per_100), info["step"])
                        if gap_c < 0:
                            delta = -abs(delta)
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc(key, new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        if not adjusted:
            break
    
    return meals


def validate(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> Tuple[bool, str]:
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    
    errors = []
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P:{curr_p:.1f}g vs {target_p}g (diff {abs(curr_p - target_p):.1f})")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C:{curr_c:.1f}g vs {target_c}g (diff {abs(curr_c - target_c):.1f})")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F:{curr_f:.1f}g vs {target_f}g (diff {abs(curr_f - target_f):.1f})")
    if abs(curr_cal - target_cal) > TOL_CAL:
        errors.append(f"Cal:{curr_cal:.1f} vs {target_cal} (diff {abs(curr_cal - target_cal):.1f})")
    
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
        
        # Constrói e ajusta
        meals = build_diet(target_p, target_c, target_f, target_cal)
        meals = fine_tune(meals, target_p, target_c, target_f, target_cal)
        
        # Valida
        is_valid, error = validate(meals, target_p, target_c, target_f, target_cal)
        if not is_valid:
            raise ValueError(f"Impossível fechar macros: {error}")
        
        # Converte para output
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
