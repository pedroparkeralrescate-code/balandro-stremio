# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import platformcode

# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import platformcode

class Meta:
    def get_meta(self, media_type, media_id):
        """Main method to get metadata"""
        print(f"[META] Tipo: {media_type}, ID: {media_id}")
        return self.get_metadata(media_id, media_type)

    def get_metadata(self, imdb_id, media_type):
        """Obtiene metadata desde TMDB"""
        try:
            from core import tmdb
            
            tipo = 'movie' if media_type == 'movie' else 'tv'
            info = tmdb.get_info(imdb_id, tipo=tipo)
            
            if info:
                meta = {
                    "id": imdb_id,
                    "type": media_type,
                    "name": info.get('title') or info.get('name', 'Sin título'),
                }
                
                if info.get('overview'):
                    meta["description"] = info['overview']
                
                if info.get('poster_path'):
                    meta["poster"] = f"https://image.tmdb.org/t/p/w500{info['poster_path']}"
                
                if info.get('backdrop_path'):
                    meta["background"] = f"https://image.tmdb.org/t/p/original{info['backdrop_path']}"
                
                if info.get('release_date'):
                    meta["year"] = info['release_date'][:4]
                elif info.get('first_air_date'):
                    meta["year"] = info['first_air_date'][:4]
                
                if info.get('genres'):
                    meta["genres"] = [g['name'] for g in info['genres']]
                
                if info.get('vote_average'):
                    meta["imdbRating"] = str(info['vote_average'])
                
                return meta
        
        except Exception as e:
            print(f"[ERROR] get_metadata: {e}")
        
        # Fallback
        return {
            "id": imdb_id,
            "type": media_type,
            "name": "Contenido disponible"
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL: /meta/{type}/{id}.json
            path_parts = self.path.split('/')
            
            if len(path_parts) < 4:
                self.send_error(400, "Invalid path")
                return
            
            media_type = path_parts[2]  # 'movie' or 'series'
            media_id = path_parts[3].replace('.json', '')
            
            meta_logic = Meta()
            meta = meta_logic.get_meta(media_type, media_id)
            
            response = {"meta": meta}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[ERROR] {e}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Devolver metadata mínima
            meta = {
                "id": media_id,
                "type": media_type,
                "name": "Contenido disponible"
            }
            self.wfile.write(json.dumps({"meta": meta}).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

