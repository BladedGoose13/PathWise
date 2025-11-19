import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

class AIGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Modelo de IA para generación de texto
        self.text_model = "gpt-4o"  
        self.temperature = 0.3
        self.max_tokens = 4000
    
    def generate_study_guide(self, topic: str, class_name: str, language: str, 
                           preferences: Optional[Dict] = None) -> str:
        f"""Genera una guía de estudio completa personalizada en lenguaje {language}"""
        if preferences is None:
            preferences = {}
        
        format_type = preferences.get('format', 'structured notes')
        difficulty = preferences.get('difficulty', 'medium')
        learning_style = preferences.get('learning_style', 'visual')
        
        system_msg = """Eres un experto creador de contenido educativo que se especializa 
        en hacer temas complejos accesibles para estudiantes de todos los niveles. 
        Crea contenido claro, atractivo y pedagógicamente sólido. Siempre incluye ejemplos
        prácticos y ejercicios con soluciones."""
        
        prompt = f"""
        Crea una guía de estudio completa para estudiantes de {class_name} sobre el tema: {topic}
        
        Formato: {format_type}
        Nivel de dificultad: {difficulty}
        Estilo de aprendizaje: {learning_style}
        Idioma: {language}
        
        DEBE incluir:
        1. Introducción clara al tema
        2. Conceptos clave explicados paso a paso
        3. 5 ejemplos resueltos con explicación detallada
        4. 10 problemas de práctica (con respuestas al final)
        5. Descripciones visuales (diagramas, tablas, gráficos)
        6. Resumen de puntos clave
        7. Errores comunes y cómo evitarlos
        8. Tips para recordar el contenido
        
        Hazlo atractivo y fácil de entender para nivel {class_name}.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error en generación de guía: {e}")
            return f"Error al generar contenido: {str(e)}"
    
    def generate_video_script(self, topic: str, class_name: str, language: str, 
                            duration: int = 300) -> str:
        """Genera un guión para video educativo"""
        
        system_msg = """Eres un guionista de videos educativos experto. Creas scripts 
        dinámicos, claros y atractivos que mantienen la atención del estudiante."""
        
        prompt = f"""
        Crea un guión de video educativo de {duration} segundos para estudiantes de {class_name} 
        sobre el tema: {topic}
        Idioma: {language}
        
        El guión DEBE tener:
        
        [0:00-0:30] GANCHO/INTRODUCCIÓN
        - Pregunta intrigante o dato sorprendente
        - Por qué este tema es importante
        
        [0:30-4:00] CONTENIDO PRINCIPAL
        - 3 puntos clave bien explicados
        - Ejemplos visuales para cada punto
        - Analogías del mundo real
        - Transiciones suaves entre secciones
        
        [4:00-5:00] CONCLUSIÓN
        - Resumen rápido de lo aprendido
        - Aplicación práctica
        - Call-to-action (practicar, explorar más)
        
        Para cada sección, especifica:
        - [TIMESTAMP] 
        - NARRACIÓN: Lo que dice el narrador
        - VISUAL: Lo que se muestra en pantalla
        - TEXTO EN PANTALLA: Puntos clave a destacar
        
        Mantén un tono amigable y motivador.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error en generación de script: {e}")
            return f"Error al generar guión: {str(e)}"
    
    def generate_practice_problems(self, topic: str, class_name: str, language: str,
                                  count: int = 10) -> str:
        """Genera problemas de práctica con soluciones detalladas"""
        
        system_msg = """Eres un profesor experto creando ejercicios de práctica. 
        Tus problemas son claros, progresivos en dificultad, y las soluciones 
        son pedagógicas (enseñan el proceso, no solo la respuesta)."""
        
        prompt = f"""
        Crea {count} problemas de práctica para estudiantes de {class_name} sobre {topic}.
        
        Idioma: {language}
        Para CADA problema (numerado del 1 al {count}):
        
        **Problema [N]:** [Enunciado claro del problema]
        
        **Nivel:** [Fácil/Medio/Difícil]
        
        **Solución paso a paso:**
        - Paso 1: [Explicación]
        - Paso 2: [Explicación]
        - Paso 3: [Explicación]
        - ...
        
        **Respuesta final:** [Resultado]
        
        **Concepto evaluado:** [Qué habilidad/concepto se practica]
        
        **Error común:** [Qué error suelen cometer los estudiantes aquí]
        
        ---
        
        IMPORTANTE:
        - Problemas 1-3: Nivel fácil (aplicación directa)
        - Problemas 4-7: Nivel medio (requieren varios pasos)
        - Problemas 8-10: Nivel difícil (aplicación creativa)
        
        Varía los tipos de problemas para cubrir diferentes aspectos del tema.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error en generación de problemas: {e}")
            return f"Error al generar problemas: {str(e)}"
    
    def generate_quiz(self, topic: str, class_name: str, language: str,
                     num_questions: int = 10) -> Dict:
        """Genera un quiz de opción múltiple"""
        
        system_msg = """Eres un experto en crear evaluaciones educativas. 
        Tus preguntas son claras, justas, y evalúan comprensión real."""
        
        prompt = f"""
        Crea un quiz de {num_questions} preguntas de opción múltiple para {class_name} 
        sobre {topic}.
        
        Tiene que tener 10 preguntas, cada una con 4 opciones (A, B, C, D) y solo UNA respuesta correcta.
        Proporciona explicaciones detalladas para la respuesta correcta e incorrectas.
        
        Idioma: {language}
        
        Para cada pregunta, responde en formato JSON:
        
        {{
          "question": "Texto de la pregunta",
          "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
          "correct_answer": "A",
          "explanation": "Por qué A es correcta y las otras no"
        }}
        
        Reglas:
        - Distractores plausibles (no obviamente incorrectos)
        - Una sola respuesta claramente correcta
        - Explicaciones educativas (no solo "porque sí")
        - Progresión de dificultad
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error en generación de quiz: {e}")
            return {"error": str(e)}

app = FastAPI(
    title="CLASES_API",
    description="API educativa con IA - Textos, Videos, Guías de estudio y más",
    version="1.0.0"
)

# CORS - permitir tu frontend local (o "*" solo en dev)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    # agregar otros orígenes si hace falta
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # o ["*"] para desarrollo rápido
    allow_credentials=True,
    allow_methods=["*"],        # permite GET, POST, OPTIONS, ...
    allow_headers=["*"],        # permite Content-Type, Authorization, ...
)
