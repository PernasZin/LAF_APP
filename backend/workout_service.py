"""
Sistema de Geração de Treino com IA
Utiliza Emergent LLM Key para gerar planos de treino personalizados

REGRA ABSOLUTA (TOLERÂNCIA ZERO):
O número de sessões de treino DEVE ser EXATAMENTE igual ao weekly_training_frequency.
Não há aproximação. Não há exceção.
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
    rest: str
    notes: Optional[str] = None

class WorkoutDay(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    day: str
    exercises: List[Exercise]
    duration: int

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

# ==================== BANCO DE EXERCÍCIOS ====================

EXERCISES = {
    "peito": [
        {"name": "Supino Reto com Barra", "focus": "Peitoral médio"},
        {"name": "Supino Inclinado com Halteres", "focus": "Peitoral superior"},
        {"name": "Crucifixo Inclinado", "focus": "Abertura peitoral"},
        {"name": "Cross Over (Polia)", "focus": "Definição peitoral"},
        {"name": "Flexão de Braço", "focus": "Peitoral geral"},
    ],
    "costas": [
        {"name": "Barra Fixa", "focus": "Dorsais"},
        {"name": "Remada Curvada com Barra", "focus": "Dorsais/Trapézio"},
        {"name": "Pulldown (Puxada Frontal)", "focus": "Dorsais"},
        {"name": "Remada Cavalinho", "focus": "Dorsais médios"},
        {"name": "Remada Unilateral", "focus": "Dorsais"},
    ],
    "quadriceps": [
        {"name": "Agachamento Livre", "focus": "Quadríceps/Glúteos"},
        {"name": "Leg Press 45°", "focus": "Quadríceps"},
        {"name": "Cadeira Extensora", "focus": "Quadríceps"},
        {"name": "Afundo com Halteres", "focus": "Quadríceps/Glúteos"},
        {"name": "Hack Squat", "focus": "Quadríceps"},
    ],
    "posterior": [
        {"name": "Stiff", "focus": "Posterior/Glúteos"},
        {"name": "Mesa Flexora", "focus": "Posterior de coxa"},
        {"name": "Cadeira Flexora", "focus": "Posterior"},
        {"name": "Elevação Pélvica", "focus": "Glúteos"},
    ],
    "panturrilha": [
        {"name": "Panturrilha em Pé", "focus": "Gastrocnêmio"},
        {"name": "Panturrilha Sentado", "focus": "Sóleo"},
    ],
    "ombros": [
        {"name": "Desenvolvimento com Halteres", "focus": "Deltoides"},
        {"name": "Elevação Lateral", "focus": "Deltoide médio"},
        {"name": "Elevação Frontal", "focus": "Deltoide anterior"},
        {"name": "Crucifixo Inverso", "focus": "Deltoide posterior"},
        {"name": "Face Pull", "focus": "Deltoide posterior"},
    ],
    "biceps": [
        {"name": "Rosca Direta com Barra", "focus": "Bíceps"},
        {"name": "Rosca Alternada", "focus": "Bíceps"},
        {"name": "Rosca Martelo", "focus": "Bíceps/Antebraço"},
        {"name": "Rosca Scott", "focus": "Pico do bíceps"},
    ],
    "triceps": [
        {"name": "Tríceps Testa", "focus": "Tríceps"},
        {"name": "Tríceps Corda (Polia)", "focus": "Tríceps"},
        {"name": "Mergulho em Paralelas", "focus": "Tríceps"},
        {"name": "Tríceps Francês", "focus": "Cabeça longa"},
    ],
    "abdomen": [
        {"name": "Abdominal Supra", "focus": "Reto abdominal"},
        {"name": "Prancha Isométrica", "focus": "Core"},
        {"name": "Elevação de Pernas", "focus": "Abdominal inferior"},
        {"name": "Abdominal Bicicleta", "focus": "Oblíquos"},
    ],
}

DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ==================== SPLITS PRÉ-DEFINIDOS ====================

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
            {"name": "Push (Empurrar)", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "Pull (Puxar)", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "Legs (Pernas)", "muscles": ["quadriceps", "posterior", "panturrilha"]},
        ],
        4: [
            {"name": "Upper A (Superior)", "muscles": ["peito", "costas", "ombros"]},
            {"name": "Lower A (Inferior)", "muscles": ["quadriceps", "posterior", "panturrilha", "abdomen"]},
            {"name": "Upper B (Superior)", "muscles": ["peito", "costas", "biceps", "triceps"]},
            {"name": "Lower B (Inferior)", "muscles": ["quadriceps", "posterior", "panturrilha", "abdomen"]},
        ],
        5: [
            {"name": "Peito/Tríceps", "muscles": ["peito", "triceps"]},
            {"name": "Costas/Bíceps", "muscles": ["costas", "biceps"]},
            {"name": "Pernas Quadríceps", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "Ombros/Abdômen", "muscles": ["ombros", "abdomen"]},
            {"name": "Pernas Posterior", "muscles": ["posterior", "quadriceps"]},
        ],
        6: [
            {"name": "Push A", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "Pull A", "muscles": ["costas", "biceps"]},
            {"name": "Legs A", "muscles": ["quadriceps", "panturrilha", "abdomen"]},
            {"name": "Push B", "muscles": ["ombros", "peito", "triceps"]},
            {"name": "Pull B", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "Legs B", "muscles": ["posterior", "quadriceps", "panturrilha"]},
        ],
        7: [
            {"name": "Peito", "muscles": ["peito"]},
            {"name": "Costas", "muscles": ["costas"]},
            {"name": "Ombros", "muscles": ["ombros", "abdomen"]},
            {"name": "Quadríceps", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "Posterior/Glúteos", "muscles": ["posterior"]},
            {"name": "Braços", "muscles": ["biceps", "triceps"]},
            {"name": "Cardio/Core", "muscles": ["abdomen"]},
        ],
    }
    
    return splits.get(freq, splits[4])

# ==================== SERVIÇO PRINCIPAL ====================

class WorkoutAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id=f"workout_{uuid.uuid4().hex[:8]}",
            system_message="Você é um personal trainer. Responda APENAS em JSON válido."
        )
    
    def generate_workout_plan(self, user_profile: Dict) -> WorkoutPlan:
        """
        Gera plano de treino com EXATAMENTE N sessões.
        N = weekly_training_frequency. Tolerância: ZERO.
        """
        frequency = user_profile.get('weekly_training_frequency', 4)
        frequency = max(1, min(7, frequency))  # Limita entre 1-7
        
        level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        
        # Tenta com IA primeiro
        try:
            plan = self._generate_with_ai(user_profile, frequency)
            if plan and len(plan.workout_days) == frequency:
                return plan
            print(f"IA gerou {len(plan.workout_days) if plan else 0} treinos, esperado {frequency}. Usando fallback.")
        except Exception as e:
            print(f"Erro na geração com IA: {e}")
        
        # Fallback determinístico - SEMPRE gera exatamente N treinos
        return self._generate_exact_workout(user_profile['id'], frequency, level, goal)
    
    def _generate_with_ai(self, user_profile: Dict, frequency: int) -> Optional[WorkoutPlan]:
        """Tenta gerar treino com IA"""
        
        level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        
        prompt = f"""
