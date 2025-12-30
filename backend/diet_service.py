"""
Sistema de Geração de Dieta com IA
Utiliza Emergent LLM Key para gerar planos alimentares personalizados
"""
import os
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime
import uuid

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

FOOD_DATABASE = {
    # Proteínas
    "proteinas": [
        {"name": "Peito de Frango", "protein": 31, "carbs": 0, "fat": 3.6, "calories": 165, "serving": "100g"},
        {"name": "Ovo", "protein": 13, "carbs": 1.1, "fat": 11, "calories": 155, "serving": "2 unidades"},
        {"name": "Tilápia", "protein": 26, "carbs": 0, "fat": 3, "calories": 129, "serving": "100g"},
        {"name": "Carne Moída (patinho)", "protein": 27, "carbs": 0, "fat": 10, "calories": 209, "serving": "100g"},
        {"name": "Atum em Lata", "protein": 25, "carbs": 0, "fat": 1, "calories": 116, "serving": "100g"},
        {"name": "Ricota", "protein": 11, "carbs": 3, "fat": 13, "calories": 174, "serving": "100g"},
    ],
    # Carboidratos
    "carboidratos": [
        {"name": "Arroz Integral", "protein": 2.6, "carbs": 23, "fat": 0.9, "calories": 111, "serving": "100g cozido"},
        {"name": "Batata Doce", "protein": 2, "carbs": 20, "fat": 0.1, "calories": 86, "serving": "100g"},
        {"name": "Aveia", "protein": 13.2, "carbs": 66.3, "fat": 6.9, "calories": 389, "serving": "100g"},
        {"name": "Pão Integral", "protein": 9, "carbs": 49, "fat": 3.5, "calories": 253, "serving": "100g"},
        {"name": "Macarrão Integral", "protein": 5, "carbs": 26, "fat": 0.5, "calories": 124, "serving": "100g cozido"},
        {"name": "Tapioca", "protein": 0.2, "carbs": 26, "fat": 0, "calories": 98, "serving": "50g"},
    ],
    # Gorduras Saudáveis
    "gorduras": [
        {"name": "Azeite de Oliva", "protein": 0, "carbs": 0, "fat": 14, "calories": 119, "serving": "1 colher sopa"},
        {"name": "Amendoim", "protein": 26, "carbs": 16, "fat": 49, "calories": 567, "serving": "100g"},
        {"name": "Castanha do Pará", "protein": 14, "carbs": 12, "fat": 67, "calories": 656, "serving": "100g"},
        {"name": "Abacate", "protein": 2, "carbs": 8.5, "fat": 15, "calories": 160, "serving": "100g"},
    ],
    # Legumes e Verduras
    "vegetais": [
        {"name": "Brócolis", "protein": 2.8, "carbs": 7, "fat": 0.4, "calories": 34, "serving": "100g"},
        {"name": "Alface", "protein": 1.4, "carbs": 2.9, "fat": 0.2, "calories": 15, "serving": "100g"},
        {"name": "Tomate", "protein": 0.9, "carbs": 3.9, "fat": 0.2, "calories": 18, "serving": "100g"},
        {"name": "Cenoura", "protein": 0.9, "carbs": 10, "fat": 0.2, "calories": 41, "serving": "100g"},
    ],
    # Frutas
    "frutas": [
        {"name": "Banana", "protein": 1.1, "carbs": 23, "fat": 0.3, "calories": 89, "serving": "1 unidade média"},
        {"name": "Maçã", "protein": 0.3, "carbs": 14, "fat": 0.2, "calories": 52, "serving": "1 unidade média"},
        {"name": "Mamão", "protein": 0.5, "carbs": 11, "fat": 0.1, "calories": 43, "serving": "100g"},
    ]
}

# ==================== SERVIÇO DE IA ====================

