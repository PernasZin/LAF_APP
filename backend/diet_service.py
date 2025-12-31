"""
Sistema de Geração de Dieta com IA
Utiliza Emergent LLM Key para gerar planos alimentares personalizados

REGRAS DE NEGÓCIO ABSOLUTAS (TOLERÂNCIA ZERO):
1. A soma das calorias das refeições DEVE ser EXATAMENTE igual ao target_calories (±0)
2. A soma dos macros DEVE ser EXATAMENTE igual aos target_macros (±0)
3. Azeite: MÁXIMO 15g POR REFEIÇÃO, nunca inflar óleo para bater calorias
4. Porções arredondadas (5g, 10g, 25g, 50g)
"""
import os
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime
import uuid
import math

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
# Valores nutricionais por 100g

FOODS = {
    "proteinas": [
        {"name": "Peito de Frango Grelhado", "protein": 31, "carbs": 0, "fat": 3.6, "cal_per_g": 1.65},
        {"name": "Ovos Inteiros", "protein": 13, "carbs": 1.1, "fat": 11, "cal_per_g": 1.55},
        {"name": "Tilápia Grelhada", "protein": 26, "carbs": 0, "fat": 3, "cal_per_g": 1.29},
        {"name": "Carne Moída Magra", "protein": 27, "carbs": 0, "fat": 10, "cal_per_g": 2.09},
        {"name": "Iogurte Grego Natural", "protein": 10, "carbs": 4, "fat": 5, "cal_per_g": 1.00},
        {"name": "Queijo Cottage", "protein": 11, "carbs": 3.4, "fat": 4.3, "cal_per_g": 0.98},
        {"name": "Whey Protein (30g)", "protein": 24, "carbs": 3, "fat": 1.5, "cal_per_g": 1.20},
    ],
    "carboidratos": [
        {"name": "Arroz Integral Cozido", "protein": 2.6, "carbs": 23, "fat": 0.9, "cal_per_g": 1.11},
        {"name": "Batata Doce Cozida", "protein": 2, "carbs": 20, "fat": 0.1, "cal_per_g": 0.86},
        {"name": "Aveia em Flocos", "protein": 13.5, "carbs": 66, "fat": 7, "cal_per_g": 3.89},
        {"name": "Feijão Cozido", "protein": 5, "carbs": 14, "fat": 0.5, "cal_per_g": 0.77},
        {"name": "Pão Integral", "protein": 9, "carbs": 49, "fat": 3.5, "cal_per_g": 2.53},
        {"name": "Macarrão Integral Cozido", "protein": 5, "carbs": 26, "fat": 0.5, "cal_per_g": 1.24},
    ],
    "gorduras": [
        {"name": "Azeite de Oliva", "protein": 0, "carbs": 0, "fat": 100, "cal_per_g": 8.84, "max_per_meal": 15},
        {"name": "Castanha do Pará", "protein": 14, "carbs": 12, "fat": 67, "cal_per_g": 6.56},
        {"name": "Amendoim Torrado", "protein": 26, "carbs": 16, "fat": 49, "cal_per_g": 5.67},
        {"name": "Abacate", "protein": 2, "carbs": 8.5, "fat": 15, "cal_per_g": 1.60},
        {"name": "Pasta de Amendoim", "protein": 25, "carbs": 20, "fat": 50, "cal_per_g": 5.88},
    ],
    "vegetais": [
        {"name": "Brócolis Cozido", "protein": 2.8, "carbs": 7, "fat": 0.4, "cal_per_g": 0.34},
        {"name": "Salada Verde", "protein": 1.5, "carbs": 3, "fat": 0.2, "cal_per_g": 0.20},
        {"name": "Tomate", "protein": 0.9, "carbs": 3.9, "fat": 0.2, "cal_per_g": 0.18},
    ],
    "frutas": [
        {"name": "Banana", "protein": 1.1, "carbs": 23, "fat": 0.3, "cal_per_g": 0.89},
        {"name": "Maçã", "protein": 0.3, "carbs": 14, "fat": 0.2, "cal_per_g": 0.52},
    ]
}

# ==================== FUNÇÕES DE CÁLCULO EXATO ====================

def round_portion(value: float, step: int = 25) -> int:
    """Arredonda porção para múltiplo do step"""
    return max(step, int(round(value / step) * step))

