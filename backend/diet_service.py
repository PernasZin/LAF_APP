"""
Sistema de Geração de Dieta - ALGORITMO DE FECHAMENTO DETERMINÍSTICO V2

PRINCÍPIOS:
1. A soma dos nutrientes dos alimentos DEVE igualar os targets por construção
2. Nenhuma aproximação é retornada ao frontend
3. Tolerâncias ESTRITAS: P±3g, C±3g, F±2g, Cal±25kcal
4. Ajustes discretos: 5g, 10g, 25g steps
5. Limites realistas: azeite ≤15g, castanha ≤25g por refeição

ALGORITMO:
1. Começa com template base
2. Escala proporcionalmente para aproximar targets
3. Ajusta iterativamente alimentos específicos para fechar gaps
4. Usa alimentos "pure" (baixa contaminação de outros macros) para ajuste fino
"""

import os
from typing import List, Dict, Optional, Tuple
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

TOLERANCE_PROTEIN = 3.0
TOLERANCE_CARBS = 3.0
TOLERANCE_FAT = 2.0
TOLERANCE_CALORIES = 25.0
MAX_ITERATIONS = 50


# ==================== FOOD DATABASE ====================

FOODS = {
    # PROTEÍNAS PURAS (alta P, baixo C/F)
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 200, "step": 30},
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 75, "max": 250, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 75, "max": 200, "step": 25},
    
    # PROTEÍNAS MISTAS
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 150, "step": 50},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 100, "max": 200, "step": 50},
    
    # CARBOIDRATOS PUROS (alto C, baixo P/F)
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "min": 50, "max": 400, "step": 25},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "min": 50, "max": 300, "step": 25},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "min": 80, "max": 200, "step": 40},
    
    # CARBOIDRATOS MISTOS
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "min": 30, "max": 80, "step": 10},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5, "min": 60, "max": 150, "step": 30},
    
    # GORDURAS PURAS (puro F)
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0, "min": 5, "max": 15, "step": 5},
    
    # GORDURAS MISTAS
    "castanha": {"name": "Castanha", "p": 14.0, "c": 12.0, "f": 67.0, "min": 10, "max": 25, "step": 5},
    
    # VEGETAIS
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "min": 80, "max": 150, "step": 25},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "min": 80, "max": 150, "step": 25},
}


# ==================== HELPER FUNCTIONS ====================

def calc_food(key: str, grams: int) -> Dict:
    """Calcula nutrientes para quantidade específica"""
    f = FOODS[key]
    factor = grams / 100.0
    protein = f["p"] * factor
    carbs = f["c"] * factor
    fat = f["f"] * factor
    calories = (protein * 4) + (carbs * 4) + (fat * 9)
    
    return {
        "key": key,
        "name": f["name"],
        "quantity": f"{grams}g",
        "grams": grams,
        "protein": round(protein, 2),
        "carbs": round(carbs, 2),
        "fat": round(fat, 2),
        "calories": round(calories, 2)
    }


