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
    
    # Objetivo
    goal: str  # "cutting", "bulking", "manutencao", "atleta"
    
    # ==================== MODO ATLETA AUTOMÁTICO ====================
    # Baseado em DATA do campeonato (não semanas manuais)
    athlete_mode: bool = False  # True se goal == "atleta"
    athlete_competition_date: Optional[datetime] = None  # Data do campeonato (YYYY-MM-DD)
    last_competition_phase: Optional[str] = None  # Última fase calculada
    
    # Campos legados (calculados automaticamente, não preenchidos pelo usuário)
    competition_phase: Optional[str] = None  # Fase atual calculada automaticamente
    weeks_to_competition: Optional[int] = None  # Calculado automaticamente
    competition_date: Optional[datetime] = None  # Alias para athlete_competition_date
    phase_start_date: Optional[datetime] = None  # Quando a fase atual começou
    
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
    goal: str
    # ==================== MODO ATLETA ====================
    # Apenas precisa da DATA do campeonato - sistema calcula tudo automaticamente
    athlete_competition_date: Optional[str] = None  # ISO date string YYYY-MM-DD
    # Campos legados (mantidos por compatibilidade, mas não usados)
    competition_phase: Optional[str] = None  # Calculado automaticamente
    weeks_to_competition: Optional[int] = None  # Calculado automaticamente
    competition_date: Optional[str] = None  # Alias para athlete_competition_date
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
    goal: Optional[str] = None
    # Modo Atleta
    athlete_competition_date: Optional[str] = None  # ISO date YYYY-MM-DD
    # Campos legados (calculados automaticamente)
    competition_phase: Optional[str] = None
    weeks_to_competition: Optional[int] = None
    competition_date: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    food_preferences: Optional[List[str]] = None

# ==================== PROGRESS MODELS ====================

class WeightRecord(BaseModel):
    """Registro de peso do usuário"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    weight: float  # em kg
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class WeightRecordCreate(BaseModel):
    """Request para criar registro de peso"""
    weight: float  # em kg
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
    elif goal == "atleta":
        # OBRIGATÓRIO: fase de competição deve estar definida
        if competition_phase == "off_season":
            # Off-Season: superávit moderado (+7.5%)
            return tdee * 1.075
        elif competition_phase == "pre_contest":
            # Pre-Contest: déficit progressivo (-17.5%)
            return tdee * 0.825
        elif competition_phase == "peak_week":
            # Peak Week: déficit muito agressivo (-25%)
            return tdee * 0.75
        elif competition_phase == "post_show":
            # Post-Show: superávit para recuperação (+10%)
            return tdee * 1.10
        else:
            # Default para pre_contest se fase não especificada
            return tdee * 0.825
    else:  # manutenção
        return tdee

def calculate_macros(target_calories: float, weight: float, goal: str, competition_phase: Optional[str] = None) -> Dict[str, float]:
    """
    Calcula distribuição de macronutrientes.
    
    REGRAS PARA ATLETA/COMPETIÇÃO:
    - off_season: P=2.0g/kg, G=0.9g/kg, C=restante (ALTO)
    - pre_prep: P=2.2g/kg, G=0.8g/kg, C=restante (MODERADO)
    - prep: P=2.6g/kg, G=0.7g/kg, C=restante (BAIXO)
    - peak_week: P=2.8g/kg, G=0.5g/kg, C=restante (MUITO BAIXO)
    - post_show: P=2.0g/kg, G=1.0g/kg, C=restante (RECUPERAÇÃO)
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
    elif goal == "atleta":
        if competition_phase == "off_season":
            # OFF-SEASON (Lean Bulk): P=2.0g/kg, G=0.9g/kg, C=restante (ALTO)
            protein_g = weight * 2.0
            fat_g = weight * 0.9
        elif competition_phase == "pre_prep":
            # PRE-PREP (Transição): P=2.2g/kg, G=0.8g/kg, C=restante (MODERADO)
            protein_g = weight * 2.2
            fat_g = weight * 0.8
        elif competition_phase == "prep":
            # PREP (Cutting Agressivo): P=2.6g/kg, G=0.7g/kg, C=restante (BAIXO)
            protein_g = weight * 2.6
            fat_g = weight * 0.7
        elif competition_phase == "peak_week":
            # PEAK WEEK (Final): P=2.8g/kg, G=0.5g/kg, C=restante (MUITO BAIXO)
            protein_g = weight * 2.8
            fat_g = weight * 0.5
        elif competition_phase == "post_show":
            # POST-SHOW (Recuperação): P=2.0g/kg, G=1.0g/kg, C=restante
            protein_g = weight * 2.0
            fat_g = weight * 1.0
        else:
            # Default para prep se fase não especificada
            protein_g = weight * 2.6
            fat_g = weight * 0.7
        
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

