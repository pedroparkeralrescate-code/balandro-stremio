# -*- coding: utf-8 -*-
"""
Kodi Mock Module - Simula las librerías de Kodi para que Balandro funcione sin Kodi
"""

import os
import sys
from typing import Any, Dict, List


# ============================================================================
# Mock xbmc
# ============================================================================
class XBMCMock:
    """Mock del módulo xbmc"""
    
    LOGDEBUG = 0
    LOGINFO = 1
    LOGWARNING = 2
    LOGERROR = 3
    LOGFATAL = 4
    LOGNONE = 5
    
    @staticmethod
    def log(msg: str, level: int = LOGDEBUG) -> None:
        """Mock de xbmc.log"""
        level_names = {0: 'DEBUG', 1: 'INFO', 2: 'WARNING', 3: 'ERROR', 4: 'FATAL'}
        print(f"[KODI-{level_names.get(level, 'DEBUG')}] {msg}")
    
    @staticmethod
    def getCondVisibility(condition: str) -> bool:
        """Mock de xbmc.getCondVisibility - siempre retorna False"""
        return False
    
    @staticmethod
    def translatePath(path: str) -> str:
        """Mock de xbmc.translatePath - retorna ruta válida y crea directorios"""
        import os
        from pathlib import Path
        
        # Obtener directorio del proyecto
        project_root = Path(__file__).parent.absolute()
        
        # Mapear rutas especiales de Kodi a rutas locales
        if 'special://' in path:
            # special://home/ -> ./data/
            if 'special://home/' in path:
                result = str(project_root / 'data' / path.replace('special://home/', ''))
            # special://temp/ -> ./temp/
            elif 'special://temp/' in path:
                result = str(project_root / 'temp' / path.replace('special://temp/', ''))
            # special://userdata/ -> ./data/
            elif 'special://userdata/' in path:
                result = str(project_root / 'data' / path.replace('special://userdata/', ''))
            else:
                # Otros casos: ./data/
                result = str(project_root / 'data')
        else:
            # Si no tiene special://, usar como está
            result = path
        
        # Crear directorio si no existe (para evitar FileNotFoundError)
        try:
            result_path = Path(result)
            if not result_path.suffix:  # Es un directorio (no tiene extensión)
                result_path.mkdir(parents=True, exist_ok=True)
            else:  # Es un archivo, crear directorio padre
                result_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠ No se pudo crear directorio para {result}: {e}")
        
        return result
    
    @staticmethod
    def sleep(milliseconds: int) -> None:
        """Mock de xbmc.sleep"""
        import time
        time.sleep(milliseconds / 1000.0)
    
    @staticmethod
    def executebuiltin(command: str) -> None:
        """Mock de xbmc.executebuiltin"""
        pass
    
    @staticmethod
    def getInfoLabel(info: str) -> str:
        """Mock de xbmc.getInfoLabel"""
        return ""


# ============================================================================
# Mock xbmcgui
# ============================================================================
class DialogMock:
    """Mock de xbmcgui.Dialog"""
    
    def ok(self, heading: str, line1: str, line2: str = "", line3: str = "") -> bool:
        """Mock de Dialog.ok"""
        print(f"[DIALOG-OK] {heading}: {line1} {line2} {line3}")
        return True
    
    def yesno(self, heading: str, line1: str, line2: str = "", line3: str = "", 
              nolabel: str = "", yeslabel: str = "") -> bool:
        """Mock de Dialog.yesno - siempre retorna True"""
        print(f"[DIALOG-YESNO] {heading}: {line1}")
        return True
    
    def notification(self, heading: str, message: str, icon: str = "", time: int = 5000, 
                     sound: bool = True) -> None:
        """Mock de Dialog.notification"""
        print(f"[NOTIFICATION] {heading}: {message}")
    
    def select(self, heading: str, list: List[str], autoclose: int = 0, 
               preselect: int = -1, useDetails: bool = False) -> int:
        """Mock de Dialog.select - retorna primer elemento"""
        print(f"[DIALOG-SELECT] {heading}: {list}")
        return 0 if list else -1
    
    def input(self, heading: str, default: str = "", type: int = 0, 
              option: int = 0, autoclose: int = 0) -> str:
        """Mock de Dialog.input - retorna valor por defecto"""
        return default


class DialogProgressMock:
    """Mock de xbmcgui.DialogProgress"""
    
    def __init__(self):
        self.percentage = 0
        self.heading = ""
    
    def create(self, heading: str, line1: str = "", line2: str = "", line3: str = "") -> None:
        """Mock de DialogProgress.create"""
        self.heading = heading
        print(f"[PROGRESS] {heading}: {line1}")
    
    def update(self, percent: int, line1: str = "", line2: str = "", line3: str = "") -> None:
        """Mock de DialogProgress.update"""
        self.percentage = percent
    
    def iscanceled(self) -> bool:
        """Mock de DialogProgress.iscanceled - siempre False"""
        return False
    
    def close(self) -> None:
        """Mock de DialogProgress.close"""
        pass


