from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
import uuid
from datetime import datetime, timedelta
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Import auth service
from auth_service import AuthService, SignUpRequest, LoginRequest, decode_token

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Initialize auth service
auth_service = AuthService(db)

# ==================== MODELS ====================

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Dados Básicos
    name: str
    email: Optional[str] = None
    age: int
    sex: str  # "masculino" ou "feminino"
    
    # Dados Físicos
    height: float  # em cm
    weight: float  # em kg
    target_weight: Optional[float] = None  # em kg
    body_fat_percentage: Optional[float] = None  # percentual
    
    # Nível de Treino
    training_level: str  # "iniciante", "intermediario", "avancado"
    weekly_training_frequency: int  # dias por semana
    available_time_per_session: int  # minutos
    
    # Objetivo (3 opções apenas)
    goal: str  # "cutting", "bulking", "manutencao"
    
    # Restrições e Preferências
    dietary_restrictions: List[str] = Field(default_factory=list)  # ["vegetariano", "lactose", etc]
    food_preferences: List[str] = Field(default_factory=list)
    injury_history: List[str] = Field(default_factory=list)
    
    # Calculados
    tdee: Optional[float] = None  # Calorias diárias
    target_calories: Optional[float] = None  # Calorias ajustadas para objetivo
    macros: Optional[Dict[str, float]] = None  # {"protein": x, "carbs": y, "fat": z}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileCreate(BaseModel):
    id: Optional[str] = None  # Se fornecido, usa este ID (para vincular ao auth)
    name: str
    age: int
    sex: str
    height: float
    weight: float
    target_weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    training_level: str
    weekly_training_frequency: int
    available_time_per_session: int
    goal: str  # "cutting", "bulking", "manutencao"
    dietary_restrictions: List[str] = Field(default_factory=list)
    food_preferences: List[str] = Field(default_factory=list)
    injury_history: List[str] = Field(default_factory=list)

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    weight: Optional[float] = None
    target_weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    weekly_training_frequency: Optional[int] = None
    goal: Optional[str] = None  # "cutting", "bulking", "manutencao"
    dietary_restrictions: Optional[List[str]] = None
    food_preferences: Optional[List[str]] = None

# ==================== PROGRESS MODELS ====================

class QuestionnaireResponse(BaseModel):
    """Respostas do questionário de acompanhamento (0-10)"""
    diet: int = Field(ge=0, le=10, description="Como foi sua dieta? (0-10)")
    training: int = Field(ge=0, le=10, description="Como foram seus treinos? (0-10)")
    cardio: int = Field(ge=0, le=10, description="Como foi seu cardio? (0-10)")
    sleep: int = Field(ge=0, le=10, description="Como foi seu sono? (0-10)")
    hydration: int = Field(ge=0, le=10, description="Como foi sua hidratação? (0-10)")


class WeightRecord(BaseModel):
    """Registro de peso do usuário com questionário de acompanhamento"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    weight: float  # em kg
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    # Questionário de acompanhamento
    questionnaire: Optional[QuestionnaireResponse] = None
    # Média do questionário
    questionnaire_average: Optional[float] = None


class WeightRecordCreate(BaseModel):
    """Request para criar registro de peso com questionário"""
    weight: float  # em kg
    notes: Optional[str] = None
    # Questionário obrigatório
    questionnaire: QuestionnaireResponse


class WeightUpdateCheck(BaseModel):
    """Resposta para verificação se pode atualizar peso"""
    can_update: bool
    reason: Optional[str] = None
    last_update: Optional[datetime] = None
    next_update_allowed: Optional[datetime] = None
    days_until_next_update: Optional[int] = None


class NotificationReminder(BaseModel):
    """Lembrete/notificação para o usuário"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # "weight_update", "general"
    title: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = None
    read: bool = False
    action_url: Optional[str] = None


# ==================== WATER TRACKER MODELS ====================

class WaterSodiumEntry(BaseModel):
    """Entrada de consumo de água/sódio"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    
    # Água consumida (em ml)
    water_ml: int = 0
    water_target_ml: int = 3000  # Meta diária padrão
    
    # Sódio consumido (em mg)
    sodium_mg: int = 0
    sodium_target_mg: int = 2000  # Meta diária padrão
    
    # Flags de segurança
    water_below_minimum: bool = False  # Abaixo de 2L
    sodium_below_minimum: bool = False  # Abaixo de 500mg
    
    notes: Optional[str] = None


class WaterSodiumEntryCreate(BaseModel):
    """Request para adicionar água/sódio"""
    water_ml: Optional[int] = None
    sodium_mg: Optional[int] = None
    notes: Optional[str] = None


# ==================== SETTINGS MODELS ====================

class MealTimeConfig(BaseModel):
    """Configuration for a single meal time"""
    name: str
    time: str  # Format: "HH:MM"

class UserSettings(BaseModel):
    """User settings for theme and privacy"""
    user_id: str
    theme_preference: str = "system"  # "system", "light", "dark"
    privacy_analytics: bool = True
    privacy_personalization: bool = True
    privacy_notifications: bool = True
    notifications_enabled: bool = True
    language: str = "pt-BR"  # "pt-BR", "en-US", "es-ES"
    meal_count: int = 6  # 4, 5, or 6 meals per day
    meal_times: List[MealTimeConfig] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSettingsUpdate(BaseModel):
    """Partial update for settings"""
    theme_preference: Optional[str] = None
    privacy_analytics: Optional[bool] = None
    privacy_personalization: Optional[bool] = None
    privacy_notifications: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    language: Optional[str] = None
    meal_count: Optional[int] = None
    meal_times: Optional[List[MealTimeConfig]] = None

# ==================== CÁLCULOS TDEE ====================

def calculate_bmr(weight: float, height: float, age: int, sex: str) -> float:
    """
    Calcula Taxa Metabólica Basal usando fórmula de Mifflin-St Jeor
    """
    if sex.lower() == "masculino":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # feminino
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return bmr

def calculate_tdee(bmr: float, training_frequency: int, training_level: str) -> float:
    """
    Calcula TDEE (Total Daily Energy Expenditure) baseado em atividade
    """
    # Fatores de atividade ajustados por nível de treino
    activity_factors = {
        "iniciante": {
            0: 1.2,   # sedentário
            1: 1.3,
            2: 1.35,
            3: 1.4,
            4: 1.5,
            5: 1.55,
            6: 1.65,
            7: 1.7
        },
        "intermediario": {
            0: 1.2,
            1: 1.35,
            2: 1.4,
            3: 1.5,
            4: 1.55,
            5: 1.65,
            6: 1.75,
            7: 1.8
        },
        "avancado": {
            0: 1.2,
            1: 1.4,
            2: 1.5,
            3: 1.6,
            4: 1.7,
            5: 1.8,
            6: 1.9,
            7: 2.0
        }
    }
    
    factor = activity_factors.get(training_level, activity_factors["intermediario"]).get(training_frequency, 1.5)
    return bmr * factor

def calculate_target_calories(tdee: float, goal: str, weight: float, competition_phase: Optional[str] = None) -> float:
    """
    Ajusta calorias baseado no objetivo e fase de competição.
    
    REGRAS PARA ATLETA/COMPETIÇÃO:
    - off_season: superávit de +7.5% (lean bulk, >16 semanas)
    - pre_contest: déficit progressivo (-15 a -20%, 2-16 semanas)
    - peak_week: déficit muito agressivo (-25%) + manipulação (<2 semanas)
    - post_show: superávit moderado (+10%) para recuperação
    """
    if goal == "cutting":
        # Déficit de 15-20% para perda de gordura
        return tdee * 0.82  # 18% de déficit
    elif goal == "bulking":
        # Superávit de 10-15% para ganho de massa
        return tdee * 1.12  # 12% de superávit
    else:  # manutenção
        return tdee

def calculate_macros(target_calories: float, weight: float, goal: str) -> Dict[str, float]:
    """
    Calcula distribuição de macronutrientes baseado no objetivo.
    
    - cutting: P=2.2g/kg, G=0.8g/kg, C=restante
    - bulking: P=2.0g/kg, G=1.0g/kg, C=restante
    - manutencao: P=1.8g/kg, G=1.0g/kg, C=restante
    """
    if goal == "cutting":
        # Alto proteína, moderado carbo, baixo gordura
        protein_g = weight * 2.2  # 2.2g por kg
        fat_g = weight * 0.8      # 0.8g por kg
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = max(0, carbs_cal / 4)
    elif goal == "bulking":
        # Alto proteína, alto carbo, moderado gordura
        protein_g = weight * 2.0  # 2g por kg
        fat_g = weight * 1.0      # 1g por kg
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = max(0, carbs_cal / 4)
    else:  # manutenção
        protein_g = weight * 1.8
        fat_g = weight * 1.0
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = max(0, carbs_cal / 4)
    
    return {
        "protein": round(protein_g, 1),
        "carbs": round(carbs_g, 1),
        "fat": round(fat_g, 1)
    }

# ==================== ROUTES ====================
    days = delta.days
    weeks = days // 7
    
    # Determina a fase baseado nas semanas
    if weeks > 16:
        return "off_season", weeks
    elif weeks >= 2:
        return "pre_contest", weeks
    else:
        # Menos de 2 semanas (14 dias) = Peak Week
        return "peak_week", weeks

def derive_phase_from_weeks(weeks: int) -> str:
    """Derives competition phase from weeks to competition (legacy)"""
    if weeks < 0:
        return "post_show"
    elif weeks > 16:
        return "off_season"
    elif weeks >= 2:
        return "pre_contest"
    else:
        return "peak_week"

# ==================== ROUTES ====================

@api_router.post("/user/profile", response_model=UserProfile)
async def create_or_update_user_profile(profile_data: UserProfileCreate):
    """
    Cria ou atualiza perfil de usuário (IDEMPOTENT - usa upsert).
    Calcula TDEE e macros automaticamente.
    """
    # OBRIGATÓRIO: ID do usuário autenticado
    if not profile_data.id:
        raise HTTPException(
            status_code=400,
            detail="Campo 'id' é obrigatório (ID do usuário autenticado)"
        )
    
    # Cria perfil completo
    profile_dict = profile_data.dict()
    profile_dict["id"] = profile_data.id
    
    # Calcula BMR
    bmr = calculate_bmr(
        weight=profile_data.weight,
        height=profile_data.height,
        age=profile_data.age,
        sex=profile_data.sex
    )
    
    # Calcula TDEE
    tdee = calculate_tdee(
        bmr=bmr,
        training_frequency=profile_data.weekly_training_frequency,
        training_level=profile_data.training_level
    )
    
    # Ajusta calorias para objetivo
    target_calories = calculate_target_calories(
        tdee=tdee,
        goal=profile_data.goal,
        weight=profile_data.weight
    )
    
    # Calcula macros
    macros = calculate_macros(
        target_calories=target_calories,
        weight=profile_data.weight,
        goal=profile_data.goal
    )
    
    # Adiciona campos calculados
    profile_dict["tdee"] = round(tdee, 0)
    profile_dict["target_calories"] = round(target_calories, 0)
    profile_dict["macros"] = macros
    profile_dict["updated_at"] = datetime.utcnow()
    
    # UPSERT: Atualiza se existe, cria se não existe (IDEMPOTENT)
    profile_dict["_id"] = profile_data.id
    
    await db.user_profiles.update_one(
        {"_id": profile_data.id},
        {"$set": profile_dict, "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True
    )
    
    # Vincula profile ao users_auth
    await db.users_auth.update_one(
        {"_id": profile_data.id},
        {"$set": {"profile_id": profile_data.id, "updated_at": datetime.utcnow()}}
    )
    
    logger.info(f"Profile upserted for user {profile_data.id}")
    
    # Retorna perfil
    return UserProfile(**profile_dict)

@api_router.get("/user/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """
    Busca perfil do usuário
    """
    profile = await db.user_profiles.find_one({"_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    
    profile["id"] = profile["_id"]
    return UserProfile(**profile)

@api_router.put("/user/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, update_data: UserProfileUpdate):
    """
    Atualiza perfil do usuário e recalcula métricas.
    
    MODO ATLETA AUTOMÁTICO:
    - Se athlete_competition_date for atualizada, recalcula a fase automaticamente
    - Fase é derivada da data do campeonato, não precisa ser informada manualmente
    """
    # Busca perfil existente
    existing_profile = await db.user_profiles.find_one({"_id": user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    
    # Atualiza dados fornecidos
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if update_dict:
        current_profile = UserProfile(**existing_profile)
        
        # ==================== MODO ATLETA - DATA DO CAMPEONATO ====================
        # Se a data de competição foi atualizada, recalcula a fase automaticamente
        comp_date_str = update_dict.get("athlete_competition_date") or update_dict.get("competition_date")
        new_goal = update_dict.get("goal", current_profile.goal)
        
        if comp_date_str or new_goal == "atleta":
            # Se tem nova data, parseia e calcula fase
            if comp_date_str:
                try:
                    if isinstance(comp_date_str, str):
                        parsed_date = datetime.fromisoformat(comp_date_str.replace('Z', '+00:00'))
                    else:
                        parsed_date = comp_date_str
                    
                    # Calcula fase e semanas AUTOMATICAMENTE
                    competition_phase, weeks_to_competition = derive_phase_from_date(parsed_date)
                    
                    update_dict["athlete_competition_date"] = parsed_date
                    update_dict["competition_date"] = parsed_date
                    update_dict["competition_phase"] = competition_phase
                    update_dict["weeks_to_competition"] = weeks_to_competition
                    update_dict["athlete_mode"] = True
                    
                    logger.info(f"ATLETA {user_id}: Data atualizada para {parsed_date.date()}, Fase={competition_phase}, Semanas={weeks_to_competition}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao parsear data de competição: {e}")
            
            # Se é atleta e tem data existente mas não nova, recalcula fase
            elif new_goal == "atleta" and not comp_date_str:
                existing_date = existing_profile.get("athlete_competition_date") or existing_profile.get("competition_date")
                if existing_date:
                    competition_phase, weeks_to_competition = derive_phase_from_date(existing_date)
                    update_dict["competition_phase"] = competition_phase
                    update_dict["weeks_to_competition"] = weeks_to_competition
        
        # Se peso, goal ou competition_phase mudou, recalcula macros
        if "weight" in update_dict or "goal" in update_dict or "competition_phase" in update_dict:
            # Usa novos valores ou mantém existentes
            new_weight = update_dict.get("weight", current_profile.weight)
            new_frequency = update_dict.get("weekly_training_frequency", current_profile.weekly_training_frequency)
            new_phase = update_dict.get("competition_phase", current_profile.competition_phase)
            
            # Recalcula
            bmr = calculate_bmr(
                weight=new_weight,
                height=current_profile.height,
                age=current_profile.age,
                sex=current_profile.sex
            )
            tdee = calculate_tdee(bmr, new_frequency, current_profile.training_level)
            target_calories = calculate_target_calories(tdee, new_goal, new_weight, new_phase)
            macros = calculate_macros(target_calories, new_weight, new_goal, new_phase)
            
            update_dict["tdee"] = round(tdee, 0)
            update_dict["target_calories"] = round(target_calories, 0)
            update_dict["macros"] = macros
        
        update_dict["updated_at"] = datetime.utcnow()
        
        await db.user_profiles.update_one(
            {"_id": user_id},
            {"$set": update_dict}
        )
    
    # Retorna perfil atualizado
    updated_profile = await db.user_profiles.find_one({"_id": user_id})
    updated_profile["id"] = updated_profile["_id"]
    return UserProfile(**updated_profile)

@api_router.get("/")
async def root():
    return {"message": "LAF API - Sistema de Dieta e Treino Personalizado"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LAF Backend"}

# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/signup")
async def signup(request: SignUpRequest):
    """
    Cadastra novo usuário com email e senha.
    Retorna token JWT para autenticação.
    """
    try:
        result = await auth_service.signup(request.email, request.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/auth/login")
async def login(request: LoginRequest):
    """
    Autentica usuário existente.
    Retorna token JWT.
    """
    try:
        result = await auth_service.login(request.email, request.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@api_router.get("/auth/validate")
async def validate_token(authorization: Optional[str] = Header(None)):
    """
    Valida token JWT.
    Retorna dados do usuário se válido.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    # Remove "Bearer " prefix if present
    token = authorization.replace("Bearer ", "")
    
    result = await auth_service.validate_token(token)
    if not result:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return result

