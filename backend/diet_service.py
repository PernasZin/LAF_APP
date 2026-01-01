"""
Sistema de Geração de Dieta - FECHAMENTO MATEMÁTICO V4

ESTRATÉGIA:
1. P e F são ajustados com alimentos de alta pureza
2. C é usado para fechar calorias (4 cal/g vs 9 cal/g de F)
3. Iteração até convergência ou falha

EQUAÇÕES:
- Cal = P*4 + C*4 + F*9
- Logo: C = (Cal - P*4 - F*9) / 4

Se definimos P e F primeiro, C é determinado!
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
    # PROTEÍNAS (ordenados por pureza P)
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 250, "step": 30},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 50, "max": 300, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 50, "max": 250, "step": 25},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 200, "step": 50},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 100, "max": 250, "step": 50},
    
    # CARBOIDRATOS (ordenados por pureza C)
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
    """Calcula nutrientes"""
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
    return max(step, int(round(val / step) * step))


def clamp(val: int, mn: int, mx: int) -> int:
    return max(mn, min(mx, val))


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    f = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, f, cal


# ==================== CORE ALGORITHM ====================

def build_diet(target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Constrói dieta atingindo macros por design.
    
    ESTRATÉGIA:
    1. Distribui proteína entre frango, tilápia, ovos, iogurte
    2. Distribui gordura entre azeite, castanha, ovos
    3. Calcula carbs necessários para atingir calorias
    4. Distribui carbs entre arroz, batata, aveia, banana
    5. Ajusta iterativamente
    """
    
    # STEP 1: Calcula contribuição base de cada fonte
    
    # Proteína: frango(31), tilápia(26), clara(11), ovos(13), iogurte(10)
    # Vamos usar:
    # - Frango: 40% da P
    # - Tilápia: 25% da P  
    # - Ovos: 15% da P (contribui F também)
    # - Iogurte: 10% da P
    # - Clara: 10% da P (ajuste fino)
    
    frango_g = rnd((target_p * 0.40 / 0.31) * 100 / 100, 25)
    tilapia_g = rnd((target_p * 0.25 / 0.26) * 100 / 100, 25)
    ovos_g = rnd((target_p * 0.15 / 0.13) * 100 / 100, 50)
    iogurte_g = rnd((target_p * 0.10 / 0.10) * 100 / 100, 50)
    
    # Aplica limites
    frango_g = clamp(frango_g, 100, 275)
    tilapia_g = clamp(tilapia_g, 100, 200)
    ovos_g = clamp(ovos_g, 50, 150)
    iogurte_g = clamp(iogurte_g, 100, 200)
    
    # Calcula P atual de proteínas fixas
    p_from_fixed = (frango_g * 0.31 + tilapia_g * 0.26 + ovos_g * 0.13 + iogurte_g * 0.10)
    
    # Clara para ajuste fino (se necessário)
    p_gap = target_p - p_from_fixed
    clara_g = 0
    if p_gap > 3:
        clara_g = clamp(rnd((p_gap / 0.11) * 100 / 100, 30), 30, 200)
    
    # Gordura: azeite(100), castanha(67), ovos já conta
    # F dos ovos = ovos_g * 0.11
    f_from_ovos = ovos_g * 0.11 / 100  # já em g
    f_remaining = target_f - f_from_ovos
    
    # Azeite: até 30g total (3x 10g por refeição principal)
    # Castanha: até 25g
    azeite_total = min(f_remaining * 0.70, 30)  # 70% do restante em azeite
    castanha_g = clamp(rnd((f_remaining * 0.30 / 0.67) * 100 / 100, 5), 10, 25)
    
    f_from_cast = castanha_g * 0.67 / 100
    azeite_g = clamp(rnd((f_remaining - f_from_cast) / 1.0, 5), 10, 30)
    
    # Carboidratos: precisamos calcular quanto falta para fechar calorias
    # Cal = P*4 + C*4 + F*9
    # C = (Cal - P*4 - F*9) / 4
    
    # Calcula P e F atuais (aproximados)
    current_p = p_from_fixed + (clara_g * 0.11 / 100)
    current_f = f_from_ovos + f_from_cast + (azeite_g * 1.0 / 100)
    
    needed_c = (target_cal - current_p * 4 - current_f * 9) / 4
    needed_c = max(50, needed_c)  # Mínimo 50g de carbs
    
    # Distribui carbs: arroz(23), batata(20), aveia(66), banana(23), feijão(14)
    # - Arroz: 35%
    # - Batata: 30%
    # - Aveia: 15%
    # - Banana: 10%
    # - Feijão: 10%
    
    arroz_g = clamp(rnd((needed_c * 0.35 / 0.23) * 100 / 100, 25), 100, 350)
    batata_g = clamp(rnd((needed_c * 0.30 / 0.20) * 100 / 100, 25), 100, 400)
    aveia_g = clamp(rnd((needed_c * 0.15 / 0.66) * 100 / 100, 10), 30, 80)
    banana_g = clamp(rnd((needed_c * 0.10 / 0.23) * 100 / 100, 40), 80, 160)
    feijao_g = clamp(rnd((needed_c * 0.10 / 0.14) * 100 / 100, 30), 60, 150)
    
    # Divide azeite em 3 refeições
    azeite_almoco = clamp(rnd(azeite_g * 0.40, 5), 5, 15)
    azeite_jantar = clamp(rnd(azeite_g * 0.40, 5), 5, 15)
    azeite_cafe = min(15, azeite_g - azeite_almoco - azeite_jantar) if azeite_g > azeite_almoco + azeite_jantar else 0
    
    # Divide frango em 2 refeições
    frango_almoco = clamp(rnd(frango_g * 0.55, 25), 75, 200)
    frango_lanche = frango_g - frango_almoco
    frango_lanche = clamp(frango_lanche, 50, 175)
    
    # Divide arroz em 2 refeições
    arroz_almoco = clamp(rnd(arroz_g * 0.55, 25), 75, 250)
    arroz_jantar = clamp(arroz_g - arroz_almoco, 50, 200)
    
    # ===== MONTA REFEIÇÕES =====
    
    meals = []
    
    # CAFÉ DA MANHÃ
    cafe = {"name": "Café da Manhã", "time": "07:00", "foods": []}
    cafe["foods"].append(calc("ovos", ovos_g))
    cafe["foods"].append(calc("aveia", aveia_g))
    cafe["foods"].append(calc("banana", banana_g))
    if clara_g > 0:
        cafe["foods"].append(calc("clara", clara_g))
    meals.append(cafe)
    
    # LANCHE MANHÃ
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
    
    # LANCHE TARDE
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
    """
    Ajuste fino iterativo para fechar gaps.
    """
    for _ in range(50):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        # Verifica se está OK
        if (abs(curr_p - target_p) <= TOL_P and 
            abs(curr_c - target_c) <= TOL_C and 
            abs(curr_f - target_f) <= TOL_F and
            abs(curr_cal - target_cal) <= TOL_CAL):
            return meals
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        gap_cal = target_cal - curr_cal
        
        adjusted = False
        
        # Ajusta PROTEÍNA primeiro (maior impacto)
        if abs(gap_p) > TOL_P:
            # Ajusta frango ou adiciona clara
            for m_idx in [2, 3]:  # Almoço, Lanche tarde
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "frango":
                        info = FOODS["frango"]
                        delta = rnd(gap_p / 0.31, info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("frango", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # Ajusta GORDURA
        if not adjusted and abs(gap_f) > TOL_F:
            for m_idx in [2, 4]:  # Almoço, Jantar
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "azeite":
                        info = FOODS["azeite"]
                        delta = rnd(gap_f / 1.0, info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("azeite", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # Ajusta CARBS (para fechar calorias)
        if not adjusted and (abs(gap_c) > TOL_C or abs(gap_cal) > TOL_CAL):
            for m_idx in [2, 4, 3]:  # Almoço, Jantar, Lanche
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] in ["arroz", "batata"]:
                        info = FOODS[food["key"]]
                        c_per_100 = info["c"]
                        delta = rnd(gap_c / (c_per_100 / 100), info["step"])
                        new_g = clamp(food["grams"] + delta, info["min"], info["max"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc(food["key"], new_g)
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
