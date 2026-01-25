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
    # Focos diferentes para garantir variedade
    "biceps": [
        {
            "name": "Rosca Direta Barra",
            "focus": "Bíceps Completo",
            "notes": "Cotovelos fixos ao lado do corpo. Suba a barra até a altura dos ombros. Desça controlado."
        },
        {
            "name": "Rosca Martelo Halteres",
            "focus": "Braquial/Braquiorradial",
            "notes": "Pegada neutra (palmas para dentro). Cotovelos fixos. Trabalha braquial e antebraço."
        },
        {
            "name": "Rosca Alternada Halteres",
            "focus": "Bíceps (Cabeça Longa)",
            "notes": "Sentado com costas apoiadas. Alterne os braços. Gire o punho (supinação) durante a subida."
        },
        {
            "name": "Rosca Scott Máquina",
            "focus": "Bíceps (Cabeça Curta/Pico)",
            "notes": "Braços apoiados no suporte. Isola o bíceps eliminando impulso. Foco no pico."
        },
    ],
    
    # ============ TRÍCEPS ============
    # Focos diferentes para garantir variedade
    "triceps": [
        {
            "name": "Tríceps Corda (Polia Alta)",
            "focus": "Cabeça Lateral",
            "notes": "Cotovelos fixos ao lado do corpo. Estenda completamente, abrindo a corda no final."
        },
        {
            "name": "Tríceps Francês Halter",
            "focus": "Cabeça Longa",
            "notes": "Sentado. Halter acima da cabeça. Desça atrás da cabeça. Estenda sem mover cotovelos."
        },
        {
            "name": "Tríceps Barra Reta (Polia Alta)",
            "focus": "Cabeça Medial",
            "notes": "Pegada pronada. Cotovelos fixos. Empurre a barra até extensão completa."
        },
        {
            "name": "Tríceps Máquina",
            "focus": "Tríceps Geral",
            "notes": "Costas apoiadas. Empurre as manoplas estendendo cotovelos. Retorne controlado."
        },
    ],
    
    # ============ QUADRÍCEPS ============
    "quadriceps": [
        {
            "name": "Leg Press 45°",
            "focus": "Quadríceps Completo",
            "notes": "Pés no centro da plataforma na largura dos ombros. Desça até 90° nos joelhos. Empurre sem travar os joelhos no topo."
        },
        {
            "name": "Cadeira Extensora",
            "focus": "Vasto Lateral/Medial",
            "notes": "Ajuste o encosto para joelhos alinhados com o eixo. Estenda as pernas completamente, contraindo no topo. Desça controlado."
        },
        {
            "name": "Agachamento no Smith Machine",
            "focus": "Quadríceps/Glúteos",
            "notes": "Pés ligeiramente à frente da barra. Desça até coxas paralelas ao chão. Suba empurrando pelos calcanhares. Joelhos alinhados com os pés."
        },
        {
            "name": "Hack Machine",
            "focus": "Vasto Lateral",
            "notes": "Costas apoiadas, ombros sob as almofadas. Pés na largura dos ombros. Desça controlado até 90°. Empurre sem travar joelhos."
        },
    ],
    
    # ============ POSTERIOR DE COXA ============
    "posterior": [
        {
            "name": "Mesa Flexora",
            "focus": "Posterior de Coxa",
            "notes": "Deite de bruços com joelhos alinhados ao eixo da máquina. Flexione as pernas trazendo os calcanhares em direção aos glúteos. Desça controlado."
        },
        {
            "name": "Cadeira Flexora (Sentado)",
            "focus": "Posterior de Coxa",
            "notes": "Sente com coxas apoiadas. Flexione as pernas para baixo e para trás. Contraia no final do movimento. Retorne controlado."
        },
        {
            "name": "Stiff na Máquina Smith",
            "focus": "Posterior/Glúteos",
            "notes": "Pernas semi-estendidas, pés na largura do quadril. Desça a barra deslizando próximo às coxas até sentir alongamento. Suba contraindo glúteos."
        },
        {
            "name": "Glúteo na Máquina (Kick Back)",
            "focus": "Glúteo Máximo",
            "notes": "Apoie o pé na plataforma. Empurre para trás estendendo o quadril. Contraia o glúteo no topo. Retorne controlado sem deixar peso bater."
        },
    ],
    
    # ============ PANTURRILHA ============
    "panturrilha": [
        {
            "name": "Panturrilha no Leg Press",
            "focus": "Gastrocnêmio",
            "notes": "Apoie apenas a ponta dos pés na plataforma. Empurre estendendo os tornozelos o máximo possível. Desça alongando bem a panturrilha."
        },
        {
            "name": "Panturrilha Sentado na Máquina",
            "focus": "Sóleo",
            "notes": "Joelhos a 90° sob as almofadas. Eleve os calcanhares o máximo possível. Desça controlado até sentir alongamento completo."
        },
        {
            "name": "Panturrilha em Pé na Máquina",
            "focus": "Gastrocnêmio",
            "notes": "Ombros sob as almofadas. Eleve nos dedos o máximo possível, contraindo no topo. Desça alongando completamente."
        },
    ],
    
    # ============ ABDÔMEN ============
    "abdomen": [
        {
            "name": "Abdominal na Máquina",
            "focus": "Reto Abdominal",
            "notes": "Sente e segure as manoplas. Flexione o tronco para frente contraindo o abdômen. Retorne controlado sem soltar a tensão."
        },
        {
            "name": "Abdominal na Polia Alta (Corda)",
            "focus": "Reto Abdominal",
            "notes": "Ajoelhe de costas para a polia. Segure a corda atrás da cabeça. Flexione o tronco em direção ao chão. Retorne controlado."
        },
        {
            "name": "Prancha Isométrica",
            "focus": "Core (Estabilização)",
            "notes": "Apoie antebraços e pontas dos pés no chão. Corpo reto da cabeça aos calcanhares. Mantenha o abdômen contraído. Não deixe o quadril subir ou descer."
        },
        {
            "name": "Elevação de Pernas no Apoio",
            "focus": "Reto Abdominal Inferior",
            "notes": "Costas apoiadas no suporte, braços nos apoios. Eleve as pernas estendidas até 90°. Desça controlado sem balançar o corpo."
        },
    ],
}

DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ==================== SPLITS ====================

def get_split_for_frequency(freq: int) -> List[Dict]:
    splits = {
        1: [{"name": "Full Body", "muscles": ["peito", "costas", "ombros", "quadriceps", "posterior", "biceps", "triceps"]}],
        2: [
            # Upper/Lower com distribuição específica
            # Upper: 2 peito, 2 costas, 2 ombro, 1 biceps, 1 triceps, 1 abdomen = 9 exercícios
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
            # C - Pernas Quad: foco quadríceps + 1 posterior para estímulo
            # E - Pernas Post: foco posteriores + 1 quadríceps para estímulo
            {"name": "A - Peito", "muscles": ["peito", "triceps"]},
            {"name": "B - Costas", "muscles": ["costas", "biceps"]},
            {"name": "C - Pernas Quad", "muscles": ["quadriceps", "posterior", "panturrilha"]},
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
        # Busca tempo disponível do perfil (available_time_per_session)
        duration = user_profile.get('available_time_per_session', 60)
        if duration is None:
            duration = 60  # Default 60 minutos
        completed_workouts = user_profile.get('completed_workouts', 0)
        
        user_id = user_profile.get('user_id') or user_profile.get('_id') or user_profile.get('id')
        return self._generate_workout(user_id, frequency, level, goal, duration, completed_workouts)
    
    def _get_exercises_per_duration(self, duration: int, level: str) -> int:
        """
        Calcula quantos exercícios cabem no tempo disponível
        REGRA DURA: Máximo absoluto = 10 exercícios
        
        Classificação por tempo:
        - ≤30 min (Curto): 3-4 exercícios
        - 30-60 min (Médio): 5-6 exercícios
        - 60-90 min (Longo): 6-8 exercícios
        - >90 min (Estendido): 8-10 exercícios (nunca mais que 10)
        """
        if duration <= 30:
            # Treino Curto: 3-4 exercícios
            max_ex = 4 if level in ['intermediario', 'avancado'] else 3
        elif duration <= 60:
            # Treino Médio: 5-6 exercícios
            max_ex = 6 if level in ['intermediario', 'avancado'] else 5
        elif duration <= 90:
            # Treino Longo: 6-8 exercícios
            max_ex = 8 if level in ['intermediario', 'avancado'] else 6
        else:
            # Treino Estendido: 8-10 exercícios
            max_ex = 10 if level == 'avancado' else 8
        
        # REGRA DURA: Nunca ultrapassar 10 exercícios
        return min(max_ex, 10)
    
    def _get_sets_per_duration(self, duration: int, level: str) -> int:
        """
        Calcula quantas séries por exercício baseado no tempo
        
        REGRA: MÁXIMO 4 SÉRIES EM TODOS OS NÍVEIS
        """
        # LIMITE FIXO: máximo 4 séries
        return 4
    
    def _generate_workout(self, user_id: str, frequency: int, level: str, goal: str, duration: int, completed_workouts: int) -> WorkoutPlan:
        split = get_split_for_frequency(frequency)
        
        # ==================== VALIDAÇÃO DE DIAS POR NÍVEL ====================
        # Novato: ideal 2-3 dias
        # 6+ dias: apenas para Intermediário e Avançado
        if level == 'novato' and frequency > 3:
            frequency = 3  # Limita novato a 3 dias
            split = get_split_for_frequency(frequency)
        elif level == 'iniciante' and frequency > 5:
            frequency = 5  # Limita iniciante a 5 dias
            split = get_split_for_frequency(frequency)
        
        # NOVATO: Treino de adaptação nas primeiras 30 sessões
        is_adaptation = level == 'novato' and completed_workouts < 30
        
        # ==================== CONFIGURAÇÕES POR NÍVEL ====================
        # NOVATO = nunca treinou (treinos simples, exercícios seguros, menor volume)
        # INICIANTE = 6 meses - 2 anos (volume moderado, compostos + acessórios leves)
        # INTERMEDIÁRIO = 2-3 anos (maior volume, pode usar técnicas)
        # AVANÇADO = 3+ anos (volume alto, técnicas avançadas)
        
        # Séries baseadas no tempo disponível
        sets_by_time = self._get_sets_per_duration(duration, level)
        
        if is_adaptation:
            # Treino de adaptação para novatos (4-8 semanas)
            config = {
                "sets": 2,  # Adaptação: 2 séries
                "reps": "15-20",
                "rest": "60s",
                "ex_per_muscle": 1,
                "machine_only": True,
                "notes_prefix": "⚠️ ADAPTAÇÃO - CARGA LEVE! ",
                "general_note": "FASE DE ADAPTAÇÃO: Técnica acima de carga."
            }
        elif level == 'novato':
            # NOVATO = nunca treinou (treinos simples, exercícios seguros, menor volume)
            config = {
                "sets": 3,  # Novato: 3 séries
                "reps": "12-15",
                "rest": "90s",
                "ex_per_muscle": 1,  # Menos exercícios por músculo
                "machine_only": True,
                "notes_prefix": "",
                "general_note": "Foco 100% na execução correta. Evite cargas pesadas."
            }
        elif level == 'iniciante':
            # INICIANTE = 6 meses - 2 anos (volume moderado, compostos + acessórios leves)
            config = {
                "sets": 4,  # LIMITE FIXO: 4 séries
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
            # INTERMEDIÁRIO = 2-3 anos (maior volume, pode usar bi-set, pirâmide, pré-exaustão)
            config = {
                "sets": 4,  # LIMITE FIXO: 4 séries
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
            # AVANÇADO = 3+ anos (volume alto, drop set, rest pause, maior intensidade)
            # DIFERENCIADO: Mais exercícios, técnicas avançadas, 10-12 reps
            config = {
                "sets": 4,  # LIMITE FIXO: 4 séries
                "reps": "10-12",  # AVANÇADO: 10-12 reps (DIFERENTE de intermediário)
                "rest": "90s",
                "ex_per_muscle": 3,  # MAIS exercícios que intermediário
                "machine_only": False,
                "allow_free_weights": True,
                "block_exercises": [],
                "notes_prefix": "🔥 ATÉ A FALHA! ",
                "general_note": "AVANÇADO: Pode usar drop set, rest pause, bi-set. Técnica impecável."
            }
        
        # ==================== MÁXIMO DE EXERCÍCIOS (REGRA DURA: 10) ====================
        max_exercises = self._get_exercises_per_duration(duration, level)
        
        # Exercícios compostos que sempre precisam de aquecimento
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
            
            # ==================== TRATAMENTO ESPECIAL: FULL BODY (1x/semana) ====================
            # Garante 1 exercício por grupo muscular principal
            if template["name"] == "Full Body" and frequency == 1:
                full_body_exercises = [
                    {"name": "Supino Reto na Máquina", "muscle_group": "Peito", "focus": "Peitoral Médio",
                     "notes": "Sente com costas apoiadas. Empurre as manoplas para frente até extensão quase completa."},
                    {"name": "Puxada Frontal Pegada Aberta", "muscle_group": "Costas", "focus": "Dorsal (Largura)",
                     "notes": "Pegada pronada mais larga que os ombros. Puxe a barra até o queixo."},
                    {"name": "Desenvolvimento Máquina", "muscle_group": "Ombros", "focus": "Deltóide Anterior/Médio",
                     "notes": "Costas totalmente apoiadas. Empurre até quase estender os cotovelos."},
                    {"name": "Leg Press 45°", "muscle_group": "Quadríceps", "focus": "Quadríceps Completo",
                     "notes": "Pés no centro da plataforma na largura dos ombros. Desça até 90° nos joelhos."},
                    {"name": "Mesa Flexora", "muscle_group": "Posterior", "focus": "Posterior de Coxa",
                     "notes": "Deite de bruços com joelhos alinhados ao eixo da máquina. Flexione trazendo calcanhares aos glúteos."},
                    {"name": "Rosca Scott Máquina", "muscle_group": "Bíceps", "focus": "Bíceps (Pico)",
                     "notes": "Braços apoiados no suporte. Isola o bíceps eliminando impulso."},
                    {"name": "Tríceps Corda (Polia Alta)", "muscle_group": "Tríceps", "focus": "Cabeça Lateral",
                     "notes": "Cotovelos fixos ao lado do corpo. Estenda completamente, abrindo a corda no final."},
                ]
                
                # Adiciona exercícios extras se tiver tempo
                if duration >= 60:
                    full_body_exercises.append(
                        {"name": "Cadeira Extensora", "muscle_group": "Quadríceps", "focus": "Vasto Lateral/Medial",
                         "notes": "Ajuste o encosto para joelhos alinhados com o eixo. Estenda as pernas completamente."}
                    )
                if duration >= 75:
                    full_body_exercises.append(
                        {"name": "Panturrilha no Leg Press", "muscle_group": "Panturrilha", "focus": "Gastrocnêmio",
                         "notes": "Apoie apenas a ponta dos pés na plataforma. Empurre estendendo os tornozelos."}
                    )
                if duration >= 90:
                    full_body_exercises.append(
                        {"name": "Crucifixo na Máquina (Peck Deck)", "muscle_group": "Peito", "focus": "Peitoral - Adução",
                         "notes": "Cotovelos na altura dos ombros. Junte os braços à frente contraindo o peitoral."}
                    )
                
                for ex_data in full_body_exercises[:max_exercises]:
                    execution_notes = ex_data.get("notes", "")
                    sets_count = config["sets"]
                    
                    if level == 'avancado':
                        notes = f"🔥 ATÉ A FALHA!\n\n🎯 {execution_notes}"
                    elif level == 'intermediario':
                        notes = f"💪 Perto da falha!\n\n🎯 {execution_notes}"
                    else:
                        notes = f"🎯 {execution_notes}"
                    
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
                
                workout_days.append(WorkoutDay(
                    day=DAYS[i],
                    name=template["name"],
                    exercises=exercises,
                    duration=len(exercises) * 6
                ))
                continue
            
            # TRATAMENTO ESPECIAL: Upper Body (2x/semana)
            # Usa lista fixa de exercícios para distribuição balanceada
            if template.get("is_upper_lower") and template["name"] == "Upper":
                # Limita exercícios baseado no tempo (máximo 10)
                upper_limit = min(max_exercises, len(UPPER_BODY_EXERCISES))
                
                # Para tempo curto (≤30min), usa versão reduzida
                if duration <= 30:
                    upper_exercises = [
                        UPPER_BODY_EXERCISES[0],  # Supino
                        UPPER_BODY_EXERCISES[2],  # Puxada
                        UPPER_BODY_EXERCISES[4],  # Desenvolvimento
                        UPPER_BODY_EXERCISES[6],  # Rosca
                    ]
                elif duration <= 45:
                    upper_exercises = [
                        UPPER_BODY_EXERCISES[0],  # Supino
                        UPPER_BODY_EXERCISES[2],  # Puxada
                        UPPER_BODY_EXERCISES[4],  # Desenvolvimento
                        UPPER_BODY_EXERCISES[6],  # Rosca
                        UPPER_BODY_EXERCISES[7],  # Triceps
                    ]
                elif duration <= 60:
                    upper_exercises = [
                        UPPER_BODY_EXERCISES[0],  # Supino
                        UPPER_BODY_EXERCISES[1],  # Crucifixo
                        UPPER_BODY_EXERCISES[2],  # Puxada
                        UPPER_BODY_EXERCISES[3],  # Remada
                        UPPER_BODY_EXERCISES[4],  # Desenvolvimento
                        UPPER_BODY_EXERCISES[6],  # Rosca
                        UPPER_BODY_EXERCISES[7],  # Triceps
                    ]
                else:
                    # 60+ min: treino completo
                    upper_exercises = UPPER_BODY_EXERCISES[:upper_limit]
                
                for ex_data in upper_exercises:
                    execution_notes = ex_data.get("notes", "")
                    sets_count = config["sets"]
                    
                    if level == 'avancado':
                        notes = f"🔥 ATÉ A FALHA!\n\n🎯 {execution_notes}"
                    elif level == 'intermediario':
                        notes = f"💪 Perto da falha!\n\n🎯 {execution_notes}"
                    else:
                        notes = f"🎯 {execution_notes}"
                    
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
                
                # ==================== LÓGICA DE ESTÍMULO COMPLEMENTAR ====================
                # Treinos de perna com foco específico devem ter apenas 1 exercício do músculo secundário
                # C - Pernas Quad: foco quadríceps, posterior é estímulo (1 exercício)
                # E - Pernas Post: foco posteriores, quadríceps é estímulo (1 exercício)
                
                template_name = template.get("name", "").lower()
                is_quad_day = "quad" in template_name
                is_post_day = "post" in template_name
                
                # Se é dia de Quad e o músculo atual é posterior = apenas 1 exercício (estímulo)
                # Se é dia de Post e o músculo atual é quadriceps = apenas 1 exercício (estímulo)
                is_stimulus_muscle = (is_quad_day and muscle == "posterior") or (is_post_day and muscle == "quadriceps")
                
                # Limite de 2 exercícios para músculos pequenos (incluindo ombros)
                if is_stimulus_muscle:
                    max_for_muscle = 1  # Apenas 1 exercício de estímulo
                elif muscle in SMALL_MUSCLES:
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
                
                # ==================== EVITAR FOCOS REPETIDOS ====================
                # Seleciona exercícios garantindo que cada um tenha um foco diferente
                selected_exercises = []
                used_focuses = set()
                
                for ex in filtered:
                    if len(selected_exercises) >= max_for_muscle:
                        break
                    
                    ex_focus = ex.get("focus", "")
                    
                    # Se o foco já foi usado, pula este exercício
                    if ex_focus and ex_focus in used_focuses:
                        continue
                    
                    selected_exercises.append(ex)
                    if ex_focus:
                        used_focuses.add(ex_focus)
                
                # Se não conseguiu exercícios suficientes com focos diferentes, 
                # completa com os disponíveis (fallback)
                if len(selected_exercises) < max_for_muscle:
                    for ex in filtered:
                        if len(selected_exercises) >= max_for_muscle:
                            break
                        if ex not in selected_exercises:
                            selected_exercises.append(ex)
                
                for j, ex_data in enumerate(selected_exercises):
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
                    
                    # Verifica se precisa aquecer (APENAS primeiro exercício do músculo)
                    needs_warmup = muscle not in muscles_warmed_up
                    
                    # Lógica de séries por nível - TODOS têm aquecimento no primeiro exercício
                    
                    # LOW VOLUME: Treino de baixo volume com estrutura completa
                    if level == 'low_volume':
                        if needs_warmup:
                            series_instruction = """📋 ESTRUTURA (4 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• 2ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)
• 4ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                            sets_count = 4
                            muscles_warmed_up.add(muscle)
                        else:
                            series_instruction = """📋 ESTRUTURA (3 SÉRIES - músculo já aquecido):
• 1ª Série: RECONHECIMENTO (90-100% carga, 1-2 reps)
• 2ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)
• 3ª Série: VÁLIDA (100% carga, 5-8 reps ATÉ A FALHA)"""
                            sets_count = 3
                        
                        notes = f"{series_instruction}\n\n🎯 EXECUÇÃO: {execution_notes}" if execution_notes else series_instruction
                        rest_str = "2min"
                    
                    # AVANÇADO: 4 séries (1 aquecimento + 3 válidas)
                    elif level == 'avancado':
                        base_sets = 4  # LIMITE FIXO
                        if needs_warmup:
                            series_instruction = f"""📋 ESTRUTURA (4 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• Séries 2-4: VÁLIDAS (ATÉ A FALHA nas últimas 2)"""
                            sets_count = 4  # Inclui aquecimento
                            muscles_warmed_up.add(muscle)
                        else:
                            series_instruction = f"🔥 4 séries - Treine ATÉ A FALHA nas últimas 2!"
                            sets_count = 4
                        
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes else series_instruction
                    
                    # INTERMEDIÁRIO: 4 séries (1 aquecimento + 3 válidas)
                    elif level == 'intermediario':
                        base_sets = 4  # LIMITE FIXO
                        if needs_warmup:
                            series_instruction = f"""📋 ESTRUTURA (4 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• Séries 2-4: VÁLIDAS (chegue PERTO DA FALHA em pelo menos 1)"""
                            sets_count = 4  # Inclui aquecimento
                            muscles_warmed_up.add(muscle)
                        else:
                            series_instruction = f"💪 4 séries - Chegue PERTO DA FALHA em pelo menos 1!"
                            sets_count = 4
                        
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes else series_instruction
                    
                    # INICIANTE: 4 séries (1 aquecimento + 3 válidas)
                    elif level == 'iniciante':
                        base_sets = 4  # LIMITE FIXO
                        if needs_warmup:
                            series_instruction = f"""📋 ESTRUTURA (4 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• Séries 2-4: VÁLIDAS (foco na execução correta)"""
                            sets_count = 4  # Inclui aquecimento
                            muscles_warmed_up.add(muscle)
                        else:
                            series_instruction = f"✅ 4 séries - Foco na execução correta!"
                            sets_count = 4
                        
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes else series_instruction
                    
                    # ADAPTAÇÃO (Novato): 2 séries
                    elif is_adaptation:
                        base_sets = 2
                        if needs_warmup:
                            series_instruction = f"""⚠️ ADAPTAÇÃO (2 SÉRIES):
• 1ª Série: AQUECIMENTO (carga muito leve, 15-20 reps)
• 2ª Série: Use carga LEVE! Foco 100% na execução"""
                            sets_count = 2
                            muscles_warmed_up.add(muscle)
                        else:
                            series_instruction = f"⚠️ ADAPTAÇÃO: 2 séries - Carga LEVE, foco na execução!"
                            sets_count = 2
                        
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes else series_instruction
                    
                    # NOVATO pós-adaptação: 3 séries
                    else:
                        base_sets = 3
                        if needs_warmup:
                            series_instruction = f"""📋 ESTRUTURA (3 SÉRIES):
• 1ª Série: AQUECIMENTO (50% da carga, 12-15 reps)
• Séries 2-3: VÁLIDAS"""
                            sets_count = 3
                            muscles_warmed_up.add(muscle)
                        else:
                            sets_count = 3
                            series_instruction = "✅ 3 séries - Foco na execução correta!"
                        
                        notes = f"{series_instruction}\n\n🎯 {execution_notes}" if execution_notes and series_instruction else (f"🎯 {execution_notes}" if execution_notes else series_instruction)
                    
                    exercises.append(Exercise(
                        name=ex_data["name"],
                        muscle_group=muscle.capitalize(),
                        focus=exercise_focus,
                        sets=sets_count,
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
