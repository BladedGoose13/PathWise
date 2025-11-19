from pydantic import BaseModel, Field, validator
from typing import Optional, Dict

class TextSearchRequest(BaseModel):
    """Modelo para búsqueda de recursos de texto"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    language: str = Field(default='es', description='Código de idioma ISO 639-1')
    grade_level: str = Field(default='high_school', description='Nivel educativo')
    max_results: int = Field(default=5, ge=1, le=20)
    
    @validator('topic', always=True)
    def combine_subject_topic(cls, v, values):
        """Combina subject y topic en un solo campo de búsqueda"""
        subject = values.get('subject', '')
        
        # Si hay topic, usarlo
        if v:
            # Si también hay subject, combinarlos
            if subject:
                return f"{subject} {v}"
            return v
        
        # Si no hay topic pero sí subject, usar subject
        if subject:
            return subject
        
        # Si no hay ninguno, lanzar error
        raise ValueError('Debe proporcionar al menos subject o topic')
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "Cálculo",
                "topic": "integrales",
                "language": "es",
                "grade_level": "high_school",
                "max_results": 5
            }
        }


class GenerateStudyGuideRequest(BaseModel):
    """Modelo para generar guía de estudio"""
    topic: str = Field(..., min_length=1, description='Tema de la guía de estudio')
    class_name: str = Field(..., description='Nivel educativo o nombre de la clase')
    language: str = Field(default='es')
    preferences: Optional[Dict] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "integrales",
                "class_name": "Cálculo",
                "language": "es",
                "preferences": {
                    "include_examples": True,
                    "difficulty": "intermediate"
                }
            }
        }


class GeneratePracticeRequest(BaseModel):
    """Modelo para generar ejercicios de práctica"""
    topic: str = Field(..., min_length=1)
    class_name: str = Field(...)
    language: str = Field(default='es')
    count: int = Field(default=5, ge=1, le=10, description='Número de problemas')
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "ecuaciones cuadráticas",
                "class_name": "Álgebra",
                "language": "es",
                "count": 5
            }
        }


class GenerateQuizRequest(BaseModel):
    """Modelo para generar quiz"""
    topic: str = Field(..., min_length=1)
    class_name: str = Field(...)
    language: str = Field(default='es')
    num_questions: int = Field(default=5, ge=1, le=15, description='Número de preguntas')
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "fotosíntesis",
                "class_name": "Biología",
                "language": "es",
                "num_questions": 5
            }
        }


class VideoSearchRequest(BaseModel):
    """Modelo para búsqueda de videos educativos"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    language: str = Field(default='es')
    grade_level: str = Field(default='high_school')
    max_results: int = Field(default=5, ge=1, le=20)
    
    @validator('topic', always=True)
    def combine_subject_topic(cls, v, values):
        """Combina subject y topic en un solo campo de búsqueda"""
        subject = values.get('subject', '')
        
        if v:
            if subject:
                return f"{subject} {v}"
            return v
        
        if subject:
            return subject
        
        raise ValueError('Debe proporcionar al menos subject o topic')
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "Física",
                "topic": "cinemática",
                "language": "es",
                "grade_level": "high_school",
                "max_results": 5
            }
        }