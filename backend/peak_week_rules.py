"""
🧾 REGRAS OFICIAIS DE PEAK WEEK - Sistema LAF Diet

Este módulo contém TODAS as regras oficiais para geração de dieta
durante a Peak Week de atletas de fisiculturismo.

OBJETIVOS:
✔️ Melhorar aparência no palco
✔️ Evitar erro clássico: atleta estufado, retido ou flat
✔️ Evitar protocolos perigosos (água zero, sódio zero, desidratação agressiva)

SEGURANÇA OBRIGATÓRIA:
💧 Água: NUNCA menos de 2L/dia
🧂 Sódio: NUNCA menos de 500mg/dia
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


# ==================== CONSTANTES DE SEGURANÇA ====================
# ESTAS REGRAS NUNCA PODEM SER QUEBRADAS

MINIMUM_WATER_LITERS = 2.0  # NUNCA abaixo de 2L/dia
MINIMUM_SODIUM_MG = 500     # NUNCA abaixo de 500mg/dia


# ==================== FASES DA PEAK WEEK ====================

class PeakWeekPhase(Enum):
    """Fases da Peak Week com suas características"""
    DEPLETION = "depletion"       # D-7 → D-4 (ou D-3 com pesagem)
    TRANSITION = "transition"      # D-3 → D-2 (sem pesagem) ou D-2 (com pesagem)
    WEIGH_IN_DAY = "weigh_in_day" # D-1 antes da pesagem (apenas com pesagem)
    CARB_UP = "carb_up"           # D-2 → D-1 (sem pesagem) ou D-1 pós-pesagem


# ==================== MACROS POR FASE (g/kg peso corporal) ====================

PEAK_WEEK_MACROS = {
    # 🟡 DEPLEÇÃO (D-7 → D-4 ou D-3)
    # Objetivo: Controle, depleção leve de glicogênio
    PeakWeekPhase.DEPLETION: {
        "protein": {"min": 2.2, "max": 2.6},      # Manter massa/estabilidade
        "carbs": {"min": 1.0, "max": 2.0},        # Leve depleção
        "fat": {"min": 0.4, "max": 0.6},          # Controlada, digestão leve
        "calories_per_kg": {"min": 22, "max": 28}, # Calorias alvo
        "description": "Controle / Depleção - Redução leve de retenção"
    },
    
    # 🟠 TRANSIÇÃO (D-3 → D-2 sem pesagem)
    # Objetivo: Começar a encher gradualmente sem retenção brusca
    PeakWeekPhase.TRANSITION: {
        "protein": {"min": 2.0, "max": 2.4},
        "carbs": {"min": 2.0, "max": 3.0},
        "fat": {"min": 0.3, "max": 0.5},
        "calories_per_kg": None,  # Calculado pelos macros
        "description": "Transição - Enchimento gradual sem retenção brusca"
    },
    
    # ⚖️ DIA DA PESAGEM - Antes da pesagem (D-1 manhã)
    # Objetivo: BATER O PESO - Nada de carga agressiva
    PeakWeekPhase.WEIGH_IN_DAY: {
        "protein": {"min": 2.2, "max": 2.2},
        "carbs": {"min": 1.0, "max": 2.0},        # SEM CARGA antes da pesagem
        "fat": {"min": 0.3, "max": 0.5},
        "calories_per_kg": None,
        "description": "Dia da Pesagem - Controle para bater o peso"
    },
    
    # 🔴 CARB-UP (D-2 → D-1 sem pesagem, ou D-1 pós-pesagem)
    # Objetivo: Pump visual - encher músculos com glicogênio
    PeakWeekPhase.CARB_UP: {
        "protein": {"min": 2.0, "max": 2.2},
        "carbs": {"min": 4.0, "max": 7.0},        # CARGA MÁXIMA
        "fat": {"min": 0.2, "max": 0.4},          # Baixa para não atrasar digestão
        "calories_per_kg": None,
        "description": "Carb-Up - Pump visual, enchimento muscular"
    },
}


# ==================== ALIMENTOS PEAK WEEK ====================

# 🚫 ALIMENTOS PROIBIDOS durante TODA Peak Week
# Motivo: fibras + fermentação = risco de distensão abdominal
PEAK_WEEK_BLOCKED_FOODS = {
    # Leguminosas (alta fermentação)
    "feijao",
    "lentilha",
    "grao_de_bico",
    "ervilha",
    
    # Cereais com fibras
    "aveia",
    "granola",
    "pao_integral",
    "macarrao_integral",
    
    # Vegetais crucíferos (alta fermentação)
    "brocolis",
    "couve_flor",
    "couve",
    "repolho",
    
    # Vegetais com alta fibra
    "cenoura",
    "beterraba",
    
    # Outros
    "cuscuz",
    "farofa",
}

# ✅ ALIMENTOS PRIORITÁRIOS para Peak Week
# Motivo: digestão leve, previsíveis, sem fermentação
PEAK_WEEK_PRIORITY_FOODS = {
    # CARBOIDRATOS LIMPOS (digestão fácil)
    "carbs": {
        "arroz_branco",     # Primeiro da lista - melhor opção
        "batata_doce",
        "batata",           # Batata inglesa
        "tapioca",          # Permitida na Peak Week
    },
    
    # PROTEÍNAS LIMPAS
    "protein": {
        "frango",           # Peito de frango - melhor opção
        "tilapia",          # Peixe magro, digestão fácil
        "claras",           # Claras de ovo - ultra clean
        "atum",             # Em água
    },
    
    # VEGETAIS LEVES (baixa fermentação)
    "vegetables": {
        "pepino",           # Ultra leve, alto em água
        "alface",           # Folha leve
        "rucola",           # Folha leve
        "espinafre",        # Folha leve (cozido)
        "tomate",           # Leve
        "vagem",            # Baixa fermentação
        "abobrinha",        # Leve, fácil digestão
    },
    
    # GORDURAS (pequenas quantidades)
    "fat": {
        "azeite",           # Pequenas quantidades apenas
    },
}


# ==================== ÁGUA E SÓDIO POR DIA ====================

def get_water_sodium_protocol(
    days_to_competition: int,
    has_weigh_in: bool = False,
    weigh_in_time: str = None  # "morning" ou "afternoon"
) -> Dict:
    """
    Retorna protocolo de água e sódio para o dia específico.
    
    REGRAS DE SEGURANÇA:
    - Água NUNCA abaixo de 2L
    - Sódio NUNCA abaixo de 500mg
    
    Args:
        days_to_competition: Dias até a competição (7=D-7, 1=D-1, 0=Dia D)
        has_weigh_in: Se há pesagem no dia anterior
        weigh_in_time: Horário da pesagem ("morning" ou "afternoon")
    
    Returns:
        Dict com water_liters, sodium_mg, e notas
    """
    
    # Protocolo padrão (sem pesagem)
    standard_protocol = {
        7: {"water": 5.0, "sodium": 2000, "phase": "depletion"},
        6: {"water": 4.5, "sodium": 1800, "phase": "depletion"},
        5: {"water": 4.0, "sodium": 1600, "phase": "depletion"},
        4: {"water": 4.0, "sodium": 1400, "phase": "depletion"},
        3: {"water": 3.5, "sodium": 1200, "phase": "transition"},
        2: {"water": 3.0, "sodium": 1000, "phase": "transition"},
        1: {"water": 2.5, "sodium": 800, "phase": "carb_up"},
        0: {"water": 2.0, "sodium": 500, "phase": "competition"},  # Dia D
    }
    
    # Protocolo COM pesagem (mais conservador)
    weigh_in_protocol = {
        7: {"water": 4.5, "sodium": 2000, "phase": "depletion"},
        6: {"water": 4.5, "sodium": 1800, "phase": "depletion"},
        5: {"water": 4.0, "sodium": 1600, "phase": "depletion"},
        4: {"water": 4.0, "sodium": 1400, "phase": "depletion"},
        3: {"water": 3.5, "sodium": 1200, "phase": "depletion"},
        2: {"water": 3.0, "sodium": 1000, "phase": "weigh_in_prep"},  # Controle
        1: {"water": 2.5, "sodium": 800, "phase": "weigh_in_day"},   # Pesagem + Carb
        0: {"water": 2.0, "sodium": 500, "phase": "competition"},
    }
    
    protocol = weigh_in_protocol if has_weigh_in else standard_protocol
    
    day_data = protocol.get(days_to_competition, protocol[0])
    
    # GARANTIA DE SEGURANÇA - NUNCA QUEBRAR
    water = max(day_data["water"], MINIMUM_WATER_LITERS)
    sodium = max(day_data["sodium"], MINIMUM_SODIUM_MG)
    
    return {
        "water_liters": water,
        "water_ml": int(water * 1000),
        "sodium_mg": sodium,
        "phase": day_data["phase"],
        "days_to_competition": days_to_competition,
        "has_weigh_in": has_weigh_in,
        "safety_note": f"Mínimos de segurança: {MINIMUM_WATER_LITERS}L água | {MINIMUM_SODIUM_MG}mg sódio"
    }


# ==================== CÁLCULO DE MACROS PEAK WEEK ====================

def calculate_peak_week_macros(
    weight_kg: float,
    days_to_competition: int,
    has_weigh_in: bool = False,
    is_post_weigh_in: bool = False
) -> Dict:
    """
    Calcula macros para Peak Week baseado no peso e dia.
    
    Args:
        weight_kg: Peso do atleta em kg
        days_to_competition: Dias até a competição
        has_weigh_in: Se há pesagem no dia anterior
        is_post_weigh_in: Se já passou a pesagem (para D-1)
    
    Returns:
        Dict com protein, carbs, fat, calories e notas
    """
    
    # Determina a fase
    if has_weigh_in:
        # COM PESAGEM
        if days_to_competition >= 3:
            phase = PeakWeekPhase.DEPLETION
        elif days_to_competition == 2:
            phase = PeakWeekPhase.WEIGH_IN_DAY  # Controle para pesagem
        elif days_to_competition == 1:
            if is_post_weigh_in:
                phase = PeakWeekPhase.CARB_UP  # Após pesagem = CARGA
            else:
                phase = PeakWeekPhase.WEIGH_IN_DAY  # Antes pesagem = controle
        else:
            phase = PeakWeekPhase.CARB_UP
    else:
        # SEM PESAGEM (padrão)
        if days_to_competition >= 4:
            phase = PeakWeekPhase.DEPLETION
        elif days_to_competition >= 2:
            phase = PeakWeekPhase.TRANSITION
        else:
            phase = PeakWeekPhase.CARB_UP
    
    # Pega os ranges de macros para a fase
    macro_ranges = PEAK_WEEK_MACROS[phase]
    
    # Calcula usando o valor médio dos ranges
    protein_per_kg = (macro_ranges["protein"]["min"] + macro_ranges["protein"]["max"]) / 2
    carbs_per_kg = (macro_ranges["carbs"]["min"] + macro_ranges["carbs"]["max"]) / 2
    fat_per_kg = (macro_ranges["fat"]["min"] + macro_ranges["fat"]["max"]) / 2
    
    # Calcula gramas totais
    protein_g = round(protein_per_kg * weight_kg)
    carbs_g = round(carbs_per_kg * weight_kg)
    fat_g = round(fat_per_kg * weight_kg)
    
    # Calcula calorias
    calories = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
    
    # Se tem range de calorias, verifica
    if macro_ranges.get("calories_per_kg"):
        cal_range = macro_ranges["calories_per_kg"]
        target_cal = ((cal_range["min"] + cal_range["max"]) / 2) * weight_kg
        # Ajusta se necessário
        if calories < target_cal * 0.9:
            # Aumenta carbs para atingir calorias
            deficit = target_cal - calories
            extra_carbs = round(deficit / 4)
            carbs_g += extra_carbs
            calories = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
    
    return {
        "phase": phase.value,
        "phase_name": get_phase_display_name(phase),
        "phase_description": macro_ranges["description"],
        "weight_kg": weight_kg,
        "days_to_competition": days_to_competition,
        "has_weigh_in": has_weigh_in,
        "is_post_weigh_in": is_post_weigh_in,
        
        # Macros por kg
        "protein_per_kg": protein_per_kg,
        "carbs_per_kg": carbs_per_kg,
        "fat_per_kg": fat_per_kg,
        
        # Macros totais
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "calories": calories,
        
        # Ranges permitidos
        "ranges": {
            "protein": macro_ranges["protein"],
            "carbs": macro_ranges["carbs"],
            "fat": macro_ranges["fat"],
        }
    }


def get_phase_display_name(phase: PeakWeekPhase) -> str:
    """Retorna nome de exibição da fase"""
    names = {
        PeakWeekPhase.DEPLETION: "🟡 CONTROLE / DEPLEÇÃO",
        PeakWeekPhase.TRANSITION: "🟠 TRANSIÇÃO",
        PeakWeekPhase.WEIGH_IN_DAY: "⚖️ DIA DA PESAGEM",
        PeakWeekPhase.CARB_UP: "🔴 CARB-UP",
    }
    return names.get(phase, phase.value.upper())


# ==================== GERAÇÃO DE DIETA PEAK WEEK ====================

def generate_peak_week_diet(
    weight_kg: float,
    days_to_competition: int,
    meal_count: int = 6,
    has_weigh_in: bool = False,
    is_post_weigh_in: bool = False,
    preferred_foods: List[str] = None
) -> Dict:
    """
    Gera dieta completa para um dia da Peak Week.
    
    REGRAS OBRIGATÓRIAS:
    1. Usar APENAS alimentos permitidos (PEAK_WEEK_PRIORITY_FOODS)
    2. NUNCA usar alimentos bloqueados (PEAK_WEEK_BLOCKED_FOODS)
    3. Macros calculados por kg de peso corporal
    4. Água e sódio dentro dos limites seguros
    
    Args:
        weight_kg: Peso do atleta
        days_to_competition: Dias até competição
        meal_count: Número de refeições (4-6)
        has_weigh_in: Se há pesagem
        is_post_weigh_in: Se já passou pesagem
        preferred_foods: Alimentos preferidos do atleta
    
    Returns:
        Dict com dieta completa do dia
    """
    
    # Calcula macros do dia
    macros = calculate_peak_week_macros(
        weight_kg, days_to_competition, has_weigh_in, is_post_weigh_in
    )
    
    # Pega protocolo de água/sódio
    water_sodium = get_water_sodium_protocol(days_to_competition, has_weigh_in)
    
    # Filtra alimentos preferidos (remove bloqueados)
    allowed_preferred = []
    if preferred_foods:
        for food in preferred_foods:
            if food not in PEAK_WEEK_BLOCKED_FOODS:
                allowed_preferred.append(food)
    
    # Seleciona alimentos prioritários
    selected_foods = select_peak_week_foods(macros, allowed_preferred)
    
    # Distribui em refeições
    meals = distribute_peak_week_meals(
        macros, selected_foods, meal_count, days_to_competition
    )
    
    # Monta resposta
    return {
        "day": f"D-{days_to_competition}" if days_to_competition > 0 else "DIA D",
        "phase": macros["phase"],
        "phase_name": macros["phase_name"],
        "phase_description": macros["phase_description"],
        
        "target_macros": {
            "protein": macros["protein_g"],
            "carbs": macros["carbs_g"],
            "fat": macros["fat_g"],
            "calories": macros["calories"],
        },
        
        "water_sodium": water_sodium,
        
        "meals": meals,
        
        "blocked_foods": list(PEAK_WEEK_BLOCKED_FOODS),
        "priority_foods": {
            "carbs": list(PEAK_WEEK_PRIORITY_FOODS["carbs"]),
            "protein": list(PEAK_WEEK_PRIORITY_FOODS["protein"]),
            "vegetables": list(PEAK_WEEK_PRIORITY_FOODS["vegetables"]),
        },
        
        "safety_warnings": [
            f"💧 Água mínima: {MINIMUM_WATER_LITERS}L/dia",
            f"🧂 Sódio mínimo: {MINIMUM_SODIUM_MG}mg/dia",
            "🚫 NUNCA usar água zero ou sódio zero",
            "⚠️ Se sentir mal-estar, aumente água e sódio",
        ],
        
        "has_weigh_in": has_weigh_in,
        "is_post_weigh_in": is_post_weigh_in,
    }


def select_peak_week_foods(macros: Dict, preferred: List[str] = None) -> Dict:
    """
    Seleciona alimentos para Peak Week.
    Prioriza: preferidos do atleta > alimentos prioritários da lista
    """
    from diet_service import FOODS
    
    selected = {
        "protein": [],
        "carbs": [],
        "vegetables": [],
        "fat": [],
    }
    
    # Proteínas
    protein_priority = list(PEAK_WEEK_PRIORITY_FOODS["protein"])
    if preferred:
        for p in preferred:
            if p in FOODS and FOODS[p]["category"] == "protein" and p not in PEAK_WEEK_BLOCKED_FOODS:
                if p not in protein_priority:
                    protein_priority.insert(0, p)
    selected["protein"] = protein_priority[:3]  # Top 3
    
    # Carboidratos
    carb_priority = list(PEAK_WEEK_PRIORITY_FOODS["carbs"])
    if preferred:
        for p in preferred:
            if p in FOODS and FOODS[p]["category"] == "carb" and p not in PEAK_WEEK_BLOCKED_FOODS:
                if p not in carb_priority:
                    carb_priority.insert(0, p)
    selected["carbs"] = carb_priority[:3]
    
    # Vegetais
    selected["vegetables"] = list(PEAK_WEEK_PRIORITY_FOODS["vegetables"])[:4]
    
    # Gordura
    selected["fat"] = list(PEAK_WEEK_PRIORITY_FOODS["fat"])
    
    return selected


def distribute_peak_week_meals(
    macros: Dict, 
    foods: Dict, 
    meal_count: int,
    days_to_competition: int
) -> List[Dict]:
    """
    Distribui macros em refeições para Peak Week.
    """
    from diet_service import FOODS, calc_food
    
    meals = []
    
    # Define estrutura de refeições
    if meal_count == 6:
        meal_structure = [
            {"name": "Café da Manhã", "time": "07:00", "p": 0.15, "c": 0.20, "f": 0.20},
            {"name": "Lanche 1", "time": "10:00", "p": 0.10, "c": 0.10, "f": 0.10},
            {"name": "Almoço", "time": "12:30", "p": 0.25, "c": 0.30, "f": 0.25},
            {"name": "Lanche 2", "time": "15:30", "p": 0.10, "c": 0.10, "f": 0.10},
            {"name": "Jantar", "time": "19:00", "p": 0.25, "c": 0.20, "f": 0.25},
            {"name": "Ceia", "time": "21:30", "p": 0.15, "c": 0.10, "f": 0.10},
        ]
    elif meal_count == 5:
        meal_structure = [
            {"name": "Café da Manhã", "time": "07:00", "p": 0.15, "c": 0.20, "f": 0.20},
            {"name": "Lanche", "time": "10:00", "p": 0.15, "c": 0.15, "f": 0.15},
            {"name": "Almoço", "time": "12:30", "p": 0.25, "c": 0.30, "f": 0.25},
            {"name": "Jantar", "time": "18:30", "p": 0.30, "c": 0.25, "f": 0.25},
            {"name": "Ceia", "time": "21:00", "p": 0.15, "c": 0.10, "f": 0.15},
        ]
    else:  # 4 refeições
        meal_structure = [
            {"name": "Café da Manhã", "time": "07:00", "p": 0.20, "c": 0.25, "f": 0.25},
            {"name": "Almoço", "time": "12:00", "p": 0.30, "c": 0.35, "f": 0.30},
            {"name": "Jantar", "time": "18:00", "p": 0.30, "c": 0.30, "f": 0.30},
            {"name": "Ceia", "time": "21:00", "p": 0.20, "c": 0.10, "f": 0.15},
        ]
    
    total_p = macros["protein_g"]
    total_c = macros["carbs_g"]
    total_f = macros["fat_g"]
    
    for meal_info in meal_structure:
        meal_p = round(total_p * meal_info["p"])
        meal_c = round(total_c * meal_info["c"])
        meal_f = round(total_f * meal_info["f"])
        
        meal_foods = []
        
        # Adiciona proteína
        if foods["protein"] and meal_p > 10:
            protein_food = foods["protein"][0]
            if protein_food in FOODS:
                protein_per_100 = FOODS[protein_food]["p"]
                grams = min(round((meal_p / protein_per_100) * 100), 250)
                meal_foods.append(calc_food(protein_food, grams))
        
        # Adiciona carboidrato (principal e lanches)
        if foods["carbs"] and meal_c > 20:
            carb_food = foods["carbs"][0]  # Arroz branco prioritário
            if carb_food in FOODS:
                carb_per_100 = FOODS[carb_food]["c"]
                grams = min(round((meal_c / carb_per_100) * 100), 300)
                meal_foods.append(calc_food(carb_food, grams))
        
        # Adiciona vegetal (almoço e jantar)
        if "Almoço" in meal_info["name"] or "Jantar" in meal_info["name"]:
            if foods["vegetables"]:
                veg_food = foods["vegetables"][0]
                if veg_food in FOODS:
                    meal_foods.append(calc_food(veg_food, 100))
        
        # Adiciona gordura (se necessário)
        if foods["fat"] and meal_f > 5:
            fat_food = foods["fat"][0]
            if fat_food in FOODS:
                fat_per_100 = FOODS[fat_food]["f"]
                grams = min(round((meal_f / fat_per_100) * 100), 15)
                meal_foods.append(calc_food(fat_food, grams))
        
        # Calcula totais da refeição
        meal_calories = sum(f.get("calories", 0) for f in meal_foods)
        meal_protein = sum(f.get("protein", 0) for f in meal_foods)
        meal_carbs = sum(f.get("carbs", 0) for f in meal_foods)
        meal_fat = sum(f.get("fat", 0) for f in meal_foods)
        
        meals.append({
            "name": meal_info["name"],
            "time": meal_info["time"],
            "foods": meal_foods,
            "totals": {
                "calories": meal_calories,
                "protein": meal_protein,
                "carbs": meal_carbs,
                "fat": meal_fat,
            },
            "target": {
                "protein": meal_p,
                "carbs": meal_c,
                "fat": meal_f,
            }
        })
    
    return meals


# ==================== VALIDAÇÃO DE SEGURANÇA ====================

def validate_peak_week_safety(diet: Dict) -> Tuple[bool, List[str]]:
    """
    Valida se a dieta Peak Week está dentro dos limites de segurança.
    
    Returns:
        (is_safe, list of warnings/errors)
    """
    warnings = []
    is_safe = True
    
    water_sodium = diet.get("water_sodium", {})
    
    # Verifica água
    water = water_sodium.get("water_liters", 0)
    if water < MINIMUM_WATER_LITERS:
        warnings.append(f"⛔ PERIGO: Água ({water}L) abaixo do mínimo seguro ({MINIMUM_WATER_LITERS}L)")
        is_safe = False
    
    # Verifica sódio
    sodium = water_sodium.get("sodium_mg", 0)
    if sodium < MINIMUM_SODIUM_MG:
        warnings.append(f"⛔ PERIGO: Sódio ({sodium}mg) abaixo do mínimo seguro ({MINIMUM_SODIUM_MG}mg)")
        is_safe = False
    
    # Verifica alimentos bloqueados
    meals = diet.get("meals", [])
    for meal in meals:
        for food in meal.get("foods", []):
            food_key = food.get("key", "")
            if food_key in PEAK_WEEK_BLOCKED_FOODS:
                warnings.append(f"⚠️ Alimento bloqueado encontrado: {food.get('name', food_key)}")
    
    # Verifica carb-up antes da pesagem
    if diet.get("has_weigh_in") and not diet.get("is_post_weigh_in"):
        macros = diet.get("target_macros", {})
        carbs = macros.get("carbs", 0)
        weight = diet.get("weight_kg", 80)
        carbs_per_kg = carbs / weight if weight > 0 else 0
        
        if carbs_per_kg > 3.0:
            warnings.append("⚠️ Carb-up detectado ANTES da pesagem - Risco de não bater peso!")
    
    return is_safe, warnings


# ==================== PROTOCOLO COMPLETO DE 7 DIAS ====================

def generate_full_peak_week_protocol(
    weight_kg: float,
    competition_date: datetime,
    has_weigh_in: bool = False,
    meal_count: int = 6,
    preferred_foods: List[str] = None
) -> Dict:
    """
    Gera protocolo completo de 7 dias de Peak Week.
    
    Args:
        weight_kg: Peso do atleta
        competition_date: Data da competição
        has_weigh_in: Se há pesagem 24h antes
        meal_count: Número de refeições por dia
        preferred_foods: Alimentos preferidos
    
    Returns:
        Dict com protocolo completo de 7 dias
    """
    
    now = datetime.utcnow()
    days_to_comp = (competition_date - now).days
    
    protocol = {
        "athlete_weight_kg": weight_kg,
        "competition_date": competition_date.isoformat(),
        "has_weigh_in": has_weigh_in,
        "generated_at": now.isoformat(),
        "days": [],
        "safety_rules": {
            "minimum_water_liters": MINIMUM_WATER_LITERS,
            "minimum_sodium_mg": MINIMUM_SODIUM_MG,
            "blocked_foods": list(PEAK_WEEK_BLOCKED_FOODS),
        },
        "warnings": [],
    }
    
    # Gera cada dia
    for day_offset in range(min(7, days_to_comp + 1)):
        days_remaining = days_to_comp - day_offset
        
        if days_remaining < 0:
            continue
        
        # Para D-1 com pesagem, gera duas versões
        if has_weigh_in and days_remaining == 1:
            # Antes da pesagem
            day_diet_pre = generate_peak_week_diet(
                weight_kg, days_remaining, meal_count, 
                has_weigh_in, is_post_weigh_in=False, 
                preferred_foods=preferred_foods
            )
            day_diet_pre["period"] = "Antes da Pesagem"
            
            # Após a pesagem
            day_diet_post = generate_peak_week_diet(
                weight_kg, days_remaining, meal_count,
                has_weigh_in, is_post_weigh_in=True,
                preferred_foods=preferred_foods
            )
            day_diet_post["period"] = "Após a Pesagem (CARB-UP)"
            
            protocol["days"].append({
                "day_number": 7 - days_remaining,
                "days_to_competition": days_remaining,
                "date": (now + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
                "has_split": True,
                "pre_weigh_in": day_diet_pre,
                "post_weigh_in": day_diet_post,
            })
        else:
            day_diet = generate_peak_week_diet(
                weight_kg, days_remaining, meal_count,
                has_weigh_in, is_post_weigh_in=False,
                preferred_foods=preferred_foods
            )
            
            protocol["days"].append({
                "day_number": 7 - days_remaining,
                "days_to_competition": days_remaining,
                "date": (now + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
                "has_split": False,
                "diet": day_diet,
            })
    
    # Validação geral
    all_safe = True
    for day in protocol["days"]:
        if day.get("has_split"):
            _, warnings = validate_peak_week_safety(day["pre_weigh_in"])
            protocol["warnings"].extend(warnings)
            _, warnings = validate_peak_week_safety(day["post_weigh_in"])
            protocol["warnings"].extend(warnings)
        else:
            _, warnings = validate_peak_week_safety(day["diet"])
            protocol["warnings"].extend(warnings)
    
    return protocol
