# -*- coding: utf-8 -*-
"""
Core package initialization
Simula el entorno de Balandro para Stremio
"""

import sys

# Importar platformcode package y registrarlo globalmente
from . import platformcode

# Registrar platformcode como módulo global si no está ya
if 'platformcode' not in sys.modules:
    sys.modules['platformcode'] = platformcode

# Registrar xbmcgui para channels que lo importan (como hdfull)
try:
    from .platformcode import xbmcgui
    if 'xbmcgui' not in sys.modules:
        sys.modules['xbmcgui'] = xbmcgui
except:
    pass

# Exportar componentes principales
__all__ = ['platformcode']

