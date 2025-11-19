"""
Rutas de autenticación (registro, login, logout)
SOLO maneja credenciales de usuario
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from database.db_manager import DatabaseManager
from models.schemas import UserRegister, UserLogin
from passlib.hash import bcrypt
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
db = DatabaseManager()

# Obtener SECRET_KEY del .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY no está definida en .env")

# Simulación de sesiones (en producción usar JWT)
active_sessions = {}


@router.post("/api/auth/register", tags=["Authentication"])
async def register_user(body: UserRegister):
    """
    Registra un nuevo usuario (solo credenciales básicas)
    
    - Verifica que el email y username no existan
    - Encripta la contraseña
    - Guarda en la base de datos
    - Retorna session_token para autenticación
    
    **Siguiente paso:** El usuario debe completar su perfil académico 
    usando POST /api/scholarships/user/create
    """
    
    # Verificar si el email ya existe
    existing_email = db.get_user_by_email(body.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Verificar si el username ya existe
    existing_username = db.get_user_by_username(body.username)
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Encriptar contraseña
    hashed_password = bcrypt.hash(body.password)
    
    # Crear usuario (SOLO credenciales)
    user_data = {
        'username': body.username,
        'email': body.email,
        'password': hashed_password
    }
    
    try:
        user = db.create_user(user_data)
        
        # Crear sesión
        session_token = secrets.token_hex(32)
        active_sessions[session_token] = user.id
        
        return {
            'success': True,
            'message': 'User registered successfully. Please complete your academic profile.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'session_token': session_token,
            'next_step': 'POST /api/scholarships/user/create'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/auth/login", tags=["Authentication"])
async def login_user(body: UserLogin):
    """
    Inicia sesión de un usuario
    
    - Verifica que el email exista
    - Compara la contraseña
    - Crea una sesión y retorna session_token
    """
    
    # Buscar usuario por email
    user = db.get_user_by_email(body.email)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verificar contraseña
    if not bcrypt.verify(body.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Crear sesión
    session_token = secrets.token_hex(32)
    active_sessions[session_token] = user.id
    
    return {
        'success': True,
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'session_token': session_token
    }


@router.post("/api/auth/logout", tags=["Authentication"])
async def logout_user(session_token: str = Header(..., alias="Authorization")):
    """
    Cierra sesión de un usuario
    
    Requiere el session_token en el header Authorization
    """
    
    # Limpiar el prefijo "Bearer " si existe
    if session_token.startswith("Bearer "):
        session_token = session_token[7:]
    
    if session_token in active_sessions:
        del active_sessions[session_token]
        return {
            'success': True,
            'message': 'Logout successful'
        }
    
    raise HTTPException(status_code=400, detail="Invalid session")


@router.get("/api/auth/me", tags=["Authentication"])
async def get_current_user(session_token: str = Header(..., alias="Authorization")):
    """
    Obtiene el usuario actual de la sesión
    
    Requiere el session_token en el header Authorization
    """
    
    # Limpiar el prefijo "Bearer " si existe
    if session_token.startswith("Bearer "):
        session_token = session_token[7:]
    
    if session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = active_sessions[session_token]
    user = db.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }


@router.get("/api/auth/validate", tags=["Authentication"])
async def validate_session(session_token: str = Header(..., alias="Authorization")):
    """
    Valida si un session_token es válido
    
    Útil para verificar sesión en el frontend
    """
    
    # Limpiar el prefijo "Bearer " si existe
    if session_token.startswith("Bearer "):
        session_token = session_token[7:]
    
    if session_token in active_sessions:
        user_id = active_sessions[session_token]
        return {
            'success': True,
            'valid': True,
            'user_id': user_id
        }
    
    return {
        'success': True,
        'valid': False
    }


# Función auxiliar para obtener el user_id desde el session_token
def get_current_user_id(session_token: str) -> int:
    """
    Función helper para obtener el user_id del token
    Usada por otros routers
    """
    if session_token.startswith("Bearer "):
        session_token = session_token[7:]
    
    if session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return active_sessions[session_token]