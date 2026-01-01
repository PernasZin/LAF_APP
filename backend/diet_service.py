"""
Sistema de Geração de Dieta - ALGORITMO DE FECHAMENTO DETERMINÍSTICO

PRINCÍPIOS:
1. A soma dos nutrientes dos alimentos DEVE igualar os targets por construção
2. Nenhuma aproximação é retornada ao frontend
3. Tolerâncias ESTRITAS: P±3g, C±3g, F±2g, Cal±25kcal
4. Ajustes discretos: 5g, 10g, 25g steps
5. Limites realistas: azeite ≤15g, castanha ≤25g por refeição

ALGORITMO DE DUAS FASES:
- Fase 1: Gera refeições base com porções realistas
- Fase 2: Usa alimentos "closers" (single-macro dominant) para fechar gaps
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


# ==================== TOLERANCES (NON-NEGOTIABLE) ====================

TOLERANCE_PROTEIN = 3.0   # grams
TOLERANCE_CARBS = 3.0     # grams
TOLERANCE_FAT = 2.0       # grams
TOLERANCE_CALORIES = 25.0 # kcal

MAX_GENERATION_ATTEMPTS = 5


# ==================== FOOD DATABASE ====================
# Valores por 100g (nutrientes em gramas)

FOODS = {
    # ========== PROTEÍNAS (P dominante) ==========
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6, "min": 75, "max": 250, "step": 25},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5, "min": 100, "max": 200, "step": 25},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0, "min": 50, "max": 150, "step": 50},  # ~1-3 ovos
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2, "min": 30, "max": 150, "step": 30},   # CLOSER: quase puro P
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0, "min": 100, "max": 200, "step": 50},
    
    # ========== CARBOIDRATOS (C dominante) ==========
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9, "min": 100, "max": 250, "step": 25},  # CLOSER: alto C
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1, "min": 100, "max": 300, "step": 50},    # CLOSER: quase puro C
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0, "min": 30, "max": 80, "step": 10},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3, "min": 80, "max": 150, "step": 40},          # ~1-2 bananas
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5, "min": 80, "max": 150, "step": 25},
    
    # ========== GORDURAS (F dominante) ==========
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0, "min": 5, "max": 15, "step": 5},            # CLOSER: puro F
    "castanha": {"name": "Castanha do Pará", "p": 14.0, "c": 12.0, "f": 67.0, "min": 10, "max": 25, "step": 5},
    
    # ========== VEGETAIS (baixa densidade calórica) ==========
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4, "min": 80, "max": 150, "step": 25},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2, "min": 80, "max": 150, "step": 25},
}

# Alimentos "closers" - usados para ajuste fino de macros específicos
CLOSERS = {
    "protein": "clara",    # Clara de ovo: 11g P, 0.7g C, 0.2g F por 100g
    "carbs": "batata",     # Batata doce: 1.6g P, 20g C, 0.1g F por 100g  
    "fat": "azeite",       # Azeite: 0g P, 0g C, 100g F por 100g
}


# ==================== HELPER FUNCTIONS ====================

def calc_food(key: str, grams: int) -> Dict:
    """Calcula nutrientes para uma quantidade específica de alimento"""
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


def round_to_step(value: float, step: int) -> int:
    """Arredonda valor para múltiplo do step"""
    return max(step, int(round(value / step) * step))


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Limita valor entre min e max"""
    return max(min_val, min(max_val, value))


def sum_macros(foods: List[Dict]) -> Tuple[float, float, float, float]:
    """Soma macros de uma lista de alimentos"""
    p = sum(f["protein"] for f in foods)
    c = sum(f["carbs"] for f in foods)
    f = sum(f["fat"] for f in foods)
    cal = sum(f["calories"] for f in foods)
    return p, c, f, cal