@api_router.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Marca logout do usuário (para tracking).
    """
    if authorization:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if payload:
            await auth_service.logout(payload.sub)
    
    return {"message": "Logout realizado com sucesso"}

# ==================== DIET ENDPOINTS ====================

@api_router.post("/diet/generate")
async def generate_diet(user_id: str):
    """
    Gera um plano de dieta personalizado.
    
    ✅ FILOSOFIA V14 BULLETPROOF:
    - NUNCA retorna erro por validação de macros
    - Dieta sempre válida e utilizável
    - Sistema auto-corrige automaticamente
    - Suporta 4, 5 ou 6 refeições configuráveis
    
    TOLERÂNCIAS AMPLAS (para garantir sucesso):
    - Proteína: ±20% ou 30g
    - Carbs: ±20% ou 50g  
    - Gordura: ±30% ou 30g
    - Calorias: ±15% ou 300kcal
    """
    try:
        # Busca perfil do usuário
        user_profile = await db.user_profiles.find_one({"_id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
        # Busca configurações do usuário (meal_count e meal_times)
        user_settings = await db.user_settings.find_one({"user_id": user_id})
        meal_count = 6  # Padrão
        meal_times = None
        
        if user_settings:
            meal_count = user_settings.get('meal_count', 6)
            meal_times = user_settings.get('meal_times', None)
        
        # Valida meal_count
        if meal_count not in [4, 5, 6]:
            meal_count = 6
        
        # Importa serviço de dieta
        from diet_service import DietAIService
        
        diet_service = DietAIService()
        
        # Gera plano de dieta (NUNCA falha - sistema bulletproof)
        diet_plan = diet_service.generate_diet_plan(
            user_profile=dict(user_profile),
            target_calories=user_profile.get('target_calories', 2000),
            target_macros=user_profile.get('macros', {"protein": 150, "carbs": 200, "fat": 60}),
            meal_count=meal_count,
            meal_times=meal_times
        )
        
        # VALIDAÇÃO INFORMATIVA (apenas log, não bloqueia)
        # Soma REAL dos alimentos (não os valores pre-computados)
        real_protein = sum(sum(f["protein"] for f in m.foods) for m in diet_plan.meals)
        real_carbs = sum(sum(f["carbs"] for f in m.foods) for m in diet_plan.meals)
        real_fat = sum(sum(f["fat"] for f in m.foods) for m in diet_plan.meals)
        real_cal = sum(sum(f["calories"] for f in m.foods) for m in diet_plan.meals)
        
        target_macros = user_profile.get('macros', {"protein": 150, "carbs": 200, "fat": 60})
        target_cal = user_profile.get('target_calories', 2000)
        
        # Calcula diferenças (apenas para logging)
        p_diff = abs(real_protein - target_macros["protein"])
        c_diff = abs(real_carbs - target_macros["carbs"])
        f_diff = abs(real_fat - target_macros["fat"])
        cal_diff = abs(real_cal - target_cal)
        
        # Tolerâncias MUITO amplas - a dieta é válida se tem alimentos
        # O sistema bulletproof garante que NUNCA falha
        max_p = max(30, target_macros["protein"] * 0.20)  # 20% ou 30g
        max_c = max(50, target_macros["carbs"] * 0.20)    # 20% ou 50g
        max_f = max(30, target_macros["fat"] * 0.30)      # 30% ou 30g
        max_cal = max(300, target_cal * 0.15)             # 15% ou 300kcal
        
        # LOG (mas NÃO bloqueia)
        if p_diff > max_p or c_diff > max_c or f_diff > max_f or cal_diff > max_cal:
            logger.warning(
                f"DIETA COM VARIAÇÃO ALTA - Targets: P{target_macros['protein']}g C{target_macros['carbs']}g F{target_macros['fat']}g {target_cal}kcal | "
                f"Computed: P{real_protein:.1f}g C{real_carbs:.1f}g F{real_fat:.1f}g {real_cal:.1f}kcal | "
                f"Diffs: P{p_diff:.1f}g C{c_diff:.1f}g F{f_diff:.1f}g {cal_diff:.1f}kcal"
            )
        
        # ✅ VALIDAÇÃO BULLETPROOF: Garante que dieta tem conteúdo
        # Se não tem meals, ERRO (mas isso nunca deve acontecer com sistema V14)
        if not diet_plan.meals or len(diet_plan.meals) == 0:
            logger.error("ERRO CRÍTICO: Dieta sem refeições!")
            raise HTTPException(status_code=500, detail="Erro ao gerar dieta: nenhuma refeição criada")
        
        # Verifica se todas as refeições têm alimentos
        for i, meal in enumerate(diet_plan.meals):
            if not meal.foods or len(meal.foods) == 0:
                logger.error(f"ERRO CRÍTICO: Refeição {i} vazia!")
                raise HTTPException(status_code=500, detail=f"Erro ao gerar dieta: refeição {meal.name} vazia")
        
        # Salva no banco (IDEMPOTENT - sobrescreve dieta existente)
        diet_dict = diet_plan.dict()
        
        # Remove dieta existente do usuário antes de inserir nova
        await db.diet_plans.delete_many({"user_id": user_id})
        
        # Define o _id como o id da dieta
        diet_dict["_id"] = diet_dict["id"]
        
        # Insere nova dieta
        await db.diet_plans.insert_one(diet_dict)
        
        logger.info(
            f"DIETA V14 GERADA COM SUCESSO - User: {user_id} | "
            f"Targets: P{target_macros['protein']}g C{target_macros['carbs']}g F{target_macros['fat']}g {target_cal}kcal | "
            f"Computed: P{real_protein:.1f}g C{real_carbs:.1f}g F{real_fat:.1f}g {real_cal:.1f}kcal"
        )
        
        return diet_plan
        
    except HTTPException:
        raise
    except ValueError as e:
        # Erro de validação do serviço de dieta
        logger.error(f"Erro de validação ao gerar dieta: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao gerar dieta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dieta: {str(e)}")

@api_router.get("/diet/{user_id}")
async def get_user_diet(user_id: str):
    """
    Busca o plano de dieta mais recente do usuário
    """
    diet_plan = await db.diet_plans.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if not diet_plan:
        raise HTTPException(status_code=404, detail="Plano de dieta não encontrado")
    
    diet_plan["id"] = diet_plan["_id"]
    return diet_plan


@api_router.delete("/diet/{user_id}")
async def delete_user_diet(user_id: str):
    """
    Deleta a dieta do usuário para permitir regeneração.
    Usado quando as configurações de refeições mudam.
    """
    result = await db.diet_plans.delete_many({"user_id": user_id})
    
    logger.info(f"Deleted {result.deleted_count} diet plans for user {user_id}")
    
    return {"message": "Dieta deletada com sucesso", "deleted_count": result.deleted_count}


class FoodSubstitutionRequest(BaseModel):
    """Request para substituir alimento na dieta"""
    meal_index: int  # Índice da refeição (0-4)
    food_index: int  # Índice do alimento na refeição
    new_food_key: str  # Chave do novo alimento


@api_router.get("/diet/{diet_id}/substitutes/{food_key}")
async def get_food_substitutes(diet_id: str, food_key: str):
    """
    Retorna lista de alimentos substitutos da mesma categoria.
    Calcula automaticamente a quantidade para manter os macros.
    """
    from diet_service import FOODS
    
    # Busca dieta
    diet_plan = await db.diet_plans.find_one({"_id": diet_id})
    if not diet_plan:
        raise HTTPException(status_code=404, detail="Dieta não encontrada")
    
    # Encontra o alimento original
    original_food = None
    for meal in diet_plan.get("meals", []):
        for food in meal.get("foods", []):
            if food.get("key") == food_key:
                original_food = food
                break
        if original_food:
            break
    
    if not original_food:
        raise HTTPException(status_code=404, detail="Alimento não encontrado na dieta")
    
    # Obtém categoria do alimento
    category = original_food.get("category", "")
    if not category or category not in ["protein", "carb", "fat", "fruit", "vegetable"]:
        raise HTTPException(status_code=400, detail="Categoria do alimento não suporta substituição")
    
    # Busca alimentos da mesma categoria
    substitutes = []
    for key, food_data in FOODS.items():
        if food_data.get("category") == category and key != food_key:
            # Calcula quantidade para manter o macro principal
            if category == "protein":
                # Mantém proteína
                target_macro = original_food.get("protein", 0)
                macro_per_100 = food_data.get("p", 1)
            elif category == "carb":
                # Mantém carboidrato
                target_macro = original_food.get("carbs", 0)
                macro_per_100 = food_data.get("c", 1)
            elif category == "fat":
                # Mantém gordura
                target_macro = original_food.get("fat", 0)
                macro_per_100 = food_data.get("f", 1)
            elif category == "fruit":
                # Mantém carboidrato (frutas são fonte de carb)
                target_macro = original_food.get("carbs", 0)
                macro_per_100 = food_data.get("c", 1)
            elif category == "vegetable":
                # Para vegetais, mantém a mesma quantidade em gramas (não têm macro principal)
                target_macro = original_food.get("grams", 100)
                macro_per_100 = 100  # Proporção 1:1 em gramas
            else:
                continue
            
            if macro_per_100 <= 0:
                continue
            
            # Calcula nova quantidade (múltiplo de 10)
            if category == "vegetable":
                new_grams = original_food.get("grams", 100)  # Mantém mesma quantidade
            else:
                new_grams = round((target_macro / macro_per_100) * 100 / 10) * 10
            new_grams = max(10, min(500, new_grams))  # Limita entre 10g e 500g
            
            # Calcula novos macros
            ratio = new_grams / 100
            new_protein = round(food_data.get("p", 0) * ratio)
            new_carbs = round(food_data.get("c", 0) * ratio)
            new_fat = round(food_data.get("f", 0) * ratio)
            new_calories = round((food_data.get("p", 0) * 4 + food_data.get("c", 0) * 4 + food_data.get("f", 0) * 9) * ratio)
            
            substitutes.append({
                "key": key,
                "name": food_data.get("name", key),
                "quantity": f"{new_grams}g",
                "grams": new_grams,
                "protein": new_protein,
                "carbs": new_carbs,
                "fat": new_fat,
                "calories": new_calories,
                "category": category
            })
    
    return {
        "original": original_food,
        "substitutes": substitutes,
        "category": category
    }


@api_router.put("/diet/{diet_id}/substitute")
async def substitute_food(diet_id: str, request: FoodSubstitutionRequest):
    """
    Substitui um alimento na dieta mantendo os macros.
    A substituição é permanente.
    """
    from diet_service import FOODS
    
    # Busca dieta
    diet_plan = await db.diet_plans.find_one({"_id": diet_id})
    if not diet_plan:
        raise HTTPException(status_code=404, detail="Dieta não encontrada")
    
    meals = diet_plan.get("meals", [])
    
    # Valida índices
    if request.meal_index < 0 or request.meal_index >= len(meals):
        raise HTTPException(status_code=400, detail="Índice de refeição inválido")
    
    meal = meals[request.meal_index]
    foods = meal.get("foods", [])
    
    if request.food_index < 0 or request.food_index >= len(foods):
        raise HTTPException(status_code=400, detail="Índice de alimento inválido")
    
    # Verifica se novo alimento existe
    if request.new_food_key not in FOODS:
        raise HTTPException(status_code=400, detail="Alimento substituto não encontrado")
    
    original_food = foods[request.food_index]
    new_food_data = FOODS[request.new_food_key]
    
    # Verifica mesma categoria
    if original_food.get("category") != new_food_data.get("category"):
        raise HTTPException(status_code=400, detail="Alimento deve ser da mesma categoria")
    
    category = original_food.get("category")
    
    # Calcula quantidade para manter macro principal
    if category == "protein":
        target_macro = original_food.get("protein", 0)
        macro_per_100 = new_food_data.get("p", 1)
    elif category == "carb":
        target_macro = original_food.get("carbs", 0)
        macro_per_100 = new_food_data.get("c", 1)
    elif category == "fat":
        target_macro = original_food.get("fat", 0)
        macro_per_100 = new_food_data.get("f", 1)
    elif category == "fruit":
        target_macro = original_food.get("carbs", 0)
        macro_per_100 = new_food_data.get("c", 1)
    else:
        raise HTTPException(status_code=400, detail="Categoria não suporta substituição")
    
    if macro_per_100 <= 0:
        raise HTTPException(status_code=400, detail="Alimento substituto inválido para esta categoria")
    
    # Calcula nova quantidade (múltiplo de 10)
    new_grams = round((target_macro / macro_per_100) * 100 / 10) * 10
    new_grams = max(10, min(500, new_grams))
    
    # Calcula novos macros
    ratio = new_grams / 100
    new_protein = round(new_food_data.get("p", 0) * ratio)
    new_carbs = round(new_food_data.get("c", 0) * ratio)
    new_fat = round(new_food_data.get("f", 0) * ratio)
    new_calories = round((new_food_data.get("p", 0) * 4 + new_food_data.get("c", 0) * 4 + new_food_data.get("f", 0) * 9) * ratio)
    
    # Cria novo objeto de alimento
    new_food = {
        "key": request.new_food_key,
        "name": new_food_data.get("name", request.new_food_key),
        "quantity": f"{new_grams}g",
        "grams": new_grams,
        "protein": new_protein,
        "carbs": new_carbs,
        "fat": new_fat,
        "calories": new_calories,
        "category": category
    }
    
    # Atualiza alimento na lista
    foods[request.food_index] = new_food
    
    # Recalcula totais da refeição
    meal_protein = sum(f.get("protein", 0) for f in foods)
    meal_carbs = sum(f.get("carbs", 0) for f in foods)
    meal_fat = sum(f.get("fat", 0) for f in foods)
    meal_calories = sum(f.get("calories", 0) for f in foods)
    
    meal["foods"] = foods
    meal["total_calories"] = meal_calories
    meal["macros"] = {"protein": meal_protein, "carbs": meal_carbs, "fat": meal_fat}
    
    # Atualiza refeição na lista
    meals[request.meal_index] = meal
    
    # Recalcula totais da dieta
    total_protein = sum(m.get("macros", {}).get("protein", 0) for m in meals)
    total_carbs = sum(m.get("macros", {}).get("carbs", 0) for m in meals)
    total_fat = sum(m.get("macros", {}).get("fat", 0) for m in meals)
    total_calories = sum(m.get("total_calories", 0) for m in meals)
    
    # Atualiza no banco
    await db.diet_plans.update_one(
        {"_id": diet_id},
        {"$set": {
            "meals": meals,
            "computed_calories": total_calories,
            "computed_macros": {"protein": total_protein, "carbs": total_carbs, "fat": total_fat},
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Retorna dieta atualizada
    updated_diet = await db.diet_plans.find_one({"_id": diet_id})
    updated_diet["id"] = updated_diet["_id"]
    
    logger.info(f"Food substituted in diet {diet_id}: {original_food.get('name')} -> {new_food['name']}")
    
    return updated_diet

# ==================== PROGRESS ENDPOINTS ====================

@api_router.get("/progress/weight/{user_id}/can-update")
async def check_can_update_weight(user_id: str):
    """
    Verifica se o usuário pode atualizar o peso.
    
    REGRAS:
    - TODOS: Bloqueio semanal (7 dias) - padronizado para melhor acompanhamento
    
    Retorna informações sobre quando pode atualizar novamente.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueio de 7 dias para todos
    block_days = 7
    is_athlete = user.get("goal") == "atleta" or user.get("athlete_mode", False)
    
    # Busca último registro
    last_record = await db.weight_records.find_one(
        {"user_id": user_id},
        sort=[("recorded_at", -1)]
    )
    
    if not last_record:
        # Primeiro registro - verifica dias desde cadastro
        if user.get("created_at"):
            days_since_creation = (datetime.utcnow() - user["created_at"]).days
            if days_since_creation < block_days:
                days_remaining = block_days - days_since_creation
                next_update = user["created_at"] + timedelta(days=block_days)
                return WeightUpdateCheck(
                    can_update=False,
                    reason=f"Aguarde {days_remaining} dia(s) para o primeiro registro de progresso",
                    last_update=user["created_at"],
                    next_update_allowed=next_update,
                    days_until_next_update=days_remaining
                )
        return WeightUpdateCheck(can_update=True, reason="Primeiro registro disponível")
    
    # Calcula dias desde último registro
    days_since_last = (datetime.utcnow() - last_record["recorded_at"]).days
    
    if days_since_last < block_days:
        days_remaining = block_days - days_since_last
        next_update = last_record["recorded_at"] + timedelta(days=block_days)
        return WeightUpdateCheck(
            can_update=False,
            reason=f"Registro semanal. Aguarde {days_remaining} dia(s)",
            last_update=last_record["recorded_at"],
            next_update_allowed=next_update,
            days_until_next_update=days_remaining
        )
    
    return WeightUpdateCheck(
        can_update=True,
        reason="Pode registrar novo peso",
        last_update=last_record["recorded_at"],
        next_update_allowed=datetime.utcnow(),
        days_until_next_update=0
    )


