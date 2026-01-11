"""
Sistema de Geração de Treino - V6 SAFE MACHINES
===============================================
REGRAS DE SEGURANÇA:
- Apenas MÁQUINAS e CABOS (polias)
- Halteres apenas quando estritamente necessário
- SEM barras, levantamentos olímpicos ou movimentos instáveis
- Prioridade: segurança, estabilidade, execução controlada
- Instruções claras em texto para cada exercício
===============================================
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
    notes: Optional[str] = None
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


# ==================== EXERCÍCIOS SEGUROS (MÁQUINAS + CABOS + HALTERES) ====================
# REGRA: Priorizar máquinas e cabos. Halteres apenas quando necessário.
# SEM: Barras, levantamentos olímpicos, movimentos instáveis

EXERCISES = {
    # ============ PEITO ============
    "peito": [
        {
            "name": "Supino na Máquina",
            "notes": "Sente com costas apoiadas. Empurre as manoplas para frente até extensão quase completa. Retorne controlado sem bater os pesos."
        },
        {
            "name": "Crucifixo na Máquina (Peck Deck)",
            "notes": "Cotovelos na altura dos ombros. Junte os braços à frente contraindo o peitoral. Abra controlado até sentir leve alongamento."
        },
        {
            "name": "Cross Over (Polia Alta)",
            "notes": "Cabos na posição alta. Dê um passo à frente. Puxe os cabos para baixo e para frente, cruzando na frente do corpo. Volte controlado."
        },
        {
            "name": "Supino Inclinado com Halteres",
            "notes": "Banco a 30°. Halteres ao lado do peito. Empurre para cima sem bater os halteres no topo. Desça controlado até cotovelos a 90°."
        },
    ],
    
    # ============ COSTAS ============
    "costas": [
        {
            "name": "Puxada Frontal (Pulley)",
            "notes": "Pegada um pouco mais larga que os ombros. Puxe a barra até a altura do queixo, levando os cotovelos para baixo e para trás. Retorne controlado."
        },
        {
            "name": "Remada na Máquina (Sentado)",
            "notes": "Peito apoiado no suporte. Puxe as manoplas em direção ao abdômen, contraindo as escápulas. Retorne estendendo completamente os braços."
        },
        {
            "name": "Remada Baixa (Polia)",
            "notes": "Sente com pernas levemente flexionadas. Puxe o triângulo até o abdômen, mantendo costas retas. Estenda os braços completamente na volta."
        },
        {
            "name": "Pulldown com Corda (Polia Alta)",
            "notes": "Braços estendidos acima. Puxe a corda até a altura das coxas, mantendo cotovelos próximos ao corpo. Retorne controlado."
        },
    ],
    
    # ============ OMBROS ============
    "ombros": [
        {
            "name": "Desenvolvimento na Máquina",
            "notes": "Sente com costas totalmente apoiadas. Empurre as manoplas para cima até quase estender os cotovelos. Desça até a altura das orelhas."
        },
        {
            "name": "Elevação Lateral na Máquina",
            "notes": "Cotovelos apoiados nas almofadas. Eleve os braços até a altura dos ombros. Desça controlado sem deixar os pesos baterem."
        },
        {
            "name": "Elevação Lateral com Halteres (Sentado)",
            "notes": "Sente no banco para mais estabilidade. Cotovelos levemente flexionados. Eleve até a altura dos ombros. Desça controlado."
        },
        {
            "name": "Face Pull (Polia)",
            "notes": "Polia na altura do rosto. Puxe a corda em direção ao rosto, abrindo os cotovelos para os lados. Aperte as escápulas no final."
        },
    ],
    
    # ============ BÍCEPS ============
    "biceps": [
        {
            "name": "Rosca na Máquina",
            "notes": "Braços apoiados no suporte. Flexione os cotovelos trazendo as manoplas em direção aos ombros. Desça controlado sem estender completamente."
        },
        {
            "name": "Rosca na Polia Baixa",
            "notes": "De frente para a polia baixa. Cotovelos fixos ao lado do corpo. Flexione puxando a barra até os ombros. Desça controlado."
        },
        {
            "name": "Rosca Alternada com Halteres (Sentado)",
            "notes": "Sente no banco com costas apoiadas. Alterne os braços. Gire o punho (supinação) durante a subida. Desça controlado."
        },
        {
            "name": "Rosca Martelo com Halteres (Sentado)",
            "notes": "Pegada neutra (palmas voltadas para dentro). Cotovelos fixos. Flexione até contrair o bíceps. Desça controlado."
        },
    ],
    
    # ============ TRÍCEPS ============
    "triceps": [
        {
            "name": "Tríceps na Polia (Corda)",
            "notes": "Cotovelos fixos ao lado do corpo. Estenda os braços completamente, abrindo a corda no final. Retorne até 90° nos cotovelos."
        },
        {
            "name": "Tríceps na Polia (Barra Reta)",
            "notes": "Pegada pronada na barra. Cotovelos fixos. Empurre a barra para baixo até extensão completa. Retorne controlado até 90°."
        },
        {
            "name": "Tríceps na Máquina",
            "notes": "Sente com costas apoiadas. Empurre as manoplas para baixo estendendo os cotovelos. Retorne controlado sem deixar pesos baterem."
        },
        {
            "name": "Tríceps Francês com Halter (Sentado)",
            "notes": "Sente no banco. Segure um halter acima da cabeça com as duas mãos. Desça atrás da cabeça. Estenda sem mover os cotovelos."
        },
    ],
    
    # ============ QUADRÍCEPS ============
    "quadriceps": [
        {
            "name": "Leg Press 45°",
            "notes": "Pés no centro da plataforma na largura dos ombros. Desça até 90° nos joelhos. Empurre sem travar os joelhos no topo."
        },
        {
            "name": "Cadeira Extensora",
            "notes": "Ajuste o encosto para joelhos alinhados com o eixo. Estenda as pernas completamente, contraindo no topo. Desça controlado."
        },
        {
            "name": "Agachamento no Smith Machine",
            "notes": "Pés ligeiramente à frente da barra. Desça até coxas paralelas ao chão. Suba empurrando pelos calcanhares. Joelhos alinhados com os pés."
        },
        {
            "name": "Leg Press Horizontal",
            "notes": "Costas totalmente apoiadas. Pés na largura dos ombros. Empurre a plataforma sem travar joelhos. Desça controlado até 90°."
        },
    ],
    
    # ============ POSTERIOR DE COXA ============
    "posterior": [
        {
            "name": "Mesa Flexora",
            "notes": "Deite de bruços com joelhos alinhados ao eixo da máquina. Flexione as pernas trazendo os calcanhares em direção aos glúteos. Desça controlado."
        },
        {
            "name": "Cadeira Flexora (Sentado)",
            "notes": "Sente com coxas apoiadas. Flexione as pernas para baixo e para trás. Contraia no final do movimento. Retorne controlado."
        },
        {
            "name": "Stiff na Máquina Smith",
            "notes": "Pernas semi-estendidas, pés na largura do quadril. Desça a barra deslizando próximo às coxas até sentir alongamento. Suba contraindo glúteos."
        },
        {
            "name": "Glúteo na Máquina (Kick Back)",
            "notes": "Apoie o pé na plataforma. Empurre para trás estendendo o quadril. Contraia o glúteo no topo. Retorne controlado sem deixar peso bater."
        },
    ],
    
    # ============ PANTURRILHA ============
    "panturrilha": [
        {
            "name": "Panturrilha no Leg Press",
            "notes": "Apoie apenas a ponta dos pés na plataforma. Empurre estendendo os tornozelos o máximo possível. Desça alongando bem a panturrilha."
        },
        {
            "name": "Panturrilha Sentado na Máquina",
            "notes": "Joelhos a 90° sob as almofadas. Eleve os calcanhares o máximo possível. Desça controlado até sentir alongamento completo."
        },
        {
            "name": "Panturrilha em Pé na Máquina",
            "notes": "Ombros sob as almofadas. Eleve nos dedos o máximo possível, contraindo no topo. Desça alongando completamente."
        },
    ],
    
    # ============ ABDÔMEN ============
    "abdomen": [
        {
            "name": "Abdominal na Máquina",
            "notes": "Sente e segure as manoplas. Flexione o tronco para frente contraindo o abdômen. Retorne controlado sem soltar a tensão."
        },
        {
            "name": "Abdominal na Polia Alta (Corda)",
            "notes": "Ajoelhe de costas para a polia. Segure a corda atrás da cabeça. Flexione o tronco em direção ao chão. Retorne controlado."
        },
        {
            "name": "Prancha Isométrica",
            "notes": "Apoie antebraços e pontas dos pés no chão. Corpo reto da cabeça aos calcanhares. Mantenha o abdômen contraído. Não deixe o quadril subir ou descer."
        },
        {
            "name": "Elevação de Pernas no Apoio",
            "notes": "Costas apoiadas no suporte, braços nos apoios. Eleve as pernas estendidas até 90°. Desça controlado sem balançar o corpo."
        },
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
        duration = user_profile.get('training_duration', 60)  # Em minutos
        completed_workouts = user_profile.get('completed_workouts', 0)
        
        return self._generate_workout(user_profile['id'], frequency, level, goal, duration, completed_workouts)
    
    def _get_exercises_per_duration(self, duration: int, level: str) -> int:
        """Calcula quantos exercícios cabem no tempo disponível"""
        # Tempo médio por exercício: ~5-7 minutos (incluindo descanso)
        # Aquecimento: ~5 minutos
        # Alongamento final: ~5 minutos
        available_time = duration - 10  # Desconta aquecimento e alongamento
        
        if level == 'novato':
            time_per_exercise = 4  # Menos séries, mais rápido
        elif level == 'avancado':
            time_per_exercise = 7  # Mais séries e descanso
        else:
            time_per_exercise = 5.5
        
        return max(4, int(available_time / time_per_exercise))
    
    def _generate_workout(self, user_id: str, frequency: int, level: str, goal: str, duration: int, completed_workouts: int) -> WorkoutPlan:
        split = get_split_for_frequency(frequency)
        
        # NOVATO: Treino de adaptação nas primeiras 30 sessões
        is_adaptation = level == 'novato' and completed_workouts < 30
        
        # Configurações baseadas no nível
        if is_adaptation:
            # Treino de adaptação para novatos (4-8 semanas)
            config = {
                "sets": 2,
                "reps": "15-20",
                "rest": "60s",
                "ex_per_muscle": 1,
                "machine_only": True,  # 100% máquinas
                "notes_prefix": "⚠️ ADAPTAÇÃO - CARGA LEVE! Foque 100% na execução perfeita do movimento. Não se preocupe com peso ainda. ",
                "general_note": "FASE DE ADAPTAÇÃO: Use cargas LEVES. O objetivo é aprender os movimentos corretamente."
            }
        elif level == 'novato':
            # Novato pós-adaptação (hipertrofia leve)
            config = {
                "sets": 3,
                "reps": "12-15",
                "rest": "90s",
                "ex_per_muscle": 2,
                "machine_only": True,  # 100% máquinas
                "notes_prefix": "",
                "general_note": "Agora pode aumentar as cargas progressivamente. Mantenha a execução correta."
            }
        elif level == 'iniciante':
            # Iniciante (0-1 anos) - Foco em máquinas, alguns livres seguros
            config = {
                "sets": 3,
                "reps": "10-12",
                "rest": "75s",
                "ex_per_muscle": 2,
                "machine_only": False,
                "allow_free_weights": ["elevacao_lateral", "rosca_alternada", "triceps_frances"],  # Livres seguros
                "block_exercises": ["supino_barra", "rosca_direta_barra", "agachamento_livre", "stiff_livre"],
                "notes_prefix": "",
                "general_note": "Foque em aumentar cargas progressivamente mantendo boa execução."
            }
        elif level == 'intermediario':
            # Intermediário (1-2 anos) - Pode usar mais livres
            config = {
                "sets": 4,
                "reps": "8-12",
                "rest": "75s",
                "ex_per_muscle": 2,
                "machine_only": False,
                "allow_free_weights": True,  # Libera maioria dos livres
                "block_exercises": ["supino_barra", "rosca_direta_barra"],  # Ainda bloqueia esses
                "notes_prefix": "💪 Chegue PERTO DA FALHA em pelo menos 1 série. ",
                "general_note": "INTERMEDIÁRIO: Em cada exercício, faça pelo menos 1 série próxima da falha muscular."
            }
        else:  # avancado
            # Avançado (3+ anos) - Estrutura completa com aquecimento e séries válidas
            config = {
                "sets": 4,  # 1 aquec + 1 reconhec + 2 válidas
                "reps": "5-8",
                "rest": "120s",
                "ex_per_muscle": 3,
                "machine_only": False,
                "allow_free_weights": True,  # Todos liberados
                "block_exercises": [],
                "notes_prefix": "🔥 ESTRUTURA: 1x Aquecimento (50% carga) → 1x Reconhecimento (90-100%, 1-2 reps) → 2x Séries Válidas ATÉ A FALHA (mín 5 reps). ",
                "general_note": "AVANÇADO: Cada exercício segue a estrutura - Aquecimento → Reconhecimento → 2 Séries até a FALHA MUSCULAR."
            }
        
        # Ajusta número de exercícios baseado no tempo disponível
        max_exercises = self._get_exercises_per_duration(duration, level)
        
        workout_days = []
        
        for i in range(frequency):
            template = split[i]
            exercises = []
            exercises_added = 0
            
            for muscle in template["muscles"]:
                if exercises_added >= max_exercises:
                    break
                    
                available = EXERCISES.get(muscle, [])
                
                # Filtra exercícios baseado no nível
                filtered = []
                for ex in available:
                    ex_name_lower = ex["name"].lower()
                    
                    # Novatos e adaptação: apenas máquinas
                    if config.get("machine_only"):
                        if "máquina" in ex_name_lower or "polia" in ex_name_lower or "pulley" in ex_name_lower or "leg press" in ex_name_lower or "cadeira" in ex_name_lower or "mesa" in ex_name_lower or "cross" in ex_name_lower or "smith" in ex_name_lower:
                            filtered.append(ex)
                    else:
                        # Verifica exercícios bloqueados
                        blocked = config.get("block_exercises", [])
                        is_blocked = False
                        
                        # Bloqueios específicos
                        if "supino" in ex_name_lower and "barra" in ex_name_lower and "supino_barra" in blocked:
                            is_blocked = True
                        if "rosca" in ex_name_lower and "barra" in ex_name_lower and "direta" in ex_name_lower:
                            is_blocked = True
                        if "agachamento" in ex_name_lower and "livre" in ex_name_lower and "agachamento_livre" in blocked:
                            is_blocked = True
                        if "stiff" in ex_name_lower and "livre" in ex_name_lower and "stiff_livre" in blocked:
                            is_blocked = True
                        
                        if not is_blocked:
                            filtered.append(ex)
                
                # Se não encontrou exercícios filtrados, usa os disponíveis (fallback)
                if not filtered:
                    filtered = available[:config["ex_per_muscle"]]
                
                for j, ex_data in enumerate(filtered[:config["ex_per_muscle"]]):
                    if exercises_added >= max_exercises:
                        break
                        
                    rest_str = config["rest"]
                    notes = ex_data.get("notes", "")
                    
                    # Adiciona prefixo baseado no nível
                    if config.get("notes_prefix"):
                        notes = f"{config['notes_prefix']}{notes}"
                    
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=muscle.capitalize(),
                        sets=config["sets"],
                        reps=config["reps"],
                        rest=rest_str,
                        rest_seconds=parse_rest_seconds(rest_str),
                        notes=notes,
                        completed=False
                    ))
                    exercises_added += 1
            
            # Calcula duração real do treino
            calc_duration = len(exercises) * (config["sets"] * 1.5 + parse_rest_seconds(config["rest"]) * config["sets"] / 60) + 10
            calc_duration = min(duration, max(20, int(calc_duration)))
            
            day_name = f"Treino {template['name']}"
            if is_adaptation:
                day_name = f"[Adaptação] {template['name']}"
            
            workout_days.append(WorkoutDay(
                name=day_name,
                day=DAYS[i] if i < 7 else f"Dia {i + 1}",
                duration=calc_duration,
                exercises=exercises,
                completed=False
            ))
        
        split_name = {
            1: "Full Body", 2: "Upper/Lower", 3: "Push/Pull/Legs",
            4: "ABCD", 5: "ABCDE", 6: "PPL 2x", 7: "Bro Split"
        }.get(frequency, "Personalizado")
        
        level_name = {
            "novato": "Novato",
            "iniciante": "Iniciante",
            "intermediario": "Intermediário",
            "avancado": "Avançado"
        }.get(level, "Intermediário")
        
        # Nota geral do treino baseada no nível
        general_note = config.get("general_note", "")
        
        # Nota especial para novatos em adaptação
        if is_adaptation:
            remaining = 30 - completed_workouts
            notes = f"🔰 FASE DE ADAPTAÇÃO ({remaining} treinos restantes)\n{general_note}\n{split_name} | {frequency}x/semana | ~{duration}min"
        elif level == 'avancado':
            notes = f"🏆 {level_name} | {split_name} | {frequency}x/semana | ~{duration}min\n{general_note}"
        elif level == 'intermediario':
            notes = f"💪 {level_name} | {split_name} | {frequency}x/semana | ~{duration}min\n{general_note}"
        else:
            notes = f"{split_name} | {level_name} | {frequency}x/semana | ~{duration}min"
        
        return WorkoutPlan(
            user_id=user_id,
            training_level=level,
            goal=goal,
            weekly_frequency=frequency,
            workout_days=workout_days,
            notes=notes
        )
