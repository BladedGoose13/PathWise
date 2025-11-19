"""
Video routes - Con integración completa de Sora
Convertido de Flask a FastAPI
Modelo actualizado: sora-2 (Noviembre 2025)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import hashlib

# Importaciones
try:
    from api_integrators.video_integrator import VideoIntegrator
    from api_integrators.ai_integrator import AIGenerator
    from api_integrators.video_generator import VideoGenerator
    from streaming.video_streamer import VideoStreamer
    from cache.redis_cache import RedisCache
except ImportError as e:
    print(f"⚠️ Importación opcional no disponible: {e}")
    VideoIntegrator = None
    AIGenerator = None
    VideoGenerator = None
    VideoStreamer = None
    RedisCache = None

router = APIRouter()

# Inicializar servicios (solo si existen)
video_integrator = VideoIntegrator() if VideoIntegrator else None
ai_generator = AIGenerator() if AIGenerator else None
video_generator = VideoGenerator() if VideoGenerator else None
video_streamer = VideoStreamer() if VideoStreamer else None
cache = RedisCache() if RedisCache else None


# ==========================================
# MODELOS PYDANTIC
# ==========================================

class VideoSearchRequest(BaseModel):
    """Búsqueda de videos existentes"""
    topic: str = Field(..., description="Tema a buscar")
    max_results: Optional[int] = Field(5, ge=1, le=20, description="Número máximo de resultados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python programming",
                "max_results": 5
            }
        }


class ScriptGenerateRequest(BaseModel):
    """Generación de script educativo"""
    topic: str = Field(..., description="Tema del script")
    class_name: str = Field(..., description="Nombre de la clase")
    duration: Optional[int] = Field(300, ge=60, le=600, description="Duración en segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Introduction to Machine Learning",
                "class_name": "AI 101",
                "duration": 300
            }
        }


class SoraVideoRequest(BaseModel):
    """Generación de video con Sora desde un script"""
    script: str = Field(..., description="Script del video")
    topic: str = Field(..., description="Tema principal")
    style: Optional[str] = Field("educational", description="Estilo: educational, cinematic, animated, realistic, minimalist, dynamic")
    aspect_ratio: Optional[str] = Field("16:9", description="Ratio: 16:9, 9:16, 1:1, 4:3")
    quality: Optional[str] = Field("standard", description="Calidad: standard, hd")
    duration: Optional[int] = Field(None, ge=10, le=60, description="Duración en segundos (máx 60)")
    multi_scene: Optional[bool] = Field(False, description="Dividir en múltiples escenas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "script": "# Python Basics\n\nPython is a powerful language...",
                "topic": "Python Programming",
                "style": "educational",
                "aspect_ratio": "16:9",
                "quality": "standard",
                "duration": 60,
                "multi_scene": False
            }
        }


class FullVideoGenerationRequest(BaseModel):
    """Generación completa: Script + Video"""
    topic: str = Field(..., description="Tema del video")
    class_name: str = Field(..., description="Nombre de la clase")
    duration: Optional[int] = Field(300, ge=60, le=600, description="Duración del script")
    style: Optional[str] = Field("educational", description="Estilo visual del video")
    aspect_ratio: Optional[str] = Field("16:9", description="Aspect ratio")
    multi_scene: Optional[bool] = Field(False, description="Dividir en escenas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Introduction to Neural Networks",
                "class_name": "Deep Learning 101",
                "duration": 300,
                "style": "educational",
                "aspect_ratio": "16:9",
                "multi_scene": False
            }
        }


# ==========================================
# ENDPOINTS - VIDEO SEARCH
# ==========================================

@router.post("/api/videos/search", tags=["Videos"])
async def search_videos(body: VideoSearchRequest):
    """
    🔍 Busca videos educativos en múltiples plataformas
    
    - Busca en YouTube, Vimeo, etc.
    - Usa cache para resultados recientes
    - Retorna metadata completa de cada video
    """
    
    if not body.topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    # Check cache
    if cache:
        cache_key = f"videos:{hashlib.md5(body.topic.encode()).hexdigest()}"
        cached_results = cache.get_json(cache_key)
        
        if cached_results:
            return {
                'success': True,
                'results': cached_results,
                'from_cache': True,
                'count': len(cached_results)
            }
    
    # Search videos
    try:
        if not video_integrator:
            # Datos de ejemplo
            results = [
                {
                    "title": f"Tutorial: {body.topic}",
                    "url": "https://www.youtube.com/watch?v=example",
                    "duration": "10:30",
                    "platform": "YouTube",
                    "thumbnail": "https://via.placeholder.com/480x360"
                }
            ]
        else:
            results = video_integrator.search_all(body.topic, body.max_results)
        
        # Cache results
        if cache:
            cache.set_json(cache_key, results, ttl=3600)
        
        return {
            'success': True,
            'results': results,
            'from_cache': False,
            'count': len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Search failed: {str(e)}')


@router.post("/api/videos/generate", tags=["Videos"])
async def generate_video_script(body: ScriptGenerateRequest):
    """
    📝 Genera un script educativo con IA (GPT-4)
    
    **Siguiente paso:** Usa POST /api/videos/sora/generate
    """
    
    if not body.topic or not body.class_name:
        raise HTTPException(status_code=400, detail="Topic and class_name are required")
    
    try:
        if not ai_generator:
            script = f"""# {body.topic}