@api_router.post("/progress/weight/{user_id}")
async def record_weight(user_id: str, record: WeightRecordCreate):
    """
    Registra peso do usuário COM questionário obrigatório de acompanhamento.
    
    RESTRIÇÕES:
    - TODOS: Bloqueio semanal (7 dias) para melhor acompanhamento
    
    QUESTIONÁRIO (0-10):
    - Dieta: Como seguiu a dieta?
    - Treino: Como foram os treinos?
    - Cardio: Como foi o cardio?
    - Sono: Como foi o sono?
    - Hidratação: Como foi a hidratação?
    
    MODO ATLETA AUTOMÁTICO:
    - Verifica se athlete_mode = true
    - Calcula fase atual baseada na data do campeonato
    - Ajusta APENAS quantidades da dieta existente
    - NUNCA gera nova dieta ou troca alimentos
    """
    from diet_service import evaluate_progress, evaluate_athlete_progress, adjust_diet_quantities
    
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueio de 7 dias para todos
    block_days = 7
    is_athlete = user.get("goal") == "atleta" or user.get("athlete_mode", False)
    
    # Verifica último registro
    last_record = await db.weight_records.find_one(
        {"user_id": user_id},
        sort=[("recorded_at", -1)]
    )
    
    if last_record:
        days_since_last = (datetime.utcnow() - last_record["recorded_at"]).days
        if days_since_last < block_days:
            days_remaining = block_days - days_since_last
            raise HTTPException(
                status_code=400,
                detail=f"Aguarde mais {days_remaining} dias para o próximo registro. Registro semanal."
            )
    
    # Valida peso
    if record.weight < 30 or record.weight > 300:
        raise HTTPException(status_code=400, detail="Peso deve estar entre 30kg e 300kg")
    
    # Calcula média do questionário
    q = record.questionnaire
    questionnaire_avg = round((q.diet + q.training + q.cardio + q.sleep + q.hydration) / 5, 1)
    
    # Determina fase do atleta (se aplicável)
    athlete_phase = None
    if is_athlete:
        comp_date = user.get("athlete_competition_date") or user.get("competition_date")
        if comp_date:
            athlete_phase, _ = derive_phase_from_date(comp_date)
        else:
            athlete_phase = user.get("competition_phase", "off_season")
    
    # Cria registro completo
    weight_record = WeightRecord(
        user_id=user_id,
        weight=round(record.weight, 1),
        notes=record.notes,
        questionnaire=record.questionnaire,
        athlete_phase=athlete_phase,
        questionnaire_average=questionnaire_avg
    )
    
    # Salva no banco
    record_dict = weight_record.dict()
    record_dict["_id"] = record_dict["id"]
    await db.weight_records.insert_one(record_dict)
    
    # Atualiza peso no perfil do usuário
    await db.user_profiles.update_one(
        {"_id": user_id},
        {"$set": {"weight": round(record.weight, 1), "updated_at": datetime.utcnow()}}
    )
    
    logger.info(f"Weight recorded for user {user_id}: {record.weight}kg")
    
    # ==================== AVALIAÇÃO DE PROGRESSO ====================
    diet_adjusted = False
    adjustment_message = None
    phase = None
    adjustment_percent = None
    
    # Só avalia se tiver registro anterior para comparar
    if last_record:
        previous_weight = last_record.get("weight", record.weight)
        current_weight = record.weight
        goal = user.get("goal", "manutencao")
        athlete_mode = user.get("athlete_mode", False)
        
        # ==================== MODO ATLETA ====================
        if athlete_mode or goal == "atleta":
            # Recalcula fase atual baseado na data do campeonato
            comp_date = user.get("athlete_competition_date") or user.get("competition_date")
            
            if comp_date:
                # Calcula fase atual
                current_phase, weeks_remaining = derive_phase_from_date(comp_date)
                
                # Atualiza fase no perfil se mudou
                old_phase = user.get("competition_phase")
                if current_phase != old_phase:
                    await db.user_profiles.update_one(
                        {"_id": user_id},
                        {"$set": {
                            "competition_phase": current_phase,
                            "last_competition_phase": old_phase,
                            "weeks_to_competition": weeks_remaining,
                            "updated_at": datetime.utcnow()
                        }}
                    )
                    logger.info(f"ATLETA {user_id}: Fase mudou de {old_phase} para {current_phase} ({weeks_remaining} semanas)")
                
                phase = current_phase
            else:
                # Sem data = usa fase salva ou off_season
                phase = user.get("competition_phase", "off_season")
            
            # Avalia progresso com lógica de ATLETA
            progress_eval = evaluate_athlete_progress(
                phase=phase,
                previous_weight=previous_weight,
                current_weight=current_weight
            )
            
            logger.info(f"ATLETA progress evaluation for {user_id}: {progress_eval}")
            
        else:
            # Avalia progresso normal (não atleta)
            progress_eval = evaluate_progress(
                goal=goal,
                previous_weight=previous_weight,
                current_weight=current_weight
            )
            
            logger.info(f"Progress evaluation for {user_id}: {progress_eval}")
        
        # Se precisa ajustar, atualiza a dieta
        if progress_eval.get("needs_adjustment"):
            # Busca dieta atual
            current_diet = await db.diet_plans.find_one({"user_id": user_id})
            
            if current_diet:
                # Ajusta APENAS quantidades (NUNCA troca alimentos)
                adjusted_diet = adjust_diet_quantities(
                    diet_plan=current_diet,
                    adjustment_type=progress_eval["adjustment_type"],
                    adjustment_percent=progress_eval["adjustment_percent"]
                )
                
                # Salva dieta ajustada (overwrite)
                adjusted_diet["adjusted_at"] = datetime.utcnow()
                adjusted_diet["adjustment_reason"] = progress_eval["reason"]
                if phase:
                    adjusted_diet["athlete_phase"] = phase
                
                await db.diet_plans.replace_one(
                    {"_id": current_diet["_id"]},
                    adjusted_diet,
                    upsert=True
                )
                
                diet_adjusted = True
                adjustment_message = progress_eval["reason"]
                adjustment_percent = progress_eval.get("adjustment_percent")
                
                logger.info(f"Diet adjusted for user {user_id}: {progress_eval['adjustment_type']} by {progress_eval['adjustment_percent']}%")
    
    # Retorna resultado com informação completa
    return {
        "record": weight_record,
        "diet_adjusted": diet_adjusted,
        "phase": phase,
        "adjustment_percent": adjustment_percent,
        "message": adjustment_message or "Peso registrado com sucesso"
    }


