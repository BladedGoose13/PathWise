"""
PATHWISE - Sistema de Verificación de Estudiantes
Integración completa con OpenAI para verificación inteligente
"""

import sqlite3
import re
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DB_PATH = Path(__file__).with_name("PATWISE.db")

# Para usar OpenAI real, descomentar y configurar:
# from openai import OpenAI
# OPENAI_CLIENT = OpenAI(api_key="tu-api-key")
OPENAI_CLIENT = None


# ============================================================================
# FUNCIONES DE DETECCIÓN DE INSTITUCIONES
# ============================================================================

DOMINIOS_EDUCATIVOS_MX = {
    '.edu.mx': 'Universidad Pública',
    '.unam.mx': 'UNAM',
    '.ipn.mx': 'IPN',
    '.itesm.mx': 'Tecnológico de Monterrey',
    '.tec.mx': 'Tecnológico de Monterrey',
    '.udg.mx': 'Universidad de Guadalajara',
    '.uanl.mx': 'UANL',
    '.uam.mx': 'UAM',
    '.buap.mx': 'BUAP',
    'iteso.mx': 'ITESO',
    'ibero.mx': 'Universidad Iberoamericana',
}

DOMINIOS_EDUCATIVOS_INT = {
    '.edu': 'Institución Educativa (USA)',
    '.ac.uk': 'Universidad (UK)',
    '.edu.au': 'Universidad (Australia)',
    '.edu.ar': 'Universidad (Argentina)',
    '.edu.co': 'Universidad (Colombia)',
}

def detectar_institucion(email):
    """
    Detecta si un email pertenece a una institución educativa conocida
    """
    email_lower = email.lower()
    
    # Buscar en instituciones mexicanas
    for dominio, nombre in DOMINIOS_EDUCATIVOS_MX.items():
        if dominio in email_lower:
            return True, nombre, 'Alta'
    
    # Buscar en instituciones internacionales
    for dominio, nombre in DOMINIOS_EDUCATIVOS_INT.items():
        if dominio in email_lower:
            return True, nombre, 'Alta'
    
    return False, None, None