## Bienvenidos a {body.class_name}

Hoy exploraremos {body.topic}.

## Contenido Principal
[Contenido generado por IA]

## Conclusión
Resumen de {body.topic}.

Duración: {body.duration}s
"""
        else:
            script = ai_generator.generate_video_script(
                body.topic,
                body.class_name,
                body.duration
            )
        
        return {
            'success': True,
            'script': script,
            'metadata': {
                'topic': body.topic,
                'class_name': body.class_name,
                'duration': body.duration
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Generation failed: {str(e)}')


@router.post("/api/videos/sora/generate", tags=["Videos - Sora"])
async def generate_with_sora(body: SoraVideoRequest):
    """
    🎬 Genera VIDEO con Sora (modelo: sora-2)
    
    **Proceso:**
    1. Script → Prompts visuales (GPT-4)
    2. Prompts → Video (Sora API - intentará llamada REAL)
    3. Retorna URL del video generado
    
    **Estilos disponibles:**
    - educational: Limpio, profesional, estilo aula
    - cinematic: Cinematográfico, dramático
    - animated: Animaciones 3D coloridas
    - realistic: Fotorealista, documental
    - minimalist: Minimalista, enfocado
    - dynamic: Dinámico, energético
    
    **Aspect Ratios:**
    - 16:9: Widescreen (YouTube, presentaciones)
    - 9:16: Vertical (TikTok, Instagram Stories)
    - 1:1: Cuadrado (Instagram posts)
    - 4:3: Estándar (proyectores)
    
    **IMPORTANTE:** Intentará hacer llamada REAL a Sora API.
    Si la API no está disponible, simulará la respuesta con placeholder.
    """
    
    if not video_generator:
        raise HTTPException(
            status_code=503,
            detail="Sora not available. Check OPENAI_API_KEY in .env"
        )
    
    try:
        if body.multi_scene:
            result = video_generator.generate_multi_scene_video(
                script=body.script,
                topic=body.topic,
                style=body.style
            )
        else:
            result = video_generator.generate_video_from_script(
                script=body.script,
                topic=body.topic,
                style=body.style,
                aspect_ratio=body.aspect_ratio,
                quality=body.quality,
                duration=body.duration
            )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Video generation failed: {str(e)}')


@router.post("/api/videos/full-generation", tags=["Videos - Sora"])
async def full_generation(body: FullVideoGenerationRequest):
    """
    🚀 GENERACIÓN COMPLETA: Script + Video en UN SOLO endpoint
    
    **Flujo automático:**
    1. 📝 Genera script educativo con GPT-4
    2. 🎨 Convierte script a prompts visuales
    3. 🎬 Genera video con Sora (modelo: sora-2)
    4. ✅ Retorna todo junto
    
    **Ventajas:**
    - ⚡ Proceso automático de principio a fin
    - 🎯 Un solo endpoint para todo el workflow
    - 📊 Información completa en la respuesta
    
    **Modelo:** sora-2 (Noviembre 2025)
    **Status:** Intentará llamada REAL a API, fallback a simulación si necesario
    """
    
    try:
        # Generar script
        if not ai_generator:
            script = f"# {body.topic}\n\nContenido sobre {body.topic} para {body.class_name}."
        else:
            script = ai_generator.generate_video_script(
                body.topic,
                body.class_name,
                body.duration
            )
        
        # Generar video
        if not video_generator:
            raise HTTPException(status_code=503, detail="Video generator unavailable")
        
        if body.multi_scene:
            video_result = video_generator.generate_multi_scene_video(
                script=script,
                topic=body.topic,
                style=body.style
            )
        else:
            video_result = video_generator.generate_video_from_script(
                script=script,
                topic=body.topic,
                style=body.style,
                aspect_ratio=body.aspect_ratio
            )
        
        return {
            'success': True,
            'message': 'Video generado completamente',
            'script': script,
            'video': video_result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Full generation failed: {str(e)}')


@router.get("/api/videos/stream", tags=["Videos"])
async def stream_video(url: str = Query(..., description="URL del video a streamear")):
    """
    📺 Stream de video a través del servidor
    
    Útil para videos con restricciones CORS
    """
    
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    try:
        if not video_streamer:
            return {'success': True, 'redirect_url': url}
        return video_streamer.stream_video(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/videos/health", tags=["Videos"])
async def health_check():
    """
    🏥 Health check de todos los servicios de video
    
    Verifica estado de:
    - Video search (YouTube, etc.)
    - AI script generator (GPT-4)
    - Sora video generator
    - Video streamer
    - Cache system
    """
    return {
        'success': True,
        'services': {
            'video_search': video_integrator is not None,
            'ai_generator': ai_generator is not None,
            'sora_generator': video_generator is not None,
            'streamer': video_streamer is not None,
            'cache': cache is not None
        },
        'sora_info': {
            'model': 'sora-2',
            'api_status': 'attempting real API calls',
            'fallback': 'simulation if API unavailable',
            'note': 'Real Sora API call will be attempted. Check server logs for details.'
        },
        'status': 'operational'
    }