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
    focus: Optional[str] = None  # Foco muscular específico (ex: "Peitoral Superior")
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
    # Inclui Elevação Lateral para trabalhar ombro no dia de peito
    "peito": [
        {
            "name": "Supino Reto na Máquina",
            "focus": "Peitoral Médio",
            "notes": "Sente com costas apoiadas. Empurre as manoplas para frente até extensão quase completa. Retorne controlado sem bater os pesos."
        },
        {
            "name": "Supino Inclinado na Máquina",
            "focus": "Peitoral Superior",
            "notes": "Banco ajustado para inclinação. Empurre para cima e para frente. Foco no peitoral superior. Desça controlado."
        },
        {
            "name": "Crucifixo na Máquina (Peck Deck)",
            "focus": "Peitoral Médio - Adução",
            "notes": "Cotovelos na altura dos ombros. Junte os braços à frente contraindo o peitoral. Abra controlado até sentir leve alongamento."
        },
        {
            "name": "Cross Over Polia Alta",
            "focus": "Peitoral Inferior",
            "notes": "Cabos na posição alta. Dê um passo à frente. Puxe os cabos para baixo e para frente, cruzando na frente do corpo."
        },
        {
            "name": "Elevação Lateral Halteres",
            "focus": "Deltóide Lateral",
            "notes": "Sentado para mais estabilidade. Cotovelos levemente flexionados. Eleve até altura dos ombros. Desça controlado."
        },
    ],
    
    # ============ COSTAS ============
    # Inclui Voador Invertido para trabalhar posterior de ombro
    "costas": [
        {
            "name": "Puxada Frontal Pegada Aberta",
            "focus": "Dorsal (Largura)",
            "notes": "Pegada pronada mais larga que os ombros. Puxe a barra até o queixo, cotovelos para baixo e para trás. Foco em abrir as costas."
        },
        {
            "name": "Puxada Pegada Neutra (Triângulo)",
            "focus": "Dorsal (Espessura)",
            "notes": "Use o triângulo/pegada neutra. Puxe até o peito, apertando as escápulas. Foco em espessura das costas."
        },
        {
            "name": "Remada Máquina Pegada Neutra",
            "focus": "Dorsal Médio (Espessura)",
            "notes": "Peito apoiado, pegada neutra. Puxe as manoplas em direção ao abdômen, contraindo as escápulas. Foco em espessura."
        },
        {
            "name": "Remada Máquina Pegada Pronada",
            "focus": "Trapézio/Romboides",
            "notes": "Pegada pronada (palmas para baixo). Puxe com cotovelos mais altos. Foco em trapézio médio e romboides."
        },
        {
            "name": "Voador Invertido (Peck Deck)",
            "focus": "Deltóide Posterior",
            "notes": "Sente de frente para o encosto. Abra os braços para trás contraindo as escápulas. Retorne controlado. Trabalha posterior de ombro."
        },
        {
            "name": "Remada Baixa Polia (Triângulo)",
            "focus": "Dorsal Inferior",
            "notes": "Sente com pernas levemente flexionadas. Puxe o triângulo até o abdômen baixo. Mantenha costas retas."
        },
    ],
    
    # ============ OMBROS ============
    # Para Full Upper e dias com ombro: Desenvolvimento + Elevação Lateral
    # (Voador vai em costas, Elevação Lateral Halteres vai em peito)
    "ombros": [
        {
            "name": "Desenvolvimento Máquina",
            "focus": "Deltóide Anterior/Médio",
            "notes": "Costas totalmente apoiadas. Empurre até quase estender os cotovelos. Desça até altura das orelhas."
        },
        {
            "name": "Elevação Lateral Máquina",
            "focus": "Deltóide Lateral",
            "notes": "Cotovelos apoiados nas almofadas. Eleve até altura dos ombros. Desça controlado."
        },
    ],
    
    # ============ BÍCEPS ============
    "biceps": [
        {
            "name": "Rosca Máquina",
            "focus": "Bíceps (Pico)",
            "notes": "Braços apoiados no suporte. Flexione trazendo manoplas aos ombros. Desça controlado sem estender completamente."
        },
        {
            "name": "Rosca Polia Baixa (Barra Reta)",
            "focus": "Bíceps (Cabeça Curta)",
            "notes": "De frente para polia baixa. Cotovelos fixos ao lado do corpo. Flexione até os ombros. Desça controlado."
        },
        {
            "name": "Rosca Alternada Halteres",
            "focus": "Bíceps (Cabeça Longa)",
            "notes": "Sentado com costas apoiadas. Alterne os braços. Gire o punho (supinação) durante a subida."
        },
        {
            "name": "Rosca Martelo Halteres",
            "focus": "Braquial/Braquiorradial",
            "notes": "Pegada neutra (palmas para dentro). Cotovelos fixos. Flexione até contrair. Trabalha braquial."
        },
    ],
    
    # ============ TRÍCEPS ============
    "triceps": [
        {
            "name": "Tríceps Polia Corda",
            "focus": "Cabeça Lateral/Medial",
            "notes": "Cotovelos fixos ao lado do corpo. Estenda completamente, abrindo a corda no final. Retorne até 90°."
        },
        {
            "name": "Tríceps Polia Barra Reta",
            "focus": "Cabeça Lateral",
            "notes": "Pegada pronada. Cotovelos fixos. Empurre a barra até extensão completa. Retorne controlado até 90°."
        },
        {
            "name": "Tríceps Máquina",
            "focus": "Tríceps Geral",
            "notes": "Costas apoiadas. Empurre as manoplas estendendo cotovelos. Retorne controlado."
        },
        {
            "name": "Tríceps Francês Halter",
            "focus": "Cabeça Longa",
            "notes": "Sentado. Halter acima da cabeça com as duas mãos. Desça atrás da cabeça. Estenda sem mover cotovelos."
        },
    ],
    
    # ============ QUADRÍCEPS ============
    "quadriceps": [
        {
            "name": "Leg Press 45°",
            "focus": "Quadríceps Geral",
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
            # Upper/Lower com distribuição específica
            # Upper: 2 peito, 2 costas, 2 ombro, 1 biceps, 1 triceps, 1 abdomen = 10 exercícios
            {"name": "Upper", "muscles": ["peito", "costas", "ombros", "biceps", "triceps", "abdomen"], "is_upper_lower": True},
            {"name": "Lower", "muscles": ["quadriceps", "posterior", "panturrilha"]},
        ],
        3: [
            {"name": "A - Push", "muscles": ["peito", "ombros", "triceps"]},
            {"name": "B - Pull", "muscles": ["costas", "biceps", "abdomen"]},
            {"name": "C - Legs", "muscles": ["quadriceps", "posterior", "panturrilha"]},
        ],
        4: [
            # ABCD: Ombro + Abdômen junto (permitido)
            {"name": "A - Peito/Tríceps", "muscles": ["peito", "triceps"]},
            {"name": "B - Costas/Bíceps", "muscles": ["costas", "biceps"]},
            {"name": "C - Pernas", "muscles": ["quadriceps", "posterior", "panturrilha"]},
            {"name": "D - Ombros/Abdômen", "muscles": ["ombros", "abdomen"]},
        ],
        5: [
            # ABCDE: Nunca treino só de ombros - D é Full Upper
            {"name": "A - Peito", "muscles": ["peito", "triceps"]},
            {"name": "B - Costas", "muscles": ["costas", "biceps"]},
            {"name": "C - Pernas Quad", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "D - Full Upper", "muscles": ["ombros", "peito", "costas"]},
            {"name": "E - Pernas Post", "muscles": ["posterior", "quadriceps", "abdomen"]},
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
            # 7x: Ombro junto com outro grupo
            {"name": "A - Peito", "muscles": ["peito"]},
            {"name": "B - Costas", "muscles": ["costas"]},
            {"name": "C - Ombros/Peito", "muscles": ["ombros", "peito"]},
            {"name": "D - Braços", "muscles": ["biceps", "triceps"]},
            {"name": "E - Quadríceps", "muscles": ["quadriceps", "panturrilha"]},
            {"name": "F - Posterior", "muscles": ["posterior"]},
            {"name": "G - Core", "muscles": ["abdomen"]},
        ],
    }
    return splits.get(freq, splits[3])

