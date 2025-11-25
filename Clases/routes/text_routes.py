from fastapi import APIRouter, Request, HTTPException
from api_integrators.text_integrator import TextIntegrator
from api_integrators.ai_integrator import AIGenerator
from streaming.pdf_streamer import PDFStreamer
from cache.redis_cache import RedisCache
from utils.rate_limiter import APIRateLimiter, RateLimitException
# Usamos la ruta absoluta del paquete para evitar conflictos con otros
# módulos llamados "models" en la aplicación principal.
from Clases.models.schemas import (
    TextSearchRequest,
    GenerateStudyGuideRequest,
    GeneratePracticeRequest,
    GenerateQuizRequest,
)
import hashlib

router = APIRouter()
text_integrator = TextIntegrator()
ai_generator = AIGenerator()
cache = RedisCache()
pdf_streamer = PDFStreamer(cache)
rate_limiter = APIRateLimiter()

@router.post("/api/text/search", tags=["Text Resources"])
async def search_text_resources(
    request: Request,
    body: TextSearchRequest
):
    """
    Busca recursos de texto educativos (libros, PDFs, papers).
    
    - **subject**: Materia (opcional si se proporciona topic)
    - **topic**: Tema específico (opcional si se proporciona subject)
    - **language**: Idioma (en, es, etc.)
    - **grade_level**: Nivel educativo (middle_school, high_school, university)
    - **max_results**: Cantidad de resultados
    
    Nota: El sistema combinará automáticamente subject y topic para la búsqueda.
    Ejemplo: subject="Cálculo", topic="integrales" → busca "Cálculo integrales"
    """
    
    # Rate limiting
    try:
        rate_limiter.check_rate_limit(
            client_id=request.client.host,
            endpoint='text_search',
            max_calls=50,
            time_window=3600
        )
    except RateLimitException as e:
        raise HTTPException(status_code=429, detail=str(e))
    
    # El topic ya está combinado por el validator de Pydantic
    combined_topic = body.topic
    
    # Verifica cache
    cache_key = f"text:{body.language}:{body.grade_level}:{hashlib.md5(combined_topic.encode()).hexdigest()}"
    cached_results = cache.get_json(cache_key)
    
    if cached_results:
        return {
            'success': True,
            'results': cached_results,
            'from_cache': True,
            'query': combined_topic
        }
    
    # Busca recursos
    try:
        print(f"\n🔎 Buscando recursos de texto...")
        print(f"   Query combinada: '{combined_topic}'")
        print(f"   Idioma: {body.language}")
        print(f"   Nivel: {body.grade_level}")
        
        results = text_integrator.search_all(
            topic=combined_topic,
            language=body.language,
            grade_level=body.grade_level,
            max_results=body.max_results
        )
        
        print(f"✅ Encontrados {len(results)} recursos\n")
        
        # Guarda en cache por 2 horas
        cache.set_json(cache_key, results, ttl=7200)
        
        return {
            'success': True,
            'results': results,
            'from_cache': False,
            'query': combined_topic,
            'total': len(results)
        }
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f'Search failed: {str(e)}')

@router.post("/api/text/generate", tags=["AI Generation"])
async def generate_study_guide(
    request: Request,
    body: GenerateStudyGuideRequest
):
    """
    Genera una guía de estudio personalizada con IA.
    
    - **topic**: Tema de la guía (requerido)
    - **class_name**: Nivel educativo (requerido)
    - **language**: Idioma (en, es, etc.)
    - **preferences**: Preferencias adicionales (opcional)
    """
    
    # Rate limiting
    try:
        rate_limiter.check_rate_limit(
            client_id=request.client.host,
            endpoint='text_generation',
            max_calls=20,
            time_window=3600
        )
    except RateLimitException as e:
        raise HTTPException(status_code=429, detail=str(e))
    
    try:
        print(f"\n📚 Generando guía de estudio...")
        print(f"   Tema: {body.topic}")
        print(f"   Clase: {body.class_name}")
        
        study_guide = ai_generator.generate_study_guide(
            body.topic, 
            body.class_name, 
            body.language,
            body.preferences
        )
        
        print(f"✅ Guía generada exitosamente\n")
        
        return {
            'success': True,
            'content': study_guide,
            'format': 'markdown',
            'topic': body.topic,
            'class_name': body.class_name
        }
    except Exception as e:
        print(f"❌ Error generando guía: {e}")
        raise HTTPException(status_code=500, detail=f'Generation failed: {str(e)}')