class ListItemMock:
    """Mock de xbmcgui.ListItem"""
    
    def __init__(self, label: str = "", label2: str = "", path: str = ""):
        self.label = label
        self.label2 = label2
        self.path = path
        self.properties = {}
        self.art = {}
        self.info = {}
    
    def setLabel(self, label: str) -> None:
        self.label = label
    
    def setProperty(self, key: str, value: str) -> None:
        self.properties[key] = value
    
    def setArt(self, art: Dict[str, str]) -> None:
        self.art.update(art)
    
    def setInfo(self, type: str, infoLabels: Dict[str, Any]) -> None:
        self.info[type] = infoLabels


class WindowDialogMock:
    """Mock de xbmcgui.WindowDialog"""
    
    def __init__(self):
        pass
    
    def show(self):
        pass
    
    def close(self):
        pass


class XBMCGUIMock:
    """Mock del módulo xbmcgui"""
    Dialog = DialogMock
    DialogProgress = DialogProgressMock
    ListItem = ListItemMock
    WindowDialog = WindowDialogMock


# ============================================================================
# Mock xbmcaddon
# ============================================================================
class AddonMock:
    """Mock de xbmcaddon.Addon"""
    
    def __init__(self, id: str = ""):
        self.id = id or "plugin.video.balandro"
        self.settings = {}
    
    def getSetting(self, id: str) -> str:
        """Mock de Addon.getSetting - retorna string vacío por defecto"""
        return self.settings.get(id, "")
    
    def getSettingBool(self, id: str) -> bool:
        """Mock de Addon.getSettingBool - retorna False por defecto"""
        value = self.settings.get(id, "false")
        return value.lower() in ('true', '1', 'yes')
    
    def getSettingInt(self, id: str) -> int:
        """Mock de Addon.getSettingInt - retorna 0 por defecto"""
        try:
            return int(self.settings.get(id, "0"))
        except ValueError:
            return 0
    
    def setSetting(self, id: str, value: str) -> None:
        """Mock de Addon.setSetting"""
        self.settings[id] = value
    
    def getAddonInfo(self, id: str) -> str:
        """Mock de Addon.getAddonInfo"""
        from pathlib import Path
        import os
        
        # Obtener directorio del proyecto (donde está kodi_mock.py)
        # Necesitamos ir al parent porque kodi_mock.py está en stremio-balandro/
        current_file = Path(__file__).absolute()
        project_root = current_file.parent  # stremio-balandro/
        balandro_src = project_root / 'balandro_src'  # stremio-balandro/balandro_src/
        
        info = {
            'id': self.id,
            'name': 'Balandro',
            'version': '4.0.22',
            'path': str(balandro_src),  # Ruta a balandro_src
            'profile': str(project_root / 'data'),  # Ruta a data/ para guardar configs
            'icon': '',
            'fanart': ''
        }
        
        # Hacer case-insensitive lookup (Balandro usa 'Path' y 'Profile' con mayúscula)
        return info.get(id.lower(), "")
    
    def openSettings(self) -> None:
        """Mock de Addon.openSettings"""
        pass


class XBMCAddonMock:
    """Mock del módulo xbmcaddon"""
    Addon = AddonMock


# ============================================================================
# Mock xbmcplugin
# ============================================================================
class XBMCPluginMock:
    """Mock del módulo xbmcplugin"""
    
    SORT_METHOD_NONE = 0
    SORT_METHOD_LABEL = 1
    SORT_METHOD_TITLE = 9
    SORT_METHOD_UNSORTED = 40
    
    @staticmethod
    def addDirectoryItem(handle: int, url: str, listitem: Any, 
                        isFolder: bool = False, totalItems: int = 0) -> bool:
        """Mock de xbmcplugin.addDirectoryItem"""
        return True
    
    @staticmethod
    def endOfDirectory(handle: int, succeeded: bool = True, 
                      updateListing: bool = False, cacheToDisc: bool = True) -> None:
        """Mock de xbmcplugin.endOfDirectory"""
        pass
    
    @staticmethod
    def setResolvedUrl(handle: int, succeeded: bool, listitem: Any) -> None:
        """Mock de xbmcplugin.setResolvedUrl"""
        pass
    
    @staticmethod
    def addSortMethod(handle: int, sortMethod: int) -> None:
        """Mock de xbmcplugin.addSortMethod"""
        pass
    
    @staticmethod
    def setContent(handle: int, content: str) -> None:
        """Mock de xbmcplugin.setContent"""
        pass