# ==================== UPPER BODY ESPECÍFICO ====================
# Configuração fixa para treino Upper (2x/semana)

UPPER_BODY_EXERCISES = [
    # 2 de Peito
    {"name": "Supino Reto na Máquina", "muscle_group": "Peito", "focus": "Peitoral Médio", 
     "notes": "Sente com costas apoiadas. Empurre as manoplas para frente até extensão quase completa."},
    {"name": "Crucifixo na Máquina (Peck Deck)", "muscle_group": "Peito", "focus": "Peitoral Médio - Adução",
     "notes": "Cotovelos na altura dos ombros. Junte os braços à frente contraindo o peitoral."},
    # 2 de Costas
    {"name": "Puxada Frontal Pegada Aberta", "muscle_group": "Costas", "focus": "Dorsal (Largura)",
     "notes": "Pegada pronada mais larga que os ombros. Puxe a barra até o queixo."},
    {"name": "Remada Baixa Polia (Triângulo)", "muscle_group": "Costas", "focus": "Dorsal Inferior",
     "notes": "Sente com pernas levemente flexionadas. Puxe o triângulo até o abdômen baixo."},
    # 2 de Ombro
    {"name": "Desenvolvimento Máquina", "muscle_group": "Ombros", "focus": "Deltóide Anterior/Médio",
     "notes": "Costas totalmente apoiadas. Empurre até quase estender os cotovelos."},
    {"name": "Elevação Lateral Máquina", "muscle_group": "Ombros", "focus": "Deltóide Lateral",
     "notes": "Cotovelos apoiados nas almofadas. Eleve até altura dos ombros."},
    # 1 de Bíceps
    {"name": "Rosca Direta Barra", "muscle_group": "Bíceps", "focus": "Bíceps Completo",
     "notes": "Cotovelos fixos ao lado do corpo. Suba a barra até a altura dos ombros."},
    # 1 de Tríceps
    {"name": "Tríceps Corda (Polia Alta)", "muscle_group": "Tríceps", "focus": "Tríceps Completo",
     "notes": "Cotovelos fixos ao lado do corpo. Estenda completamente e separe as pontas da corda."},
    # 1 de Abdômen
    {"name": "Abdominal Máquina", "muscle_group": "Abdômen", "focus": "Reto Abdominal",
     "notes": "Segure as manoplas, flexione o tronco para baixo contraindo o abdômen."},
]


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
        
        # ==================== AJUSTE BASEADO NO TEMPO DISPONÍVEL ====================
        # Tempo curto (≤45 min): Reduz exercícios repetidos e -1 série
        # Tempo médio (46-75 min): Normal
        # Tempo longo (≥76 min): Permite mais exercícios por grupo
        
        time_adjustment = {
            "reduce_sets": 0,  # Quantas séries a menos
            "reduce_exercises": 0,  # Quantos exercícios a menos por grupo
            "time_note": ""
        }
        
        if duration <= 45:
            # Tempo curto: treino mais enxuto
            time_adjustment["reduce_sets"] = 1
            time_adjustment["reduce_exercises"] = 1
            time_adjustment["time_note"] = "⏱️ TREINO OTIMIZADO (tempo curto): Menos exercícios e séries para caber no seu tempo."
        elif duration <= 60:
            # Tempo médio-curto: reduz apenas séries
            time_adjustment["reduce_sets"] = 1
            time_adjustment["reduce_exercises"] = 0
            time_adjustment["time_note"] = "⏱️ TREINO COMPACTO: 1 série a menos por exercício."
        elif duration >= 90:
            # Tempo longo: pode ter mais exercícios
            time_adjustment["reduce_sets"] = 0
            time_adjustment["reduce_exercises"] = -1  # Negativo = adiciona
            time_adjustment["time_note"] = ""
        
        # Aplica ajuste de séries (mínimo 2 séries)
        config["sets"] = max(2, config["sets"] - time_adjustment["reduce_sets"])
        
        # Aplica ajuste de exercícios por músculo (mínimo 1)
        config["ex_per_muscle"] = max(1, config["ex_per_muscle"] - time_adjustment["reduce_exercises"])
        
        # Ajusta número de exercícios baseado no tempo disponível
        max_exercises = self._get_exercises_per_duration(duration, level)
        
        # Exercícios compostos que sempre precisam de aquecimento (envolvem múltiplos grupos)
        COMPOUND_EXERCISES = [
            "agachamento", "stiff", "levantamento", "supino", "desenvolvimento",
            "remada", "puxada", "leg press", "hack"
        ]
        
        # Músculos pequenos: máximo 2 exercícios
        SMALL_MUSCLES = ["ombros", "triceps", "biceps", "panturrilha", "abdomen"]
        
        workout_days = []
        
        for i in range(frequency):
            template = split[i]
            exercises = []
            exercises_added = 0
            muscles_warmed_up = set()  # Rastreia músculos já aquecidos (para avançado)
            
            # TRATAMENTO ESPECIAL: Upper Body (2x/semana)
            # Usa lista fixa de exercícios para distribuição balanceada
            if template.get("is_upper_lower") and template["name"] == "Upper":
                # Para tempo curto, usa menos exercícios do Upper
                upper_exercises = UPPER_BODY_EXERCISES
                if duration <= 45:
                    # Remove 1 exercício de cada grupo que tem 2
                    # Mantém: 1 peito, 1 costas, 1 ombro, 1 biceps, 1 triceps, 1 abdomen = 6
                    upper_exercises = [
                        UPPER_BODY_EXERCISES[0],  # Supino
                        UPPER_BODY_EXERCISES[2],  # Puxada
                        UPPER_BODY_EXERCISES[4],  # Desenvolvimento
                        UPPER_BODY_EXERCISES[6],  # Rosca
                        UPPER_BODY_EXERCISES[7],  # Triceps
                        UPPER_BODY_EXERCISES[8],  # Abdomen
                    ]
                
                for ex_data in upper_exercises:
                    # Instruções baseadas no nível
                    execution_notes = ex_data.get("notes", "")
                    
                    # Ajuste de séries para avançado baseado no tempo
                    adjusted_sets = config["sets"]
                    
                    if level == 'avancado':
                        # Se tempo curto: 3 séries (1 aquec + 1 reconhec + 1 válida)
                        # Se tempo normal: 4 séries (1 aquec + 1 reconhec + 2 válidas)
                        if duration <= 60:
                            series_instruction = """📋 ESTRUTURA (3 SÉRIES - tempo otimizado):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• 2ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                            sets_count = 3
                        else:
                            series_instruction = """📋 ESTRUTURA (4 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• 2ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)
