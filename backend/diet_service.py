"""
Sistema de Geração de Dieta - V9 FECHAMENTO GARANTIDO

INSIGHT CRÍTICO:
- Calorias = P*4 + C*4 + F*9
- Se P, C, F estão corretos, calorias DEVEM estar corretas
- O problema é que os targets de macros podem não somar corretamente às calorias target

ESTRATÉGIA:
1. Primeiro valida se macros x calorias são consistentes
2. Se inconsistente, ajusta macros proporcionalmente
3. Então gera a dieta com macros corrigidos
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
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0},
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5},
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0},
    "castanha": {"name": "Castanha", "p": 14.0, "c": 12.0, "f": 67.0},
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2},
}


def calc_food(key: str, grams: float) -> Dict:
    g = max(1, round(grams))
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


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    fv = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, fv, cal


def clamp(val: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, val))


# ==================== CONSISTÊNCIA ====================

def ensure_consistency(target_cal: float, target_p: float, target_c: float, target_f: float) -> Tuple[float, float, float]:
    """
    Garante que P*4 + C*4 + F*9 = target_cal.
    Ajusta macros proporcionalmente se necessário.
    """
    calc_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    if abs(calc_cal - target_cal) <= 1:
        return target_p, target_c, target_f
    
    # Ajusta proporcionalmente
    ratio = target_cal / calc_cal
    new_p = target_p * ratio
    new_c = target_c * ratio
    new_f = target_f * ratio
    
    # Verifica novamente
    verify_cal = new_p * 4 + new_c * 4 + new_f * 9
    
    # Ajuste fino na gordura para fechar exatamente
    if abs(verify_cal - target_cal) > 0.1:
        diff = target_cal - (new_p * 4 + new_c * 4)
        new_f = diff / 9
    
    return round(new_p, 1), round(new_c, 1), round(new_f, 1)


# ==================== GERAÇÃO ====================

def generate_base_diet(target_p: float, target_c: float, target_f: float) -> List[Dict]:
    """
    Gera dieta base usando proporções calculadas.
    """
    
    # ESTRUTURA DE 5 REFEIÇÕES
    # Cada refeição tem proporção fixa dos macros totais
    
    # Alimentos por refeição com suas funções:
    # - Proteína pura: frango (31P), tilápia (26P), clara (11P)
    # - Proteína mista: ovos (13P, 11F), iogurte (10P, 5F)
    # - Carb puro: arroz (23C), batata (20C), banana (23C)
    # - Carb misto: aveia (13.5P, 66C, 7F)
    # - Gordura pura: azeite (100F)
    # - Gordura mista: castanha (14P, 12C, 67F)
    
    meals = []
    
    # ===== CAFÉ DA MANHÃ (20% P, 25% C, 30% F) =====
    cafe_p = target_p * 0.20
    cafe_c = target_c * 0.25
    cafe_f = target_f * 0.30
    
    # Ovos contribuem P e F
    ovos_g = clamp(cafe_p / 0.13 * 0.6, 50, 150)  # 60% da proteína via ovos
    ovos_p = FOODS["ovos"]["p"] * ovos_g / 100
    ovos_f = FOODS["ovos"]["f"] * ovos_g / 100
    
    # Aveia para carbs e proteína extra
    aveia_g = clamp(cafe_c * 0.3 / 0.66, 20, 80)
    aveia_p = FOODS["aveia"]["p"] * aveia_g / 100
    aveia_c = FOODS["aveia"]["c"] * aveia_g / 100
    aveia_f = FOODS["aveia"]["f"] * aveia_g / 100
    
    # Banana para carbs
    remaining_c = cafe_c - aveia_c
    banana_g = clamp(remaining_c / 0.23, 40, 200)
    
    cafe_foods = [
        calc_food("ovos", ovos_g),
        calc_food("aveia", aveia_g),
        calc_food("banana", banana_g),
    ]
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": cafe_foods})
    
    # ===== LANCHE MANHÃ (10% P, 5% C, 20% F) =====
    lanche1_p = target_p * 0.10
    lanche1_f = target_f * 0.20
    
    # Iogurte
    iogurte_g = clamp(lanche1_p / 0.10, 50, 200)
    
    # Castanha para gordura
    remaining_f = lanche1_f - (FOODS["iogurte"]["f"] * iogurte_g / 100)
    castanha_g = clamp(remaining_f / 0.67, 5, 40)
    
    lanche1_foods = [
        calc_food("iogurte", iogurte_g),
        calc_food("castanha", castanha_g),
    ]
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": lanche1_foods})
    
    # ===== ALMOÇO (30% P, 35% C, 25% F) =====
    almoco_p = target_p * 0.30
    almoco_c = target_c * 0.35
    almoco_f = target_f * 0.25
    
    # Frango para proteína
    frango_almoco = clamp(almoco_p / 0.31, 75, 300)
    frango_f = FOODS["frango"]["f"] * frango_almoco / 100
    
    # Arroz para carbs
    arroz_almoco = clamp(almoco_c * 0.6 / 0.23, 75, 400)
    
    # Feijão
    feijao_g = clamp(almoco_c * 0.25 / 0.14, 30, 150)
    
    # Azeite para gordura
    remaining_f = almoco_f - frango_f - (FOODS["arroz"]["f"] * arroz_almoco / 100)
    azeite_almoco = clamp(remaining_f, 3, 15)
    
    almoco_foods = [
        calc_food("frango", frango_almoco),
        calc_food("arroz", arroz_almoco),
        calc_food("feijao", feijao_g),
        calc_food("salada", 100),
        calc_food("azeite", azeite_almoco),
    ]
    meals.append({"name": "Almoço", "time": "12:30", "foods": almoco_foods})
    
    # ===== LANCHE TARDE (15% P, 20% C, 5% F) =====
    lanche2_p = target_p * 0.15
    lanche2_c = target_c * 0.20
    
    # Batata para carbs
    batata_g = clamp(lanche2_c / 0.20, 50, 400)
    
    # Frango para proteína
    frango_lanche = clamp(lanche2_p / 0.31, 50, 200)
    
    lanche2_foods = [
        calc_food("batata", batata_g),
        calc_food("frango", frango_lanche),
    ]
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": lanche2_foods})
    
    # ===== JANTAR (25% P, 15% C, 20% F) =====
    jantar_p = target_p * 0.25
    jantar_c = target_c * 0.15
    jantar_f = target_f * 0.20
    
    # Tilápia ou frango
    tilapia_g = clamp(jantar_p / 0.26, 75, 300)
    tilapia_f = FOODS["tilapia"]["f"] * tilapia_g / 100
    
    # Arroz
    arroz_jantar = clamp(jantar_c / 0.23, 50, 250)
    
    # Azeite
    remaining_f = jantar_f - tilapia_f - (FOODS["arroz"]["f"] * arroz_jantar / 100)
    azeite_jantar = clamp(remaining_f, 3, 15)
    
    jantar_foods = [
        calc_food("tilapia", tilapia_g),
        calc_food("arroz", arroz_jantar),
        calc_food("brocolis", 100),
        calc_food("azeite", azeite_jantar),
    ]
    meals.append({"name": "Jantar", "time": "19:30", "foods": jantar_foods})
    
    return meals


def fine_tune_diet(meals: List[Dict], target_p: float, target_c: float, target_f: float, max_iter: int = 500) -> List[Dict]:
    """
    Ajuste fino iterativo.
    """
    
    for _ in range(max_iter):
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, _ = sum_foods(all_foods)
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Verifica tolerâncias
        if abs(gap_p) <= TOL_P and abs(gap_c) <= TOL_C and abs(gap_f) <= TOL_F:
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
                # Ajusta frango ou tilápia
                for m_idx in [2, 3, 4]:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["key"] in ["frango", "tilapia"]:
                            p_per_100 = FOODS[food["key"]]["p"]
                            delta = gap / (p_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 50, 400)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(food["key"], round(new_g))
                                adjusted = True
                                break
                    if adjusted:
                        break
                
                # Se não ajustou, tenta clara
                if not adjusted and gap > 5:
                    for m_idx in [0, 2]:
                        has_clara = any(f["key"] == "clara" for f in meals[m_idx]["foods"])
                        if not has_clara:
                            clara_g = clamp(gap / 0.11, 30, 200)
                            meals[m_idx]["foods"].append(calc_food("clara", round(clara_g)))
                            adjusted = True
                            break
                        else:
                            for f_idx, food in enumerate(meals[m_idx]["foods"]):
                                if food["key"] == "clara":
                                    delta = gap / 0.11
                                    new_g = clamp(food["grams"] + delta, 30, 300)
                                    meals[m_idx]["foods"][f_idx] = calc_food("clara", round(new_g))
                                    adjusted = True
                                    break
                        if adjusted:
                            break
            
            elif macro == "c" and abs(gap) > TOL_C:
                # Ajusta arroz, batata, aveia, banana
                for m_idx, key in [(3, "batata"), (2, "arroz"), (4, "arroz"), (0, "aveia"), (0, "banana")]:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["key"] == key:
                            c_per_100 = FOODS[key]["c"]
                            delta = gap / (c_per_100 / 100)
                            new_g = clamp(food["grams"] + delta, 20, 500)
                            if abs(new_g - food["grams"]) >= 10:
                                meals[m_idx]["foods"][f_idx] = calc_food(key, round(new_g))
                                adjusted = True
                                break
                    if adjusted:
                        break
            
            elif macro == "f" and abs(gap) > TOL_F:
                # Ajusta azeite primeiro
                for m_idx in [2, 4, 1]:
                    for f_idx, food in enumerate(meals[m_idx]["foods"]):
                        if food["key"] == "azeite":
                            new_g = clamp(food["grams"] + gap, 1, 20)
                            if abs(new_g - food["grams"]) >= 1:
                                meals[m_idx]["foods"][f_idx] = calc_food("azeite", round(new_g))
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
                                meals[1]["foods"][f_idx] = calc_food("castanha", round(new_g))
                                adjusted = True
                                break
                
                # Ajusta ovos se precisa reduzir gordura
                if not adjusted and gap < -3:
                    for f_idx, food in enumerate(meals[0]["foods"]):
                        if food["key"] == "ovos":
                            delta = gap / 0.11
                            new_g = clamp(food["grams"] + delta, 50, 200)
                            if abs(new_g - food["grams"]) >= 25:
                                meals[0]["foods"][f_idx] = calc_food("ovos", round(new_g))
                                adjusted = True
                                break
        
        if not adjusted:
            break
    
    return meals


# ==================== VALIDAÇÃO ====================

def validate_diet(meals: List[Dict], target_p: float, target_c: float, target_f: float) -> Tuple[bool, str]:
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    target_cal = target_p * 4 + target_c * 4 + target_f * 9
    
    errors = []
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P:{curr_p:.1f}g vs {target_p}g")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C:{curr_c:.1f}g vs {target_c}g")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F:{curr_f:.1f}g vs {target_f}g")
    if abs(curr_cal - target_cal) > TOL_CAL:
        errors.append(f"Cal:{curr_cal:.0f} vs {target_cal:.0f}")
    
    return len(errors) == 0, "; ".join(errors)


# ==================== SERVICE ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        # Garante consistência entre macros e calorias
        adjusted_p, adjusted_c, adjusted_f = ensure_consistency(
            target_calories,
            target_macros["protein"],
            target_macros["carbs"],
            target_macros["fat"]
        )
        
        # Gera dieta base
        meals = generate_base_diet(adjusted_p, adjusted_c, adjusted_f)
        
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
                total_calories=round(mcal, 2),
                macros={"protein": round(mp, 2), "carbs": round(mc, 2), "fat": round(mf, 2)}
            ))
        
        all_foods = [f for m in meals for f in m["foods"]]
        total_p, total_c, total_f, total_cal = sum_foods(all_foods)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_calories,
            target_macros={"protein": adjusted_p, "carbs": adjusted_c, "fat": adjusted_f},
            meals=final_meals,
            computed_calories=round(total_cal, 2),
            computed_macros={"protein": round(total_p, 2), "carbs": round(total_c, 2), "fat": round(total_f, 2)},
            notes=f"Dieta: {int(total_cal)}kcal | P:{int(total_p)}g C:{int(total_c)}g G:{int(total_f)}g"
        )