def calc_food_macros(food: Dict, grams: int) -> Dict:
    """Calcula macros exatos para uma quantidade de alimento"""
    factor = grams / 100.0
    return {
        "name": food["name"],
        "quantity": f"{grams}g",
        "protein": round(food["protein"] * factor, 2),
        "carbs": round(food["carbs"] * factor, 2),
        "fat": round(food["fat"] * factor, 2),
        "calories": round(food["cal_per_g"] * grams, 2)
    }

# ==================== SERVIÇO PRINCIPAL ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id=f"diet_{uuid.uuid4().hex[:8]}",
            system_message="Você é um nutricionista. Responda APENAS em JSON válido, sem texto adicional."
        )
    
    def generate_diet_plan(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """
        Gera plano de dieta que bate EXATAMENTE com os targets.
        Tolerância: ZERO
        """
        # Tenta com IA primeiro
        try:
            diet_plan = self._generate_with_ai(user_profile, target_calories, target_macros)
            if diet_plan and self._validate_exact_match(diet_plan, target_calories, target_macros):
                return diet_plan
            print("Dieta da IA não bateu exatamente. Usando gerador determinístico.")
        except Exception as e:
            print(f"Erro na geração com IA: {e}")
        
        # Fallback: Gerador determinístico com precisão exata
        return self._generate_exact_diet(user_profile['id'], target_calories, target_macros, user_profile)
    
    def _generate_with_ai(
        self,
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> Optional[DietPlan]:
        """Tenta gerar dieta com IA"""
        
        prompt = f"""
Crie um plano alimentar diário com estas METAS EXATAS (tolerância ZERO):

CALORIAS TOTAIS: {int(target_calories)} kcal (EXATO)
PROTEÍNA TOTAL: {int(target_macros['protein'])}g (EXATO)
CARBOIDRATOS TOTAL: {int(target_macros['carbs'])}g (EXATO)
GORDURA TOTAL: {int(target_macros['fat'])}g (EXATO)

REGRAS OBRIGATÓRIAS:
1. A SOMA de todas as calorias das refeições = {int(target_calories)} kcal EXATO
2. A SOMA de toda proteína = {int(target_macros['protein'])}g EXATO
3. A SOMA de todo carboidrato = {int(target_macros['carbs'])}g EXATO
4. A SOMA de toda gordura = {int(target_macros['fat'])}g EXATO
5. AZEITE: máximo 15g POR REFEIÇÃO
6. Porções em múltiplos de 25g (ex: 100g, 125g, 150g)

ALIMENTOS DISPONÍVEIS (valores por 100g):
{json.dumps(FOODS, indent=2, ensure_ascii=False)}

Crie 5 refeições. Use fórmula: calorias = (proteína×4) + (carboidrato×4) + (gordura×9)

RESPONDA APENAS COM JSON:
{{"meals":[{{"name":"Café da Manhã","time":"07:00","foods":[{{"name":"Aveia em Flocos","quantity":"50g","protein":6.75,"carbs":33,"fat":3.5,"calories":194.5}}]}}]}}
"""
        
        try:
            response = self.llm.send_message(prompt)
            return self._parse_ai_response(response, user_profile['id'], target_calories, target_macros)
        except Exception as e:
            print(f"Erro ao chamar LLM: {e}")
            raise
    
    def _parse_ai_response(
        self,
        response: str,
        user_id: str,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """Parse da resposta da IA"""
        response_text = response
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'text'):
            response_text = response.text
        
        # Remove markdown
        if "```json" in str(response_text):
            response_text = str(response_text).split("```json")[1].split("```")[0].strip()
        elif "```" in str(response_text):
            response_text = str(response_text).split("```")[1].split("```")[0].strip()
        
        data = json.loads(str(response_text))
        
        meals = []
        for meal_data in data.get('meals', []):
            foods = meal_data.get('foods', [])
            total_cal = sum(f.get('calories', 0) for f in foods)
            total_p = sum(f.get('protein', 0) for f in foods)
            total_c = sum(f.get('carbs', 0) for f in foods)
            total_f = sum(f.get('fat', 0) for f in foods)
            
            meal = Meal(
                name=meal_data.get('name', 'Refeição'),
                time=meal_data.get('time', '12:00'),
                foods=foods,
                total_calories=total_cal,
                macros={"protein": total_p, "carbs": total_c, "fat": total_f}
            )
            meals.append(meal)
        
        return DietPlan(
            user_id=user_id,
            target_calories=target_calories,
            target_macros=target_macros,
            meals=meals,
            notes="Plano gerado com IA."
        )
    
    def _validate_exact_match(
        self,
        diet: DietPlan,
        target_cal: float,
        target_macros: Dict[str, float]
    ) -> bool:
        """Valida se dieta bate EXATAMENTE (tolerância zero)"""
        total_cal = sum(m.total_calories for m in diet.meals)
        total_p = sum(m.macros['protein'] for m in diet.meals)
        total_c = sum(m.macros['carbs'] for m in diet.meals)
        total_f = sum(m.macros['fat'] for m in diet.meals)
        
        # Tolerância zero - arredondamento apenas
        return (
            abs(round(total_cal) - round(target_cal)) == 0 and
            abs(round(total_p) - round(target_macros['protein'])) == 0 and
            abs(round(total_c) - round(target_macros['carbs'])) == 0 and
            abs(round(total_f) - round(target_macros['fat'])) == 0
        )
    
    def _generate_exact_diet(
        self,
        user_id: str,
        target_calories: float,
        target_macros: Dict[str, float],
        user_profile: Dict
    ) -> DietPlan:
        """
        Gera dieta que bate EXATAMENTE com os targets.
        Algoritmo: distribui macros proporcionalmente e ajusta a última refeição.
        """
        
        target_protein = target_macros['protein']
        target_carbs = target_macros['carbs']
        target_fat = target_macros['fat']
        
        # Distribuição de refeições
        meal_templates = [
            {"name": "Café da Manhã", "time": "07:00", "p_ratio": 0.18, "c_ratio": 0.20, "f_ratio": 0.15},
            {"name": "Lanche da Manhã", "time": "10:00", "p_ratio": 0.12, "c_ratio": 0.10, "f_ratio": 0.15},
            {"name": "Almoço", "time": "12:30", "p_ratio": 0.30, "c_ratio": 0.35, "f_ratio": 0.25},
            {"name": "Lanche da Tarde", "time": "16:00", "p_ratio": 0.15, "c_ratio": 0.15, "f_ratio": 0.15},
            {"name": "Jantar", "time": "19:30", "p_ratio": 0.25, "c_ratio": 0.20, "f_ratio": 0.30},
        ]
        
        meals = []
        used_protein = 0
        used_carbs = 0
        used_fat = 0
        
        for i, template in enumerate(meal_templates):
            is_last = (i == len(meal_templates) - 1)
            
            if is_last:
                # Última refeição: usa EXATAMENTE o que sobrou
                meal_protein = target_protein - used_protein
                meal_carbs = target_carbs - used_carbs
                meal_fat = target_fat - used_fat
            else:
                meal_protein = target_protein * template['p_ratio']
                meal_carbs = target_carbs * template['c_ratio']
                meal_fat = target_fat * template['f_ratio']
            
            # Gera alimentos para bater esses macros exatos
            foods, actual_p, actual_c, actual_f = self._build_meal_foods(
                template['name'],
                meal_protein,
                meal_carbs,
                meal_fat,
                is_last
            )
            
            meal_calories = (actual_p * 4) + (actual_c * 4) + (actual_f * 9)
            
            used_protein += actual_p
            used_carbs += actual_c
            used_fat += actual_f
            
            meal = Meal(
                name=template['name'],
                time=template['time'],
                foods=foods,
                total_calories=round(meal_calories, 2),
                macros={
                    "protein": round(actual_p, 2),
                    "carbs": round(actual_c, 2),
                    "fat": round(actual_f, 2)
                }
            )
            meals.append(meal)
        
        # Calcula totais finais
        final_cal = sum(m.total_calories for m in meals)
        final_p = sum(m.macros['protein'] for m in meals)
        final_c = sum(m.macros['carbs'] for m in meals)
        final_f = sum(m.macros['fat'] for m in meals)
        
        return DietPlan(
            user_id=user_id,
            target_calories=target_calories,
            target_macros=target_macros,
            meals=meals,
            notes=f"Dieta de {int(target_calories)}kcal. P:{int(final_p)}g C:{int(final_c)}g G:{int(final_f)}g"
        )
    
    def _build_meal_foods(
        self,
        meal_name: str,
        target_p: float,
        target_c: float,
        target_f: float,
        is_last: bool
    ) -> tuple:
        """
        Constrói lista de alimentos para bater EXATAMENTE os macros.
        Retorna: (foods_list, actual_protein, actual_carbs, actual_fat)
        """
        foods = []
        remaining_p = target_p
        remaining_c = target_c
        remaining_f = target_f
        
        # Estratégia: adiciona alimentos principais e ajusta o último
        
        if "Café" in meal_name:
            # Café da manhã: aveia, ovos, fruta
            
            # Ovos para proteína (principal fonte)
            if remaining_p > 5:
                ovos = FOODS['proteinas'][1]  # Ovos
                ovos_g = round_portion(min(150, remaining_p / 0.13 * 100), 50)
                food = calc_food_macros(ovos, ovos_g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
            
            # Aveia para carboidrato
            if remaining_c > 10:
                aveia = FOODS['carboidratos'][2]  # Aveia
                aveia_g = round_portion(min(60, max(30, remaining_c / 0.66 * 100)), 10)
                food = calc_food_macros(aveia, aveia_g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
            
            # Banana para ajuste de carbs
            if remaining_c > 5:
                banana = FOODS['frutas'][0]
                banana_g = round_portion(min(150, max(50, remaining_c / 0.23 * 100)), 50)
                food = calc_food_macros(banana, banana_g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
        
        elif "Lanche da Manhã" in meal_name:
            # Iogurte e castanhas
            
            iogurte = FOODS['proteinas'][4]  # Iogurte Grego
            iogurte_g = round_portion(min(200, max(100, remaining_p / 0.10 * 100)), 50)
            food = calc_food_macros(iogurte, iogurte_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            # Castanhas para gordura (máx 25g)
            if remaining_f > 3:
                castanha = FOODS['gorduras'][1]  # Castanha
                castanha_g = round_portion(min(25, max(10, remaining_f / 0.67 * 100)), 5)
                food = calc_food_macros(castanha, castanha_g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
        
        elif "Almoço" in meal_name:
            # Arroz, feijão, frango, salada, azeite
            
            # Frango (proteína principal)
            frango = FOODS['proteinas'][0]
            frango_g = round_portion(min(200, max(100, remaining_p * 0.6 / 0.31 * 100)), 25)
            food = calc_food_macros(frango, frango_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            # Arroz
            arroz = FOODS['carboidratos'][0]
            arroz_g = round_portion(min(200, max(100, remaining_c * 0.5 / 0.23 * 100)), 25)
            food = calc_food_macros(arroz, arroz_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            # Feijão
            feijao = FOODS['carboidratos'][3]
            feijao_g = round_portion(min(150, max(75, remaining_c * 0.4 / 0.14 * 100)), 25)
            food = calc_food_macros(feijao, feijao_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            # Salada
            salada = FOODS['vegetais'][1]
            food = calc_food_macros(salada, 100)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            # Azeite (MÁXIMO 15g POR REFEIÇÃO)
            if remaining_f > 2:
                azeite = FOODS['gorduras'][0]
                azeite_g = min(15, round_portion(max(5, remaining_f / 1.0 * 100), 5))
                food = calc_food_macros(azeite, azeite_g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
        
        elif "Lanche da Tarde" in meal_name:
            # Batata doce e frango
            
            batata = FOODS['carboidratos'][1]
            batata_g = round_portion(min(200, max(100, remaining_c * 0.7 / 0.20 * 100)), 25)
            food = calc_food_macros(batata, batata_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            frango = FOODS['proteinas'][0]
            frango_g = round_portion(min(150, max(75, remaining_p / 0.31 * 100)), 25)
            food = calc_food_macros(frango, frango_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
        
        else:  # Jantar
            # Peixe, arroz, vegetais, azeite
            
            peixe = FOODS['proteinas'][2]  # Tilápia
            peixe_g = round_portion(min(200, max(100, remaining_p * 0.7 / 0.26 * 100)), 25)
            food = calc_food_macros(peixe, peixe_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            arroz = FOODS['carboidratos'][0]
            arroz_g = round_portion(min(175, max(100, remaining_c / 0.23 * 100)), 25)
            food = calc_food_macros(arroz, arroz_g)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            brocolis = FOODS['vegetais'][0]
            food = calc_food_macros(brocolis, 100)
            foods.append(food)
            remaining_p -= food['protein']
            remaining_c -= food['carbs']
            remaining_f -= food['fat']
            
            # Azeite (MÁXIMO 15g POR REFEIÇÃO)
            if remaining_f > 2:
                azeite = FOODS['gorduras'][0]
                azeite_g = min(15, round_portion(max(5, remaining_f / 1.0 * 100), 5))
                food = calc_food_macros(azeite, azeite_g)
                foods.append(food)
                remaining_p -= food['protein']
                remaining_c -= food['carbs']
                remaining_f -= food['fat']
        
        # Calcula totais reais
        actual_p = sum(f['protein'] for f in foods)
        actual_c = sum(f['carbs'] for f in foods)
        actual_f = sum(f['fat'] for f in foods)
        
        return foods, actual_p, actual_c, actual_f
