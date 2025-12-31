"""
Sistema de Geração de Treino com IA
Utiliza Emergent LLM Key para gerar planos de treino personalizados

REGRAS DE NEGÓCIO OBRIGATÓRIAS:
1. O número de sessões de treino DEVE ser EXATAMENTE igual ao training_frequency do usuário
2. Cada sessão deve ser distinta, sem duplicatas
3. O split deve ser adequado ao nível e objetivo do usuário
4. Splits pré-definidos garantem consistência
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
    """Modelo de um exercício"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    muscle_group: str
    sets: int
    reps: str  # Ex: "8-12", "12-15", "até a falha"
    rest: str  # Ex: "60s", "90s", "2min"
    notes: Optional[str] = None

class WorkoutDay(BaseModel):
    """Modelo de um dia de treino"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Ex: "Treino A - Peito/Tríceps"
    day: str  # Ex: "Segunda", "Terça"
    exercises: List[Exercise]
    duration: int  # Tempo estimado em minutos

class WorkoutPlan(BaseModel):
    """Plano de treino completo"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    training_level: str
    goal: str
    weekly_frequency: int
    workout_days: List[WorkoutDay]
    notes: Optional[str] = None

class WorkoutGenerateRequest(BaseModel):
    """Request para gerar treino"""
    user_id: str

# ==================== BANCO DE EXERCÍCIOS ====================

EXERCISE_DATABASE = {
    "peito": [
        {"name": "Supino Reto com Barra", "focus": "Peitoral médio", "equipment": "Barra"},
        {"name": "Supino Inclinado com Halteres", "focus": "Peitoral superior", "equipment": "Halteres"},
        {"name": "Crucifixo Inclinado", "focus": "Abertura peitoral superior", "equipment": "Halteres"},
        {"name": "Flexão de Braço", "focus": "Peitoral geral", "equipment": "Peso corporal"},
        {"name": "Cross Over (Polia Alta)", "focus": "Definição peitoral", "equipment": "Polia"},
        {"name": "Supino Declinado", "focus": "Peitoral inferior", "equipment": "Barra"},
    ],
    "costas": [
        {"name": "Barra Fixa", "focus": "Dorsais", "equipment": "Peso corporal"},
        {"name": "Remada Curvada com Barra", "focus": "Dorsais/Trapézio", "equipment": "Barra"},
        {"name": "Remada Cavalinho", "focus": "Dorsais médios", "equipment": "Máquina"},
        {"name": "Pulldown (Puxada Frontal)", "focus": "Dorsais", "equipment": "Polia"},
        {"name": "Levantamento Terra", "focus": "Costas completa/Posterior", "equipment": "Barra"},
        {"name": "Remada Unilateral com Halter", "focus": "Dorsais", "equipment": "Halteres"},
    ],
    "pernas_quadriceps": [
        {"name": "Agachamento Livre", "focus": "Quadríceps/Glúteos", "equipment": "Barra"},
        {"name": "Leg Press 45°", "focus": "Quadríceps/Glúteos", "equipment": "Máquina"},
        {"name": "Cadeira Extensora", "focus": "Quadríceps", "equipment": "Máquina"},
        {"name": "Afundo com Halteres", "focus": "Quadríceps/Glúteos", "equipment": "Halteres"},
        {"name": "Hack Squat", "focus": "Quadríceps", "equipment": "Máquina"},
    ],
    "pernas_posterior": [
        {"name": "Mesa Flexora", "focus": "Posterior de coxa", "equipment": "Máquina"},
        {"name": "Stiff", "focus": "Posterior de coxa/Glúteos", "equipment": "Barra/Halteres"},
        {"name": "Cadeira Flexora", "focus": "Posterior de coxa", "equipment": "Máquina"},
        {"name": "Elevação Pélvica", "focus": "Glúteos", "equipment": "Barra"},
    ],
    "panturrilhas": [
        {"name": "Panturrilha em Pé", "focus": "Panturrilhas", "equipment": "Máquina"},
        {"name": "Panturrilha Sentado", "focus": "Sóleo", "equipment": "Máquina"},
    ],
    "ombros": [
        {"name": "Desenvolvimento com Barra", "focus": "Deltoides anterior/médio", "equipment": "Barra"},
        {"name": "Desenvolvimento com Halteres", "focus": "Deltoides", "equipment": "Halteres"},
        {"name": "Elevação Lateral", "focus": "Deltoide médio", "equipment": "Halteres"},
        {"name": "Elevação Frontal", "focus": "Deltoide anterior", "equipment": "Halteres/Anilha"},
        {"name": "Crucifixo Inverso", "focus": "Deltoide posterior", "equipment": "Halteres"},
        {"name": "Face Pull", "focus": "Deltoide posterior/Trapézio", "equipment": "Polia"},
    ],
    "biceps": [
        {"name": "Rosca Direta com Barra", "focus": "Bíceps geral", "equipment": "Barra"},
        {"name": "Rosca Alternada com Halteres", "focus": "Bíceps", "equipment": "Halteres"},
        {"name": "Rosca Martelo", "focus": "Bíceps/Antebraço", "equipment": "Halteres"},
        {"name": "Rosca Scott", "focus": "Pico do bíceps", "equipment": "Barra W"},
        {"name": "Rosca Concentrada", "focus": "Bíceps", "equipment": "Halteres"},
    ],
    "triceps": [
        {"name": "Tríceps Testa com Barra", "focus": "Tríceps", "equipment": "Barra"},
        {"name": "Tríceps Corda (Polia)", "focus": "Tríceps lateral", "equipment": "Polia"},
        {"name": "Mergulho em Paralelas", "focus": "Tríceps geral", "equipment": "Peso corporal"},
        {"name": "Tríceps Coice com Halteres", "focus": "Tríceps", "equipment": "Halteres"},
        {"name": "Tríceps Francês", "focus": "Cabeça longa", "equipment": "Halteres"},
    ],
    "abdomen": [
        {"name": "Abdominal Supra", "focus": "Reto abdominal", "equipment": "Peso corporal"},
        {"name": "Prancha Isométrica", "focus": "Core completo", "equipment": "Peso corporal"},
        {"name": "Abdominal Bicicleta", "focus": "Oblíquos", "equipment": "Peso corporal"},
        {"name": "Elevação de Pernas", "focus": "Reto abdominal inferior", "equipment": "Peso corporal"},
        {"name": "Abdominal na Polia", "focus": "Reto abdominal", "equipment": "Polia"},
    ],
}

