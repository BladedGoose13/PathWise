import requests
import hashlib
from fastapi import HTTPException
from fastapi.responses import Response
from typing import Optional
import io

class PDFStreamer:
    def __init__(self, cache_manager):
        self.cache = cache_manager
    
    def stream_pdf(self, pdf_url: str) -> Response:
        """Stream PDF through your server with caching"""
        cache_key = f"pdf:{hashlib.md5(pdf_url.encode()).hexdigest()}"
        
        # Check cache first
        cached_pdf = self.cache.get(cache_key)
        if cached_pdf:
            return Response(
                content=cached_pdf,
                media_type='application/pdf',
                headers={'Content-Disposition': 'inline'}
            )
        
        # Download PDF
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            pdf_data = response.content
            
            # Cache for 24 hours
            self.cache.set(cache_key, pdf_data, ttl=86400)
            
            return Response(
                content=pdf_data,
                media_type='application/pdf',
                headers={'Content-Disposition': 'inline'}
            )
        except Exception as e:
            print(f"PDF streaming error: {e}")
            # En lugar de Response con status=500, lanzamos HTTPException para FastAPI
            raise HTTPException(status_code=500, detail=f"Error streaming PDF: {str(e)}")
    
    def download_and_cache_pdf(self, pdf_url: str) -> Optional[bytes]:
        """Download PDF and return bytes"""
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"PDF download error: {e}")
            return None