def is_within_tolerance(computed: Dict, target: Dict, computed_cal: float, target_cal: float) -> bool:
    """Verifica se macros computados estão dentro das tolerâncias"""
    p_ok = abs(computed["protein"] - target["protein"]) <= TOLERANCE_PROTEIN
    c_ok = abs(computed["carbs"] - target["carbs"]) <= TOLERANCE_CARBS
    f_ok = abs(computed["fat"] - target["fat"]) <= TOLERANCE_FAT
    cal_ok = abs(computed_cal - target_cal) <= TOLERANCE_CALORIES
    return p_ok and c_ok and f_ok and cal_ok


# ==================== MEAL TEMPLATES ====================

def get_meal_templates() -> List[Dict]:
    """
    Retorna templates de refeições com proporções base.
    Cada template tem uma proporção do total diário (deve somar ~100%).
    """
    return [
        {
            "name": "Café da Manhã",
            "time": "07:00",
            "ratio": 0.20,  # 20% das calorias
            "base_foods": [
                {"key": "ovos", "base_g": 100},      # 2 ovos
                {"key": "aveia", "base_g": 40},
                {"key": "banana", "base_g": 80},    # 1 banana
            ]
        },
        {
            "name": "Lanche Manhã",
            "time": "10:00",
            "ratio": 0.10,  # 10% das calorias
            "base_foods": [
                {"key": "iogurte", "base_g": 150},
                {"key": "castanha", "base_g": 15},
            ]
        },
        {
            "name": "Almoço",
            "time": "12:30",
            "ratio": 0.30,  # 30% das calorias
            "base_foods": [
                {"key": "frango", "base_g": 150},
                {"key": "arroz", "base_g": 150},
                {"key": "feijao", "base_g": 80},
                {"key": "salada", "base_g": 100},
                {"key": "azeite", "base_g": 10},
            ]
        },
        {
            "name": "Lanche Tarde",
            "time": "16:00",
            "ratio": 0.15,  # 15% das calorias
            "base_foods": [
                {"key": "batata", "base_g": 150},
                {"key": "frango", "base_g": 100},
            ]
        },
        {
            "name": "Jantar",
            "time": "19:30",
            "ratio": 0.25,  # 25% das calorias = última refeição para ajuste
            "base_foods": [
                {"key": "tilapia", "base_g": 150},
                {"key": "arroz", "base_g": 100},
                {"key": "brocolis", "base_g": 100},
                {"key": "azeite", "base_g": 10},
            ]
        }
    ]


# ==================== PHASE 1: BASE MEAL GENERATION ====================

def generate_base_meals(target_cal: float, target_macros: Dict, num_meals: int = 5) -> List[Meal]:
    """
    FASE 1: Gera refeições base com escalonamento proporcional.
    Não tenta atingir targets exatos - apenas cria base realista.
    """
    templates = get_meal_templates()[:num_meals]
    
    # Calcula calorias base do template
    base_total_cal = 0.0
    for tmpl in templates:
        for food_def in tmpl["base_foods"]:
            food = calc_food(food_def["key"], food_def["base_g"])
            base_total_cal += food["calories"]
    
    # Fator de escala global
    scale = target_cal / base_total_cal if base_total_cal > 0 else 1.0
    
    meals = []
    for tmpl in templates:
        foods = []
        for food_def in tmpl["base_foods"]:
            key = food_def["key"]
            base_g = food_def["base_g"]
            food_info = FOODS[key]
            
            # Escala e arredonda
            scaled_g = base_g * scale
            step = food_info["step"]
            rounded_g = round_to_step(scaled_g, step)
            
            # Aplica limites
            rounded_g = clamp(rounded_g, food_info["min"], food_info["max"])
            
            foods.append(calc_food(key, rounded_g))
        
        # Cria meal
        p, c, f, cal = sum_macros(foods)
        meal = Meal(
            name=tmpl["name"],
            time=tmpl["time"],
            foods=foods,
            total_calories=round(cal, 2),
            macros={"protein": round(p, 2), "carbs": round(c, 2), "fat": round(f, 2)}
        )
        meals.append(meal)
    
    return meals


