from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os
from dotenv import load_dotenv

# 🔥 CARGAR .env PRIMERO
load_dotenv()

from pathlib import Path
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)
print("DEBUG KEY:", os.getenv("OPENAI_API_KEY"))

# Verificar API Key al inicio
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("❌ ERROR: OPENAI_API_KEY no encontrada en .env")
    print("💡 Crea un archivo .env con:")
    print("   OPENAI_API_KEY=sk-proj-tu_clave_aqui")
else:
    print(f"✅ OpenAI API Key detectada: {API_KEY[:15]}...{API_KEY[-4:]}")

# --- Sora config (agrega estas variables en tu .env) ---
SORA_API_URL = os.getenv("SORA_API_URL")      # ej: https://api.sora.example/v1/videos
SORA_API_KEY = os.getenv("SORA_API_KEY")      # clave para Sora (Bearer)

# Test de OpenAI API al inicio
if API_KEY:
    print("\n🧪 Probando conexión con OpenAI...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # ✅ CORRECTO: Usar 'messages' no 'input'
    data = {
        "model": "gpt-4o-mini",  # ✅ Modelo correcto y más barato para tests
        "messages": [
            {"role": "user", "content": "Di 'hola' si funciona"}
        ],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", 
            headers=headers, 
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ OpenAI respondió: {message}")
        else:
            print(f"⚠️ Error {response.status_code}: {response.json()}")
    
    except Exception as e:
        print(f"❌ Error probando OpenAI: {e}")

print("\n" + "="*60)

# <-- AQUÍ IMPORTAS TUS ROUTERS -->
from routes.text_routes import router as text_router
from routes.video_routes import router as video_router
from routes.pdf_routes import router as pdf_router

# Crear la app
app = FastAPI(
    title="SKKU HACKEDU API",
    description="API educativa con IA - Textos, Videos, Guías de estudio y más",
    version="1.0.0"
)

# --- CORS (mantener/ajustar según tu frontend) ---
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(text_router)
app.include_router(video_router)
app.include_router(pdf_router)

# --- NUEVO: helper para generar videos en Sora ---
def generate_video_sora(prompt: str, duration: int = 6, resolution: str = "720p", voice: str | None = None):
    """
    Envía una petición a la API de Sora (configurada por SORA_API_URL/SORA_API_KEY)
    - prompt: texto descriptivo para generar el video
    - duration: segundos aproximados
    - resolution: "480p"/"720p"/"1080p" (según Sora)
    - voice: id de locución si aplica
    Devuelve el JSON que retorne Sora (puede incluir video_url o video_base64).
    """
    api_url = SORA_API_URL
    api_key = SORA_API_KEY
    if not api_url or not api_key:
        raise ValueError("SORA_API_URL o SORA_API_KEY no configurados en el entorno (.env)")

    payload = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
    }
    if voice:
        payload["voice"] = voice

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(api_url, json=payload, headers=headers, timeout=180)
    try:
        resp.raise_for_status()
    except Exception as e:
        # Propagar error con detalle del cuerpo para debugging
        raise Exception(f"Sora API error {resp.status_code}: {resp.text}") from e

    return resp.json()

# --- NUEVO: endpoint para generar video via Sora ---
@app.post("/sora/generate")
async def sora_generate(request: Request):
    """
    POST /sora/generate
    JSON body:
      { "prompt": "...", "duration": 6, "resolution": "720p", "voice": "v1" }
    Responde con el JSON que devuelva Sora (o error estructurado).
    """
    body = await request.json()
    prompt = body.get("prompt")
    if not prompt or not isinstance(prompt, str) or prompt.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Missing or invalid 'prompt' in request body."})

    try:
        result = generate_video_sora(
            prompt=prompt,
            duration=int(body.get("duration", 6)),
            resolution=body.get("resolution", "720p"),
            voice=body.get("voice")
        )
        return JSONResponse(status_code=200, content={"ok": True, "sora_response": result})
    except ValueError as ve:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=502, content={"ok": False, "error": str(e)})

# Handler global para errores
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

# Ruta de prueba rápida
@app.get("/")
def home():
    return {
        "message": "🎓 SKKU HACKEDU API corriendo!",
        "status": "online",
        "openai_configured": API_KEY is not None,
        "sora_configured": bool(SORA_API_URL and SORA_API_KEY),
        "docs": "/docs"
    }

if __name__ == "__main__":
    print("\n🚀 Iniciando SKKU HACKEDU API...")
    print("📍 Disponible en: http://127.0.0.1:8000")
    print("📚 Documentación: http://127.0.0.1:8000/docs")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)