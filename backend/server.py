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
    
    # Fase de Competição (OBRIGATÓRIO se goal == "atleta")
    competition_phase: Optional[str] = None  # "offseason", "prep"
    
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
    competition_phase: Optional[str] = None  # OBRIGATÓRIO se goal == "atleta"
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
    dietary_restrictions: Optional[List[str]] = None
    food_preferences: Optional[List[str]] = None

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
    Ajusta calorias baseado no objetivo
    """
    if goal == "cutting":
        # Déficit de 15-20% para perda de gordura
        return tdee * 0.82  # 18% de déficit
    elif goal == "bulking":
        # Superávit de 10-15% para ganho de massa
        return tdee * 1.12  # 12% de superávit
    elif goal == "atleta":
        # Superávit moderado para performance
        return tdee * 1.08  # 8% de superávit
    else:  # manutenção
        return tdee

def calculate_macros(target_calories: float, weight: float, goal: str) -> Dict[str, float]:
    """
    Calcula distribuição de macronutrientes
    """
    if goal == "cutting":
        # Alto proteína, moderado carbo, baixo gordura
        protein_g = weight * 2.2  # 2.2g por kg
        fat_g = weight * 0.8      # 0.8g por kg
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = carbs_cal / 4
    elif goal == "bulking":
        # Alto proteína, alto carbo, moderado gordura
        protein_g = weight * 2.0  # 2g por kg
        fat_g = weight * 1.0      # 1g por kg
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = carbs_cal / 4
    elif goal == "atleta":
        # Balanceado para performance
        protein_g = weight * 2.2
        fat_g = weight * 1.0
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = carbs_cal / 4
    else:  # manutenção
        protein_g = weight * 1.8
        fat_g = weight * 1.0
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = carbs_cal / 4
    
    return {
        "protein": round(protein_g, 1),
        "carbs": round(carbs_g, 1),
        "fat": round(fat_g, 1)
    }

# ==================== ROUTES ====================

@api_router.post("/user/profile", response_model=UserProfile)
async def create_user_profile(profile_data: UserProfileCreate):
    """
    Cria perfil de usuário e calcula TDEE e macros automaticamente
    """
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
        # Se peso mudou, recalcula tudo
        if "weight" in update_dict or "goal" in update_dict:
            current_profile = UserProfile(**existing_profile)
            
            # Usa novos valores ou mantém existentes
            new_weight = update_dict.get("weight", current_profile.weight)
            new_goal = update_dict.get("goal", current_profile.goal)
            new_frequency = update_dict.get("weekly_training_frequency", current_profile.weekly_training_frequency)
            
            # Recalcula
            bmr = calculate_bmr(
                weight=new_weight,
                height=current_profile.height,
                age=current_profile.age,
                sex=current_profile.sex
            )
            tdee = calculate_tdee(bmr, new_frequency, current_profile.training_level)
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
    Gera um plano de dieta personalizado com IA
    """
    try:
        # Busca perfil do usuário
        user_profile = await db.user_profiles.find_one({"_id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        
        # Importa serviço de dieta
        from diet_service import DietAIService
        
        diet_service = DietAIService()
        
        # Gera plano de dieta
        diet_plan = diet_service.generate_diet_plan(
            user_profile=dict(user_profile),
            target_calories=user_profile.get('target_calories', 2000),
            target_macros=user_profile.get('macros', {"protein": 150, "carbs": 200, "fat": 60})
        )
        
        # Salva no banco
        diet_dict = diet_plan.dict()
        diet_dict["_id"] = diet_dict["id"]
        await db.diet_plans.insert_one(diet_dict)
        
        return diet_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar dieta: {e}")
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