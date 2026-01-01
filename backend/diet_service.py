"""
Sistema de Geração de Dieta - FECHAMENTO EXATO V7

ESTRATÉGIA: Otimização por refeição final
1. Gera N-1 refeições base
2. Calcula o gap para os targets
3. Constrói a última refeição para fechar exatamente
4. Usa retry com diferentes templates se falhar
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
    # PROTEÍNAS
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 300, "step": 30},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 50, "max": 400, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 50, "max": 350, "step": 25},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 200, "step": 50},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 50, "max": 300, "step": 50},
    
    # CARBOIDRATOS
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "min": 50, "max": 500, "step": 25},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "min": 50, "max": 500, "step": 25},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "min": 40, "max": 300, "step": 40},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "min": 20, "max": 120, "step": 10},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5, "min": 30, "max": 200, "step": 30},
    
    # GORDURAS
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0, "min": 3, "max": 15, "step": 1},
    "castanha": {"name": "Castanha", "p": 14.0, "c": 12.0, "f": 67.0, "min": 5, "max": 40, "step": 5},
    
    # VEGETAIS (baixa caloria)
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "min": 50, "max": 200, "step": 25},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "min": 50, "max": 200, "step": 25},
}


def calc(key: str, g: float) -> Dict:
    """Calcula nutrientes para quantidade em gramas"""
    g = max(1, round(g))  # Garante pelo menos 1g
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


def clamp(val: float, mn: float, mx: float) -> float:
    """Limita valor entre min e max"""
    return max(mn, min(mx, val))


def sum_foods(foods: List[Dict]) -> Tuple[float, float, float, float]:
    """Soma nutrientes de lista de alimentos"""
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    fv = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, fv, cal


def sum_meals(meals: List[Dict]) -> Tuple[float, float, float, float]:
    """Soma nutrientes de lista de refeições"""
    all_foods = [f for m in meals for f in m["foods"]]
    return sum_foods(all_foods)


# ==================== TEMPLATES ====================

def get_template_standard(scale_p: float, scale_c: float, scale_f: float) -> List[Dict]:
    """Template padrão: 5 refeições balanceadas"""
    
    # Café (15% P, 25% C, 30% F)
    cafe = {"name": "Café da Manhã", "time": "07:00", "foods": [
        calc("ovos", clamp(rnd(100 * scale_p * 0.8, 50), 50, 150)),
        calc("aveia", clamp(rnd(40 * scale_c, 10), 20, 70)),
        calc("banana", clamp(rnd(80 * scale_c, 40), 40, 160)),
    ]}
    
    # Lanche 1 (10% P, 5% C, 20% F)
    lanche1 = {"name": "Lanche Manhã", "time": "10:00", "foods": [
        calc("iogurte", clamp(rnd(120 * scale_p, 50), 50, 200)),
        calc("castanha", clamp(rnd(15 * scale_f, 5), 5, 30)),
    ]}
    
    # Almoço (30% P, 35% C, 25% F)
    almoco = {"name": "Almoço", "time": "12:30", "foods": [
        calc("frango", clamp(rnd(130 * scale_p, 25), 75, 250)),
        calc("arroz", clamp(rnd(150 * scale_c, 25), 75, 300)),
        calc("feijao", clamp(rnd(60 * scale_c, 30), 30, 120)),
        calc("salada", 100),
        calc("azeite", clamp(rnd(8 * scale_f, 1), 3, 12)),
    ]}
    
    # Lanche 2 (20% P, 20% C, 5% F)
    lanche2 = {"name": "Lanche Tarde", "time": "16:00", "foods": [
        calc("batata", clamp(rnd(130 * scale_c, 25), 75, 300)),
        calc("frango", clamp(rnd(90 * scale_p, 25), 50, 175)),
    ]}
    
    return [cafe, lanche1, almoco, lanche2]


def get_template_low_carb(scale_p: float, scale_c: float, scale_f: float) -> List[Dict]:
    """Template low-carb para cutting"""
    
    # Café (20% P, 15% C, 35% F)
    cafe = {"name": "Café da Manhã", "time": "07:00", "foods": [
        calc("ovos", clamp(rnd(100 * scale_p, 50), 50, 150)),
        calc("aveia", clamp(rnd(25 * scale_c, 10), 20, 50)),
    ]}
    
    # Lanche 1 (15% P, 5% C, 25% F)
    lanche1 = {"name": "Lanche Manhã", "time": "10:00", "foods": [
        calc("iogurte", clamp(rnd(150 * scale_p, 50), 100, 250)),
        calc("castanha", clamp(rnd(20 * scale_f, 5), 10, 35)),
    ]}
    
    # Almoço (35% P, 40% C, 25% F)
    almoco = {"name": "Almoço", "time": "12:30", "foods": [
        calc("frango", clamp(rnd(150 * scale_p, 25), 100, 300)),
        calc("arroz", clamp(rnd(100 * scale_c, 25), 50, 200)),
        calc("salada", 100),
        calc("brocolis", 100),
        calc("azeite", clamp(rnd(8 * scale_f, 1), 3, 12)),
    ]}
    
    # Lanche 2 (15% P, 25% C, 5% F)
    lanche2 = {"name": "Lanche Tarde", "time": "16:00", "foods": [
        calc("batata", clamp(rnd(100 * scale_c, 25), 50, 200)),
        calc("clara", clamp(rnd(100 * scale_p * 0.6, 30), 60, 180)),
    ]}
    
    return [cafe, lanche1, almoco, lanche2]


def get_template_high_carb(scale_p: float, scale_c: float, scale_f: float) -> List[Dict]:
    """Template high-carb para bulking"""
    
    # Café (12% P, 30% C, 25% F)
    cafe = {"name": "Café da Manhã", "time": "07:00", "foods": [
        calc("ovos", clamp(rnd(80 * scale_p, 50), 50, 150)),
        calc("aveia", clamp(rnd(60 * scale_c, 10), 30, 100)),
        calc("banana", clamp(rnd(120 * scale_c, 40), 80, 200)),
    ]}
    
    # Lanche 1 (10% P, 10% C, 25% F)
    lanche1 = {"name": "Lanche Manhã", "time": "10:00", "foods": [
        calc("iogurte", clamp(rnd(120 * scale_p, 50), 100, 200)),
        calc("banana", clamp(rnd(80 * scale_c, 40), 40, 160)),
        calc("castanha", clamp(rnd(20 * scale_f, 5), 10, 35)),
    ]}
    
    # Almoço (30% P, 30% C, 25% F)
    almoco = {"name": "Almoço", "time": "12:30", "foods": [
        calc("frango", clamp(rnd(140 * scale_p, 25), 100, 300)),
        calc("arroz", clamp(rnd(200 * scale_c, 25), 100, 400)),
        calc("feijao", clamp(rnd(100 * scale_c, 30), 60, 180)),
        calc("salada", 100),
        calc("azeite", clamp(rnd(10 * scale_f, 1), 5, 15)),
    ]}
    
    # Lanche 2 (20% P, 20% C, 10% F)
    lanche2 = {"name": "Lanche Tarde", "time": "16:00", "foods": [
        calc("batata", clamp(rnd(200 * scale_c, 25), 100, 400)),
        calc("frango", clamp(rnd(100 * scale_p, 25), 75, 200)),
    ]}
    
    return [cafe, lanche1, almoco, lanche2]


# ==================== AJUSTE FINAL ====================

def build_final_meal(gap_p: float, gap_c: float, gap_f: float) -> Dict:
    """
    Constrói a última refeição (Jantar) para fechar exatamente os targets.
    Usa sistema de equações para calcular porções.
    """
    
    # Alimentos disponíveis para jantar
    # Proteína principal: tilápia (26P, 0C, 2.5F por 100g)
    # Carb principal: arroz (2.6P, 23C, 0.9F por 100g)
    # Gordura: azeite (0P, 0C, 100F por 100g)
    # Extra: brócolis (2.8P, 7C, 0.4F por 100g) - fixo 100g
    
    # Brócolis fixo
    brocolis_g = 100
    brocolis = calc("brocolis", brocolis_g)
    gap_p -= brocolis["protein"]  # 2.8g
    gap_c -= brocolis["carbs"]     # 7g
    gap_f -= brocolis["fat"]       # 0.4g
    
    # Resolver sistema para tilápia, arroz, azeite
    # P = 0.26*tilapia + 0.026*arroz
    # C = 0.23*arroz
    # F = 0.025*tilapia + 0.009*arroz + 1.0*azeite
    
    # De C: arroz = gap_c / 0.23
    arroz_g = max(0, gap_c / 0.23)
    
    # De P: tilapia = (gap_p - 0.026*arroz) / 0.26
    tilapia_g = max(0, (gap_p - 0.026 * arroz_g) / 0.26)
    
    # De F: azeite = gap_f - 0.025*tilapia - 0.009*arroz
    azeite_g = gap_f - 0.025 * tilapia_g - 0.009 * arroz_g
    
    # Ajusta para limites
    tilapia_g = clamp(tilapia_g, FOODS["tilapia"]["min"], FOODS["tilapia"]["max"])
    arroz_g = clamp(arroz_g, FOODS["arroz"]["min"], FOODS["arroz"]["max"])
    azeite_g = clamp(azeite_g, 0, FOODS["azeite"]["max"])
    
    # Arredonda para step
    tilapia_g = rnd(tilapia_g, FOODS["tilapia"]["step"])
    arroz_g = rnd(arroz_g, FOODS["arroz"]["step"])
    azeite_g = round(azeite_g)  # Azeite com precisão de 1g
    
    foods = [
        calc("tilapia", tilapia_g),
        calc("arroz", arroz_g),
        calc("brocolis", brocolis_g),
    ]
    
    if azeite_g >= 3:  # Só adiciona se for quantidade razoável
        foods.append(calc("azeite", azeite_g))
    
    return {"name": "Jantar", "time": "19:30", "foods": foods}


def fine_tune_meals(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float, max_iter: int = 100) -> List[Dict]:
    """
    Ajusta finely cada refeição para fechar tolerâncias.
    """
    
    for iteration in range(max_iter):
        curr_p, curr_c, curr_f, curr_cal = sum_meals(meals)
        
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Verifica tolerâncias
        if abs(gap_p) <= TOL_P and abs(gap_c) <= TOL_C and abs(gap_f) <= TOL_F and abs(curr_cal - target_cal) <= TOL_CAL:
            return meals
        
        # Encontra o maior gap
        adjusted = False
        
        # Ajusta proteína
        if abs(gap_p) > TOL_P:
            for m_idx in [2, 3, 4]:  # Almoço, Lanche, Jantar
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] in ["frango", "tilapia", "clara"]:
                        info = FOODS[food["key"]]
                        delta_g = (gap_p / info["p"]) * 100
                        new_g = clamp(food["grams"] + delta_g, info["min"], info["max"])
                        new_g = rnd(new_g, info["step"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc(food["key"], new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # Ajusta carboidrato
        if not adjusted and abs(gap_c) > TOL_C:
            for m_idx, key in [(3, "batata"), (2, "arroz"), (4, "arroz"), (0, "aveia")]:
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == key:
                        info = FOODS[key]
                        delta_g = (gap_c / info["c"]) * 100
                        new_g = clamp(food["grams"] + delta_g, info["min"], info["max"])
                        new_g = rnd(new_g, info["step"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc(key, new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        # Ajusta gordura
        if not adjusted and abs(gap_f) > TOL_F:
            for m_idx in [2, 4, 1, 0]:  # Almoço, Jantar, Lanche, Café
                if m_idx >= len(meals):
                    continue
                for f_idx, food in enumerate(meals[m_idx]["foods"]):
                    if food["key"] == "azeite":
                        new_g = clamp(food["grams"] + gap_f, 3, 15)
                        new_g = round(new_g)
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("azeite", new_g)
                            adjusted = True
                            break
                    elif food["key"] == "castanha":
                        info = FOODS["castanha"]
                        delta_g = (gap_f / info["f"]) * 100
                        new_g = clamp(food["grams"] + delta_g, info["min"], info["max"])
                        new_g = rnd(new_g, info["step"])
                        if new_g != food["grams"]:
                            meals[m_idx]["foods"][f_idx] = calc("castanha", new_g)
                            adjusted = True
                            break
                if adjusted:
                    break
        
        if not adjusted:
            break
    
    return meals


# ==================== MAIN BUILDER ====================

def build_diet(target_p: float, target_c: float, target_f: float, target_cal: float) -> List[Dict]:
    """
    Constrói dieta completa.
    Estratégia: 4 refeições base + jantar calculado para fechar exatamente.
    """
    
    # Determina tipo de dieta baseado na proporção de macros
    carb_ratio = target_c / (target_p + target_c + target_f)
    
    scale_p = target_p / 150.0
    scale_c = target_c / 200.0
    scale_f = target_f / 60.0
    
    # Escolhe template baseado no tipo
    templates = []
    
    if carb_ratio < 0.35:  # Low carb (cutting)
        templates = [
            get_template_low_carb(scale_p * 0.75, scale_c * 0.75, scale_f * 0.75),
            get_template_low_carb(scale_p * 0.7, scale_c * 0.7, scale_f * 0.7),
            get_template_standard(scale_p * 0.7, scale_c * 0.7, scale_f * 0.7),
        ]
    elif carb_ratio > 0.50:  # High carb (bulking)
        templates = [
            get_template_high_carb(scale_p * 0.8, scale_c * 0.8, scale_f * 0.8),
            get_template_high_carb(scale_p * 0.75, scale_c * 0.75, scale_f * 0.75),
            get_template_standard(scale_p * 0.75, scale_c * 0.75, scale_f * 0.75),
        ]
    else:  # Standard (manutenção)
        templates = [
            get_template_standard(scale_p * 0.75, scale_c * 0.75, scale_f * 0.75),
            get_template_standard(scale_p * 0.7, scale_c * 0.7, scale_f * 0.7),
            get_template_low_carb(scale_p * 0.7, scale_c * 0.7, scale_f * 0.7),
        ]
    
    best_meals = None
    best_error = float('inf')
    
    for base_meals in templates:
        # Soma nutrientes das 4 refeições base
        curr_p, curr_c, curr_f, _ = sum_meals(base_meals)
        
        # Calcula gap para jantar
        gap_p = target_p - curr_p
        gap_c = target_c - curr_c
        gap_f = target_f - curr_f
        
        # Verifica se gap é viável (positivo e não excessivo)
        if gap_p < 10 or gap_c < 10 or gap_p > 100 or gap_c > 200:
            continue
        
        # Constrói jantar
        jantar = build_final_meal(gap_p, gap_c, gap_f)
        
        # Junta tudo
        meals = base_meals + [jantar]
        
        # Fine-tune
        meals = fine_tune_meals(meals, target_p, target_c, target_f, target_cal)
        
        # Calcula erro
        final_p, final_c, final_f, final_cal = sum_meals(meals)
        error = (
            abs(final_p - target_p) / TOL_P +
            abs(final_c - target_c) / TOL_C +
            abs(final_f - target_f) / TOL_F +
            abs(final_cal - target_cal) / TOL_CAL
        )
        
        if error < best_error:
            best_error = error
            best_meals = meals
        
        # Se erro zero, retorna imediatamente
        if error < 4:  # Todos dentro da tolerância
            return meals
    
    return best_meals if best_meals else templates[0] + [build_final_meal(target_p * 0.25, target_c * 0.25, target_f * 0.25)]


def validate(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> Tuple[bool, str]:
    """Valida se a dieta atende as tolerâncias"""
    curr_p, curr_c, curr_f, curr_cal = sum_meals(meals)
    
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
        
        # Tenta construir dieta
        meals = build_diet(target_p, target_c, target_f, target_cal)
        
        # Valida
        is_valid, error = validate(meals, target_p, target_c, target_f, target_cal)
        
        if not is_valid:
            # Se falhou, tenta uma segunda passagem com ajustes menores
            meals = fine_tune_meals(meals, target_p, target_c, target_f, target_cal, max_iter=200)
            is_valid, error = validate(meals, target_p, target_c, target_f, target_cal)
        
        if not is_valid:
            raise ValueError(f"Impossível fechar macros dentro da tolerância: {error}")
        
        # Formata refeições
        final_meals = []
        for m in meals:
            mp, mc, mf, mcal = sum_foods(m["foods"])
            meal = Meal(
                name=m["name"], 
                time=m["time"], 
                foods=m["foods"],
                total_calories=round(mcal, 2),
                macros={"protein": round(mp, 2), "carbs": round(mc, 2), "fat": round(mf, 2)}
            )
            final_meals.append(meal)
        
        total_p, total_c, total_f, total_cal = sum_meals(meals)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=round(total_cal, 2),
            computed_macros={"protein": round(total_p, 2), "carbs": round(total_c, 2), "fat": round(total_f, 2)},
            notes=f"Dieta: {int(total_cal)}kcal | P:{int(total_p)}g C:{int(total_c)}g G:{int(total_f)}g"
        )