@api_router.get("/progress/weight/{user_id}")
async def get_weight_history(user_id: str, days: int = 365):
    """
    Retorna histórico de peso do usuário com questionários e gráficos.
    Default: último ano (365 dias) para visualização completa.
    
    Retorna:
    - Histórico completo de peso com questionários
    - Estatísticas de evolução
    - Médias dos questionários por período
    - Dados formatados para gráficos
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueio de 7 dias para todos
    block_days = 7
    is_athlete = user.get("goal") == "atleta" or user.get("athlete_mode", False)
    
    # Busca registros dos últimos N dias
    from_date = datetime.utcnow() - timedelta(days=days)
    
    records = await db.weight_records.find(
        {"user_id": user_id, "recorded_at": {"$gte": from_date}}
    ).sort("recorded_at", 1).to_list(length=365)
    
    # Formata resposta com dados completos
    history = []
    questionnaire_totals = {"diet": 0, "training": 0, "cardio": 0, "sleep": 0, "hydration": 0}
    questionnaire_count = 0
    
    for r in records:
        record_data = {
            "id": r["_id"],
            "weight": r["weight"],
            "recorded_at": r["recorded_at"].isoformat(),
            "notes": r.get("notes"),
            "athlete_phase": r.get("athlete_phase"),
            "questionnaire_average": r.get("questionnaire_average"),
        }
        
        # Inclui questionário se existir
        if r.get("questionnaire"):
            q = r["questionnaire"]
            record_data["questionnaire"] = q
            
            # Soma para média geral
            if isinstance(q, dict):
                questionnaire_totals["diet"] += q.get("diet", 0)
                questionnaire_totals["training"] += q.get("training", 0)
                questionnaire_totals["cardio"] += q.get("cardio", 0)
                questionnaire_totals["sleep"] += q.get("sleep", 0)
                questionnaire_totals["hydration"] += q.get("hydration", 0)
                questionnaire_count += 1
        
        history.append(record_data)
    
    # Calcula estatísticas de peso
    current_weight = user.get("weight", 0)
    target_weight = user.get("target_weight")
    
    if history:
        first_weight = history[0]["weight"]
        last_weight = history[-1]["weight"]
        total_change = round(last_weight - first_weight, 1)
        
        # Calcula progresso em relação ao objetivo
        if target_weight and target_weight != first_weight:
            progress_percent = round(((first_weight - last_weight) / (first_weight - target_weight)) * 100, 1)
            progress_percent = max(0, min(100, progress_percent))  # Limita entre 0 e 100
        else:
            progress_percent = 0
    else:
        first_weight = current_weight
        last_weight = current_weight
        total_change = 0
        progress_percent = 0
    
    # Calcula médias dos questionários
    questionnaire_averages = None
    if questionnaire_count > 0:
        questionnaire_averages = {
            "diet": round(questionnaire_totals["diet"] / questionnaire_count, 1),
            "training": round(questionnaire_totals["training"] / questionnaire_count, 1),
            "cardio": round(questionnaire_totals["cardio"] / questionnaire_count, 1),
            "sleep": round(questionnaire_totals["sleep"] / questionnaire_count, 1),
            "hydration": round(questionnaire_totals["hydration"] / questionnaire_count, 1),
            "overall": round(sum(questionnaire_totals.values()) / (questionnaire_count * 5), 1)
        }
    
    # Verifica se pode registrar novo peso
    last_record = await db.weight_records.find_one(
        {"user_id": user_id},
        sort=[("recorded_at", -1)]
    )
    
    can_record = True
    days_until_next = 0
    next_record_date = None
    
    if last_record:
        days_since_last = (datetime.utcnow() - last_record["recorded_at"]).days
        if days_since_last < block_days:
            can_record = False
            days_until_next = block_days - days_since_last
            next_record_date = (last_record["recorded_at"] + timedelta(days=block_days)).isoformat()
    else:
        # Primeiro registro - verifica dias desde cadastro
        if user.get("created_at"):
            days_since_creation = (datetime.utcnow() - user["created_at"]).days
            if days_since_creation < block_days:
                can_record = False
                days_until_next = block_days - days_since_creation
                next_record_date = (user["created_at"] + timedelta(days=block_days)).isoformat()
    
    # Dados para gráficos (formato simplificado)
    chart_data = {
        "weight": [{"x": r["recorded_at"], "y": r["weight"]} for r in history],
        "questionnaire": []
    }
    
    # Adiciona dados de questionário para gráfico
    for r in history:
        if r.get("questionnaire_average"):
            chart_data["questionnaire"].append({
                "x": r["recorded_at"],
                "y": r["questionnaire_average"]
            })
    
    return {
        "user_id": user_id,
        "current_weight": current_weight,
        "target_weight": target_weight,
        "is_athlete": is_athlete,
        "athlete_phase": user.get("competition_phase"),
        "history": history,
        "stats": {
            "total_records": len(history),
            "first_weight": first_weight,
            "last_weight": last_weight,
            "total_change": total_change,
            "progress_percent": progress_percent,
            "questionnaire_averages": questionnaire_averages
        },
        "can_record": can_record,
        "days_until_next_record": days_until_next,
        "next_record_date": next_record_date,
        "block_period_days": block_days,
        "chart_data": chart_data
    }


@api_router.delete("/progress/weight/{record_id}")
async def delete_weight_record(record_id: str):
    """
    Deleta um registro de peso específico.
    """
    result = await db.weight_records.delete_one({"_id": record_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    return {"message": "Registro deletado com sucesso"}


# ==================== NOTIFICATIONS ENDPOINTS ====================

@api_router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str, unread_only: bool = False):
    """
    Retorna notificações/lembretes do usuário.
    
    Inclui:
    - Lembretes de atualização de peso
    - Alertas de Peak Week
    - Notificações gerais
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca notificações
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    
    notifications = await db.notifications.find(query).sort("created_at", -1).to_list(50)
    
    # Gera notificações dinâmicas baseadas no contexto
    dynamic_notifications = []
    
    # 1. Verificar se precisa atualizar peso
    last_weight = await db.weight_records.find_one(
        {"user_id": user_id},
        sort=[("recorded_at", -1)]
    )
    
    if last_weight:
        days_since_last = (datetime.utcnow() - last_weight["recorded_at"]).days
        if days_since_last >= 7:
            dynamic_notifications.append({
                "id": "weight_reminder",
                "type": "weight_update",
                "title": "📊 Hora de atualizar seu peso!",
                "message": f"Já se passaram {days_since_last} dias desde seu último registro. Registre seu peso para acompanhar seu progresso.",
                "created_at": datetime.utcnow().isoformat(),
                "read": False,
                "action_url": "/progress",
                "priority": "high"
            })
        elif days_since_last >= 5:
            dynamic_notifications.append({
                "id": "weight_reminder_soon",
                "type": "weight_update",
                "title": "⏰ Atualização de peso em breve",
                "message": f"Em {7 - days_since_last} dia(s) você poderá registrar seu novo peso.",
                "created_at": datetime.utcnow().isoformat(),
                "read": False,
                "action_url": "/progress",
                "priority": "low"
            })
    
    # 2. Verificar Peak Week para atletas
    is_athlete = user.get("goal") == "atleta" or user.get("athlete_mode", False)
    if is_athlete:
        comp_date = user.get("athlete_competition_date") or user.get("competition_date")
        if comp_date:
            days_to_comp = (comp_date - datetime.utcnow()).days
            
            if 0 < days_to_comp <= 7:
                dynamic_notifications.append({
                    "id": "peak_week_active",
                    "type": "peak_week",
                    "title": "🏆 PEAK WEEK ATIVA!",
                    "message": f"Faltam {days_to_comp} dia(s) para a competição. Siga o protocolo de Peak Week com atenção.",
                    "created_at": datetime.utcnow().isoformat(),
                    "read": False,
                    "action_url": "/peak-week",
                    "priority": "critical"
                })
            elif 7 < days_to_comp <= 14:
                dynamic_notifications.append({
                    "id": "peak_week_approaching",
                    "type": "peak_week",
                    "title": "⚡ Peak Week se aproximando",
                    "message": f"Em {days_to_comp - 7} dia(s) começa sua Peak Week. Prepare-se!",
                    "created_at": datetime.utcnow().isoformat(),
                    "read": False,
                    "action_url": "/peak-week",
                    "priority": "medium"
                })
    
    # Formata notificações do banco
    db_notifications = []
    for n in notifications:
        db_notifications.append({
            "id": n["_id"],
            "type": n.get("type", "general"),
            "title": n.get("title", ""),
            "message": n.get("message", ""),
            "created_at": n.get("created_at", datetime.utcnow()).isoformat() if isinstance(n.get("created_at"), datetime) else n.get("created_at"),
            "read": n.get("read", False),
            "action_url": n.get("action_url"),
            "priority": n.get("priority", "normal")
        })
    
    return {
        "user_id": user_id,
        "notifications": dynamic_notifications + db_notifications,
        "unread_count": len([n for n in dynamic_notifications + db_notifications if not n.get("read", False)])
    }


