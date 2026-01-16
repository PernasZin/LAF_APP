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

# ROOT LEVEL HEALTH CHECK - Required for Kubernetes deployment
@app.get("/health")
async def root_health_check():
    """Health check endpoint at root level for Kubernetes probes"""
    return {"status": "healthy", "service": "LAF Backend"}

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
    
    # Configurações
    language: str = "pt-BR"  # "pt-BR", "en-US", "es-ES"
    
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
    meal_count: Optional[int] = 6  # 4, 5, ou 6 refeições por dia
    language: str = "pt-BR"  # "pt-BR", "en-US", "es-ES"

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    weight: Optional[float] = None
    target_weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    weekly_training_frequency: Optional[int] = None
    training_level: Optional[str] = None  # "novato", "iniciante", "intermediario", "avancado"
    training_duration: Optional[int] = None  # Tempo disponível em minutos
    goal: Optional[str] = None  # "cutting", "bulking", "manutencao"
    dietary_restrictions: Optional[List[str]] = None
    food_preferences: Optional[List[str]] = None
    meal_count: Optional[int] = None  # 4, 5, ou 6 refeições

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

def calculate_target_calories(tdee: float, goal: str, weight: float) -> float:
    """
    Calcula calorias baseado na fórmula simplificada.
    Usa: kcal = (proteína × 4) + (carbo × 4) + (gordura × 9)
    """
    macros = calculate_macros(0, weight, goal)  # tdee não é mais usado
    return (macros["protein"] * 4) + (macros["carbs"] * 4) + (macros["fat"] * 9)

