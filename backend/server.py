from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, Request
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
    preferred_foods: List[str] = Field(default_factory=list)  # Alias para food_preferences
    injury_history: List[str] = Field(default_factory=list)
    meal_count: Optional[int] = 6  # 4, 5, ou 6 refeições por dia
    language: str = "pt-BR"  # "pt-BR", "en-US", "es-ES"
    training_days: List[int] = Field(default_factory=list)  # Dias da semana para treino

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

# ==================== WORKOUT TRACKING MODELS ====================

class WorkoutDayStatus(BaseModel):
    """Status de treino de um dia específico"""
    date: str  # YYYY-MM-DD
    trained: bool = False
    completed_at: Optional[str] = None  # ISO datetime quando foi marcado
    user_id: str

class WorkoutStatusResponse(BaseModel):
    """Resposta do status de treino"""
    date: str
    trained: bool
    is_training_day: bool  # Baseado no plano semanal do usuário
    diet_type: str  # "training" ou "rest"
    calorie_multiplier: float
    carb_multiplier: float

class FinishWorkoutRequest(BaseModel):
    """Request para marcar treino como concluído"""
    date: Optional[str] = None  # Se não informado, usa hoje

class AdjustedMacros(BaseModel):
    """Macros ajustados para o dia"""
    base_calories: float
    adjusted_calories: float
    base_protein: float
    adjusted_protein: float  # Não muda
    base_carbs: float
    adjusted_carbs: float
    base_fat: float
    adjusted_fat: float  # Não muda
    diet_type: str
    multiplier_info: str

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

def normalize_goal(goal: str) -> str:
    """
    Normaliza o objetivo para valores consistentes.
    
    Aceita:
    - "ganho_muscular", "bulking", "hipertrofia" → "bulking"
    - "cutting", "definicao", "emagrecimento" → "cutting"
    - "manutencao", "manutenção", "maintenance" → "manutencao"
    """
    if not goal:
        return "manutencao"
    
    goal = goal.lower().strip()
    
    # Bulking aliases
    if goal in ["ganho_muscular", "bulking", "hipertrofia", "ganho", "massa"]:
        return "bulking"
    
    # Cutting aliases
    if goal in ["cutting", "definicao", "definição", "emagrecimento", "emagrecer"]:
        return "cutting"
    
    # Manutenção aliases
    if goal in ["manutencao", "manutenção", "maintenance", "manter"]:
        return "manutencao"
    
    return "manutencao"  # Default


def get_cardio_weekly_calories(goal: str) -> int:
    """
    Retorna as calorias semanais queimadas pelo cardio planejado.
    Baseado na função generate_cardio_for_goal.
    
    REGRAS:
    - Cutting: Mais cardio (4-6x/semana) ~1270 kcal/semana
    - Bulking: Cardio mínimo (2-3x/semana) ~420 kcal/semana
    - Manutenção: Cardio moderado (3-4x/semana) ~656 kcal/semana
    """
    goal = normalize_goal(goal)
    
    if goal == "cutting":
        # 3x caminhada_inclinada + 2x bike_moderada + 1x escada
        return 1270
    elif goal == "bulking":
        # 2x caminhada_leve + 1x bike_leve
        return 420
    else:  # manutencao
        # 2x caminhada_moderada + 1x bike_moderada + 1x escada_leve
        return 656


def calculate_tdee(bmr: float, training_frequency: int, training_level: str, goal: str = 'manutencao') -> float:
    """
    Calcula TDEE (Total Daily Energy Expenditure) baseado em atividade
    
    INCLUI GASTO DO CARDIO PLANEJADO PELO APP!
    
    Fatores de atividade:
    - 1.3 sedentário (0-1x/semana)
    - 1.45 leve (2-3x/semana)
    - 1.6 moderado (4-5x/semana)
    - 1.75 pesado (6-7x/semana)
    
    Fórmula:
    TDEE_base = BMR × Fator de Atividade
    Cardio_daily = Cardio_weekly / 7
    TDEE_real = TDEE_base + Cardio_daily
    """
    # Mapeia frequência para fator de atividade
    if training_frequency <= 1:
        factor = 1.3   # sedentário
    elif training_frequency <= 3:
        factor = 1.45  # leve
    elif training_frequency <= 5:
        factor = 1.6   # moderado
    else:
        factor = 1.75  # pesado
    
    tdee_base = bmr * factor
    
    # NOVO: Adiciona gasto do cardio planejado
    cardio_weekly = get_cardio_weekly_calories(goal)
    cardio_daily = cardio_weekly / 7
    
    tdee_real = tdee_base + cardio_daily
    
    print(f"[TDEE] BMR={bmr:.0f} × {factor} = TDEE_base={tdee_base:.0f}")
    print(f"[TDEE] Cardio semanal ({goal})={cardio_weekly}kcal -> diário={cardio_daily:.0f}kcal")
    print(f"[TDEE] TDEE_real = {tdee_base:.0f} + {cardio_daily:.0f} = {tdee_real:.0f}kcal")
    
    return tdee_real

def calculate_target_calories(tdee: float, goal: str, weight: float) -> float:
    """
    🎯 Ajusta TDEE baseado no objetivo
    
    CUTTING: TDEE × 0.80 (déficit de 20%)
    MANUTENÇÃO: TDEE × 1.00
    BULKING: TDEE × 1.12 (superávit de 12%)
    """
    goal = normalize_goal(goal)
    
    if goal == "cutting":
        return tdee * 0.80  # -20% déficit
    elif goal == "bulking":
        return tdee * 1.12  # +12% superávit
    else:  # manutenção
        return tdee