@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Marca uma notificação como lida"""
    result = await db.notifications.update_one(
        {"_id": notification_id},
        {"$set": {"read": True, "read_at": datetime.utcnow()}}
    )
    
    return {"success": result.modified_count > 0}


# ==================== PEAK WEEK ENDPOINTS ====================

# Importa regras oficiais de Peak Week
from peak_week_rules import (
    generate_full_peak_week_protocol,
    generate_peak_week_diet,
    calculate_peak_week_macros,
    get_water_sodium_protocol,
    MINIMUM_WATER_LITERS,
    MINIMUM_SODIUM_MG,
    PEAK_WEEK_BLOCKED_FOODS,
    PEAK_WEEK_PRIORITY_FOODS
)

@api_router.get("/peak-week/{user_id}")
async def get_peak_week_plan(user_id: str):
    """
    🏆 PROTOCOLO OFICIAL DE PEAK WEEK
    
    Gera o plano completo de Peak Week usando as REGRAS OFICIAIS:
    
    📋 3 FASES:
    - DEPLEÇÃO (D-7 → D-4): Controle, depleção leve de glicogênio
    - TRANSIÇÃO (D-3 → D-2): Enchimento gradual sem retenção
    - CARB-UP (D-1): Pump visual, enchimento muscular
    
    ⚖️ ATLETAS COM PESAGEM:
    - Se has_weigh_in=true, carb-up é ADIADO até APÓS a pesagem
    - D-1 antes da pesagem: dieta leve
    - D-1 após pesagem: carb-up (4-7 g/kg)
    
    🚫 ALIMENTOS BLOQUEADOS:
    - Leguminosas (feijão, lentilha, grão de bico)
    - Cereais com fibras (aveia, granola, pão integral)
    - Crucíferos (brócolis, couve-flor, repolho)
    
    ✅ ALIMENTOS PRIORITÁRIOS:
    - Arroz branco, batata doce, batata
    - Frango, tilápia, claras
    - Pepino, alface, espinafre
    
    ⚠️ SEGURANÇA OBRIGATÓRIA:
    - Água NUNCA abaixo de 2L/dia
    - Sódio NUNCA abaixo de 500mg/dia
    """
    # Verifica se usuário existe e é atleta
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    is_athlete = user.get("goal") == "atleta" or user.get("athlete_mode", False)
    if not is_athlete:
        raise HTTPException(status_code=400, detail="Peak Week disponível apenas para atletas")
    
    comp_date = user.get("athlete_competition_date") or user.get("competition_date")
    if not comp_date:
        raise HTTPException(status_code=400, detail="Data de competição não definida")
    
    days_to_comp = (comp_date - datetime.utcnow()).days
    if days_to_comp > 14:
        raise HTTPException(
            status_code=400, 
            detail=f"Peak Week disponível apenas 14 dias antes da competição. Faltam {days_to_comp} dias."
        )
    
    # Dados do atleta
    current_weight = user.get("weight", 80)
    target_weight = user.get("target_weight", current_weight)
    has_weigh_in = user.get("has_weigh_in", False)
    has_weight_class = user.get("has_weight_class", False)
    weigh_in_hours = user.get("weigh_in_hours_before", 24)
    
    # Preferências alimentares do atleta
    food_preferences = user.get("food_preferences", [])
    
    # Gera protocolo OFICIAL de Peak Week
    full_protocol = generate_full_peak_week_protocol(
        weight_kg=current_weight,
        competition_date=comp_date,
        has_weigh_in=has_weigh_in,
        meal_count=6,  # Pode ser configurável
        preferred_foods=food_preferences
    )
    
    # Converte para formato do frontend existente (compatibilidade)
    protocols = convert_official_protocol_to_legacy(full_protocol, current_weight, comp_date)
    
    # Avisos de segurança obrigatórios (REGRAS OFICIAIS)
    safety_warnings = [
        f"⚠️ NUNCA reduza água abaixo de {MINIMUM_WATER_LITERS}L/dia",
        f"⚠️ NUNCA reduza sódio abaixo de {MINIMUM_SODIUM_MG}mg/dia",
        "⚠️ Água zero e sódio zero são PROIBIDOS - causam problemas graves",
        "⚠️ Se sentir tontura, fraqueza ou cãibras, aumente água e sódio",
        "⚠️ Este protocolo deve ser supervisionado por um profissional",
    ]
    
    # Informações sobre pesagem (se aplicável)
    weigh_in_info = None
    if has_weigh_in:
        weigh_in_info = {
            "has_weigh_in": True,
            "hours_before": weigh_in_hours,
            "strategy": "CARB-UP ADIADO",
            "notes": [
                "⚖️ Você tem pesagem antes da competição",
                "🟡 Carb-up será feito APÓS a pesagem oficial",
                "🔴 D-1 antes da pesagem: dieta leve, controlar peso",
                "🟢 D-1 após pesagem: carb-up agressivo (4-7g/kg)",
            ]
        }
    
    return {
        "user_id": user_id,
        "competition_date": comp_date.isoformat(),
        "days_to_competition": max(0, days_to_comp),
        "current_weight": current_weight,
        "target_weight": target_weight,
        "current_day": 7 - max(0, min(7, days_to_comp)) + 1,
        
        # Protocolo oficial
        "protocols": protocols,
        "full_protocol": full_protocol,  # Dados completos para frontend avançado
        
        # Informações de pesagem
        "has_weigh_in": has_weigh_in,
        "weigh_in_info": weigh_in_info,
        
        # Alimentos
        "blocked_foods": list(PEAK_WEEK_BLOCKED_FOODS),
        "priority_foods": {
            "carbs": list(PEAK_WEEK_PRIORITY_FOODS["carbs"]),
            "protein": list(PEAK_WEEK_PRIORITY_FOODS["protein"]),
            "vegetables": list(PEAK_WEEK_PRIORITY_FOODS["vegetables"]),
        },
        
        # Segurança
        "safety_warnings": safety_warnings,
        "safety_limits": {
            "min_water_liters": MINIMUM_WATER_LITERS,
            "min_sodium_mg": MINIMUM_SODIUM_MG,
        },
        
        "disclaimer": "Este protocolo segue as REGRAS OFICIAIS de Peak Week. É informativo e educacional. Consulte sempre um profissional de saúde."
    }


def convert_official_protocol_to_legacy(full_protocol: dict, weight: float, comp_date: datetime) -> List[dict]:
    """
    Converte o protocolo oficial para o formato usado pelo frontend existente.
    Mantém compatibilidade com a UI atual enquanto adiciona novos dados.
    """
    days_of_week = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    comp_weekday = comp_date.weekday()
    
    protocols = []
    days_data = full_protocol.get("days", [])
    
    for day_info in days_data:
        day_num = day_info.get("day_number", 1) + 1  # Ajusta para 1-7
        days_remaining = day_info.get("days_to_competition", 0)
        
        # Calcula dia da semana
        day_offset = day_num - 7
        day_weekday = (comp_weekday + day_offset) % 7
        day_name = days_of_week[day_weekday]
        
        # Pega dados do dia (pode ter split se for dia de pesagem)
        if day_info.get("has_split"):
            # Dia com pesagem - mostra dados pré-pesagem por padrão
            diet = day_info.get("pre_weigh_in", {})
            post_diet = day_info.get("post_weigh_in", {})
            has_split = True
        else:
            diet = day_info.get("diet", {})
            post_diet = None
            has_split = False
        
        # Extrai dados de água/sódio
        water_sodium = diet.get("water_sodium", {})
        water = water_sodium.get("water_liters", 3.0)
        sodium = water_sodium.get("sodium_mg", 1500)
        
        # Extrai macros
        macros = diet.get("target_macros", {})
        carbs_g = macros.get("carbs", 0)
        carbs_per_kg = round(carbs_g / weight, 1) if weight > 0 else 0
        
        # Determina estratégia de carbs
        phase = diet.get("phase", "depletion")
        if phase == "carb_up":
            carb_strategy = "loading"
        elif phase == "transition":
            carb_strategy = "moderate"
        else:
            carb_strategy = "depletion"
        
        # Determina tipo de treino
        if days_remaining >= 4:
            training = "full_body"
        elif days_remaining >= 2:
            training = "light_pump"
        elif days_remaining >= 1:
            training = "posing"
        else:
            training = "rest"
        
        # Notas
        water_note = get_water_note_official(days_remaining, water)
        sodium_note = get_sodium_note_official(days_remaining, sodium)
        carb_note = f"{diet.get('phase_name', 'Fase')}: {carbs_g}g de carbs ({carbs_per_kg}g/kg)"
        training_note = get_training_note(days_remaining, training)
        general_note = diet.get("phase_description", get_general_note(day_num))
        
        # Aviso especial
        warning = None
        if days_remaining <= 1:
            warning = "⚠️ Monitore seu corpo atentamente. Qualquer mal-estar, volte à hidratação normal."
        
        protocol_data = {
            "day": day_num,
            "day_name": day_name,
            "days_to_competition": days_remaining,
            "water_liters": water,
            "water_note": water_note,
            "sodium_mg": sodium,
            "sodium_note": sodium_note,
            "carb_strategy": carb_strategy,
            "carb_grams_per_kg": carbs_per_kg,
            "carb_total_grams": carbs_g,
            "carb_note": carb_note,
            "training_type": training,
            "training_note": training_note,
            "general_notes": general_note,
            "warning": warning,
            
            # Dados extras do protocolo oficial
            "phase": phase,
            "phase_name": diet.get("phase_name", ""),
            "has_split": has_split,
            "meals": diet.get("meals", []),
            "macros": macros,
        }
        
        # Se tem dados pós-pesagem, inclui
        if post_diet:
            post_macros = post_diet.get("target_macros", {})
            protocol_data["post_weigh_in"] = {
                "phase": post_diet.get("phase", "carb_up"),
                "phase_name": post_diet.get("phase_name", "🔴 CARB-UP"),
                "carbs_g": post_macros.get("carbs", 0),
                "carbs_per_kg": round(post_macros.get("carbs", 0) / weight, 1) if weight > 0 else 0,
                "meals": post_diet.get("meals", []),
            }
        
        protocols.append(protocol_data)
    
    # Preenche dias faltantes se necessário
    while len(protocols) < 7:
        day_num = len(protocols) + 1
        protocols.append(generate_fallback_protocol_day(day_num, weight, comp_date))
    
    return protocols


def get_water_note_official(days_to_comp: int, liters: float) -> str:
    """Notas de água baseadas nas regras oficiais"""
    if days_to_comp >= 5:
        return f"Hidratação alta ({liters}L). Distribua ao longo do dia."
    elif days_to_comp >= 3:
        return f"Transição ({liters}L). Corpo se ajustando."
    elif days_to_comp >= 1:
        return f"Controle ({liters}L). NUNCA abaixo de 2L!"
    else:
        return f"Dia D ({liters}L mínimo). MANTENHA-SE HIDRATADO!"


def get_sodium_note_official(days_to_comp: int, mg: int) -> str:
    """Notas de sódio baseadas nas regras oficiais"""
    if days_to_comp >= 5:
        return f"Sódio normal ({mg}mg). Tempere normalmente."
    elif days_to_comp >= 3:
        return f"Redução gradual ({mg}mg). Evite ultraprocessados."
    elif days_to_comp >= 1:
        return f"Sódio controlado ({mg}mg). NUNCA zero!"
    else:
        return f"Mínimo seguro ({mg}mg). Essencial para músculos!"


def generate_fallback_protocol_day(day: int, weight: float, comp_date: datetime) -> dict:
    """Gera dia de protocolo fallback se dados oficiais não disponíveis"""
    days_of_week = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    comp_weekday = comp_date.weekday()
    day_offset = day - 7
    day_weekday = (comp_weekday + day_offset) % 7
    
    return {
        "day": day,
        "day_name": days_of_week[day_weekday],
        "days_to_competition": 7 - day,
        "water_liters": max(2.0, 5.0 - (day * 0.4)),
        "water_note": "Mantenha hidratação adequada",
        "sodium_mg": max(500, 2000 - (day * 200)),
        "sodium_note": "Controle de sódio gradual",
        "carb_strategy": "depletion" if day <= 3 else "moderate" if day <= 5 else "loading",
        "carb_grams_per_kg": 1.5 if day <= 3 else 2.5 if day <= 5 else 5.0,
        "carb_total_grams": round((1.5 if day <= 3 else 2.5 if day <= 5 else 5.0) * weight),
        "carb_note": "Siga o plano de carbs",
        "training_type": "full_body" if day <= 2 else "light_pump" if day <= 4 else "posing",
        "training_note": "Siga o plano de treino",
        "general_notes": get_general_note(day),
        "warning": None,
    }


def get_water_note(day: int, liters: float) -> str:
    notes = {
        1: f"Hidratação alta ({liters}L). Beba consistentemente ao longo do dia.",
        2: f"Mantenha {liters}L. Distribua uniformemente.",
        3: f"Redução gradual para {liters}L. Evite beber muito de uma vez.",
        4: f"Transição ({liters}L). Corpo começando a ajustar.",
        5: f"Redução moderada ({liters}L). Monitore cor da urina.",
        6: f"Dia de carga ({liters}L). Hidrate junto com os carboidratos.",
        7: f"Dia D ({liters}L mínimo). NUNCA fique desidratado!"
    }
    return notes.get(day, f"{liters}L de água")


def get_sodium_note(day: int, mg: int) -> str:
    notes = {
        1: f"Sódio normal ({mg}mg). Tempere normalmente.",
        2: f"Leve redução ({mg}mg). Evite alimentos ultraprocessados.",
        3: f"Redução moderada ({mg}mg). Prefira temperos naturais.",
        4: f"Sódio baixo ({mg}mg). Cuidado com fontes escondidas.",
        5: f"Sódio reduzido ({mg}mg). Monitore cãibras.",
        6: f"Sódio mínimo seguro ({mg}mg). Não corte totalmente!",
        7: f"Mínimo fisiológico ({mg}mg). Essencial para função muscular."
    }
    return notes.get(day, f"{mg}mg de sódio")


def get_carb_note(day: int, strategy: str, grams_kg: float, weight: float) -> str:
    total = round(grams_kg * weight)
    
    if strategy == "depletion":
        return f"Depleção: {total}g de carbs ({grams_kg}g/kg). Foque em treino e esgote glicogênio."
    elif strategy == "moderate":
        return f"Transição: {total}g de carbs ({grams_kg}g/kg). Corpo se preparando para carga."
    else:  # loading
        return f"Carga: {total}g de carbs ({grams_kg}g/kg). Fontes limpas: arroz, batata doce."


def get_training_note(day: int, training_type: str) -> str:
    notes = {
        "full_body": "Treino full body de alto volume. Objetivo: deplecionar glicogênio muscular.",
        "light_pump": "Treino leve de pump. Séries altas, cargas baixas. Apenas para fluxo sanguíneo.",
        "posing": "Apenas prática de poses. Economize energia.",
        "rest": "Descanso total. Apenas poses se necessário."
    }
    return notes.get(training_type, "Siga o plano de treino")


def get_general_note(day: int) -> str:
    notes = {
        1: "Início da semana. Foco total na depleção. Mantenha rotina de sono.",
        2: "Continue deplecando. Sua energia pode cair - é normal.",
        3: "Último dia de depleção intensa. Prepare-se para a transição.",
        4: "Transição. Corpo pode parecer 'flat' - é temporário.",
        5: "Início da carga. Músculos começam a encher. Monitore o visual.",
        6: "Carga principal. Coma carboidratos limpos a cada 2-3 horas.",
        7: "DIA DA COMPETIÇÃO! Confie no processo. Você está pronto! 🏆"
    }
    return notes.get(day, "Siga o protocolo com atenção")


# ==================== PERFORMANCE CHART ENDPOINT ====================

@api_router.get("/progress/performance/{user_id}")
async def get_performance_chart_data(user_id: str, days: int = 90):
    """
    Retorna dados formatados para gráfico de desempenho.
    
    Inclui:
    - Evolução do peso ao longo do tempo
    - Linha de desempenho (média do questionário)
    - Tendências e projeções
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca registros
    from_date = datetime.utcnow() - timedelta(days=days)
    
    records = await db.weight_records.find(
        {"user_id": user_id, "recorded_at": {"$gte": from_date}}
    ).sort("recorded_at", 1).to_list(length=100)
    
    if not records:
        return {
            "user_id": user_id,
            "has_data": False,
            "message": "Nenhum registro encontrado no período"
        }
    
    # Formata dados para gráfico
    weight_data = []
    performance_data = []
    
    for r in records:
        date_str = r["recorded_at"].strftime("%Y-%m-%d")
        
        weight_data.append({
            "date": date_str,
            "value": r["weight"],
            "phase": r.get("athlete_phase")
        })
        
        if r.get("questionnaire_average"):
            performance_data.append({
                "date": date_str,
                "value": r["questionnaire_average"],
                "breakdown": r.get("questionnaire", {})
            })
    
    # Calcula tendências
    if len(weight_data) >= 2:
        first_weight = weight_data[0]["value"]
        last_weight = weight_data[-1]["value"]
        weight_change = last_weight - first_weight
        days_elapsed = (records[-1]["recorded_at"] - records[0]["recorded_at"]).days
        
        if days_elapsed > 0:
            weekly_rate = (weight_change / days_elapsed) * 7
        else:
            weekly_rate = 0
    else:
        weight_change = 0
        weekly_rate = 0
    
    # Calcula média de desempenho
    if performance_data:
        avg_performance = sum(p["value"] for p in performance_data) / len(performance_data)
        
        # Breakdown por categoria
        category_totals = {"diet": 0, "training": 0, "cardio": 0, "sleep": 0, "hydration": 0}
        category_count = 0
        
        for p in performance_data:
            bd = p.get("breakdown", {})
            if bd:
                for key in category_totals:
                    category_totals[key] += bd.get(key, 0)
                category_count += 1
        
        if category_count > 0:
            category_averages = {k: round(v / category_count, 1) for k, v in category_totals.items()}
        else:
            category_averages = category_totals
    else:
        avg_performance = 0
        category_averages = {}
    
    # Identifica a categoria mais fraca
    weakest_category = None
    if category_averages:
        weakest_category = min(category_averages, key=category_averages.get)
    
    # Sugestões baseadas nos dados
    suggestions = generate_performance_suggestions(
        weight_change, weekly_rate, avg_performance, category_averages, user.get("goal")
    )
    
    return {
        "user_id": user_id,
        "has_data": True,
        "period_days": days,
        "total_records": len(records),
        
        # Dados para gráficos
        "weight_chart": {
            "data": weight_data,
            "min": min(d["value"] for d in weight_data) - 1,
            "max": max(d["value"] for d in weight_data) + 1
        },
        "performance_chart": {
            "data": performance_data,
            "average": round(avg_performance, 1)
        },
        
        # Estatísticas
        "stats": {
            "weight_change": round(weight_change, 1),
            "weekly_rate": round(weekly_rate, 2),
            "avg_performance": round(avg_performance, 1),
            "category_averages": category_averages,
            "weakest_category": weakest_category,
            "target_weight": user.get("target_weight"),
            "current_weight": user.get("weight")
        },
        
        # Sugestões
        "suggestions": suggestions
    }


