"""
Sistema de Geração de Treino - V3 CURATED
==========================================
REGRAS RÍGIDAS:
1. Lista FIXA de exercícios verificados
2. Cada exercício DEVE ter GIF correto
3. Se não tem GIF, não usa o exercício
4. Prioriza POUCOS exercícios corretos
5. Objetivo: execução correta, app leve e confiável
==========================================
"""
import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# ==================== MODELS ====================

class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    muscle_group: str
    sets: int
    reps: str
    rest: str
    rest_seconds: int = 60
    notes: Optional[str] = None
    gif_url: str  # OBRIGATÓRIO - sem GIF, sem exercício
    completed: bool = False


class WorkoutDay(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    day: str
    exercises: List[Exercise]
    duration: int
    completed: bool = False


class WorkoutPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    training_level: str
    goal: str
    weekly_frequency: int
    workout_days: List[WorkoutDay]
    notes: Optional[str] = None


class WorkoutGenerateRequest(BaseModel):
    user_id: str


# ==================== EXERCÍCIOS VERIFICADOS ====================
# REGRA: Cada exercício tem GIF verificado e correto
# Fonte: ExerciseDB API (v2.exercisedb.io)
# Formato: https://v2.exercisedb.io/image/{id}

VERIFIED_EXERCISES = {
    # ============ PEITO (6 exercícios) ============
    "peito": [
        {
            "name": "Supino Reto com Barra",
            "gif": "https://v2.exercisedb.io/image/olM1PodWdLfDuT",
            "focus": "Peitoral médio e tríceps"
        },
        {
            "name": "Supino Inclinado com Halteres",
            "gif": "https://v2.exercisedb.io/image/IYaSFgP7M3DDhd",
            "focus": "Peitoral superior"
        },
        {
            "name": "Crucifixo com Halteres",
            "gif": "https://v2.exercisedb.io/image/slxLPcWCtIVc1r",
            "focus": "Abertura e definição peitoral"
        },
        {
            "name": "Flexão de Braço",
            "gif": "https://v2.exercisedb.io/image/Ib7iwouNPMorTZ",
            "focus": "Peitoral, tríceps e core"
        },
    ],
    
    # ============ COSTAS (5 exercícios) ============
    "costas": [
        {
            "name": "Remada Curvada com Barra",
            "gif": "https://v2.exercisedb.io/image/HfJvLC6Ts-R8oT",
            "focus": "Dorsais e trapézio"
        },
        {
            "name": "Puxada Frontal (Pulley)",
            "gif": "https://v2.exercisedb.io/image/SbgPg5SyN1PKMI",
            "focus": "Dorsais - largura"
        },
        {
            "name": "Remada Unilateral com Halter",
            "gif": "https://v2.exercisedb.io/image/pHX4xMjPxZvNmI",
            "focus": "Dorsais - espessura"
        },
        {
            "name": "Pulldown com Corda",
            "gif": "https://v2.exercisedb.io/image/kVRaNfT9AjFgMl",
            "focus": "Dorsais inferiores"
        },
    ],
    
    # ============ OMBROS (4 exercícios) ============
    "ombros": [
        {
            "name": "Desenvolvimento com Halteres",
            "gif": "https://v2.exercisedb.io/image/WNK2POJkTTavlE",
            "focus": "Deltoides - força geral"
        },
        {
            "name": "Elevação Lateral",
            "gif": "https://v2.exercisedb.io/image/kHpgO2qSGpQl52",
            "focus": "Deltoide lateral"
        },
        {
            "name": "Elevação Frontal com Halteres",
            "gif": "https://v2.exercisedb.io/image/gI-UUJMcCWKQTu",
            "focus": "Deltoide anterior"
        },
        {
            "name": "Face Pull com Corda",
            "gif": "https://v2.exercisedb.io/image/4kA46YUmhJRqq7",
            "focus": "Deltoide posterior e rotadores"
        },
    ],
    
    # ============ BÍCEPS (3 exercícios) ============
    "biceps": [
        {
            "name": "Rosca Direta com Barra",
            "gif": "https://v2.exercisedb.io/image/duD0hs3ybPrMXy",
            "focus": "Bíceps - massa geral"
        },
        {
            "name": "Rosca Alternada com Halteres",
            "gif": "https://v2.exercisedb.io/image/qFcxgWvsPCxxwW",
            "focus": "Bíceps - pico"
        },
        {
            "name": "Rosca Martelo",
            "gif": "https://v2.exercisedb.io/image/0K3253dDbG7lFH",
            "focus": "Bíceps e braquial"
        },
    ],
    
    # ============ TRÍCEPS (3 exercícios) ============
    "triceps": [
        {
            "name": "Tríceps Corda (Pulley)",
            "gif": "https://v2.exercisedb.io/image/b5jqMulSQ78an8",
            "focus": "Tríceps - cabeça lateral"
        },
        {
            "name": "Tríceps Testa com Barra",
            "gif": "https://v2.exercisedb.io/image/nGp3rJqA2xRGmZ",
            "focus": "Tríceps - cabeça longa"
        },
        {
            "name": "Mergulho entre Bancos",
            "gif": "https://v2.exercisedb.io/image/t0gKC8ZmpBqR10",
            "focus": "Tríceps - força geral"
        },
    ],
    
    # ============ QUADRÍCEPS (4 exercícios) ============
    "quadriceps": [
        {
            "name": "Agachamento com Barra",
            "gif": "https://v2.exercisedb.io/image/y8VRjjLOQeblgb",
            "focus": "Quadríceps, glúteos e core"
        },
        {
            "name": "Leg Press 45°",
            "gif": "https://v2.exercisedb.io/image/aFk01enahYCTVY",
            "focus": "Quadríceps - força"
        },
        {
            "name": "Cadeira Extensora",
            "gif": "https://v2.exercisedb.io/image/oRfpGwDbFJTfSM",
            "focus": "Quadríceps - isolamento"
        },
        {
            "name": "Afundo com Halteres",
            "gif": "https://v2.exercisedb.io/image/Lh0GgLgH6-5HE4",
            "focus": "Quadríceps e glúteos"
        },
    ],
    
    # ============ POSTERIOR DE COXA (3 exercícios) ============
    "posterior": [
        {
            "name": "Stiff com Barra",
            "gif": "https://v2.exercisedb.io/image/1tOVSp5enGZjRr",
            "focus": "Posterior e glúteos"
        },
        {
            "name": "Mesa Flexora",
            "gif": "https://v2.exercisedb.io/image/JDJhxFpNgAIYS0",
            "focus": "Posterior - isolamento"
        },
        {
            "name": "Elevação Pélvica (Hip Thrust)",
            "gif": "https://v2.exercisedb.io/image/7WGGpkLjU0JWKy",
            "focus": "Glúteos e posterior"
        },
    ],
    
    # ============ PANTURRILHA (2 exercícios) ============
    "panturrilha": [
        {
            "name": "Panturrilha em Pé na Máquina",
            "gif": "https://v2.exercisedb.io/image/BC4rTSsOuuoHXK",
            "focus": "Gastrocnêmio"
        },
        {
            "name": "Panturrilha Sentado",
            "gif": "https://v2.exercisedb.io/image/4YIBN4uJXlDYDt",
            "focus": "Sóleo"
        },
    ],
    
    # ============ ABDÔMEN (3 exercícios) ============
    "abdomen": [
        {
            "name": "Abdominal Crunch",
            "gif": "https://v2.exercisedb.io/image/QajGP8xnVk2YFa",
            "focus": "Reto abdominal superior"
        },
        {
            "name": "Prancha Isométrica",
            "gif": "https://v2.exercisedb.io/image/KjSIReuLyoVdGC",
            "focus": "Core completo"
        },
        {
            "name": "Elevação de Pernas",
            "gif": "https://v2.exercisedb.io/image/q6RKcc8jBuLEyH",
            "focus": "Abdominal inferior"
        },
    ],
}

DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ==================== SPLITS OTIMIZADOS ====================
# Usa APENAS os exercícios verificados acima

def get_split_for_frequency(freq: int) -> List[Dict]:
    """Retorna split usando apenas exercícios verificados"""
    
    splits = {
        1: [
            {"name": "Full Body", "muscles": ["peito", "costas", "quadriceps", "ombros", "biceps", "triceps"]}
        ],
        2: [
            {"name": "Upper (Superior)", "muscles": ["peito", "costas", "ombros", "biceps", "triceps"]},
            {"name": "Lower (Inferior)", "muscles": ["quadriceps", "posterior", "panturrilha", "abdomen"]},
        ],
        3: [
            {"name": "A - Push (Empurrar)", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "B - Pull (Puxar)", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "C - Legs (Pernas)", "muscles": ["quadriceps", "posterior", "panturrilha"]},
        ],
        4: [
            {"name": "A - Peito/Tríceps", "muscles": ["peito", "triceps"]},
            {"name": "B - Costas/Bíceps", "muscles": ["costas", "biceps"]},
            {"name": "C - Pernas", "muscles": ["quadriceps", "posterior", "panturrilha"]},
            {"name": "D - Ombros/Abdômen", "muscles": ["ombros", "abdomen"]},
        ],
        5: [
            {"name": "A - Peito", "muscles": ["peito", "triceps"]},
            {"name": "B - Costas", "muscles": ["costas", "biceps"]},
            {"name": "C - Pernas Quad", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "D - Ombros", "muscles": ["ombros", "abdomen"]},
            {"name": "E - Pernas Post", "muscles": ["posterior", "quadriceps"]},
        ],
        6: [
            {"name": "A - Push", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "B - Pull", "muscles": ["costas", "biceps"]},
            {"name": "C - Legs", "muscles": ["quadriceps", "posterior", "panturrilha"]},
            {"name": "D - Push", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "E - Pull", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "F - Legs", "muscles": ["quadriceps", "posterior", "panturrilha"]},
        ],
        7: [
            {"name": "A - Peito", "muscles": ["peito"]},
            {"name": "B - Costas", "muscles": ["costas"]},
            {"name": "C - Ombros", "muscles": ["ombros"]},
            {"name": "D - Braços", "muscles": ["biceps", "triceps"]},
            {"name": "E - Quadríceps", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "F - Posterior", "muscles": ["posterior"]},
            {"name": "G - Core", "muscles": ["abdomen"]},
        ],
    }
    
    return splits.get(freq, splits[3])


def parse_rest_seconds(rest_str: str) -> int:
    """Converte string de descanso para segundos"""
    rest_str = rest_str.lower().replace(" ", "")
    if "s" in rest_str:
        return int(rest_str.replace("s", ""))
    elif "min" in rest_str:
        return int(rest_str.replace("min", "")) * 60
    return 60


# ==================== SERVIÇO PRINCIPAL ====================

class WorkoutAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    def generate_workout_plan(self, user_profile: Dict) -> WorkoutPlan:
        """
        Gera plano de treino usando APENAS exercícios verificados.
        """
        frequency = user_profile.get('weekly_training_frequency', 3)
        frequency = max(1, min(7, frequency))
        
        level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        
        return self._generate_verified_workout(user_profile['id'], frequency, level, goal)
    
    def _generate_verified_workout(
        self,
        user_id: str,
        frequency: int,
        level: str,
        goal: str
    ) -> WorkoutPlan:
        """
        Gera treino usando APENAS exercícios com GIFs verificados.
        """
        
        split = get_split_for_frequency(frequency)
        
        # Configuração por nível
        config = {
            "iniciante": {"sets": 3, "reps": "12-15", "rest": "90s", "ex_per_muscle": 2},
            "intermediario": {"sets": 4, "reps": "10-12", "rest": "75s", "ex_per_muscle": 2},
            "avancado": {"sets": 4, "reps": "8-12", "rest": "60s", "ex_per_muscle": 3}
        }.get(level, {"sets": 4, "reps": "10-12", "rest": "75s", "ex_per_muscle": 2})
        
        workout_days = []
        
        for i in range(frequency):
            template = split[i]
            exercises = []
            
            for muscle in template["muscles"]:
                available = VERIFIED_EXERCISES.get(muscle, [])
                
                # Pega apenas exercícios verificados
                for j in range(min(config["ex_per_muscle"], len(available))):
                    ex_data = available[j]
                    
                    # REGRA: Só adiciona se tem GIF
                    if not ex_data.get("gif"):
                        continue
                    
                    rest_str = config["rest"]
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=muscle.capitalize(),
                        sets=config["sets"],
                        reps=config["reps"],
                        rest=rest_str,
                        rest_seconds=parse_rest_seconds(rest_str),
                        notes=ex_data.get("focus"),
                        gif_url=ex_data["gif"],
                        completed=False
                    ))
            
            duration = len(exercises) * 5 + 10
            
            workout_days.append(WorkoutDay(
                name=f"Treino {template['name']}",
                day=DAYS[i] if i < 7 else f"Dia {i + 1}",
                duration=duration,
                exercises=exercises,
                completed=False
            ))
        
        split_name = {
            1: "Full Body",
            2: "Upper/Lower",
            3: "Push/Pull/Legs (A/B/C)",
            4: "ABCD Split",
            5: "ABCDE Split",
            6: "PPL 2x (A-F)",
            7: "Bro Split (A-G)"
        }.get(frequency, "Personalizado")
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=level,
            goal=goal,
            weekly_frequency=frequency,
            workout_days=workout_days,
            notes=f"Divisão {split_name} - {frequency}x/semana. Todos os exercícios com demonstração em vídeo."
        )
