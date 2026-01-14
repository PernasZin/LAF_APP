"""
Workout Module - Exercise Database
==================================
All exercises organized by muscle group
"""

# ==================== EXERCÍCIOS SEGUROS (MÁQUINAS + CABOS + HALTERES) ====================
# REGRA: Priorizar máquinas e cabos. Halteres apenas quando necessário.
# SEM: Barras, levantamentos olímpicos, movimentos instáveis

EXERCISES = {
    # ============ PEITO ============
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
    "costas": [
        {
            "name": "Puxada Frontal Pegada Aberta",
            "focus": "Dorsal (Largura)",
            "notes": "Pegada pronada mais larga que os ombros. Puxe a barra até o queixo, cotovelos para baixo e para trás. Foco em abrir as costas."
        },
        {
            "name": "Puxada Pegada Neutra (Triângulo)",
            "focus": "Dorsal (Espessura)",
            "notes": "Pegada neutra com triângulo. Puxe até o peito, focando em aproximar as escápulas. Ótimo para costas médias."
        },
        {
            "name": "Remada Máquina Pegada Neutra",
            "focus": "Dorsal (Espessura)",
            "notes": "Peito apoiado no banco. Puxe os cabos até contrair completamente as costas. Foco em espremer as escápulas."
        },
        {
            "name": "Remada Máquina Pegada Pronada",
            "focus": "Dorsal Superior",
            "notes": "Pegada pronada (palmas para baixo). Cotovelos mais abertos para trabalhar costas superiores e trapézio."
        },
        {
            "name": "Voador Invertido (Peck Deck)",
            "focus": "Deltóide Posterior",
            "notes": "Sentado de frente para a máquina. Puxe os braços para trás em arco. Trabalha posterior de ombro junto com costas."
        },
        {
            "name": "Remada Baixa Polia (Triângulo)",
            "focus": "Dorsal Inferior",
            "notes": "Sente com pernas levemente flexionadas. Puxe o triângulo até o abdômen baixo. Costas retas durante todo o movimento."
        },
    ],
    
    # ============ OMBROS ============
    "ombros": [
        {
            "name": "Desenvolvimento Máquina",
            "focus": "Deltóide Anterior/Médio",
            "notes": "Costas totalmente apoiadas. Empurre até quase estender os cotovelos. Desça até altura das orelhas."
        },
        {
            "name": "Elevação Lateral Máquina",
            "focus": "Deltóide Lateral",
            "notes": "Cotovelos apoiados nas almofadas. Eleve até altura dos ombros. Controle a descida - não deixe os pesos baterem."
        },
    ],
    
    # ============ BÍCEPS ============
    "biceps": [
        {
            "name": "Rosca Direta Barra",
            "focus": "Bíceps Completo",
            "notes": "Cotovelos fixos ao lado do corpo. Suba a barra até a altura dos ombros. Evite balançar o corpo."
        },
        {
            "name": "Rosca Martelo Halteres",
            "focus": "Braquial",
            "notes": "Pegada neutra (polegares para cima). Suba alternadamente. Excelente para espessura do braço."
        },
        {
            "name": "Rosca Alternada Halteres",
            "focus": "Bíceps com Supinação",
            "notes": "Comece com pegada neutra. Durante a subida, gire o punho (supinação). Maximiza contração do bíceps."
        },
        {
            "name": "Rosca Scott Máquina",
            "focus": "Bíceps Curto",
            "notes": "Braços apoiados no banco Scott. Isola completamente o bíceps. Não estenda totalmente para proteger cotovelos."
        },
    ],
    
    # ============ TRÍCEPS ============
    "triceps": [
        {
            "name": "Tríceps Corda (Polia Alta)",
            "focus": "Tríceps Completo",
            "notes": "Cotovelos fixos ao lado do corpo. Estenda completamente e separe as pontas da corda no final."
        },
        {
            "name": "Tríceps Francês Halter",
            "focus": "Cabeça Longa",
            "notes": "Deitado ou sentado. Halter atrás da cabeça. Estenda apenas o antebraço, mantendo cotovelos fixos."
        },
        {
            "name": "Tríceps Barra Reta (Polia Alta)",
            "focus": "Tríceps Lateral",
            "notes": "Similar à corda mas com barra reta. Pegada pronada. Foco na cabeça lateral do tríceps."
        },
        {
            "name": "Tríceps Máquina",
            "focus": "Tríceps Completo",
            "notes": "Sentado na máquina. Empurre até extensão completa. Máquina guiada = execução mais segura."
        },
    ],
    
    # ============ QUADRÍCEPS ============
    "quadriceps": [
        {
            "name": "Leg Press 45°",
            "focus": "Quadríceps Completo",
            "notes": "Pés na largura dos ombros. Desça até 90° de flexão do joelho. NÃO trave os joelhos na subida."
        },
        {
            "name": "Cadeira Extensora",
            "focus": "Quadríceps (Isolamento)",
            "notes": "Ajuste o encosto para costas apoiadas. Estenda até quase travar, segure 1s no topo. Desça controlado."
        },
        {
            "name": "Agachamento no Smith Machine",
            "focus": "Quadríceps/Glúteos",
            "notes": "Pés ligeiramente à frente da barra. Desça até coxas paralelas ao chão. Smith garante estabilidade."
        },
        {
            "name": "Leg Press Horizontal",
            "focus": "Quadríceps",
            "notes": "Variação mais suave que 45°. Bom para quem tem dor lombar. Mesma técnica do Leg Press normal."
        },
    ],
    
    # ============ POSTERIOR DE COXA ============
    "posterior": [
        {
            "name": "Mesa Flexora",
            "focus": "Posterior de Coxa",
            "notes": "Deitado de bruços. Flexione até ~90°, segure no topo. Não levante o quadril do banco."
        },
        {
            "name": "Cadeira Flexora (Sentado)",
            "focus": "Posterior de Coxa",
            "notes": "Sentado com coxas apoiadas. Flexione puxando os calcanhares para baixo do banco."
        },
        {
            "name": "Stiff na Máquina Smith",
            "focus": "Posterior + Glúteos",
            "notes": "Joelhos levemente flexionados (nunca travados). Desça até sentir alongamento. Costas SEMPRE retas."
        },
        {
            "name": "Glúteo na Máquina (Kick Back)",
            "focus": "Glúteo Máximo",
            "notes": "Apoie um joelho. Empurre a plataforma para trás. Não hiperextenda a lombar."
        },
    ],
    
    # ============ PANTURRILHA ============
    "panturrilha": [
        {
            "name": "Panturrilha no Leg Press",
            "focus": "Gastrocnêmio",
            "notes": "Apenas pontas dos pés na plataforma. Estenda tornozelo completamente. Amplitude completa."
        },
        {
            "name": "Panturrilha Sentado na Máquina",
            "focus": "Sóleo",
            "notes": "Sentado isola mais o sóleo (músculo profundo). Faça com controle, sem quicar."
        },
        {
            "name": "Panturrilha em Pé na Máquina",
            "focus": "Gastrocnêmio",
            "notes": "Ombros sob as almofadas. Eleve-se nas pontas dos pés. Desça alongando completamente."
        },
    ],
    
    # ============ ABDÔMEN ============
    "abdomen": [
        {
            "name": "Abdominal na Máquina",
            "focus": "Reto Abdominal",
            "notes": "Segure as manoplas acima. Flexione o tronco para baixo contraindo o abdômen. Não puxe com os braços."
        },
        {
            "name": "Abdominal na Polia Alta (Corda)",
            "focus": "Reto Abdominal",
            "notes": "Ajoelhado. Segure a corda atrás da cabeça. Flexione o tronco trazendo cotovelos aos joelhos."
        },
        {
            "name": "Prancha Isométrica",
            "focus": "Core Completo",
            "notes": "Apoio em antebraços e pontas dos pés. Corpo reto da cabeça aos calcanhares. Contraia abdômen e glúteos."
        },
        {
            "name": "Elevação de Pernas no Apoio",
            "focus": "Abdômen Inferior",
            "notes": "Apoie-se nos braços. Eleve as pernas estendidas ou flexionadas (mais fácil). Não balance."
        },
    ],
}

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

