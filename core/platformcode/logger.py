# -*- coding: utf-8 -*-
"""
Stub for platformcode.logger
"""

def info(message, force=False):
    """Log info message"""
    print(f"[INFO] {message}")

def debug(message, force=False):
    """Log debug message"""
    print(f"[DEBUG] {message}")

def error(message, force=False):
    """Log error message"""
    print(f"[ERROR] {message}")
