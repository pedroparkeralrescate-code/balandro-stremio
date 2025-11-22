# -*- coding: utf-8 -*-
"""
platformcode package
"""
import sys
import os

# Importar submodules
from . import config as config_module
from . import logger as logger_module
from . import platformtools as platformtools_module

# Crear instancia de Config
config = config_module.Config()

# Exponer funciones de logger como objeto
class Logger:
    @staticmethod
    def info(msg=""):
        logger_module.info(msg)
    
    @staticmethod
    def error(msg):
        logger_module.error(msg)
    
    @staticmethod
    def debug(msg):
        logger_module.debug(msg)

logger = Logger()

# Exponer funciones de platformtools como objeto
class Platformtools:
    @staticmethod
    def dialog_notification(title, msg):
        platformtools_module.dialog_notification(title, msg)
    
    @staticmethod
    def dialog_ok(title, msg):
        platformtools_module.dialog_ok(title, msg)
    
    @staticmethod
    def dialog_yesno(title, msg):
        platformtools_module.dialog_yesno(title, msg)

platformtools = Platformtools()

# Exponer WebErrorException
WebErrorException = config_module.WebErrorException

# Exportar
__all__ = ['config', 'logger', 'platformtools', 'WebErrorException']