def calculate_macros(target_calories: float, weight: float, goal: str) -> Dict[str, float]:
    """
    🎯 FÓRMULA SIMPLIFICADA DE MACROS
    
    CUTTING:
       - Proteína: peso × 2.2
       - Carboidrato: peso × 2.5
       - Gordura: peso × 0.8
    
    MANUTENÇÃO:
       - Proteína: peso × 2.0
       - Carboidrato: peso × 3.5
       - Gordura: peso × 0.85
    
    BULKING:
       - Proteína: peso × 2.0
       - Carboidrato: peso × 5.0
       - Gordura: peso × 0.9
    """
    if goal == "cutting":
        protein_g = weight * 2.2
        carbs_g = weight * 2.5
        fat_g = weight * 0.8
    elif goal == "bulking":
        protein_g = weight * 2.0
        carbs_g = weight * 5.0
        fat_g = weight * 0.9
    else:  # manutenção
        protein_g = weight * 2.0
        carbs_g = weight * 3.5
        fat_g = weight * 0.85
    
    return {
        "protein": round(protein_g, 1),
        "carbs": round(carbs_g, 1),
        "fat": round(fat_g, 1)
    }

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
    
    # ✅ SALVA meal_count nas user_settings também
    meal_count = profile_data.meal_count if profile_data.meal_count and profile_data.meal_count in [4, 5, 6] else 6
    logger.info(f"Saving meal_count={meal_count} for user {profile_data.id}")
    
    await db.user_settings.update_one(
        {"user_id": profile_data.id},
        {"$set": {"meal_count": meal_count, "user_id": profile_data.id, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    
    # Também salva meal_count no próprio perfil para fallback
    await db.user_profiles.update_one(
        {"_id": profile_data.id},
        {"$set": {"meal_count": meal_count}}
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
    """
    # Busca perfil existente
    existing_profile = await db.user_profiles.find_one({"_id": user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    
    # Atualiza dados fornecidos
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    # Mapeia training_duration para available_time_per_session (nome do campo no UserProfile)
    if "training_duration" in update_dict:
        update_dict["available_time_per_session"] = update_dict.pop("training_duration")
    
    if update_dict:
        current_profile = UserProfile(**existing_profile)
        new_goal = update_dict.get("goal", current_profile.goal)
        new_level = update_dict.get("training_level", current_profile.training_level)
        new_frequency = update_dict.get("weekly_training_frequency", current_profile.weekly_training_frequency)
        new_weight = update_dict.get("weight", current_profile.weight)
        
        # Se peso, goal, level ou frequência mudou, recalcula macros
        if any(key in update_dict for key in ["weight", "goal", "training_level", "weekly_training_frequency"]):
            # Recalcula
            bmr = calculate_bmr(
                weight=new_weight,
                height=current_profile.height,
                age=current_profile.age,
                sex=current_profile.sex
            )
            tdee = calculate_tdee(bmr, new_frequency, new_level)
            target_calories = calculate_target_calories(tdee, new_goal, new_weight)
            macros = calculate_macros(target_calories, new_weight, new_goal)
            
            update_dict["tdee"] = round(tdee, 0)
            update_dict["target_calories"] = round(target_calories, 0)
            update_dict["macros"] = macros
        
        update_dict["updated_at"] = datetime.utcnow()
        
        await db.user_profiles.update_one(
            {"_id": user_id},
            {"$set": update_dict}
        )
        
        logger.info(f"Profile updated for user {user_id}: {list(update_dict.keys())}")
    
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
async def generate_diet(user_id: str, request_meal_count: Optional[int] = None):
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
        
        # PRIORIDADE 1: User Settings (mais recente)
        if user_settings and user_settings.get('meal_count') in [4, 5, 6]:
            meal_count = user_settings.get('meal_count')
            meal_times = user_settings.get('meal_times', None)
        # PRIORIDADE 2: User Profile (fallback)
        elif user_profile.get('meal_count') and user_profile.get('meal_count') in [4, 5, 6]:
            meal_count = user_profile.get('meal_count')
        
        # Valida meal_count
        if meal_count not in [4, 5, 6]:
            meal_count = 6
        
        print(f"[DIET] Gerando dieta com meal_count={meal_count} para user={user_id}")
        
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
        
        # Traduz a dieta baseado no idioma do usuário
        user_language = user_profile.get('language', 'pt-BR')
        lang_code = user_language.split('-')[0] if user_language else 'pt'  # 'pt-BR' -> 'pt'
        
        if lang_code in ['en', 'es']:
            from diet.translations import translate_diet
            diet_dict_translated = translate_diet(diet_plan.dict(), lang_code)
            return diet_dict_translated
        
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
    
    # Traduz baseado no idioma do perfil do usuário
    user_profile = await db.user_profiles.find_one({"_id": user_id})
    if user_profile:
        user_language = user_profile.get('language', 'pt-BR')
        lang_code = user_language.split('-')[0] if user_language else 'pt'
        
        if lang_code in ['en', 'es']:
            from diet.translations import translate_diet
            return translate_diet(diet_plan, lang_code)
    
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


@api_router.get("/diet/{user_id}/substitutes/{food_key}")
async def get_food_substitutes(user_id: str, food_key: str):
    """
    Retorna lista de alimentos substitutos da mesma categoria.
    Calcula automaticamente a quantidade para manter os macros.
    """
    from diet_service import FOODS
    
    # Busca dieta pelo user_id
    diet_plan = await db.diet_plans.find_one({"user_id": user_id})
    if not diet_plan:
        # Tenta buscar por _id também (compatibilidade)
        diet_plan = await db.diet_plans.find_one({"_id": user_id})
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


@api_router.put("/diet/{user_id}/substitute")
async def substitute_food(user_id: str, request: FoodSubstitutionRequest):
    """
    Substitui um alimento na dieta mantendo os macros.
    A substituição é permanente.
    """
    from diet_service import FOODS
    
    # Busca dieta pelo user_id
    diet_plan = await db.diet_plans.find_one({"user_id": user_id})
    if not diet_plan:
        # Tenta buscar por _id também (compatibilidade)
        diet_plan = await db.diet_plans.find_one({"_id": user_id})
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
    
    # Obtém o _id da dieta para atualizar
    diet_id = diet_plan.get("_id")
    
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
    - Bloqueio de 14 dias (2 semanas) para melhor acompanhamento
    
    Retorna informações sobre quando pode atualizar novamente.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueio de 14 dias (2 semanas)
    block_days = 14
    
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
    - Bloqueio de 14 dias (2 semanas) para melhor acompanhamento
    
    QUESTIONÁRIO (0-10):
    - Dieta: Como seguiu a dieta?
    - Treino: Como foram os treinos?
    - Cardio: Como foi o cardio?
    - Sono: Como foi o sono?
    - Hidratação: Como foi a hidratação?
    """
    from diet_service import evaluate_progress, adjust_diet_quantities
    
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueio de 14 dias (2 semanas)
    block_days = 14
    
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
                detail=f"Aguarde mais {days_remaining} dias para o próximo registro. Atualização a cada 2 semanas."
            )
    
    # Valida peso
    if record.weight < 30 or record.weight > 300:
        raise HTTPException(status_code=400, detail="Peso deve estar entre 30kg e 300kg")
    
    # Calcula média do questionário
    q = record.questionnaire
    questionnaire_avg = round((q.diet + q.training + q.cardio + q.sleep + q.hydration) / 5, 1)
    
    # Cria registro completo
    weight_record = WeightRecord(
        user_id=user_id,
        weight=round(record.weight, 1),
        notes=record.notes,
        questionnaire=record.questionnaire,
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
    adjustment_percent = None
    
    # Só avalia se tiver registro anterior para comparar
    if last_record:
        previous_weight = last_record.get("weight", record.weight)
        current_weight = record.weight
        goal = user.get("goal", "manutencao")
        
        # Avalia progresso
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
        "adjustment_percent": adjustment_percent,
        "message": adjustment_message or "Peso registrado com sucesso"
    }


# Modelo para o check-in completo
class CheckInQuestionnaire(BaseModel):
    diet: int = Field(ge=0, le=10)
    training: int = Field(ge=0, le=10)
    cardio: int = Field(ge=0, le=10)
    sleep: int = Field(ge=0, le=10)
    hydration: int = Field(ge=0, le=10)
    energy: int = Field(ge=0, le=10, default=7)
    hunger: int = Field(ge=0, le=10, default=5)
    followedDiet: str = "yes"  # yes, mostly, no
    followedTraining: str = "yes"
    followedCardio: str = "yes"
    boredFoods: str = ""  # Alimentos que enjoou
    observations: str = ""

class CheckInRequest(BaseModel):
    weight: float
    questionnaire: CheckInQuestionnaire


@api_router.post("/progress/checkin/{user_id}")
async def biweekly_checkin(user_id: str, checkin: CheckInRequest):
    """
    Check-in quinzenal completo com:
    - Registro de peso
    - Questionário expandido
    - Ajuste automático de dieta baseado no objetivo (percentual)
    - Substituição de alimentos que enjoou
    """
    from diet_service import evaluate_progress, adjust_diet_quantities, FOODS, calc_food
    
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueio de 14 dias
    block_days = 14
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
                detail=f"Aguarde mais {days_remaining} dias para o próximo check-in."
            )
    
    # Valida peso
    if checkin.weight < 30 or checkin.weight > 300:
        raise HTTPException(status_code=400, detail="Peso deve estar entre 30kg e 300kg")
    
    q = checkin.questionnaire
    
    # Calcula média do questionário (só as avaliações numéricas principais)
    questionnaire_avg = round((q.diet + q.training + q.cardio + q.sleep + q.hydration + q.energy) / 6, 1)
    
    # Salva registro de peso
    weight_record = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "weight": round(checkin.weight, 1),
        "recorded_at": datetime.utcnow(),
        "questionnaire": q.dict(),
        "questionnaire_average": questionnaire_avg,
    }
    weight_record["_id"] = weight_record["id"]
    await db.weight_records.insert_one(weight_record)
    
    # Atualiza peso no perfil
    await db.user_profiles.update_one(
        {"_id": user_id},
        {"$set": {"weight": round(checkin.weight, 1), "updated_at": datetime.utcnow()}}
    )
    
    logger.info(f"Check-in recorded for user {user_id}: {checkin.weight}kg, avg: {questionnaire_avg}")
    
    # ==================== AJUSTE DE DIETA ====================
    diet_kept = True
    calories_change = 0
    foods_replaced = 0
    
    current_diet = await db.diet_plans.find_one({"user_id": user_id})
    
    if current_diet and last_record:
        previous_weight = last_record.get("weight", checkin.weight)
        current_weight = checkin.weight
        goal = user.get("goal", "manutencao")
        
        # Avalia progresso
        progress_eval = evaluate_progress(
            goal=goal,
            previous_weight=previous_weight,
            current_weight=current_weight
        )
        
        # Se precisa ajustar calorias
        if progress_eval.get("needs_adjustment"):
            adjusted_diet = adjust_diet_quantities(
                diet_plan=current_diet,
                adjustment_type=progress_eval["adjustment_type"],
                adjustment_percent=progress_eval["adjustment_percent"]
            )
            
            # Calcula mudança de calorias
            old_calories = current_diet.get("total_calories", 0)
            new_calories = adjusted_diet.get("total_calories", old_calories)
            calories_change = new_calories - old_calories
            
            adjusted_diet["adjusted_at"] = datetime.utcnow()
            adjusted_diet["adjustment_reason"] = progress_eval["reason"]
            
            await db.diet_plans.replace_one(
                {"_id": current_diet["_id"]},
                adjusted_diet,
                upsert=True
            )
            
            current_diet = adjusted_diet
            diet_kept = False
            
            logger.info(f"Diet adjusted for {user_id}: {calories_change}kcal change")
    
    # ==================== SUBSTITUIÇÃO DE ALIMENTOS ====================
    if current_diet and q.boredFoods and q.boredFoods.strip():
        import random
        bored_list = [f.strip().lower() for f in q.boredFoods.split(',')]
        
        # Procura alimentos para substituir
        for meal in current_diet.get("meals", []):
            for i, food in enumerate(meal.get("foods", [])):
                food_name_lower = food.get("name", "").lower()
                food_key = food.get("key", "")
                
                # Verifica se o alimento está na lista de enjoados
                should_replace = any(bored in food_name_lower for bored in bored_list)
                
                if should_replace:
                    # Obtém categoria do alimento
                    category = food.get("category", "")
                    if not category or category not in ["protein", "carb", "fat", "fruit", "vegetable"]:
                        continue
                    
                    # Busca alimentos da mesma categoria no banco FOODS
                    substitutes = []
                    for key, food_data in FOODS.items():
                        if food_data.get("category") == category and key != food_key:
                            # Verifica se o substituto também não está na lista de enjoados
                            sub_name_lower = food_data.get("name", "").lower()
                            if any(bored in sub_name_lower for bored in bored_list):
                                continue
                            
                            # Calcula quantidade para manter o macro principal
                            if category == "protein":
                                target_macro = food.get("protein", 0)
                                macro_per_100 = food_data.get("p", 1)
                            elif category == "carb":
                                target_macro = food.get("carbs", 0)
                                macro_per_100 = food_data.get("c", 1)
                            elif category == "fat":
                                target_macro = food.get("fat", 0)
                                macro_per_100 = food_data.get("f", 1)
                            elif category == "fruit":
                                target_macro = food.get("carbs", 0)
                                macro_per_100 = food_data.get("c", 1)
                            else:
                                target_macro = food.get("grams", 100)
                                macro_per_100 = 100
                            
                            if macro_per_100 <= 0:
                                continue
                            
                            # Calcula nova quantidade usando calc_food
                            new_grams = round((target_macro / macro_per_100) * 100 / 10) * 10
                            new_grams = max(10, min(500, new_grams))
                            
                            # Usa calc_food para calcular macros corretamente
                            new_food = calc_food(key, new_grams)
                            substitutes.append(new_food)
                    
                    if substitutes:
                        # Escolhe um substituto aleatoriamente
                        new_food = random.choice(substitutes)
                        
                        # Substitui o alimento
                        meal["foods"][i] = new_food
                        foods_replaced += 1
                        
                        logger.info(f"Replaced {food.get('name')} with {new_food.get('name')} for user {user_id}")
        
        # Recalcula totais se houve substituições
        if foods_replaced > 0:
            # Recalcula totais de cada refeição
            for meal in current_diet.get("meals", []):
                foods = meal.get("foods", [])
                meal_p = sum(f.get("protein", 0) for f in foods)
                meal_c = sum(f.get("carbs", 0) for f in foods)
                meal_f = sum(f.get("fat", 0) for f in foods)
                meal_cal = sum(f.get("calories", 0) for f in foods)
                meal["total_calories"] = meal_cal
                meal["macros"] = {"protein": meal_p, "carbs": meal_c, "fat": meal_f}
            
            # Recalcula totais da dieta
            all_foods = [f for m in current_diet.get("meals", []) for f in m.get("foods", [])]
            total_p = sum(f.get("protein", 0) for f in all_foods)
            total_c = sum(f.get("carbs", 0) for f in all_foods)
            total_f = sum(f.get("fat", 0) for f in all_foods)
            total_cal = sum(f.get("calories", 0) for f in all_foods)
            
            current_diet["computed_calories"] = total_cal
            current_diet["computed_macros"] = {"protein": total_p, "carbs": total_c, "fat": total_f}
            current_diet["foods_replaced_at"] = datetime.utcnow()
            
            await db.diet_plans.replace_one(
                {"_id": current_diet["_id"]},
                current_diet,
                upsert=True
            )
    
    return {
        "success": True,
        "weight": checkin.weight,
        "questionnaire_average": questionnaire_avg,
        "diet_kept": diet_kept,
        "calories_change": calories_change,
        "foods_replaced": foods_replaced,
        "message": "Check-in realizado com sucesso!"
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
    
    # Bloqueio de 14 dias (2 semanas)
    block_days = 14
    
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
                "message": f"Em {14 - days_since_last} dia(s) você poderá registrar seu novo peso.",
                "created_at": datetime.utcnow().isoformat(),
                "read": False,
                "action_url": "/progress",
                "priority": "low"
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
            "value": r["weight"]
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
    
    # Metas padrão
    water_target = 3000  # 3L em ml
    sodium_target = 2000  # 2000mg
    
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
    
    # Traduz baseado no idioma do perfil do usuário
    user_profile = await db.user_profiles.find_one({"_id": user_id})
    if user_profile:
        user_language = user_profile.get('language', 'pt-BR')
        lang_code = user_language.split('-')[0] if user_language else 'pt'
        
        if lang_code in ['en', 'es']:
            from workout.translations import translate_workout_plan
            return translate_workout_plan(workout_plan, lang_code)
    
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
    goal: str  # "cutting", "bulking", "manutencao"
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

def generate_cardio_for_goal(goal: str, weight: float) -> List[dict]:
    """
    Gera sessão de cardio baseada no objetivo.
    
    REGRAS:
    - Cutting: Mais cardio (4-6x/semana), foco em queima
    - Bulking: Cardio mínimo (2-3x/semana), preservar massa
    - Manutenção: Cardio moderado (3-4x/semana)
    """
    exercises = []
    
    if goal == "cutting":
        # Cutting: foco em queima calórica
        exercises = [
            {**CARDIO_EXERCISES["caminhada_inclinada"], "sessions_per_week": 3},
            {**CARDIO_EXERCISES["bicicleta_moderada"], "sessions_per_week": 2},
            {**CARDIO_EXERCISES["escada_moderada"], "sessions_per_week": 1},
        ]
    elif goal == "bulking":
        # Bulking: cardio mínimo para saúde cardiovascular
        exercises = [
            {**CARDIO_EXERCISES["caminhada_leve"], "sessions_per_week": 2},
            {**CARDIO_EXERCISES["bicicleta_leve"], "sessions_per_week": 1},
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
    
    # Gera cardio
    exercises = generate_cardio_for_goal(goal, weight)
    
    # Calcula totais
    total_duration = sum(ex["duration_minutes"] * ex["sessions_per_week"] for ex in exercises)
    total_calories = sum(ex["calories_burned"] * ex["sessions_per_week"] for ex in exercises)
    total_sessions = sum(ex["sessions_per_week"] for ex in exercises)
    
    return {
        "user_id": user_id,
        "goal": goal,
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