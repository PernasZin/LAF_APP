"""
Sistema de Geração de Treino com IA
Utiliza Emergent LLM Key para gerar planos de treino personalizados
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

# ==================== BANCO DE EXERCÍCIOS BRASILEIROS ====================

EXERCISE_DATABASE = {
    # Peito
    "peito": [
        {"name": "Supino Reto com Barra", "focus": "Peitoral médio", "equipment": "Barra"},
        {"name": "Supino Inclinado com Halteres", "focus": "Peitoral superior", "equipment": "Halteres"},
        {"name": "Crucifixo Inclinado", "focus": "Abertura peitoral superior", "equipment": "Halteres"},
        {"name": "Flexão de Braço", "focus": "Peitoral geral", "equipment": "Peso corporal"},
        {"name": "Cross Over (Polia Alta)", "focus": "Definição peitoral", "equipment": "Polia"},
    ],
    # Costas
    "costas": [
        {"name": "Barra Fixa", "focus": "Dorsais", "equipment": "Peso corporal"},
        {"name": "Remada Curvada com Barra", "focus": "Dorsais/Trapézio", "equipment": "Barra"},
        {"name": "Remada Cavalinho", "focus": "Dorsais médios", "equipment": "Polia"},
        {"name": "Pulldown (Puxada Frontal)", "focus": "Dorsais", "equipment": "Polia"},
        {"name": "Levantamento Terra", "focus": "Costas completa/Posterior", "equipment": "Barra"},
    ],
    # Pernas
    "pernas": [
        {"name": "Agachamento Livre", "focus": "Quadríceps/Glúteos", "equipment": "Barra"},
        {"name": "Leg Press 45°", "focus": "Quadríceps/Glúteos", "equipment": "Máquina"},
        {"name": "Cadeira Extensora", "focus": "Quadríceps", "equipment": "Máquina"},
        {"name": "Mesa Flexora", "focus": "Posterior de coxa", "equipment": "Máquina"},
        {"name": "Stiff", "focus": "Posterior de coxa/Glúteos", "equipment": "Barra/Halteres"},
        {"name": "Panturrilha em Pé", "focus": "Panturrilhas", "equipment": "Máquina"},
        {"name": "Afundo com Halteres", "focus": "Quadríceps/Glúteos", "equipment": "Halteres"},
    ],
    # Ombros
    "ombros": [
        {"name": "Desenvolvimento com Barra", "focus": "Deltoides anterior/médio", "equipment": "Barra"},
        {"name": "Desenvolvimento com Halteres", "focus": "Deltoides", "equipment": "Halteres"},
        {"name": "Elevação Lateral", "focus": "Deltoide médio", "equipment": "Halteres"},
        {"name": "Elevação Frontal", "focus": "Deltoide anterior", "equipment": "Halteres/Anilha"},
        {"name": "Crucifixo Inverso", "focus": "Deltoide posterior", "equipment": "Halteres"},
    ],
    # Bíceps
    "biceps": [
        {"name": "Rosca Direta com Barra", "focus": "Bíceps geral", "equipment": "Barra"},
        {"name": "Rosca Alternada com Halteres", "focus": "Bíceps", "equipment": "Halteres"},
        {"name": "Rosca Martelo", "focus": "Bíceps/Antebraço", "equipment": "Halteres"},
        {"name": "Rosca Scott", "focus": "Pico do bíceps", "equipment": "Barra W"},
    ],
    # Tríceps
    "triceps": [
        {"name": "Tríceps Testa com Barra", "focus": "Tríceps", "equipment": "Barra"},
        {"name": "Tríceps Corda (Polia)", "focus": "Tríceps lateral", "equipment": "Polia"},
        {"name": "Mergulho em Paralelas", "focus": "Tríceps geral", "equipment": "Peso corporal"},
        {"name": "Tríceps Coice com Halteres", "focus": "Tríceps", "equipment": "Halteres"},
    ],
    # Abdômen
    "abdomen": [
        {"name": "Abdominal Supra", "focus": "Reto abdominal", "equipment": "Peso corporal"},
        {"name": "Prancha Isométrica", "focus": "Core completo", "equipment": "Peso corporal"},
        {"name": "Abdominal Bicicleta", "focus": "Oblíquos", "equipment": "Peso corporal"},
        {"name": "Elevação de Pernas", "focus": "Reto abdominal inferior", "equipment": "Peso corporal"},
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
    
    def generate_workout_plan(
        self, 
        user_profile: Dict
    ) -> WorkoutPlan:
        """
        Gera um plano de treino personalizado usando IA
        """
        try:
            # Monta prompt para a IA
            prompt = self._build_workout_prompt(user_profile)
            
            # Chama a IA
            user_message = UserMessage(text=prompt)
            
            response = self.llm.chat(
                user_messages=[user_message],
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=2500
            )
            
            # Parse da resposta
            workout_data = self._parse_ai_response(response, user_profile['id'])
            
            return workout_data
            
        except Exception as e:
            print(f"Erro ao gerar treino com IA: {e}")
            # Fallback: gera treino básico
            return self._generate_fallback_workout(user_profile['id'], user_profile)
    
    def _build_workout_prompt(self, user_profile: Dict) -> str:
        """Constrói prompt para a IA"""
        
        training_level = user_profile.get('training_level', 'intermediario')
        goal = user_profile.get('goal', 'bulking')
        weekly_frequency = user_profile.get('weekly_training_frequency', 4)
        available_time = user_profile.get('available_time_per_session', 60)
        injuries = user_profile.get('injury_history', [])
        
        injuries_text = ", ".join(injuries) if injuries else "Nenhuma"
        
        prompt = f"""
