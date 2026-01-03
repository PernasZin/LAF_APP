"""
Sistema de Geração de Treino - V5 TEXT ONLY
===========================================
DECISÃO DE PRODUTO FINAL:
- Sem GIFs, sem vídeos, sem mídia
- Orientação de execução apenas por TEXTO
- Simplicidade e correção > visuais
===========================================
"""
import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# ==================== MODELS ====================

class Exercise(BaseModel):
    """Exercício - TEXT ONLY, sem mídia"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    muscle_group: str
    sets: int
    reps: str
    rest: str
    rest_seconds: int = 60
    notes: Optional[str] = None  # Dicas de execução em texto
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


# ==================== BANCO DE EXERCÍCIOS (TEXT ONLY) ====================

EXERCISES = {
    "peito": [
        {"name": "Supino Reto com Barra", "notes": "Deite no banco, desça a barra até o peito, empurre até extensão completa"},
        {"name": "Supino Inclinado com Halteres", "notes": "Banco a 30-45°, desça controlado, suba sem bater os halteres"},
        {"name": "Crucifixo com Halteres", "notes": "Braços levemente flexionados, desça em arco até sentir alongamento"},
        {"name": "Flexão de Braço", "notes": "Corpo reto, desça até o peito quase tocar o chão, suba explosivo"},
    ],
    "costas": [
        {"name": "Remada Curvada com Barra", "notes": "Costas retas a 45°, puxe a barra até o abdômen, contraia as escápulas"},
        {"name": "Puxada Frontal", "notes": "Pegada um pouco mais larga que ombros, puxe até o queixo, controle a descida"},
        {"name": "Remada Unilateral", "notes": "Apoie um joelho no banco, costas retas, puxe o cotovelo para trás"},
        {"name": "Pulldown com Corda", "notes": "Braços estendidos, puxe até as coxas, aperte no final"},
    ],
    "ombros": [
        {"name": "Desenvolvimento com Halteres", "notes": "Sentado ou em pé, empurre acima da cabeça, desça até orelhas"},
        {"name": "Elevação Lateral", "notes": "Cotovelos levemente flexionados, eleve até altura dos ombros"},
        {"name": "Elevação Frontal", "notes": "Braços estendidos, eleve até altura dos olhos, desça controlado"},
        {"name": "Face Pull", "notes": "Puxe a corda em direção ao rosto, cotovelos altos, aperte escápulas"},
    ],
    "biceps": [
        {"name": "Rosca Direta com Barra", "notes": "Cotovelos fixos ao lado do corpo, suba contraindo, desça controlado"},
        {"name": "Rosca Alternada", "notes": "Alterne os braços, supine o punho no topo, controle a descida"},
        {"name": "Rosca Martelo", "notes": "Pegada neutra, cotovelos fixos, suba até contrair o bíceps"},
    ],
    "triceps": [
        {"name": "Tríceps Corda", "notes": "Cotovelos fixos, estenda completamente, abra a corda no final"},
        {"name": "Tríceps Testa", "notes": "Deite no banco, desça a barra até a testa, estenda sem mover cotovelos"},
        {"name": "Mergulho entre Bancos", "notes": "Mãos no banco atrás, desça até 90° nos cotovelos, empurre"},
    ],
    "quadriceps": [
        {"name": "Agachamento Livre", "notes": "Pés na largura dos ombros, desça até coxas paralelas, joelhos alinhados"},
        {"name": "Leg Press 45°", "notes": "Pés no meio da plataforma, desça até 90°, empurre sem travar joelhos"},
        {"name": "Cadeira Extensora", "notes": "Estenda as pernas completamente, contraia no topo, desça controlado"},
        {"name": "Afundo com Halteres", "notes": "Passo largo à frente, desça até joelho quase tocar o chão"},
    ],
    "posterior": [
        {"name": "Stiff com Barra", "notes": "Pernas semi-estendidas, desça a barra deslizando nas coxas, sinta alongar"},
        {"name": "Mesa Flexora", "notes": "Deite de bruços, flexione até contrair posterior, desça controlado"},
        {"name": "Elevação Pélvica", "notes": "Costas no banco, pés no chão, eleve o quadril contraindo glúteos"},
    ],
    "panturrilha": [
        {"name": "Panturrilha em Pé", "notes": "Eleve nos dedos o máximo possível, desça alongando bem"},
        {"name": "Panturrilha Sentado", "notes": "Joelhos a 90°, eleve os calcanhares, contraia no topo"},
    ],
    "abdomen": [
        {"name": "Abdominal Crunch", "notes": "Mãos atrás da cabeça, eleve ombros do chão, não puxe o pescoço"},
        {"name": "Prancha Isométrica", "notes": "Corpo reto da cabeça aos pés, não deixe o quadril subir ou descer"},
        {"name": "Elevação de Pernas", "notes": "Costas no chão, eleve pernas estendidas até 90°, desça sem tocar"},
    ],
}

DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ==================== SPLITS ====================

def get_split_for_frequency(freq: int) -> List[Dict]:
    splits = {
        1: [{"name": "Full Body", "muscles": ["peito", "costas", "quadriceps", "ombros", "biceps", "triceps"]}],
        2: [
            {"name": "Upper", "muscles": ["peito", "costas", "ombros", "biceps", "triceps"]},
            {"name": "Lower", "muscles": ["quadriceps", "posterior", "panturrilha", "abdomen"]},
        ],
        3: [
            {"name": "A - Push", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "B - Pull", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "C - Legs", "muscles": ["quadriceps", "posterior", "panturrilha"]},
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
    rest_str = rest_str.lower().replace(" ", "")
    if "s" in rest_str:
        return int(rest_str.replace("s", ""))
    elif "min" in rest_str:
        return int(rest_str.replace("min", "")) * 60
    return 60


# ==================== SERVIÇO ====================

class WorkoutAIService:
    def __init__(self):
        pass
    
    def generate_workout_plan(self, user_profile: Dict) -> WorkoutPlan:
        frequency = user_profile.get('weekly_training_frequency', 3)
        frequency = max(1, min(7, frequency))
        
        level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        
        return self._generate_workout(user_profile['id'], frequency, level, goal)
    
    def _generate_workout(self, user_id: str, frequency: int, level: str, goal: str) -> WorkoutPlan:
        split = get_split_for_frequency(frequency)
        
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
                        notes=ex_data.get("notes"),
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
            1: "Full Body", 2: "Upper/Lower", 3: "Push/Pull/Legs",
            4: "ABCD", 5: "ABCDE", 6: "PPL 2x", 7: "Bro Split"
        }.get(frequency, "Personalizado")
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=level,
            goal=goal,
            weekly_frequency=frequency,
            workout_days=workout_days,
            notes=f"{split_name} - {frequency}x/semana"
        )
