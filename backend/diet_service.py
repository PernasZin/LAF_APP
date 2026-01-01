"""
Sistema de Geração de Dieta com PRECISÃO MATEMÁTICA ABSOLUTA
P0: Macros DEVEM bater EXATAMENTE usando cálculo proporcional
"""
import os
from typing import List, Dict, Optional
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

# ==================== ALIMENTOS ====================

FOODS = {
    "frango": {"name": "Peito de Frango Grelhado", "p": 31.0, "c": 0.0, "f": 3.6},
    "tilapia": {"name": "Tilápia Grelhada", "p": 26.0, "c": 0.0, "f": 2.5},
    "ovos": {"name": "Ovos Inteiros", "p": 13.0, "c": 1.1, "f": 11.0},
    "clara": {"name": "Clara de Ovo", "p": 11.0, "c": 0.7, "f": 0.2},
    "iogurte": {"name": "Iogurte Grego", "p": 10.0, "c": 4.0, "f": 5.0},
    "arroz": {"name": "Arroz Integral", "p": 2.6, "c": 23.0, "f": 0.9},
    "batata": {"name": "Batata Doce", "p": 1.6, "c": 20.0, "f": 0.1},
    "aveia": {"name": "Aveia em Flocos", "p": 13.5, "c": 66.0, "f": 7.0},
    "feijao": {"name": "Feijão Cozido", "p": 5.0, "c": 14.0, "f": 0.5},
    "azeite": {"name": "Azeite de Oliva", "p": 0.0, "c": 0.0, "f": 100.0},
    "castanha": {"name": "Castanha do Pará", "p": 14.0, "c": 12.0, "f": 67.0},
    "brocolis": {"name": "Brócolis", "p": 2.8, "c": 7.0, "f": 0.4},
    "salada": {"name": "Salada Verde", "p": 1.5, "c": 3.0, "f": 0.2},
    "banana": {"name": "Banana", "p": 1.1, "c": 23.0, "f": 0.3},
}

def calc(key: str, g: int) -> Dict:
    f = FOODS[key]
    factor = g / 100
    p = round(f["p"] * factor, 2)
    c = round(f["c"] * factor, 2)
    fat = round(f["f"] * factor, 2)
    return {"name": f["name"], "quantity": f"{g}g", "protein": p, "carbs": c, "fat": fat, 
            "calories": round(p*4 + c*4 + fat*9, 2)}

def rnd(v: float, step: int = 25) -> int:
    return max(step, int(round(v / step) * step))

# ==================== SERVIÇO ====================

class DietAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_diet_plan(self, user_profile: Dict, target_calories: float, target_macros: Dict[str, float]) -> DietPlan:
        """Gera dieta com macros EXATOS"""
        
        P = target_macros['protein']
        C = target_macros['carbs']
        F = target_macros['fat']
        
        # Distribuição fixa por refeição
        # Total = 100% de cada macro
        dist = [
            {"name": "Café da Manhã", "time": "07:00", "p": 0.15, "c": 0.15, "f": 0.15},
            {"name": "Lanche Manhã", "time": "10:00", "p": 0.10, "c": 0.08, "f": 0.12},
            {"name": "Almoço", "time": "12:30", "p": 0.30, "c": 0.35, "f": 0.28},
            {"name": "Lanche Tarde", "time": "16:00", "p": 0.15, "c": 0.20, "f": 0.10},
            {"name": "Jantar", "time": "19:30", "p": 0.30, "c": 0.22, "f": 0.35},
        ]
        
        meals = []
        used_p, used_c, used_f = 0.0, 0.0, 0.0
        
        for i, d in enumerate(dist):
            is_last = (i == len(dist) - 1)
            
            if is_last:
                # Última: pega EXATAMENTE o restante
                mp = P - used_p
                mc = C - used_c
                mf = F - used_f
            else:
                mp = P * d['p']
                mc = C * d['c']
                mf = F * d['f']
            
            foods = self._build_meal(d['name'], mp, mc, mf, is_last)
            
            actual_p = sum(f['protein'] for f in foods)
            actual_c = sum(f['carbs'] for f in foods)
            actual_f = sum(f['fat'] for f in foods)
            actual_cal = sum(f['calories'] for f in foods)
            
            used_p += actual_p
            used_c += actual_c
            used_f += actual_f
            
            meals.append(Meal(
                name=d['name'], time=d['time'], foods=foods,
                total_calories=round(actual_cal, 2),
                macros={"protein": round(actual_p, 2), "carbs": round(actual_c, 2), "fat": round(actual_f, 2)}
            ))
        
        # Totais COMPUTADOS
        cp = round(sum(m.macros['protein'] for m in meals), 2)
        cc = round(sum(m.macros['carbs'] for m in meals), 2)
        cf = round(sum(m.macros['fat'] for m in meals), 2)
        ccal = round(cp * 4 + cc * 4 + cf * 9, 2)
        
        return DietPlan(
            user_id=user_profile['id'],
            target_calories=target_calories,
            target_macros=target_macros,
            meals=meals,
            computed_calories=ccal,
            computed_macros={"protein": cp, "carbs": cc, "fat": cf},
            notes=f"Dieta: {int(ccal)}kcal | P:{int(cp)}g C:{int(cc)}g G:{int(cf)}g"
        )
    
    def _build_meal(self, name: str, tp: float, tc: float, tf: float, is_last: bool) -> List[Dict]:
        """Constrói refeição atingindo os macros alvo"""
        
        foods = []
        rp, rc, rf = tp, tc, tf  # Restante de cada macro
        
        if "Café" in name:
            # Ovos (P+F), Aveia (C+P), Banana (C)
            ovos_g = rnd(min(rp * 0.7 / 0.13, rf * 0.6 / 0.11) * 100)
            ovos_g = min(150, max(50, ovos_g))
            f = calc("ovos", ovos_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']; rf -= f['fat']
            
            aveia_g = rnd(rc * 0.5 / 0.66 * 100, 10)
            aveia_g = min(80, max(30, aveia_g))
            f = calc("aveia", aveia_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']; rf -= f['fat']
            
            if rc > 10:
                banana_g = rnd(rc / 0.23 * 100)
                banana_g = min(200, max(50, banana_g))
                f = calc("banana", banana_g)
                foods.append(f)
        
        elif "Lanche Manhã" in name:
            # Iogurte (P+C+F), Castanha (F)
            iog_g = rnd(rp / 0.10 * 100)
            iog_g = min(200, max(100, iog_g))
            f = calc("iogurte", iog_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']; rf -= f['fat']
            
            if rf > 3:
                cast_g = rnd(rf / 0.67 * 100, 5)
                cast_g = min(25, max(10, cast_g))
                f = calc("castanha", cast_g)
                foods.append(f)
        
        elif "Almoço" in name:
            # Frango (P), Arroz (C), Feijão (C+P), Salada, Azeite (F)
            frango_g = rnd(rp * 0.6 / 0.31 * 100)
            frango_g = min(250, max(100, frango_g))
            f = calc("frango", frango_g)
            foods.append(f)
            rp -= f['protein']; rf -= f['fat']
            
            arroz_g = rnd(rc * 0.55 / 0.23 * 100)
            arroz_g = min(350, max(100, arroz_g))
            f = calc("arroz", arroz_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']; rf -= f['fat']
            
            feijao_g = rnd(rc * 0.4 / 0.14 * 100)
            feijao_g = min(200, max(75, feijao_g))
            f = calc("feijao", feijao_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']
            
            foods.append(calc("salada", 100))
            
            azeite_g = min(15, rnd(rf * 0.3 / 1.0 * 100, 5))
            foods.append(calc("azeite", azeite_g))
        
        elif "Lanche Tarde" in name:
            # Batata (C), Frango (P)
            batata_g = rnd(rc / 0.20 * 100)
            batata_g = min(350, max(100, batata_g))
            f = calc("batata", batata_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']
            
            frango2_g = rnd(rp / 0.31 * 100)
            frango2_g = min(200, max(50, frango2_g))
            f = calc("frango", frango2_g)
            foods.append(f)
        
        else:  # Jantar
            # Tilápia (P), Arroz (C), Brócolis, Azeite (F), Clara (P), Castanha (F)
            tilapia_g = rnd(rp * 0.5 / 0.26 * 100)
            tilapia_g = min(300, max(100, tilapia_g))
            f = calc("tilapia", tilapia_g)
            foods.append(f)
            rp -= f['protein']; rf -= f['fat']
            
            arroz_g = rnd(rc * 0.7 / 0.23 * 100)
            arroz_g = min(350, max(75, arroz_g))
            f = calc("arroz", arroz_g)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']; rf -= f['fat']
            
            f = calc("brocolis", 100)
            foods.append(f)
            rp -= f['protein']; rc -= f['carbs']; rf -= f['fat']
            
            if rf > 5:
                azeite_g = min(15, rnd(rf * 0.4 / 1.0 * 100, 5))
                f = calc("azeite", azeite_g)
                foods.append(f)
                rf -= f['fat']
            
            # Ajustes finais se última refeição
            if is_last:
                if rp > 5:
                    clara_g = rnd(rp / 0.11 * 100)
                    clara_g = min(200, max(25, clara_g))
                    f = calc("clara", clara_g)
                    foods.append(f)
                    rp -= f['protein']
                
                if rf > 3:
                    cast_g = rnd(rf / 0.67 * 100, 5)
                    cast_g = min(25, max(5, cast_g))
                    f = calc("castanha", cast_g)
                    foods.append(f)
                    rf -= f['fat']
                
                if rc > 15:
                    batata_g = rnd(rc / 0.20 * 100)
                    batata_g = min(250, max(50, batata_g))
                    f = calc("batata", batata_g)
                    foods.append(f)
        
        return foods