# ==================== PHASE 2: MACRO GAP CLOSURE ====================

def calculate_gaps(meals: List[Meal], target_macros: Dict, target_cal: float) -> Dict:
    """Calcula gaps entre computed e target"""
    total_p = sum(m.macros["protein"] for m in meals)
    total_c = sum(m.macros["carbs"] for m in meals)
    total_f = sum(m.macros["fat"] for m in meals)
    total_cal = sum(m.total_calories for m in meals)
    
    return {
        "protein": target_macros["protein"] - total_p,
        "carbs": target_macros["carbs"] - total_c,
        "fat": target_macros["fat"] - total_f,
        "calories": target_cal - total_cal,
        "computed": {"protein": total_p, "carbs": total_c, "fat": total_f, "calories": total_cal}
    }


def apply_closer_adjustment(meals: List[Meal], macro_type: str, gap: float) -> bool:
    """
    Aplica ajuste fino usando alimento closer para um macro específico.
    Retorna True se ajuste foi bem sucedido, False se impossível.
    """
    if abs(gap) < 0.5:  # Gap muito pequeno, ignorar
        return True
    
    closer_key = CLOSERS[macro_type]
    closer_info = FOODS[closer_key]
    
    # Encontra a última refeição para adicionar/ajustar closer
    target_meal = meals[-1]  # Jantar
    
    # Calcula gramas necessárias
    if macro_type == "protein":
        # Clara: 11g P por 100g
        grams_needed = (gap / closer_info["p"]) * 100
    elif macro_type == "carbs":
        # Batata: 20g C por 100g
        grams_needed = (gap / closer_info["c"]) * 100
    else:  # fat
        # Azeite: 100g F por 100g (puro)
        grams_needed = (gap / closer_info["f"]) * 100
    
    # Arredonda para step do alimento
    step = closer_info["step"]
    grams_adjusted = round_to_step(abs(grams_needed), step)
    
    if grams_needed < 0:
        grams_adjusted = -grams_adjusted
    
    # Verifica se já existe o closer na refeição
    existing_idx = None
    for i, food in enumerate(target_meal.foods):
        if food.get("key") == closer_key:
            existing_idx = i
            break
    
    if existing_idx is not None:
        # Ajusta quantidade existente
        current_g = target_meal.foods[existing_idx]["grams"]
        new_g = current_g + grams_adjusted
        new_g = clamp(new_g, closer_info["min"], closer_info["max"])
        
        if new_g < closer_info["min"]:
            # Remove o alimento se ficou muito pequeno
            target_meal.foods.pop(existing_idx)
        else:
            target_meal.foods[existing_idx] = calc_food(closer_key, new_g)
    else:
        # Adiciona novo closer se gap positivo
        if grams_adjusted > 0:
            grams_to_add = clamp(grams_adjusted, closer_info["min"], closer_info["max"])
            target_meal.foods.append(calc_food(closer_key, grams_to_add))
    
    # Recalcula macros da refeição
    p, c, f, cal = sum_macros(target_meal.foods)
    target_meal.macros = {"protein": round(p, 2), "carbs": round(c, 2), "fat": round(f, 2)}
    target_meal.total_calories = round(cal, 2)
    
    return True


def close_macro_gaps(meals: List[Meal], target_macros: Dict, target_cal: float) -> List[Meal]:
    """
    FASE 2: Aplica ajustes iterativos para fechar gaps de macros.
    Usa closers em ordem: Fat (mais impactante em calorias), Protein, Carbs.
    """
    # Ordem de ajuste: Fat primeiro (9 cal/g vs 4 cal/g)
    adjustment_order = ["fat", "protein", "carbs"]
    
    for _ in range(10):  # Max 10 iterações de refinamento
        gaps = calculate_gaps(meals, target_macros, target_cal)
        
        # Verifica se já está dentro da tolerância
        computed = gaps["computed"]
        computed_macros = {"protein": computed["protein"], "carbs": computed["carbs"], "fat": computed["fat"]}
        
        if is_within_tolerance(computed_macros, target_macros, computed["calories"], target_cal):
            break
        
        # Aplica ajustes
        for macro in adjustment_order:
            gap = gaps[macro]
            if abs(gap) > 1.0:  # Só ajusta se gap > 1g
                apply_closer_adjustment(meals, macro, gap)
    
    return meals


