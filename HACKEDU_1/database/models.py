"""
Define las tablas de SQLite para usuarios y becas
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Tabla de usuarios/estudiantes"""
    __tablename__ = 'users'
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(200), nullable=False)  # 1. Nombre completo
    email = Column(String(100), unique=True, nullable=False)  # 2. Email único
    username = Column(String(50), unique=True, nullable=False)  # 3. Username único
    password = Column(String(255), nullable=False)  # 6. Contraseña (encriptada)
    
    # === INFORMACIÓN PERSONAL ===
    edad = Column(Integer, nullable=False)  # 4. Edad
    genero = Column(String(20))  # 5. Género: masculino, femenino, otro, prefiero no decir
    ciudad = Column(String(100))  # 9. Ciudad de residencia
    
    # === INFORMACIÓN ACADÉMICA ===
    objetivo_academico = Column(String(50))  # 7. Objetivo: high_school, bachelor, master, phd
    promedio_actual = Column(Float)  # 8. Promedio: 0.0 a 10.0 (o 0.0 a 4.0 según sistema)
    
    # === METADATA ===
    created_at = Column(DateTime, default=datetime.utcnow)  # Fecha de creación
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última actualización

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Scholarship(Base):
    """Tabla de becas encontradas"""
    __tablename__ = 'scholarships'
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # Nombre de la beca
    organization = Column(String(200))  # Universidad/Fundación/Gobierno
    
    # === DETALLES DE LA BECA ===
    description = Column(Text)  # Descripción completa
    amount = Column(String(50))  # Monto: "$5,000 USD" o "100% matrícula"
    deadline = Column(String(50))  # Fecha límite
    eligibility = Column(Text)  # Requisitos de elegibilidad
    url = Column(String(500))  # URL oficial de la beca
    
    # === CRITERIOS DE FILTRADO ===
    country = Column(String(50))  # País (Mexico, Global, etc)
    field_of_study = Column(String(100))  # Campo de estudio
    education_level = Column(String(50))  # Nivel educativo requerido
    
    # === SISTEMA DE RECOMENDACIÓN ===
    match_score = Column(Float)  # Score de coincidencia: 0-100
    ai_recommendation = Column(Text)  # Por qué la IA recomienda esta beca
    source = Column(String(100))  # Origen: ai_search, web_scraping, manual
    
    # === ESTADO ===
    is_active = Column(Boolean, default=True)  # Si la beca está activa
    created_at = Column(DateTime, default=datetime.utcnow)  # Fecha de creación

    def __repr__(self):
        return f"<Scholarship(id={self.id}, name='{self.name}', match_score={self.match_score})>"