def calculate_macros(target_calories: float, weight: float, goal: str) -> Dict[str, float]:
    """
    🎯 Calcula macros com regras esportivas
    
    REGRAS:
    1. PROTEÍNA (prioridade): peso × 2.0 g/kg
       - Limites: 1.8 - 2.3 g/kg
       
    2. GORDURA (controlada): peso × 0.9 g/kg
       - Limites: 0.7 - 1.0 g/kg
       - NUNCA usar para compensar calorias
       
    3. CARBOIDRATO (macro de ajuste):
       - Pisos mínimos por objetivo:
         * CUTTING: peso × 2.0
         * MANUTENÇÃO: peso × 3.0
         * BULKING: peso × 4.5
       - Ajustado para bater calorias ±5%
    """
    goal = normalize_goal(goal)
    
    # 1. PROTEÍNA - fixa em 2.0 g/kg
    protein_g = weight * 2.0
    # Validação de limites
    protein_min = weight * 1.8
    protein_max = weight * 2.3
    protein_g = max(protein_min, min(protein_max, protein_g))
    
    # 2. GORDURA - fixa em 0.9 g/kg
    fat_g = weight * 0.9
    # Validação de limites
    fat_min = weight * 0.7
    fat_max = weight * 1.0
    fat_g = max(fat_min, min(fat_max, fat_g))
    
    # 3. CARBOIDRATO - macro de ajuste
    # Pisos mínimos por objetivo
    if goal == "cutting":
        carb_min = weight * 2.0
    elif goal == "bulking":
        carb_min = weight * 4.5
    else:  # manutenção
        carb_min = weight * 3.0
    
    # Calorias de proteína e gordura (fixas)
    protein_cal = protein_g * 4
    fat_cal = fat_g * 9
    
    # Calorias restantes para carboidrato
    carb_cal = target_calories - protein_cal - fat_cal
    carb_g = carb_cal / 4
    
    # Garante piso mínimo de carbs
    carb_g = max(carb_min, carb_g)
    
    # 4. VALIDAÇÃO FINAL - calorias dentro de ±5%
    total_cal = (protein_g * 4) + (carb_g * 4) + (fat_g * 9)
    cal_diff_pct = abs(total_cal - target_calories) / target_calories * 100
    
    # Se fora do ±5%, ajusta APENAS carboidrato
    if cal_diff_pct > 5:
        # Recalcula carbs para bater calorias
        carb_cal_needed = target_calories - protein_cal - fat_cal
        carb_g_adjusted = carb_cal_needed / 4
        # Mas nunca abaixo do piso
        carb_g = max(carb_min, carb_g_adjusted)
    
    return {
        "protein": round(protein_g, 1),
        "carbs": round(carb_g, 1),
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
    
    # MAPEAMENTO: preferred_foods -> food_preferences (compatibilidade frontend)
    if hasattr(profile_data, 'preferred_foods') and profile_data.preferred_foods:
        profile_dict["food_preferences"] = profile_data.preferred_foods
    elif "preferred_foods" in profile_dict and profile_dict["preferred_foods"]:
        profile_dict["food_preferences"] = profile_dict["preferred_foods"]
    
    # Calcula BMR
    bmr = calculate_bmr(
        weight=profile_data.weight,
        height=profile_data.height,
        age=profile_data.age,
        sex=profile_data.sex
    )
    
    # Calcula TDEE (INCLUI CARDIO PLANEJADO!)
    tdee = calculate_tdee(
        bmr=bmr,
        training_frequency=profile_data.weekly_training_frequency,
        training_level=profile_data.training_level,
        goal=profile_data.goal  # NOVO: passa goal para calcular cardio
    )
    
    # 🎯 PASSO 2: Ajusta TDEE baseado no objetivo (superávit/déficit)
    target_calories = calculate_target_calories(
        tdee=tdee,
        goal=profile_data.goal,
        weight=profile_data.weight
    )
    
    # 🎯 PASSO 3: Distribui macros a partir das calorias ajustadas
    macros = calculate_macros(
        target_calories=target_calories,
        weight=profile_data.weight,
        goal=profile_data.goal
    )
    
    # Adiciona campos calculados
    profile_dict["tdee"] = round(tdee, 0)  # TDEE base
    profile_dict["target_calories"] = round(target_calories, 0)  # TDEE + superávit/déficit
    profile_dict["macros"] = macros
    profile_dict["updated_at"] = datetime.utcnow()
    
    # UPSERT: Atualiza se existe, cria se não existe (IDEMPOTENT)
    profile_dict["_id"] = profile_data.id
    
    await db.user_profiles.update_one(
        {"_id": profile_data.id},
        {"$set": profile_dict, "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True
    )
    
    # ✅ SALVA meal_count nas user_settings também (mínimo 4 refeições)
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
    Se o objetivo mudar, regenera a dieta automaticamente.
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
    
    goal_changed = False
    old_goal = existing_profile.get("goal")
    
    if update_dict:
        current_profile = UserProfile(**existing_profile)
        new_goal = update_dict.get("goal", current_profile.goal)
        new_level = update_dict.get("training_level", current_profile.training_level)
        new_frequency = update_dict.get("weekly_training_frequency", current_profile.weekly_training_frequency)
        new_weight = update_dict.get("weight", current_profile.weight)
        
        # Detectar se o objetivo mudou
        if "goal" in update_dict and old_goal != new_goal:
            goal_changed = True
            logger.info(f"Goal changed for user {user_id}: {old_goal} -> {new_goal}")
        
        # Se peso, goal, level ou frequência mudou, recalcula macros
        if any(key in update_dict for key in ["weight", "goal", "training_level", "weekly_training_frequency"]):
            # Recalcula
            bmr = calculate_bmr(
                weight=new_weight,
                height=current_profile.height,
                age=current_profile.age,
                sex=current_profile.sex
            )
            tdee = calculate_tdee(bmr, new_frequency, new_level, new_goal)  # INCLUI CARDIO!
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
    
    # Se objetivo mudou, regenera a dieta automaticamente
    if goal_changed:
        try:
            logger.info(f"Regenerating diet for user {user_id} due to goal change")
            # Busca perfil atualizado para gerar nova dieta
            updated_profile_data = await db.user_profiles.find_one({"_id": user_id})
            if updated_profile_data:
                # Usar DietAIService (mesmo que o endpoint oficial)
                from diet_service import DietAIService
                
                # Busca meal_count das settings ou usa o do perfil
                user_settings = await db.user_settings.find_one({"user_id": user_id})
                meal_count = 6  # Padrão
                meal_times = None
                
                if user_settings and user_settings.get('meal_count') in [4, 5, 6]:
                    meal_count = user_settings.get('meal_count')
                    meal_times = user_settings.get('meal_times', None)
                elif updated_profile_data.get('meal_count') and updated_profile_data.get('meal_count') in [4, 5, 6]:
                    meal_count = updated_profile_data.get('meal_count')
                
                # Gera nova dieta usando DietAIService (mesmo fluxo do endpoint /api/diet/generate)
                diet_service = DietAIService()
                diet_plan = diet_service.generate_diet_plan(
                    user_profile=dict(updated_profile_data),
                    target_calories=updated_profile_data.get('target_calories', 2000),
                    target_macros=updated_profile_data.get('macros', {"protein": 150, "carbs": 200, "fat": 60}),
                    meal_count=meal_count,
                    meal_times=meal_times
                )
                
                # Calcula totais reais dos alimentos
                computed_protein = sum(sum(f["protein"] for f in m.foods) for m in diet_plan.meals)
                computed_carbs = sum(sum(f["carbs"] for f in m.foods) for m in diet_plan.meals)
                computed_fat = sum(sum(f["fat"] for f in m.foods) for m in diet_plan.meals)
                computed_calories = sum(sum(f["calories"] for f in m.foods) for m in diet_plan.meals)
                
                # Converte para formato de dicionário para salvar no MongoDB
                meals_data = []
                for meal in diet_plan.meals:
                    meal_dict = {
                        "id": str(uuid.uuid4()),
                        "name": meal.name,
                        "time": meal.time,
                        "foods": [dict(f) if hasattr(f, '__dict__') else f for f in meal.foods],
                        "total_calories": meal.total_calories,
                        "macros": meal.macros
                    }
                    meals_data.append(meal_dict)
                
                # Salva nova dieta
                diet_id = str(uuid.uuid4())
                diet_doc = {
                    "_id": diet_id,
                    "id": diet_id,
                    "user_id": user_id,
                    "diet_type": "training",
                    "target_calories": updated_profile_data.get('target_calories', 2000),
                    "target_macros": updated_profile_data.get('macros', {"protein": 150, "carbs": 200, "fat": 60}),
                    "computed_calories": computed_calories,
                    "computed_protein": computed_protein,
                    "computed_carbs": computed_carbs,
                    "computed_fat": computed_fat,
                    "meals": meals_data,
                    "version": 14,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Remove dieta antiga e salva nova
                await db.diet_plans.delete_many({"user_id": user_id})
                await db.diet_plans.insert_one(diet_doc)
                
                target_cal = updated_profile_data.get('target_calories', 2000)
                logger.info(f"DIETA REGENERADA - User: {user_id} | Goal: {updated_profile_data.get('goal')} | Target: {target_cal} | Computed: {computed_calories}")
        except Exception as e:
            logger.error(f"Error regenerating diet for user {user_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Não falha o endpoint, apenas loga o erro
    
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


class DeleteAccountRequest(BaseModel):
    user_id: str
    password: str


@api_router.delete("/auth/delete-account")
async def delete_account(request: DeleteAccountRequest):
    """
    Exclui permanentemente a conta do usuário e todos os seus dados.
    Requer confirmação com a senha da conta.
    
    Dados excluídos:
    - users_auth (credenciais)
    - user_profiles (perfil)
    - user_settings (configurações)
    - diet_plans (dietas)
    - workouts (treinos)
    - training_cycles (ciclos de treino)
    - weight_history (histórico de peso)
    - cardio_sessions (sessões de cardio)
    """
    import hashlib
    
    user_id = request.user_id
    password = request.password
    
    try:
        # 1. Buscar usuário auth
        user_auth = await db.users_auth.find_one({"_id": user_id})
        if not user_auth:
            # Tentar buscar por id também
            user_auth = await db.users_auth.find_one({"id": user_id})
        
        if not user_auth:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # 2. Verificar senha
        salt = user_auth.get("salt", "")
        stored_hash = user_auth.get("password_hash", "")
        input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        if input_hash != stored_hash:
            raise HTTPException(status_code=401, detail="Senha incorreta")
        
        # 3. Excluir todos os dados do usuário
        logger.info(f"🗑️ Iniciando exclusão de conta: {user_id}")
        
        # Excluir dados em todas as coleções
        collections_to_clean = [
            "users_auth",
            "user_profiles", 
            "user_settings",
            "diet_plans",
            "diets",
            "workouts",
            "training_cycles",
            "weight_history",
            "cardio_sessions",
            "progress_photos",
            "meal_logs",
        ]
        
        deleted_counts = {}
        for collection_name in collections_to_clean:
            try:
                collection = db[collection_name]
                # Tentar deletar por _id e user_id
                result1 = await collection.delete_many({"_id": user_id})
                result2 = await collection.delete_many({"user_id": user_id})
                result3 = await collection.delete_many({"id": user_id})
                total = result1.deleted_count + result2.deleted_count + result3.deleted_count
                if total > 0:
                    deleted_counts[collection_name] = total
            except Exception as e:
                logger.warning(f"Erro ao limpar {collection_name}: {e}")
        
        logger.info(f"✅ Conta excluída com sucesso: {user_id}")
        logger.info(f"   Dados removidos: {deleted_counts}")
        
        return {
            "success": True,
            "message": "Conta excluída com sucesso",
            "deleted_data": deleted_counts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir conta {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao excluir conta")

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
        
        # PRIORIDADE 1: User Settings (mais recente) - mínimo 4 refeições
        if user_settings and user_settings.get('meal_count') in [4, 5, 6]:
            meal_count = user_settings.get('meal_count')
            meal_times = user_settings.get('meal_times', None)
        # PRIORIDADE 2: User Profile (fallback)
        elif user_profile.get('meal_count') and user_profile.get('meal_count') in [4, 5, 6]:
            meal_count = user_profile.get('meal_count')
        
        # Valida meal_count (mínimo 4)
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
    Busca o plano de dieta mais recente do usuário.
    
    🎯 AJUSTE DINÂMICO POR DIA:
    - Dia de Treino: quantidades originais (+5% cal, +15% carbs)
    - Dia de Descanso: quantidades reduzidas (-5% cal, -20% carbs)
    
    Apenas as QUANTIDADES mudam, não os alimentos!
    """
    diet_plan = await db.diet_plans.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if not diet_plan:
        raise HTTPException(status_code=404, detail="Plano de dieta não encontrado")
    
    diet_plan["id"] = diet_plan["_id"]
    
    # Busca perfil do usuário
    user_profile = await db.user_profiles.find_one({"_id": user_id})
    
    # 🎯 DETERMINA TIPO DE DIA (treino ou descanso)
    training_days = user_profile.get("training_days", []) if user_profile else []
    today_weekday = datetime.now().weekday()
    is_training_day = today_weekday in training_days
    
    # 🎯 MULTIPLICADORES BASEADOS NO TIPO DE DIA
    if is_training_day:
        calorie_mult = 1.05  # +5% calorias
        carb_mult = 1.15     # +15% carboidratos
        diet_type = "training"
    else:
        calorie_mult = 0.95  # -5% calorias
        carb_mult = 0.80     # -20% carboidratos
        diet_type = "rest"
    
    # 🎯 AJUSTA QUANTIDADES DOS ALIMENTOS
    adjusted_meals = []
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for meal in diet_plan.get("meals", []):
        adjusted_foods = []
        meal_calories = 0
        meal_protein = 0
        meal_carbs = 0
        meal_fat = 0
        
        for food in meal.get("foods", []):
            # Copia o alimento
            adjusted_food = dict(food)
            
            # Identifica se é carboidrato (arroz, batata, macarrão, etc)
            food_key = food.get("key", food.get("name", "")).lower()
            is_carb_food = any(carb in food_key for carb in [
                "arroz", "rice", "batata", "potato", "macarr", "pasta", 
                "aveia", "oat", "pao", "bread", "tapioca", "cuscuz", 
                "quinoa", "feijao", "bean", "milho", "corn"
            ])
            
            # Ajusta quantidade baseado no tipo de alimento
            original_grams = food.get("grams", 100)
            
            if is_carb_food:
                # Carboidratos: ajuste maior
                # 🔒 IMPORTANTE: Sempre arredondar para múltiplo de 10!
                adjusted_grams = round(original_grams * carb_mult / 10) * 10
                
                # Recalcula macros proporcionalmente
                ratio = adjusted_grams / original_grams if original_grams > 0 else 1
                adjusted_food["grams"] = adjusted_grams
                adjusted_food["calories"] = round(food.get("calories", 0) * ratio)
                adjusted_food["protein"] = round(food.get("protein", 0) * ratio, 1)
                adjusted_food["carbs"] = round(food.get("carbs", 0) * ratio, 1)
                adjusted_food["fat"] = round(food.get("fat", 0) * ratio, 1)
            else:
                # Outros alimentos: mantém igual
                adjusted_food["grams"] = original_grams
            
            adjusted_foods.append(adjusted_food)
            
            # Soma macros da refeição
            meal_calories += adjusted_food.get("calories", 0)
            meal_protein += adjusted_food.get("protein", 0)
            meal_carbs += adjusted_food.get("carbs", 0)
            meal_fat += adjusted_food.get("fat", 0)
        
        # Monta refeição ajustada
        adjusted_meal = dict(meal)
        adjusted_meal["foods"] = adjusted_foods
        adjusted_meal["calories"] = round(meal_calories)
        adjusted_meal["total_calories"] = round(meal_calories)
        adjusted_meal["protein"] = round(meal_protein, 1)
        adjusted_meal["carbs"] = round(meal_carbs, 1)
        adjusted_meal["fat"] = round(meal_fat, 1)
        adjusted_meals.append(adjusted_meal)
        
        # Soma totais
        total_calories += meal_calories
        total_protein += meal_protein
        total_carbs += meal_carbs
        total_fat += meal_fat
    
    # Atualiza dieta com valores ajustados
    diet_plan["meals"] = adjusted_meals
    diet_plan["computed_calories"] = round(total_calories)
    diet_plan["computed_protein"] = round(total_protein, 1)
    diet_plan["computed_carbs"] = round(total_carbs, 1)
    diet_plan["computed_fat"] = round(total_fat, 1)
    
    # Adiciona info do tipo de dia
    diet_plan["diet_type"] = diet_type
    diet_plan["is_training_day"] = is_training_day
    diet_plan["adjustments"] = {
        "type": diet_type,
        "calorie_multiplier": calorie_mult,
        "carb_multiplier": carb_mult,
        "info": "Dia de Treino: +5% cal, +15% carbs" if is_training_day else "Dia de Descanso: -5% cal, -20% carbs"
    }
    
    # Traduz baseado no idioma do perfil do usuário
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
    suggest_goal_change = False
    suggested_goal = None
    suggest_reason = None
    
    if last_record:
        previous_weight = last_record.get("weight", record.weight)
        current_weight = record.weight
        goal = user.get("goal", "manutencao")
        
        # Busca calorias atuais da dieta
        current_diet = await db.diet_plans.find_one({"user_id": user_id})
        current_diet_calories = current_diet.get("computed_calories", 0) if current_diet else 0
        
        # Calcula o TDEE do usuário
        user_tdee = calculate_tdee(
            weight=user.get("weight", current_weight),
            height=user.get("height", 170),
            age=user.get("age", 25),
            sex=user.get("sex", "male"),
            activity_level=user.get("activity_level", "moderado")
        )
        
        # Avalia progresso com TDEE
        progress_eval = evaluate_progress(
            goal=goal,
            previous_weight=previous_weight,
            current_weight=current_weight,
            current_diet_calories=current_diet_calories,
            user_tdee=user_tdee
        )
        
        logger.info(f"Progress evaluation for {user_id}: {progress_eval}")
        
        # Verifica sugestão de mudança de objetivo
        suggest_goal_change = progress_eval.get("suggest_goal_change", False)
        suggested_goal = progress_eval.get("suggested_goal")
        suggest_reason = progress_eval.get("suggest_reason")
        
        # Se precisa ajustar, atualiza a dieta
        if progress_eval.get("needs_adjustment"):
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
        "message": adjustment_message or "Peso registrado com sucesso",
        "suggest_goal_change": suggest_goal_change,
        "suggested_goal": suggested_goal,
        "suggest_reason": suggest_reason
    }


@api_router.post("/user/{user_id}/switch-goal/{new_goal}")
async def switch_goal(user_id: str, new_goal: str):
    """
    Muda o objetivo do usuário e regenera a dieta.
    new_goal pode ser: 'cutting', 'bulking', 'manutencao', 'manter'
    """
    from diet_service import generate_diet, calculate_tdee
    
    # Normaliza o objetivo
    valid_goals = ["cutting", "bulking", "manutencao", "manter"]
    if new_goal not in valid_goals:
        raise HTTPException(status_code=400, detail=f"Objetivo inválido. Use: {', '.join(valid_goals)}")
    
    # Normaliza 'manter' para 'manutencao'
    if new_goal == "manter":
        new_goal = "manutencao"
    
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    current_goal = user.get("goal", "manutencao")
    
    # Não precisa mudar se já está no mesmo objetivo
    if current_goal == new_goal:
        return {
            "success": True,
            "message": f"Você já está em {new_goal}!",
            "new_goal": new_goal
        }
    
    # Atualiza o objetivo
    await db.user_profiles.update_one(
        {"_id": user_id},
        {"$set": {"goal": new_goal, "updated_at": datetime.utcnow()}}
    )
    
    # Regenera a dieta para o novo objetivo
    try:
        # Calcula TDEE e macros para o novo objetivo
        weight = user.get("weight", 70)
        height = user.get("height", 170)
        age = user.get("age", 25)
        sex = user.get("sex", "masculino")
        activity_level = user.get("activity_level", "moderado")
        training_level = user.get("training_level", "intermediario")
        
        tdee = calculate_tdee(weight, height, age, sex, activity_level, training_level, new_goal)
        
        # Ajusta calorias baseado no objetivo
        if new_goal == "cutting":
            target_calories = tdee - 500
        elif new_goal == "bulking":
            target_calories = tdee + 400
        else:  # manutenção
            target_calories = tdee
        
        # Calcula macros
        protein = int(weight * 2.0)  # 2g/kg
        fat = int(weight * 1.0)  # 1g/kg
        remaining_cals = target_calories - (protein * 4) - (fat * 9)
        carbs = max(100, int(remaining_cals / 4))
        
        # Gera dieta
        user_foods_set = set(user.get("food_preferences", []))
        meals_list = generate_diet(
            target_p=protein,
            target_c=carbs,
            target_f=fat,
            preferred=user_foods_set,
            restrictions=user.get("dietary_restrictions", []),
            meal_count=user.get("meal_count", 4),
            goal=new_goal
        )
        
        # Calcula totais (soma direta dos alimentos já que generate_diet não retorna total_calories)
        total_cals = 0
        total_p = 0
        total_c = 0
        total_f = 0
        
        for meal in meals_list:
            meal_cals = 0
            meal_p = 0
            meal_c = 0
            meal_f = 0
            
            for food in meal.get("foods", []):
                meal_cals += food.get("calories", 0)
                meal_p += food.get("protein", 0)
                meal_c += food.get("carbs", 0)
                meal_f += food.get("fat", 0)
            
            # Adiciona total_calories à refeição
            meal["total_calories"] = int(meal_cals)
            meal["macros"] = {"protein": int(meal_p), "carbs": int(meal_c), "fat": int(meal_f)}
            
            total_cals += meal_cals
            total_p += meal_p
            total_c += meal_c
            total_f += meal_f
        
        # Monta estrutura da dieta
        new_diet = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "meals": meals_list,
            "target_calories": target_calories,
            "target_macros": {"protein": protein, "carbs": carbs, "fat": fat},
            "computed_calories": total_cals,
            "computed_macros": {"protein": int(total_p), "carbs": int(total_c), "fat": int(total_f)},
            "goal_changed_at": datetime.utcnow(),
            "previous_goal": current_goal,
            "created_at": datetime.utcnow()
        }
        new_diet["_id"] = new_diet["id"]
        
        # Remove dieta antiga e insere nova
        await db.diet_plans.delete_many({"user_id": user_id})
        await db.diet_plans.insert_one(new_diet)
        
        goal_names = {"cutting": "Cutting", "bulking": "Bulking", "manutencao": "Manutenção"}
        logger.info(f"User {user_id} switched from {current_goal} to {new_goal}. New diet generated.")
        
        return {
            "success": True,
            "message": f"Objetivo alterado para {goal_names.get(new_goal, new_goal)}! Nova dieta gerada.",
            "new_goal": new_goal,
            "previous_goal": current_goal,
            "new_calories": new_diet.get("computed_calories"),
            "new_macros": new_diet.get("computed_macros")
        }
    except Exception as e:
        logger.error(f"Error generating diet for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar nova dieta: {str(e)}")


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
    suggest_goal_change = False
    suggested_goal = None
    suggest_reason = None
    
    current_diet = await db.diet_plans.find_one({"user_id": user_id})
    
    if current_diet and last_record:
        previous_weight = last_record.get("weight", checkin.weight)
        current_weight = checkin.weight
        goal = user.get("goal", "manutencao")
        
        # Calcula TDEE do usuário
        user_tdee = calculate_tdee(
            weight=user.get("weight", current_weight),
            height=user.get("height", 170),
            age=user.get("age", 25),
            sex=user.get("sex", "male"),
            activity_level=user.get("activity_level", "moderado")
        )
        
        # Avalia progresso com TDEE
        progress_eval = evaluate_progress(
            goal=goal,
            previous_weight=previous_weight,
            current_weight=current_weight,
            current_diet_calories=current_diet.get("computed_calories", 0),
            user_tdee=user_tdee
        )
        
        # Guarda sugestão de mudança de objetivo
        suggest_goal_change = progress_eval.get("suggest_goal_change", False)
        suggested_goal = progress_eval.get("suggested_goal")
        suggest_reason = progress_eval.get("suggest_reason")
        
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
        "diet_adjusted": not diet_kept,
        "calories_change": calories_change,
        "foods_replaced": foods_replaced,
        "suggest_goal_change": suggest_goal_change,
        "suggested_goal": suggested_goal,
        "suggest_reason": suggest_reason,
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


# ==================== WORKOUT TRACKING ENDPOINTS ====================

def get_today_date() -> str:
    """Retorna a data de hoje no formato YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")

def calculate_adjusted_macros(base_calories: float, base_protein: float, base_carbs: float, base_fat: float, is_training_day: bool) -> Dict:
    """
    Calcula macros ajustados baseado no tipo de dia.
    
    REGRAS:
    - Proteína e Gordura NÃO mudam
    - Apenas Carboidratos e Calorias são ajustados
    
    Dia de treino:
    - calorias = baseCalories * 1.05
    - carboidratos = baseCarbs * 1.15
    
    Dia sem treino:
    - calorias = baseCalories * 0.95
    - carboidratos = baseCarbs * 0.80
    """
    if is_training_day:
        calorie_multiplier = 1.05
        carb_multiplier = 1.15
        diet_type = "training"
        multiplier_info = "+5% calorias, +15% carbs"
    else:
        calorie_multiplier = 0.95
        carb_multiplier = 0.80
        diet_type = "rest"
        multiplier_info = "-5% calorias, -20% carbs"
    
    adjusted_calories = base_calories * calorie_multiplier
    adjusted_carbs = base_carbs * carb_multiplier
    
    return {
        "base_calories": round(base_calories, 0),
        "adjusted_calories": round(adjusted_calories, 0),
        "base_protein": round(base_protein, 1),
        "adjusted_protein": round(base_protein, 1),  # Não muda
        "base_carbs": round(base_carbs, 1),
        "adjusted_carbs": round(adjusted_carbs, 1),
        "base_fat": round(base_fat, 1),
        "adjusted_fat": round(base_fat, 1),  # Não muda
        "diet_type": diet_type,
        "is_training_day": is_training_day,
        "calorie_multiplier": calorie_multiplier,
        "carb_multiplier": carb_multiplier,
        "multiplier_info": multiplier_info
    }

# ==================== WORKOUT CYCLE SYSTEM ====================

def get_day_type_from_training_days(training_days: List[int], check_date_str: str = None) -> Dict:
    """
    🎯 NOVA LÓGICA: Calcula se é dia de TREINO ou DESCANSO baseado nos dias selecionados pelo usuário.
    
    REGRA SIMPLES:
    - Se o dia da semana atual está em training_days → "train"
    - Senão → "rest"
    
    Args:
        training_days: Lista de dias da semana (0=Domingo, 1=Segunda, ..., 6=Sábado)
        check_date_str: Data para verificar (YYYY-MM-DD) - default: hoje
    
    Returns:
        Dict com day_type ("train"/"rest"), weekday, etc.
    """
    from datetime import datetime
    
    # Parse da data
    check_date = datetime.strptime(check_date_str, "%Y-%m-%d").date() if check_date_str else datetime.now().date()
    
    # Pega o dia da semana (0=Segunda no Python, mas queremos 0=Domingo)
    # Python: weekday() retorna 0=Segunda ... 6=Domingo
    # Convertemos para 0=Domingo, 1=Segunda, ..., 6=Sábado
    python_weekday = check_date.weekday()  # 0=Segunda ... 6=Domingo
    weekday = (python_weekday + 1) % 7     # 0=Domingo, 1=Segunda ... 6=Sábado
    
    # Nomes dos dias
    day_names = {0: 'Domingo', 1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta', 6: 'Sábado'}
    
    # Verifica se é dia de treino
    is_training_day = weekday in training_days
    day_type = "train" if is_training_day else "rest"
    
    return {
        "day_type": day_type,
        "weekday": weekday,
        "weekday_name": day_names.get(weekday, ""),
        "training_days": training_days,
        "is_training_day": is_training_day,
        "reason": f"{day_names.get(weekday, '')} - {'dia de treino' if is_training_day else 'dia de descanso'}"
    }


def get_day_type_from_division(start_date_str: str, frequency: int, check_date_str: str = None) -> Dict:
    """
    🎯 Calcula automaticamente se é dia de TREINO ou DESCANSO baseado no ciclo semanal.
    NOTA: Esta função é usada como FALLBACK quando o usuário não tem training_days definidos.
    
    REGRAS:
    1. Dia 0 (startDate) = SEMPRE DESCANSO
    2. A partir do dia 1, começa o ciclo de treino
    3. Ciclo de 7 dias se repete
    
    Distribuição de dias de treino na semana:
    - 2x: dias 1, 4 (treino nos dias 2 e 5 do ciclo)
    - 3x: dias 1, 3, 5
    - 4x: dias 1, 2, 4, 5
    - 5x: dias 1, 2, 3, 4, 5
    - 6x: dias 1, 2, 3, 4, 5, 6
    
    Args:
        start_date_str: Data de início (YYYY-MM-DD) - primeiro dia do app
        frequency: Frequência semanal (2-6)
        check_date_str: Data para verificar (YYYY-MM-DD) - default: hoje
    
    Returns:
        Dict com day_type ("train"/"rest"), day_number, cycle_day, etc.
    """
    from datetime import datetime, timedelta
    
    # Parse das datas
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    check_date = datetime.strptime(check_date_str, "%Y-%m-%d").date() if check_date_str else datetime.now().date()
    
    # Calcula quantos dias se passaram desde o início
    days_elapsed = (check_date - start_date).days
    
    # Dia 0 = SEMPRE descanso
    if days_elapsed == 0:
        return {
            "day_type": "rest",
            "day_number": 0,
            "cycle_day": 0,
            "cycle_week": 0,
            "is_first_day": True,
            "reason": "Primeiro dia do app - descanso obrigatório"
        }
    
    # A partir do dia 1, calcula o ciclo de 7 dias
    # Ciclo começa no dia 1, então ciclo_dia vai de 1 a 7
    cycle_day = ((days_elapsed - 1) % 7) + 1  # 1-7
    cycle_week = (days_elapsed - 1) // 7 + 1
    
    # Mapeamento de dias de treino por frequência
    # O dia 7 (domingo) é SEMPRE descanso
    training_days_by_frequency = {
        2: [1, 4],           # Segunda, Quinta
        3: [1, 3, 5],        # Segunda, Quarta, Sexta
        4: [1, 2, 4, 5],     # Segunda, Terça, Quinta, Sexta
        5: [1, 2, 3, 4, 5],  # Segunda a Sexta
        6: [1, 2, 3, 4, 5, 6],  # Segunda a Sábado
    }
    
    # Pega os dias de treino para a frequência (default: 4x)
    training_days = training_days_by_frequency.get(frequency, [1, 2, 4, 5])
    
    # Verifica se o dia do ciclo é dia de treino
    is_training_day = cycle_day in training_days
    day_type = "train" if is_training_day else "rest"
    
    return {
        "day_type": day_type,
        "day_number": days_elapsed,
        "cycle_day": cycle_day,
        "cycle_week": cycle_week,
        "is_first_day": False,
        "training_days_in_cycle": training_days,
        "reason": f"Ciclo dia {cycle_day} - {'treino' if is_training_day else 'descanso'}"
    }


class TrainingCycleSetup(BaseModel):
    """Setup inicial do ciclo de treino"""
    frequency: int = Field(ge=2, le=6, description="Frequência semanal (2-6)")


class TrainingSessionStart(BaseModel):
    """Request para iniciar sessão de treino"""
    workout_day_index: Optional[int] = None  # Índice do dia de treino (opcional)


class TrainingSessionFinish(BaseModel):
    """Request para finalizar sessão de treino"""
    duration_seconds: int = Field(ge=0, description="Duração do treino em segundos")
    exercises_completed: Optional[int] = None


@api_router.post("/training-cycle/setup/{user_id}")
async def setup_training_cycle(user_id: str, setup: TrainingCycleSetup):
    """
    🎯 Configura o ciclo de treino do usuário.
    
    - Salva a data de início (startDate)
    - Salva a frequência semanal
    - Primeiro dia = DESCANSO
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    today = get_today_date()
    
    # Salva configuração do ciclo
    cycle_config = {
        "user_id": user_id,
        "start_date": today,
        "frequency": setup.frequency,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Upsert no banco
    await db.training_cycles.update_one(
        {"user_id": user_id},
        {"$set": cycle_config},
        upsert=True
    )
    
    # Também atualiza a frequência no perfil
    await db.user_profiles.update_one(
        {"_id": user_id},
        {"$set": {"weekly_training_frequency": setup.frequency}}
    )
    
    # Calcula o status do primeiro dia
    day_status = get_day_type_from_division(today, setup.frequency, today)
    
    logger.info(f"Training cycle setup for user {user_id}: {setup.frequency}x/week, start_date={today}")
    
    return {
        "success": True,
        "message": "Ciclo de treino configurado com sucesso",
        "start_date": today,
        "frequency": setup.frequency,
        "first_day_type": day_status["day_type"],
        "day_status": day_status
    }


@api_router.get("/training-cycle/status/{user_id}")
async def get_training_cycle_status(user_id: str, date: str = None):
    """
    🎯 Retorna o status completo do ciclo de treino.
    
    Inclui:
    - Tipo do dia (train/rest)
    - Informações do ciclo
    - Status da sessão de treino do dia
    - Multiplicadores de dieta
    """
    # Verifica se usuário existe (busca por id ou _id)
    user = await db.user_profiles.find_one({"id": user_id})
    if not user:
        user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    check_date = date or get_today_date()
    
    # Busca configuração do ciclo
    cycle_config = await db.training_cycles.find_one({"user_id": user_id})
    
    # Pega training_days do perfil do usuário (se existir)
    training_days = user.get("training_days", [])
    
    if not cycle_config:
        # Se não tem ciclo configurado, usa a frequência do perfil e hoje como início
        frequency = user.get("weekly_training_frequency", 4)
        start_date = get_today_date()
        
        # Auto-cria o ciclo
        await db.training_cycles.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "start_date": start_date,
                "frequency": frequency,
                "created_at": datetime.utcnow()
            }},
            upsert=True
        )
        cycle_config = {"start_date": start_date, "frequency": frequency}
    
    start_date = cycle_config.get("start_date", get_today_date())
    frequency = cycle_config.get("frequency", user.get("weekly_training_frequency", 4))
    
    # 🎯 NOVA LÓGICA: Usa training_days do perfil se disponível
    if training_days and len(training_days) > 0:
        # Usa os dias selecionados pelo usuário
        from datetime import datetime as dt
        check_dt = dt.strptime(check_date, "%Y-%m-%d").date()
        # Python weekday: 0=Monday ... 6=Sunday
        # Nosso formato: 0=Sunday, 1=Monday ... 6=Saturday
        python_weekday = check_dt.weekday()
        today_weekday = (python_weekday + 1) % 7  # Converte para nosso formato
        
        is_training_day = today_weekday in training_days
        day_names = {0: 'Domingo', 1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta', 5: 'Sexta', 6: 'Sábado'}
        
        # ==================== LÓGICA DE TREINO DO DIA ====================
        # Determina qual treino mostrar baseado na divisão e posição na semana
        training_split = user.get("training_split", "full_body")
        today_workout_name = None
        today_workout_index = 0
        
        if is_training_day:
            # Ordena os training_days para saber a posição do dia atual
            sorted_training_days = sorted(training_days)
            day_position = sorted_training_days.index(today_weekday)  # 0, 1, 2, ...
            
            if frequency == 6 or training_split == "ppl":
                # PPL: Push, Pull, Legs, Push, Pull, Legs
                ppl_sequence = ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]
                today_workout_index = day_position % len(ppl_sequence)
                today_workout_name = ppl_sequence[today_workout_index]
            else:
                # Full Body ou outras divisões
                today_workout_index = day_position
                today_workout_name = "Full Body"
        
        day_status = {
            "day_type": "train" if is_training_day else "rest",
            "weekday": today_weekday,
            "weekday_name": day_names.get(today_weekday, ""),
            "training_days": training_days,
            "training_split": training_split,
            "today_workout_name": today_workout_name,
            "today_workout_index": today_workout_index,
            "reason": f"{day_names.get(today_weekday, '')} - {'dia de treino' if is_training_day else 'dia de descanso'}"
        }
    else:
        # Fallback para o sistema antigo baseado em ciclo
        day_status = get_day_type_from_division(start_date, frequency, check_date)
    
    # Busca sessão de treino do dia
    training_session = await db.training_sessions.find_one({
        "user_id": user_id,
        "date": check_date
    })
    
    # Verifica se já treinou hoje
    has_trained_today = training_session is not None and training_session.get("completed", False)
    is_training_in_progress = training_session is not None and training_session.get("started", False) and not training_session.get("completed", False)
    
    # ==================== LÓGICA DE DIETA ====================
    # 🎯 REGRA: A dieta é definida pelo TIPO DO DIA PLANEJADO
    # A dieta NUNCA depende de ações do usuário - é automática baseada no plano
    #
    # 1. Se plannedDayType = "train":
    #    → Dieta de TREINO desde o início do dia
    #
    # 2. Se plannedDayType = "rest":
    #    → Dieta de DESCANSO (sem exceções, sem treino bônus)
    
    planned_day_type = day_status["day_type"]  # "train" ou "rest"
    
    if planned_day_type == "train":
        # Dia planejado como TREINO → dieta de treino SEMPRE
        diet_type = "training"
        calorie_multiplier = 1.05
        carb_multiplier = 1.15
        diet_reason = "Dia de treino planejado"
    else:
        # Dia planejado como DESCANSO → dieta de descanso SEMPRE
        # NÃO existe mais treino bônus - treino bloqueado em dias de descanso
        diet_type = "rest"
        calorie_multiplier = 0.95
        carb_multiplier = 0.80
        diet_reason = "Dia de descanso"
    
    # Status do treino
    # - train + não treinou → pending
    # - train + treinou → completed
    # - rest → rest (treino bloqueado)
    if planned_day_type == "train":
        if has_trained_today:
            workout_status = "completed"
            workout_status_text = "Treino realizado ✅"
        elif is_training_in_progress:
            workout_status = "in_progress"
            workout_status_text = "Treino em andamento"
        else:
            workout_status = "pending"
            workout_status_text = "Treino pendente"
    else:
        # Dia de descanso - treino BLOQUEADO
        workout_status = "rest"
        workout_status_text = "Dia de descanso - treino bloqueado"
    
    # Flag para indicar se treino está bloqueado
    is_training_blocked = planned_day_type == "rest"
    
    return {
        "date": check_date,
        "day_type": day_status["day_type"],
        "planned_day_type": planned_day_type,
        "day_number": day_status.get("day_number", 0),
        "cycle_day": day_status.get("cycle_day", day_status.get("weekday", 0)),
        "cycle_week": day_status.get("cycle_week", 1),
        "is_first_day": day_status.get("is_first_day", False),
        "reason": day_status.get("reason", ""),
        "weekday": day_status.get("weekday"),
        "weekday_name": day_status.get("weekday_name"),
        "training_days": training_days,
        "training_split": day_status.get("training_split"),
        "today_workout_name": day_status.get("today_workout_name"),
        "today_workout_index": day_status.get("today_workout_index", 0),
        "frequency": frequency,
        "start_date": start_date,
        "has_trained_today": has_trained_today,
        "is_training_in_progress": is_training_in_progress,
        "is_training_blocked": is_training_blocked,
        "workout_status": workout_status,
        "workout_status_text": workout_status_text,
        "training_session": {
            "started_at": training_session.get("started_at") if training_session else None,
            "completed_at": training_session.get("completed_at") if training_session else None,
            "duration_seconds": training_session.get("duration_seconds") if training_session else None,
        } if training_session else None,
        "diet": {
            "type": diet_type,
            "calorie_multiplier": calorie_multiplier,
            "carb_multiplier": carb_multiplier,
            "reason": diet_reason,
            "info": "+5% cal, +15% carbs" if diet_type == "training" else "-5% cal, -20% carbs"
        }
    }


@api_router.post("/training-cycle/start-session/{user_id}")
async def start_training_session(user_id: str, request: TrainingSessionStart = None):
    """
    🎯 Inicia uma sessão de treino.
    
    - Registra o horário de início
    - Não permite iniciar duas vezes no mesmo dia
    - BLOQUEIA treino em dias de descanso
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    today = get_today_date()
    
    # 🚫 VERIFICA SE É DIA DE DESCANSO - BLOQUEIA TREINO
    training_days = user.get("training_days", [])
    if training_days:
        from datetime import datetime as dt
        check_dt = dt.strptime(today, "%Y-%m-%d").date()
        python_weekday = check_dt.weekday()
        today_weekday = (python_weekday + 1) % 7  # 0=Domingo, 1=Segunda, ...
        
        if today_weekday not in training_days:
            raise HTTPException(
                status_code=403, 
                detail="Hoje é dia de descanso. Treino não permitido. Descanse para recuperação muscular!"
            )
    
    # Verifica se já existe sessão do dia
    existing_session = await db.training_sessions.find_one({
        "user_id": user_id,
        "date": today
    })
    
    if existing_session:
        if existing_session.get("completed", False):
            raise HTTPException(status_code=400, detail="Treino já foi concluído hoje. Tente novamente amanhã.")
        if existing_session.get("started", False):
            # Já iniciou, retorna o existente
            return {
                "success": True,
                "message": "Treino já em andamento",
                "session": {
                    "started_at": existing_session.get("started_at"),
                    "date": today,
                    "already_started": True
                }
            }
    
    # Cria nova sessão
    now = datetime.utcnow()
    session = {
        "user_id": user_id,
        "date": today,
        "started": True,
        "completed": False,
        "started_at": now.isoformat(),
        "completed_at": None,
        "duration_seconds": None,
        "workout_day_index": request.workout_day_index if request else None,
        "created_at": now
    }
    
    await db.training_sessions.update_one(
        {"user_id": user_id, "date": today},
        {"$set": session},
        upsert=True
    )
    
    logger.info(f"Training session started for user {user_id}")
    
    return {
        "success": True,
        "message": "Treino iniciado com sucesso!",
        "session": {
            "started_at": now.isoformat(),
            "date": today,
            "already_started": False
        }
    }


@api_router.post("/training-cycle/finish-session/{user_id}")
async def finish_training_session(user_id: str, request: TrainingSessionFinish):
    """
    🎯 Finaliza uma sessão de treino.
    
    - Registra o horário de término
    - Salva a duração
    - Atualiza o status do treino para concluído
    - Salva no histórico de treinos
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    today = get_today_date()
    
    # Busca sessão existente
    existing_session = await db.training_sessions.find_one({
        "user_id": user_id,
        "date": today
    })
    
    if not existing_session:
        raise HTTPException(status_code=400, detail="Nenhuma sessão de treino iniciada hoje")
    
    if existing_session.get("completed", False):
        raise HTTPException(status_code=400, detail="Treino já foi concluído hoje")
    
    # Finaliza a sessão
    now = datetime.utcnow()
    
    await db.training_sessions.update_one(
        {"user_id": user_id, "date": today},
        {"$set": {
            "completed": True,
            "completed_at": now.isoformat(),
            "duration_seconds": request.duration_seconds,
            "exercises_completed": request.exercises_completed
        }}
    )
    
    # Também atualiza o workout_tracking antigo para compatibilidade
    await db.workout_tracking.update_one(
        {"user_id": user_id, "date": today},
        {"$set": {
            "user_id": user_id,
            "date": today,
            "trained": True,
            "completed_at": now.isoformat(),
            "duration_seconds": request.duration_seconds
        }},
        upsert=True
    )
    
    # Busca o nome do treino do plano atual
    workout_plan = await db.workout_plans.find_one({"user_id": user_id})
    workout_day_name = "Treino"
    total_exercises = request.exercises_completed
    
    if workout_plan and workout_plan.get("workout_days"):
        # Determina qual dia do treino é hoje baseado no ciclo
        training_days = user.get("training_days", [])
        today_weekday = datetime.now().weekday()
        
        if training_days and today_weekday in training_days:
            day_index = training_days.index(today_weekday)
            workout_days = workout_plan.get("workout_days", [])
            if day_index < len(workout_days):
                workout_day = workout_days[day_index]
                workout_day_name = workout_day.get("name", f"Dia {day_index + 1}")
                total_exercises = len(workout_day.get("exercises", []))
    
    # Salva no histórico de treinos
    history_entry = {
        "_id": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "workout_day_name": workout_day_name,
        "exercises_completed": request.exercises_completed,
        "total_exercises": total_exercises,
        "duration_minutes": request.duration_seconds // 60,
        "notes": None,
        "completed_at": now
    }
    
    await db.workout_history.insert_one(history_entry)
    
    # Formata duração
    duration_mins = request.duration_seconds // 60
    duration_secs = request.duration_seconds % 60
    duration_formatted = f"{duration_mins}:{duration_secs:02d}"
    
    # Determina o próximo treino
    next_workout = "Amanhã"
    try:
        # Busca configuração do ciclo para saber a frequência
        cycle_config = await db.training_cycles.find_one({"user_id": user_id})
        frequency = cycle_config.get("frequency", 4) if cycle_config else user.get("weekly_training_frequency", 4)
        
        # Calcula qual será o próximo dia de treino
        if workout_plan and workout_plan.get("workout_days"):
            workout_days = workout_plan.get("workout_days", [])
            # Encontra o índice do treino de hoje
            current_day_index = 0
            if training_days and today_weekday in training_days:
                current_day_index = training_days.index(today_weekday)
            
            # Próximo treino é o próximo na lista (circular)
            next_day_index = (current_day_index + 1) % len(workout_days)
            next_workout_day = workout_days[next_day_index]
            next_workout = next_workout_day.get("name", f"Treino {chr(65 + next_day_index)}")
    except Exception as e:
        logger.error(f"Error calculating next workout: {e}")
        next_workout = "Próximo treino"
    
    logger.info(f"Training session finished for user {user_id}: {duration_formatted} - Saved to history")
    
    return {
        "success": True,
        "message": f"Treino concluído! Duração: {duration_formatted}",
        "next_workout": next_workout,
        "session": {
            "date": today,
            "started_at": existing_session.get("started_at"),
            "completed_at": now.isoformat(),
            "duration_seconds": request.duration_seconds,
            "duration_formatted": duration_formatted,
            "exercises_completed": request.exercises_completed
        }
    }


@api_router.get("/training-cycle/week-preview/{user_id}")
async def get_week_preview(user_id: str):
    """
    🎯 Retorna preview da semana com dias de treino e descanso.
    """
    # Busca configuração do ciclo
    cycle_config = await db.training_cycles.find_one({"user_id": user_id})
    user = await db.user_profiles.find_one({"_id": user_id})
    
    if not cycle_config:
        frequency = user.get("weekly_training_frequency", 4) if user else 4
        start_date = get_today_date()
    else:
        frequency = cycle_config.get("frequency", 4)
        start_date = cycle_config.get("start_date", get_today_date())
    
    # Gera preview dos próximos 7 dias
    today = datetime.now().date()
    week_preview = []
    
    day_names = {
        0: "Segunda", 1: "Terça", 2: "Quarta", 
        3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"
    }
    
    for i in range(7):
        check_date = today + timedelta(days=i)
        check_date_str = check_date.strftime("%Y-%m-%d")
        
        day_status = get_day_type_from_division(start_date, frequency, check_date_str)
        
        # Busca se já treinou nesse dia
        session = await db.training_sessions.find_one({
            "user_id": user_id,
            "date": check_date_str
        })
        
        week_preview.append({
            "date": check_date_str,
            "day_name": day_names.get(check_date.weekday(), ""),
            "day_type": day_status["day_type"],
            "cycle_day": day_status["cycle_day"],
            "is_today": i == 0,
            "has_trained": session.get("completed", False) if session else False
        })
    
    return {
        "frequency": frequency,
        "start_date": start_date,
        "week_preview": week_preview
    }


@api_router.get("/workout/status/{user_id}")
async def get_workout_status(user_id: str, date: str = None):
    """
    Retorna o status de treino do dia.
    
    Se date não for informado, usa a data de hoje.
    """
    if not date:
        date = get_today_date()
    
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca registro de treino do dia
    workout_record = await db.workout_tracking.find_one({
        "user_id": user_id,
        "date": date
    })
    
    trained = workout_record.get("trained", False) if workout_record else False
    completed_at = workout_record.get("completed_at") if workout_record else None
    
    # Verifica se é dia de treino baseado na frequência semanal do usuário
    weekly_frequency = user.get("weekly_training_frequency", 4)
    day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()  # 0=segunda, 6=domingo
    
    # Dias de treino padrão baseado na frequência
    # Ex: 4x/semana = seg, ter, qui, sex (0, 1, 3, 4)
    training_days_map = {
        1: [0],  # Segunda
        2: [0, 3],  # Segunda, Quinta
        3: [0, 2, 4],  # Segunda, Quarta, Sexta
        4: [0, 1, 3, 4],  # Segunda, Terça, Quinta, Sexta
        5: [0, 1, 2, 3, 4],  # Segunda a Sexta
        6: [0, 1, 2, 3, 4, 5],  # Segunda a Sábado
        7: [0, 1, 2, 3, 4, 5, 6],  # Todos os dias
    }
    
    scheduled_training_days = training_days_map.get(weekly_frequency, [0, 2, 4])
    is_scheduled_training_day = day_of_week in scheduled_training_days
    
    # Se já treinou, é dia de treino. Senão, usa o agendado.
    is_training_day = trained or is_scheduled_training_day
    
    # Determina o tipo de dieta
    if trained:
        diet_type = "training"
        calorie_multiplier = 1.05
        carb_multiplier = 1.15
    else:
        diet_type = "rest"
        calorie_multiplier = 0.95
        carb_multiplier = 0.80
    
    return {
        "date": date,
        "trained": trained,
        "completed_at": completed_at,
        "is_scheduled_training_day": is_scheduled_training_day,
        "is_training_day": is_training_day,
        "diet_type": diet_type,
        "calorie_multiplier": calorie_multiplier,
        "carb_multiplier": carb_multiplier,
        "weekly_frequency": weekly_frequency,
        "day_of_week": day_of_week
    }

@api_router.post("/workout/finish/{user_id}")
async def finish_workout(user_id: str, request: FinishWorkoutRequest = None):
    """
    Marca o treino do dia como concluído.
    
    - Salva no banco de dados
    - Impede marcar o mesmo dia duas vezes
    - Retorna o novo status
    """
    date = request.date if request and request.date else get_today_date()
    
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verifica se já foi marcado
    existing = await db.workout_tracking.find_one({
        "user_id": user_id,
        "date": date
    })
    
    if existing and existing.get("trained"):
        raise HTTPException(
            status_code=400, 
            detail="Treino já foi marcado como concluído para este dia"
        )
    
    # Marca como concluído
    completed_at = datetime.now().isoformat()
    
    await db.workout_tracking.update_one(
        {"user_id": user_id, "date": date},
        {
            "$set": {
                "user_id": user_id,
                "date": date,
                "trained": True,
                "completed_at": completed_at
            }
        },
        upsert=True
    )
    
    logging.info(f"Workout finished for user {user_id} on {date}")
    
    return {
        "success": True,
        "message": "Treino concluído com sucesso!",
        "date": date,
        "trained": True,
        "completed_at": completed_at,
        "diet_type": "training"
    }

@api_router.get("/workout/history/{user_id}")
async def get_workout_history(user_id: str, days: int = 30):
    """
    Retorna histórico de treinos dos últimos N dias.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Calcula data inicial
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Busca registros
    records = await db.workout_tracking.find({
        "user_id": user_id,
        "date": {"$gte": start_date}
    }).sort("date", -1).to_list(100)
    
    # Conta estatísticas
    trained_days = sum(1 for r in records if r.get("trained"))
    
    return {
        "user_id": user_id,
        "period_days": days,
        "total_workouts": trained_days,
        "history": [
            {
                "date": r["date"],
                "trained": r.get("trained", False),
                "completed_at": r.get("completed_at")
            }
            for r in records
        ]
    }

@api_router.get("/workout/adjusted-macros/{user_id}")
async def get_adjusted_macros(user_id: str, date: str = None):
    """
    Retorna os macros ajustados para o dia (treino ou descanso).
    
    - Busca a dieta base do usuário
    - Aplica os multiplicadores corretos
    - Retorna macros ajustados
    """
    if not date:
        date = get_today_date()
    
    # Busca perfil do usuário
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca dieta do usuário
    diet = await db.diet_plans.find_one({"user_id": user_id})
    if not diet:
        raise HTTPException(status_code=404, detail="Dieta não encontrada. Gere uma dieta primeiro.")
    
    # Pega status de treino
    workout_status = await get_workout_status(user_id, date)
    is_training_day = workout_status["trained"]
    
    # Pega macros base da dieta
    base_calories = diet.get("computed_calories", diet.get("target_calories", 2000))
    base_macros = diet.get("computed_macros", diet.get("target_macros", {}))
    base_protein = base_macros.get("protein", 150)
    base_carbs = base_macros.get("carbs", 300)
    base_fat = base_macros.get("fat", 60)
    
    # Calcula macros ajustados
    adjusted = calculate_adjusted_macros(
        base_calories, base_protein, base_carbs, base_fat, is_training_day
    )
    
    adjusted["date"] = date
    adjusted["trained"] = is_training_day
    
    return adjusted


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


@api_router.get("/cardio/history/{user_id}")
async def get_cardio_history(user_id: str):
    """
    Retorna o histórico de sessões de cardio do usuário.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca histórico de sessões
    sessions = await db.cardio_sessions.find(
        {"user_id": user_id}
    ).sort("completed_at", -1).to_list(100)
    
    # Calcula estatísticas
    total_sessions = len(sessions)
    total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
    total_calories = sum(s.get("calories_burned", 0) for s in sessions)
    
    return {
        "user_id": user_id,
        "sessions": sessions,
        "stats": {
            "total_sessions": total_sessions,
            "total_duration_minutes": total_duration,
            "total_calories_burned": total_calories,
            "avg_duration_per_session": round(total_duration / total_sessions, 1) if total_sessions > 0 else 0,
            "avg_calories_per_session": round(total_calories / total_sessions, 1) if total_sessions > 0 else 0
        }
    }


@api_router.post("/cardio/history/{user_id}")
async def log_cardio_session(user_id: str, session: dict):
    """
    Registra uma sessão de cardio completada.
    """
    # Verifica se usuário existe
    user = await db.user_profiles.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Cria registro da sessão
    session_record = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "exercise_id": session.get("exercise_id"),
        "exercise_name": session.get("exercise_name"),
        "duration_minutes": session.get("duration_minutes", 0),
        "calories_burned": session.get("calories_burned", 0),
        "intensity": session.get("intensity", "moderate"),
        "notes": session.get("notes", ""),
        "completed_at": datetime.utcnow()
    }
    
    await db.cardio_sessions.insert_one(session_record)
    
    return {
        "success": True,
        "session": session_record
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


# =====================================
# IN-APP PURCHASE (IAP) Endpoints
# =====================================

class IAPPurchaseRequest(BaseModel):
    user_id: str
    product_id: str
    transaction_id: str
    receipt: str
    platform: str  # 'ios' or 'android'

@api_router.post("/user/premium")
async def update_user_premium(request: IAPPurchaseRequest):
    """
    Atualiza o status premium do usuário após compra IAP.
    
    IMPORTANTE: Em produção, você deve validar o recibo com:
    - iOS: Apple App Store Server API
    - Android: Google Play Developer API
    """
    try:
        user_id = request.user_id
        
        # Verificar se o usuário existe
        user_auth = await db.users_auth.find_one({"id": user_id})
        user_profile = await db.user_profiles.find_one({"id": user_id})
        
        if not user_auth and not user_profile:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Determinar tipo de plano baseado no product_id
        plan_type = "monthly"
        if "annual" in request.product_id.lower():
            plan_type = "annual"
        
        # Atualizar status premium
        update_data = {
            "subscription_status": "active",
            "current_plan": plan_type,
            "iap_transaction_id": request.transaction_id,
            "iap_product_id": request.product_id,
            "iap_platform": request.platform,
            "iap_receipt": request.receipt[:500] if request.receipt else None,  # Guardar parte do recibo para referência
            "premium_activated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Atualizar em ambas as coleções
        if user_auth:
            await db.users_auth.update_one({"id": user_id}, {"$set": update_data})
        if user_profile:
            await db.user_profiles.update_one({"id": user_id}, {"$set": update_data})
        
        logger.info(f"User {user_id} premium activated via IAP: {request.product_id} on {request.platform}")
        
        return {
            "success": True,
            "message": "Premium ativado com sucesso",
            "plan_type": plan_type
        }
        
    except Exception as e:
        logger.error(f"Error updating premium status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/user/premium/{user_id}")
async def get_user_premium_status(user_id: str):
    """Retorna o status premium do usuário"""
    try:
        user_auth = await db.users_auth.find_one({"id": user_id})
        user_profile = await db.user_profiles.find_one({"id": user_id})
        
        if not user_auth and not user_profile:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Combinar dados
        user = user_auth if user_auth else {}
        if user_profile:
            user.update({k: v for k, v in user_profile.items() if k not in user or not user.get(k)})
        
        subscription_status = user.get("subscription_status", "inactive")
        
        return {
            "is_premium": subscription_status == "active",
            "subscription_status": subscription_status,
            "current_plan": user.get("current_plan"),
            "iap_platform": user.get("iap_platform"),
            "premium_activated_at": user.get("premium_activated_at")
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/admin/create-test-account")
async def create_apple_reviewer_account():
    """
    Cria uma conta de teste para os revisores da Apple.
    
    CREDENCIAIS:
    - Email: apple-reviewer@laf.com
    - Senha: AppleReview2025!
    
    Esta conta já terá:
    - Assinatura ativa (premium)
    - Perfil completo
    - Dieta e treino gerados
    """
    import hashlib
    import secrets
    
    test_email = "apple-reviewer@laf.com"
    test_password = "AppleReview2025!"
    
    # Verificar se já existe
    existing = await db.users_auth.find_one({"email": test_email})
    if existing:
        # Atualizar para garantir que está premium
        await db.users_auth.update_one(
            {"email": test_email},
            {"$set": {
                "subscription_status": "active",
                "current_plan": "annual",
                "premium_activated_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        return {
            "success": True,
            "message": "Conta de teste atualizada",
            "email": test_email,
            "password": test_password,
            "user_id": existing.get("id")
        }
    
    # Criar nova conta
    user_id = str(uuid.uuid4())
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((test_password + salt).encode()).hexdigest()
    
    # Criar usuário auth
    user_auth = {
        "_id": user_id,
        "id": user_id,
        "email": test_email,
        "password_hash": password_hash,
        "salt": salt,
        "subscription_status": "active",
        "current_plan": "annual",
        "premium_activated_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.users_auth.insert_one(user_auth)
    
    # Criar perfil completo
    profile = {
        "_id": user_id,
        "id": user_id,
        "name": "Apple Reviewer",
        "email": test_email,
        "age": 30,
        "sex": "masculino",
        "height": 175,
        "weight": 75,
        "target_weight": 72,
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "goal": "manutencao",
        "dietary_restrictions": [],
        "food_preferences": [],
        "injury_history": [],
        "language": "pt-BR",
        "meal_count": 5,
        "training_days": [1, 2, 4, 5],  # Segunda, Terça, Quinta, Sexta
        "subscription_status": "active",
        "current_plan": "annual",
        "premium_activated_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Calcular TDEE e macros
    bmr = calculate_bmr(profile["weight"], profile["height"], profile["age"], profile["sex"])
    tdee = calculate_tdee(bmr, profile["weekly_training_frequency"], profile["training_level"], profile["goal"])
    target_calories = calculate_target_calories(tdee, profile["goal"], profile["weight"])
    macros = calculate_macros(target_calories, profile["weight"], profile["goal"])
    
    profile["tdee"] = round(tdee, 0)
    profile["target_calories"] = round(target_calories, 0)
    profile["macros"] = macros
    
    await db.user_profiles.insert_one(profile)
    
    # Criar settings
    settings = {
        "_id": user_id,
        "user_id": user_id,
        "theme_preference": "system",
        "language": "pt-BR",
        "meal_count": 5,
        "notifications_enabled": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.user_settings.insert_one(settings)
    
    logger.info(f"✅ Conta de teste para Apple criada: {test_email}")
    
    return {
        "success": True,
        "message": "Conta de teste criada com sucesso",
        "email": test_email,
        "password": test_password,
        "user_id": user_id,
        "status": "premium",
        "plan": "annual"
    }


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