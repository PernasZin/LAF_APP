"""
Sistema de Geração de Dieta - V8 OTIMIZAÇÃO DIRETA

ESTRATÉGIA FINAL:
1. Usa sistema de equações lineares para calcular porções exatas
2. Distribui em refeições depois do cálculo total
3. Fine-tune iterativo apenas para ajustes finos
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
# Valores nutricionais por 100g

FOODS = {
    # PROTEÍNAS PURAS (alta P, baixa C/F)
    "clara": {"p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 400},
    "frango": {"p": 31.0, "c": 0.0, "f": 3.6, "min": 50, "max": 400},
    "tilapia": {"p": 26.0, "c": 0.0, "f": 2.5, "min": 50, "max": 400},
    
    # PROTEÍNAS MISTAS
    "ovos": {"p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 200},
    "iogurte": {"p": 10.0, "c": 4.0, "f": 5.0, "min": 50, "max": 300},
    
    # CARBOIDRATOS PUROS (alta C, baixa P/F)
    "batata": {"p": 1.6, "c": 20.0, "f": 0.1, "min": 50, "max": 600},
    "arroz": {"p": 2.6, "c": 23.0, "f": 0.9, "min": 50, "max": 600},
    "banana": {"p": 1.1, "c": 23.0, "f": 0.3, "min": 40, "max": 400},
    
    # CARBOIDRATOS MISTOS
    "aveia": {"p": 13.5, "c": 66.0, "f": 7.0, "min": 20, "max": 150},
    "feijao": {"p": 5.0, "c": 14.0, "f": 0.5, "min": 30, "max": 200},
    
    # GORDURAS PURAS
    "azeite": {"p": 0.0, "c": 0.0, "f": 100.0, "min": 1, "max": 50},
    
    # GORDURAS MISTAS
    "castanha": {"p": 14.0, "c": 12.0, "f": 67.0, "min": 5, "max": 60},
    
    # VEGETAIS (baixa caloria)
    "brocolis": {"p": 2.8, "c": 7.0, "f": 0.4, "min": 50, "max": 200},
    "salada": {"p": 1.5, "c": 3.0, "f": 0.2, "min": 50, "max": 200},
}

FOOD_NAMES = {
    "clara": "Clara de Ovo",
    "frango": "Peito de Frango",
    "tilapia": "Tilápia",
    "ovos": "Ovos Inteiros",
    "iogurte": "Iogurte Grego",
    "batata": "Batata Doce",
    "arroz": "Arroz Integral",
    "banana": "Banana",
    "aveia": "Aveia",
    "feijao": "Feijão",
    "azeite": "Azeite",
    "castanha": "Castanha",
    "brocolis": "Brócolis",
    "salada": "Salada Verde",
}


def calc_food(key: str, grams: float) -> Dict:
    """Calcula nutrientes para quantidade em gramas"""
    g = max(1, round(grams))
    f = FOODS[key]
    r = g / 100.0
    return {
        "key": key,
        "name": FOOD_NAMES.get(key, key),
        "quantity": f"{g}g",
        "grams": g,
        "protein": round(f["p"] * r, 2),
        "carbs": round(f["c"] * r, 2),
        "fat": round(f["f"] * r, 2),
        "calories": round((f["p"]*4 + f["c"]*4 + f["f"]*9) * r, 2)
    }


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    """Soma nutrientes de lista de alimentos"""
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    fv = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, fv, cal


def clamp(val: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, val))


# ==================== OTIMIZAÇÃO ====================

def solve_macros(target_p: float, target_c: float, target_f: float) -> Dict[str, float]:
    """
    Resolve sistema para calcular gramas de cada alimento.
    
    Usa 3 grupos principais:
    - Proteína: frango (31P, 0C, 3.6F por 100g)
    - Carboidrato: arroz (2.6P, 23C, 0.9F por 100g)
    - Gordura: azeite (0P, 0C, 100F por 100g)
    
    Ajustes secundários para equilibrar.
    """
    
    # Passo 1: Resolver o sistema básico
    # P = 0.31*frango + 0.026*arroz
    # C = 0.23*arroz
    # F = 0.036*frango + 0.009*arroz + 1.0*azeite
    
    # De C: arroz_g = target_c / 0.23
    arroz_g = target_c / 0.23
    
    # De P: frango_g = (target_p - 0.026*arroz_g) / 0.31
    frango_g = (target_p - 0.026 * arroz_g) / 0.31
    
    # De F: azeite_g = target_f - 0.036*frango_g - 0.009*arroz_g
    azeite_g = target_f - 0.036 * frango_g - 0.009 * arroz_g
    
    # Garante valores positivos
    frango_g = max(0, frango_g)
    arroz_g = max(0, arroz_g)
    azeite_g = max(0, azeite_g)
    
    # Limita azeite (máximo ~45g no dia = ~3x15g por refeição)
    if azeite_g > 45:
        # Excesso de gordura - substitui parte por castanha
        excess_f = azeite_g - 40
        azeite_g = 40
        castanha_g = (excess_f / 0.67) * 100  # 67g F por 100g castanha
        castanha_g = clamp(castanha_g, 0, 60)
    else:
        castanha_g = 0
    
    # Se azeite ficou negativo, precisa reduzir gordura de outra fonte
    if azeite_g < 0:
        # Substitui parte do frango por tilápia (menos gordura)
        deficit_f = abs(azeite_g)
        # frango: 3.6F, tilapia: 2.5F (diferença 1.1F por 100g)
        swap_g = min(frango_g * 0.3, (deficit_f / 1.1) * 100)
        tilapia_g = swap_g
        frango_g = frango_g - swap_g
        azeite_g = 0
    else:
        tilapia_g = 0
    
    return {
        "frango": frango_g,
        "arroz": arroz_g,
        "azeite": azeite_g,
        "castanha": castanha_g,
        "tilapia": tilapia_g,
    }


def distribute_to_meals(food_totals: Dict[str, float], target_p: float, target_c: float, target_f: float) -> List[Dict]:
    """
    Distribui os totais calculados em 5 refeições.
    """
    
    frango_total = food_totals.get("frango", 0)
    tilapia_total = food_totals.get("tilapia", 0)
    arroz_total = food_totals.get("arroz", 0)
    azeite_total = food_totals.get("azeite", 0)
    castanha_total = food_totals.get("castanha", 0)
    
    # Adiciona alimentos complementares fixos
    ovos_g = clamp(round(target_p * 0.35), 50, 150)  # ~10-15% da proteína
    aveia_g = clamp(round(target_c * 0.08), 20, 80)   # ~5-10% dos carbs
    banana_g = clamp(round(target_c * 0.15), 40, 200)  # ~10-15% dos carbs
    batata_g = clamp(round(target_c * 0.25), 50, 400)  # ~20-25% dos carbs
    iogurte_g = clamp(round(target_p * 0.25), 50, 200)  # ~5-10% proteína
    
    # Recalcula carbs de arroz após adicionar outros carbs
    carbs_from_extras = (
        FOODS["aveia"]["c"] * aveia_g / 100 +
        FOODS["banana"]["c"] * banana_g / 100 +
        FOODS["batata"]["c"] * batata_g / 100 +
        FOODS["ovos"]["c"] * ovos_g / 100 +
        FOODS["iogurte"]["c"] * iogurte_g / 100
    )
    arroz_needed_c = target_c - carbs_from_extras
    arroz_total = max(100, arroz_needed_c / 0.23)
    
    # Recalcula proteína após adicionar extras
    protein_from_extras = (
        FOODS["aveia"]["p"] * aveia_g / 100 +
        FOODS["ovos"]["p"] * ovos_g / 100 +
        FOODS["iogurte"]["p"] * iogurte_g / 100
    )
    protein_needed = target_p - protein_from_extras
    
    # Distribui proteína entre frango e tilápia
    if tilapia_total > 0:
        # Usa tilápia como substituto
        tilapia_contrib = FOODS["tilapia"]["p"] * tilapia_total / 100
        frango_needed_p = protein_needed - tilapia_contrib
        frango_total = max(100, frango_needed_p / 0.31)
    else:
        frango_total = max(100, protein_needed / 0.31)
        tilapia_total = 0
    
    # Recalcula gordura
    fat_from_foods = (
        FOODS["frango"]["f"] * frango_total / 100 +
        FOODS["tilapia"]["f"] * tilapia_total / 100 +
        FOODS["arroz"]["f"] * arroz_total / 100 +
        FOODS["ovos"]["f"] * ovos_g / 100 +
        FOODS["aveia"]["f"] * aveia_g / 100 +
        FOODS["iogurte"]["f"] * iogurte_g / 100 +
        FOODS["castanha"]["f"] * castanha_total / 100
    )
    azeite_total = max(0, target_f - fat_from_foods)
    
    # Limita azeite a 45g total
    azeite_total = min(45, azeite_total)
    
    # Se ainda falta gordura, adiciona mais castanha
    if azeite_total >= 45:
        remaining_f = target_f - fat_from_foods - 45
        if remaining_f > 0:
            extra_castanha = (remaining_f / 0.67) * 100
            castanha_total = min(60, castanha_total + extra_castanha)
    
    # Distribui em refeições
    meals = []
    
    # CAFÉ DA MANHÃ (07:00)
    cafe_foods = [
        calc_food("ovos", ovos_g),
        calc_food("aveia", aveia_g),
        calc_food("banana", banana_g * 0.5),
    ]
    meals.append({"name": "Café da Manhã", "time": "07:00", "foods": cafe_foods})
    
    # LANCHE MANHÃ (10:00)
    lanche1_foods = [
        calc_food("iogurte", iogurte_g),
        calc_food("castanha", castanha_total),
    ]
    meals.append({"name": "Lanche Manhã", "time": "10:00", "foods": lanche1_foods})
    
    # ALMOÇO (12:30)
    almoco_foods = [
        calc_food("frango", frango_total * 0.5),
        calc_food("arroz", arroz_total * 0.45),
        calc_food("feijao", 90),
        calc_food("salada", 100),
        calc_food("azeite", azeite_total * 0.4),
    ]
    meals.append({"name": "Almoço", "time": "12:30", "foods": almoco_foods})
    
    # LANCHE TARDE (16:00)
    lanche2_foods = [
        calc_food("batata", batata_g),
        calc_food("frango", frango_total * 0.25),
    ]
    meals.append({"name": "Lanche Tarde", "time": "16:00", "foods": lanche2_foods})
    
    # JANTAR (19:30)
    jantar_protein = frango_total * 0.25 if tilapia_total == 0 else tilapia_total
    jantar_protein_key = "frango" if tilapia_total == 0 else "tilapia"
    
    jantar_foods = [
        calc_food(jantar_protein_key, jantar_protein),
        calc_food("arroz", arroz_total * 0.55),
        calc_food("brocolis", 100),
        calc_food("azeite", azeite_total * 0.6),
    ]
    
    # Adiciona banana restante se houver
    if banana_g * 0.5 >= 40:
        jantar_foods.append(calc_food("banana", banana_g * 0.5))
    
    meals.append({"name": "Jantar", "time": "19:30", "foods": jantar_foods})
    
    return meals


def fine_tune(meals: List[Dict], target_p: float, target_c: float, target_f: float, max_iter: int = 300) -> List[Dict]:
    """
    Ajuste fino iterativo para fechar nas tolerâncias exatas.
    """
    
    for iteration in range(max_iter):
        # Soma atual
        all_foods = [f for m in meals for f in m["foods"]]
        curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Verifica se está dentro das tolerâncias
        target_cal = target_p * 4 + target_c * 4 + target_f * 9
        if abs(gap_p) <= TOL_P and abs(gap_c) <= TOL_C and abs(gap_f) <= TOL_F and abs(curr_cal - target_cal) <= TOL_CAL:
            return meals
        
        adjusted = False
        
        # 1. Ajusta PROTEÍNA se fora da tolerância
        if abs(gap_p) > TOL_P:
            # Encontra frango ou tilápia para ajustar
            for m_idx in [2, 3, 4]:  # Almoço, Lanche, Jantar
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] in ["frango", "tilapia"]:
                        p_per_g = FOODS[food["key"]]["p"] / 100
                        delta = gap_p / p_per_g
                        new_g = clamp(food["grams"] + delta, FOODS[food["key"]]["min"], FOODS[food["key"]]["max"])
                        if abs(new_g - food["grams"]) >= 5:
                            meals[m_idx]["foods"][f_idx] = calc_food(food["key"], round(new_g))
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # 2. Ajusta CARBOIDRATO se fora da tolerância
        if not adjusted and abs(gap_c) > TOL_C:
            for m_idx, key in [(3, "batata"), (2, "arroz"), (4, "arroz"), (0, "aveia")]:
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == key:
                        c_per_g = FOODS[key]["c"] / 100
                        delta = gap_c / c_per_g
                        new_g = clamp(food["grams"] + delta, FOODS[key]["min"], FOODS[key]["max"])
                        if abs(new_g - food["grams"]) >= 5:
                            meals[m_idx]["foods"][f_idx] = calc_food(key, round(new_g))
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # 3. Ajusta GORDURA se fora da tolerância
        if not adjusted and abs(gap_f) > TOL_F:
            for m_idx in [2, 4, 1]:  # Almoço, Jantar, Lanche
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "azeite":
                        new_g = clamp(food["grams"] + gap_f, 1, 20)
                        if abs(new_g - food["grams"]) >= 1:
                            meals[m_idx]["foods"][f_idx] = calc_food("azeite", round(new_g))
                            adjusted = True
                            break
                    elif food["key"] == "castanha":
                        f_per_g = FOODS["castanha"]["f"] / 100
                        delta = gap_f / f_per_g
                        new_g = clamp(food["grams"] + delta, 5, 60)
                        if abs(new_g - food["grams"]) >= 3:
                            meals[m_idx]["foods"][f_idx] = calc_food("castanha", round(new_g))
                            adjusted = True
                            break
                if adjusted:
                    break
        
        if not adjusted:
            # Tenta ajustes menores
            # Proteína via clara (muito pura)
            if abs(gap_p) > 1:
                for m_idx in [0, 2]:  # Café ou Almoço
                    has_clara = any(f["key"] == "clara" for f in meals[m_idx]["foods"])
                    if not has_clara and gap_p > 5:
                        clara_g = min(120, gap_p / 0.11)
                        meals[m_idx]["foods"].append(calc_food("clara", round(clara_g)))
                        adjusted = True
                        break
                    elif has_clara:
                        for f_idx, food in enumerate(meals[m_idx]["foods"]):
                            if food["key"] == "clara":
                                delta = gap_p / 0.11
                                new_g = clamp(food["grams"] + delta, 30, 250)
                                meals[m_idx]["foods"][f_idx] = calc_food("clara", round(new_g))
                                adjusted = True
                                break
                    if adjusted:
                        break
            
            if not adjusted:
                break
    
    return meals


# ==================== VALIDAÇÃO ====================

def validate(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> Tuple[bool, str]:
    """Valida se dieta atende tolerâncias"""
    all_foods = [f for m in meals for f in m["foods"]]
    curr_p, curr_c, curr_f, curr_cal = sum_foods(all_foods)
    
    errors = []
    if abs(curr_p - target_p) > TOL_P:
        errors.append(f"P:{curr_p:.1f}g vs {target_p}g (Δ{abs(curr_p-target_p):.1f})")
    if abs(curr_c - target_c) > TOL_C:
        errors.append(f"C:{curr_c:.1f}g vs {target_c}g (Δ{abs(curr_c-target_c):.1f})")
    if abs(curr_f - target_f) > TOL_F:
        errors.append(f"F:{curr_f:.1f}g vs {target_f}g (Δ{abs(curr_f-target_f):.1f})")
    if abs(curr_cal - target_cal) > TOL_CAL:
        errors.append(f"Cal:{curr_cal:.0f} vs {target_cal:.0f} (Δ{abs(curr_cal-target_cal):.0f})")
    
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
        
        # Calcula totais otimizados
        food_totals = solve_macros(target_p, target_c, target_f)
        
        # Distribui em refeições
        meals = distribute_to_meals(food_totals, target_p, target_c, target_f)
        
        # Fine-tune
        meals = fine_tune(meals, target_p, target_c, target_f, max_iter=500)
        
        # Valida
        is_valid, error = validate(meals, target_p, target_c, target_f, target_cal)
        
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
            target_calories=target_cal,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=round(total_cal, 2),
            computed_macros={"protein": round(total_p, 2), "carbs": round(total_c, 2), "fat": round(total_f, 2)},
            notes=f"Dieta: {int(total_cal)}kcal | P:{int(total_p)}g C:{int(total_c)}g G:{int(total_f)}g"
        )
