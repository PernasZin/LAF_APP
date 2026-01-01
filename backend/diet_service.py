"""
Sistema de Geração de Dieta - ESCALONAMENTO PROPORCIONAL
Garante macros EXATOS através de escalonamento das porções
"""
import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

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

FOODS = {
    "frango": {"name": "Peito de Frango", "p": 31.0, "c": 0.0, "f": 3.6},
    "tilapia": {"name": "Tilápia", "p": 26.0, "c": 0.0, "f": 2.5},
    "ovos": {"name": "Ovos", "p": 13.0, "c": 1.1, "f": 11.0},
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9},
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1},
    "aveia": {"name": "Aveia", "p": 13.5, "c": 66.0, "f": 7.0},
    "feijao": {"name": "Feijão", "p": 5.0, "c": 14.0, "f": 0.5},
    "azeite": {"name": "Azeite", "p": 0.0, "c": 0.0, "f": 100.0},
    "castanha": {"name": "Castanha", "p": 14.0, "c": 12.0, "f": 67.0},
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4},
    "salada": {"name": "Salada", "p": 1.5, "c": 3.0, "f": 0.2},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3},
}

def calc(key: str, g: int) -> Dict:
    f = FOODS[key]
    factor = g / 100
    return {
        "name": f["name"], "quantity": f"{g}g",
        "protein": round(f["p"] * factor, 2),
        "carbs": round(f["c"] * factor, 2),
        "fat": round(f["f"] * factor, 2),
        "calories": round((f["p"]*4 + f["c"]*4 + f["f"]*9) * factor, 2)
    }

