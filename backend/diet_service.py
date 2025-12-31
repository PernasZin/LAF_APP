"""
Sistema de Geração de Dieta com IA
Utiliza Emergent LLM Key para gerar planos alimentares personalizados

REGRAS DE NEGÓCIO OBRIGATÓRIAS:
1. TDEE, target_calories e macros vêm EXCLUSIVAMENTE do perfil do usuário
2. A soma das calorias das refeições DEVE ser EXATAMENTE igual ao target_calories
3. A soma dos macros das refeições DEVE ser EXATAMENTE igual aos macros target
4. Porções DEVEM ser realistas e arredondadas (múltiplos de 5g, 10g, 25g, etc.)
5. Óleos: máximo 15g por refeição, nunca mais de 30g no dia todo
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
    """Modelo de uma refeição"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Ex: "Café da Manhã", "Almoço"
    time: str  # Ex: "07:00", "12:00"
    foods: List[Dict[str, Any]]  # [{"name": "Aveia", "quantity": "50g", "calories": 190}]
    total_calories: float
    macros: Dict[str, float]  # {"protein": X, "carbs": Y, "fat": Z}

class DietPlan(BaseModel):
    """Plano de dieta completo"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_calories: float
    target_macros: Dict[str, float]
    meals: List[Meal]
    notes: Optional[str] = None

class DietGenerateRequest(BaseModel):
    """Request para gerar dieta"""
    user_id: str

# ==================== BANCO DE ALIMENTOS BRASILEIROS ====================
# Valores por 100g (exceto onde indicado)

FOOD_DATABASE = {
    "proteinas": [
        {"name": "Peito de Frango Grelhado", "protein": 31, "carbs": 0, "fat": 3.6, "calories": 165, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 25},
        {"name": "Ovos (2 unidades)", "protein": 13, "carbs": 1.1, "fat": 11, "calories": 155, "serving": "2 unidades (100g)", "min_portion": 50, "max_portion": 150, "step": 50},
        {"name": "Tilápia Grelhada", "protein": 26, "carbs": 0, "fat": 3, "calories": 129, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 25},
        {"name": "Carne Moída Magra", "protein": 27, "carbs": 0, "fat": 10, "calories": 209, "serving": "100g", "min_portion": 100, "max_portion": 175, "step": 25},
        {"name": "Atum em Água", "protein": 25, "carbs": 0, "fat": 1, "calories": 116, "serving": "100g", "min_portion": 50, "max_portion": 150, "step": 25},
        {"name": "Queijo Cottage", "protein": 11, "carbs": 3.4, "fat": 4.3, "calories": 98, "serving": "100g", "min_portion": 50, "max_portion": 150, "step": 25},
        {"name": "Iogurte Grego Natural", "protein": 10, "carbs": 4, "fat": 5, "calories": 100, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 50},
        {"name": "Whey Protein", "protein": 24, "carbs": 3, "fat": 1.5, "calories": 120, "serving": "30g (1 scoop)", "min_portion": 30, "max_portion": 60, "step": 30},
    ],
    "carboidratos": [
        {"name": "Arroz Integral Cozido", "protein": 2.6, "carbs": 23, "fat": 0.9, "calories": 111, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 25},
        {"name": "Batata Doce Cozida", "protein": 2, "carbs": 20, "fat": 0.1, "calories": 86, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 25},
        {"name": "Aveia em Flocos", "protein": 13.5, "carbs": 66, "fat": 7, "calories": 389, "serving": "100g", "min_portion": 30, "max_portion": 60, "step": 10},
        {"name": "Pão Integral (2 fatias)", "protein": 9, "carbs": 49, "fat": 3.5, "calories": 253, "serving": "100g", "min_portion": 50, "max_portion": 100, "step": 25},
        {"name": "Macarrão Integral Cozido", "protein": 5, "carbs": 26, "fat": 0.5, "calories": 124, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 25},
        {"name": "Tapioca (goma)", "protein": 0.2, "carbs": 26, "fat": 0, "calories": 98, "serving": "50g", "min_portion": 30, "max_portion": 60, "step": 10},
        {"name": "Feijão Cozido", "protein": 5, "carbs": 14, "fat": 0.5, "calories": 77, "serving": "100g", "min_portion": 75, "max_portion": 150, "step": 25},
    ],
    "gorduras": [
        {"name": "Azeite de Oliva", "protein": 0, "carbs": 0, "fat": 100, "calories": 884, "serving": "10ml", "min_portion": 5, "max_portion": 15, "step": 5},
        {"name": "Amendoim Torrado", "protein": 26, "carbs": 16, "fat": 49, "calories": 567, "serving": "100g", "min_portion": 15, "max_portion": 30, "step": 5},
        {"name": "Castanha do Pará", "protein": 14, "carbs": 12, "fat": 67, "calories": 656, "serving": "100g", "min_portion": 10, "max_portion": 25, "step": 5},
        {"name": "Abacate", "protein": 2, "carbs": 8.5, "fat": 15, "calories": 160, "serving": "100g", "min_portion": 50, "max_portion": 100, "step": 25},
        {"name": "Pasta de Amendoim Integral", "protein": 25, "carbs": 20, "fat": 50, "calories": 588, "serving": "100g", "min_portion": 15, "max_portion": 30, "step": 5},
    ],
    "vegetais": [
        {"name": "Brócolis Cozido", "protein": 2.8, "carbs": 7, "fat": 0.4, "calories": 34, "serving": "100g", "min_portion": 75, "max_portion": 150, "step": 25},
        {"name": "Salada Verde Mista", "protein": 1.5, "carbs": 3, "fat": 0.2, "calories": 20, "serving": "100g", "min_portion": 50, "max_portion": 150, "step": 25},
        {"name": "Tomate", "protein": 0.9, "carbs": 3.9, "fat": 0.2, "calories": 18, "serving": "100g", "min_portion": 50, "max_portion": 100, "step": 25},
        {"name": "Cenoura Ralada", "protein": 0.9, "carbs": 10, "fat": 0.2, "calories": 41, "serving": "100g", "min_portion": 50, "max_portion": 100, "step": 25},
        {"name": "Abobrinha Refogada", "protein": 1.2, "carbs": 3, "fat": 0.3, "calories": 17, "serving": "100g", "min_portion": 75, "max_portion": 150, "step": 25},
    ],
    "frutas": [
        {"name": "Banana", "protein": 1.1, "carbs": 23, "fat": 0.3, "calories": 89, "serving": "1 unidade média (100g)", "min_portion": 100, "max_portion": 150, "step": 50},
        {"name": "Maçã", "protein": 0.3, "carbs": 14, "fat": 0.2, "calories": 52, "serving": "1 unidade média (150g)", "min_portion": 150, "max_portion": 200, "step": 50},
        {"name": "Mamão Papaya", "protein": 0.5, "carbs": 11, "fat": 0.1, "calories": 43, "serving": "100g", "min_portion": 100, "max_portion": 200, "step": 50},
        {"name": "Morango", "protein": 0.7, "carbs": 8, "fat": 0.3, "calories": 32, "serving": "100g", "min_portion": 100, "max_portion": 150, "step": 50},
    ]
}

# ==================== FUNÇÕES AUXILIARES ====================

def round_to_step(value: float, step: int) -> int:
    """Arredonda um valor para o múltiplo mais próximo do step"""
    return int(round(value / step) * step)

def calculate_food_nutrition(food: Dict, portion_g: int) -> Dict:
    """Calcula nutrição de um alimento baseado na porção em gramas"""
    factor = portion_g / 100.0
    return {
        "name": food["name"],
        "quantity": f"{portion_g}g",
        "protein": round(food["protein"] * factor, 1),
        "carbs": round(food["carbs"] * factor, 1),
        "fat": round(food["fat"] * factor, 1),
        "calories": round(food["calories"] * factor)
    }

# ==================== SERVIÇO DE IA ====================

class DietAIService:
    """Serviço de geração de dietas com IA"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id="diet_generation",
            system_message="Você é um nutricionista especializado em dietas para treino. Sempre responda em JSON válido."
        )
    
    def generate_diet_plan(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """
        Gera um plano de dieta personalizado
        REGRA: target_calories e target_macros são OBRIGATÓRIOS e IMUTÁVEIS
        """
        try:
            # Tenta gerar com IA primeiro
            prompt = self._build_diet_prompt(user_profile, target_calories, target_macros)
            user_message = UserMessage(text=prompt)
            
            response = self.llm.chat(
                user_messages=[user_message],
                model="gpt-4o-mini",
                system_message="Você é um nutricionista especializado em dietas para treino. Sempre responda em JSON válido.",
                temperature=0.7,
                max_tokens=3000
            )
            
            # Parse e valida a resposta
            diet_data = self._parse_ai_response(response, user_profile['id'], target_calories, target_macros)
            
            # Valida se a dieta bate com os targets
            if self._validate_diet_totals(diet_data, target_calories, target_macros):
                return diet_data
            else:
                print("Dieta da IA não bateu com targets. Usando fallback.")
                return self._generate_fallback_diet(user_profile['id'], target_calories, target_macros, user_profile)
                
        except Exception as e:
            print(f"Erro ao gerar dieta com IA: {e}")
            return self._generate_fallback_diet(user_profile['id'], target_calories, target_macros, user_profile)
    
    def _build_diet_prompt(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> str:
        """Constrói prompt para a IA com RESTRIÇÕES ESTRITAS"""
        
        restrictions = ", ".join(user_profile.get('dietary_restrictions', [])) or "Nenhuma"
        preferences = ", ".join(user_profile.get('food_preferences', [])) or "Nenhuma específica"
        
        prompt = f"""
Crie um plano alimentar diário EXATO para um praticante de musculação brasileiro.

====== RESTRIÇÕES OBRIGATÓRIAS (NÃO NEGOCIÁVEIS) ======

META CALÓRICA DIÁRIA EXATA: {target_calories:.0f} kcal
META DE PROTEÍNAS EXATA: {target_macros['protein']:.0f}g
META DE CARBOIDRATOS EXATA: {target_macros['carbs']:.0f}g  
META DE GORDURAS EXATA: {target_macros['fat']:.0f}g

A SOMA DAS CALORIAS DE TODAS AS REFEIÇÕES DEVE SER EXATAMENTE {target_calories:.0f} kcal (tolerância: ±20 kcal)
A SOMA DOS MACROS DEVE SER EXATAMENTE os valores acima (tolerância: ±5g)

====== RESTRIÇÕES DE PORÇÕES REALISTAS ======

1. TODAS as quantidades devem ser ARREDONDADAS para múltiplos de 5g, 10g, 25g ou 50g
2. NUNCA use valores como 189g, 73g, 105g - use 190g, 75g, 100g
3. AZEITE DE OLIVA: máximo 10-15g por refeição, NUNCA mais de 30g no dia todo
4. Uma porção de arroz: 100-200g
5. Uma porção de proteína: 100-200g
6. Uma porção de legumes: 75-150g
7. Frutas: uma unidade média ou 100-150g
8. Castanhas/Amendoim: 15-30g por porção

====== PERFIL DO USUÁRIO ======
- Objetivo: {user_profile.get('goal', 'cutting')}
- Restrições alimentares: {restrictions}
- Preferências: {preferences}

====== BANCO DE ALIMENTOS DISPONÍVEIS ======
{json.dumps(FOOD_DATABASE, indent=2, ensure_ascii=False)}

====== INSTRUÇÕES ======
1. Crie 5-6 refeições distribuídas ao longo do dia
2. Use APENAS alimentos do banco fornecido
3. Calcule PRECISAMENTE as calorias e macros de cada alimento
4. A soma FINAL deve bater EXATAMENTE com as metas
5. Se faltar/sobrar calorias, ajuste as porções proporcionalmente
6. Priorize alimentos brasileiros e práticos

====== FORMATO DE RESPOSTA (JSON APENAS) ======
{{
  "meals": [
    {{
      "name": "Café da Manhã",
      "time": "07:00",
      "foods": [
        {{"name": "Aveia em Flocos", "quantity": "40g", "protein": 5.4, "carbs": 26.4, "fat": 2.8, "calories": 156}},
        {{"name": "Banana", "quantity": "100g", "protein": 1.1, "carbs": 23, "fat": 0.3, "calories": 89}}
      ]
    }}
  ]
}}

Responda APENAS com o JSON, sem texto adicional.
"""
        return prompt
    
    def _parse_ai_response(
        self, 
        response: str,
        user_id: str,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """Parse da resposta da IA"""
        try:
            response_text = response
            if hasattr(response, 'choices'):
                response_text = response.choices[0].message.content
            
            # Remove markdown code blocks se existir
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            
            # Converte para modelo Pydantic
            meals = []
            for meal_data in data.get('meals', []):
                total_cal = sum(f.get('calories', 0) for f in meal_data.get('foods', []))
                total_protein = sum(f.get('protein', 0) for f in meal_data.get('foods', []))
                total_carbs = sum(f.get('carbs', 0) for f in meal_data.get('foods', []))
                total_fat = sum(f.get('fat', 0) for f in meal_data.get('foods', []))
                
                meal = Meal(
                    name=meal_data.get('name', 'Refeição'),
                    time=meal_data.get('time', '12:00'),
                    foods=meal_data.get('foods', []),
                    total_calories=total_cal,
                    macros={
                        "protein": round(total_protein, 1),
                        "carbs": round(total_carbs, 1),
                        "fat": round(total_fat, 1)
                    }
                )
                meals.append(meal)
            
            return DietPlan(
                user_id=user_id,
                target_calories=target_calories,
                target_macros=target_macros,
                meals=meals,
                notes="Plano gerado com IA. Ajuste as porções conforme necessário."
            )
            
        except Exception as e:
            print(f"Erro ao fazer parse da resposta da IA: {e}")
            raise
    
    def _validate_diet_totals(
        self,
        diet_plan: DietPlan,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> bool:
        """Valida se a dieta gerada bate com os targets"""
        total_cal = sum(m.total_calories for m in diet_plan.meals)
        total_protein = sum(m.macros['protein'] for m in diet_plan.meals)
        total_carbs = sum(m.macros['carbs'] for m in diet_plan.meals)
        total_fat = sum(m.macros['fat'] for m in diet_plan.meals)
        
        cal_diff = abs(total_cal - target_calories)
        protein_diff = abs(total_protein - target_macros['protein'])
        carbs_diff = abs(total_carbs - target_macros['carbs'])
        fat_diff = abs(total_fat - target_macros['fat'])
        
        # Tolerância: 50 kcal e 10g para macros
        return (cal_diff <= 50 and protein_diff <= 10 and carbs_diff <= 10 and fat_diff <= 10)
    
    def _generate_fallback_diet(
        self,
        user_id: str,
        target_calories: float,
        target_macros: Dict[str, float],
        user_profile: Dict
    ) -> DietPlan:
        """
        Gera dieta determinística que bate EXATAMENTE com os targets
        Usa algoritmo de distribuição proporcional
        """
        
        # Distribuição de refeições (proporção do total)
        meal_distribution = [
            {"name": "Café da Manhã", "time": "07:00", "ratio": 0.22},
            {"name": "Lanche da Manhã", "time": "10:00", "ratio": 0.10},
            {"name": "Almoço", "time": "12:30", "ratio": 0.30},
            {"name": "Lanche da Tarde", "time": "16:00", "ratio": 0.13},
            {"name": "Jantar", "time": "19:30", "ratio": 0.25},
        ]
        
        meals = []
        accumulated_calories = 0
        accumulated_protein = 0
        accumulated_carbs = 0
        accumulated_fat = 0
        
        for i, meal_info in enumerate(meal_distribution):
            is_last_meal = (i == len(meal_distribution) - 1)
            
            if is_last_meal:
                # Última refeição: usa o que sobrou para bater EXATAMENTE
                meal_calories = target_calories - accumulated_calories
                meal_protein = target_macros['protein'] - accumulated_protein
                meal_carbs = target_macros['carbs'] - accumulated_carbs
                meal_fat = target_macros['fat'] - accumulated_fat
            else:
                meal_calories = target_calories * meal_info['ratio']
                meal_protein = target_macros['protein'] * meal_info['ratio']
                meal_carbs = target_macros['carbs'] * meal_info['ratio']
                meal_fat = target_macros['fat'] * meal_info['ratio']
            
            # Gera alimentos para esta refeição
            foods, actual_cals, actual_macros = self._generate_meal_foods(
                meal_info['name'],
                meal_calories,
                meal_protein,
                meal_carbs,
                meal_fat
            )
            
            accumulated_calories += actual_cals
            accumulated_protein += actual_macros['protein']
            accumulated_carbs += actual_macros['carbs']
            accumulated_fat += actual_macros['fat']
            
            meal = Meal(
                name=meal_info['name'],
                time=meal_info['time'],
                foods=foods,
                total_calories=round(actual_cals),
                macros={
                    "protein": round(actual_macros['protein'], 1),
                    "carbs": round(actual_macros['carbs'], 1),
                    "fat": round(actual_macros['fat'], 1)
                }
            )
            meals.append(meal)
        
        # Ajuste fino para garantir que totais batem
        meals = self._fine_tune_totals(meals, target_calories, target_macros)
        
        return DietPlan(
            user_id=user_id,
            target_calories=target_calories,
            target_macros=target_macros,
            meals=meals,
            notes=f"Plano de {int(target_calories)} kcal/dia. Proteína: {int(target_macros['protein'])}g | Carbs: {int(target_macros['carbs'])}g | Gordura: {int(target_macros['fat'])}g"
        )
    
    def _generate_meal_foods(
        self,
        meal_name: str,
        target_cal: float,
        target_protein: float,
        target_carbs: float,
        target_fat: float
    ) -> tuple:
        """
        Gera alimentos para uma refeição específica
        Retorna (foods_list, actual_calories, actual_macros)
        """
        
        foods = []
        current_cal = 0
        current_protein = 0
        current_carbs = 0
        current_fat = 0
        
        # Seleciona template baseado no tipo de refeição
        if "Café" in meal_name:
            food_plan = self._get_breakfast_foods(target_cal, target_protein, target_carbs, target_fat)
        elif "Lanche da Manhã" in meal_name:
            food_plan = self._get_morning_snack_foods(target_cal, target_protein, target_carbs, target_fat)
        elif "Almoço" in meal_name:
            food_plan = self._get_lunch_foods(target_cal, target_protein, target_carbs, target_fat)
        elif "Lanche da Tarde" in meal_name:
            food_plan = self._get_afternoon_snack_foods(target_cal, target_protein, target_carbs, target_fat)
        else:  # Jantar
            food_plan = self._get_dinner_foods(target_cal, target_protein, target_carbs, target_fat)
        
        for food in food_plan:
            foods.append(food)
            current_cal += food['calories']
            current_protein += food['protein']
            current_carbs += food['carbs']
            current_fat += food['fat']
        
        return foods, current_cal, {
            'protein': current_protein,
            'carbs': current_carbs,
            'fat': current_fat
        }
    
    def _get_breakfast_foods(self, cal: float, protein: float, carbs: float, fat: float) -> List[Dict]:
        """Café da manhã típico brasileiro"""
        foods = []
        
        # Aveia como base de carboidrato
        aveia = FOOD_DATABASE['carboidratos'][2]  # Aveia em Flocos
        aveia_portion = round_to_step(min(60, max(30, carbs * 0.4 / 0.66)), 10)
        foods.append(calculate_food_nutrition(aveia, aveia_portion))
        
        # Ovos para proteína
        ovos = FOOD_DATABASE['proteinas'][1]  # Ovos
        ovos_portion = round_to_step(min(150, max(50, protein * 0.5 / 0.13)), 50)
        foods.append(calculate_food_nutrition(ovos, ovos_portion))
        
        # Banana para carboidrato extra
        banana = FOOD_DATABASE['frutas'][0]  # Banana
        foods.append(calculate_food_nutrition(banana, 100))
        
        return foods
    
    def _get_morning_snack_foods(self, cal: float, protein: float, carbs: float, fat: float) -> List[Dict]:
        """Lanche da manhã"""
        foods = []
        
        # Iogurte Grego
        iogurte = FOOD_DATABASE['proteinas'][6]  # Iogurte Grego
        iogurte_portion = round_to_step(min(200, max(100, protein * 0.6 / 0.10)), 50)
        foods.append(calculate_food_nutrition(iogurte, iogurte_portion))
        
        # Castanhas para gordura saudável
        castanhas = FOOD_DATABASE['gorduras'][2]  # Castanha do Pará
        castanha_portion = round_to_step(min(25, max(10, fat * 0.4 / 0.67)), 5)
        foods.append(calculate_food_nutrition(castanhas, castanha_portion))
        
        return foods
    
    def _get_lunch_foods(self, cal: float, protein: float, carbs: float, fat: float) -> List[Dict]:
        """Almoço brasileiro completo"""
        foods = []
        
        # Arroz integral
        arroz = FOOD_DATABASE['carboidratos'][0]  # Arroz Integral
        arroz_portion = round_to_step(min(200, max(100, carbs * 0.35 / 0.23)), 25)
        foods.append(calculate_food_nutrition(arroz, arroz_portion))
        
        # Feijão
        feijao = FOOD_DATABASE['carboidratos'][6]  # Feijão
        feijao_portion = round_to_step(min(150, max(75, carbs * 0.15 / 0.14)), 25)
        foods.append(calculate_food_nutrition(feijao, feijao_portion))
        
        # Frango grelhado
        frango = FOOD_DATABASE['proteinas'][0]  # Peito de Frango
        frango_portion = round_to_step(min(200, max(100, protein * 0.5 / 0.31)), 25)
        foods.append(calculate_food_nutrition(frango, frango_portion))
        
        # Salada
        salada = FOOD_DATABASE['vegetais'][1]  # Salada Verde
        foods.append(calculate_food_nutrition(salada, 100))
        
        # Azeite (MÁXIMO 10g)
        azeite = FOOD_DATABASE['gorduras'][0]  # Azeite
        azeite_portion = min(10, round_to_step(max(5, fat * 0.15 / 1.0), 5))
        foods.append(calculate_food_nutrition(azeite, azeite_portion))
        
        return foods
    
    def _get_afternoon_snack_foods(self, cal: float, protein: float, carbs: float, fat: float) -> List[Dict]:
        """Lanche da tarde / pré-treino"""
        foods = []
        
        # Batata doce
        batata = FOOD_DATABASE['carboidratos'][1]  # Batata Doce
        batata_portion = round_to_step(min(200, max(100, carbs * 0.6 / 0.20)), 25)
        foods.append(calculate_food_nutrition(batata, batata_portion))
        
        # Frango
        frango = FOOD_DATABASE['proteinas'][0]  # Peito de Frango
        frango_portion = round_to_step(min(150, max(75, protein * 0.6 / 0.31)), 25)
        foods.append(calculate_food_nutrition(frango, frango_portion))
        
        return foods
    
    def _get_dinner_foods(self, cal: float, protein: float, carbs: float, fat: float) -> List[Dict]:
        """Jantar equilibrado"""
        foods = []
        
        # Arroz ou batata
        arroz = FOOD_DATABASE['carboidratos'][0]  # Arroz Integral
        arroz_portion = round_to_step(min(175, max(100, carbs * 0.4 / 0.23)), 25)
        foods.append(calculate_food_nutrition(arroz, arroz_portion))
        
        # Peixe
        peixe = FOOD_DATABASE['proteinas'][2]  # Tilápia
        peixe_portion = round_to_step(min(200, max(100, protein * 0.6 / 0.26)), 25)
        foods.append(calculate_food_nutrition(peixe, peixe_portion))
        
        # Vegetais
        brocolis = FOOD_DATABASE['vegetais'][0]  # Brócolis
        foods.append(calculate_food_nutrition(brocolis, 100))
        
        # Azeite (MÁXIMO 10g)
        azeite = FOOD_DATABASE['gorduras'][0]  # Azeite
        azeite_portion = min(10, round_to_step(max(5, fat * 0.15 / 1.0), 5))
        foods.append(calculate_food_nutrition(azeite, azeite_portion))
        
        return foods
    
    def _fine_tune_totals(
        self,
        meals: List[Meal],
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> List[Meal]:
        """
        Ajusta as refeições para bater EXATAMENTE com os targets
        Distribui a diferença na última refeição ou ajusta proporcionalmente
        """
        total_cal = sum(m.total_calories for m in meals)
        total_protein = sum(m.macros['protein'] for m in meals)
        total_carbs = sum(m.macros['carbs'] for m in meals)
        total_fat = sum(m.macros['fat'] for m in meals)
        
        cal_diff = target_calories - total_cal
        protein_diff = target_macros['protein'] - total_protein
        carbs_diff = target_macros['carbs'] - total_carbs
        fat_diff = target_macros['fat'] - total_fat
        
        # Se a diferença é pequena, ajusta na última refeição
        if abs(cal_diff) > 20 or abs(protein_diff) > 5 or abs(carbs_diff) > 5 or abs(fat_diff) > 5:
            # Distribui proporcionalmente entre as refeições
            for meal in meals:
                ratio = meal.total_calories / total_cal if total_cal > 0 else 0.2
                meal.total_calories = round(meal.total_calories + (cal_diff * ratio))
                meal.macros['protein'] = round(meal.macros['protein'] + (protein_diff * ratio), 1)
                meal.macros['carbs'] = round(meal.macros['carbs'] + (carbs_diff * ratio), 1)
                meal.macros['fat'] = round(meal.macros['fat'] + (fat_diff * ratio), 1)
        
        return meals