# ============================================================================
# Mock xbmcvfs
# ============================================================================
class XBMCVFSMock:
    """Mock del módulo xbmcvfs"""
    
    class File:
        """Mock de xbmcvfs.File"""
        def __init__(self, path, mode='r'):
            self.path = path
            self.mode = mode
            self.file_obj = None
            try:
                if 'b' in mode:
                    self.file_obj = open(path, mode)
                else:
                    self.file_obj = open(path, mode, encoding='utf-8')
            except Exception as e:
                print(f"⚠ Error abriendo archivo {path}: {e}")
        
        def read(self, bytes=-1):
            if self.file_obj:
                return self.file_obj.read(bytes)
            return b'' if 'b' in self.mode else ''
        
        def readBytes(self, bytes):
            if self.file_obj:
                return self.file_obj.read(bytes)
            return b''
        
        def write(self, data):
            if self.file_obj:
                return self.file_obj.write(data)
            return False
        
        def close(self):
            if self.file_obj:
                self.file_obj.close()
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()
    
    @staticmethod
    def translatePath(path: str) -> str:
        """Mock de xbmcvfs.translatePath - igual que xbmc.translatePath"""
        # Usar la misma implementación que xbmc.translatePath
        return XBMCMock.translatePath(path)
    
    @staticmethod
    def exists(path: str) -> bool:
        """Mock de xbmcvfs.exists"""
        return os.path.exists(path)
    
    @staticmethod
    def mkdir(path: str) -> bool:
        """Mock de xbmcvfs.mkdir"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except:
            return False
    
    @staticmethod
    def mkdirs(path: str) -> bool:
        """Mock de xbmcvfs.mkdirs"""
        return XBMCVFSMock.mkdir(path)
    
    @staticmethod
    def delete(file: str) -> bool:
        """Mock de xbmcvfs.delete"""
        try:
            if os.path.exists(file):
                os.remove(file)
            return True
        except:
            return False
    
    @staticmethod
    def rmdir(path: str, force: bool = False) -> bool:
        """Mock de xbmcvfs.rmdir"""
        try:
            if force:
                import shutil
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.rmdir(path)
            return True
        except:
            return False
    
    @staticmethod
    def listdir(path: str) -> tuple:
        """Mock de xbmcvfs.listdir - retorna (dirs, files)"""
        try:
            items = os.listdir(path)
            dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
            files = [f for f in items if os.path.isfile(os.path.join(path, f))]
            return (dirs, files)
        except:
            return ([], [])


# ============================================================================
# Instanciar mocks
# ============================================================================
xbmc = XBMCMock()
xbmcgui = XBMCGUIMock()
xbmcaddon = XBMCAddonMock()
xbmcplugin = XBMCPluginMock()
xbmcvfs = XBMCVFSMock()

# Exponer CLASES de xbmcgui a nivel de módulo
# (necesario porque código hace: dialog = xbmcgui.Dialog())
Dialog = DialogMock
DialogProgress = DialogProgressMock
ListItem = ListItemMock
WindowDialog = WindowDialogMock

# Exponer CLASE de xbmcaddon a nivel de módulo
# (necesario porque config.py hace: __settings__ = xbmcaddon.Addon())
Addon = AddonMock

# Exponer funciones de xbmcvfs a nivel de módulo
# (necesario porque config.py hace: translatePath = xbmcvfs.translatePath)
translatePath = XBMCVFSMock.translatePath
exists = XBMCVFSMock.exists
mkdir = XBMCVFSMock.mkdir
mkdirs = XBMCVFSMock.mkdirs
delete = XBMCVFSMock.delete
rmdir = XBMCVFSMock.rmdir
listdir = XBMCVFSMock.listdir
File = XBMCVFSMock.File

# Exponer constantes de xbmc a nivel de módulo
LOGDEBUG = XBMCMock.LOGDEBUG
LOGINFO = XBMCMock.LOGINFO
LOGWARNING = XBMCMock.LOGWARNING
LOGERROR = XBMCMock.LOGERROR
LOGFATAL = XBMCMock.LOGFATAL
LOGNONE = XBMCMock.LOGNONE

# Exponer funciones de xbmc a nivel de módulo
log = XBMCMock.log
getCondVisibility = XBMCMock.getCondVisibility
sleep = XBMCMock.sleep
executebuiltin = XBMCMock.executebuiltin
getInfoLabel = XBMCMock.getInfoLabel

# Exponer funciones de xbmcplugin a nivel de módulo
addDirectoryItem = XBMCPluginMock.addDirectoryItem
endOfDirectory = XBMCPluginMock.endOfDirectory
setResolvedUrl = XBMCPluginMock.setResolvedUrl
addSortMethod = XBMCPluginMock.addSortMethod
setContent = XBMCPluginMock.setContent

# Exponer constantes de xbmcplugin
SORT_METHOD_NONE = XBMCPluginMock.SORT_METHOD_NONE
SORT_METHOD_LABEL = XBMCPluginMock.SORT_METHOD_LABEL
SORT_METHOD_TITLE = XBMCPluginMock.SORT_METHOD_TITLE
SORT_METHOD_UNSORTED = XBMCPluginMock.SORT_METHOD_UNSORTED


# ============================================================================
# Función de inicialización
# ============================================================================
def install_mocks():
    """Instala los mocks en sys.modules"""
    sys.modules['xbmc'] = sys.modules[__name__]
    sys.modules['xbmcgui'] = sys.modules[__name__]
    sys.modules['xbmcaddon'] = sys.modules[__name__]
    sys.modules['xbmcplugin'] = sys.modules[__name__]
    sys.modules['xbmcvfs'] = sys.modules[__name__]
    print("✓ Kodi mocks instalados correctamente")
