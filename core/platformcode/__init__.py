# -*- coding: utf-8 -*-
"""
Platformcode package - Simulates Kodi platform APIs
"""

# Import modules
from . import config
from . import logger
from . import platformtools
from . import xbmcgui

# Export to make them accessible via "from platformcode import config"
__all__ = ['config', 'logger', 'platformtools', 'xbmcgui']
