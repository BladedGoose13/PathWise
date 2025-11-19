"""
Maneja todas las operaciones de la base de datos SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, User, Scholarship
from typing import Optional, List, Dict
import json
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path: str = "database/scholarships.db"):
        """
        Inicializa la conexión a SQLite
        """
        # Asegurar que la carpeta database existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        print(f"✅ Base de datos inicializada: {db_path}")
    
    def get_session(self) -> Session:
        """Obtiene una nueva sesión de base de datos"""
        return self.SessionLocal()
    
    # ==================== OPERACIONES DE USUARIOS ====================
    
    def create_user(self, user_data: Dict) -> User:
        """Crea un nuevo usuario en la base de datos"""
        session = self.get_session()
        try:
            user = User(**user_data)
            session.add(user)
            session.commit()
            session.refresh(user)
            
            print(f"✅ Usuario creado: {user.nombre_completo} (ID: {user.id})")
            return user
        except Exception as e:
            session.rollback()
            print(f"❌ Error creando usuario: {e}")
            raise
        finally:
            session.close()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return user
        finally:
            session.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            return user
        finally:
            session.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por username"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user
        finally:
            session.close()
    
    def get_all_users(self) -> List[User]:
        """Obtiene todos los usuarios"""
        session = self.get_session()
        try:
            users = session.query(User).all()
            return users
        finally:
            session.close()
    
    def update_user(self, user_id: int, user_data: Dict) -> Optional[User]:
        """Actualiza un usuario existente"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key) and key != 'password':  # No actualizar password directamente
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(user)
                print(f"✅ Usuario actualizado: {user.nombre_completo}")
            return user
        except Exception as e:
            session.rollback()
            print(f"❌ Error actualizando usuario: {e}")
            raise
        finally:
            session.close()
        
    def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                print(f"✅ Usuario eliminado: ID {user_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Error eliminando usuario: {e}")
            raise
        finally:
            session.close()
    
    # ==================== OPERACIONES DE BECAS ====================
    
    def save_scholarship(self, scholarship_data: Dict) -> Scholarship:
        """Guarda una beca en la base de datos"""
        session = self.get_session()
        try:
            scholarship = Scholarship(**scholarship_data)
            session.add(scholarship)
            session.commit()
            session.refresh(scholarship)
            return scholarship
        except Exception as e:
            session.rollback()
            print(f"❌ Error guardando beca: {e}")
            raise
        finally:
            session.close()
    
    def save_scholarships(self, scholarships: List[Dict]) -> List[Scholarship]:
        """Guarda múltiples becas en la base de datos"""
        session = self.get_session()
        try:
            saved = []
            for sch_data in scholarships:
                scholarship = Scholarship(**sch_data)
                session.add(scholarship)
                saved.append(scholarship)
            session.commit()
            
            print(f"✅ {len(saved)} becas guardadas en la BD")
            return saved
        except Exception as e:
            session.rollback()
            print(f"❌ Error guardando becas: {e}")
            raise
        finally:
            session.close()
    
    def get_scholarship(self, scholarship_id: int) -> Optional[Scholarship]:
        """Obtiene una beca por ID"""
        session = self.get_session()
        try:
            return session.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        finally:
            session.close()
    
    def get_all_scholarships(self, active_only: bool = True) -> List[Scholarship]:
        """Obtiene todas las becas"""
        session = self.get_session()
        try:
            query = session.query(Scholarship)
            if active_only:
                query = query.filter(Scholarship.is_active == True)
            return query.all()
        finally:
            session.close()
    
    def get_user_scholarships(self, user_id: int, limit: int = 10) -> List[Scholarship]:
        """
        Obtiene becas recomendadas para un usuario específico
        Filtra por país, campo de estudio y nivel educativo
        Ordena por match_score descendente
        """
        session = self.get_session()
        try:
            user = self.get_user(user_id)
            if not user:
                return []
            
            # Construir query con filtros
            query = session.query(Scholarship).filter(Scholarship.is_active == True)
            
            # Filtrar por país (si está definido)
            if user.country:
                query = query.filter(
                    (Scholarship.country == user.country) | 
                    (Scholarship.country == 'Global')
                )
            
            # Filtrar por campo de estudio (si está definido)
            if user.field_of_study:
                query = query.filter(
                    Scholarship.field_of_study.like(f"%{user.field_of_study}%")
                )
            
            # Filtrar por nivel educativo (si está definido)
            if user.education_level:
                query = query.filter(
                    (Scholarship.education_level == user.education_level) |
                    (Scholarship.education_level == 'Any')
                )
            
            # Ordenar por match_score descendente
            scholarships = query.order_by(Scholarship.match_score.desc()).limit(limit).all()
            
            print(f"📚 {len(scholarships)} becas encontradas para {user.name}")
            return scholarships
        finally:
            session.close()
    
    def deactivate_scholarship(self, scholarship_id: int) -> bool:
        """Desactiva una beca (marca como inactiva)"""
        session = self.get_session()
        try:
            scholarship = session.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
            if scholarship:
                scholarship.is_active = False
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Error desactivando beca: {e}")
            raise
        finally:
            session.close()
    
    # ==================== CONVERSIÓN A DICCIONARIOS ====================
    
    def user_to_dict(self, user: User) -> Dict:
        """Convierte objeto User a diccionario para JSON"""
        return {
            'id': user.id,
            'nombre_completo': user.nombre_completo,
            'email': user.email,
            'username': user.username,
            # NO incluir password en el dict (seguridad)
            'edad': user.edad,
            'genero': user.genero,
            'ciudad': user.ciudad,
            'objetivo_academico': user.objetivo_academico,
            'promedio_actual': user.promedio_actual,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
    
    def scholarship_to_dict(self, scholarship: Scholarship) -> Dict:
        """Convierte objeto Scholarship a diccionario para JSON"""
        return {
            'id': scholarship.id,
            'name': scholarship.name,
            'organization': scholarship.organization,
            'description': scholarship.description,
            'amount': scholarship.amount,
            'deadline': scholarship.deadline,
            'eligibility': scholarship.eligibility,
            'url': scholarship.url,
            'country': scholarship.country,
            'field_of_study': scholarship.field_of_study,
            'education_level': scholarship.education_level,
            'match_score': scholarship.match_score,
            'ai_recommendation': scholarship.ai_recommendation,
            'source': scholarship.source,
            'is_active': scholarship.is_active,
            'created_at': scholarship.created_at.isoformat() if scholarship.created_at else None
        }
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas generales de la base de datos"""
        session = self.get_session()
        try:
            total_users = session.query(User).count()
            total_scholarships = session.query(Scholarship).count()
            active_scholarships = session.query(Scholarship).filter(Scholarship.is_active == True).count()
            
            return {
                'total_users': total_users,
                'total_scholarships': total_scholarships,
                'active_scholarships': active_scholarships
            }
        finally:
            session.close()