def round_step(value: float, step: int) -> int:
    """Arredonda para múltiplo de step"""
    return max(step, int(round(value / step) * step))


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Limita entre min e max"""
    return max(min_val, min(max_val, value))


def sum_all_foods(meals: List[Dict]) -> Tuple[float, float, float, float]:
    """Soma total de macros de todas as refeições"""
    total_p = total_c = total_f = total_cal = 0.0
    for meal in meals:
        for food in meal["foods"]:
            total_p += food["protein"]
            total_c += food["carbs"]
            total_f += food["fat"]
            total_cal += food["calories"]
    return total_p, total_c, total_f, total_cal


def is_valid(computed_p, computed_c, computed_f, computed_cal, target_p, target_c, target_f, target_cal) -> bool:
    """Verifica se está dentro das tolerâncias"""
    return (
        abs(computed_p - target_p) <= TOLERANCE_PROTEIN and
        abs(computed_c - target_c) <= TOLERANCE_CARBS and
        abs(computed_f - target_f) <= TOLERANCE_FAT and
        abs(computed_cal - target_cal) <= TOLERANCE_CALORIES
    )


# ==================== MEAL GENERATION ====================

def create_base_meal_plan(target_cal: float) -> List[Dict]:
    """
    Cria plano base de 5 refeições com proporções fixas.
    """
    # Escala base para ~2500 kcal
    scale = target_cal / 2500.0
    
    meals = [
        {
            "name": "Café da Manhã",
            "time": "07:00",
            "foods": [
                calc_food("ovos", clamp(round_step(100 * scale, 50), 50, 150)),
                calc_food("aveia", clamp(round_step(40 * scale, 10), 30, 80)),
                calc_food("banana", clamp(round_step(100 * scale, 40), 80, 200)),
            ]
        },
        {
            "name": "Lanche Manhã",
            "time": "10:00",
            "foods": [
                calc_food("iogurte", clamp(round_step(150 * scale, 50), 100, 200)),
                calc_food("castanha", clamp(round_step(15 * scale, 5), 10, 25)),
            ]
        },
        {
            "name": "Almoço",
            "time": "12:30",
            "foods": [
                calc_food("frango", clamp(round_step(150 * scale, 25), 75, 250)),
                calc_food("arroz", clamp(round_step(150 * scale, 25), 100, 300)),
                calc_food("feijao", clamp(round_step(80 * scale, 30), 60, 150)),
                calc_food("salada", 100),
                calc_food("azeite", clamp(round_step(10 * scale, 5), 5, 15)),
            ]
        },
        {
            "name": "Lanche Tarde",
            "time": "16:00",
            "foods": [
                calc_food("batata", clamp(round_step(200 * scale, 25), 100, 400)),
                calc_food("frango", clamp(round_step(100 * scale, 25), 75, 200)),
            ]
        },
        {
            "name": "Jantar",
            "time": "19:30",
            "foods": [
                calc_food("tilapia", clamp(round_step(150 * scale, 25), 75, 200)),
                calc_food("arroz", clamp(round_step(120 * scale, 25), 50, 250)),
                calc_food("brocolis", 100),
                calc_food("azeite", clamp(round_step(10 * scale, 5), 5, 15)),
            ]
        }
    ]
    
    return meals


def adjust_food_quantity(meal: Dict, food_idx: int, delta_grams: int) -> bool:
    """
    Ajusta quantidade de um alimento específico.
    Retorna True se ajuste foi aplicado.
    """
    food = meal["foods"][food_idx]
    key = food["key"]
    info = FOODS[key]
    
    current_g = food["grams"]
    new_g = current_g + delta_grams
    
    # Arredonda para step
    new_g = round_step(new_g, info["step"])
    
    # Aplica limites
    new_g = clamp(new_g, info["min"], info["max"])
    
    if new_g != current_g:
        meal["foods"][food_idx] = calc_food(key, new_g)
        return True
    return False


def find_food_in_meals(meals: List[Dict], food_key: str) -> List[Tuple[int, int]]:
    """Encontra todos os índices (meal_idx, food_idx) de um alimento"""
    result = []
    for m_idx, meal in enumerate(meals):
        for f_idx, food in enumerate(meal["foods"]):
            if food["key"] == food_key:
                result.append((m_idx, f_idx))
    return result


def add_food_to_meal(meals: List[Dict], meal_idx: int, food_key: str, grams: int):
    """Adiciona alimento a uma refeição"""
    info = FOODS[food_key]
    grams = clamp(round_step(grams, info["step"]), info["min"], info["max"])
    meals[meal_idx]["foods"].append(calc_food(food_key, grams))


# ==================== ITERATIVE ADJUSTMENT ====================

def adjust_for_macro(meals: List[Dict], macro: str, gap: float, target_cal: float):
    """
    Ajusta alimentos para fechar gap de um macro específico.
    
    Estratégia:
    - Se gap > 0: precisa ADICIONAR macro
    - Se gap < 0: precisa REMOVER macro
    
    Usa alimentos "puros" para minimizar impacto em outros macros.
    """
    if abs(gap) < 1.0:
        return
    
    # Alimentos puros para cada macro
    if macro == "protein":
        # Clara: 11g P por 100g, quase zero C/F
        pure_foods = ["clara", "frango", "tilapia"]
        nutrient_per_100g = {"clara": 11.0, "frango": 31.0, "tilapia": 26.0}
    elif macro == "carbs":
        # Batata: 20g C por 100g, quase zero P/F
        pure_foods = ["batata", "arroz", "banana"]
        nutrient_per_100g = {"batata": 20.0, "arroz": 23.0, "banana": 23.0}
    else:  # fat
        # Azeite: 100g F por 100g, zero P/C
        pure_foods = ["azeite"]
        nutrient_per_100g = {"azeite": 100.0}
    
    direction = 1 if gap > 0 else -1
    
    for food_key in pure_foods:
        if abs(gap) < 1.0:
            break
            
        locations = find_food_in_meals(meals, food_key)
        info = FOODS[food_key]
        step = info["step"]
        
        # Calcula quanto o step representa em macro
        macro_per_step = (nutrient_per_100g[food_key] / 100.0) * step
        
        # Quantos steps precisa?
        steps_needed = int(abs(gap) / macro_per_step) if macro_per_step > 0 else 0
        steps_needed = max(1, min(steps_needed, 5))  # Limita a 5 steps por vez
        
        if locations:
            # Ajusta primeiro local encontrado
            m_idx, f_idx = locations[0]
            delta = step * steps_needed * direction
            adjusted = adjust_food_quantity(meals[m_idx], f_idx, delta)
            
            if adjusted:
                # Recalcula gap
                total_p, total_c, total_f, _ = sum_all_foods(meals)
                if macro == "protein":
                    gap = gap - (delta / 100.0) * nutrient_per_100g[food_key]
                elif macro == "carbs":
                    gap = gap - (delta / 100.0) * nutrient_per_100g[food_key]
                else:
                    gap = gap - (delta / 100.0) * nutrient_per_100g[food_key]
        else:
            # Adiciona alimento se gap > 0 (precisamos adicionar)
            if direction > 0:
                grams_needed = (abs(gap) / nutrient_per_100g[food_key]) * 100
                grams_needed = clamp(round_step(grams_needed, step), info["min"], info["max"])
                
                # Adiciona na última refeição (jantar) ou almoço
                target_meal = 4 if food_key not in ["clara"] else 0  # Clara no café
                add_food_to_meal(meals, target_meal, food_key, grams_needed)


def iterative_adjustment(meals: List[Dict], target_p: float, target_c: float, target_f: float, target_cal: float) -> bool:
    """
    Ajusta iterativamente até atingir tolerâncias ou max iterações.
    Retorna True se conseguiu convergir.
    """
    for iteration in range(MAX_ITERATIONS):
        total_p, total_c, total_f, total_cal = sum_all_foods(meals)
        
        if is_valid(total_p, total_c, total_f, total_cal, target_p, target_c, target_f, target_cal):
            return True
        
        # Calcula gaps
        gap_p = target_p - total_p
        gap_c = target_c - total_c
        gap_f = target_f - total_f
        gap_cal = target_cal - total_cal
        
        # Prioriza ajuste pelo maior gap relativo
        # Mas FAT impacta mais em calorias (9 cal/g vs 4 cal/g)
        
        # Ordena por impacto
        gaps = [
            ("fat", gap_f, abs(gap_f) / TOLERANCE_FAT if TOLERANCE_FAT > 0 else 0),
            ("protein", gap_p, abs(gap_p) / TOLERANCE_PROTEIN if TOLERANCE_PROTEIN > 0 else 0),
            ("carbs", gap_c, abs(gap_c) / TOLERANCE_CARBS if TOLERANCE_CARBS > 0 else 0),
        ]
        gaps.sort(key=lambda x: x[2], reverse=True)
        
        # Ajusta o macro com maior gap relativo
        for macro, gap, _ in gaps:
            if macro == "fat" and abs(gap) > TOLERANCE_FAT:
                adjust_for_macro(meals, "fat", gap, target_cal)
                break
            elif macro == "protein" and abs(gap) > TOLERANCE_PROTEIN:
                adjust_for_macro(meals, "protein", gap, target_cal)
                break
            elif macro == "carbs" and abs(gap) > TOLERANCE_CARBS:
                adjust_for_macro(meals, "carbs", gap, target_cal)
                break
    
    return False


# ==================== FINAL VALIDATION ====================

def validate_and_finalize(meals: List[Dict]) -> Tuple[List[Meal], Dict]:
    """
    Valida e converte para estrutura final.
    """
    total_p = total_c = total_f = total_cal = 0.0
    final_meals = []
    
    for meal_data in meals:
        # Recalcula macros da refeição
        meal_p = sum(f["protein"] for f in meal_data["foods"])
        meal_c = sum(f["carbs"] for f in meal_data["foods"])
        meal_f = sum(f["fat"] for f in meal_data["foods"])
        meal_cal = sum(f["calories"] for f in meal_data["foods"])
        
        total_p += meal_p
        total_c += meal_c
        total_f += meal_f
        total_cal += meal_cal
        
        # Remove key dos foods (não precisa no output)
        clean_foods = []
        for food in meal_data["foods"]:
            clean_food = {k: v for k, v in food.items() if k != "key" and k != "grams"}
            clean_foods.append(clean_food)
        
        meal = Meal(
            name=meal_data["name"],
            time=meal_data["time"],
            foods=meal_data["foods"],  # Mantém com key para debug
            total_calories=round(meal_cal, 2),
            macros={
                "protein": round(meal_p, 2),
                "carbs": round(meal_c, 2),
                "fat": round(meal_f, 2)
            }
        )
        final_meals.append(meal)
    
    computed = {
        "protein": round(total_p, 2),
        "carbs": round(total_c, 2),
        "fat": round(total_f, 2),
        "calories": round(total_cal, 2)
    }
    
    return final_meals, computed


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
        
        # Cria plano base
        meals = create_base_meal_plan(target_cal)
        
        # Ajusta iterativamente
        success = iterative_adjustment(meals, target_p, target_c, target_f, target_cal)
        
        if not success:
            # Verifica se está perto o suficiente
            total_p, total_c, total_f, total_cal = sum_all_foods(meals)
            
            if not is_valid(total_p, total_c, total_f, total_cal, target_p, target_c, target_f, target_cal):
                raise ValueError(
                    f"Impossível fechar macros. "
                    f"Target: P{target_p}g C{target_c}g F{target_f}g {target_cal}kcal | "
                    f"Computed: P{total_p:.1f}g C{total_c:.1f}g F{total_f:.1f}g {total_cal:.1f}kcal | "
                    f"Diffs: P{abs(total_p - target_p):.1f}g C{abs(total_c - target_c):.1f}g F{abs(total_f - target_f):.1f}g {abs(total_cal - target_cal):.1f}kcal"
                )
        
        # Finaliza
        final_meals, computed = validate_and_finalize(meals)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_cal,
            target_macros={"protein": target_p, "carbs": target_c, "fat": target_f},
            meals=final_meals,
            computed_calories=computed["calories"],
            computed_macros={
                "protein": computed["protein"],
                "carbs": computed["carbs"],
                "fat": computed["fat"]
            },
            notes=f"Dieta: {int(computed['calories'])}kcal | P:{int(computed['protein'])}g C:{int(computed['carbs'])}g G:{int(computed['fat'])}g"
        )