# ==================== DIAS DA SEMANA ====================
DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ==================== SPLITS DE TREINO ====================
SPLITS = {
    1: [{"name": "Full Body", "muscles": ["peito", "costas", "quadriceps", "ombros", "biceps", "triceps"]}],
    2: [
        {"name": "Upper", "muscles": ["peito", "costas", "ombros", "biceps", "triceps", "abdomen"], "is_upper_lower": True},
        {"name": "Lower", "muscles": ["quadriceps", "posterior", "panturrilha"]},
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
        {"name": "A - Peito", "muscles": ["peito"]},
        {"name": "B - Costas", "muscles": ["costas"]},
        {"name": "C - Ombros/Peito", "muscles": ["ombros", "peito"]},
        {"name": "D - Braços", "muscles": ["biceps", "triceps"]},
        {"name": "E - Quadríceps", "muscles": ["quadriceps", "panturrilha"]},
        {"name": "F - Posterior", "muscles": ["posterior"]},
        {"name": "G - Core", "muscles": ["abdomen"]},
    ],
}

# ==================== MÚSCULOS PEQUENOS ====================
SMALL_MUSCLES = ["ombros", "triceps", "biceps", "panturrilha", "abdomen"]

# ==================== EXERCÍCIOS COMPOSTOS ====================
COMPOUND_EXERCISES = [
    "agachamento", "stiff", "levantamento", "supino", "desenvolvimento",
    "remada", "puxada", "leg press", "hack"
]


def get_split_for_frequency(freq: int):
    """Retorna o split apropriado para a frequência de treino"""
    return SPLITS.get(freq, SPLITS[3])