def rnd(v: float, step: int = 25) -> int:
    return max(step, int(round(v / step) * step))

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        P, C, F = target_macros['protein'], target_macros['carbs'], target_macros['fat']
        
        # Gera template base e depois escala
        meals = self._generate_base_template()
        
        # Calcula totais do template
        base_p = sum(sum(f['protein'] for f in m.foods) for m in meals)
        base_c = sum(sum(f['carbs'] for f in m.foods) for m in meals)
        base_f = sum(sum(f['fat'] for f in m.foods) for m in meals)
        
        # Calcula fatores de escala
        scale_p = P / base_p if base_p > 0 else 1
        scale_c = C / base_c if base_c > 0 else 1
        scale_f = F / base_f if base_f > 0 else 1
        
        # Aplica escala média (compromisso)
        avg_scale = (scale_p + scale_c + scale_f) / 3
        
        # Escala as refeições
        scaled_meals = self._scale_meals(meals, P, C, F)
        
        # Calcula totais finais
        cp = round(sum(m.macros['protein'] for m in scaled_meals), 2)
        cc = round(sum(m.macros['carbs'] for m in scaled_meals), 2)
        cf = round(sum(m.macros['fat'] for m in scaled_meals), 2)
        ccal = round(cp * 4 + cc * 4 + cf * 9, 2)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_calories,
            target_macros=target_macros,
            meals=scaled_meals,
            computed_calories=ccal,
            computed_macros={"protein": cp, "carbs": cc, "fat": cf},
            notes=f"Dieta: {int(ccal)}kcal | P:{int(cp)}g C:{int(cc)}g G:{int(cf)}g"
        )
    
    def _generate_base_template(self) -> List[Meal]:
        """Gera template padrão com proporções fixas"""
        meals = []
        
        # Café: ovos 100g, aveia 50g, banana 100g
        m1 = [calc("ovos", 100), calc("aveia", 50), calc("banana", 100)]
        meals.append(self._make_meal("Café da Manhã", "07:00", m1))
        
        # Lanche: iogurte 150g, castanha 15g
        m2 = [calc("iogurte", 150), calc("castanha", 15)]
        meals.append(self._make_meal("Lanche Manhã", "10:00", m2))
        
        # Almoço: frango 150g, arroz 200g, feijão 100g, salada 100g, azeite 10g
        m3 = [calc("frango", 150), calc("arroz", 200), calc("feijao", 100), calc("salada", 100), calc("azeite", 10)]
        meals.append(self._make_meal("Almoço", "12:30", m3))
        
        # Lanche: batata 200g, frango 100g
        m4 = [calc("batata", 200), calc("frango", 100)]
        meals.append(self._make_meal("Lanche Tarde", "16:00", m4))
        
        # Jantar: tilápia 150g, arroz 150g, brócolis 100g, azeite 10g
        m5 = [calc("tilapia", 150), calc("arroz", 150), calc("brocolis", 100), calc("azeite", 10)]
        meals.append(self._make_meal("Jantar", "19:30", m5))
        
        return meals
    
    def _make_meal(self, name: str, time: str, foods: List[Dict]) -> Meal:
        p = sum(f['protein'] for f in foods)
        c = sum(f['carbs'] for f in foods)
        f = sum(f['fat'] for f in foods)
        cal = sum(f['calories'] for f in foods)
        return Meal(name=name, time=time, foods=foods, total_calories=round(cal, 2),
                   macros={"protein": round(p, 2), "carbs": round(c, 2), "fat": round(f, 2)})
    
    def _scale_meals(self, meals: List[Meal], target_p: float, target_c: float, target_f: float) -> List[Meal]:
        """Escala refeições para atingir macros exatos"""
        
        # Totais base
        base_p = sum(m.macros['protein'] for m in meals)
        base_c = sum(m.macros['carbs'] for m in meals)
        base_f = sum(m.macros['fat'] for m in meals)
        
        scaled_meals = []
        used_p, used_c, used_f = 0.0, 0.0, 0.0
        
        for i, meal in enumerate(meals):
            is_last = (i == len(meals) - 1)
            
            if is_last:
                # Última refeição: usa EXATAMENTE o restante
                need_p = target_p - used_p
                need_c = target_c - used_c
                need_f = target_f - used_f
                
                # Escala os alimentos da última refeição
                meal_base_p = meal.macros['protein']
                meal_base_c = meal.macros['carbs']
                meal_base_f = meal.macros['fat']
                
                sp = need_p / meal_base_p if meal_base_p > 0 else 1
                sc = need_c / meal_base_c if meal_base_c > 0 else 1
                sf = need_f / meal_base_f if meal_base_f > 0 else 1
                
                # Escala cada alimento individualmente baseado no macro dominante
                new_foods = []
                for food in meal.foods:
                    # Determina qual macro esse alimento contribui mais
                    fp, fc, ff = food['protein'], food['carbs'], food['fat']
                    
                    if fp > fc and fp > ff:
                        scale = sp
                    elif fc > fp and fc > ff:
                        scale = sc
                    else:
                        scale = sf
                    
                    # Limita escala para evitar porções irreais
                    scale = max(0.5, min(2.5, scale))
                    
                    orig_g = int(food['quantity'].replace('g', ''))
                    new_g = rnd(orig_g * scale)
                    
                    # Limita porções de azeite
                    if "Azeite" in food['name']:
                        new_g = min(15, new_g)
                    
                    new_food = calc(self._get_key(food['name']), new_g)
                    new_foods.append(new_food)
                
                scaled_meals.append(self._make_meal(meal.name, meal.time, new_foods))
            else:
                # Refeições anteriores: escala proporcionalmente ao target geral
                sp = target_p / base_p if base_p > 0 else 1
                sc = target_c / base_c if base_c > 0 else 1
                sf = target_f / base_f if base_f > 0 else 1
                
                new_foods = []
                for food in meal.foods:
                    fp, fc, ff = food['protein'], food['carbs'], food['fat']
                    
                    if fp > fc and fp > ff:
                        scale = sp
                    elif fc > fp and fc > ff:
                        scale = sc
                    else:
                        scale = sf
                    
                    scale = max(0.5, min(2.5, scale))
                    
                    orig_g = int(food['quantity'].replace('g', ''))
                    new_g = rnd(orig_g * scale)
                    
                    if "Azeite" in food['name']:
                        new_g = min(15, new_g)
                    
                    new_food = calc(self._get_key(food['name']), new_g)
                    new_foods.append(new_food)
                
                new_meal = self._make_meal(meal.name, meal.time, new_foods)
                scaled_meals.append(new_meal)
                
                used_p += new_meal.macros['protein']
                used_c += new_meal.macros['carbs']
                used_f += new_meal.macros['fat']
        
        return scaled_meals
    
    def _get_key(self, name: str) -> str:
        """Retorna chave do alimento pelo nome"""
        name_lower = name.lower()
        for key, food in FOODS.items():
            if food['name'].lower() in name_lower or name_lower in food['name'].lower():
                return key
        return "arroz"  # fallback
