import time
import requests
from typing import Optional, Tuple

class HTTPClient:
    """Cliente HTTP robusto con reintentos y backoff exponencial"""
    
    def __init__(self, max_retries: int = 3, base_backoff: float = 1.5, timeout: int = 30):
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.timeout = timeout
    
    def post_with_retry(self, url: str, *, headers=None, params=None, data=None, json=None, 
                       retry_on: Tuple[int, ...] = (429, 500, 502, 503, 504)) -> Optional[requests.Response]:
        """
        Realiza petición POST con reintentos automáticos
        
        Args:
            url: URL destino
            headers: Headers de la petición
            params: Parámetros URL
            data: Datos del cuerpo
            json: Datos JSON
            retry_on: Códigos de estado para reintentar
            
        Returns:
            Response object o None si falla después de todos los reintentos
        """
        last_response = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, 
                    headers=headers, 
                    params=params, 
                    data=data, 
                    json=json, 
                    timeout=self.timeout
                )
                
                # Éxito - no reintentar
                if response.status_code < 400:
                    return response
                
                # Error del cliente (excepto 429) - no reintentar
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    return response
                
                # Error del servidor o 429 - reintentar
                if response.status_code in retry_on:
                    last_response = response
                    print(f"⚠️  Intento {attempt + 1}/{self.max_retries} falló con código {response.status_code}. Reintentando...")
                else:
                    return response
                    
            except requests.RequestException as e:
                last_response = e
                print(f"⚠️  Intento {attempt + 1}/{self.max_retries} falló con excepción: {e}. Reintentando...")
            
            # Backoff exponencial: 1.5^0=1s, 1.5^1=1.5s, 1.5^2=2.25s...
            wait_time = self.base_backoff ** attempt
            time.sleep(wait_time)
        
        print(f"❌ Todos los {self.max_retries} reintentos fallaron")
        return last_response