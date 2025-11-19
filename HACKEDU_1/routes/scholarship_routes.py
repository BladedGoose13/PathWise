from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from api_integrators.scholarship_finder import ScholarshipIntegrator

router = APIRouter()
scholarship_integrator = ScholarshipIntegrator()

class StudentProfile(BaseModel):
    """Modelo del perfil del estudiante"""
    nombre: Optional[str] = Field(default="Estudiante", description="Nombre del estudiante")
    ubicacion: Optional[str] = Field(default="México", description="Ciudad, Estado")
    nivel_educativo: str = Field(..., description="Nivel: primaria, secundaria, preparatoria, universidad, posgrado")
    promedio: Optional[float] = Field(default=None, ge=6, le=10, description="Promedio escolar")
    situacion_economica: Optional[str] = Field(default=None, description="baja, media-baja, media, media-alta")
    area_interes: Optional[str] = Field(default=None, description="stem, humanidades, artes, deportes, general")
    descripcion: Optional[str] = Field(default=None, description="Información adicional del estudiante")
    
    class Config:
        schema_extra = {
            "example": {
                "nombre": "María González",
                "ubicacion": "Quechultenango, Guerrero",
                "nivel_educativo": "secundaria",
                "promedio": 8.5,
                "situacion_economica": "baja",
                "area_interes": "general",
                "descripcion": "Estudiante de secundaria en comunidad rural. No tengo proyectos escolares especiales aún, pero tengo interés en seguir estudiando."
            }
        }


@router.post("/api/scholarships/search", tags=["Scholarships"])
async def search_scholarships(
    request: Request,
    profile: StudentProfile
):
    """
    Busca becas personalizadas según el perfil del estudiante.
    
    El sistema evalúa:
    - Nivel educativo
    - Promedio académico
    - Situación económica
    - Ubicación geográfica
    - Área de interés
    - Descripción personal
    
    Retorna una lista de becas ordenadas por relevancia (match_score).
    """
    
    print(f"\n📥 Nueva búsqueda de becas:")
    print(f"   Estudiante: {profile.nombre}")
    print(f"   Ubicación: {profile.ubicacion}")
    print(f"   Nivel: {profile.nivel_educativo}")
    
    try:
        # Convertir perfil a diccionario
        perfil_dict = profile.dict()
        
        # Buscar becas compatibles
        becas = scholarship_integrator.search_scholarships(perfil_dict)
        
        # (Opcional) Generar recomendación con IA
        ai_recommendation = None
        if becas and scholarship_integrator.openai_api_key:
            ai_recommendation = scholarship_integrator.generate_ai_recommendation(
                perfil_dict, 
                becas
            )
        
        response = {
            'success': True,
            'profile': {
                'nombre': profile.nombre,
                'nivel': profile.nivel_educativo,
                'ubicacion': profile.ubicacion
            },
            'scholarships': becas,
            'total': len(becas),
            'ai_recommendation': ai_recommendation
        }
        
        print(f"✅ Retornando {len(becas)} becas\n")
        
        return response
        
    except Exception as e:
        print(f"❌ Error en búsqueda de becas: {e}")
        raise HTTPException(status_code=500, detail=f'Scholarship search failed: {str(e)}')


@router.get("/api/scholarships/all", tags=["Scholarships"])
async def get_all_scholarships():
    """
    Obtiene todas las becas disponibles en la base de datos.
    Sin filtros ni personalización.
    """
    try:
        becas = scholarship_integrator.becas_database
        
        return {
            'success': True,
            'scholarships': becas,
            'total': len(becas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to get scholarships: {str(e)}')


@router.get("/api/scholarships/{scholarship_id}", tags=["Scholarships"])
async def get_scholarship_details(scholarship_id: str):
    """
    Obtiene detalles de una beca específica por ID.
    """
    try:
        beca = next(
            (b for b in scholarship_integrator.becas_database if b['id'] == scholarship_id),
            None
        )
        
        if not beca:
            raise HTTPException(status_code=404, detail='Scholarship not found')
        
        return {
            'success': True,
            'scholarship': beca
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to get scholarship: {str(e)}')


@router.post("/api/scholarships/recommend", tags=["Scholarships"])
async def get_ai_recommendation(profile: StudentProfile):
    """
    Genera una recomendación personalizada usando IA (requiere OpenAI API key).
    """
    
    if not scholarship_integrator.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail='AI recommendation not available: OpenAI API key not configured'
        )
    
    try:
        perfil_dict = profile.dict()
        becas = scholarship_integrator.search_scholarships(perfil_dict)
        
        if not becas:
            return {
                'success': True,
                'recommendation': 'No se encontraron becas compatibles con tu perfil. Te recomendamos ampliar tu búsqueda o consultar con tu escuela sobre oportunidades locales.'
            }
        
        recommendation = scholarship_integrator.generate_ai_recommendation(
            perfil_dict,
            becas
        )
        
        return {
            'success': True,
            'recommendation': recommendation,
            'top_scholarships': becas[:3]  # Top 3 becas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'AI recommendation failed: {str(e)}')