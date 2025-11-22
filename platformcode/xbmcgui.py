# -*- coding: utf-8 -*-
"""
Stub for xbmcgui module
"""

class ListItem:
    """Stub for xbmcgui.ListItem"""
    def __init__(self, label="", label2="", path=""):
        self.label = label
        self.label2 = label2
        self.path = path
    
    def setInfo(self, type, infoLabels):
        pass
    
    def setArt(self, values):
        pass
    
    def setProperty(self, key, value):
        pass

class Dialog:
    """Stub for xbmcgui.Dialog"""
    def ok(self, heading, line1, line2="", line3=""):
        pass
    
    def yesno(self, heading, line1, line2="", line3=""):
        return True

class DialogProgress:
    """Stub for xbmcgui.DialogProgress"""
    def create(self, heading, message=""):
        pass
    
    def update(self, percent, message=""):
        pass
    
    def iscanceled(self):
        return False
    
    def close(self):
        pass

class WindowDialog:
    """Stub for xbmcgui.WindowDialog"""
    def __init__(self):
        pass
    
    def show(self):
        pass
    
    def close(self):
        pass
