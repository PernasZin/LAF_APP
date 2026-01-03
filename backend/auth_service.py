"""
Serviço de Autenticação - JWT + Email/Senha
P0 CRÍTICO: Nenhum perfil sem autenticação
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from pydantic import BaseModel, Field, EmailStr
import uuid

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'laf-secret-key-2025-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 dias


# ==================== MODELS ====================

class UserAuth(BaseModel):
    """Modelo de autenticação do usuário"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    salt: str
    is_active: bool = True
    is_verified: bool = False
    profile_id: Optional[str] = None  # Vincula ao perfil após onboarding
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class SignUpRequest(BaseModel):
    """Request de cadastro"""
    email: str
    password: str  # Mínimo 8 caracteres


class LoginRequest(BaseModel):
    """Request de login"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Response com token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
    user_id: str
    email: str
    has_profile: bool  # Se já completou onboarding
    profile_id: Optional[str] = None


class TokenPayload(BaseModel):
    """Payload do JWT"""
    sub: str  # user_id
    email: str
    exp: datetime
    iat: datetime


# ==================== FUNÇÕES ====================

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Gera hash da senha com salt"""
    if not salt:
        salt = secrets.token_hex(32)
    
    # SHA-256 com salt
    password_bytes = (password + salt).encode('utf-8')
    password_hash = hashlib.sha256(password_bytes).hexdigest()
    
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verifica se a senha está correta"""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash


def create_access_token(user_id: str, email: str) -> str:
    """Cria token JWT"""
    now = datetime.utcnow()
    expire = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": now
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Optional[TokenPayload]:
    """Decodifica e valida token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"])
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def validate_email(email: str) -> bool:
    """Validação básica de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    """Valida requisitos mínimos da senha"""
    if len(password) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"
    return True, ""


# ==================== SERVICE CLASS ====================

class AuthService:
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users_auth
    
    async def signup(self, email: str, password: str) -> Dict:
        """Cadastra novo usuário"""
        # Valida email
        if not validate_email(email):
            raise ValueError("Email inválido")
        
        # Valida senha
        is_valid, error = validate_password(password)
        if not is_valid:
            raise ValueError(error)
        
        # Verifica se email já existe
        existing = await self.users_collection.find_one({"email": email.lower()})
        if existing:
            raise ValueError("Email já cadastrado")
        
        # Cria hash da senha
        password_hash, salt = hash_password(password)
        
        # Cria usuário
        user = UserAuth(
            email=email.lower(),
            password_hash=password_hash,
            salt=salt
        )
        
        # Salva no banco
        user_dict = user.dict()
        user_dict["_id"] = user_dict["id"]
        await self.users_collection.insert_one(user_dict)
        
        # Gera token
        access_token = create_access_token(user.id, user.email)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,
            "user_id": user.id,
            "email": user.email,
            "has_profile": False,
            "profile_id": None
        }
    
    async def login(self, email: str, password: str) -> Dict:
        """Autentica usuário existente"""
        # Busca usuário auth
        user = await self.users_collection.find_one({"email": email.lower()})
        if not user:
            raise ValueError("Email ou senha incorretos")
        
        # Verifica senha
        if not verify_password(password, user["password_hash"], user["salt"]):
            raise ValueError("Email ou senha incorretos")
        
        # Verifica se está ativo
        if not user.get("is_active", True):
            raise ValueError("Conta desativada")
        
        # Atualiza last_login
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Verifica se tem perfil (busca na collection user_profiles pelo ID ou _id)
        profiles_collection = self.db.user_profiles
        profile = await profiles_collection.find_one({"$or": [
            {"_id": user["_id"]},
            {"id": user["_id"]}
        ]})
        has_profile = profile is not None
        profile_id = profile["_id"] if profile else None
        
        # Se tem profile mas profile_id não está setado no auth, atualiza
        if has_profile and not user.get("profile_id"):
            await self.users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"profile_id": profile_id}}
            )
        
        # Gera token
        access_token = create_access_token(user["_id"], user["email"])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,
            "user_id": user["_id"],
            "email": user["email"],
            "has_profile": has_profile,
            "profile_id": str(profile_id) if profile_id else None
        }
    
    async def validate_token(self, token: str) -> Optional[Dict]:
        """Valida token e retorna dados do usuário"""
        payload = decode_token(token)
        if not payload:
            return None
        
        # Verifica se usuário ainda existe e está ativo
        user = await self.users_collection.find_one({"_id": payload.sub})
        if not user or not user.get("is_active", True):
            return None
        
        return {
            "user_id": user["_id"],
            "email": user["email"],
            "has_profile": user.get("profile_id") is not None,
            "profile_id": user.get("profile_id")
        }
    
    async def link_profile(self, user_id: str, profile_id: str) -> bool:
        """Vincula perfil ao usuário autenticado"""
        result = await self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"profile_id": profile_id, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def logout(self, user_id: str) -> bool:
        """Marca logout (para tracking)"""
        # Em uma implementação mais robusta, invalidaria o token
        # Por agora, apenas retorna sucesso
        return True
    
    async def delete_user(self, user_id: str) -> bool:
        """Deleta usuário (para testes/cleanup)"""
        result = await self.users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