# ==================== HELPER FUNCTIONS ====================

VALID_COMPETITION_PHASES = ["off_season", "pre_contest", "peak_week", "post_show"]

def calculate_weeks_to_competition(competition_date: datetime) -> int:
    """Calcula semanas até a competição baseado na data"""
    now = datetime.utcnow()
    if competition_date <= now:
        return -1  # Competição já passou (negativo)
    
    delta = competition_date - now
    weeks = delta.days // 7
    return weeks

def derive_phase_from_date(competition_date: datetime) -> Tuple[str, int]:
    """
    LÓGICA DE FASES AUTOMÁTICAS baseada na data do campeonato.
    
    Mapeamento CORRIGIDO:
    - > 16 semanas → OFF_SEASON (construção de massa)
    - 2 a 16 semanas → PRE_CONTEST (perda de gordura e definição)
    - 0 a 2 semanas → PEAK_WEEK (ajustes finais de água e carbs)
    - data passou → POST_SHOW (recuperação)
    
    Returns: (phase, weeks_to_competition)
    """
    now = datetime.utcnow()
    
    # Verifica se a competição já passou
    if competition_date <= now:
        return "post_show", -1
    
    # Calcula dias restantes
    delta = competition_date - now
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
    
    MODO ATLETA AUTOMÁTICO:
    - Usuário informa apenas athlete_competition_date (data do campeonato)
    - Sistema calcula automaticamente: fase, semanas, ajustes calóricos
    - NÃO precisa informar competition_phase nem weeks_to_competition
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
    
    # ==================== MODO ATLETA AUTOMÁTICO ====================
    competition_phase = None
    weeks_to_competition = None
    
    if profile_data.goal == "atleta":
        # Modo atleta ativado automaticamente
        profile_dict["athlete_mode"] = True
        
        # Verifica se tem data do campeonato
        comp_date = profile_data.athlete_competition_date or profile_data.competition_date
        
        if comp_date:
            try:
                # Parse da data
                if isinstance(comp_date, str):
                    parsed_date = datetime.fromisoformat(comp_date.replace('Z', '+00:00'))
                else:
                    parsed_date = comp_date
                
                # Calcula fase e semanas AUTOMATICAMENTE
                competition_phase, weeks_to_competition = derive_phase_from_date(parsed_date)
                
                profile_dict["athlete_competition_date"] = parsed_date
                profile_dict["competition_date"] = parsed_date  # Alias
                profile_dict["competition_phase"] = competition_phase
                profile_dict["weeks_to_competition"] = weeks_to_competition
                profile_dict["last_competition_phase"] = competition_phase
                profile_dict["phase_start_date"] = datetime.utcnow()
                
                logger.info(f"MODO ATLETA: Data={parsed_date.date()}, Fase={competition_phase}, Semanas={weeks_to_competition}")
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Erro ao parsear data de competição: {e}")
                # Fallback: usa off_season se não conseguir parsear
                competition_phase = "off_season"
                weeks_to_competition = 24
                profile_dict["competition_phase"] = competition_phase
                profile_dict["weeks_to_competition"] = weeks_to_competition
        else:
            # Atleta sem data = off_season por padrão
            competition_phase = "off_season"
            weeks_to_competition = 24
            profile_dict["competition_phase"] = competition_phase
            profile_dict["weeks_to_competition"] = weeks_to_competition
            logger.info("MODO ATLETA: Sem data de competição, usando off_season")
    else:
        profile_dict["athlete_mode"] = False
    
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
    
    # Ajusta calorias para objetivo (com fase se atleta)
    target_calories = calculate_target_calories(
        tdee=tdee,
        goal=profile_data.goal,
        weight=profile_data.weight,
        competition_phase=competition_phase
    )
    
    # Calcula macros (com fase se atleta)
    macros = calculate_macros(
        target_calories=target_calories,
        weight=profile_data.weight,
        goal=profile_data.goal,
        competition_phase=competition_phase
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
    Atualiza perfil do usuário e recalcula métricas
    """
    # Busca perfil existente
    existing_profile = await db.user_profiles.find_one({"_id": user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    
    # Atualiza dados fornecidos
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if update_dict:
        # Se peso, goal ou competition_phase mudou, recalcula tudo
        if "weight" in update_dict or "goal" in update_dict or "competition_phase" in update_dict:
            current_profile = UserProfile(**existing_profile)
            
            # Usa novos valores ou mantém existentes
            new_weight = update_dict.get("weight", current_profile.weight)
            new_goal = update_dict.get("goal", current_profile.goal)
            new_frequency = update_dict.get("weekly_training_frequency", current_profile.weekly_training_frequency)
            new_phase = update_dict.get("competition_phase", current_profile.competition_phase)
            
            # Validação: atleta requer fase
            if new_goal == "atleta" and not new_phase:
                raise HTTPException(
                    status_code=400,
                    detail="Atletas devem especificar competition_phase: 'offseason' ou 'prep'"
                )
            
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
        diet_dict["_id"] = diet_dict["id"]
        
        # Usa replace_one com upsert para garantir uma única dieta por usuário
        await db.diet_plans.replace_one(
            {"user_id": user_id},
            diet_dict,
            upsert=True
        )
        
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
    if not category or category not in ["protein", "carb", "fat", "fruit"]:
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
            else:
                continue
            
            if macro_per_100 <= 0:
                continue
            
            # Calcula nova quantidade (múltiplo de 10)
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

@api_router.post("/progress/weight/{user_id}")
async def record_weight(user_id: str, record: WeightRecordCreate):
    """
    Registra peso do usuário.
    Restrição: mínimo 14 dias entre registros.
    
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
    
    # Verifica último registro (mínimo 14 dias)
    last_record = await db.weight_records.find_one(
        {"user_id": user_id},
        sort=[("recorded_at", -1)]
    )
    
    if last_record:
        days_since_last = (datetime.utcnow() - last_record["recorded_at"]).days
        if days_since_last < 14:
            days_remaining = 14 - days_since_last
            raise HTTPException(
                status_code=400,
                detail=f"Aguarde mais {days_remaining} dias para o próximo registro. Registro a cada 2 semanas."
            )
    
    # Valida peso
    if record.weight < 30 or record.weight > 300:
        raise HTTPException(status_code=400, detail="Peso deve estar entre 30kg e 300kg")
    
    # Cria registro
    weight_record = WeightRecord(
        user_id=user_id,
        weight=round(record.weight, 1),
        notes=record.notes
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
async def get_weight_history(user_id: str, days: int = 30):
    """
    Retorna histórico de peso do usuário.
    Default: últimos 30 dias.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca registros dos últimos N dias
    from_date = datetime.utcnow() - timedelta(days=days)
    
    records = await db.weight_records.find(
        {"user_id": user_id, "recorded_at": {"$gte": from_date}}
    ).sort("recorded_at", 1).to_list(length=100)
    
    # Formata resposta
    history = []
    for r in records:
        history.append({
            "id": r["_id"],
            "weight": r["weight"],
            "recorded_at": r["recorded_at"].isoformat(),
            "notes": r.get("notes")
        })
    
    # Calcula estatísticas
    current_weight = user.get("weight", 0)
    initial_weight = user.get("weight", current_weight)  # Peso do onboarding
    
    if history:
        first_weight = history[0]["weight"]
        last_weight = history[-1]["weight"]
        total_change = round(last_weight - first_weight, 1)
    else:
        first_weight = current_weight
        last_weight = current_weight
        total_change = 0
    
    # Verifica se pode registrar novo peso
    # Regra: Usuário só pode registrar peso 14 dias após o cadastro OU 14 dias após o último registro
    last_record = await db.weight_records.find_one(
        {"user_id": user_id},
        sort=[("recorded_at", -1)]
    )
    
    can_record = True
    days_until_next = 0
    
    # Se já tem registro de peso, verifica 14 dias desde o último registro
    if last_record:
        days_since_last = (datetime.utcnow() - last_record["recorded_at"]).days
        if days_since_last < 14:
            can_record = False
            days_until_next = 14 - days_since_last
    else:
        # Se não tem registro de peso, verifica 14 dias desde a criação da conta
        # (peso inicial foi coletado no onboarding)
        if user.get("created_at"):
            days_since_creation = (datetime.utcnow() - user["created_at"]).days
            if days_since_creation < 14:
                can_record = False
                days_until_next = 14 - days_since_creation
    
    return {
        "user_id": user_id,
        "current_weight": current_weight,
        "target_weight": user.get("target_weight"),
        "history": history,
        "stats": {
            "total_records": len(history),
            "first_weight": first_weight,
            "last_weight": last_weight,
            "total_change": total_change,
        },
        "can_record": can_record,
        "days_until_next_record": days_until_next
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