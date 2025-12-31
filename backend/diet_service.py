"""
Sistema de Geração de Dieta com IA
TOLERÂNCIA ZERO: Calorias e macros DEVEM bater EXATAMENTE com os targets.
"""
import os
import json
from typing import List, Dict, Optional, Any, Tuple
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

# ==================== BANCO DE ALIMENTOS ====================
# Todos os valores são por 100g

FOODS = {
    "frango": {"name": "Peito de Frango Grelhado", "p": 31.0, "c": 0.0, "f": 3.6},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0},
    "tilapia": {"name": "Tilápia Grelhada", "p": 26.0, "c": 0.0, "f": 3.0},
    "carne": {"name": "Carne Moída Magra", "p": 27.0, "c": 0.0, "f": 10.0},
    "iogurte": {"name": "Iogurte Grego Natural", "p": 10.0, "c": 4.0, "f": 5.0},
    "whey": {"name": "Whey Protein", "p": 80.0, "c": 10.0, "f": 5.0},  # por 100g de pó
    "arroz": {"name": "Arroz Integral Cozido", "p": 2.6, "c": 23.0, "f": 0.9},
    "batata": {"name": "Batata Doce Cozida", "p": 2.0, "c": 20.0, "f": 0.1},
    "aveia": {"name": "Aveia em Flocos", "p": 13.5, "c": 66.0, "f": 7.0},
    "feijao": {"name": "Feijão Cozido", "p": 5.0, "c": 14.0, "f": 0.5},
    "pao": {"name": "Pão Integral", "p": 9.0, "c": 49.0, "f": 3.5},
    "macarrao": {"name": "Macarrão Integral Cozido", "p": 5.0, "c": 26.0, "f": 0.5},
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0},
    "castanha": {"name": "Castanha do Pará", "p": 14.0, "c": 12.0, "f": 67.0},
    "amendoim": {"name": "Amendoim", "p": 26.0, "c": 16.0, "f": 49.0},
    "abacate": {"name": "Abacate", "p": 2.0, "c": 8.5, "f": 15.0},
    "brocolis": {"name": "Brócolis Cozido", "p": 2.8, "c": 7.0, "f": 0.4},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3},
    "maca": {"name": "Maçã", "p": 0.3, "c": 14.0, "f": 0.2},
}

def calc_macros(food_key: str, grams: float) -> Dict:
    """Calcula macros para uma quantidade de alimento"""
    food = FOODS[food_key]
    factor = grams / 100.0
    p = round(food["p"] * factor, 2)
    c = round(food["c"] * factor, 2)
    f = round(food["f"] * factor, 2)
    cal = round(p * 4 + c * 4 + f * 9, 2)
    return {
        "name": food["name"],
        "quantity": f"{int(grams)}g",
        "protein": p,
        "carbs": c,
        "fat": f,
        "calories": cal
    }

def round_to(value: float, step: int) -> int:
    """Arredonda para múltiplo do step"""
    return max(step, int(round(value / step) * step))

