# -*- coding: utf-8 -*-
"""
Proxy Cache System for Balandro-Stremio
Manages in-memory caching of proxies with TTL
"""
import time
import threading

class ProxyCache:
    """Cache de proxies con TTL para entorno serverless"""
    
    def __init__(self):
        self._cache = {}  # {canal: {'proxies': [...], 'timestamp': timestamp}}
        self._lock = threading.Lock()
        self.TTL = 3600  # 1 hora (en segundos)
        self.MAX_CACHE_ITEMS = 50  # Límite de canales en caché
    
    def get(self, canal):
        """
        Obtiene proxies del caché si no han expirado
        
        Args:
            canal (str): Nombre del canal
            
        Returns:
            str: Lista de proxies separados por comas, o None si no hay/expiró
        """
        with self._lock:
            if canal in self._cache:
                cached_data = self._cache[canal]
                age = time.time() - cached_data['timestamp']
                
                if age < self.TTL:
                    return cached_data['proxies']
                else:
                    # Expiró, eliminar del caché
                    del self._cache[canal]
        
        return None
    
    def set(self, canal, proxies):
        """
        Guarda proxies en caché
        
        Args:
            canal (str): Nombre del canal
            proxies (str): Lista de proxies separados por comas
        """
        with self._lock:
            # Limitar tamaño del caché (FIFO simple)
            if len(self._cache) >= self.MAX_CACHE_ITEMS:
                # Eliminar el más antiguo
                oldest_canal = min(self._cache.keys(), 
                                 key=lambda k: self._cache[k]['timestamp'])
                del self._cache[oldest_canal]
            
            self._cache[canal] = {
                'proxies': proxies,
                'timestamp': time.time()
            }
    
    def clear(self, canal=None):
        """
        Limpia el caché
        
        Args:
            canal (str, optional): Canal específico a limpiar. Si es None, limpia todo
        """
        with self._lock:
            if canal:
                if canal in self._cache:
                    del self._cache[canal]
            else:
                self._cache.clear()
    
    def get_stats(self):
        """
        Obtiene estadísticas del caché
        
        Returns:
            dict: Estadísticas del caché
        """
        with self._lock:
            total = len(self._cache)
            valid = sum(1 for data in self._cache.values() 
                       if time.time() - data['timestamp'] < self.TTL)
            
            return {
                'total_entries': total,
                'valid_entries': valid,
                'expired_entries': total - valid,
                'ttl_seconds': self.TTL
            }

# Instancia global del caché
_proxy_cache = ProxyCache()

def get_proxy_cache():
    """Obtiene la instancia global del caché de proxies"""
    return _proxy_cache