Crie um plano de treino semanal com EXATAMENTE {frequency} TREINOS.

REGRA ABSOLUTA: Gere EXATAMENTE {frequency} treinos, nem mais nem menos.

PERFIL:
- Nível: {level}
- Objetivo: {goal}
- Frequência: {frequency}x/semana

EXERCÍCIOS DISPONÍVEIS:
{json.dumps(EXERCISES, indent=2, ensure_ascii=False)}

RESPONDA APENAS COM JSON:
{{"workout_days":[{{"name":"Treino A","day":"Segunda","duration":60,"exercises":[{{"name":"Supino Reto com Barra","muscle_group":"Peito","sets":4,"reps":"8-12","rest":"90s"}}]}}]}}

LEMBRE-SE: EXATAMENTE {frequency} treinos!
"""
        
        try:
            response = self.llm.send_message(prompt)
            return self._parse_ai_response(response, user_profile['id'], user_profile)
        except Exception as e:
            print(f"Erro ao chamar LLM: {e}")
            raise
    
    def _parse_ai_response(self, response: str, user_id: str, user_profile: Dict) -> WorkoutPlan:
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
        
        workout_days = []
        for day_data in data.get('workout_days', []):
            exercises = []
            for ex in day_data.get('exercises', []):
                exercises.append(Exercise(
                    name=ex.get('name', 'Exercício'),
                    muscle_group=ex.get('muscle_group', 'Geral'),
                    sets=ex.get('sets', 3),
                    reps=ex.get('reps', '10-12'),
                    rest=ex.get('rest', '60s'),
                    notes=ex.get('notes')
                ))
            
            workout_days.append(WorkoutDay(
                name=day_data.get('name', 'Treino'),
                day=day_data.get('day', ''),
                duration=day_data.get('duration', 60),
                exercises=exercises
            ))
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=user_profile.get('training_level', 'intermediario'),
            goal=user_profile.get('goal', 'bulking'),
            weekly_frequency=user_profile.get('weekly_training_frequency', len(workout_days)),
            workout_days=workout_days,
            notes="Plano gerado com IA."
        )
    
    def _generate_exact_workout(
        self,
        user_id: str,
        frequency: int,
        level: str,
        goal: str
    ) -> WorkoutPlan:
        """
        Gera treino determinístico com EXATAMENTE frequency sessões.
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
            template = split[i]  # Já garantido que len(split) == frequency
            exercises = []
            
            for muscle in template["muscles"]:
                available = EXERCISES.get(muscle, [])
                for j in range(min(config["ex_per_muscle"], len(available))):
                    ex_data = available[j]
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=muscle.capitalize(),
                        sets=config["sets"],
                        reps=config["reps"],
                        rest=config["rest"],
                        notes=ex_data.get("focus")
                    ))
            
            duration = len(exercises) * 5 + 10
            
            workout_days.append(WorkoutDay(
                name=f"Treino {chr(65 + i)} - {template['name']}",
                day=DAYS[i] if i < 7 else f"Dia {i + 1}",
                duration=duration,
                exercises=exercises
            ))
        
        # VERIFICAÇÃO FINAL: garante que temos EXATAMENTE frequency treinos
        assert len(workout_days) == frequency, f"Erro: gerou {len(workout_days)}, esperado {frequency}"
        
        split_name = {
            1: "Full Body",
            2: "Full Body A/B",
            3: "Push/Pull/Legs",
            4: "Upper/Lower",
            5: "ABCDE",
            6: "PPL 2x",
            7: "Bro Split"
        }.get(frequency, "Personalizado")
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=level,
            goal=goal,
            weekly_frequency=frequency,
            workout_days=workout_days,
            notes=f"Split {split_name} - {frequency}x/semana. Aumente cargas progressivamente."
        )
