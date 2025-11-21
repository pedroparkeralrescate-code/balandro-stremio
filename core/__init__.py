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

# Exportar componentes principales
__all__ = ['platformcode']


