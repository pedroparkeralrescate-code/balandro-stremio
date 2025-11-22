# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import importlib
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar platformcode primero
from core import platformcode

# Lista de channels más populares y confiables (ordenados por prioridad)
PRIORITY_CHANNELS = [
    'cuevana3',
    'gnula',
    'hdfull',
    'cinecalidad',
    'pelispedia',
    'pelismart',
    'cuevana3video',
    'jkanime',
    'animefenix',
    'animeflv'
]

# Timeout por channel (segundos)
CHANNEL_TIMEOUT = 5
MAX_WORKERS = 10

class Streams:
    def get_streams(self, media_type, media_id, season=None, episode=None):
        """Main method to get streams"""
        print(f"[STREAMS] Buscando streams para {media_type} {media_id}")
        
        # Obtener metadata del IMDb ID
        metadata = self.get_metadata_from_imdb(media_id)
        
        if not metadata:
            return []
        
        # Buscar streams en paralelo
        streams = self.search_all_channels(
            metadata, 
            media_type,
            season,
            episode
        )
        
        return streams

    def get_metadata_from_imdb(self, imdb_id):
        """Obtiene metadata desde OMDb API usando el IMDb ID"""
        try:
            import requests
            # Usar OMDb API (gratis, 1000 requests/día)
            omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey=trilogy"
            response = requests.get(omdb_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    return {
                        'imdb_id': imdb_id,
                        'title': data.get('Title', imdb_id),
                        'year': data.get('Year', ''),
                        'type': 'movie' if data.get('Type') == 'movie' else 'tvshow'
                    }
        except Exception as e:
            print(f"[ERROR] No se pudo obtener metadata de OMDb: {e}")
        
        # Fallback: usar solo el IMDb ID
        return {
            'imdb_id': imdb_id,
            'title': imdb_id,
            'year': '',
            'type': 'movie'
        }
    
    def search_all_channels(self, metadata, media_type, season=None, episode=None):
        """Busca streams en todos los channels en paralelo"""
        all_streams = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {}
            
            for channel_name in PRIORITY_CHANNELS:
                future = executor.submit(
                    self.search_single_channel,
                    channel_name,
                    metadata,
                    media_type,
                    season,
                    episode
                )
                futures[future] = channel_name
            
            # Esperar resultados con timeout
            for future in futures:
                channel_name = futures[future]
                try:
                    streams = future.result(timeout=CHANNEL_TIMEOUT)
                    if streams:
                        all_streams.extend(streams)
                        print(f"[SUCCESS] {channel_name}: {len(streams)} streams")
                except TimeoutError:
                    print(f"[TIMEOUT] {channel_name}")
                except Exception as e:
                    print(f"[ERROR] {channel_name}: {str(e)}")
        
        return all_streams
    
    def search_single_channel(self, channel_name, metadata, media_type, season=None, episode=None):
        """Busca en un channel específico"""
        try:
            # Importar el channel dinámicamente
            channel = importlib.import_module(f'channels.{channel_name}')
            print(f"[{channel_name}] Module loaded successfully")
            
            # Crear item de búsqueda
            from core.item import Item
            search_item = Item(
                channel=channel_name,
                search_type='all'  # Permitir búsqueda de movies y series
            )
            
            # Buscar en el channel
            if not hasattr(channel, 'search'):
                print(f"[{channel_name}] No search function")
                return []
            
            print(f"[{channel_name}] Searching for: {metadata['title']}")
            # La función search en Balandro espera (item, texto)
            search_results = channel.search(search_item, metadata['title'])
            print(f"[{channel_name}] Search returned {len(search_results) if search_results else 0} results")
            
            if not search_results:
                print(f"[{channel_name}] No search results")
                return []
            
            print(f"[{channel_name}] First result URL: {getattr(search_results[0], 'url', 'NO URL')}")
            print(f"[{channel_name}] First result title: {getattr(search_results[0], 'title', 'NO TITLE')}")
            
            # Para películas: obtener enlaces directamente
            if media_type == 'movie':
                print(f"[{channel_name}] Getting movie streams for first result")
                streams = self.get_movie_streams(channel, search_results[0])
                print(f"[{channel_name}] Got {len(streams)} streams")
                return streams
            
            # Para series: encontrar episodio específico
            elif media_type == 'series' and season and episode:
                return self.get_episode_streams(channel, search_results[0], season, episode)
            
        except Exception as e:
            print(f"[ERROR] {channel_name}: {str(e)}")
            print(f"[ERROR] {channel_name}: {traceback.format_exc()}")
        
        return []
    
    def get_movie_streams(self, channel, item):
        """Obtiene streams de una película"""
        streams = []
        
        try:
            if not hasattr(channel, 'findvideos'):
                return []
            
            video_items = channel.findvideos(item)
            
            for video in video_items:
                # Resolver el servidor
                stream_url = self.resolve_server(video)
                
                if stream_url:
                    quality = getattr(video, 'quality', 'HD')
                    language = getattr(video, 'language', 'ES')
                    server = getattr(video, 'server', 'directo')
                    
                    streams.append({
                        "name": f"{item.channel.upper()}",
                        "title": f"{quality} - {language} [{server}]",
                        "url": stream_url,
                        "behaviorHints": {
                            "notWebReady": True
                        }
                    })
        
        except Exception as e:
            print(f"[ERROR] get_movie_streams: {e}")
        
        return streams
    
    def get_episode_streams(self, channel, series_item, season, episode):
        """Obtiene streams de un episodio de serie"""
        streams = []
        
        try:
            # Obtener temporadas
            if not hasattr(channel, 'temporadas'):
                return []
            
            season_items = channel.temporadas(series_item)
            
            # Buscar la temporada correcta
            season_item = None
            for s in season_items:
                if str(getattr(s, 'contentSeason', '')) == str(season):
                    season_item = s
                    break
            
            if not season_item:
                return []
            
            # Obtener episodios
            if not hasattr(channel, 'episodios'):
                return []
            
            episode_items = channel.episodios(season_item)
            
            # Buscar el episodio correcto
            episode_item = None
            for ep in episode_items:
                if str(getattr(ep, 'contentEpisodeNumber', '')) == str(episode):
                    episode_item = ep
                    break
            
            if not episode_item:
                return []
            
            # Obtener streams del episodio
            return self.get_movie_streams(channel, episode_item)
        
        except Exception as e:
            print(f"[ERROR] get_episode_streams: {e}")
        
        return streams
    
    def resolve_server(self, video_item):
        """Resuelve el enlace usando los servers de Balandro"""
        try:
            server_name = getattr(video_item, 'server', '')
            url = getattr(video_item, 'url', '')
            
            if not server_name or not url:
                return None
            
            # Si el servidor es 'directo', devolver la URL directamente
            if server_name == 'directo':
                return url
            
            # Intentar resolver con el server module
            try:
                server = importlib.import_module(f'servers.{server_name}')
                
                if hasattr(server, 'get_video_url'):
                    resolved = server.get_video_url(url)
                    
                    if resolved and len(resolved) > 0:
                        # resolved es una lista de [quality, url]
                        return resolved[0][1] if isinstance(resolved[0], (list, tuple)) else resolved[0]
            except Exception as e:
                print(f"[ERROR] Resolviendo {server_name}: {e}")
            
            # Fallback: devolver URL original
            return url
            
        except Exception as e:
            print(f"[ERROR] resolve_server: {e}")
        
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL: /stream/{type}/{id}.json
            path_parts = self.path.split('/')
            
            if len(path_parts) < 4:
                self.send_error(400, "Invalid path")
                return
            
            media_type = path_parts[2]  # 'movie' or 'series'
            media_id = path_parts[3].replace('.json', '')
            
            # Parsear query params (season, episode para series)
            query_params = {}
            if '?' in self.path:
                query_string = self.path.split('?')[1]
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
            
            streams_logic = Streams()
            streams = streams_logic.get_streams(
                media_type,
                media_id,
                query_params.get('season'),
                query_params.get('episode')
            )
            
            # Formatear respuesta
            response = {"streams": streams}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[ERROR] {traceback.format_exc()}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"streams": []}).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

