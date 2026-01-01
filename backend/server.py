from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Dados Básicos
    name: str
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
    
    # ==================== ATHLETE DOMAIN MODEL ====================
    # OBRIGATÓRIO se goal == "atleta"
    # Phases: "off_season", "pre_prep", "prep", "peak_week", "post_show"
    competition_phase: Optional[str] = None
    
    # Timeline tracking
    weeks_to_competition: Optional[int] = None  # Semanas até próxima competição
    competition_date: Optional[datetime] = None  # Data alvo da competição
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
    # Athlete-specific fields (REQUIRED if goal == "atleta")
    competition_phase: Optional[str] = None  # "off_season", "pre_prep", "prep", "peak_week", "post_show"
    weeks_to_competition: Optional[int] = None
    competition_date: Optional[str] = None  # ISO date string
    dietary_restrictions: List[str] = Field(default_factory=list)
    food_preferences: List[str] = Field(default_factory=list)
    injury_history: List[str] = Field(default_factory=list)

class UserProfileUpdate(BaseModel):
    weight: Optional[float] = None
    target_weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    weekly_training_frequency: Optional[int] = None
    goal: Optional[str] = None
    competition_phase: Optional[str] = None
    weeks_to_competition: Optional[int] = None
    competition_date: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    food_preferences: Optional[List[str]] = None

# ==================== SETTINGS MODELS ====================

class UserSettings(BaseModel):
    """User settings for theme and privacy"""
    user_id: str
    theme_preference: str = "system"  # "system", "light", "dark"
    privacy_analytics: bool = True
    privacy_personalization: bool = True
    privacy_notifications: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSettingsUpdate(BaseModel):
    """Partial update for settings"""
    theme_preference: Optional[str] = None
    privacy_analytics: Optional[bool] = None
    privacy_personalization: Optional[bool] = None
    privacy_notifications: Optional[bool] = None

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
    - off_season: superávit de +7.5% (lean bulk)
    - pre_prep: manutenção ou leve déficit (-5%)
    - prep: déficit agressivo (-22.5%)
    - peak_week: déficit muito agressivo (-25%) + manipulação
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
        elif competition_phase == "pre_prep":
            # Pre-Prep: transição, leve déficit (-5%)
            return tdee * 0.95
        elif competition_phase == "prep":
            # Prep/Contest: déficit agressivo (-22.5%)
            return tdee * 0.775
        elif competition_phase == "peak_week":
            # Peak Week: déficit muito agressivo (-25%)
            return tdee * 0.75
        elif competition_phase == "post_show":
            # Post-Show: superávit para recuperação (+10%)
            return tdee * 1.10
        else:
            # Default para prep se fase não especificada
            return tdee * 0.775
    else:  # manutenção
        return tdee