@router.post("/api/text/practice", tags=["AI Generation"])
async def generate_practice(
    request: Request,
    body: GeneratePracticeRequest
):
    """
    Genera problemas de práctica con soluciones detalladas.
    
    - **topic**: Tema de práctica (requerido)
    - **class_name**: Nivel educativo (requerido)
    - **language**: Idioma
    - **count**: Número de problemas a generar
    """
    
    # Rate limiting
    try:
        rate_limiter.check_rate_limit(
            client_id=request.client.host,
            endpoint='practice_generation',
            max_calls=30,
            time_window=3600
        )
    except RateLimitException as e:
        raise HTTPException(status_code=429, detail=str(e))
    
    try:
        print(f"\n✏️ Generando ejercicios de práctica...")
        print(f"   Tema: {body.topic}")
        print(f"   Cantidad: {body.count}")
        
        problems = ai_generator.generate_practice_problems(
            body.topic, 
            body.class_name, 
            body.language,
            body.count
        )
        
        print(f"✅ {len(problems)} ejercicios generados\n")
        
        return {
            'success': True,
            'problems': problems,
            'count': len(problems),
            'topic': body.topic
        }
    except Exception as e:
        print(f"❌ Error generando ejercicios: {e}")
        raise HTTPException(status_code=500, detail=f'Generation failed: {str(e)}')

@router.post("/api/text/quiz", tags=["AI Generation"])
async def generate_quiz(
    request: Request,
    body: GenerateQuizRequest
):
    """
    Genera un quiz de opción múltiple.
    
    - **topic**: Tema del quiz (requerido)
    - **class_name**: Nivel educativo (requerido)
    - **language**: Idioma
    - **num_questions**: Número de preguntas
    """
    
    # Rate limiting
    try:
        rate_limiter.check_rate_limit(
            client_id=request.client.host,
            endpoint='quiz_generation',
            max_calls=20,
            time_window=3600
        )
    except RateLimitException as e:
        raise HTTPException(status_code=429, detail=str(e))
    
    try:
        print(f"\n📝 Generando quiz...")
        print(f"   Tema: {body.topic}")
        print(f"   Preguntas: {body.num_questions}")
        
        quiz = ai_generator.generate_quiz(
            body.topic, 
            body.class_name, 
            body.language,
            body.num_questions
        )
        
        print(f"✅ Quiz con {len(quiz)} preguntas generado\n")
        
        return {
            'success': True,
            'quiz': quiz,
            'total_questions': len(quiz),
            'topic': body.topic
        }
    except Exception as e:
        print(f"❌ Error generando quiz: {e}")
        raise HTTPException(status_code=500, detail=f'Generation failed: {str(e)}')

@router.get("/api/text/export/pdf", tags=["Export"])
async def export_text_to_pdf(id: str):
    """
    Exporta un recurso de texto a PDF.
    
    - **id**: ID del recurso (puede ser URL de OpenLibrary, arXiv, etc.)
    """
    
    if not id:
        raise HTTPException(status_code=400, detail='ID parameter required')
    
    try:
        # Si es una URL de OpenLibrary, redirigir al PDF
        if 'openlibrary.org' in id:
            # Convertir URL de lectura a URL de descarga
            pdf_url = id.replace('/read', '') + '.pdf'
            return {
                'success': True,
                'download_url': pdf_url,
                'message': 'Redirigiendo a OpenLibrary PDF'
            }
        
        # Si es arXiv, construir URL del PDF
        if 'arxiv.org' in id:
            # Extraer ID de arXiv
            arxiv_id = id.split('/')[-1]
            pdf_url = f'https://arxiv.org/pdf/{arxiv_id}.pdf'
            return {
                'success': True,
                'download_url': pdf_url,
                'message': 'Redirigiendo a arXiv PDF'
            }
        
        raise HTTPException(status_code=400, detail='Tipo de recurso no soportado para exportación')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Export failed: {str(e)}')

@router.get("/api/text/stream-pdf", tags=["Streaming"])
async def stream_pdf(url: str):
    """Hace streaming de PDF a través del servidor"""
    if not url:
        raise HTTPException(status_code=400, detail='URL parameter required')
    
    return pdf_streamer.stream_pdf(url)