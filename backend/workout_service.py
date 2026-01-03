"""
Sistema de Geração de Treino com IA - V2
========================================
- Divisão A/B/C semanal
- GIFs de demonstração de exercícios
- Suporte para marcar exercícios como concluídos
"""
import os
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime
import uuid

# ==================== MODELS ====================

class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    muscle_group: str
    sets: int
    reps: str
    rest: str  # Tempo de descanso em segundos (ex: "60s", "90s")
    rest_seconds: int = 60  # Tempo em segundos para o timer
    notes: Optional[str] = None
    gif_url: Optional[str] = None  # URL do GIF demonstrativo
    completed: bool = False  # Marcar como concluído


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


# ==================== BANCO DE EXERCÍCIOS COM GIFs ====================
# GIFs de exercícios públicos (musclewiki, giphy, etc.)

EXERCISES = {
    "peito": [
        {
            "name": "Supino Reto com Barra",
            "focus": "Peitoral médio",
            "gif": "https://www.gymvisual.com/img/p/1/7/5/5/9/17559.gif"
        },
        {
            "name": "Supino Inclinado com Halteres",
            "focus": "Peitoral superior",
            "gif": "https://www.gymvisual.com/img/p/4/9/7/5/4975.gif"
        },
        {
            "name": "Crucifixo Inclinado",
            "focus": "Abertura peitoral",
            "gif": "https://www.gymvisual.com/img/p/2/1/2/0/9/21209.gif"
        },
        {
            "name": "Cross Over (Polia)",
            "focus": "Definição peitoral",
            "gif": "https://www.gymvisual.com/img/p/5/0/0/0/5000.gif"
        },
        {
            "name": "Flexão de Braço",
            "focus": "Peitoral geral",
            "gif": "https://www.gymvisual.com/img/p/2/0/9/1/3/20913.gif"
        },
    ],
    "costas": [
        {
            "name": "Barra Fixa",
            "focus": "Dorsais",
            "gif": "https://www.gymvisual.com/img/p/1/0/8/3/0/10830.gif"
        },
        {
            "name": "Remada Curvada com Barra",
            "focus": "Dorsais/Trapézio",
            "gif": "https://www.gymvisual.com/img/p/1/7/9/4/7/17947.gif"
        },
        {
            "name": "Pulldown (Puxada Frontal)",
            "focus": "Dorsais",
            "gif": "https://www.gymvisual.com/img/p/1/3/0/0/0/13000.gif"
        },
        {
            "name": "Remada Cavalinho",
            "focus": "Dorsais médios",
            "gif": "https://www.gymvisual.com/img/p/2/0/2/5/3/20253.gif"
        },
        {
            "name": "Remada Unilateral",
            "focus": "Dorsais",
            "gif": "https://www.gymvisual.com/img/p/4/9/0/6/4906.gif"
        },
    ],
    "quadriceps": [
        {
            "name": "Agachamento Livre",
            "focus": "Quadríceps/Glúteos",
            "gif": "https://www.gymvisual.com/img/p/2/0/4/1/7/20417.gif"
        },
        {
            "name": "Leg Press 45°",
            "focus": "Quadríceps",
            "gif": "https://www.gymvisual.com/img/p/1/0/5/4/1/10541.gif"
        },
        {
            "name": "Cadeira Extensora",
            "focus": "Quadríceps",
            "gif": "https://www.gymvisual.com/img/p/1/0/5/2/7/10527.gif"
        },
        {
            "name": "Afundo com Halteres",
            "focus": "Quadríceps/Glúteos",
            "gif": "https://www.gymvisual.com/img/p/4/9/4/0/4940.gif"
        },
        {
            "name": "Hack Squat",
            "focus": "Quadríceps",
            "gif": "https://www.gymvisual.com/img/p/2/0/9/5/7/20957.gif"
        },
    ],
    "posterior": [
        {
            "name": "Stiff",
            "focus": "Posterior/Glúteos",
            "gif": "https://www.gymvisual.com/img/p/2/0/4/0/9/20409.gif"
        },
        {
            "name": "Mesa Flexora",
            "focus": "Posterior de coxa",
            "gif": "https://www.gymvisual.com/img/p/1/0/5/1/5/10515.gif"
        },
        {
            "name": "Cadeira Flexora",
            "focus": "Posterior",
            "gif": "https://www.gymvisual.com/img/p/1/0/5/1/9/10519.gif"
        },
        {
            "name": "Elevação Pélvica",
            "focus": "Glúteos",
            "gif": "https://www.gymvisual.com/img/p/6/0/6/8/6068.gif"
        },
    ],
    "panturrilha": [
        {
            "name": "Panturrilha em Pé",
            "focus": "Gastrocnêmio",
            "gif": "https://www.gymvisual.com/img/p/1/0/5/5/5/10555.gif"
        },
        {
            "name": "Panturrilha Sentado",
            "focus": "Sóleo",
            "gif": "https://www.gymvisual.com/img/p/1/0/5/5/9/10559.gif"
        },
    ],
    "ombros": [
        {
            "name": "Desenvolvimento com Halteres",
            "focus": "Deltoides",
            "gif": "https://www.gymvisual.com/img/p/4/8/6/8/4868.gif"
        },
        {
            "name": "Elevação Lateral",
            "focus": "Deltoide médio",
            "gif": "https://www.gymvisual.com/img/p/4/8/7/6/4876.gif"
        },
        {
            "name": "Elevação Frontal",
            "focus": "Deltoide anterior",
            "gif": "https://www.gymvisual.com/img/p/4/8/9/2/4892.gif"
        },
        {
            "name": "Crucifixo Inverso",
            "focus": "Deltoide posterior",
            "gif": "https://www.gymvisual.com/img/p/5/7/4/4/5744.gif"
        },
        {
            "name": "Face Pull",
            "focus": "Deltoide posterior",
            "gif": "https://www.gymvisual.com/img/p/1/2/2/2/8/12228.gif"
        },
    ],
    "biceps": [
        {
            "name": "Rosca Direta com Barra",
            "focus": "Bíceps",
            "gif": "https://www.gymvisual.com/img/p/1/7/5/7/3/17573.gif"
        },
        {
            "name": "Rosca Alternada",
            "focus": "Bíceps",
            "gif": "https://www.gymvisual.com/img/p/4/7/7/6/4776.gif"
        },
        {
            "name": "Rosca Martelo",
            "focus": "Bíceps/Antebraço",
            "gif": "https://www.gymvisual.com/img/p/4/7/8/0/4780.gif"
        },
        {
            "name": "Rosca Scott",
            "focus": "Pico do bíceps",
            "gif": "https://www.gymvisual.com/img/p/4/8/2/0/4820.gif"
        },
    ],
    "triceps": [
        {
            "name": "Tríceps Testa",
            "focus": "Tríceps",
            "gif": "https://www.gymvisual.com/img/p/1/7/5/9/3/17593.gif"
        },
        {
            "name": "Tríceps Corda (Polia)",
            "focus": "Tríceps",
            "gif": "https://www.gymvisual.com/img/p/1/2/7/1/2/12712.gif"
        },
        {
            "name": "Mergulho em Paralelas",
            "focus": "Tríceps",
            "gif": "https://www.gymvisual.com/img/p/6/2/7/2/6272.gif"
        },
        {
            "name": "Tríceps Francês",
            "focus": "Cabeça longa",
            "gif": "https://www.gymvisual.com/img/p/4/8/4/4/4844.gif"
        },
    ],
    "abdomen": [
        {
            "name": "Abdominal Supra",
            "focus": "Reto abdominal",
            "gif": "https://www.gymvisual.com/img/p/1/0/4/9/1/10491.gif"
        },
        {
            "name": "Prancha Isométrica",
            "focus": "Core",
            "gif": "https://www.gymvisual.com/img/p/6/1/1/2/6112.gif"
        },
        {
            "name": "Elevação de Pernas",
            "focus": "Abdominal inferior",
            "gif": "https://www.gymvisual.com/img/p/1/9/8/6/5/19865.gif"
        },
        {
            "name": "Abdominal Bicicleta",
            "focus": "Oblíquos",
            "gif": "https://www.gymvisual.com/img/p/1/1/1/6/8/11168.gif"
        },
    ],
}

DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ==================== SPLITS A/B/C ====================

def get_split_for_frequency(freq: int) -> List[Dict]:
    """Retorna split EXATO para a frequência especificada"""
    
    splits = {
        1: [
            {"name": "Full Body", "muscles": ["peito", "costas", "quadriceps", "ombros", "biceps", "triceps", "abdomen"]}
        ],
        2: [
            {"name": "Full Body A", "muscles": ["peito", "costas", "quadriceps", "ombros", "abdomen"]},
            {"name": "Full Body B", "muscles": ["peito", "costas", "posterior", "biceps", "triceps"]},
        ],
        3: [
            {"name": "A - Push (Empurrar)", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "B - Pull (Puxar)", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "C - Legs (Pernas)", "muscles": ["quadriceps", "posterior", "panturrilha"]},
        ],
        4: [
            {"name": "A - Upper (Superior)", "muscles": ["peito", "costas", "ombros"]},
            {"name": "B - Lower (Inferior)", "muscles": ["quadriceps", "posterior", "panturrilha", "abdomen"]},
            {"name": "C - Upper (Superior)", "muscles": ["peito", "costas", "biceps", "triceps"]},
            {"name": "D - Lower (Inferior)", "muscles": ["quadriceps", "posterior", "panturrilha", "abdomen"]},
        ],
        5: [
            {"name": "A - Peito/Tríceps", "muscles": ["peito", "triceps"]},
            {"name": "B - Costas/Bíceps", "muscles": ["costas", "biceps"]},
            {"name": "C - Pernas Quad", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "D - Ombros/Abdômen", "muscles": ["ombros", "abdomen"]},
            {"name": "E - Pernas Posterior", "muscles": ["posterior", "quadriceps"]},
        ],
        6: [
            {"name": "A - Push", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "B - Pull", "muscles": ["costas", "biceps"]},
            {"name": "C - Legs", "muscles": ["quadriceps", "panturrilha", "abdomen"]},
            {"name": "D - Push", "muscles": ["ombros", "peito", "triceps"]},
            {"name": "E - Pull", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "F - Legs", "muscles": ["posterior", "quadriceps", "panturrilha"]},
        ],
        7: [
            {"name": "A - Peito", "muscles": ["peito"]},
            {"name": "B - Costas", "muscles": ["costas"]},
            {"name": "C - Ombros", "muscles": ["ombros", "abdomen"]},
            {"name": "D - Quadríceps", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "E - Posterior", "muscles": ["posterior"]},
            {"name": "F - Braços", "muscles": ["biceps", "triceps"]},
            {"name": "G - Core/Cardio", "muscles": ["abdomen"]},
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
        Gera plano de treino com EXATAMENTE N sessões.
        N = weekly_training_frequency. Tolerância: ZERO.
        """
        frequency = user_profile.get('weekly_training_frequency', 3)
        frequency = max(1, min(7, frequency))  # Limita entre 1-7
        
        level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        
        # Gera treino determinístico com GIFs
        return self._generate_exact_workout(user_profile['id'], frequency, level, goal)
    
    def _generate_exact_workout(
        self,
        user_id: str,
        frequency: int,
        level: str,
        goal: str
    ) -> WorkoutPlan:
        """
        Gera treino determinístico com EXATAMENTE frequency sessões.
        Inclui GIFs de demonstração para cada exercício.
        """
        
        # Obtém split para esta frequência
        split = get_split_for_frequency(frequency)
        
        # Configuração por nível
        config = {
            "iniciante": {"sets": 3, "reps": "12-15", "rest": "90s", "ex_per_muscle": 2},
            "intermediario": {"sets": 4, "reps": "10-12", "rest": "75s", "ex_per_muscle": 3},
            "avancado": {"sets": 4, "reps": "8-12", "rest": "60s", "ex_per_muscle": 4}
        }.get(level, {"sets": 4, "reps": "10-12", "rest": "75s", "ex_per_muscle": 3})
        
        workout_days = []
        
        # Gera EXATAMENTE frequency treinos
        for i in range(frequency):
            template = split[i]
            exercises = []
            
            for muscle in template["muscles"]:
                available = EXERCISES.get(muscle, [])
                for j in range(min(config["ex_per_muscle"], len(available))):
                    ex_data = available[j]
                    rest_str = config["rest"]
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=muscle.capitalize(),
                        sets=config["sets"],
                        reps=config["reps"],
                        rest=rest_str,
                        rest_seconds=parse_rest_seconds(rest_str),
                        notes=ex_data.get("focus"),
                        gif_url=ex_data.get("gif"),
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
        
        # VERIFICAÇÃO FINAL
        assert len(workout_days) == frequency, f"Erro: gerou {len(workout_days)}, esperado {frequency}"
        
        split_name = {
            1: "Full Body",
            2: "Full Body A/B",
            3: "Push/Pull/Legs (A/B/C)",
            4: "Upper/Lower (A/B/C/D)",
            5: "ABCDE",
            6: "PPL 2x (A-F)",
            7: "Bro Split (A-G)"
        }.get(frequency, "Personalizado")
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=level,
            goal=goal,
            weekly_frequency=frequency,
            workout_days=workout_days,
            notes=f"Divisão {split_name} - {frequency}x/semana. Descanse entre séries conforme indicado. Aumente cargas progressivamente."
        )
