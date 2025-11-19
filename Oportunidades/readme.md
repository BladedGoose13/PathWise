"""
Aplicación principal de FastAPI
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

from routes.auth_routes import router as auth_router
from routes.scholarship_routes import router as scholarship_router

# 🔥 Cargar variables de entorno
load_dotenv()

# 🔥 Obtener configuración del .env
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scholarships.db")
PORT = int(os.getenv("PORT", 8001))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Verificar que existan variables críticas
if not SECRET_KEY:
    raise ValueError("❌ ERROR: SECRET_KEY no está definida en .env")

print("=" * 60)
print("🎓 SKKU Scholarship Finder API")
print("=" * 60)
print(f"🔑 SECRET_KEY: {SECRET_KEY[:10]}..." if SECRET_KEY else "❌ No SECRET_KEY")
print(f"💾 DATABASE: {DATABASE_URL}")
print(f"🌍 ENVIRONMENT: {ENVIRONMENT}")
print(f"🚀 PORT: {PORT}")
print("=" * 60)

# Crear la aplicación FastAPI
app = FastAPI(
    title="SKKU Scholarship Finder API",
    description="""
    ## 🎓 API para búsqueda personalizada de becas usando IA
    
    ### Flujo de uso:
    1. **Registro:** `POST /api/auth/register` - Crea tu cuenta
    2. **Login:** `POST /api/auth/login` - Inicia sesión
    3. **Perfil:** `POST /api/scholarships/user/create` - Completa tu perfil académico
    4. **Buscar:** `GET /api/scholarships/search` - Busca becas
    5. **Recomendaciones:** `GET /api/scholarships/recommendations` - Obtén becas recomendadas
    
    ### Características:
    - ✅ Autenticación segura con sesiones
    - ✅ Perfiles académicos personalizados
    - ✅ Búsqueda inteligente de becas
    - ✅ Recomendaciones basadas en IA
    - ✅ Base de datos SQLite
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (permite peticiones desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(scholarship_router)


# ==========================================
# EXCEPTION HANDLERS
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Maneja todas las excepciones no capturadas"""
    print(f"❌ ERROR: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc) if ENVIRONMENT == "development" else "An error occurred"
        }
    )


# ==========================================
# ENDPOINTS PRINCIPALES
# ==========================================

@app.get("/", tags=["Root"])
def home():
    """
    Endpoint principal - Información de la API
    """
    return {
        "message": "🎓 SKKU Scholarship Finder API",
        "status": "online",
        "version": "2.0.0",
        "environment": ENVIRONMENT,
        "features": [
            "👤 User Authentication (Register, Login, Logout)",
            "📝 Academic Profile Management",
            "🔍 AI-Powered Scholarship Search",
            "💡 Personalized Recommendations",
            "💾 SQLite Database Storage",
            "📊 Match Score Calculation"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        },
        "getting_started": {
            "step_1": "POST /api/auth/register - Create account",
            "step_2": "POST /api/auth/login - Login",
            "step_3": "POST /api/scholarships/user/create - Complete profile",
            "step_4": "GET /api/scholarships/recommendations - Get scholarships"
        }
    }


@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint - Verifica que la API esté funcionando
    """
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "database": DATABASE_URL,
        "version": "2.0.0"
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Endpoint para el favicon (evita el error 404 en navegadores)
    """
    from fastapi.responses import Response
    return Response(status_code=204)


# ==========================================
# STARTUP & SHUTDOWN EVENTS
# ==========================================

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    print("\n✅ API iniciada correctamente")
    print(f"📍 Disponible en: http://127.0.0.1:{PORT}")
    print(f"📚 Documentación: http://127.0.0.1:{PORT}/docs")
    print(f"📖 ReDoc: http://127.0.0.1:{PORT}/redoc\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación"""
    print("\n👋 Cerrando API...")


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    print("\n🚀 Iniciando SKKU Scholarship Finder API...")
    print(f"📍 Servidor: http://127.0.0.1:{PORT}")
    print(f"📚 Documentación: http://127.0.0.1:{PORT}/docs")
    print(f"🔄 Hot reload: {'Activado' if ENVIRONMENT == 'development' else 'Desactivado'}")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "app_becas:app",
        host="0.0.0.0",
        port=PORT,
        reload=ENVIRONMENT == "development",
        log_level="info"
    )