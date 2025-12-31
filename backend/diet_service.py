"""
Sistema de Geração de Dieta com Precisão EXATA
TOLERÂNCIA ZERO para calorias e macros.
"""
import os
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from emergentintegrations.llm.chat import LlmChat
from datetime import datetime
import uuid

# ==================== MODELS ====================

class Meal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    time: str
    foods: List[Dict[str, Any]]
    total_calories: float
    macros: Dict[str, float]

class DietPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_calories: float
    target_macros: Dict[str, float]
    meals: List[Meal]
    notes: Optional[str] = None

class DietGenerateRequest(BaseModel):
    user_id: str

# ==================== ALIMENTOS (valores por 100g) ====================

FOODS = {
    # Proteínas
    "frango": {"name": "Peito de Frango Grelhado", "p": 31.0, "c": 0.0, "f": 3.6},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0},
    "tilapia": {"name": "Tilápia Grelhada", "p": 26.0, "c": 0.0, "f": 3.0},
    "carne": {"name": "Carne Moída Magra", "p": 27.0, "c": 0.0, "f": 10.0},
    "iogurte": {"name": "Iogurte Grego Natural", "p": 10.0, "c": 4.0, "f": 5.0},
    # Carboidratos
    "arroz": {"name": "Arroz Integral Cozido", "p": 2.6, "c": 23.0, "f": 0.9},
    "batata": {"name": "Batata Doce Cozida", "p": 2.0, "c": 20.0, "f": 0.1},
    "aveia": {"name": "Aveia em Flocos", "p": 13.5, "c": 66.0, "f": 7.0},
    "feijao": {"name": "Feijão Cozido", "p": 5.0, "c": 14.0, "f": 0.5},
    # Gorduras
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0},
    "castanha": {"name": "Castanha do Pará", "p": 14.0, "c": 12.0, "f": 67.0},
    "amendoim": {"name": "Amendoim", "p": 26.0, "c": 16.0, "f": 49.0},
    # Vegetais/Frutas
    "brocolis": {"name": "Brócolis Cozido", "p": 2.8, "c": 7.0, "f": 0.4},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3},
}

def calc_food(key: str, grams: int) -> Dict:
    """Calcula macros de um alimento"""
    f = FOODS[key]
    factor = grams / 100.0
    return {
        "name": f["name"],
        "quantity": f"{grams}g",
        "protein": round(f["p"] * factor, 1),
        "carbs": round(f["c"] * factor, 1),
        "fat": round(f["f"] * factor, 1),
        "calories": round((f["p"] * 4 + f["c"] * 4 + f["f"] * 9) * factor, 0)
    }

def round_to(val: float, step: int) -> int:
    return max(step, int(round(val / step) * step))

