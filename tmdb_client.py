# -*- coding: utf-8 -*-
"""
TMDb Integration - Cliente para The Movie Database API
"""

import requests
from typing import Optional, Dict, List
import time

class TMDbClient:
    """Cliente para TMDb API"""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa cliente TMDb
        
        Args:
            api_key: API key de TMDb. Si es None, usa la key configurada.
        """
        # API Key de TMDb del usuario
        self.api_key = api_key or "f48a003d6b95c16021e61ca700c88b53"
        
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        
        # Cache simple para evitar requests duplicadas
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Realiza request a TMDb API con manejo de errores"""
        
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        params['language'] = 'es-ES'  # Español
        
        # Verificar cache
        cache_key = f"{endpoint}:{str(params)}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Guardar en cache
            self.cache[cache_key] = (data, time.time())
            
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en TMDb API: {e}")
            return {}
    
    def search_movie(self, title: str, year: int = None) -> Optional[Dict]:
        """
        Busca película por título
        
        Args:
            title: Título de la película
            year: Año (opcional, mejora precisión)
        
        Returns:
            Diccionario con info de TMDb o None si no se encuentra
        """
        params = {'query': title}
        if year:
            params['year'] = year
        
        data = self._make_request('/search/movie', params)
        
        results = data.get('results', [])
        if results:
            # Retornar primer resultado
            return results[0]
        
        return None
    
    def search_tv(self, title: str, year: int = None) -> Optional[Dict]:
        """
        Busca serie por título
        
        Args:
            title: Título de la serie
            year: Año (opcional)
        
        Returns:
            Diccionario con info de TMDb o None
        """
        params = {'query': title}
        if year:
            params['first_air_date_year'] = year
        
        data = self._make_request('/search/tv', params)
        
        results = data.get('results', [])
        if results:
            return results[0]
        
        return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de una película"""
        return self._make_request(f'/movie/{tmdb_id}')
    
    def get_tv_details(self, tmdb_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de una serie"""
        return self._make_request(f'/tv/{tmdb_id}')
    
    def get_poster_url(self, poster_path: str, size: str = 'w500') -> str:
        """
        Construye URL completa para poster
        
        Args:
            poster_path: Path del poster desde TMDb
            size: Tamaño (w92, w154, w185, w342, w500, w780, original)
        
        Returns:
            URL completa del poster
        """
        if not poster_path:
            return ""
        
        return f"{self.image_base_url}/{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = 'w1280') -> str:
        """
        Construye URL completa para backdrop/background
        
        Args:
            backdrop_path: Path del backdrop desde TMDb
            size: Tamaño (w300, w780, w1280, original)
        
        Returns:
            URL completa del backdrop
        """
        if not backdrop_path:
            return ""
        
        return f"{self.image_base_url}/{size}{backdrop_path}"
    
    def match_content(self, title: str, content_type: str = 'movie', year: int = None) -> Optional[Dict]:
        """
        Busca contenido y retorna match más cercano
        
        Args:
            title: Título a buscar
            content_type: 'movie' o 'series'
            year: Año opcional
        
        Returns:
            Dict con: {tmdb_id, title, poster, backdrop, overview, ...}
        """
        if content_type == 'movie':
            result = self.search_movie(title, year)
        else:
            result = self.search_tv(title, year)
        
        if not result:
            return None
        
        # Construir objeto normalizado
        matched = {
            'tmdb_id': result.get('id'),
            'title': result.get('title') or result.get('name'),
            'original_title': result.get('original_title') or result.get('original_name'),
            'overview': result.get('overview', ''),
            'poster': self.get_poster_url(result.get('poster_path', '')),
            'backdrop': self.get_backdrop_url(result.get('backdrop_path', '')),
            'release_date': result.get('release_date') or result.get('first_air_date', ''),
            'vote_average': result.get('vote_average', 0),
            'popularity': result.get('popularity', 0)
        }
        
        return matched


# Instancia global del cliente
tmdb_client = TMDbClient()
