from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserProfileCreate(BaseModel):
    """Schema para crear un perfil de usuario"""
    nombre_completo: str = Field(..., min_length=3, max_length=200, example="María González Pérez")
    email: EmailStr = Field(..., example="maria@example.com")
    username: str = Field(..., min_length=3, max_length=50, example="mariagp21")
    password: str = Field(..., min_length=8, example="MiPassword123!")
    edad: int = Field(..., ge=15, le=100, example=21)
    genero: str = Field(..., example="femenino")  # masculino, femenino, otro, prefiero no decir
    ciudad: str = Field(..., max_length=100, example="Ciudad de México")
    objetivo_academico: str = Field(..., example="bachelor")  # high_school, bachelor, master, phd
    promedio_actual: float = Field(..., ge=0.0, le=10.0, example=8.5)

    class Config:
        json_schema_extra = {
            "example": {
                "nombre_completo": "Juan Pérez López",
                "email": "juan@example.com",
                "username": "juanp",
                "password": "SecurePass123!",
                "edad": 22,
                "genero": "masculino",
                "estado": "Jalisco",
                "objetivo_academico": "bachelor",
                "promedio_actual": 9.2
            }
        }

class UserRegister(BaseModel):
    """Schema para registrar usuario"""
    nombre_completo: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    edad: int = Field(..., ge=15, le=100)
    genero: str
    ciudad: str = Field(..., max_length=100)
    objetivo_academico: str
    promedio_actual: float = Field(..., ge=0.0, le=10.0)


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Schema para actualizar perfil (todos opcionales)"""
    nombre_completo: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    edad: Optional[int] = Field(None, ge=15, le=100)
    genero: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    objetivo_academico: Optional[str] = None
    promedio_actual: Optional[float] = Field(None, ge=0.0, le=10.0)


class ScholarshipSearchRequest(BaseModel):
    """Schema para buscar becas"""
    user_id: int = Field(..., description="ID del usuario", example=1)
    num_scholarships: int = Field(default=10, ge=1, le=50, example=10)
    refresh: bool = Field(default=False, example=False)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "num_scholarships": 10,
                "refresh": False
            }
        }