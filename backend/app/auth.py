from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================

# Contexto para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Variables de configuración
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_larga_cambiar_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Esquema de seguridad (para que Swagger UI muestre Login)
security = HTTPBearer()

# ============================================
# FUNCIONES DE CONTRASEÑA
# ============================================

def hash_password(password: str) -> str:
    """Encripta una contraseña usando bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña coincida con su versión hasheada"""
    return pwd_context.verify(plain_password, hashed_password)

# ============================================
# FUNCIONES DE TOKEN JWT
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "usuario@email.com", "rol": "Coordinador"})
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT encriptado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token a verificar
    
    Returns:
        Payload del token si es válido
    
    Raises:
        HTTPException si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return payload
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido"
        )

# ============================================
# DEPENDENCIAS PARA PROTEGER ENDPOINTS
# ============================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependencia que extrae y valida el usuario actual del token
    
    Uso en endpoints:
        @app.get("/mi-perfil")
        def mi_perfil(usuario: dict = Depends(get_current_user)):
            return {"email": usuario["sub"]}
    """
    token = credentials.credentials
    payload = verify_token(token)
    return payload

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Dependencia que valida token si está presente, pero no es obligatorio
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except:
        return None

def check_rol(rol_requerido: str):
    """
    Crea una dependencia que verifica el rol del usuario
    
    Uso en endpoints:
        @app.get("/admin")
        def panel_admin(usuario: dict = Depends(check_rol("Coordinador"))):
            return {"mensaje": "Eres coordinador"}
    """
    async def verificar_rol(usuario: dict = Depends(get_current_user)) -> dict:
        rol_usuario = usuario.get("rol")
        
        if rol_usuario != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere rol: {rol_requerido}. Tú tienes: {rol_usuario}"
            )
        return usuario
    
    return verificar_rol

# ============================================
# ESQUEMAS PYDANTIC PARA AUTENTICACIÓN
# ============================================

from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Esquema para el login"""
    email: str
    password: str

class TokenResponse(BaseModel):
    """Esquema para la respuesta con token"""
    access_token: str
    token_type: str = "bearer"
    usuario: dict
    rol: str

class RegisterRequest(BaseModel):
    """Esquema para registrar nuevo usuario"""
    email: str
    nombre: str
    apellido: str
    password: str
    rol: str = "Participante"  # Por defecto