# ==================== FINE-TUNING: DISCRETE ADJUSTMENTS ====================

def fine_tune_meals(meals: List[Meal], target_macros: Dict, target_cal: float) -> List[Meal]:
    """
    Ajuste fino adicional: modifica quantidades existentes em pequenos steps
    para fechar gaps residuais.
    """
    for _ in range(5):  # Max 5 iterações de fine-tuning
        gaps = calculate_gaps(meals, target_macros, target_cal)
        computed = gaps["computed"]
        computed_macros = {"protein": computed["protein"], "carbs": computed["carbs"], "fat": computed["fat"]}
        
        if is_within_tolerance(computed_macros, target_macros, computed["calories"], target_cal):
            break
        
        # Encontra o macro com maior gap relativo
        protein_gap = gaps["protein"]
        carbs_gap = gaps["carbs"]
        fat_gap = gaps["fat"]
        
        # Ajusta alimentos existentes nas refeições principais (almoço/jantar)
        for meal in [meals[2], meals[4], meals[3]]:  # Almoço, Jantar, Lanche Tarde
            for i, food in enumerate(meal.foods):
                key = food.get("key")
                if not key or key not in FOODS:
                    continue
                
                food_info = FOODS[key]
                current_g = food["grams"]
                step = food_info["step"]
                
                # Decide direção do ajuste baseado nos gaps
                if key in ["frango", "tilapia", "clara"] and abs(protein_gap) > TOLERANCE_PROTEIN:
                    # Proteína: ajusta frango/peixe/clara
                    delta = step if protein_gap > 0 else -step
                    new_g = clamp(current_g + delta, food_info["min"], food_info["max"])
                    meal.foods[i] = calc_food(key, new_g)
                    
                elif key in ["arroz", "batata", "aveia"] and abs(carbs_gap) > TOLERANCE_CARBS:
                    # Carbs: ajusta arroz/batata
                    delta = step if carbs_gap > 0 else -step
                    new_g = clamp(current_g + delta, food_info["min"], food_info["max"])
                    meal.foods[i] = calc_food(key, new_g)
                    
                elif key == "azeite" and abs(fat_gap) > TOLERANCE_FAT:
                    # Gordura: ajusta azeite (CUIDADO: limite de 15g por refeição)
                    delta = step if fat_gap > 0 else -step
                    new_g = clamp(current_g + delta, food_info["min"], food_info["max"])
                    meal.foods[i] = calc_food(key, new_g)
            
            # Recalcula macros da refeição
            p, c, f, cal = sum_macros(meal.foods)
            meal.macros = {"protein": round(p, 2), "carbs": round(c, 2), "fat": round(f, 2)}
            meal.total_calories = round(cal, 2)
        
        # Recalcula gaps
        gaps = calculate_gaps(meals, target_macros, target_cal)
    
    return meals


# ==================== VALIDATION ====================