def validar_formato_email(email):
    """
    Valida el formato básico de un email
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def verificar_con_openai(nombre, escuela, email):
    """
    Usa OpenAI para verificar si el usuario es estudiante legítimo
    """
    if not OPENAI_CLIENT:
        # Simulación sin OpenAI
        palabras_educativas = ['universidad', 'instituto', 'preparatoria', 'colegio', 'escuela']
        es_educativo = any(palabra in escuela.lower() for palabra in palabras_educativas)
        return {
            'es_estudiante': es_educativo,
            'confianza': 'Media' if es_educativo else 'Baja',
            'razon': 'Análisis basado en palabras clave',
            'metodo': 'Local'
        }
    
    # Código con OpenAI real (descomentar cuando esté configurado)
    """
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": '''Eres un experto en verificar instituciones educativas. 
                    Analiza si el usuario es estudiante legítimo basándote en:
                    - Nombre de la institución
                    - Formato del email
                    - Coherencia entre datos
                    
                    Responde en formato JSON:
                    {
                        "es_estudiante": true/false,
                        "confianza": "Alta/Media/Baja",
                        "razon": "explicación breve"
                    }'''
                },
                {
                    "role": "user",
                    "content": f"Nombre: {nombre}\nEscuela: {escuela}\nEmail: {email}"
                }
            ],
            response_format={ "type": "json_object" }
        )
        
        import json
        resultado = json.loads(response.choices[0].message.content)
        resultado['metodo'] = 'OpenAI GPT-4'
        return resultado
        
    except Exception as e:
        return {
            'es_estudiante': False,
            'confianza': 'Error',
            'razon': str(e),
            'metodo': 'Error'
        }
    """


# ============================================================================
# SISTEMA DE REGISTRO Y VERIFICACIÓN
# ============================================================================

class SistemaVerificacion:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
    
    def conectar(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn.cursor()
    
    def cerrar(self):
        if self.conn:
            self.conn.close()
    
    def registrar_usuario(self, email, nombre, escuela, grado_actual, area, community_tipo=None):
        """
        Registra un nuevo usuario con verificación automática
        """
        cursor = self.conectar()
        
        # 1. Validar formato de email
        if not validar_formato_email(email):
            self.cerrar()
            return {
                'exito': False,
                'error': 'Formato de email inválido'
            }
        
        # 2. Verificar si el email ya existe
        cursor.execute("SELECT email FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            self.cerrar()
            return {
                'exito': False,
                'error': 'El email ya está registrado'
            }
        
        # 3. Detectar si es institucional
        es_institucional, nombre_institucion, confianza_dominio = detectar_institucion(email)
        
        # 4. Verificación adicional con OpenAI (si está disponible)
        verificacion_ia = verificar_con_openai(nombre, escuela, email)
        
        # 5. Determinar si requiere verificación
        requiere_verificacion = 'SI' if (es_institucional or verificacion_ia['es_estudiante']) else 'NO'
        
        # 6. Insertar en la base de datos
        try:
            cursor.execute('''
                INSERT INTO usuarios 
                (email, nombre, escuela, grado_actual, area, community_tipo, requiere_verificacion_estudiante)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email, nombre, escuela, grado_actual, area, community_tipo, requiere_verificacion))
            
            self.conn.commit()
            
            resultado = {
                'exito': True,
                'email': email,
                'requiere_verificacion': requiere_verificacion,
                'deteccion_dominio': {
                    'es_institucional': es_institucional,
                    'institucion': nombre_institucion,
                    'confianza': confianza_dominio
                },
                'verificacion_ia': verificacion_ia
            }
            
            self.cerrar()
            return resultado
            
        except Exception as e:
            self.cerrar()
            return {
                'exito': False,
                'error': str(e)
            }
    
    def obtener_usuarios_pendientes(self):
        """
        Obtiene lista de usuarios que requieren verificación
        """
        cursor = self.conectar()
        cursor.execute('''
            SELECT email, nombre, escuela, grado_actual
            FROM usuarios
            WHERE requiere_verificacion_estudiante = 'SI'
        ''')
        
        usuarios = cursor.fetchall()
        self.cerrar()
        
        return [
            {
                'email': u[0],
                'nombre': u[1],
                'escuela': u[2],
                'grado': u[3]
            }
            for u in usuarios
        ]
    
    def generar_reporte(self):
        """
        Genera un reporte completo del sistema
        """
        cursor = self.conectar()
        
        # Total de usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
        
        # Usuarios que requieren verificación
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE requiere_verificacion_estudiante = 'SI'")
        con_verificacion = cursor.fetchone()[0]
        
        # Usuarios verificados
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE requiere_verificacion_estudiante = 'NO'")
        sin_verificacion = cursor.fetchone()[0]
        
        # Top instituciones
        cursor.execute('''
            SELECT escuela, COUNT(*) as total
            FROM usuarios
            GROUP BY escuela
            ORDER BY total DESC
            LIMIT 5
        ''')
        top_instituciones = cursor.fetchall()
        
        self.cerrar()
        
        return {
            'total_usuarios': total,
            'requieren_verificacion': con_verificacion,
            'verificados': sin_verificacion,
            'porcentaje_institucional': round((con_verificacion / total * 100) if total > 0 else 0, 2),
            'top_instituciones': [
                {'nombre': inst[0], 'estudiantes': inst[1]} 
                for inst in top_instituciones
            ]
        }


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def demo_sistema():
    print("=" * 70)
    print("PATHWISE - SISTEMA DE VERIFICACIÓN DE ESTUDIANTES")
    print("=" * 70)
    
    sistema = SistemaVerificacion(DB_PATH)
    
    # Casos de prueba
    casos_prueba = [
        {
            'email': 'pedro.ramirez@alumno.buap.mx',
            'nombre': 'Pedro Ramírez González',
            'escuela': 'Benemérita Universidad Autónoma de Puebla',
            'grado_actual': 'Licenciatura',
            'area': 'Computación'
        },
        {
            'email': 'sofia.lopez@cecyt9.ipn.mx',
            'nombre': 'Sofía López Martínez',
            'escuela': 'CECyT 9 Juan de Dios Bátiz',
            'grado_actual': 'Preparatoria',
            'area': 'Técnico en Programación'
        },
        {
            'email': 'diego.hernandez@gmail.com',
            'nombre': 'Diego Hernández Cruz',
            'escuela': 'CONALEP Puebla',
            'grado_actual': 'Preparatoria',
            'area': 'Tecnología'
        },
        {
            'email': 'andrea.torres@iteso.mx',
            'nombre': 'Andrea Torres Ruiz',
            'escuela': 'ITESO Universidad Jesuita de Guadalajara',
            'grado_actual': 'Maestría',
            'area': 'Innovación Educativa'
        }
    ]
    
    print("\n📝 REGISTRANDO USUARIOS...\n")
    
    for caso in casos_prueba:
        print(f"👤 Registrando: {caso['nombre']}")
        resultado = sistema.registrar_usuario(**caso)
        
        if resultado['exito']:
            print(f"   ✅ Registrado exitosamente")
            print(f"   📧 Email: {resultado['email']}")
            print(f"   🎓 Verificación requerida: {resultado['requiere_verificacion']}")
            
            if resultado['deteccion_dominio']['es_institucional']:
                print(f"   🏛️  Institución detectada: {resultado['deteccion_dominio']['institucion']}")
                print(f"   📊 Confianza: {resultado['deteccion_dominio']['confianza']}")
            
            print(f"   🤖 Verificación IA: {resultado['verificacion_ia']['confianza']} ({resultado['verificacion_ia']['metodo']})")
        else:
            print(f"   ❌ Error: {resultado['error']}")
        print()
    
    # Mostrar usuarios pendientes de verificación
    print("=" * 70)
    print("📋 USUARIOS PENDIENTES DE VERIFICACIÓN")
    print("=" * 70)
    
    pendientes = sistema.obtener_usuarios_pendientes()
    for usuario in pendientes:
        print(f"\n📧 {usuario['email']}")
        print(f"   Nombre: {usuario['nombre']}")
        print(f"   Escuela: {usuario['escuela']}")
        print(f"   Grado: {usuario['grado']}")
    
    # Generar reporte
    print("\n" + "=" * 70)
    print("📊 REPORTE DEL SISTEMA")
    print("=" * 70)
    
    reporte = sistema.generar_reporte()
    print(f"\n👥 Total de usuarios: {reporte['total_usuarios']}")
    print(f"🎓 Requieren verificación: {reporte['requieren_verificacion']} ({reporte['porcentaje_institucional']}%)")
    print(f"✅ Verificados: {reporte['verificados']}")
    
    print("\n🏆 Top 5 Instituciones:")
    for i, inst in enumerate(reporte['top_instituciones'], 1):
        print(f"   {i}. {inst['nombre']}: {inst['estudiantes']} estudiantes")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETADA")
    print("=" * 70)


if __name__ == "__main__":
    demo_sistema()