Crie um plano de treino semanal para musculação.

**Perfil do Atleta:**
- Nível: {training_level}
- Objetivo: {goal}
- Frequência Semanal: {weekly_frequency}x por semana
- Tempo Disponível: {available_time} minutos por treino
- Histórico de Lesões: {injuries_text}

**Banco de Exercícios Disponíveis:**
{json.dumps(EXERCISE_DATABASE, indent=2, ensure_ascii=False)}

**Instruções:**
1. Crie {weekly_frequency} treinos diferentes (divisão adequada ao nível)
2. Use APENAS exercícios do banco fornecido
3. Para cada exercício, defina:
   - Séries (3-5 séries conforme nível)
   - Repetições (ex: "8-12", "12-15")
   - Descanso entre séries (ex: "60s", "90s", "2min")
4. Distribuição recomendada:
   - 3x/semana: ABC (Push/Pull/Legs) ou Full Body
   - 4x/semana: ABCD ou Upper/Lower
   - 5x/semana: ABCDE (divisão por grupos musculares)
   - 6x/semana: Push/Pull/Legs 2x
5. Ajuste volume e intensidade ao nível:
   - Iniciante: 3-4 exercícios por grupo, 3 séries, descanso maior
   - Intermediário: 4-5 exercícios, 3-4 séries, descanso moderado
   - Avançado: 5-6 exercícios, 4-5 séries, descanso menor
6. Considere lesões ao escolher exercícios

**Formato de Resposta (JSON):**
{{
  "workout_days": [
    {{
      "name": "Treino A - Peito/Tríceps",
      "day": "Segunda",
      "duration": 60,
      "exercises": [
        {{
          "name": "Supino Reto com Barra",
          "muscle_group": "Peito",
          "sets": 4,
          "reps": "8-12",
          "rest": "90s",
          "notes": "Exercício composto - foco em progressão de carga"
        }}
      ]
    }}
  ]
}}

