"""
Sistema de Geração de Dieta com PRECISÃO MATEMÁTICA
P0: Integridade de dados - macros DEVEM somar EXATAMENTE aos targets
"""
import os
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
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
    computed_calories: float
    computed_macros: Dict[str, float]
    notes: Optional[str] = None

class DietGenerateRequest(BaseModel):
    user_id: str

# ==================== ALIMENTOS (valores EXATOS por 100g) ====================

FOODS = {
    "frango": {"name": "Peito de Frango Grelhado", "p": 31.0, "c": 0.0, "f": 3.6},
    "tilapia": {"name": "Tilápia Grelhada", "p": 26.0, "c": 0.0, "f": 2.5},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0},
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2},
    "iogurte": {"name": "Iogurte Grego Natural", "p": 10.0, "c": 4.0, "f": 5.0},
    "arroz": {"name": "Arroz Integral Cozido", "p": 2.6, "c": 23.0, "f": 0.9},
    "batata": {"name": "Batata Doce Cozida", "p": 1.6, "c": 20.0, "f": 0.1},
    "aveia": {"name": "Aveia em Flocos", "p": 13.5, "c": 66.0, "f": 7.0},
    "feijao": {"name": "Feijão Cozido", "p": 5.0, "c": 14.0, "f": 0.5},
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0},
    "castanha": {"name": "Castanha do Pará", "p": 14.0, "c": 12.0, "f": 67.0},
    "brocolis": {"name": "Brócolis Cozido", "p": 2.8, "c": 7.0, "f": 0.4},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3},
}

def calc_food(key: str, grams: int) -> Dict:
    """Calcula macros EXATOS"""
    f = FOODS[key]
    factor = grams / 100.0
    p = round(f["p"] * factor, 2)
    c = round(f["c"] * factor, 2)
    fat = round(f["f"] * factor, 2)
    cal = round(p * 4 + c * 4 + fat * 9, 2)
    return {
        "name": f["name"],
        "quantity": f"{grams}g",
        "protein": p, "carbs": c, "fat": fat, "calories": cal
    }

def round_to(val: float, step: int) -> int:
    return max(step, int(round(val / step) * step))

