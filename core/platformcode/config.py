# -*- coding: utf-8 -*-
"""
Stub for platformcode.config
"""

# Addon metadata (with double underscore for name mangling)
__addon_name = "Balandro"
__addon_version = "1.0.0"

# Also provide without underscore for compatibility
addon_name = "Balandro"
addon_version = "1.0.0"

# Exception class for web errors
class WebErrorException(Exception):
    """Exception for web errors"""
    pass

def get_addon_version():
    """Get addon version"""
    return __addon_version

def get_setting(name, default=""):
    """Stub for getting settings"""
    return default

def set_setting(name, value):
    """Stub for setting settings"""
    pass

def get_videolibrary_config_path():
    """Stub for video library path"""
    return ""

def get_data_path():
    """Stub for data path"""
    return ""