def generate_performance_suggestions(weight_change: float, weekly_rate: float, 
                                    avg_performance: float, categories: dict, goal: str) -> List[dict]:
    """Gera sugestões personalizadas baseadas nos dados de desempenho"""
    
    suggestions = []
    
    # Sugestões baseadas no peso
    if goal == "cutting" and weekly_rate > 0:
        suggestions.append({
            "type": "weight",
            "icon": "⚖️",
            "title": "Ajuste no déficit calórico",
            "message": "Você está ganhando peso em um período de cutting. Considere aumentar o déficit ou a atividade física."
        })
    elif goal == "bulking" and weekly_rate < 0:
        suggestions.append({
            "type": "weight",
            "icon": "⚖️",
            "title": "Aumente a ingestão calórica",
            "message": "Você está perdendo peso em um período de bulking. Aumente gradualmente as calorias."
        })
    elif abs(weekly_rate) > 1.0:
        suggestions.append({
            "type": "weight",
            "icon": "⚠️",
            "title": "Mudança de peso acelerada",
            "message": f"Você está {'perdendo' if weekly_rate < 0 else 'ganhando'} mais de 1kg por semana. Isso pode não ser sustentável."
        })
    
    # Sugestões baseadas nas categorias
    if categories:
        weakest = min(categories, key=categories.get)
        weakest_score = categories[weakest]
        
        category_suggestions = {
            "diet": {
                "icon": "🍽️",
                "title": "Melhore a adesão à dieta",
                "message": "Sua pontuação de dieta está baixa. Tente preparar as refeições com antecedência."
            },
            "training": {
                "icon": "🏋️",
                "title": "Consistência no treino",
                "message": "Seus treinos podem melhorar. Defina horários fixos para treinar."
            },
            "cardio": {
                "icon": "🏃",
                "title": "Aumente o cardio",
                "message": "O cardio está abaixo do ideal. Tente adicionar caminhadas diárias."
            },
            "sleep": {
                "icon": "😴",
                "title": "Priorize o sono",
                "message": "Seu sono precisa de atenção. Estabeleça uma rotina noturna consistente."
            },
            "hydration": {
                "icon": "💧",
                "title": "Beba mais água",
                "message": "Hidratação baixa afeta performance e recuperação. Use lembretes para beber água."
            }
        }
        
        if weakest_score < 6:
            suggestion = category_suggestions.get(weakest, {
                "icon": "📊",
                "title": f"Melhore {weakest}",
                "message": f"Esta é sua área mais fraca (média: {weakest_score})."
            })
            suggestions.append({
                "type": "category",
                **suggestion,
                "category": weakest,
                "score": weakest_score
            })
    
    # Sugestão de consistência
    if avg_performance >= 8:
        suggestions.append({
            "type": "positive",
            "icon": "🌟",
            "title": "Excelente consistência!",
            "message": "Sua média de desempenho está ótima. Continue assim!"
        })
    elif avg_performance < 5:
        suggestions.append({
            "type": "warning",
            "icon": "⚡",
            "title": "Foco na consistência",
            "message": "Sua média geral está baixa. Escolha UMA área para melhorar esta semana."
        })
    
    return suggestions


# ==================== ATHLETE PHASE HISTORY ENDPOINTS ====================

@api_router.get("/athlete/phases/{user_id}")
async def get_athlete_phase_history(user_id: str):
    """
    Retorna histórico completo das fases do atleta.
    
    Inclui:
    - Todas as fases registradas (OFF, PREP, PEAK, POST)
    - Datas de início e fim
    - Peso no início e fim de cada fase
    - Estatísticas de cada fase
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca histórico de fases
    phases = await db.athlete_phases.find(
        {"user_id": user_id}
    ).sort("started_at", -1).to_list(length=50)
    
    # Formata resposta
    history = []
    for p in phases:
        history.append({
            "id": p["_id"],
            "phase": p["phase"],
            "phase_name": format_phase_name(p["phase"]),
            "started_at": p["started_at"].isoformat(),
            "ended_at": p.get("ended_at").isoformat() if p.get("ended_at") else None,
            "competition_date": p.get("competition_date").isoformat() if p.get("competition_date") else None,
            "competition_name": p.get("competition_name"),
            "start_weight": p.get("start_weight"),
            "end_weight": p.get("end_weight"),
            "weight_change": round(p.get("end_weight", 0) - p.get("start_weight", 0), 1) if p.get("end_weight") else None,
            "duration_days": (p.get("ended_at") - p["started_at"]).days if p.get("ended_at") else None,
            "notes": p.get("notes"),
            "stats": p.get("stats", {})
        })
    
    # Fase atual
    current_phase = user.get("competition_phase")
    current_phase_start = None
    
    # Busca início da fase atual (última fase sem ended_at)
    current_phase_record = await db.athlete_phases.find_one(
        {"user_id": user_id, "ended_at": None}
    )
    
    if current_phase_record:
        current_phase_start = current_phase_record["started_at"]
    
    # Estatísticas gerais
    total_preps = sum(1 for p in history if p["phase"] == "pre_contest")
    total_competitions = sum(1 for p in history if p.get("competition_date"))
    
    return {
        "user_id": user_id,
        "is_athlete": user.get("goal") == "atleta" or user.get("athlete_mode", False),
        "current_phase": current_phase,
        "current_phase_name": format_phase_name(current_phase) if current_phase else None,
        "current_phase_start": current_phase_start.isoformat() if current_phase_start else None,
        "history": history,
        "stats": {
            "total_phases": len(history),
            "total_preps": total_preps,
            "total_competitions": total_competitions
        }
    }


@api_router.post("/athlete/phases/{user_id}")
async def start_athlete_phase(user_id: str, phase_data: AthletePhaseHistoryCreate):
    """
    Inicia uma nova fase para o atleta.
    
    Automaticamente:
    - Finaliza a fase anterior (se existir)
    - Registra peso atual como peso inicial
    - Cria novo registro de fase
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Finaliza fase anterior se existir
    previous_phase = await db.athlete_phases.find_one(
        {"user_id": user_id, "ended_at": None}
    )
    
    if previous_phase:
        # Busca último peso registrado
        last_weight = await db.weight_records.find_one(
            {"user_id": user_id},
            sort=[("recorded_at", -1)]
        )
        
        end_weight = last_weight["weight"] if last_weight else user.get("weight")
        
        # Calcula estatísticas da fase anterior
        phase_stats = await calculate_phase_stats(
            user_id, 
            previous_phase["started_at"], 
            datetime.utcnow()
        )
        
        # Atualiza fase anterior
        await db.athlete_phases.update_one(
            {"_id": previous_phase["_id"]},
            {"$set": {
                "ended_at": datetime.utcnow(),
                "end_weight": end_weight,
                "stats": phase_stats
            }}
        )
    
    # Cria nova fase
    current_weight = user.get("weight", 80)
    
    new_phase = AthletePhaseRecord(
        user_id=user_id,
        phase=phase_data.phase,
        started_at=datetime.utcnow(),
        competition_date=phase_data.competition_date,
        competition_name=phase_data.competition_name,
        start_weight=current_weight,
        target_weight=user.get("target_weight"),
        notes=phase_data.notes
    )
    
    phase_dict = new_phase.dict()
    phase_dict["_id"] = phase_dict["id"]
    await db.athlete_phases.insert_one(phase_dict)
    
    # Atualiza fase no perfil do usuário
    await db.user_profiles.update_one(
        {"_id": user_id},
        {"$set": {
            "competition_phase": phase_data.phase,
            "athlete_competition_date": phase_data.competition_date,
            "athlete_mode": True
        }}
    )
    
    return {
        "success": True,
        "phase": new_phase.dict(),
        "message": f"Fase {format_phase_name(phase_data.phase)} iniciada com sucesso"
    }


async def calculate_phase_stats(user_id: str, start_date: datetime, end_date: datetime) -> dict:
    """Calcula estatísticas de uma fase"""
    
    # Busca registros de peso do período
    weight_records = await db.weight_records.find(
        {
            "user_id": user_id,
            "recorded_at": {"$gte": start_date, "$lte": end_date}
        }
    ).to_list(length=100)
    
    if not weight_records:
        return {}
    
    # Calcula estatísticas
    weights = [r["weight"] for r in weight_records]
    questionnaire_avgs = [r.get("questionnaire_average", 0) for r in weight_records if r.get("questionnaire_average")]
    
    stats = {
        "total_weight_records": len(weight_records),
        "weight_change": round(weights[-1] - weights[0], 1) if len(weights) >= 2 else 0,
        "lowest_weight": min(weights),
        "highest_weight": max(weights),
        "average_performance": round(sum(questionnaire_avgs) / len(questionnaire_avgs), 1) if questionnaire_avgs else 0
    }
    
    return stats


def format_phase_name(phase: str) -> str:
    """Formata nome da fase para exibição"""
    names = {
        "off_season": "OFF-SEASON",
        "pre_contest": "PREP",
        "peak_week": "PEAK WEEK",
        "post_show": "PÓS-SHOW"
    }
    return names.get(phase, phase.upper() if phase else "")


# ==================== WATER/SODIUM TRACKER ENDPOINTS ====================

@api_router.get("/tracker/water-sodium/{user_id}")
async def get_water_sodium_tracker(user_id: str, date: str = None):
    """
    Retorna dados do tracker de água/sódio do dia.
    
    Se não especificado, retorna dados de hoje.
    
    SEGURANÇA:
    - Alerta se água < 2L
    - Alerta se sódio < 500mg
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Determina a data
    if date:
        try:
            target_date = datetime.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
    else:
        target_date = datetime.utcnow()
    
    # Início e fim do dia
    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    
    # Busca entrada do dia
    entry = await db.water_sodium_tracker.find_one({
        "user_id": user_id,
        "date": {"$gte": day_start, "$lt": day_end}
    })
    
    # Determina metas baseadas na fase (Peak Week tem metas específicas)
    is_athlete = user.get("goal") == "atleta" or user.get("athlete_mode", False)
    competition_phase = user.get("competition_phase")
    
    # Metas padrão
    water_target = 3000  # 3L em ml
    sodium_target = 2000  # 2000mg
    
    # Ajusta metas para Peak Week
    if is_athlete and competition_phase == "peak_week":
        comp_date = user.get("athlete_competition_date") or user.get("competition_date")
        if comp_date:
            days_to_comp = (comp_date - datetime.utcnow()).days
            peak_day = 7 - max(0, min(7, days_to_comp))
            
            # Metas por dia da Peak Week
            peak_week_targets = {
                1: {"water": 5000, "sodium": 2000},
                2: {"water": 4500, "sodium": 1700},
                3: {"water": 4000, "sodium": 1400},
                4: {"water": 3500, "sodium": 1000},
                5: {"water": 3000, "sodium": 800},
                6: {"water": 2500, "sodium": 600},
                7: {"water": 2000, "sodium": 500},
            }
            
            targets = peak_week_targets.get(peak_day, {"water": 3000, "sodium": 2000})
            water_target = targets["water"]
            sodium_target = targets["sodium"]
    
    # Se não tem entrada, retorna valores zerados
    if not entry:
        return {
            "user_id": user_id,
            "date": day_start.isoformat(),
            "water_ml": 0,
            "water_target_ml": water_target,
            "water_percent": 0,
            "sodium_mg": 0,
            "sodium_target_mg": sodium_target,
            "sodium_percent": 0,
            "is_peak_week": competition_phase == "peak_week",
            "peak_week_day": 7 - max(0, min(7, (comp_date - datetime.utcnow()).days)) if competition_phase == "peak_week" and comp_date else None,
            "warnings": [],
            "entries": []
        }
    
    # Calcula porcentagens
    water_percent = min(100, round((entry.get("water_ml", 0) / water_target) * 100))
    sodium_percent = min(100, round((entry.get("sodium_mg", 0) / sodium_target) * 100))
    
    # Verifica limites de segurança
    warnings = []
    water_ml = entry.get("water_ml", 0)
    sodium_mg = entry.get("sodium_mg", 0)
    
    # Água mínima: 2L
    if water_ml > 0 and water_ml < 2000:
        warnings.append({
            "type": "danger",
            "icon": "💧",
            "message": "Atenção: Ingestão de água abaixo do mínimo seguro (2L). Aumente a hidratação!"
        })
    
    # Sódio mínimo: 500mg
    if sodium_mg > 0 and sodium_mg < 500:
        warnings.append({
            "type": "danger",
            "icon": "🧂",
            "message": "Atenção: Sódio abaixo do mínimo seguro (500mg). Não corte completamente!"
        })
    
    # Busca entradas individuais do dia (log de adições)
    entries_log = entry.get("entries_log", [])
    
    return {
        "user_id": user_id,
        "date": day_start.isoformat(),
        "water_ml": water_ml,
        "water_target_ml": water_target,
        "water_percent": water_percent,
        "sodium_mg": sodium_mg,
        "sodium_target_mg": sodium_target,
        "sodium_percent": sodium_percent,
        "is_peak_week": competition_phase == "peak_week",
        "peak_week_day": 7 - max(0, min(7, (comp_date - datetime.utcnow()).days)) if competition_phase == "peak_week" and 'comp_date' in dir() and comp_date else None,
        "warnings": warnings,
        "entries_log": entries_log,
        "notes": entry.get("notes")
    }


@api_router.post("/tracker/water-sodium/{user_id}")
async def add_water_sodium(user_id: str, entry: WaterSodiumEntryCreate):
    """
    Adiciona entrada de água/sódio.
    
    Soma aos valores existentes do dia.
    
    SEGURANÇA:
    - Emite alerta se água < 2L no final do dia
    - Emite alerta se sódio < 500mg
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Dia atual
    now = datetime.utcnow()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    
    # Busca entrada existente do dia
    existing = await db.water_sodium_tracker.find_one({
        "user_id": user_id,
        "date": {"$gte": day_start, "$lt": day_end}
    })
    
    # Prepara log de entrada
    entry_log = {
        "time": now.isoformat(),
        "water_ml": entry.water_ml or 0,
        "sodium_mg": entry.sodium_mg or 0,
        "notes": entry.notes
    }
    
    if existing:
        # Atualiza entrada existente
        new_water = existing.get("water_ml", 0) + (entry.water_ml or 0)
        new_sodium = existing.get("sodium_mg", 0) + (entry.sodium_mg or 0)
        
        # Adiciona ao log
        entries_log = existing.get("entries_log", [])
        entries_log.append(entry_log)
        
        await db.water_sodium_tracker.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "water_ml": new_water,
                "sodium_mg": new_sodium,
                "water_below_minimum": new_water < 2000,
                "sodium_below_minimum": new_sodium < 500,
                "entries_log": entries_log,
                "updated_at": now
            }}
        )
        
        result_water = new_water
        result_sodium = new_sodium
    else:
        # Cria nova entrada
        new_entry = WaterSodiumEntry(
            user_id=user_id,
            date=day_start,
            water_ml=entry.water_ml or 0,
            sodium_mg=entry.sodium_mg or 0,
            water_below_minimum=(entry.water_ml or 0) < 2000,
            sodium_below_minimum=(entry.sodium_mg or 0) < 500,
            notes=entry.notes
        )
        
        entry_dict = new_entry.dict()
        entry_dict["_id"] = entry_dict["id"]
        entry_dict["entries_log"] = [entry_log]
        entry_dict["created_at"] = now
        
        await db.water_sodium_tracker.insert_one(entry_dict)
        
        result_water = entry.water_ml or 0
        result_sodium = entry.sodium_mg or 0
    
    # Verifica warnings
    warnings = []
    if result_water < 2000:
        warnings.append("⚠️ Água abaixo de 2L. Continue hidratando!")
    if result_sodium < 500:
        warnings.append("⚠️ Sódio abaixo do mínimo seguro (500mg)")
    
    return {
        "success": True,
        "water_ml": result_water,
        "sodium_mg": result_sodium,
        "added_water": entry.water_ml or 0,
        "added_sodium": entry.sodium_mg or 0,
        "warnings": warnings,
        "message": "Registro adicionado com sucesso"
    }


