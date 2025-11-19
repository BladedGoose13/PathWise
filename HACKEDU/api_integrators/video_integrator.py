import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class VideoIntegrator:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.vimeo_access_token = os.getenv('VIMEO_ACCESS_TOKEN')
        
        if not self.youtube_api_key:
            print("\n" + "="*70)
            print("⚠️  ADVERTENCIA: YOUTUBE_API_KEY NO CONFIGURADA")
            print("="*70)
            print("   Los videos NO funcionarán sin esta API key.")
            print("="*70 + "\n")
        else:
            print(f"✅ YouTube API configurada (key: ...{self.youtube_api_key[-4:]})")
    
    def search_youtube(self, topic: str, language: str, max_results: int = 5) -> List[Dict]:
        """
        Busca videos educativos en YouTube.
        Requiere YOUTUBE_API_KEY en .env
        """
        
        if not self.youtube_api_key:
            print("❌ No se puede buscar en YouTube: API key no configurada")
            return []
        
        url = "https://www.googleapis.com/youtube/v3/search"
        
        # Agregar término educativo según idioma
        educational_terms = {
            'es': 'tutorial',
            'en': 'tutorial',
            'fr': 'tutoriel',
            'de': 'tutorial',
            'pt': 'tutorial'
        }
        
        term = educational_terms.get(language, 'tutorial')
        enhanced_query = f"{topic} {term}"
        
        params = {
            'part': 'snippet',
            'q': enhanced_query,
            'type': 'video',
            'maxResults': max_results,
            'key': self.youtube_api_key,
            'relevanceLanguage': language,
            'safeSearch': 'strict',
            'videoEmbeddable': 'true',
            'videoSyndicated': 'true',
            'order': 'relevance'
            # NO INCLUIR: 'videoLicense': 'creativeCommon'
            # Ese filtro elimina el 99% de videos educativos
        }
        
        print(f"🔍 Buscando en YouTube: '{enhanced_query}'")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            print(f"📊 YouTube - Encontrados: {len(items)} videos")
            
            if not items:
                print("⚠️  No se encontraron videos")
                return []
            
            results = []
            for item in items:
                # Validar que tenga video_id
                video_id = item.get('id', {}).get('videoId')
                if not video_id:
                    print(f"⚠️  Item sin video_id, saltando")
                    continue
                
                snippet = item.get('snippet', {})
                
                # Construir URLs correctas
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                
                # Obtener thumbnail
                thumbnails = snippet.get('thumbnails', {})
                thumbnail = (
                    thumbnails.get('high', {}).get('url') or
                    thumbnails.get('medium', {}).get('url') or
                    thumbnails.get('default', {}).get('url') or
                    ''
                )
                
                result = {
                    'source': 'youtube',
                    'video_id': video_id,
                    'title': snippet.get('title', 'Sin título'),
                    'description': snippet.get('description', ''),
                    'channel': snippet.get('channelTitle', 'Canal desconocido'),
                    'thumbnail': thumbnail,
                    'published_at': snippet.get('publishedAt', ''),
                    'url': video_url,
                    'embed_url': embed_url,
                    'platform': 'YouTube',
                    'type': 'video'
                }
                
                print(f"   ✅ Video: {result['title'][:60]}...")
                print(f"      URL: {video_url}")
                
                results.append(result)
            
            print(f"✅ YouTube devolvió {len(results)} videos válidos\n")
            return results
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"❌ Error 403: Verifica tu YouTube API key y cuota")
                print(f"   Respuesta: {e.response.text[:200]}")
            elif e.response.status_code == 400:
                print(f"❌ Error 400: Parámetros de búsqueda inválidos")
                print(f"   Respuesta: {e.response.text[:200]}")
            else:
                print(f"❌ YouTube HTTP error {e.response.status_code}: {e}")
            return []
        except Exception as e:
            print(f"❌ YouTube API error: {e}")
            return []
    
    def search_vimeo(self, topic: str, language: str, max_results: int = 5) -> List[Dict]:
        """
        Busca videos educativos en Vimeo (opcional).
        Requiere VIMEO_ACCESS_TOKEN en .env
        """
        
        if not self.vimeo_access_token:
            return []
        
        url = "https://api.vimeo.com/videos"
        headers = {
            'Authorization': f'Bearer {self.vimeo_access_token}'
        }
        
        educational_query = f"{topic} education"
        
        params = {
            'query': educational_query,
            'filter': 'CC',
            'per_page': max_results,
            'sort': 'relevant'
        }
        
        print(f"🔍 Buscando en Vimeo: '{educational_query}'")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('data', [])
            print(f"📊 Vimeo - Encontrados: {len(items)} videos")
            
            results = []
            for item in items:
                video_id = item['uri'].split('/')[-1]
                
                pictures = item.get('pictures', {}).get('sizes', [])
                thumbnail = pictures[2]['link'] if len(pictures) > 2 else ''
                
                result = {
                    'source': 'vimeo',
                    'video_id': video_id,
                    'title': item.get('name', 'Sin título'),
                    'description': item.get('description', ''),
                    'url': item.get('link', ''),
                    'embed_url': item.get('player_embed_url', ''),
                    'thumbnail': thumbnail,
                    'platform': 'Vimeo',
                    'type': 'video'
                }
                
                results.append(result)
            
            print(f"✅ Vimeo devolvió {len(results)} resultados\n")
            return results
            
        except Exception as e:
            print(f"❌ Vimeo API error: {e}")
            return []
    
    def search_all(self, topic: str, language: str = 'es', grade_level: str = 'high_school', 
                   max_results: int = 5) -> List[Dict]:
        """
        Busca videos educativos en todas las plataformas disponibles.
        
        Prioridad:
        1. YouTube (principal fuente)
        2. Vimeo (si está configurado)
        3. Otras plataformas de video
        """
        
        print(f"\n{'='*70}")
        print(f"🚀 BÚSQUEDA DE VIDEOS INICIADA")
        print(f"   Tema: {topic}")
        print(f"   Idioma: {language}")
        print(f"   Nivel: {grade_level}")
        print(f"   Max resultados: {max_results}")
        print(f"{'='*70}\n")
        
        results = []
        
        # 1. Buscar en YouTube (principal)
        if self.youtube_api_key:
            youtube_results = self.search_youtube(topic, language, max_results)
            results.extend(youtube_results)
            print(f"📚 Agregados {len(youtube_results)} videos de YouTube\n")
        else:
            print("⚠️  YouTube API no disponible\n")
        
        # 2. Si no hay suficientes, buscar en Vimeo
        if len(results) < max_results and self.vimeo_access_token:
            remaining = max_results - len(results)
            vimeo_results = self.search_vimeo(topic, language, remaining)
            results.extend(vimeo_results)
            print(f"📚 Agregados {len(vimeo_results)} videos de Vimeo\n")
        
        # Validar que todos tengan URL
        valid_results = []
        for result in results:
            if result.get('url'):
                valid_results.append(result)
            else:
                print(f"⚠️  Resultado sin URL descartado: {result.get('title', 'Sin título')}")
        
        # Limitar al máximo solicitado
        final_results = valid_results[:max_results]
        
        print(f"{'='*70}")
        print(f"✅ BÚSQUEDA COMPLETADA")
        print(f"   Total válidos: {len(valid_results)}")
        print(f"   Devolviendo: {len(final_results)} videos")
        print(f"{'='*70}\n")
        
        if not final_results:
            print("⚠️  ADVERTENCIA: No se encontraron videos.")
            if not self.youtube_api_key:
                print("   → Configura YOUTUBE_API_KEY en .env")
            print("   → Verifica tu conexión a internet")
            print("   → Intenta con otros términos de búsqueda\n")
        
        return final_results