def calculate_macros(target_calories: float, weight: float, goal: str, competition_phase: Optional[str] = None) -> Dict[str, float]:
    """
    Calcula distribuição de macronutrientes.
    
    REGRAS PARA ATLETA/COMPETIÇÃO:
    - offseason: P=1.8-2.2g/kg, G=0.8-1.0g/kg, C=restante (ALTO)
    - prep: P=2.4-2.8g/kg, G=0.6-0.8g/kg, C=restante (BAIXO)
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
        if competition_phase == "offseason":
            # OFF-SEASON (Lean Bulk): P=2.0g/kg, G=0.9g/kg, C=restante (ALTO)
            protein_g = weight * 2.0
            fat_g = weight * 0.9
            protein_cal = protein_g * 4
            fat_cal = fat_g * 9
            carbs_cal = target_calories - protein_cal - fat_cal
            carbs_g = max(0, carbs_cal / 4)
        elif competition_phase == "prep":
            # PREP (Cutting Agressivo): P=2.6g/kg, G=0.7g/kg, C=restante (BAIXO)
            protein_g = weight * 2.6
            fat_g = weight * 0.7
            protein_cal = protein_g * 4
            fat_cal = fat_g * 9
            carbs_cal = target_calories - protein_cal - fat_cal
            carbs_g = max(0, carbs_cal / 4)
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

# ==================== ROUTES ====================

@api_router.post("/user/profile", response_model=UserProfile)
async def create_user_profile(profile_data: UserProfileCreate):
    """
    Cria perfil de usuário e calcula TDEE e macros automaticamente.
    
    REGRA: Se goal == "atleta", competition_phase é OBRIGATÓRIO.
    """
    # Validação: atleta requer fase de competição
    if profile_data.goal == "atleta" and not profile_data.competition_phase:
        raise HTTPException(
            status_code=400, 
            detail="Atletas devem especificar competition_phase: 'offseason' ou 'prep'"
        )
    
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
        competition_phase=profile_data.competition_phase
    )
    
    # Calcula macros (com fase se atleta)
    macros = calculate_macros(
        target_calories=target_calories,
        weight=profile_data.weight,
        goal=profile_data.goal,
        competition_phase=profile_data.competition_phase
    )
    
    # Cria perfil completo
    profile = UserProfile(
        **profile_data.dict(),
        tdee=round(tdee, 0),
        target_calories=round(target_calories, 0),
        macros=macros
    )
    
    # Salva no banco
    profile_dict = profile.dict()
    profile_dict["_id"] = profile_dict["id"]
    await db.user_profiles.insert_one(profile_dict)
    
    return profile

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

# ==================== DIET ENDPOINTS ====================

@api_router.post("/diet/generate")
async def generate_diet(user_id: str):
    """
    Gera um plano de dieta personalizado com GARANTIA de integridade.
    
    CONTRATO:
    - Retorna dieta SOMENTE se macros computados = targets (±tolerâncias estritas)
    - Se impossível fechar macros → retorna HTTP 500 (NÃO fallback)
    - Frontend deve mostrar erro se receber 500
    
    TOLERÂNCIAS:
    - Proteína: ±3g
    - Carbs: ±3g
    - Gordura: ±2g
    - Calorias: ±25kcal
    """
    try:
        # Busca perfil do usuário
        user_profile = await db.user_profiles.find_one({"_id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
        # Importa serviço de dieta
        from diet_service import DietAIService
        
        diet_service = DietAIService()
        
        # Gera plano de dieta (levanta exceção se impossível)
        diet_plan = diet_service.generate_diet_plan(
            user_profile=dict(user_profile),
            target_calories=user_profile.get('target_calories', 2000),
            target_macros=user_profile.get('macros', {"protein": 150, "carbs": 200, "fat": 60})
        )
        
        # VALIDAÇÃO FINAL: Asserts de integridade
        # Soma REAL dos alimentos (não os valores pre-computados)
        real_protein = sum(sum(f["protein"] for f in m.foods) for m in diet_plan.meals)
        real_carbs = sum(sum(f["carbs"] for f in m.foods) for m in diet_plan.meals)
        real_fat = sum(sum(f["fat"] for f in m.foods) for m in diet_plan.meals)
        real_cal = sum(sum(f["calories"] for f in m.foods) for m in diet_plan.meals)
        
        target_macros = user_profile.get('macros', {"protein": 150, "carbs": 200, "fat": 60})
        target_cal = user_profile.get('target_calories', 2000)
        
        # Verifica tolerâncias estritas
        p_diff = abs(real_protein - target_macros["protein"])
        c_diff = abs(real_carbs - target_macros["carbs"])
        f_diff = abs(real_fat - target_macros["fat"])
        cal_diff = abs(real_cal - target_cal)
        
        if p_diff > 3 or c_diff > 3 or f_diff > 2 or cal_diff > 25:
            logger.error(
                f"INTEGRIDADE FALHOU - Targets: P{target_macros['protein']}g C{target_macros['carbs']}g F{target_macros['fat']}g {target_cal}kcal | "
                f"Computed: P{real_protein:.1f}g C{real_carbs:.1f}g F{real_fat:.1f}g {real_cal:.1f}kcal | "
                f"Diffs: P{p_diff:.1f}g C{c_diff:.1f}g F{f_diff:.1f}g {cal_diff:.1f}kcal"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Erro de integridade: macros computados não batem com targets. "
                       f"P:{real_protein:.0f}g vs {target_macros['protein']}g, "
                       f"C:{real_carbs:.0f}g vs {target_macros['carbs']}g, "
                       f"G:{real_fat:.0f}g vs {target_macros['fat']}g"
            )
        
        # Salva no banco
        diet_dict = diet_plan.dict()
        diet_dict["_id"] = diet_dict["id"]
        await db.diet_plans.insert_one(diet_dict)
        
        logger.info(
            f"DIETA GERADA COM SUCESSO - User: {user_id} | "
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

# ==================== WORKOUT ENDPOINTS ====================

@api_router.post("/workout/generate")
async def generate_workout(user_id: str):
    """
    Gera um plano de treino personalizado com IA
    """
    try:
        # Busca perfil do usuário
        user_profile = await db.user_profiles.find_one({"_id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
        # Importa serviço de treino
        from workout_service import WorkoutAIService
        
        workout_service = WorkoutAIService()
        
        # Gera plano de treino
        workout_plan = workout_service.generate_workout_plan(
            user_profile=dict(user_profile)
        )
        
        # Salva no banco
        workout_dict = workout_plan.dict()
        workout_dict["_id"] = workout_dict["id"]
        await db.workout_plans.insert_one(workout_dict)
        
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
    
    # Busca settings existentes ou cria
    settings = await db.user_settings.find_one({"user_id": user_id})
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
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