@api_router.get("/tracker/water-sodium/{user_id}/history")
async def get_water_sodium_history(user_id: str, days: int = 7):
    """
    Retorna histórico de água/sódio dos últimos N dias.
    
    Útil para visualizar tendências durante Peak Week.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Período
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Busca entradas
    entries = await db.water_sodium_tracker.find(
        {"user_id": user_id, "date": {"$gte": from_date}}
    ).sort("date", 1).to_list(length=days)
    
    # Formata resposta
    history = []
    for e in entries:
        history.append({
            "date": e["date"].strftime("%Y-%m-%d"),
            "water_ml": e.get("water_ml", 0),
            "sodium_mg": e.get("sodium_mg", 0),
            "water_below_minimum": e.get("water_below_minimum", False),
            "sodium_below_minimum": e.get("sodium_below_minimum", False)
        })
    
    # Estatísticas
    if history:
        avg_water = sum(h["water_ml"] for h in history) / len(history)
        avg_sodium = sum(h["sodium_mg"] for h in history) / len(history)
        days_below_water = sum(1 for h in history if h["water_below_minimum"])
        days_below_sodium = sum(1 for h in history if h["sodium_below_minimum"])
    else:
        avg_water = 0
        avg_sodium = 0
        days_below_water = 0
        days_below_sodium = 0
    
    return {
        "user_id": user_id,
        "period_days": days,
        "history": history,
        "stats": {
            "avg_water_ml": round(avg_water),
            "avg_sodium_mg": round(avg_sodium),
            "days_below_minimum_water": days_below_water,
            "days_below_minimum_sodium": days_below_sodium
        }
    }


# ==================== WORKOUT ENDPOINTS ====================

@api_router.post("/workout/generate")
async def generate_workout(user_id: str, force: bool = False):
    """
    Gera um plano de treino personalizado.
    Se force=true, substitui o treino existente.
    """
    try:
        # Busca perfil do usuário
        user_profile = await db.user_profiles.find_one({"_id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
        # Verifica se já existe treino (e não é force)
        existing = await db.workout_plans.find_one({"user_id": user_id})
        if existing and not force:
            # Delete o treino antigo para criar um novo
            await db.workout_plans.delete_many({"user_id": user_id})
        
        # Importa serviço de treino
        from workout_service import WorkoutAIService
        
        workout_service = WorkoutAIService()
        
        # Gera plano de treino
        workout_plan = workout_service.generate_workout_plan(
            user_profile=dict(user_profile)
        )
        
        # Salva no banco (substituindo qualquer existente)
        workout_dict = workout_plan.dict()
        workout_dict["_id"] = workout_dict["id"]
        
        # Delete todos os treinos antigos do usuário e insere o novo
        await db.workout_plans.delete_many({"user_id": user_id})
        await db.workout_plans.insert_one(workout_dict)
        
        logger.info(f"Workout generated for user {user_id}")
        
        return workout_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar treino: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar treino: {str(e)}")

@api_router.get("/workout/{user_id}")
async def get_user_workout(user_id: str):
    """
    Busca o plano de treino mais recente do usuário
    """
    workout_plan = await db.workout_plans.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if not workout_plan:
        raise HTTPException(status_code=404, detail="Plano de treino não encontrado")
    
    workout_plan["id"] = workout_plan["_id"]
    return workout_plan


class ExerciseCompletionRequest(BaseModel):
    """Request para marcar exercício como concluído"""
    workout_day_index: int
    exercise_index: int
    completed: bool


@api_router.put("/workout/{workout_id}/exercise/complete")
async def toggle_exercise_completion(workout_id: str, request: ExerciseCompletionRequest):
    """
    Marca/desmarca um exercício como concluído.
    """
    # Busca treino
    workout = await db.workout_plans.find_one({"_id": workout_id})
    if not workout:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    
    workout_days = workout.get("workout_days", [])
    
    # Valida índices
    if request.workout_day_index < 0 or request.workout_day_index >= len(workout_days):
        raise HTTPException(status_code=400, detail="Índice de dia inválido")
    
    exercises = workout_days[request.workout_day_index].get("exercises", [])
    
    if request.exercise_index < 0 or request.exercise_index >= len(exercises):
        raise HTTPException(status_code=400, detail="Índice de exercício inválido")
    
    # Atualiza status do exercício
    exercises[request.exercise_index]["completed"] = request.completed
    workout_days[request.workout_day_index]["exercises"] = exercises
    
    # Verifica se todos exercícios do dia foram concluídos
    all_completed = all(ex.get("completed", False) for ex in exercises)
    workout_days[request.workout_day_index]["completed"] = all_completed
    
    # Atualiza no banco
    await db.workout_plans.update_one(
        {"_id": workout_id},
        {"$set": {
            "workout_days": workout_days,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Retorna treino atualizado
    updated_workout = await db.workout_plans.find_one({"_id": workout_id})
    updated_workout["id"] = updated_workout["_id"]
    
    return updated_workout


@api_router.put("/workout/{workout_id}/reset")
async def reset_workout_progress(workout_id: str):
    """
    Reseta o progresso de todos os exercícios do treino.
    """
    # Busca treino
    workout = await db.workout_plans.find_one({"_id": workout_id})
    if not workout:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    
    workout_days = workout.get("workout_days", [])
    
    # Reseta todos os exercícios
    for day in workout_days:
        day["completed"] = False
        for ex in day.get("exercises", []):
            ex["completed"] = False
    
    # Atualiza no banco
    await db.workout_plans.update_one(
        {"_id": workout_id},
        {"$set": {
            "workout_days": workout_days,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Retorna treino atualizado
    updated_workout = await db.workout_plans.find_one({"_id": workout_id})
    updated_workout["id"] = updated_workout["_id"]
    
    return updated_workout


# ==================== WORKOUT HISTORY ENDPOINTS ====================

class WorkoutHistoryEntry(BaseModel):
    """Modelo para entrada no histórico de treinos"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    workout_day_name: str  # "Treino A - Peito/Tríceps"
    exercises_completed: int
    total_exercises: int
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class WorkoutHistoryCreate(BaseModel):
    """Request para salvar treino no histórico"""
    workout_day_name: str
    exercises_completed: int
    total_exercises: int
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


@api_router.post("/workout/history/{user_id}")
async def save_workout_to_history(user_id: str, entry: WorkoutHistoryCreate):
    """
    Salva um treino concluído no histórico.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Cria entrada no histórico
    history_entry = WorkoutHistoryEntry(
        user_id=user_id,
        workout_day_name=entry.workout_day_name,
        exercises_completed=entry.exercises_completed,
        total_exercises=entry.total_exercises,
        duration_minutes=entry.duration_minutes,
        notes=entry.notes
    )
    
    # Salva no banco
    entry_dict = history_entry.dict()
    entry_dict["_id"] = entry_dict["id"]
    await db.workout_history.insert_one(entry_dict)
    
    logger.info(f"Workout saved to history for user {user_id}: {entry.workout_day_name}")
    
    return history_entry


@api_router.get("/workout/history/{user_id}")
async def get_workout_history(user_id: str, days: int = 30, limit: int = 50):
    """
    Retorna histórico de treinos do usuário.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca histórico dos últimos N dias
    from_date = datetime.utcnow() - timedelta(days=days)
    
    history = await db.workout_history.find(
        {"user_id": user_id, "completed_at": {"$gte": from_date}}
    ).sort("completed_at", -1).to_list(length=limit)
    
    # Formata resposta
    formatted_history = []
    for h in history:
        formatted_history.append({
            "id": h["_id"],
            "workout_day_name": h["workout_day_name"],
            "exercises_completed": h["exercises_completed"],
            "total_exercises": h["total_exercises"],
            "duration_minutes": h.get("duration_minutes"),
            "notes": h.get("notes"),
            "completed_at": h["completed_at"].isoformat()
        })
    
    # Estatísticas
    total_workouts = len(formatted_history)
    total_exercises = sum(h["exercises_completed"] for h in formatted_history)
    
    # Frequência por semana
    this_week_count = 0
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    for h in history:
        if h["completed_at"] >= week_start:
            this_week_count += 1
    
    return {
        "user_id": user_id,
        "history": formatted_history,
        "stats": {
            "total_workouts": total_workouts,
            "total_exercises": total_exercises,
            "this_week_count": this_week_count,
            "target_frequency": user.get("weekly_training_frequency", 0)
        }
    }

# ==================== CARDIO SYSTEM ====================

class CardioExercise(BaseModel):
    """Modelo de exercício cardio"""
    id: str
    name: str
    name_en: str
    name_es: str
    duration_minutes: int
    intensity: str  # "low", "moderate", "high"
    calories_burned: int
    heart_rate_zone: str  # "Zone 2 (60-70%)", etc.
    description: str
    description_en: str
    description_es: str
    how_to_feel: str  # Como saber se está funcionando
    how_to_feel_en: str
    how_to_feel_es: str
    substitutes: List[str]  # IDs dos exercícios substitutos

class CardioSession(BaseModel):
    """Sessão de cardio do usuário"""
    user_id: str
    exercises: List[CardioExercise]
    total_duration: int
    total_calories: int
    goal: str  # "cutting", "bulking", "manutencao", "atleta"
    competition_phase: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Base de exercícios cardio (SEM CORRIDA - apenas bicicleta, caminhada, escada)