• 4ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                            sets_count = 4
                        notes = f"{series_instruction}\n\n🎯 EXECUÇÃO: {execution_notes}"
                    elif level == 'intermediario':
                        series_instruction = "💪 Chegue PERTO DA FALHA em pelo menos 1 série!"
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}"
                        sets_count = adjusted_sets
                    elif is_adaptation:
                        series_instruction = "⚠️ ADAPTAÇÃO: Use carga LEVE! Foco 100% na execução correta."
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}"
                        sets_count = adjusted_sets
                    else:
                        notes = f"🎯 {execution_notes}"
                        sets_count = adjusted_sets
                    
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=ex_data["muscle_group"],
                        focus=ex_data.get("focus"),
                        sets=sets_count,
                        reps=config["reps"],
                        rest=config["rest"],
                        rest_seconds=parse_rest_seconds(config["rest"]),
                        notes=notes,
                        completed=False
                    ))
                
                # Cria o dia de treino Upper com exercícios fixos
                workout_days.append(WorkoutDay(
                    day=DAYS[i],
                    name=template["name"],
                    exercises=exercises,
                    duration=len(exercises) * 5  # ~5 min por exercício
                ))
                continue  # Pula para o próximo dia
            
            for muscle in template["muscles"]:
                if exercises_added >= max_exercises:
                    break
                
                # Limite de 2 exercícios para músculos pequenos (incluindo ombros)
                if muscle in SMALL_MUSCLES:
                    max_for_muscle = 2
                else:
                    max_for_muscle = config["ex_per_muscle"]
                    
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
                
                for j, ex_data in enumerate(filtered[:max_for_muscle]):
                    if exercises_added >= max_exercises:
                        break
                    
                    ex_name_lower = ex_data["name"].lower()
                    rest_str = config["rest"]
                    
                    # Foco muscular específico
                    exercise_focus = ex_data.get("focus", None)
                    
                    # Instruções de EXECUÇÃO do exercício (separadas)
                    execution_notes = ex_data.get("notes", "")
                    
                    # Verifica se é exercício composto
                    is_compound = any(comp in ex_name_lower for comp in COMPOUND_EXERCISES)
                    
                    # Lógica de séries para AVANÇADO
                    if level == 'avancado':
                        needs_warmup = (muscle not in muscles_warmed_up) or is_compound
                        
                        # Ajuste baseado no tempo disponível
                        # Tempo curto (≤60min): reduz 1 série válida
                        reduce_valid_sets = 1 if duration <= 60 else 0
                        
                        if needs_warmup:
                            # Precisa aquecer (primeiro do grupo OU exercício composto)
                            if reduce_valid_sets:
                                # Tempo curto: 3 séries (1 aquec + 1 reconhec + 1 válida)
                                series_instruction = """📋 ESTRUTURA (3 SÉRIES - tempo otimizado):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• 2ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                                sets_count = 3
                            else:
                                # Tempo normal: 4 séries (1 aquec + 1 reconhec + 2 válidas)
                                series_instruction = """📋 ESTRUTURA (4 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• 2ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)