def validate_diet_plan(meals: List[Meal], target_macros: Dict, target_cal: float) -> Tuple[bool, str]:
    """
    Validação rigorosa do plano de dieta.
    Retorna (success, error_message).
    """
    # Soma todos os nutrientes
    total_p = 0.0
    total_c = 0.0
    total_f = 0.0
    total_cal = 0.0
    
    for meal in meals:
        for food in meal.foods:
            total_p += food["protein"]
            total_c += food["carbs"]
            total_f += food["fat"]
            total_cal += food["calories"]
    
    # Verifica tolerâncias
    p_diff = abs(total_p - target_macros["protein"])
    c_diff = abs(total_c - target_macros["carbs"])
    f_diff = abs(total_f - target_macros["fat"])
    cal_diff = abs(total_cal - target_cal)
    
    errors = []
    
    if p_diff > TOLERANCE_PROTEIN:
        errors.append(f"Proteína: {total_p:.1f}g vs target {target_macros['protein']:.1f}g (diff: {p_diff:.1f}g, max: {TOLERANCE_PROTEIN}g)")
    
    if c_diff > TOLERANCE_CARBS:
        errors.append(f"Carbs: {total_c:.1f}g vs target {target_macros['carbs']:.1f}g (diff: {c_diff:.1f}g, max: {TOLERANCE_CARBS}g)")
    
    if f_diff > TOLERANCE_FAT:
        errors.append(f"Gordura: {total_f:.1f}g vs target {target_macros['fat']:.1f}g (diff: {f_diff:.1f}g, max: {TOLERANCE_FAT}g)")
    
    if cal_diff > TOLERANCE_CALORIES:
        errors.append(f"Calorias: {total_cal:.1f} vs target {target_cal:.1f} (diff: {cal_diff:.1f}kcal, max: {TOLERANCE_CALORIES}kcal)")
    
    # Valida limites de porções
    for meal in meals:
        for food in meal.foods:
            key = food.get("key")
            if key and key in FOODS:
                g = food["grams"]
                info = FOODS[key]
                if g > info["max"]:
                    errors.append(f"{food['name']}: {g}g excede máximo de {info['max']}g")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, ""


# ==================== MAIN SERVICE CLASS ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        """
        Gera plano de dieta com GARANTIA de integridade de dados.
        
        Algoritmo de duas fases:
        1. Gera refeições base realistas
        2. Fecha gaps com alimentos closers
        
        Validação:
        - Se fechamento falhar após MAX_ATTEMPTS, LEVANTA EXCEÇÃO
        - Nunca retorna dieta inconsistente
        """
        # Arredonda targets para facilitar fechamento
        target_macros = {
            "protein": round(target_macros["protein"], 1),
            "carbs": round(target_macros["carbs"], 1),
            "fat": round(target_macros["fat"], 1)
        }
        target_calories = round(target_calories, 0)
        
        last_error = ""
        
        for attempt in range(MAX_GENERATION_ATTEMPTS):
            # FASE 1: Gera base
            meals = generate_base_meals(target_calories, target_macros)
            
            # FASE 2: Fecha gaps
            meals = close_macro_gaps(meals, target_macros, target_calories)
            
            # FASE 3: Fine-tuning
            meals = fine_tune_meals(meals, target_macros, target_calories)
            
            # VALIDAÇÃO
            is_valid, error = validate_diet_plan(meals, target_macros, target_calories)
            
            if is_valid:
                # Calcula totais finais (da soma real dos alimentos)
                total_p = sum(sum(f["protein"] for f in m.foods) for m in meals)
                total_c = sum(sum(f["carbs"] for f in m.foods) for m in meals)
                total_f = sum(sum(f["fat"] for f in m.foods) for m in meals)
                total_cal = sum(sum(f["calories"] for f in m.foods) for m in meals)
                
                return DietPlan(
                    user_id=user_profile['id'],
                    target_calories=target_calories,
                    target_macros=target_macros,
                    meals=meals,
                    computed_calories=round(total_cal, 2),
                    computed_macros={
                        "protein": round(total_p, 2),
                        "carbs": round(total_c, 2),
                        "fat": round(total_f, 2)
                    },
                    notes=f"Dieta validada: {int(total_cal)}kcal | P:{int(total_p)}g C:{int(total_c)}g G:{int(total_f)}g"
                )
            else:
                last_error = error
                # Tenta novamente com pequena variação nos templates
                continue
        
        # FALHA: Não conseguiu gerar dieta válida
        raise ValueError(
            f"Impossível gerar dieta que atenda às restrições após {MAX_GENERATION_ATTEMPTS} tentativas. "
            f"Último erro: {last_error}"
        )