Responda APENAS com o JSON, sem texto adicional.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, user_id: str) -> WorkoutPlan:
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
            
            # Pega dados do user_profile para completar
            from server import db
            import asyncio
            
            async def get_profile():
                return await db.user_profiles.find_one({"_id": user_id})
            
            try:
                loop = asyncio.get_event_loop()
                user_profile = loop.run_until_complete(get_profile())
            except:
                user_profile = {}
            
            return WorkoutPlan(
                user_id=user_id,
                training_level=user_profile.get('training_level', 'intermediario'),
                goal=user_profile.get('goal', 'bulking'),
                weekly_frequency=user_profile.get('weekly_training_frequency', len(workout_days)),
                workout_days=workout_days,
                notes="Plano gerado com IA. Ajuste cargas e volumes conforme sua evolução."
            )
            
        except Exception as e:
            print(f"Erro ao fazer parse da resposta da IA: {e}")
            raise
    
    def _generate_fallback_workout(self, user_id: str, user_profile: Dict) -> WorkoutPlan:
        """Gera treino básico que respeita EXATAMENTE a frequência semanal escolhida"""
        
        weekly_frequency = user_profile.get('weekly_training_frequency', 4)
        training_level = user_profile.get('training_level', 'intermediario')
        
        # Define TODOS os treinos possíveis (até 7 dias)
        all_possible_workouts = [
            WorkoutDay(
                name="Treino A - Peito/Tríceps",
                day="Segunda",
                duration=60,
                exercises=[
                    Exercise(name="Supino Reto com Barra", muscle_group="Peito", sets=4, reps="8-12", rest="90s", notes="Exercício base"),
                    Exercise(name="Supino Inclinado com Halteres", muscle_group="Peito", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Crucifixo Inclinado", muscle_group="Peito", sets=3, reps="12-15", rest="60s"),
                    Exercise(name="Tríceps Testa com Barra", muscle_group="Tríceps", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Tríceps Corda (Polia)", muscle_group="Tríceps", sets=3, reps="12-15", rest="45s"),
                ]
            ),
            WorkoutDay(
                name="Treino B - Costas/Bíceps",
                day="Terça",
                duration=60,
                exercises=[
                    Exercise(name="Barra Fixa", muscle_group="Costas", sets=4, reps="máximo", rest="90s", notes="Assistida se necessário"),
                    Exercise(name="Remada Curvada com Barra", muscle_group="Costas", sets=4, reps="8-12", rest="90s"),
                    Exercise(name="Pulldown (Puxada Frontal)", muscle_group="Costas", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Rosca Direta com Barra", muscle_group="Bíceps", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Rosca Martelo", muscle_group="Bíceps", sets=3, reps="12-15", rest="45s"),
                ]
            ),
            WorkoutDay(
                name="Treino C - Pernas/Ombros",
                day="Quarta",
                duration=70,
                exercises=[
                    Exercise(name="Agachamento Livre", muscle_group="Pernas", sets=4, reps="8-12", rest="2min", notes="Exercício base"),
                    Exercise(name="Leg Press 45°", muscle_group="Pernas", sets=3, reps="12-15", rest="90s"),
                    Exercise(name="Cadeira Extensora", muscle_group="Pernas", sets=3, reps="12-15", rest="60s"),
                    Exercise(name="Mesa Flexora", muscle_group="Pernas", sets=3, reps="12-15", rest="60s"),
                    Exercise(name="Desenvolvimento com Halteres", muscle_group="Ombros", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Elevação Lateral", muscle_group="Ombros", sets=3, reps="12-15", rest="45s"),
                ]
            ),
            WorkoutDay(
                name="Treino D - Posterior/Abdômen",
                day="Quinta",
                duration=50,
                exercises=[
                    Exercise(name="Stiff", muscle_group="Posterior", sets=4, reps="10-12", rest="90s"),
                    Exercise(name="Afundo com Halteres", muscle_group="Pernas", sets=3, reps="12 cada", rest="60s"),
                    Exercise(name="Panturrilha em Pé", muscle_group="Panturrilhas", sets=4, reps="15-20", rest="45s"),
                    Exercise(name="Abdominal Supra", muscle_group="Abdômen", sets=3, reps="15-20", rest="30s"),
                    Exercise(name="Prancha Isométrica", muscle_group="Core", sets=3, reps="60s", rest="60s"),
                ]
            ),
            WorkoutDay(
                name="Treino E - Pernas Completo",
                day="Sexta",
                duration=65,
                exercises=[
                    Exercise(name="Agachamento Livre", muscle_group="Pernas", sets=4, reps="8-12", rest="2min"),
                    Exercise(name="Stiff", muscle_group="Posterior", sets=3, reps="10-12", rest="90s"),
                    Exercise(name="Leg Press 45°", muscle_group="Pernas", sets=3, reps="12-15", rest="90s"),
                    Exercise(name="Mesa Flexora", muscle_group="Posterior", sets=3, reps="12-15", rest="60s"),
                    Exercise(name="Panturrilha em Pé", muscle_group="Panturrilhas", sets=4, reps="15-20", rest="45s"),
                ]
            ),
            WorkoutDay(
                name="Treino F - Peito/Costas",
                day="Sábado",
                duration=65,
                exercises=[
                    Exercise(name="Supino Reto com Barra", muscle_group="Peito", sets=4, reps="8-12", rest="90s"),
                    Exercise(name="Remada Curvada com Barra", muscle_group="Costas", sets=4, reps="8-12", rest="90s"),
                    Exercise(name="Crucifixo Inclinado", muscle_group="Peito", sets=3, reps="12-15", rest="60s"),
                    Exercise(name="Pulldown (Puxada Frontal)", muscle_group="Costas", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Flexão de Braço", muscle_group="Peito", sets=3, reps="máximo", rest="45s"),
                ]
            ),
            WorkoutDay(
                name="Treino G - Ombros/Braços/Abdômen",
                day="Domingo",
                duration=55,
                exercises=[
                    Exercise(name="Desenvolvimento com Barra", muscle_group="Ombros", sets=4, reps="8-12", rest="90s"),
                    Exercise(name="Elevação Lateral", muscle_group="Ombros", sets=3, reps="12-15", rest="60s"),
                    Exercise(name="Rosca Direta com Barra", muscle_group="Bíceps", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Tríceps Testa com Barra", muscle_group="Tríceps", sets=3, reps="10-12", rest="60s"),
                    Exercise(name="Abdominal Supra", muscle_group="Abdômen", sets=3, reps="15-20", rest="30s"),
                ]
            ),
        ]
        
        # Retorna EXATAMENTE o número de treinos solicitado
        selected_workouts = all_possible_workouts[:weekly_frequency]
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=training_level,
            goal=user_profile.get('goal', 'bulking'),
            weekly_frequency=weekly_frequency,
            workout_days=selected_workouts,
            notes=f"Plano de {weekly_frequency}x por semana gerado automaticamente. Aumente cargas progressivamente a cada treino."
        )
