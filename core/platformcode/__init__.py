# -*- coding: utf-8 -*-
"""
Platformcode package - Simulates Kodi platform APIs
"""

def __getattr__(name):
    """Lazy import to avoid circular dependencies"""
    if name in ['config', 'logger', 'platformtools', 'xbmcgui']:
        import importlib
        return importlib.import_module(f'.{name}', __package__)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
