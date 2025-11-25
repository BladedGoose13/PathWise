# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from dotenv import load_dotenv

# 🔥 AGREGAR PATHS AL PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Clases'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Oportunidades'))

# Cargar .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
SORA_API_URL = os.getenv("SORA_API_URL")

# ============================================================================
# CREAR APP PRINCIPAL
# ============================================================================

app = FastAPI(
    title="PathWise - Plataforma Educativa",
    description="Plataforma integral para educación con IA",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# IMPORTAR ROUTERS - CLASES
# ============================================================================

try:
    from Clases.routes.text_routes import router as text_router
    from Clases.routes.video_routes import router as video_router
    from Clases.routes.pdf_routes import router as pdf_router

    app.include_router(text_router, prefix="/clases/text", tags=["📝 Clases - Texto"])
    app.include_router(video_router, prefix="/clases/video", tags=["🎥 Clases - Video"])
    app.include_router(pdf_router, prefix="/clases/pdf", tags=["📄 Clases - PDF"])
    
    print("✅ Módulo de Clases cargado")
except ImportError as e:
    print(f"⚠️ Error cargando Clases: {e}")

# ============================================================================
# IMPORTAR ROUTERS - OPORTUNIDADES (si existen)
# ============================================================================

try:
    from Oportunidades.routes.auth_routes import router as auth_router
    from Oportunidades.routes.scholarship_routes import router as scholarship_router
    
    app.include_router(auth_router, prefix="/api/auth", tags=["🔐 Auth"])
    app.include_router(scholarship_router, prefix="/api/scholarships", tags=["🎓 Becas"])
    
    print("✅ Módulo de Oportunidades cargado")
except ImportError as e:
    print(f"⚠️ Oportunidades no disponible: {e}")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {
        "app": "PathWise",
        "version": "2.0.0",
        "status": "online",
        "openai": "✅" if OPENAI_API_KEY else "❌",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    print("\n" + "="*70)
    print("🚀 PATHWISE API")
    print("="*70)
    print(f"✅ OpenAI: {'OK' if OPENAI_API_KEY else 'NO'}")
    print("📍 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    print("="*70 + "\n")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)