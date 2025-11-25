from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from verificacion import SistemaVerificacion
from typing import Optional

app = FastAPI(
    title="PathWise API",
    description="API de verificación de estudiantes",
    version="2.0"
)

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sistema = SistemaVerificacion('PATWISE_modified.db')

# Modelos Pydantic
class UsuarioRegistro(BaseModel):
    email: EmailStr
    nombre: str
    escuela: str
    grado_actual: str
    area: Optional[str] = None
    community_tipo: Optional[str] = None

class UsuarioRespuesta(BaseModel):
    email: str
    nombre: str
    escuela: str
    requiere_verificacion: str

# Endpoints
@app.post("/api/registro", response_model=dict, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario: UsuarioRegistro):
    """
    Registra un nuevo usuario con verificación automática
    """
    resultado = sistema.registrar_usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        escuela=usuario.escuela,
        grado_actual=usuario.grado_actual,
        area=usuario.area,
        community_tipo=usuario.community_tipo
    )
    
    if not resultado['exito']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado['error']
        )
    
    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "data": {
            "email": resultado['email'],
            "requiere_verificacion": resultado['requiere_verificacion'],
            "deteccion": resultado['deteccion_dominio']
        }
    }

@app.get("/api/usuarios/{email}", response_model=UsuarioRespuesta)
async def obtener_usuario(email: str):
    """
    Obtiene información de un usuario por email
    """
    import sqlite3
    conn = sqlite3.connect('PATWISE_modified.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT email, nombre, escuela, requiere_verificacion_estudiante
        FROM usuarios
        WHERE email = ?
    ''', (email,))
    
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "email": usuario[0],
        "nombre": usuario[1],
        "escuela": usuario[2],
        "requiere_verificacion": usuario[3]
    }

@app.get("/api/estadisticas")
async def obtener_estadisticas():
    """
    Obtiene estadísticas del sistema
    """
    return sistema.generar_reporte()

@app.get("/api/usuarios/verificar/pendientes")
async def usuarios_pendientes():
    """
    Lista usuarios que requieren verificación
    """
    return {
        "usuarios": sistema.obtener_usuarios_pendientes()
    }