# ==================== SPLITS PRÉ-DEFINIDOS ====================

DAYS_OF_WEEK = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

def get_split_templates():
    """Retorna templates de splits para cada frequência semanal"""
    return {
        # 2x/semana - Full Body
        2: [
            {
                "name": "Full Body A",
                "focus": ["peito", "costas", "pernas_quadriceps", "ombros", "abdomen"],
                "exercises_per_group": 2
            },
            {
                "name": "Full Body B", 
                "focus": ["peito", "costas", "pernas_posterior", "biceps", "triceps"],
                "exercises_per_group": 2
            },
        ],
        # 3x/semana - Push/Pull/Legs
        3: [
            {
                "name": "Push (Empurrar)",
                "focus": ["peito", "ombros", "triceps"],
                "exercises_per_group": 3
            },
            {
                "name": "Pull (Puxar)",
                "focus": ["costas", "biceps", "abdomen"],
                "exercises_per_group": 3
            },
            {
                "name": "Legs (Pernas)",
                "focus": ["pernas_quadriceps", "pernas_posterior", "panturrilhas"],
                "exercises_per_group": 3
            },
        ],
        # 4x/semana - Upper/Lower
        4: [
            {
                "name": "Upper A (Superior)",
                "focus": ["peito", "costas", "ombros"],
                "exercises_per_group": 3
            },
            {
                "name": "Lower A (Inferior)",
                "focus": ["pernas_quadriceps", "pernas_posterior", "panturrilhas", "abdomen"],
                "exercises_per_group": 2
            },
            {
                "name": "Upper B (Superior)",
                "focus": ["peito", "costas", "biceps", "triceps"],
                "exercises_per_group": 2
            },
            {
                "name": "Lower B (Inferior)",
                "focus": ["pernas_quadriceps", "pernas_posterior", "panturrilhas", "abdomen"],
                "exercises_per_group": 2
            },
        ],
        # 5x/semana - ABCDE (Split por grupo muscular)
        5: [
            {
                "name": "Peito/Tríceps",
                "focus": ["peito", "triceps"],
                "exercises_per_group": 4
            },
            {
                "name": "Costas/Bíceps",
                "focus": ["costas", "biceps"],
                "exercises_per_group": 4
            },
            {
                "name": "Pernas Quadríceps",
                "focus": ["pernas_quadriceps", "panturrilhas"],
                "exercises_per_group": 4
            },
            {
                "name": "Ombros/Abdômen",
                "focus": ["ombros", "abdomen"],
                "exercises_per_group": 4
            },
            {
                "name": "Pernas Posterior/Glúteos",
                "focus": ["pernas_posterior", "pernas_quadriceps"],
                "exercises_per_group": 4
            },
        ],
        # 6x/semana - Push/Pull/Legs 2x
        6: [
            {
                "name": "Push A (Peito foco)",
                "focus": ["peito", "ombros", "triceps"],
                "exercises_per_group": 3
            },
            {
                "name": "Pull A (Costas foco)",
                "focus": ["costas", "biceps"],
                "exercises_per_group": 4
            },
            {
                "name": "Legs A (Quadríceps foco)",
                "focus": ["pernas_quadriceps", "panturrilhas", "abdomen"],
                "exercises_per_group": 3
            },
            {
                "name": "Push B (Ombros foco)",
                "focus": ["ombros", "peito", "triceps"],
                "exercises_per_group": 3
            },
            {
                "name": "Pull B (Espessura costas)",
                "focus": ["costas", "biceps", "abdomen"],
                "exercises_per_group": 3
            },
            {
                "name": "Legs B (Posterior foco)",
                "focus": ["pernas_posterior", "pernas_quadriceps", "panturrilhas"],
                "exercises_per_group": 3
            },
        ],
        # 7x/semana - Bro Split + Cardio
        7: [
            {
                "name": "Peito",
                "focus": ["peito"],
                "exercises_per_group": 5
            },
            {
                "name": "Costas",
                "focus": ["costas"],
                "exercises_per_group": 5
            },
            {
                "name": "Ombros",
                "focus": ["ombros", "abdomen"],
                "exercises_per_group": 4
            },
            {
                "name": "Quadríceps/Panturrilhas",
                "focus": ["pernas_quadriceps", "panturrilhas"],
                "exercises_per_group": 4
            },
            {
                "name": "Posterior/Glúteos",
                "focus": ["pernas_posterior"],
                "exercises_per_group": 5
            },
            {
                "name": "Braços",
                "focus": ["biceps", "triceps"],
                "exercises_per_group": 4
            },
            {
                "name": "Cardio/Funcional/Abdômen",
                "focus": ["abdomen"],
                "exercises_per_group": 5
            },
        ],
    }

