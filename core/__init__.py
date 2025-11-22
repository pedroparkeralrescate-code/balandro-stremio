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

# Importar y exportar los módulos core que los channels necesitan
from . import httptools
from . import scrapertools
from . import servertools
from . import tmdb
from . import jsontools
from . import filetools
from . import item

# Exportar componentes principales
__all__ = ['platformcode', 'httptools', 'scrapertools', 'servertools', 'tmdb', 'jsontools', 'filetools', 'item']
