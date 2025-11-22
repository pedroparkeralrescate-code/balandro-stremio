# -*- coding: utf-8 -*-
"""
platformcode.config module
"""
import os
import tempfile
import sys

__addon_name = "Balandro"
__addon_version = "1.0.0"

class WebErrorException(Exception):
    """Excepción personalizada para errores web"""
    pass

# Almacenamiento global de settings
_settings = {}
_channel_settings = {}

# Proxies públicos gratuitos por defecto (rotativos)
DEFAULT_PROXIES = {
    'cuevana3': '',  # Probar sin proxy primero
    'pelispedia': '',
    'gnula': '',
    'cinecalidad': '',
    'hdfull': '',
    'cuevana3video': '',
    'pelismart': '',
    'jkanime': '',
    'animeflv': '',
    'animefenix': ''
}

def get_setting(key, channel=None, default=None):
    """Get a setting value"""
    if channel and key == 'proxies':
        # Buscar en configuración del canal
        if channel in _channel_settings and key in _channel_settings[channel]:
            return _channel_settings[channel][key]
        
        # Buscar en caché de proxies
        from platformcode.proxy_cache import get_proxy_cache
        cache = get_proxy_cache()
        cached_proxies = cache.get(channel)
        if cached_proxies:
            return cached_proxies
        
        # Si no hay proxies, iniciar búsqueda automática
        if channel in DEFAULT_PROXIES and DEFAULT_PROXIES[channel] == '':
            # Trigger búsqueda automática de proxies
            print(f'[CONFIG] No hay proxies para {channel}, iniciando búsqueda automática...')
            
            try:
                from core import proxytools
                # Buscar proxies en background (no bloqueante)
                success = proxytools.buscar_proxies_automatico(channel)
                
                if success:
                    # Devolver los proxies recién encontrados
                    if channel in _channel_settings and key in _channel_settings[channel]:
                        proxies = _channel_settings[channel][key]
                        # Guardar en caché
                        cache.set(channel, proxies)
                        return proxies
            except Exception as e:
                print(f'[CONFIG] Error en búsqueda automática de proxies: {e}')
        
        # Retornar proxy por defecto si existe
        if channel in DEFAULT_PROXIES:
            return DEFAULT_PROXIES[channel]
    
    # Buscar en settings globales
    if key in _settings:
        return _settings[key]
    
    # Variables de entorno como fallback
    return os.environ.get(key, default)


def set_setting(key, value, channel=None):
    """Set a setting value"""
    if channel:
        if channel not in _channel_settings:
            _channel_settings[channel] = {}
        _channel_settings[channel][key] = value
    else:
        _settings[key] = value

def get_addon_version():
    """Get addon version"""
    return __addon_version

def get_data_path():
    """Get data path for cookies and cache"""
    # Usar directorio temporal para serverless
    data_path = os.path.join(tempfile.gettempdir(), 'balandro_data')
    if not os.path.exists(data_path):
        try:
            os.makedirs(data_path)
        except:
            pass
    return data_path

# Implementar get_runtime_path para httptools
def get_runtime_path():
    """Get runtime path"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Capturar las variables de módulo ANTES de la definición de clase para evitar name mangling
_ADDON_NAME = __addon_name
_ADDON_VERSION = __addon_version

# Crear una clase Config para que httptools pueda acceder a config.__addon_name
class Config:
    """Config object that exposes addon metadata"""
    
    def __init__(self):
        # Usar setattr para evitar name mangling, usando las variables capturadas
        setattr(self, '__addon_name', _ADDON_NAME)
        setattr(self, '__addon_version', _ADDON_VERSION)
    
    def get_setting(self, key, channel=None, default=None):
        return get_setting(key, channel, default)
    
    def set_setting(self, key, value, channel=None):
        return set_setting(key, value, channel)
    
    def get_addon_version(self):
        return get_addon_version()
    
    def get_data_path(self):
        return get_data_path()
    
    def get_runtime_path(self):
        return get_runtime_path()

# Hacer que el módulo mismo tenga estos atributos
sys.modules[__name__].__addon_name = __addon_name
sys.modules[__name__].__addon_version = __addon_version



