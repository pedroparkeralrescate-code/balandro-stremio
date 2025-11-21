# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import importlib

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import platformcode

# Channels principales para catálogos
CATALOG_CHANNELS = [
    'cuevana3',
    'pelisplus',
    'gnula',
    'hdfull',
    'cinecalidad'
]

# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import importlib

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import platformcode

# Channels principales para catálogos
CATALOG_CHANNELS = [
    'cuevana3',
    'pelisplus',
    'gnula',
    'hdfull',
    'cinecalidad'
]

class Catalog:
    def get_catalog(self, media_type, catalog_id, skip=0):
        """Main method to get catalog"""
        print(f"[CATALOG] Tipo: {media_type}, ID: {catalog_id}, Skip: {skip}")
        return self.get_catalog_items(media_type, catalog_id, skip)

    def get_catalog_items(self, media_type, catalog_id, skip=0):
        """Obtiene items del catálogo desde un channel"""
        metas = []
        
        try:
            # Usar el primer channel disponible
            channel_name = CATALOG_CHANNELS[0]
            channel = importlib.import_module(f'channels.{channel_name}')
            
            from core.item import Item
            
            # Crear item base
            if media_type == 'movie':
                list_item = Item(
                    channel=channel_name,
                    action='list_all',
                    url=self.get_channel_url(channel_name, 'movie'),
                    search_type='movie'
                )
            else:
                list_item = Item(
                    channel=channel_name,
                    action='list_all',
                    url=self.get_channel_url(channel_name, 'series'),
                    search_type='tvshow'
                )
            
            # Obtener listado
            if hasattr(channel, 'list_all'):
                items = channel.list_all(list_item)
                
                # Convertir a formato Stremio
                for item in items[:20]:  # Limitar a 20 items
                    meta = self.item_to_meta(item, media_type)
                    if meta:
                        metas.append(meta)
        
        except Exception as e:
            print(f"[ERROR] get_catalog_items: {e}")
            import traceback
            traceback.print_exc()
        
        return metas
    
    def get_channel_url(self, channel_name, media_type):
        """Obtiene la URL base del channel para listar contenido"""
        urls = {
            'cuevana3': {
                'movie': 'https://cuevana3.io/peliculas',
                'series': 'https://cuevana3.io/serie'
            },
            'pelisplus': {
                'movie': 'https://pelisplus.icu/peliculas',
                'series': 'https://pelisplus.icu/series'
            },
            'gnula': {
                'movie': 'https://gnula.one/peliculas',
                'series': 'https://gnula.one/series'
            },
            'hdfull': {
                'movie': 'https://hdfull.lv/peliculas',
                'series': 'https://hdfull.lv/series'
            },
            'cinecalidad': {
                'movie': 'https://cinecalidad.run/',
                'series': 'https://cinecalidad.run/series'
            }
        }
        
        return urls.get(channel_name, {}).get(media_type, '')
    
    def item_to_meta(self, item, media_type):
        """Convierte un Item de Balandro a formato meta de Stremio"""
        try:
            # Obtener IMDb ID si está disponible
            imdb_id = getattr(item, 'imdb_id', '')
            
            if not imdb_id:
                # Generar ID temporal basado en el título
                title = getattr(item, 'title', '').replace(' ', '-').lower()
                imdb_id = f"balandro-{title}"
            
            meta = {
                "id": imdb_id,
                "type": media_type,
                "name": getattr(item, 'title', 'Sin título'),
            }
            
            # Agregar thumbnail si existe
            thumbnail = getattr(item, 'thumbnail', '')
            if thumbnail:
                meta["poster"] = thumbnail
            
            # Agregar año si existe
            year = getattr(item, 'infoLabels', {}).get('year', '')
            if year:
                meta["year"] = str(year)
            
            # Agregar descripción si existe
            plot = getattr(item, 'plot', '') or getattr(item, 'infoLabels', {}).get('plot', '')
            if plot:
                meta["description"] = plot
            
            return meta
            
        except Exception as e:
            print(f"[ERROR] item_to_meta: {e}")
            return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL: /catalog/{type}/{id}.json o /catalog/{type}/{id}/skip={offset}.json
            path_parts = self.path.split('/')
            
            if len(path_parts) < 4:
                self.send_error(400, "Invalid path")
                return
            
            media_type = path_parts[2]  # 'movie' or 'series'
            catalog_id = path_parts[3].split('.')[0]
            
            # Parsear skip/offset
            skip = 0
            if 'skip=' in self.path:
                try:
                    skip = int(self.path.split('skip=')[1].split('.')[0].split('&')[0])
                except:
                    skip = 0
            
            catalog_logic = Catalog()
            metas = catalog_logic.get_catalog(media_type, catalog_id, skip)
            
            response = {"metas": metas}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"metas": []}).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

