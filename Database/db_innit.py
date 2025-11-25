from pathlib import Path
from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from .verificacion import SistemaVerificacion

DB_PATH = Path(__file__).with_name("PATWISE.db")
DB_PATH_STR = str(DB_PATH)

sistema = SistemaVerificacion(DB_PATH_STR)

ROUTER_PREFIX = "/database"
router = APIRouter(prefix=ROUTER_PREFIX, tags=["Database"])


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
@router.post("/registro", response_model=dict, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario: UsuarioRegistro):
    """Registra un nuevo usuario con verificación automática."""
    resultado = sistema.registrar_usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        escuela=usuario.escuela,
        grado_actual=usuario.grado_actual,
        area=usuario.area,
        community_tipo=usuario.community_tipo,
    )

    if not resultado["exito"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["error"],
        )

    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "data": {
            "email": resultado["email"],
            "requiere_verificacion": resultado["requiere_verificacion"],
            "deteccion": resultado["deteccion_dominio"],
        },
    }


@router.get("/usuarios/{email}", response_model=UsuarioRespuesta)
async def obtener_usuario(email: str):
    """Obtiene información de un usuario por email."""
    import sqlite3

    with sqlite3.connect(DB_PATH_STR) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT email, nombre, escuela, requiere_verificacion_estudiante
            FROM usuarios
            WHERE email = ?
            """,
            (email,),
        )

        usuario = cursor.fetchone()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return {
        "email": usuario[0],
        "nombre": usuario[1],
        "escuela": usuario[2],
        "requiere_verificacion": usuario[3],
    }


@router.get("/estadisticas")
async def obtener_estadisticas():
    """Obtiene estadísticas del sistema."""
    return sistema.generar_reporte()


@router.get("/usuarios/verificar/pendientes")
async def usuarios_pendientes():
    """Lista usuarios que requieren verificación."""
    return {"usuarios": sistema.obtener_usuarios_pendientes()}


def create_app() -> FastAPI:
    """Crea una instancia de FastAPI para ejecutar el servicio de verificación."""
    app = FastAPI(
        title="PathWise API",
        description="API de verificación de estudiantes",
        version="2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mantener el mismo prefijo que en main.py cuando se ejecuta de forma independiente
    app.include_router(router, prefix="/api")
    return app


app = create_app()