# ==================== SERVIÇO DE IA ====================

class WorkoutAIService:
    """Serviço de geração de treinos com IA"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.llm = LlmChat(
            api_key=self.api_key,
            session_id="workout_generation",
            system_message="Você é um personal trainer especializado em musculação. Sempre responda em JSON válido."
        )
    
    def generate_workout_plan(self, user_profile: Dict) -> WorkoutPlan:
        """
        Gera um plano de treino personalizado
        REGRA: O número de sessões DEVE ser EXATAMENTE igual ao weekly_training_frequency
        """
        weekly_frequency = user_profile.get('weekly_training_frequency', 4)
        training_level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        
        # Valida frequência (1-7)
        weekly_frequency = max(1, min(7, weekly_frequency))
        
        # Frequência 1 é tratada como 2 (Full Body 2x por semana, fazendo um por semana)
        if weekly_frequency == 1:
            weekly_frequency = 2
            # Mas retornamos apenas 1 treino
            workout_plan = self._generate_deterministic_plan(user_profile['id'], 2, training_level, goal)
            workout_plan.workout_days = workout_plan.workout_days[:1]
            workout_plan.weekly_frequency = 1
            workout_plan.notes = "Treino Full Body. Para melhores resultados, considere aumentar para 2-3x/semana."
            return workout_plan
        
        try:
            # Tenta gerar com IA primeiro
            prompt = self._build_workout_prompt(user_profile, weekly_frequency)
            user_message = UserMessage(text=prompt)
            
            response = self.llm.chat(
                user_messages=[user_message],
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=3000
            )
            
            workout_data = self._parse_ai_response(response, user_profile['id'], user_profile)
            
            # Valida se tem o número correto de treinos
            if len(workout_data.workout_days) == weekly_frequency:
                return workout_data
            else:
                print(f"IA gerou {len(workout_data.workout_days)} treinos em vez de {weekly_frequency}. Usando fallback.")
                return self._generate_deterministic_plan(user_profile['id'], weekly_frequency, training_level, goal)
                
        except Exception as e:
            print(f"Erro ao gerar treino com IA: {e}")
            return self._generate_deterministic_plan(user_profile['id'], weekly_frequency, training_level, goal)
    
    def _build_workout_prompt(self, user_profile: Dict, weekly_frequency: int) -> str:
        """Constrói prompt para a IA com RESTRIÇÕES ESTRITAS"""
        
        training_level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        available_time = user_profile.get('available_time_per_session', 60)
        injuries = user_profile.get('injury_history', [])
        injuries_text = ", ".join(injuries) if injuries else "Nenhuma"
        
        # Sugere split baseado na frequência
        split_suggestion = {
            2: "Full Body A/B",
            3: "Push/Pull/Legs",
            4: "Upper/Lower 2x",
            5: "ABCDE (divisão por grupos)",
            6: "Push/Pull/Legs 2x",
            7: "Bro Split + Cardio"
        }
        
        prompt = f"""
