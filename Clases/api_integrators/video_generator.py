"""
Video Generator usando Sora de OpenAI
Estructura oficial: openai.Video.create()
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Optional
import json
from datetime import datetime

load_dotenv()


class SoraVideoGenerator:
    """Generador de videos con Sora API (Estructura Oficial)"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env")
        
        print(f"✅ API Key detectada: {self.api_key[:15]}...{self.api_key[-4:]}")
        
        # Inicializar cliente de OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self.model = "sora-2"
    
    def generate_video_from_script(
        self,
        script: str,
        topic: str,
        style: str = "educational",
        aspect_ratio: str = "16:9",
        quality: str = "standard",
        duration: Optional[int] = None
    ) -> Dict:
        """
        Genera un video usando Sora a partir de un script
        
        Args:
            script: Script educativo
            topic: Tema del video
            style: Estilo visual
            aspect_ratio: Ratio (16:9, 9:16, 1:1)
            quality: Calidad (standard, hd)
            duration: Duración en segundos (máx 60)
        
        Returns:
            Dict con información del video generado
        """
        
        print(f"\n{'='*60}")
        print(f"🎬 GENERACIÓN DE VIDEO CON SORA")
        print(f"{'='*60}")
        print(f"📚 Tema: {topic}")
        print(f"🎨 Estilo: {style}")
        print(f"🤖 Modelo: {self.model}")
        print(f"📐 Aspect Ratio: {aspect_ratio}")
        print(f"⏱️  Duración: {duration or 60}s")
        print(f"{'='*60}\n")
        
        # Validar duración
        if duration and duration > 60:
            print(f"⚠️ Duración {duration}s excede el máximo, usando 60s")
            duration = 60
        
        # Paso 1: Convertir script a prompt visual
        print("📝 Paso 1/3: Convirtiendo script a prompt visual...")
        visual_prompt = self._script_to_visual_prompt(script, topic, style)
        print(f"✅ Prompt visual generado ({len(visual_prompt)} chars)")
        print(f"   Preview: {visual_prompt[:100]}...\n")
        
        # Paso 2: Generar video con Sora
        print("🎬 Paso 2/3: Generando video con Sora API...")
        video_result = self._call_sora_api(
            prompt=visual_prompt,
            aspect_ratio=aspect_ratio,
            quality=quality,
            duration=duration or 60
        )
        
        if video_result.get('success'):
            print("✅ Video generado exitosamente!\n")
        else:
            print(f"❌ Error: {video_result.get('error')}\n")
        
        # Paso 3: Preparar respuesta
        print("📦 Paso 3/3: Preparando respuesta...")
        
        result = {
            'success': video_result.get('success', False),
            'video_url': video_result.get('video_url'),
            'video_id': video_result.get('video_id'),
            'prompt': visual_prompt,
            'script': script,
            'metadata': {
                'topic': topic,
                'style': style,
                'aspect_ratio': aspect_ratio,
                'quality': quality,
                'duration': video_result.get('duration', duration or 60),
                'generated_at': datetime.now().isoformat(),
                'model': self.model
            }
        }
        
        if not video_result.get('success'):
            result['error'] = video_result.get('error')
            result['note'] = video_result.get('note')
        
        print(f"{'='*60}")
        print(f"✅ PROCESO COMPLETADO")
        print(f"{'='*60}\n")
        
        return result
    
    def _script_to_visual_prompt(
        self,
        script: str,
        topic: str,
        style: str
    ) -> str:
        """Convierte un script educativo en un prompt visual para Sora"""
        
        style_descriptions = {
            'educational': 'clean modern classroom with soft lighting, whiteboard with diagrams, professional educational aesthetic',
            'cinematic': 'dramatic lighting, smooth camera movements, cinematic composition, professional cinematography',
            'animated': 'colorful 3D animations, playful characters, vibrant backgrounds, cartoon style',
            'realistic': 'photorealistic scenes, natural environments, documentary style, real-world settings',
            'minimalist': 'simple clean backgrounds, focused on content, minimal distractions',
            'dynamic': 'energetic transitions, fast-paced visuals, engaging motion graphics'
        }
        
        style_desc = style_descriptions.get(style, style_descriptions['educational'])
        
        system_prompt = f"""Eres un experto en convertir scripts educativos en prompts visuales para Sora.

Crea un prompt visual detallado (SOLO VISUALES, no diálogos).

Estilo: {style}
Descripción: {style_desc}

Reglas:
1. Descripción visual clara y específica
2. Incluir: escenografía, colores, movimientos de cámara
3. NO incluir diálogos ni texto
4. Máximo 500 caracteres
5. Lenguaje cinematográfico

Ejemplo:
"A modern classroom with natural lighting. Camera pans across whiteboard with colorful diagrams about {topic}. 3D models rotate in foreground. Professional educational aesthetic."
"""
        
        script_preview = script[:1500] if len(script) > 1500 else script
        
        user_message = f"""Script:
---
{script_preview}
---

Tema: {topic}

Genera prompt visual para Sora (máx 500 chars):"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            visual_prompt = response.choices[0].message.content.strip()
            
            # Limitar a 500 caracteres
            if len(visual_prompt) > 500:
                visual_prompt = visual_prompt[:497] + "..."
            
            return visual_prompt
        
        except Exception as e:
            print(f"⚠️ Error generando prompt con GPT-4: {e}")
            print("🔄 Usando prompt genérico...")
            return f"An educational video about {topic}. {style_desc}. Smooth camera movements, clear visuals, professional lighting."[:500]
    
    def _call_sora_api(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        quality: str = "standard",
        duration: int = 60
    ) -> Dict:
        """
        Llama a la API de Sora usando la estructura oficial
        openai.Video.create()
        """
        
        print(f"🔑 Usando API Key: {self.api_key[:15]}...")
        print(f"🎯 Modelo: {self.model}")
        print(f"📝 Prompt: {prompt[:100]}...")
        print(f"📐 Aspect Ratio: {aspect_ratio}")
        print(f"💎 Quality: {quality}")
        print(f"⏱️  Duration: {duration}s")
        
        try:
            print(f"\n📤 Llamando a openai.Video.create()...")
            
            # Estructura oficial de Sora API
            video = self.client.videos.generate(
                model=self.model,
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                quality=quality
            )
            
            print("✅ Respuesta recibida de Sora API!")
            
            # Procesar respuesta con diferentes estructuras posibles
            video_url = None
            video_id = None

            if hasattr(video, "url"):
                # Caso: la respuesta tiene url directa
                video_url = video.url
                video_id = getattr(video, "id", None)

            elif hasattr(video, "data"):
                # Caso: la respuesta viene en .data[]
                video_data = video.data[0] if isinstance(video.data, list) else video.data
                video_url = getattr(video_data, "url", None)
                video_id = getattr(video_data, "id", None)

            else:
                # Caso genérico: intentar convertir a dict
                video_dict = video.model_dump() if hasattr(video, "model_dump") else dict(video)
                video_url = video_dict.get("url") or video_dict.get("video_url")
                video_id = video_dict.get("id") or video_dict.get("video_id")

            # 🔹 Ajuste clave:
            # Si no hay video_url pero sí hay video_id,
            # construimos la URL interna de la API de OpenAI.
            if not video_url and video_id:
                video_url = f"https://api.openai.com/v1/videos/{video_id}"

            if not video_url:
                print(f"⚠️ No se encontró URL en la respuesta")
                print(f"Respuesta: {video}")
                return {
                    "success": False,
                    "error": "No video URL in response",
                    "raw_response": str(video)
                }
            
            print(f"📹 Video URL: {video_url}")
            print(f"🆔 Video ID: {video_id}")
            
            return {
                "success": True,
                "video_url": video_url,
                "video_id": video_id,
                "duration": duration,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "quality": quality,
                "model": self.model
            }
        
        except AttributeError as e:
            error_msg = str(e)
            print(f"❌ AttributeError: {error_msg}")
            
            if "has no attribute 'videos'" in error_msg:
                return {
                    "success": False,
                    "error": "videos.generate not available in OpenAI SDK",
                    "note": "Try updating: pip install --upgrade openai",
                    "suggestion": "Or use: pip install openai>=1.50.0"
                }
            
            return {
                "success": False,
                "error": f"AttributeError: {error_msg}"
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error llamando a Sora API: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "note": "Check if your OpenAI SDK supports video generation"
            }
    
    def generate_multi_scene_video(
        self,
        script: str,
        topic: str,
        style: str = "educational"
    ) -> Dict:
        """Genera video multi-escena"""
        
        print(f"\n{'='*60}")
        print(f"🎬 GENERACIÓN MULTI-ESCENA")
        print(f"{'='*60}\n")
        
        # Por ahora, generar video único
        # TODO: Implementar división en escenas
        print("ℹ️  Multi-scene aún no implementado, generando video único...")
        
        return self.generate_video_from_script(
            script=script,
            topic=topic,
            style=style,
            duration=60
        )


# Función helper
def generate_educational_video(
    script: str,
    topic: str,
    style: str = "educational",
    aspect_ratio: str = "16:9",
    multi_scene: bool = False
) -> Dict:
    """Función simplificada para generar videos"""
    
    generator = SoraVideoGenerator()
    
    if multi_scene:
        return generator.generate_multi_scene_video(script, topic, style)
    else:
        return generator.generate_video_from_script(
            script, topic, style, aspect_ratio
        )


if __name__ == "__main__":
    # Test
    sample_script = """
    # Introduction to Python
    
    Python is a powerful programming language.
    
    ## Key Features
    - Easy to learn
    - Versatile
    - Great community
    """
    
    result = generate_educational_video(
        script=sample_script,
        topic="Python Programming Basics",
        style="educational",
        aspect_ratio="16:9"
    )
    
    print("\n" + "="*60)
    print("📹 RESULTADO FINAL")
    print("="*60)
    print(json.dumps(result, indent=2))