CARDIO_EXERCISES = {
    "caminhada_leve": {
        "id": "caminhada_leve",
        "name": "Caminhada Leve",
        "name_en": "Light Walk",
        "name_es": "Caminata Ligera",
        "duration_minutes": 30,
        "intensity": "low",
        "calories_per_min": 4,
        "heart_rate_zone": "Zona 2 (60-70% FCM)",
        "description": "Caminhada em ritmo tranquilo, consegue conversar normalmente",
        "description_en": "Walking at a relaxed pace, can talk normally",
        "description_es": "Caminata a ritmo tranquilo, puede conversar normalmente",
        "how_to_feel": "Respiração leve, sem suor excessivo. Você deve conseguir falar frases completas sem ficar ofegante. Sensação de relaxamento.",
        "how_to_feel_en": "Light breathing, no excessive sweating. You should be able to speak complete sentences without getting breathless.",
        "how_to_feel_es": "Respiración ligera, sin sudor excesivo. Deberías poder hablar oraciones completas sin quedarte sin aliento.",
        "substitutes": ["bicicleta_leve"]
    },
    "caminhada_moderada": {
        "id": "caminhada_moderada",
        "name": "Caminhada Moderada",
        "name_en": "Moderate Walk",
        "name_es": "Caminata Moderada",
        "duration_minutes": 40,
        "intensity": "moderate",
        "calories_per_min": 6,
        "heart_rate_zone": "Zona 3 (70-80% FCM)",
        "description": "Caminhada em ritmo acelerado, consegue falar com algum esforço",
        "description_en": "Brisk walking pace, can talk with some effort",
        "description_es": "Caminata a ritmo acelerado, puede hablar con algo de esfuerzo",
        "how_to_feel": "Respiração mais pesada, suor leve. Consegue falar mas precisa pausar entre frases. Batimentos cardíacos elevados mas controlados.",
        "how_to_feel_en": "Heavier breathing, light sweating. Can talk but need to pause between sentences. Elevated but controlled heart rate.",
        "how_to_feel_es": "Respiración más pesada, sudor ligero. Puede hablar pero necesita pausar entre oraciones.",
        "substitutes": ["bicicleta_moderada", "escada_leve"]
    },
    "caminhada_inclinada": {
        "id": "caminhada_inclinada",
        "name": "Caminhada Inclinada (Esteira)",
        "name_en": "Incline Walking (Treadmill)",
        "name_es": "Caminata Inclinada (Cinta)",
        "duration_minutes": 25,
        "intensity": "moderate",
        "calories_per_min": 8,
        "heart_rate_zone": "Zona 3-4 (70-85% FCM)",
        "description": "Caminhada em esteira com inclinação de 10-15%",
        "description_en": "Treadmill walking with 10-15% incline",
        "description_es": "Caminata en cinta con inclinación del 10-15%",
        "how_to_feel": "Queimação nas pernas (glúteos e panturrilhas), suor moderado. Respiração controlada mas intensa. Sente os músculos trabalhando.",
        "how_to_feel_en": "Burning sensation in legs (glutes and calves), moderate sweating. Controlled but intense breathing.",
        "how_to_feel_es": "Sensación de ardor en las piernas, sudoración moderada. Respiración controlada pero intensa.",
        "substitutes": ["escada_moderada", "bicicleta_moderada"]
    },
    "bicicleta_leve": {
        "id": "bicicleta_leve",
        "name": "Bicicleta Ergométrica Leve",
        "name_en": "Light Stationary Bike",
        "name_es": "Bicicleta Estática Ligera",
        "duration_minutes": 30,
        "intensity": "low",
        "calories_per_min": 5,
        "heart_rate_zone": "Zona 2 (60-70% FCM)",
        "description": "Pedalada leve, resistência baixa, ritmo constante",
        "description_en": "Light pedaling, low resistance, steady pace",
        "description_es": "Pedaleo ligero, resistencia baja, ritmo constante",
        "how_to_feel": "Movimento fluido, sem esforço nas pernas. Respiração tranquila. Ótimo para recuperação ativa ou aquecimento.",
        "how_to_feel_en": "Fluid movement, no strain on legs. Calm breathing. Great for active recovery or warm-up.",
        "how_to_feel_es": "Movimiento fluido, sin esfuerzo en las piernas. Respiración tranquila.",
        "substitutes": ["caminhada_leve"]
    },
    "bicicleta_moderada": {
        "id": "bicicleta_moderada",
        "name": "Bicicleta Ergométrica Moderada",
        "name_en": "Moderate Stationary Bike",
        "name_es": "Bicicleta Estática Moderada",
        "duration_minutes": 35,
        "intensity": "moderate",
        "calories_per_min": 8,
        "heart_rate_zone": "Zona 3 (70-80% FCM)",
        "description": "Pedalada com resistência média, ritmo constante",
        "description_en": "Pedaling with medium resistance, steady pace",
        "description_es": "Pedaleo con resistencia media, ritmo constante",
        "how_to_feel": "Coxas trabalhando, suor aparecendo. Respiração mais rápida mas controlada. Consegue manter por 30+ minutos.",
        "how_to_feel_en": "Thighs working, sweating starting. Faster but controlled breathing. Can maintain for 30+ minutes.",
        "how_to_feel_es": "Muslos trabajando, sudoración comenzando. Respiración más rápida pero controlada.",
        "substitutes": ["caminhada_moderada", "escada_leve"]
    },
    "bicicleta_intensa": {
        "id": "bicicleta_intensa",
        "name": "Bicicleta HIIT",
        "name_en": "HIIT Bike",
        "name_es": "Bicicleta HIIT",
        "duration_minutes": 20,
        "intensity": "high",
        "calories_per_min": 12,
        "heart_rate_zone": "Zona 4-5 (80-95% FCM)",
        "description": "Intervalos de alta intensidade: 30s forte / 30s leve",
        "description_en": "High intensity intervals: 30s hard / 30s easy",
        "description_es": "Intervalos de alta intensidad: 30s fuerte / 30s ligero",
        "how_to_feel": "Nos picos: pernas pegando fogo, respiração ofegante. Na recuperação: alívio mas ainda elevado. Suor intenso.",
        "how_to_feel_en": "At peaks: legs burning, heavy breathing. In recovery: relief but still elevated. Intense sweating.",
        "how_to_feel_es": "En los picos: piernas ardiendo, respiración pesada. En recuperación: alivio pero aún elevado.",
        "substitutes": ["escada_intensa"]
    },
    "escada_leve": {
        "id": "escada_leve",
        "name": "Escada/StairMaster Leve",
        "name_en": "Light StairMaster",
        "name_es": "Escaladora Ligera",
        "duration_minutes": 20,
        "intensity": "moderate",
        "calories_per_min": 7,
        "heart_rate_zone": "Zona 3 (70-80% FCM)",
        "description": "Subida de escada em ritmo constante, velocidade baixa",
        "description_en": "Stair climbing at steady pace, low speed",
        "description_es": "Subida de escalera a ritmo constante, velocidad baja",
        "how_to_feel": "Glúteos e quadríceps aquecendo, respiração controlada. Sensação de trabalho muscular contínuo.",
        "how_to_feel_en": "Glutes and quads warming up, controlled breathing. Feeling of continuous muscle work.",
        "how_to_feel_es": "Glúteos y cuádriceps calentando, respiración controlada.",
        "substitutes": ["caminhada_inclinada", "bicicleta_moderada"]
    },
    "escada_moderada": {
        "id": "escada_moderada",
        "name": "Escada/StairMaster Moderada",
        "name_en": "Moderate StairMaster",
        "name_es": "Escaladora Moderada",
        "duration_minutes": 25,
        "intensity": "moderate",
        "calories_per_min": 10,
        "heart_rate_zone": "Zona 3-4 (75-85% FCM)",
        "description": "Subida de escada com velocidade média",
        "description_en": "Stair climbing at medium speed",
        "description_es": "Subida de escalera a velocidad media",
        "how_to_feel": "Pernas trabalhando forte, suor visível. Respiração pesada mas consegue manter o ritmo. Queimação muscular.",
        "how_to_feel_en": "Legs working hard, visible sweating. Heavy breathing but can maintain pace. Muscle burn.",
        "how_to_feel_es": "Piernas trabajando fuerte, sudoración visible. Respiración pesada pero puede mantener el ritmo.",
        "substitutes": ["caminhada_inclinada", "bicicleta_intensa"]
    },
    "escada_intensa": {
        "id": "escada_intensa",
        "name": "Escada/StairMaster Intensa",
        "name_en": "Intense StairMaster",
        "name_es": "Escaladora Intensa",
        "duration_minutes": 15,
        "intensity": "high",
        "calories_per_min": 14,
        "heart_rate_zone": "Zona 4-5 (85-95% FCM)",
        "description": "Subida rápida com velocidade alta",
        "description_en": "Fast climbing at high speed",
        "description_es": "Subida rápida a alta velocidad",
        "how_to_feel": "Pernas em chamas, suor escorrendo. Respiração muito pesada, difícil falar. Sensação de exaustão produtiva.",
        "how_to_feel_en": "Legs on fire, sweat dripping. Very heavy breathing, hard to talk. Feeling of productive exhaustion.",
        "how_to_feel_es": "Piernas en llamas, sudor goteando. Respiración muy pesada, difícil hablar.",
        "substitutes": ["bicicleta_intensa"]
    }
}

def generate_cardio_for_goal(goal: str, weight: float, competition_phase: Optional[str] = None) -> List[dict]:
    """
    Gera sessão de cardio baseada no objetivo.
    
    REGRAS:
    - Cutting/Pre-Contest: Mais cardio (4-6x/semana), foco em queima
    - Bulking/Off-Season: Cardio mínimo (2-3x/semana), preservar massa
    - Manutenção: Cardio moderado (3-4x/semana)
    - Peak Week: LISS leve apenas (recuperação)
    """
    exercises = []
    
    if goal == "cutting" or competition_phase == "pre_contest":
        # Cutting: foco em queima calórica
        exercises = [
            {**CARDIO_EXERCISES["caminhada_inclinada"], "sessions_per_week": 3},
            {**CARDIO_EXERCISES["bicicleta_moderada"], "sessions_per_week": 2},
            {**CARDIO_EXERCISES["escada_moderada"], "sessions_per_week": 1},
        ]
    elif goal == "bulking" or competition_phase == "off_season":
        # Bulking: cardio mínimo para saúde cardiovascular
        exercises = [
            {**CARDIO_EXERCISES["caminhada_leve"], "sessions_per_week": 2},
            {**CARDIO_EXERCISES["bicicleta_leve"], "sessions_per_week": 1},
        ]
    elif competition_phase == "peak_week":
        # Peak Week: apenas LISS leve
        exercises = [
            {**CARDIO_EXERCISES["caminhada_leve"], "sessions_per_week": 2},
        ]
    elif competition_phase == "post_show":
        # Post-Show: cardio moderado para transição
        exercises = [
            {**CARDIO_EXERCISES["bicicleta_leve"], "sessions_per_week": 2},
            {**CARDIO_EXERCISES["caminhada_moderada"], "sessions_per_week": 1},
        ]
    else:  # manutencao
        # Manutenção: equilíbrio
        exercises = [
            {**CARDIO_EXERCISES["caminhada_moderada"], "sessions_per_week": 2},
            {**CARDIO_EXERCISES["bicicleta_moderada"], "sessions_per_week": 1},
            {**CARDIO_EXERCISES["escada_leve"], "sessions_per_week": 1},
        ]
    
    # Calcula calorias estimadas por exercício e substitutos com tempo equivalente
    for ex in exercises:
        ex["calories_burned"] = ex["calories_per_min"] * ex["duration_minutes"]
        
        # Converte substitutes para lista de exercícios com tempo equivalente
        original_calories = ex["calories_burned"]
        substitutes_with_time = []
        
        for sub_id in ex.get("substitutes", []):
            sub_exercise = CARDIO_EXERCISES.get(sub_id)
            if sub_exercise:
                # Calcula tempo equivalente para queimar as mesmas calorias
                sub_calories_per_min = sub_exercise.get("calories_per_min", 5)
                equivalent_minutes = round(original_calories / sub_calories_per_min)
                
                substitutes_with_time.append({
                    "id": sub_id,
                    "name": sub_exercise["name"],
                    "name_en": sub_exercise["name_en"],
                    "name_es": sub_exercise["name_es"],
                    "original_duration": ex["duration_minutes"],
                    "equivalent_duration": equivalent_minutes,
                    "intensity": sub_exercise["intensity"],
                    "calories_per_min": sub_calories_per_min
                })
        
        ex["substitutes_detailed"] = substitutes_with_time
        # Mantém lista simples para compatibilidade
        ex["substitutes"] = [s["name"] for s in substitutes_with_time]
    
    return exercises

@api_router.get("/cardio/{user_id}")
async def get_user_cardio(user_id: str):
    """
    Retorna plano de cardio do usuário baseado no objetivo.
    """
    # Busca perfil do usuário
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    goal = user.get("goal", "manutencao")
    weight = user.get("weight", 70)
    competition_phase = user.get("competition_phase")
    
    # Gera cardio
    exercises = generate_cardio_for_goal(goal, weight, competition_phase)
    
    # Calcula totais
    total_duration = sum(ex["duration_minutes"] * ex["sessions_per_week"] for ex in exercises)
    total_calories = sum(ex["calories_burned"] * ex["sessions_per_week"] for ex in exercises)
    total_sessions = sum(ex["sessions_per_week"] for ex in exercises)
    
    return {
        "user_id": user_id,
        "goal": goal,
        "competition_phase": competition_phase,
        "exercises": exercises,
        "weekly_summary": {
            "total_sessions": total_sessions,
            "total_duration_minutes": total_duration,
            "total_calories_burned": total_calories
        },
        "tips": {
            "pt": "Faça o cardio em qualquer horário do dia. O importante é a consistência!",
            "en": "Do cardio at any time of day. Consistency is key!",
            "es": "Haz cardio a cualquier hora del día. ¡La consistencia es clave!"
        }
    }

@api_router.post("/cardio/{user_id}/substitute")
async def substitute_cardio_exercise(user_id: str, exercise_id: str, substitute_id: str):
    """
    Substitui um exercício de cardio por outro.
    """
    if exercise_id not in CARDIO_EXERCISES:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    
    if substitute_id not in CARDIO_EXERCISES:
        raise HTTPException(status_code=404, detail="Substituto não encontrado")
    
    original = CARDIO_EXERCISES[exercise_id]
    substitute = CARDIO_EXERCISES[substitute_id]
    
    # Verifica se é um substituto válido
    if substitute_id not in original.get("substitutes", []):
        raise HTTPException(status_code=400, detail="Este não é um substituto válido para este exercício")
    
    return {
        "success": True,
        "original": original,
        "substitute": substitute,
        "message": f"Substituído {original['name']} por {substitute['name']}"
    }

@api_router.get("/cardio/exercises/all")
async def get_all_cardio_exercises():
    """
    Retorna todos os exercícios de cardio disponíveis.
    """
    return {
        "exercises": list(CARDIO_EXERCISES.values()),
        "categories": {
            "caminhada": ["caminhada_leve", "caminhada_moderada", "caminhada_inclinada"],
            "bicicleta": ["bicicleta_leve", "bicicleta_moderada", "bicicleta_intensa"],
            "escada": ["escada_leve", "escada_moderada", "escada_intensa"]
        }
    }

# ==================== SETTINGS ENDPOINTS ====================

@api_router.get("/user/settings/{user_id}", response_model=UserSettings)
async def get_user_settings(user_id: str):
    """
    Busca configurações do usuário
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca settings ou retorna defaults
    settings = await db.user_settings.find_one({"user_id": user_id})
    
    if not settings:
        # Cria settings padrão
        default_settings = UserSettings(user_id=user_id)
        settings_dict = default_settings.dict()
        await db.user_settings.insert_one(settings_dict)
        return default_settings
    
    return UserSettings(**settings)

@api_router.patch("/user/settings/{user_id}", response_model=UserSettings)
async def update_user_settings(user_id: str, update_data: UserSettingsUpdate):
    """
    Atualiza configurações do usuário
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Valida theme_preference
    if update_data.theme_preference and update_data.theme_preference not in ["system", "light", "dark"]:
        raise HTTPException(
            status_code=400,
            detail="theme_preference deve ser 'system', 'light' ou 'dark'"
        )
    
    # Valida meal_count
    if update_data.meal_count and update_data.meal_count not in [4, 5, 6]:
        raise HTTPException(
            status_code=400,
            detail="meal_count deve ser 4, 5 ou 6"
        )
    
    # Busca settings existentes ou cria
    settings = await db.user_settings.find_one({"user_id": user_id})
    
    update_dict = {}
    for k, v in update_data.dict().items():
        if v is not None:
            if k == "meal_times" and v:
                # Converte lista de MealTimeConfig para dict
                update_dict[k] = [{"name": m["name"], "time": m["time"]} for m in v]
            else:
                update_dict[k] = v
    
    update_dict["updated_at"] = datetime.utcnow()
    
    if settings:
        await db.user_settings.update_one(
            {"user_id": user_id},
            {"$set": update_dict}
        )
    else:
        # Cria novo settings com updates
        new_settings = UserSettings(user_id=user_id, **update_dict)
        await db.user_settings.insert_one(new_settings.dict())
    
    # Retorna settings atualizado
    updated = await db.user_settings.find_one({"user_id": user_id})
    return UserSettings(**updated)

@api_router.put("/user/settings/{user_id}", response_model=UserSettings)
async def update_user_settings_put(user_id: str, update_data: UserSettingsUpdate):
    """
    PUT endpoint para atualizar configurações (compatibilidade frontend)
    """
    return await update_user_settings(user_id, update_data)

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()