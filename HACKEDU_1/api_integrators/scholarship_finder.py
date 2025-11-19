import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json

load_dotenv()

class ScholarshipIntegrator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Base de datos de becas (puedes expandir esto)
        self.becas_database = self._cargar_becas_database()
    
    def _cargar_becas_database(self) -> List[Dict]:
        """Carga la base de datos de becas disponibles"""
        return [
            {
                "id": "1",
                "title": "Beca Benito Juárez para el Bienestar",
                "institution": "Gobierno de México - SEP",
                "level": ["secundaria", "preparatoria"],
                "description": "Apoyo económico bimestral para estudiantes de familias en situación de pobreza. Prioriza zonas rurales e indígenas.",
                "amount": "$1,600 MXN bimestrales",
                "requirements": ["Nivel secundaria o media superior", "Situación económica vulnerable", "Inscrito en escuela pública"],
                "deadline": "Febrero - Marzo (cada ciclo escolar)",
                "url": "https://www.gob.mx/becasbenitojuarez",
                "tags": ["gobierno", "rural", "vulnerable"],
                "economic_requirement": ["baja", "media-baja"],
                "geographic_priority": ["comunidades rurales", "zonas indígenas"]
            },
            {
                "id": "2",
                "title": "Becas CONACYT",
                "institution": "CONACYT",
                "level": ["universidad", "posgrado"],
                "description": "Becas para estudiantes de alto rendimiento que deseen estudiar carreras STEM o realizar posgrados.",
                "amount": "Hasta $12,000 MXN mensuales",
                "requirements": ["Promedio mínimo 8.5", "Carrera STEM", "Admisión a institución reconocida"],
                "deadline": "Convocatorias semestrales",
                "url": "https://conahcyt.mx/becas/",
                "tags": ["stem", "alto rendimiento", "posgrado"],
                "academic_requirement": 8.5,
                "area": ["stem"]
            },
            {
                "id": "3",
                "title": "Beca BBVA México",
                "institution": "Fundación BBVA México",
                "level": ["preparatoria", "universidad"],
                "description": "Apoyo para estudiantes destacados con necesidad económica para continuar estudios de nivel medio superior y superior.",
                "amount": "Colegiatura completa + $3,000 MXN mensuales",
                "requirements": ["Promedio mínimo 8.0", "Necesidad económica", "Carta de motivos"],
                "deadline": "Mayo - Junio",
                "url": "https://www.fundacionbbva.mx/becas",
                "tags": ["privada", "alto rendimiento", "económica"],
                "economic_requirement": ["baja", "media-baja", "media"],
                "academic_requirement": 8.0
            },
            {
                "id": "4",
                "title": "Becas Jóvenes Escribiendo el Futuro",
                "institution": "Gobierno de México",
                "level": ["universidad"],
                "description": "Apoyo económico mensual para estudiantes universitarios de escuelas públicas en todo el país.",
                "amount": "$2,400 MXN mensuales",
                "requirements": ["Estudiante de universidad pública", "Mexicano", "Inscrito a tiempo completo"],
                "deadline": "Agosto - Septiembre",
                "url": "https://www.gob.mx/jovenesescribiendoelfuturo",
                "tags": ["gobierno", "universidad", "general"],
                "economic_requirement": ["baja", "media-baja", "media"]
            },
            {
                "id": "5",
                "title": "Beca PROBEM Guerrero",
                "institution": "Gobierno del Estado de Guerrero",
                "level": ["secundaria", "preparatoria", "universidad"],
                "description": "Programa de Becas Estatal para estudiantes guerrerenses de bajos recursos. Especial atención a comunidades marginadas.",
                "amount": "$800 - $2,000 MXN mensuales según nivel",
                "requirements": ["Residir en Guerrero", "Situación económica vulnerable", "Promedio mínimo 7.0"],
                "deadline": "Septiembre - Octubre",
                "url": "https://guerrero.gob.mx/becas",
                "tags": ["estatal", "guerrero", "vulnerable"],
                "economic_requirement": ["baja", "media-baja"],
                "academic_requirement": 7.0,
                "geographic_priority": ["Guerrero", "comunidades marginadas"]
            },
            {
                "id": "6",
                "title": "Becas INPI - Pueblos Indígenas",
                "institution": "Instituto Nacional de los Pueblos Indígenas",
                "level": ["secundaria", "preparatoria", "universidad"],
                "description": "Apoyo económico para estudiantes indígenas o de comunidades indígenas. Prioriza lenguas originarias.",
                "amount": "$1,500 - $4,000 MXN mensuales",
                "requirements": ["Pertenecer a comunidad indígena", "Acreditar identidad indígena", "Carta de la comunidad"],
                "deadline": "Julio - Agosto",
                "url": "https://www.gob.mx/inpi/acciones-y-programas/becas-para-estudiantes-indigenas",
                "tags": ["indígena", "comunidades", "cultural"],
                "geographic_priority": ["comunidades indígenas", "pueblos originarios"]
            },
            {
                "id": "7",
                "title": "Fundación Telmex - Becas",
                "institution": "Fundación Telmex",
                "level": ["secundaria", "preparatoria"],
                "description": "Apoyo para estudiantes de secundaria y preparatoria con buen desempeño académico en situación económica difícil.",
                "amount": "$1,000 - $1,500 MXN mensuales",
                "requirements": ["Promedio mínimo 8.0", "Necesidad económica comprobada", "Inscrito en escuela pública"],
                "deadline": "Convocatorias abiertas todo el año",
                "url": "https://www.fundaciontelmex.org/becas",
                "tags": ["privada", "secundaria", "preparatoria"],
                "economic_requirement": ["baja", "media-baja"],
                "academic_requirement": 8.0
            },
            {
                "id": "8",
                "title": "Beca Elisa Acuña - Mujeres en STEM",
                "institution": "SEP - Programa de Equidad",
                "level": ["preparatoria", "universidad"],
                "description": "Beca especial para mujeres que estudien carreras STEM (Ciencia, Tecnología, Ingeniería, Matemáticas).",
                "amount": "$3,000 MXN mensuales + Laptop",
                "requirements": ["Ser mujer", "Carrera STEM", "Promedio mínimo 8.5", "Carta de motivación"],
                "deadline": "Abril - Mayo",
                "url": "https://www.gob.mx/sep/becas-stem",
                "tags": ["mujer", "stem", "equidad"],
                "area": ["stem"],
                "academic_requirement": 8.5,
                "demographic": ["mujer"]
            }
        ]
    
    def calculate_match_score(self, beca: Dict, perfil: Dict) -> tuple[int, str]:
        """
        Calcula qué tan bien coincide una beca con el perfil del estudiante.
        Retorna (score, razón)
        """
        score = 0
        reasons = []
        
        # Verificar nivel educativo (crítico)
        if perfil.get('nivel_educativo') in beca.get('level', []):
            score += 30
            reasons.append(f"✅ Aplica para tu nivel educativo ({perfil.get('nivel_educativo')})")
        else:
            return 0, "❌ No aplica para tu nivel educativo actual"
        
        # Verificar requisitos académicos
        if 'academic_requirement' in beca:
            promedio_estudiante = perfil.get('promedio', 0)
            if promedio_estudiante >= beca['academic_requirement']:
                score += 20
                reasons.append(f"✅ Tu promedio ({promedio_estudiante}) cumple el requisito")
            else:
                score -= 15
                reasons.append(f"⚠️ Promedio mínimo requerido: {beca['academic_requirement']}")
        else:
            score += 10  # Bonus si no hay requisito de promedio
        
        # Verificar situación económica
        if 'economic_requirement' in beca and perfil.get('situacion_economica'):
            if perfil['situacion_economica'] in beca['economic_requirement']:
                score += 25
                reasons.append("✅ Tu situación económica coincide con los requisitos")
        
        # Verificar área de interés
        if 'area' in beca and perfil.get('area_interes'):
            if perfil['area_interes'] in beca['area']:
                score += 15
                reasons.append(f"✅ Beca enfocada en tu área de interés ({perfil['area_interes']})")
        
        # Verificar prioridad geográfica
        if 'geographic_priority' in beca and perfil.get('ubicacion'):
            ubicacion_lower = perfil['ubicacion'].lower()
            for prioridad in beca['geographic_priority']:
                if prioridad.lower() in ubicacion_lower or any(palabra in ubicacion_lower for palabra in prioridad.lower().split()):
                    score += 20
                    reasons.append(f"✅ Prioridad geográfica para tu ubicación ({perfil['ubicacion']})")
                    break
        
        # Verificar datos demográficos
        if 'demographic' in beca:
            # Aquí podrías agregar lógica para género, edad, etc.
            pass
        
        # Bonus si la beca es específica de su estado
        if perfil.get('ubicacion'):
            estado = perfil['ubicacion'].split(',')[-1].strip().lower()
            if estado in beca.get('institution', '').lower() or estado in ' '.join(beca.get('tags', [])).lower():
                score += 10
                reasons.append(f"✅ Beca específica para tu estado")
        
        # Bonus general por tags relevantes
        tags_relevant = ['rural', 'vulnerable', 'comunidades', 'indígena']
        perfil_descripcion = (perfil.get('descripcion') or '').lower()
        for tag in beca.get('tags', []):
            if tag in tags_relevant and any(palabra in perfil_descripcion for palabra in ['rural', 'comunidad', 'indígena', 'vulnerable']):
                score += 5
        
        # Limitar score a 100
        score = min(score, 100)
        
        reason_text = "\n".join(reasons) if reasons else "Esta beca podría ser adecuada para ti"
        
        return score, reason_text
    
    def search_scholarships(self, perfil: Dict) -> List[Dict]:
        """
        Busca y filtra becas según el perfil del estudiante.
        """
        print(f"\n{'='*60}")
        print(f"🎓 BÚSQUEDA DE BECAS PERSONALIZADA")
        print(f"   Estudiante: {perfil.get('nombre', 'Anónimo')}")
        print(f"   Ubicación: {perfil.get('ubicacion', 'No especificado')}")
        print(f"   Nivel: {perfil.get('nivel_educativo', 'No especificado')}")
        print(f"{'='*60}\n")
        
        resultados = []
        
        for beca in self.becas_database:
            score, reason = self.calculate_match_score(beca, perfil)
            
            if score > 0:  # Solo incluir becas con algún match
                beca_result = beca.copy()
                beca_result['match_score'] = score
                beca_result['why_recommended'] = reason
                resultados.append(beca_result)
                
                print(f"✅ {beca['title']}: {score}% match")
        
        # Ordenar por score descendente
        resultados.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"\n{'='*60}")
        print(f"✅ ENCONTRADAS {len(resultados)} BECAS COMPATIBLES")
        print(f"{'='*60}\n")
        
        return resultados
    
    def generate_ai_recommendation(self, perfil: Dict, becas: List[Dict]) -> str:
        """
        Usa IA (OpenAI) para generar un resumen personalizado.
        Esta función es opcional y requiere OpenAI API key.
        """
        if not self.openai_api_key:
            return None
        
        # Preparar prompt para OpenAI
        becas_str = "\n".join([f"- {b['title']}: {b['match_score']}% match" for b in becas[:5]])
        
        prompt = f"""Eres un asesor educativo experto. Un estudiante con el siguiente perfil está buscando becas:

Perfil:
- Nombre: {perfil.get('nombre')}
- Ubicación: {perfil.get('ubicacion')}
- Nivel: {perfil.get('nivel_educativo')}
- Promedio: {perfil.get('promedio', 'No especificado')}
- Situación económica: {perfil.get('situacion_economica', 'No especificado')}
- Descripción: {perfil.get('descripcion', 'No especificado')}

Becas encontradas:
{becas_str}

Genera un mensaje motivador y personalizado (máximo 150 palabras) que:
1. Reconozca su situación
2. Destaque las mejores oportunidades
3. Dé consejos prácticos para aplicar
4. Sea motivador y empático
"""
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"⚠️ No se pudo generar recomendación IA: {e}")
        
        return None