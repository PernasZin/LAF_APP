"""
Workout Module - Training Level Configurations
===============================================
Configuration settings for each training level
"""

from typing import Dict, Any


def get_config_for_level(level: str, duration: int, completed_workouts: int = 0) -> Dict[str, Any]:
    """
    Retorna a configuração de treino baseada no nível e tempo disponível
    
    Níveis:
    - novato: Nunca treinou (treinos simples, máquinas, menor volume)
    - iniciante: 6 meses - 2 anos (volume moderado)
    - intermediario: 2-3 anos (maior volume, técnicas)
    - avancado: 3+ anos (volume alto, técnicas avançadas)
    """
    # Séries baseadas no tempo disponível
    sets_by_time = get_sets_per_duration(duration, level)
    
    # NOVATO: Treino de adaptação nas primeiras 30 sessões
    is_adaptation = level == 'novato' and completed_workouts < 30
    
    if is_adaptation:
        # Treino de adaptação para novatos (4-8 semanas)
        return {
            "sets": min(sets_by_time, 2),
            "reps": "15-20",
            "rest": "60s",
            "ex_per_muscle": 1,
            "machine_only": True,
            "notes_prefix": "⚠️ ADAPTAÇÃO - CARGA LEVE! ",
            "general_note": "FASE DE ADAPTAÇÃO: Técnica acima de carga."
        }
    elif level == 'novato':
        return {
            "sets": min(sets_by_time, 3),
            "reps": "12-15",
            "rest": "90s",
            "ex_per_muscle": 1,
            "machine_only": True,
            "notes_prefix": "",
            "general_note": "Foco 100% na execução correta. Evite cargas pesadas."
        }
    elif level == 'iniciante':
        return {
            "sets": sets_by_time,
            "reps": "10-12",
            "rest": "75s",
            "ex_per_muscle": 2,
            "machine_only": False,
            "allow_free_weights": ["elevacao_lateral", "rosca_alternada", "triceps_frances"],
            "block_exercises": ["supino_barra", "agachamento_livre", "stiff_livre"],
            "notes_prefix": "",
            "general_note": "Progressão simples. Aumente cargas gradualmente."
        }
    elif level == 'intermediario':
        return {
            "sets": sets_by_time,
            "reps": "8-12",
            "rest": "75s",
            "ex_per_muscle": 2,
            "machine_only": False,
            "allow_free_weights": True,
            "block_exercises": [],
            "notes_prefix": "💪 Chegue PERTO DA FALHA em pelo menos 1 série. ",
            "general_note": "Controle de descanso. Pode usar técnicas como bi-set e pirâmide."
        }
    else:  # avancado
        return {
            "sets": sets_by_time,
            "reps": "5-8",
            "rest": "120s",
            "ex_per_muscle": 2,
            "machine_only": False,
            "allow_free_weights": True,
            "block_exercises": [],
            "notes_prefix": "🔥 ATÉ A FALHA! ",
            "general_note": "AVANÇADO: Pode usar drop set, rest pause. Controle técnico máximo."
        }


def get_exercises_per_duration(duration: int, level: str) -> int:
    """
    Calcula quantos exercícios cabem no tempo disponível
    REGRA DURA: Máximo absoluto = 10 exercícios
    
    Classificação por tempo:
    - ≤30 min (Curto): 3-4 exercícios
    - 30-60 min (Médio): 5-6 exercícios
    - 60-90 min (Longo): 6-8 exercícios
    - >90 min (Estendido): 8-10 exercícios
    """
    if duration <= 30:
        max_ex = 4 if level in ['intermediario', 'avancado'] else 3
    elif duration <= 60:
        max_ex = 6 if level in ['intermediario', 'avancado'] else 5
    elif duration <= 90:
        max_ex = 8 if level in ['intermediario', 'avancado'] else 6
    else:
        max_ex = 10 if level == 'avancado' else 8
    
    return min(max_ex, 10)


def get_sets_per_duration(duration: int, level: str) -> int:
    """
    Calcula quantas séries por exercício baseado no tempo
    
    - ≤30 min (Curto): 2-3 séries
    - 30-60 min (Médio): 3-4 séries
    - 60-90 min (Longo): 3-4 séries
    - >90 min (Estendido): 4 séries
    """
    if duration <= 30:
        return 2 if level == 'novato' else 3
    elif duration <= 60:
        return 3
    elif duration <= 90:
        return 4 if level in ['intermediario', 'avancado'] else 3
    else:
        return 4


def get_max_days_for_level(level: str) -> int:
    """Retorna o máximo de dias de treino para cada nível"""
    if level == 'novato':
        return 3
    elif level == 'iniciante':
        return 5
    else:  # intermediario, avancado
        return 7


def parse_rest_seconds(rest_str: str) -> int:
    """Converte string de descanso para segundos"""
    rest_str = rest_str.lower().replace(" ", "")
    if "s" in rest_str:
        return int(rest_str.replace("s", ""))
    elif "min" in rest_str:
        return int(rest_str.replace("min", "")) * 60
    return 60