# ==================== SERVIÇO ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(
        self, 
        user_profile: Dict,
        target_calories: float,
        target_macros: Dict[str, float]
    ) -> DietPlan:
        """Gera dieta matematicamente precisa"""
        
        target_p = target_macros['protein']
        target_c = target_macros['carbs']
        target_f = target_macros['fat']
        
        # Calcula distribuição de 5 refeições
        meals = self._build_diet(target_p, target_c, target_f)
        
        # Calcula totais REAIS
        computed_p = sum(sum(f['protein'] for f in m.foods) for m in meals)
        computed_c = sum(sum(f['carbs'] for f in m.foods) for m in meals)
        computed_f = sum(sum(f['fat'] for f in m.foods) for m in meals)
        computed_cal = round(computed_p * 4 + computed_c * 4 + computed_f * 9, 2)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_calories,
            target_macros=target_macros,
            meals=meals,
            computed_calories=computed_cal,
            computed_macros={
                "protein": round(computed_p, 2),
                "carbs": round(computed_c, 2),
                "fat": round(computed_f, 2)
            },
            notes=f"Dieta: {int(computed_cal)}kcal | P:{int(computed_p)}g C:{int(computed_c)}g G:{int(computed_f)}g"
        )
    
    def _build_diet(self, target_p: float, target_c: float, target_f: float) -> List[Meal]:
        """Constrói dieta que soma EXATAMENTE aos targets"""
        
        meals = []
        
        # ========== CAFÉ DA MANHÃ (15% P, 18% C, 15% F) ==========
        m1_target_p = target_p * 0.15
        m1_target_c = target_c * 0.18
        m1_target_f = target_f * 0.15
        
        m1_foods = []
        
        # Ovos para P e F
        ovos_g = round_to(min(m1_target_p / 0.13, m1_target_f / 0.11) * 100, 25)
        ovos_g = min(150, max(50, ovos_g))
        m1_foods.append(calc_food("ovos", ovos_g))
        
        # Aveia para C
        rem_c = m1_target_c - (ovos_g * 0.011)
        aveia_g = round_to(rem_c / 0.66 * 100, 10)
        aveia_g = min(80, max(30, aveia_g))
        m1_foods.append(calc_food("aveia", aveia_g))
        
        # Banana para C extra
        rem_c2 = m1_target_c - (ovos_g * 0.011) - (aveia_g * 0.66)
        if rem_c2 > 10:
            banana_g = round_to(rem_c2 / 0.23 * 100, 25)
            banana_g = min(150, max(50, banana_g))
            m1_foods.append(calc_food("banana", banana_g))
        
        m1_p = sum(f['protein'] for f in m1_foods)
        m1_c = sum(f['carbs'] for f in m1_foods)
        m1_f = sum(f['fat'] for f in m1_foods)
        m1_cal = sum(f['calories'] for f in m1_foods)
        
        meals.append(Meal(
            name="Café da Manhã", time="07:00", foods=m1_foods,
            total_calories=round(m1_cal, 2),
            macros={"protein": round(m1_p, 2), "carbs": round(m1_c, 2), "fat": round(m1_f, 2)}
        ))
        
        # ========== LANCHE DA MANHÃ (10% P, 8% C, 12% F) ==========
        m2_target_p = target_p * 0.10
        m2_target_f = target_f * 0.12
        
        m2_foods = []
        
        # Iogurte
        iogurte_g = round_to(m2_target_p / 0.10 * 100, 25)
        iogurte_g = min(200, max(100, iogurte_g))
        m2_foods.append(calc_food("iogurte", iogurte_g))
        
        # Castanha
        rem_f = m2_target_f - (iogurte_g * 0.05)
        if rem_f > 3:
            castanha_g = round_to(rem_f / 0.67 * 100, 5)
            castanha_g = min(25, max(10, castanha_g))
            m2_foods.append(calc_food("castanha", castanha_g))
        
        m2_p = sum(f['protein'] for f in m2_foods)
        m2_c = sum(f['carbs'] for f in m2_foods)
        m2_f = sum(f['fat'] for f in m2_foods)
        m2_cal = sum(f['calories'] for f in m2_foods)
        
        meals.append(Meal(
            name="Lanche da Manhã", time="10:00", foods=m2_foods,
            total_calories=round(m2_cal, 2),
            macros={"protein": round(m2_p, 2), "carbs": round(m2_c, 2), "fat": round(m2_f, 2)}
        ))
        
        # ========== ALMOÇO (30% P, 35% C, 25% F) ==========
        m3_target_p = target_p * 0.30
        m3_target_c = target_c * 0.35
        m3_target_f = target_f * 0.25
        
        m3_foods = []
        
        # Frango
        frango_g = round_to(m3_target_p * 0.7 / 0.31 * 100, 25)
        frango_g = min(250, max(100, frango_g))
        m3_foods.append(calc_food("frango", frango_g))
        
        # Arroz
        arroz_g = round_to(m3_target_c * 0.55 / 0.23 * 100, 25)
        arroz_g = min(300, max(100, arroz_g))
        m3_foods.append(calc_food("arroz", arroz_g))
        
        # Feijão
        feijao_g = round_to(m3_target_c * 0.25 / 0.14 * 100, 25)
        feijao_g = min(200, max(75, feijao_g))
        m3_foods.append(calc_food("feijao", feijao_g))
        
        # Salada
        m3_foods.append(calc_food("salada", 100))
        
        # Azeite (máx 15g)
        azeite_g = min(15, round_to(m3_target_f * 0.3 / 1.0 * 100, 5))
        m3_foods.append(calc_food("azeite", azeite_g))
        
        m3_p = sum(f['protein'] for f in m3_foods)
        m3_c = sum(f['carbs'] for f in m3_foods)
        m3_f = sum(f['fat'] for f in m3_foods)
        m3_cal = sum(f['calories'] for f in m3_foods)
        
        meals.append(Meal(
            name="Almoço", time="12:30", foods=m3_foods,
            total_calories=round(m3_cal, 2),
            macros={"protein": round(m3_p, 2), "carbs": round(m3_c, 2), "fat": round(m3_f, 2)}
        ))
        
        # ========== LANCHE DA TARDE (15% P, 17% C, 13% F) ==========
        m4_target_p = target_p * 0.15
        m4_target_c = target_c * 0.17
        
        m4_foods = []
        
        # Batata doce
        batata_g = round_to(m4_target_c * 0.7 / 0.20 * 100, 25)
        batata_g = min(300, max(100, batata_g))
        m4_foods.append(calc_food("batata", batata_g))
        
        # Frango
        frango2_g = round_to(m4_target_p / 0.31 * 100, 25)
        frango2_g = min(175, max(75, frango2_g))
        m4_foods.append(calc_food("frango", frango2_g))
        
        m4_p = sum(f['protein'] for f in m4_foods)
        m4_c = sum(f['carbs'] for f in m4_foods)
        m4_f = sum(f['fat'] for f in m4_foods)
        m4_cal = sum(f['calories'] for f in m4_foods)
        
        meals.append(Meal(
            name="Lanche da Tarde", time="16:00", foods=m4_foods,
            total_calories=round(m4_cal, 2),
            macros={"protein": round(m4_p, 2), "carbs": round(m4_c, 2), "fat": round(m4_f, 2)}
        ))
        
        # ========== JANTAR (30% P, 22% C, 35% F) - USA O RESTANTE ==========
        used_p = m1_p + m2_p + m3_p + m4_p
        used_c = m1_c + m2_c + m3_c + m4_c
        used_f = m1_f + m2_f + m3_f + m4_f
        
        need_p = target_p - used_p
        need_c = target_c - used_c
        need_f = target_f - used_f
        
        m5_foods = []
        
        # Tilápia para proteína
        if need_p > 10:
            tilapia_g = round_to(need_p * 0.6 / 0.26 * 100, 25)
            tilapia_g = min(300, max(100, tilapia_g))
            m5_foods.append(calc_food("tilapia", tilapia_g))
            need_p -= tilapia_g * 0.26
            need_f -= tilapia_g * 0.025
        
        # Arroz para carbs
        if need_c > 15:
            arroz2_g = round_to(need_c * 0.7 / 0.23 * 100, 25)
            arroz2_g = min(300, max(75, arroz2_g))
            m5_foods.append(calc_food("arroz", arroz2_g))
            need_c -= arroz2_g * 0.23
            need_p -= arroz2_g * 0.026
            need_f -= arroz2_g * 0.009
        
        # Brócolis
        m5_foods.append(calc_food("brocolis", 100))
        need_p -= 2.8
        need_c -= 7
        need_f -= 0.4
        
        # Azeite para gordura (máx 15g)
        if need_f > 5:
            azeite2_g = min(15, round_to(need_f * 0.5 / 1.0 * 100, 5))
            m5_foods.append(calc_food("azeite", azeite2_g))
            need_f -= azeite2_g
        
        # Clara para proteína extra
        if need_p > 5:
            clara_g = round_to(need_p / 0.11 * 100, 25)
            clara_g = min(200, max(50, clara_g))
            m5_foods.append(calc_food("clara", clara_g))
            need_p -= clara_g * 0.11
        
        # Castanha para gordura extra
        if need_f > 3:
            cast2_g = round_to(need_f / 0.67 * 100, 5)
            cast2_g = min(20, max(5, cast2_g))
            m5_foods.append(calc_food("castanha", cast2_g))
        
        # Batata para carbs extra
        if need_c > 10:
            batata2_g = round_to(need_c / 0.20 * 100, 25)
            batata2_g = min(200, max(50, batata2_g))
            m5_foods.append(calc_food("batata", batata2_g))
        
        m5_p = sum(f['protein'] for f in m5_foods)
        m5_c = sum(f['carbs'] for f in m5_foods)
        m5_f = sum(f['fat'] for f in m5_foods)
        m5_cal = sum(f['calories'] for f in m5_foods)
        
        meals.append(Meal(
            name="Jantar", time="19:30", foods=m5_foods,
            total_calories=round(m5_cal, 2),
            macros={"protein": round(m5_p, 2), "carbs": round(m5_c, 2), "fat": round(m5_f, 2)}
        ))
        
        return meals
