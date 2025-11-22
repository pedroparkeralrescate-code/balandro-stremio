# -*- coding: utf-8 -*-
# Stub for xbmcgui module (used by some channels like hdfull)

class Dialog:
    def ok(self, heading, message):
        pass
    
    def notification(self, heading, message, icon="", time=5000, sound=True):
        pass
    
    def yesno(self, heading, message, nolabel="No", yeslabel="Yes", autoclose=0):
        return False
    
    def select(self, heading, list, autoclose=0, preselect=-1, useDetails=False):
        return -1
    
    def input(self, heading, default="", type=0, option=0, autoclose=0):
        return ""

class DialogProgress:
    def create(self, heading, message=""):
        pass
    
    def update(self, percent, message=""):
        pass
    
    def iscanceled(self):
        return False
    
    def close(self):
        pass

class ListItem:
    def __init__(self, label="", label2="", path=""):
        self.label = label
        self.label2 = label2
        self.path = path
    
    def setInfo(self, type, infoLabels):
        pass
    
    def setArt(self, dictionary):
        pass
    
    def setProperty(self, key, value):
        pass
