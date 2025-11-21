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

def get_setting(key, channel=None, default=None):
    """Get a setting value"""
    return os.environ.get(key, default)

def set_setting(key, value, channel=None):
    """Set a setting value"""
    pass

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

# Hacer que el módulo mismo tenga estos atributos
sys.modules[__name__].__addon_name = __addon_name
sys.modules[__name__].__addon_version = __addon_version