• 4ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                                sets_count = 4
                            
                            if is_compound:
                                series_instruction = "⚠️ EXERCÍCIO COMPOSTO - Sempre aquecer!\n" + series_instruction
                            muscles_warmed_up.add(muscle)
                        else:
                            # Músculo já aquecido e não é composto
                            if reduce_valid_sets:
                                # Tempo curto: 2 séries (1 reconhec + 1 válida)
                                series_instruction = """📋 ESTRUTURA (2 SÉRIES - músculo aquecido, tempo otimizado):
• 1ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 2ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                                sets_count = 2
                            else:
                                # Tempo normal: 3 séries (1 reconhec + 2 válidas)
                                series_instruction = """📋 ESTRUTURA (3 SÉRIES - músculo já aquecido):
• 1ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 2ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                                sets_count = 3
                        
                        # Combina instrução de séries + execução
                        notes = f"{series_instruction}\n\n🎯 EXECUÇÃO: {execution_notes}" if execution_notes else series_instruction
                    
                    elif level == 'intermediario':
                        series_instruction = "💪 Chegue PERTO DA FALHA em pelo menos 1 série!"
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes else series_instruction
                        sets_count = config["sets"]
                    
                    elif is_adaptation:
                        series_instruction = "⚠️ ADAPTAÇÃO: Use carga LEVE! Foco 100% na execução correta."
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes else series_instruction
                        sets_count = config["sets"]
                    
                    else:
                        # Novato pós-adaptação e Iniciante
                        notes = f"🎯 {execution_notes}" if execution_notes else ""
                        sets_count = config["sets"]
                    
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=muscle.capitalize(),
                        focus=exercise_focus,
                        sets=sets_count if level == 'avancado' else config["sets"],
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