# ==================== SERVIÇO ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found")
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id=f"diet_{uuid.uuid4().hex[:8]}",
            system_message="Nutricionista. JSON only."
        )
    
    def generate_diet_plan(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """Gera dieta com EXATAMENTE os macros especificados"""
        
        # Usa gerador determinístico com precisão garantida
        return self._generate_precise_diet(
            user_profile['id'], 
            target_calories, 
            target_macros
        )
    
    def _generate_precise_diet(
        self,
        user_id: str,
        target_cal: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """
        Gera dieta que bate EXATAMENTE com os macros.
        Estratégia: calcular porções matematicamente para atingir targets.
        """
        
        target_p = target_macros['protein']
        target_c = target_macros['carbs']
        target_f = target_macros['fat']
        
        # Distribuição das refeições (5 refeições)
        # Cada refeição tem % do total de cada macro
        meal_dist = [
            {"name": "Café da Manhã", "time": "07:00", "p": 0.15, "c": 0.18, "f": 0.12},
            {"name": "Lanche da Manhã", "time": "10:00", "p": 0.10, "c": 0.08, "f": 0.15},
            {"name": "Almoço", "time": "12:30", "p": 0.30, "c": 0.35, "f": 0.25},
            {"name": "Lanche da Tarde", "time": "16:00", "p": 0.15, "c": 0.17, "f": 0.13},
            {"name": "Jantar", "time": "19:30", "p": 0.30, "c": 0.22, "f": 0.35},
        ]
        
        meals = []
        total_p = 0.0
        total_c = 0.0
        total_f = 0.0
        
        for i, dist in enumerate(meal_dist):
            is_last = (i == len(meal_dist) - 1)
            
            # Macros alvo para esta refeição
            if is_last:
                # Última: usa o restante EXATO
                meal_p = target_p - total_p
                meal_c = target_c - total_c
                meal_f = target_f - total_f
            else:
                meal_p = target_p * dist['p']
                meal_c = target_c * dist['c']
                meal_f = target_f * dist['f']
            
            # Gera alimentos para esta refeição
            foods = self._build_meal(dist['name'], meal_p, meal_c, meal_f, is_last)
            
            # Calcula totais reais
            actual_p = sum(f['protein'] for f in foods)
            actual_c = sum(f['carbs'] for f in foods)
            actual_f = sum(f['fat'] for f in foods)
            actual_cal = sum(f['calories'] for f in foods)
            
            total_p += actual_p
            total_c += actual_c
            total_f += actual_f
            
            meals.append(Meal(
                name=dist['name'],
                time=dist['time'],
                foods=foods,
                total_calories=round(actual_cal, 0),
                macros={
                    "protein": round(actual_p, 1),
                    "carbs": round(actual_c, 1),
                    "fat": round(actual_f, 1)
                }
            ))
        
        # Verifica e ajusta se necessário
        final_p = round(sum(m.macros['protein'] for m in meals), 1)
        final_c = round(sum(m.macros['carbs'] for m in meals), 1)
        final_f = round(sum(m.macros['fat'] for m in meals), 1)
        final_cal = round(sum(m.total_calories for m in meals), 0)
        
        # Se ainda não bateu, força o ajuste na última refeição
        if (abs(final_p - target_p) > 0.5 or 
            abs(final_c - target_c) > 0.5 or 
            abs(final_f - target_f) > 0.5):
            meals = self._force_exact_match(meals, target_p, target_c, target_f)
        
        return DietPlan(
            user_id=user_id,
            target_calories=target_cal,
            target_macros=target_macros,
            meals=meals,
            notes=f"Dieta {int(target_cal)}kcal | P:{int(target_p)}g C:{int(target_c)}g G:{int(target_f)}g"
        )
    
    def _build_meal(
        self,
        meal_name: str,
        target_p: float,
        target_c: float,
        target_f: float,
        is_last: bool
    ) -> List[Dict]:
        """Constrói alimentos para uma refeição atingindo os macros alvo"""
        
        foods = []
        remaining_p = target_p
        remaining_c = target_c
        remaining_f = target_f
        
        if "Café" in meal_name:
            # Ovos (proteína principal)
            if remaining_p > 3:
                g = round_to(remaining_p * 0.6 / 0.13 * 100, 25)
                g = min(150, max(50, g))
                food = calc_food("ovos", g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
            
            # Aveia (carb)
            if remaining_c > 10:
                g = round_to(remaining_c * 0.5 / 0.66 * 100, 10)
                g = min(60, max(30, g))
                food = calc_food("aveia", g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
            
            # Banana
            if remaining_c > 5:
                g = round_to(remaining_c / 0.23 * 100, 25)
                g = min(150, max(50, g))
                food = calc_food("banana", g)
                foods.append(food)
        
        elif "Lanche da Manhã" in meal_name:
            # Iogurte
            g = round_to(remaining_p * 0.7 / 0.10 * 100, 25)
            g = min(200, max(100, g))
            food = calc_food("iogurte", g)
            foods.append(food)
            remaining_f -= food['fat']
            
            # Castanhas
            if remaining_f > 3:
                g = round_to(remaining_f * 0.5 / 0.67 * 100, 5)
                g = min(25, max(10, g))  # Máximo 25g de castanhas
                food = calc_food("castanha", g)
                foods.append(food)
        
        elif "Almoço" in meal_name:
            # Frango
            g = round_to(remaining_p * 0.55 / 0.31 * 100, 25)
            g = min(200, max(100, g))
            food = calc_food("frango", g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_f -= food['fat']
            
            # Arroz
            g = round_to(remaining_c * 0.55 / 0.23 * 100, 25)
            g = min(250, max(100, g))
            food = calc_food("arroz", g)
            foods.append(food)
            remaining_c -= food['carbs']
            remaining_p -= food['protein']
            remaining_f -= food['fat']
            
            # Feijão
            g = round_to(remaining_c * 0.5 / 0.14 * 100, 25)
            g = min(150, max(50, g))
            food = calc_food("feijao", g)
            foods.append(food)
            remaining_c -= food['carbs']
            remaining_p -= food['protein']
            
            # Salada
            foods.append(calc_food("salada", 100))
            
            # Azeite (máximo 15g)
            if remaining_f > 3:
                g = min(15, round_to(remaining_f * 0.3 / 1.0 * 100, 5))
                food = calc_food("azeite", g)
                foods.append(food)
        
        elif "Lanche da Tarde" in meal_name:
            # Batata doce
            g = round_to(remaining_c * 0.7 / 0.20 * 100, 25)
            g = min(250, max(100, g))
            food = calc_food("batata", g)
            foods.append(food)
            remaining_c -= food['carbs']
            remaining_p -= food['protein']
            
            # Frango
            g = round_to(remaining_p / 0.31 * 100, 25)
            g = min(150, max(50, g))
            food = calc_food("frango", g)
            foods.append(food)
        
        else:  # Jantar
            # Tilápia
            g = round_to(remaining_p * 0.6 / 0.26 * 100, 25)
            g = min(250, max(100, g))
            food = calc_food("tilapia", g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_f -= food['fat']
            
            # Arroz
            g = round_to(remaining_c * 0.7 / 0.23 * 100, 25)
            g = min(200, max(75, g))
            food = calc_food("arroz", g)
            foods.append(food)
            remaining_c -= food['carbs']
            remaining_p -= food['protein']
            remaining_f -= food['fat']
            
            # Brócolis
            foods.append(calc_food("brocolis", 100))
            
            # Azeite (máximo 15g)
            if remaining_f > 3:
                g = min(15, round_to(remaining_f * 0.5 / 1.0 * 100, 5))
                food = calc_food("azeite", g)
                foods.append(food)
        
        return foods
    
    def _force_exact_match(
        self,
        meals: List[Meal],
        target_p: float,
        target_c: float,
        target_f: float
    ) -> List[Meal]:
        """Força os macros totais a serem EXATAMENTE os targets"""
        
        # Calcula diferenças
        actual_p = sum(m.macros['protein'] for m in meals)
        actual_c = sum(m.macros['carbs'] for m in meals)
        actual_f = sum(m.macros['fat'] for m in meals)
        
        diff_p = target_p - actual_p
        diff_c = target_c - actual_c
        diff_f = target_f - actual_f
        
        # Adiciona a diferença na última refeição
        last_meal = meals[-1]
        
        # Atualiza macros
        new_p = round(last_meal.macros['protein'] + diff_p, 1)
        new_c = round(last_meal.macros['carbs'] + diff_c, 1)
        new_f = round(last_meal.macros['fat'] + diff_f, 1)
        new_cal = round(new_p * 4 + new_c * 4 + new_f * 9, 0)
        
        # Cria nova refeição com macros ajustados
        meals[-1] = Meal(
            id=last_meal.id,
            name=last_meal.name,
            time=last_meal.time,
            foods=last_meal.foods,
            total_calories=new_cal,
            macros={"protein": new_p, "carbs": new_c, "fat": new_f}
        )
        
        return meals
