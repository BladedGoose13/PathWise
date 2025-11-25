import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

class TextIntegrator:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        
        # Mapeo de idiomas
        self.language_map = {
            'en': ['en', 'eng', 'english'],
            'es': ['es', 'spa', 'spanish', 'español'],
            'fr': ['fr', 'fre', 'fra', 'french', 'français'],
            'de': ['de', 'ger', 'deu', 'german', 'deutsch'],
            'it': ['it', 'ita', 'italian', 'italiano'],
            'pt': ['pt', 'por', 'portuguese', 'português'],
            'zh': ['zh', 'chi', 'zho', 'chinese'],
            'ja': ['ja', 'jpn', 'japanese'],
            'ko': ['ko', 'kor', 'korean'],
            'ar': ['ar', 'ara', 'arabic'],
            'ru': ['ru', 'rus', 'russian'],
        }
    
    def normalize_language(self, language: str) -> List[str]:
        """Convierte código de idioma a todas sus variantes"""
        language_lower = language.lower()
        if language_lower in self.language_map:
            return self.language_map[language_lower]
        return [language_lower]
    
    def matches_language(self, doc_languages: List[str], target_language: str) -> bool:
        """Verifica si el documento coincide con el idioma buscado"""
        if not doc_languages:
            return True
        
        if not isinstance(doc_languages, list):
            doc_languages = [doc_languages]
        
        doc_languages_lower = [lang.lower().strip() for lang in doc_languages if lang]
        target_variants = self.normalize_language(target_language)
        
        for variant in target_variants:
            if any(variant in doc_lang or doc_lang in variant for doc_lang in doc_languages_lower):
                return True
        
        return False
    
    def search_openlibrary(self, topic: str, language: str, max_results: int = 5) -> List[Dict]:
        """Busca libros educativos en OpenLibrary"""
        url = "https://openlibrary.org/search.json"
        
        params = {
            'q': topic,
            'limit': max_results * 2,  # Buscar más para filtrar después
            'has_fulltext': 'true'
        }
        
        print(f"🔍 Buscando: '{topic}'")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            total_found = data.get('numFound', 0)
            docs = data.get('docs', [])
            print(f"📊 OpenLibrary - Total encontrados: {total_found}, Docs: {len(docs)}")
            
            results = []
            for doc in docs:
                if not doc.get('has_fulltext'):
                    continue
                
                key = doc.get('key', '')
                doc_languages = doc.get('language', [])
                
                # Filtrar por idioma
                if not self.matches_language(doc_languages, language):
                    continue
                
                title = doc.get('title', 'Sin título')
                author = ', '.join(doc.get('author_name', ['Desconocido']))
                year = doc.get('first_publish_year', 'N/A')
                
                # Crear descripción con lo que tengamos
                subjects = doc.get('subject', [])[:3]  # Primeros 3 temas
                description = f"Temas: {', '.join(subjects)}" if subjects else "Libro educativo disponible en OpenLibrary"
                
                result = {
                    'source': 'openlibrary',
                    'id': key.replace('/works/', ''),
                    'title': title,
                    'author': author,
                    'url': f"https://openlibrary.org{key}",
                    'read_url': f"https://openlibrary.org{key}",
                    'year': year,
                    'type': 'book',
                    'languages': doc_languages if doc_languages else ['unknown'],
                    'description': description,
                    'content': f"""📚 {title}
👤 Autor: {author}
📅 Año: {year}
🌐 Idiomas: {', '.join(doc_languages[:3]) if doc_languages else 'No especificado'}

📖 Descripción:
{description}

🔗 Este libro está disponible en OpenLibrary para lectura online.
👉 Haz clic en "Leer en OpenLibrary" abajo para acceder al contenido completo.

💡 OpenLibrary es una biblioteca digital gratuita con millones de libros.
   Puedes leer este libro directamente en tu navegador sin necesidad de descarga.
"""
                }
                
                print(f"✅ Libro: {title} ({year})")
                results.append(result)
                
                if len(results) >= max_results:
                    break
            
            print(f"✅ OpenLibrary devolvió {len(results)} resultados\n")
            return results
            
        except Exception as e:
            print(f"❌ OpenLibrary API error: {e}")
            return []
    
    def search_arxiv(self, topic: str, language: str, max_results: int = 5) -> List[Dict]:
        """Busca papers académicos en arXiv"""
        url = "http://export.arxiv.org/api/query"
        
        params = {
            'search_query': f'all:{topic}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        print(f"🔍 Buscando en arXiv: '{topic}'")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', namespace)
            
            print(f"📊 arXiv - Encontrados: {len(entries)} papers")
            
            results = []
            for entry in entries:
                title = entry.find('atom:title', namespace).text.strip()
                summary = entry.find('atom:summary', namespace).text.strip()
                paper_id = entry.find('atom:id', namespace).text
                
                # Limpiar el summary (remover saltos de línea excesivos)
                summary_clean = ' '.join(summary.split())
                
                pdf_link = entry.find('atom:link[@title="pdf"]', namespace)
                pdf_url = pdf_link.get('href') if pdf_link is not None else ''
                
                # Extraer arXiv ID
                arxiv_id = paper_id.split('/')[-1]
                
                result = {
                    'source': 'arxiv',
                    'id': arxiv_id,
                    'title': title,
                    'summary': summary_clean[:500] + '...' if len(summary_clean) > 500 else summary_clean,
                    'url': paper_id,
                    'pdf_url': pdf_url,
                    'type': 'paper',
                    'content': f"""📄 {title}

📋 Resumen:
{summary_clean}

🔗 Paper completo: {paper_id}
📥 PDF: {pdf_url if pdf_url else 'No disponible'}

💡 Este es un paper académico de arXiv, una plataforma de pre-publicaciones científicas.
"""
                }
                
                print(f"✅ Paper: {title[:60]}...")
                results.append(result)
            
            print(f"✅ arXiv devolvió {len(results)} resultados\n")
            return results
            
        except Exception as e:
            print(f"❌ arXiv API error: {e}")
            return []
    
    def search_educational_pdfs(self, topic: str, language: str, max_results: int = 5) -> List[Dict]:
        """Busca PDFs educativos usando Google Custom Search"""
        
        if not self.google_api_key or not self.google_cse_id:
            print(f"⚠️  Google Custom Search no configurado, saltando...")
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        educational_terms = " (lecture OR tutorial OR \"course\" OR \"lecture notes\" OR syllabus OR tutorial OR \"teaching material\" OR \"study guide\")"
        query = f"{topic}{educational_terms}"
        
        params = {
            'key': os.getenv('GOOGLE_API_KEY'),
            'cx': self.google_cse_id,
            'q': query,
            'num': max_results,
            'lr': f'lang_{language}'
        }
        
        print(f"🔍 Buscando en Google: '{topic}'")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            print(f"📊 Google - Encontrados: {len(items)}")
            
            results = []
            for item in items:
                pdf_url = item.get('link', '')
                
                result = {
                    'source': 'google',
                    'id': pdf_url,
                    'title': item.get('title', 'Sin título'),
                    'snippet': item.get('snippet', ''),
                    'url': pdf_url,
                    'pdf_url': pdf_url,
                    'type': 'pdf',
                    'content': f"""📄 {item.get('title', 'Sin título')}

📝 Vista previa:
{item.get('snippet', 'No disponible')}

🔗 Enlace directo al PDF:
{pdf_url}

💡 Este es un material encontrado en sitios educativos.
   Puedes descargarlo haciendo clic en el enlace de arriba.
"""
                }
                
                results.append(result)
            
            print(f"✅ Google devolvió {len(results)} PDFs\n")
            return results
            
        except Exception as e:
            print(f"❌ Google Custom Search error: {e}")
            return []
    
    def search_all(self, topic: str, language: str, grade_level: str, max_results: int = 5) -> List[Dict]:
    
        """Busca recursos de texto en múltiples plataformas sin priorizar una sobre otra.
        Ejecuta búsquedas en paralelo y devuelve una mezcla intercalada (round-robin)."""
        print(f"\n{'='*60}")
        print(f"🚀 BÚSQUEDA DE TEXTO INICIADA (sin prioridad fija)")
        print(f"   Tema: {topic}  Idioma: {language}  Nivel: {grade_level}  Max: {10}")
        print(f"{'='*60}\n")

        # lanzar todas las búsquedas en paralelo (cada función ya filtra si no está configurada)
        with ThreadPoolExecutor(max_workers=3) as ex:
            future_map = {
                ex.submit(self.search_arxiv, topic, language, max_results): 'arxiv',
                ex.submit(self.search_openlibrary, topic, language, max_results): 'openlibrary',        
                ex.submit(self.search_educational_pdfs, topic, language, max_results): 'google'
            }
            results_by_source = {'All': [], 'arxiv': [], 'openlibrary': [], 'google': []}
            for fut in as_completed(future_map):
                src = future_map[fut]
                try:
                    results_by_source[src] = fut.result() or []
                except Exception as e:
                    print(f"⚠️ Error en búsqueda {src}: {e}")
                    results_by_source[src] = []

        # Opcional: remover fuentes vacías y tomar un orden inicial aleatorio para evitar sesgo
        available_sources = [k for k, v in results_by_source.items() if v]
        if not available_sources:
            return []

        random.shuffle(available_sources)

        # Intercalar resultados (round-robin) y deduplicar por URL/ID
        iterators = {s: iter(results_by_source[s]) for s in available_sources}
        final_results = []
        seen = set()

        while len(final_results) < max_results and iterators:
            for s in list(available_sources):  # list() porque podemos modificar available_sources dentro
                if s not in iterators:
                    continue
                try:
                    item = next(iterators[s])
                    uid = item.get('url') or item.get('id') or item.get('pdf_url') or None
                    if uid and uid in seen:
                        continue
                    if uid:
                        seen.add(uid)
                    final_results.append(item)
                    if len(final_results) >= max_results:
                        break
                except StopIteration:
                    # fuente agotada -> eliminarla
                    available_sources.remove(s)
                    iterators.pop(s, None)
            # si quedaron fuentes pero ya no producen, salimos
            if not available_sources:
                break

        print(f"✅ BÚSQUEDA COMPLETADA (sin prioridad). Devolviendo {len(final_results)} recursos\n")
        return final_results