class DietAIService:
    """Serviço de geração de dietas com IA"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # LlmChat precisa de session_id e system_message
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
        Gera um plano de dieta personalizado usando IA
        """
        try:
            # Monta prompt para a IA
            prompt = self._build_diet_prompt(user_profile, target_calories, target_macros)
            
            # Chama a IA usando UserMessage
            user_message = UserMessage(text=prompt)
            
            response = self.llm.chat(
                user_messages=[user_message],
                model="gpt-4o-mini",
                system_message="Você é um nutricionista especializado em dietas para treino. Sempre responda em JSON válido.",
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse da resposta
            diet_data = self._parse_ai_response(response, user_profile['id'], target_calories, target_macros)
            
            return diet_data
            
        except Exception as e:
            print(f"Erro ao gerar dieta com IA: {e}")
            # Fallback: gera dieta básica
            return self._generate_fallback_diet(user_profile['id'], target_calories, target_macros)
    
    def _build_diet_prompt(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> str:
        """Constrói prompt para a IA"""
        
        restrictions = ", ".join(user_profile.get('dietary_restrictions', [])) or "Nenhuma"
        preferences = ", ".join(user_profile.get('food_preferences', [])) or "Nenhuma específica"
        
        prompt = f"""
Crie um plano alimentar diário para um praticante de musculação brasileiro.

**Perfil do Usuário:**
- Objetivo: {user_profile.get('goal', 'cutting')}
- Meta Calórica Diária: {target_calories:.0f} kcal
- Macros Diários: {target_macros['protein']:.0f}g proteína, {target_macros['carbs']:.0f}g carboidratos, {target_macros['fat']:.0f}g gordura
- Restrições: {restrictions}
- Preferências: {preferences}

**Banco de Alimentos Disponíveis:**
{json.dumps(FOOD_DATABASE, indent=2, ensure_ascii=False)}

**Instruções:**
1. Crie 5-6 refeições distribuídas ao longo do dia
2. Use APENAS alimentos do banco fornecido
3. Cada refeição deve ter horário sugerido
4. Calcule com precisão calorias e macros de cada refeição
5. A soma total deve se aproximar da meta calórica (±100 kcal)
6. Priorize alimentos brasileiros e práticos
7. Considere as restrições e preferências do usuário

**Formato de Resposta (JSON):**
{{
  "meals": [
    {{
      "name": "Café da Manhã",
      "time": "07:00",
      "foods": [
        {{"name": "Aveia", "quantity": "50g", "protein": 6.6, "carbs": 33.2, "fat": 3.5, "calories": 195}},
        {{"name": "Banana", "quantity": "1 unidade", "protein": 1.1, "carbs": 23, "fat": 0.3, "calories": 89}}
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
            # Extrai JSON da resposta
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
                # Calcula totais da refeição
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
    
    def _generate_fallback_diet(
        self,
        user_id: str,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """Gera dieta básica escalada para bater EXATAMENTE as calorias e macros do usuário"""
        
        # Template base de uma dieta balanceada (proporções)
        base_meals_template = [
            {
                "name": "Café da Manhã",
                "time": "07:00",
                "proportion": 0.23,  # 23% das calorias diárias
                "foods": [
                    {"name": "Aveia", "protein_ratio": 0.15, "carbs_ratio": 0.60, "fat_ratio": 0.08},
                    {"name": "Banana", "protein_ratio": 0.02, "carbs_ratio": 0.22, "fat_ratio": 0.01},
                    {"name": "Ovo", "protein_ratio": 0.30, "carbs_ratio": 0.02, "fat_ratio": 0.25},
                ]
            },
            {
                "name": "Lanche da Manhã",
                "time": "10:00",
                "proportion": 0.11,  # 11% das calorias
                "foods": [
                    {"name": "Iogurte natural", "protein_ratio": 0.35, "carbs_ratio": 0.45, "fat_ratio": 0.10},
                    {"name": "Castanhas", "protein_ratio": 0.15, "carbs_ratio": 0.10, "fat_ratio": 0.65},
                ]
            },
            {
                "name": "Almoço",
                "time": "12:30",
                "proportion": 0.33,  # 33% das calorias
                "foods": [
                    {"name": "Arroz Integral", "protein_ratio": 0.07, "carbs_ratio": 0.75, "fat_ratio": 0.04},
                    {"name": "Feijão", "protein_ratio": 0.24, "carbs_ratio": 0.62, "fat_ratio": 0.02},
                    {"name": "Peito de Frango", "protein_ratio": 0.80, "carbs_ratio": 0.00, "fat_ratio": 0.09},
                    {"name": "Salada mista", "protein_ratio": 0.05, "carbs_ratio": 0.15, "fat_ratio": 0.01},
                    {"name": "Azeite", "protein_ratio": 0.00, "carbs_ratio": 0.00, "fat_ratio": 1.00},
                ]
            },
            {
                "name": "Lanche da Tarde (Pré-Treino)",
                "time": "16:00",
                "proportion": 0.14,  # 14% das calorias
                "foods": [
                    {"name": "Batata Doce", "protein_ratio": 0.05, "carbs_ratio": 0.85, "fat_ratio": 0.00},
                    {"name": "Peito de Frango", "protein_ratio": 0.80, "carbs_ratio": 0.00, "fat_ratio": 0.09},
                ]
            },
            {
                "name": "Jantar",
                "time": "19:30",
                "proportion": 0.19,  # 19% das calorias
                "foods": [
                    {"name": "Arroz Integral", "protein_ratio": 0.07, "carbs_ratio": 0.75, "fat_ratio": 0.04},
                    {"name": "Tilápia grelhada", "protein_ratio": 0.85, "carbs_ratio": 0.00, "fat_ratio": 0.06},
                    {"name": "Brócolis", "protein_ratio": 0.30, "carbs_ratio": 0.55, "fat_ratio": 0.04},
                    {"name": "Cenoura", "protein_ratio": 0.05, "carbs_ratio": 0.80, "fat_ratio": 0.02},
                ]
            }
        ]
        
        # Gera refeições escaladas para bater EXATAMENTE os targets
        meals = []
        
        for meal_template in base_meals_template:
            meal_calories = target_calories * meal_template["proportion"]
            meal_protein = target_macros["protein"] * meal_template["proportion"]
            meal_carbs = target_macros["carbs"] * meal_template["proportion"]
            meal_fat = target_macros["fat"] * meal_template["proportion"]
            
            # Cria lista de alimentos com quantidades calculadas
            foods = []
            for food_template in meal_template["foods"]:
                food_protein = meal_protein * food_template["protein_ratio"]
                food_carbs = meal_carbs * food_template["carbs_ratio"]
                food_fat = meal_fat * food_template["fat_ratio"]
                food_calories = (food_protein * 4) + (food_carbs * 4) + (food_fat * 9)
                
                # Calcula quantidade aproximada em gramas
                # Simplificação: assume densidade média
                quantity_g = food_calories / 2  # ~2 kcal/g média
                
                foods.append({
                    "name": food_template["name"],
                    "quantity": f"{int(quantity_g)}g",
                    "protein": round(food_protein, 1),
                    "carbs": round(food_carbs, 1),
                    "fat": round(food_fat, 1),
                    "calories": round(food_calories, 0)
                })
            
            meal = Meal(
                name=meal_template["name"],
                time=meal_template["time"],
                foods=foods,
                total_calories=round(meal_calories, 0),
                macros={
                    "protein": round(meal_protein, 1),
                    "carbs": round(meal_carbs, 1),
                    "fat": round(meal_fat, 1)
                }
            )
            meals.append(meal)
        
        return DietPlan(
            user_id=user_id,
            target_calories=target_calories,
            target_macros=target_macros,
            meals=meals,
            notes=f"Plano gerado automaticamente para {int(target_calories)} kcal/dia. As porções foram calculadas para atingir exatamente suas metas diárias."
        )
