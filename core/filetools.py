# -*- coding: utf-8 -*-
"""
Mock filetools module for serverless environment
"""
import os

def read(filename):
    """Read file contents"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def write(filename, data):
    """Write file contents"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
        return True
    except:
        return False

def exists(filename):
    """Check if file exists"""
    return os.path.exists(filename)

def join(*args):
    """Join path components"""
    return os.path.join(*args)

def dirname(path):
    """Get directory name"""
    return os.path.dirname(path)

def basename(path):
    """Get base name"""
    return os.path.basename(path)