Crie um plano de treino semanal para musculação.

====== RESTRIÇÃO OBRIGATÓRIA (NÃO NEGOCIÁVEL) ======

FREQUÊNCIA SEMANAL EXATA: {weekly_frequency}x por semana
VOCÊ DEVE GERAR EXATAMENTE {weekly_frequency} TREINOS DIFERENTES
NÃO GERE MAIS NEM MENOS QUE {weekly_frequency} TREINOS

====== PERFIL DO ATLETA ======
- Nível: {training_level}
- Objetivo: {goal}
- Tempo por Treino: {available_time} minutos
- Histórico de Lesões: {injuries_text}

====== SPLIT SUGERIDO ======
Para {weekly_frequency}x/semana, use: {split_suggestion.get(weekly_frequency, "Divisão personalizada")}

====== BANCO DE EXERCÍCIOS DISPONÍVEIS ======
{json.dumps(EXERCISE_DATABASE, indent=2, ensure_ascii=False)}

====== INSTRUÇÕES ======
1. Crie EXATAMENTE {weekly_frequency} treinos diferentes
2. Use APENAS exercícios do banco fornecido
3. Cada treino deve ter nome descritivo (ex: "Treino A - Push" ou "Peito/Tríceps")
4. Para cada exercício, defina:
   - Séries (3-5 conforme nível)
   - Repetições (ex: "8-12", "12-15")
   - Descanso (ex: "60s", "90s", "2min")
5. Ajuste volume ao nível:
   - Iniciante: 3-4 exercícios por grupo, 3 séries
   - Intermediário: 4-5 exercícios, 3-4 séries
   - Avançado: 5-6 exercícios, 4-5 séries

====== FORMATO DE RESPOSTA (JSON APENAS) ======
{{
  "workout_days": [
    {{
      "name": "Treino A - Push",
      "day": "Segunda",
      "duration": {available_time},
      "exercises": [
        {{
          "name": "Supino Reto com Barra",
          "muscle_group": "Peito",
          "sets": 4,
          "reps": "8-12",
          "rest": "90s",
          "notes": "Foco em progressão de carga"
        }}
      ]
    }}
  ]
}}

