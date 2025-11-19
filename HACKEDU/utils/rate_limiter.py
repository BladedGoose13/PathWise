
import time
from typing import Dict

class APIRateLimiter:
    def __init__(self):
        self.calls: Dict[str, list] = {}
    
    def check_rate_limit(self, client_id: str, endpoint: str, max_calls: int, time_window: int):
        """
        Verifica si el cliente puede hacer otra llamada
        
        Args:
            client_id: IP del cliente
            endpoint: Nombre del endpoint (ej: 'video_search')
            max_calls: Máximo de llamadas permitidas
            time_window: Ventana de tiempo en segundos
        """
        now = time.time()
        key = f"{client_id}:{endpoint}"
        
        # Inicializa si no existe
        if key not in self.calls:
            self.calls[key] = []
        
        # Limpia timestamps viejos (fuera de la ventana)
        window_start = now - time_window
        self.calls[key] = [ts for ts in self.calls[key] if ts > window_start]
        
        # Verifica límite
        if len(self.calls[key]) >= max_calls:
            wait_time = int(self.calls[key][0] - window_start + 1)
            raise RateLimitException(
                f"Rate limit exceeded for {endpoint}. Try again in {wait_time} seconds."
            )
        
        # Agrega timestamp actual
        self.calls[key].append(now)

class RateLimitException(Exception):
    """Excepción personalizada para rate limit"""
    pass