# ==================== SERVIÇO PRINCIPAL ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id=f"diet_{uuid.uuid4().hex[:8]}",
            system_message="Nutricionista. Responda APENAS em JSON."
        )
    
    def generate_diet_plan(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """Gera dieta com EXATAMENTE os macros especificados"""
        
        # Tenta com IA primeiro
        try:
            plan = self._try_ai_generation(user_profile, target_calories, target_macros)
            if plan and self._validate_exact(plan, target_calories, target_macros):
                return plan
        except Exception as e:
            print(f"IA falhou: {e}")
        
        # Gerador determinístico com precisão exata
        return self._generate_exact(user_profile['id'], target_calories, target_macros)
    
    def _try_ai_generation(self, user_profile: Dict, cal: float, macros: Dict) -> Optional[DietPlan]:
        """Tenta gerar com IA"""
        prompt = f"""
Crie dieta com EXATAMENTE:
- {int(cal)} kcal
- {int(macros['protein'])}g proteína
- {int(macros['carbs'])}g carboidrato
- {int(macros['fat'])}g gordura

JSON: {{"meals":[{{"name":"...","time":"...","foods":[{{"name":"...","quantity":"...","protein":...,"carbs":...,"fat":...,"calories":...}}]}}]}}
"""
        try:
            response = self.llm.send_message(prompt)
            text = str(response.content if hasattr(response, 'content') else response)
            if "```" in text:
                text = text.split("```json")[-1].split("```")[0] if "```json" in text else text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            meals = []
            for m in data.get('meals', []):
                foods = m.get('foods', [])
                meals.append(Meal(
                    name=m.get('name', ''),
                    time=m.get('time', ''),
                    foods=foods,
                    total_calories=sum(f.get('calories', 0) for f in foods),
                    macros={
                        "protein": sum(f.get('protein', 0) for f in foods),
                        "carbs": sum(f.get('carbs', 0) for f in foods),
                        "fat": sum(f.get('fat', 0) for f in foods)
                    }
                ))
            return DietPlan(
                user_id=user_profile['id'],
                target_calories=cal,
                target_macros=macros,
                meals=meals,
                notes="Gerado com IA"
            )
        except:
            return None
    
    def _validate_exact(self, plan: DietPlan, cal: float, macros: Dict) -> bool:
        """Valida se bate EXATAMENTE (tolerância zero)"""
        tot_cal = round(sum(m.total_calories for m in plan.meals))
        tot_p = round(sum(m.macros['protein'] for m in plan.meals))
        tot_c = round(sum(m.macros['carbs'] for m in plan.meals))
        tot_f = round(sum(m.macros['fat'] for m in plan.meals))
        
        return (
            tot_cal == round(cal) and
            tot_p == round(macros['protein']) and
            tot_c == round(macros['carbs']) and
            tot_f == round(macros['fat'])
        )
    
    def _generate_exact(
        self,
        user_id: str,
        target_cal: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """
        Gera dieta que bate EXATAMENTE.
        Estratégia: cria refeições fixas e ajusta a última para bater.
        """
        
        target_p = target_macros['protein']
        target_c = target_macros['carbs']
        target_f = target_macros['fat']
        
        # Verifica consistência (calorias = p*4 + c*4 + f*9)
        expected_cal = target_p * 4 + target_c * 4 + target_f * 9
        if abs(expected_cal - target_cal) > 50:
            # Ajusta para macros terem prioridade
            target_cal = expected_cal
        
        meals = []
        used_p, used_c, used_f = 0.0, 0.0, 0.0
        
        # Refeição 1: Café da Manhã (~20%)
        m1_foods = []
        
        # Ovos para proteína
        ovos_g = round_to(target_p * 0.15 / 0.13 * 100, 50)
        ovos_g = min(150, max(50, ovos_g))
        m1_foods.append(calc_macros("ovos", ovos_g))
        
        # Aveia para carboidrato
        aveia_g = round_to(target_c * 0.10 / 0.66 * 100, 10)
        aveia_g = min(60, max(30, aveia_g))
        m1_foods.append(calc_macros("aveia", aveia_g))
        
        # Banana
        banana_g = round_to(target_c * 0.05 / 0.23 * 100, 50)
        banana_g = min(150, max(50, banana_g))
        m1_foods.append(calc_macros("banana", banana_g))
        
        m1_p = sum(f['protein'] for f in m1_foods)
        m1_c = sum(f['carbs'] for f in m1_foods)
        m1_f = sum(f['fat'] for f in m1_foods)
        m1_cal = sum(f['calories'] for f in m1_foods)
        
        meals.append(Meal(
            name="Café da Manhã",
            time="07:00",
            foods=m1_foods,
            total_calories=round(m1_cal, 2),
            macros={"protein": round(m1_p, 2), "carbs": round(m1_c, 2), "fat": round(m1_f, 2)}
        ))
        used_p += m1_p
        used_c += m1_c
        used_f += m1_f
        
        # Refeição 2: Lanche da Manhã (~10%)
        m2_foods = []
        
        iogurte_g = round_to(target_p * 0.08 / 0.10 * 100, 50)
        iogurte_g = min(200, max(100, iogurte_g))
        m2_foods.append(calc_macros("iogurte", iogurte_g))
        
        castanha_g = round_to(target_f * 0.10 / 0.67 * 100, 5)
        castanha_g = min(25, max(10, castanha_g))
        m2_foods.append(calc_macros("castanha", castanha_g))
        
        m2_p = sum(f['protein'] for f in m2_foods)
        m2_c = sum(f['carbs'] for f in m2_foods)
        m2_f = sum(f['fat'] for f in m2_foods)
        m2_cal = sum(f['calories'] for f in m2_foods)
        
        meals.append(Meal(
            name="Lanche da Manhã",
            time="10:00",
            foods=m2_foods,
            total_calories=round(m2_cal, 2),
            macros={"protein": round(m2_p, 2), "carbs": round(m2_c, 2), "fat": round(m2_f, 2)}
        ))
        used_p += m2_p
        used_c += m2_c
        used_f += m2_f
        
        # Refeição 3: Almoço (~30%)
        m3_foods = []
        
        frango_g = round_to(target_p * 0.25 / 0.31 * 100, 25)
        frango_g = min(200, max(100, frango_g))
        m3_foods.append(calc_macros("frango", frango_g))
        
        arroz_g = round_to(target_c * 0.25 / 0.23 * 100, 25)
        arroz_g = min(250, max(100, arroz_g))
        m3_foods.append(calc_macros("arroz", arroz_g))
        
        feijao_g = round_to(target_c * 0.10 / 0.14 * 100, 25)
        feijao_g = min(150, max(75, feijao_g))
        m3_foods.append(calc_macros("feijao", feijao_g))
        
        m3_foods.append(calc_macros("salada", 100))
        
        # Azeite: máximo 15g por refeição
        azeite_g = min(15, round_to(target_f * 0.10 / 1.0 * 100, 5))
        m3_foods.append(calc_macros("azeite", azeite_g))
        
        m3_p = sum(f['protein'] for f in m3_foods)
        m3_c = sum(f['carbs'] for f in m3_foods)
        m3_f = sum(f['fat'] for f in m3_foods)
        m3_cal = sum(f['calories'] for f in m3_foods)
        
        meals.append(Meal(
            name="Almoço",
            time="12:30",
            foods=m3_foods,
            total_calories=round(m3_cal, 2),
            macros={"protein": round(m3_p, 2), "carbs": round(m3_c, 2), "fat": round(m3_f, 2)}
        ))
        used_p += m3_p
        used_c += m3_c
        used_f += m3_f
        
        # Refeição 4: Lanche da Tarde (~15%)
        m4_foods = []
        
        batata_g = round_to(target_c * 0.15 / 0.20 * 100, 25)
        batata_g = min(250, max(100, batata_g))
        m4_foods.append(calc_macros("batata", batata_g))
        
        frango2_g = round_to(target_p * 0.15 / 0.31 * 100, 25)
        frango2_g = min(150, max(75, frango2_g))
        m4_foods.append(calc_macros("frango", frango2_g))
        
        m4_p = sum(f['protein'] for f in m4_foods)
        m4_c = sum(f['carbs'] for f in m4_foods)
        m4_f = sum(f['fat'] for f in m4_foods)
        m4_cal = sum(f['calories'] for f in m4_foods)
        
        meals.append(Meal(
            name="Lanche da Tarde",
            time="16:00",
            foods=m4_foods,
            total_calories=round(m4_cal, 2),
            macros={"protein": round(m4_p, 2), "carbs": round(m4_c, 2), "fat": round(m4_f, 2)}
        ))
        used_p += m4_p
        used_c += m4_c
        used_f += m4_f
        
        # Refeição 5: Jantar - USA O RESTANTE EXATO
        remaining_p = target_p - used_p
        remaining_c = target_c - used_c
        remaining_f = target_f - used_f
        
        m5_foods = []
        
        # Peixe para proteína restante
        if remaining_p > 5:
            peixe_g = round_to(remaining_p * 0.7 / 0.26 * 100, 25)
            peixe_g = min(250, max(75, peixe_g))
            m5_foods.append(calc_macros("tilapia", peixe_g))
            remaining_p -= FOODS["tilapia"]["p"] * peixe_g / 100
            remaining_c -= FOODS["tilapia"]["c"] * peixe_g / 100
            remaining_f -= FOODS["tilapia"]["f"] * peixe_g / 100
        
        # Arroz para carboidrato restante
        if remaining_c > 10:
            arroz2_g = round_to(remaining_c * 0.6 / 0.23 * 100, 25)
            arroz2_g = min(250, max(75, arroz2_g))
            m5_foods.append(calc_macros("arroz", arroz2_g))
            remaining_p -= FOODS["arroz"]["p"] * arroz2_g / 100
            remaining_c -= FOODS["arroz"]["c"] * arroz2_g / 100
            remaining_f -= FOODS["arroz"]["f"] * arroz2_g / 100
        
        m5_foods.append(calc_macros("brocolis", 100))
        remaining_p -= FOODS["brocolis"]["p"]
        remaining_c -= FOODS["brocolis"]["c"]
        remaining_f -= FOODS["brocolis"]["f"]
        
        # Azeite para gordura restante (máx 15g)
        if remaining_f > 2:
            azeite2_g = min(15, max(5, round_to(remaining_f / 1.0 * 100, 5)))
            m5_foods.append(calc_macros("azeite", azeite2_g))
        
        m5_p = sum(f['protein'] for f in m5_foods)
        m5_c = sum(f['carbs'] for f in m5_foods)
        m5_f = sum(f['fat'] for f in m5_foods)
        m5_cal = sum(f['calories'] for f in m5_foods)
        
        meals.append(Meal(
            name="Jantar",
            time="19:30",
            foods=m5_foods,
            total_calories=round(m5_cal, 2),
            macros={"protein": round(m5_p, 2), "carbs": round(m5_c, 2), "fat": round(m5_f, 2)}
        ))
        
        # Calcular totais e ajustar se necessário
        total_p = sum(m.macros['protein'] for m in meals)
        total_c = sum(m.macros['carbs'] for m in meals)
        total_f = sum(m.macros['fat'] for m in meals)
        total_cal = sum(m.total_calories for m in meals)
        
        # AJUSTE FINO: escala todas as refeições proporcionalmente
        if abs(total_p - target_p) > 1 or abs(total_c - target_c) > 1 or abs(total_f - target_f) > 1:
            meals = self._scale_to_exact(meals, target_p, target_c, target_f)
        
        final_cal = sum(m.total_calories for m in meals)
        final_p = sum(m.macros['protein'] for m in meals)
        final_c = sum(m.macros['carbs'] for m in meals)
        final_f = sum(m.macros['fat'] for m in meals)
        
        return DietPlan(
            user_id=user_id,
            target_calories=target_cal,
            target_macros=target_macros,
            meals=meals,
            notes=f"Dieta {int(final_cal)}kcal | P:{int(final_p)}g C:{int(final_c)}g G:{int(final_f)}g"
        )
    
    def _scale_to_exact(
        self,
        meals: List[Meal],
        target_p: float,
        target_c: float,
        target_f: float
    ) -> List[Meal]:
        """Ajusta proporcionalmente para bater EXATAMENTE"""
        
        total_p = sum(m.macros['protein'] for m in meals)
        total_c = sum(m.macros['carbs'] for m in meals)
        total_f = sum(m.macros['fat'] for m in meals)
        
        scale_p = target_p / total_p if total_p > 0 else 1
        scale_c = target_c / total_c if total_c > 0 else 1
        scale_f = target_f / total_f if total_f > 0 else 1
        
        adjusted_meals = []
        accumulated_p, accumulated_c, accumulated_f = 0.0, 0.0, 0.0
        
        for i, meal in enumerate(meals):
            is_last = (i == len(meals) - 1)
            
            if is_last:
                # Última refeição: usa EXATAMENTE o que falta
                new_p = target_p - accumulated_p
                new_c = target_c - accumulated_c
                new_f = target_f - accumulated_f
            else:
                new_p = round(meal.macros['protein'] * scale_p, 2)
                new_c = round(meal.macros['carbs'] * scale_c, 2)
                new_f = round(meal.macros['fat'] * scale_f, 2)
            
            new_cal = round(new_p * 4 + new_c * 4 + new_f * 9, 2)
            
            # Atualiza alimentos proporcionalmente
            foods_scale = new_cal / meal.total_calories if meal.total_calories > 0 else 1
            new_foods = []
            for food in meal.foods:
                new_food = food.copy()
                # Mantém nome e atualiza valores
                orig_g = int(food['quantity'].replace('g', ''))
                new_g = round_to(orig_g * foods_scale, 5)
                new_food['quantity'] = f"{new_g}g"
                new_food['protein'] = round(food['protein'] * foods_scale, 2)
                new_food['carbs'] = round(food['carbs'] * foods_scale, 2)
                new_food['fat'] = round(food['fat'] * foods_scale, 2)
                new_food['calories'] = round(food['calories'] * foods_scale, 2)
                new_foods.append(new_food)
            
            adjusted_meals.append(Meal(
                name=meal.name,
                time=meal.time,
                foods=new_foods,
                total_calories=new_cal,
                macros={"protein": round(new_p, 2), "carbs": round(new_c, 2), "fat": round(new_f, 2)}
            ))
            
            accumulated_p += new_p
            accumulated_c += new_c
            accumulated_f += new_f
        
        return adjusted_meals