LEMBRE-SE: Gere EXATAMENTE {weekly_frequency} treinos!
Responda APENAS com o JSON, sem texto adicional.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, user_id: str, user_profile: Dict) -> WorkoutPlan:
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
            
            workout_days = []
            for day_data in data.get('workout_days', []):
                exercises = []
                for ex_data in day_data.get('exercises', []):
                    exercise = Exercise(
                        name=ex_data.get('name', 'Exercício'),
                        muscle_group=ex_data.get('muscle_group', 'Geral'),
                        sets=ex_data.get('sets', 3),
                        reps=ex_data.get('reps', '10-12'),
                        rest=ex_data.get('rest', '60s'),
                        notes=ex_data.get('notes')
                    )
                    exercises.append(exercise)
                
                workout_day = WorkoutDay(
                    name=day_data.get('name', 'Treino'),
                    day=day_data.get('day', ''),
                    duration=day_data.get('duration', 60),
                    exercises=exercises
                )
                workout_days.append(workout_day)
            
            weekly_frequency = user_profile.get('weekly_training_frequency', len(workout_days))
            
            return WorkoutPlan(
                user_id=user_id,
                training_level=user_profile.get('training_level', 'intermediario'),
                goal=user_profile.get('goal', 'bulking'),
                weekly_frequency=weekly_frequency,
                workout_days=workout_days,
                notes="Plano gerado com IA. Ajuste cargas e volumes conforme sua evolução."
            )
            
        except Exception as e:
            print(f"Erro ao fazer parse da resposta da IA: {e}")
            raise
    
    def _generate_deterministic_plan(
        self,
        user_id: str,
        weekly_frequency: int,
        training_level: str,
        goal: str
    ) -> WorkoutPlan:
        """
        Gera treino determinístico que respeita EXATAMENTE a frequência selecionada
        """
        
        # Obtém o template de split para esta frequência
        split_templates = get_split_templates()
        templates = split_templates.get(weekly_frequency, split_templates[4])  # Default para 4x
        
        # Configurações baseadas no nível
        level_config = {
            "iniciante": {"sets": 3, "reps": "12-15", "rest": "90s"},
            "intermediario": {"sets": 4, "reps": "10-12", "rest": "75s"},
            "avancado": {"sets": 4, "reps": "8-12", "rest": "60s"}
        }
        config = level_config.get(training_level, level_config["intermediario"])
        
        workout_days = []
        
        for i, template in enumerate(templates):
            exercises = []
            
            for muscle_group in template["focus"]:
                # Obtém exercícios para este grupo muscular
                available_exercises = EXERCISE_DATABASE.get(muscle_group, [])
                
                # Seleciona quantidade de exercícios baseado no template
                num_exercises = min(template["exercises_per_group"], len(available_exercises))
                
                for j in range(num_exercises):
                    if j < len(available_exercises):
                        ex_data = available_exercises[j]
                        exercise = Exercise(
                            name=ex_data["name"],
                            muscle_group=muscle_group.replace("pernas_", "").replace("_", " ").title(),
                            sets=config["sets"],
                            reps=config["reps"],
                            rest=config["rest"],
                            notes=ex_data.get("focus")
                        )
                        exercises.append(exercise)
            
            # Calcula duração estimada
            duration = len(exercises) * 5 + 10  # ~5 min por exercício + aquecimento
            
            workout_day = WorkoutDay(
                name=f"Treino {chr(65 + i)} - {template['name']}",
                day=DAYS_OF_WEEK[i] if i < 7 else f"Dia {i + 1}",
                duration=duration,
                exercises=exercises
            )
            workout_days.append(workout_day)
        
        # Descrição do split
        split_names = {
            2: "Full Body A/B",
            3: "Push/Pull/Legs",
            4: "Upper/Lower 2x",
            5: "ABCDE",
            6: "Push/Pull/Legs 2x",
            7: "Bro Split"
        }
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=training_level,
            goal=goal,
            weekly_frequency=weekly_frequency,
            workout_days=workout_days,
            notes=f"Plano {split_names.get(weekly_frequency, 'personalizado')} com {weekly_frequency}x por semana. Aumente cargas progressivamente."
        )
