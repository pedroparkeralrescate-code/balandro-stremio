# -*- coding: utf-8 -*-
"""
Stub for platformcode.config
"""

# Addon metadata
addon_name = "Balandro"
addon_version = "1.0.0"

# Exception class for web errors
class WebErrorException(Exception):
    """Exception for web errors"""
    pass

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

