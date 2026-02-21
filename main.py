import sys
import os
from pathlib import Path

# Suprimir SyntaxWarnings de Balandro (usan escape sequences antiguos)
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

# Agregar ruta del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# CRÍTICO: Agregar balandro_src al path para que imports relativos funcionen
# Balandro usa "from platformcode import ..." en lugar de "from balandro_src.platformcode import ..."
balandro_path = project_root / "balandro_src"
sys.path.insert(0, str(balandro_path))

# ============================================================================
# PASO 0: Parchear versión de Python para compatibilidad con Balandro
# ============================================================================
# Balandro fue diseñado para Python 3.9-3.11 y tiene comparaciones que fallan en 3.12
# Hacemos que Python 3.12 se reporte como Python 3.11
import sys

_original_version_info = sys.version_info

# Crear version_info compatible que siempre retorna integers comparables
class CompatVersionInfo:
    def __init__(self):
        self._info = (3, 11, 0, 'final', 0)  # Fingir que somos Python 3.11
    
    def __getitem__(self, index):
        return self._info[index]
    
    def __iter__(self):
        return iter(self._info)
    
    def __repr__(self):
        return f"sys.version_info(major={self._info[0]}, minor={self._info[1]}, micro={self._info[2]}, releaselevel='{self._info[3]}', serial={self._info[4]})"
    
    def __lt__(self, other):
        if isinstance(other, tuple):
            return self._info < other
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, tuple):
            return self._info <= other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, tuple):
            return self._info > other
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, tuple):
            return self._info >= other
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, tuple):
            return self._info == other
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, tuple):
            return self._info != other
        return NotImplemented

# Aplicar parche
sys.version_info = CompatVersionInfo()
print(f"[OK] Python version patched: {_original_version_info[0]}.{_original_version_info[1]} -> 3.11 (compatibility)")

# ============================================================================
# PASO 1: Instalar Mocks ANTES de importar cualquier cosa de Balandro
# ============================================================================
import kodi_mock
kodi_mock.install_mocks()

# ============================================================================
# PASO 2: Aplicar Patches (cloudscraper)
# ============================================================================
import patcher
patcher.apply_patches()

# ============================================================================
# PASO 3: Ahora sí, importar FastAPI y módulos de Balandro
# ============================================================================
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from typing import Optional
import addon

# Crear app FastAPI
app = FastAPI(
    title="Stremio Balandro Addon",
    description="Addon de Stremio que integra los canales de Balandro",
    version="1.0.0"
)

# Configurar CORS para que Stremio pueda acceder
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\n🌍 RECEIVING REQUEST: {request.method} {request.url}")
    response = await call_next(request)
    print(f"🌍 RESPONSE STATUS: {response.status_code}")
    return response

# ============================================================================
# Configuración del Addon
# ============================================================================
ADDON_ID = "community.balandro"
ADDON_NAME = "Balandro"
ADDON_DESCRIPTION = "Acceso a contenido en español mediante los canales de Balandro"

# Importar lista completa de canales desde all_channels.py
try:
    from all_channels import ALL_CHANNELS
    AVAILABLE_CHANNELS = ALL_CHANNELS
    print(f"✓ Cargados {len(AVAILABLE_CHANNELS)} canales de Balandro")
except ImportError:
    # Fallback si all_channels.py no existe
    print("⚠ No se pudo cargar all_channels.py, usando canales por defecto")
    AVAILABLE_CHANNELS = [
        {'id': 'cinecalidad', 'name': 'CineCalidad', 'types': ['movie', 'series']},
        {'id': 'pelisplus', 'name': 'PelisPlus', 'types': ['movie', 'series']},
        {'id': 'cuevana3re', 'name': 'Cuevana3', 'types': ['movie', 'series']},
    ]


# ============================================================================
# Endpoint: Manifest
# ============================================================================
@app.get("/manifest.json")
async def get_manifest():
    """
    Retorna el manifest del addon de Stremio
    Define capacidades, catálogos y tipos de contenido soportados
    """
    
    # Construir catálogos dinámicamente desde canales disponibles
    catalogs = []
    
    for channel in AVAILABLE_CHANNELS:
        if 'movie' in channel['types']:
            catalogs.append({
                'type': 'movie',
                'id': f"{channel['id']}-movies",
                'name': f"{channel['name']} - Películas",
                'extra': [
                    {'name': 'search', 'isRequired': False}
                ]
            })
        
        if 'series' in channel['types']:
            catalogs.append({
                'type': 'series',
                'id': f"{channel['id']}-series",
                'name': f"{channel['name']} - Series",
                'extra': [
                    {'name': 'search', 'isRequired': False}
                ]
            })
    
    manifest = {
        'id': ADDON_ID,
        'version': '1.0.0',
        'name': ADDON_NAME,
        'description': ADDON_DESCRIPTION,
        'resources': [
            'catalog',
            'meta',
            'stream'
        ],
        'types': ['movie', 'series'],
        'catalogs': catalogs,
        'idPrefixes': ['tmdb:', 'balandro:', 'tt'],  # Soportar TMDb, custom IDs, y standard IMDb IDs
        'behaviorHints': {
            'configurable': False,
            'configurationRequired': False
        }
    }
    
    return JSONResponse(content=manifest)


# ============================================================================
# Endpoint: Catalog
# ============================================================================
@app.get("/catalog/{type}/{id}/{extra}.json")
@app.get("/catalog/{type}/{id}.json")
async def get_catalog(
    type: str,
    id: str,
    extra: Optional[str] = None,
    search: Optional[str] = Query(None, alias='search')
):
    """
    Retorna catálogo de películas/series de un canal
    
    Args:
        type: 'movie' o 'series'
        id: ID del catálogo (ej: 'cinecalidad-movies')
        extra: Parámetro extra de Stremio (ej: 'search=Interstellar')
        search: Término de búsqueda (por query params, fallback)
    """
    
    metas = []
    
    # Extraer search del path de Stremio (ej: search=Interstellar)
    if extra and extra.startswith('search='):
        from urllib.parse import unquote
        search = unquote(extra.split('=', 1)[1])
    
    try:
        # Parsear ID del catálogo (formato: "channel-type")
        parts = id.rsplit('-', 1)
        if len(parts) == 2:
            channel_name = parts[0]
            catalog_type = parts[1]  # 'movies' o 'series'
        else:
            channel_name = id
            catalog_type = type
        
        # Si hay búsqueda, usar función de búsqueda
        if search:
            print(f"🔍 Búsqueda: '{search}' en {channel_name} ({type})")
            
            # Ejecutar búsqueda en threadpool (código síncrono de Balandro)
            metas = await run_in_threadpool(
                addon.search_content,
                search,
                type,
                channel_name
            )
        
        else:
            # Obtener mainlist del canal
            print(f"📂 Cargando catálogo: {channel_name} ({type})")
            
            # Cargar canal en threadpool
            def get_channel_items():
                channel = addon.load_channel(channel_name)
                
                if not channel:
                    return []
                
                # Intentar obtener mainlist
                if hasattr(channel, 'mainlist'):
                    from balandro_src.core.item import Item
                    
                    # Crear item base
                    base_item = Item(channel=channel_name)
                    
                    # Llamar mainlist
                    items = channel.mainlist(base_item)
                    
                    # Filtrar por tipo y convertir a metas
                    result_metas = []
                    for item in items:
                        # Solo items de contenido (no acciones, búsquedas, etc.)
                        item_action = getattr(item, 'action', '')
                        
                        if item_action in ['list_all', 'findvideos', 'temporadas']:
                            # Verificar tipo
                            content_type = getattr(item, 'contentType', 'movie')
                            
                            if type == 'movie' and content_type == 'movie':
                                meta = addon.item_to_meta(item, ADDON_ID)
                                result_metas.append(meta)
                            elif type == 'series' and content_type in ['tvshow', 'season']:
                                meta = addon.item_to_meta(item, ADDON_ID)
                                result_metas.append(meta)
                        
                        # Límite de resultados
                        if len(result_metas) >= 100:
                            break
                    
                    return result_metas
                
                return []
            
            metas = await run_in_threadpool(get_channel_items)
    
    except Exception as e:
        print(f"❌ Error en get_catalog: {e}")
        import traceback
        traceback.print_exc()
    
    return JSONResponse(content={'metas': metas})


# ============================================================================
# Endpoint: Meta
# ============================================================================
@app.get("/meta/{type}/{id}.json")
async def get_meta(type: str, id: str):
    """
    Retorna metadatos detallados de un item específico
    
    Args:
        type: 'movie' o 'series'
        id: ID serializado del item (formato: 'balandro:BASE64_DATA')
    """
    
    try:
        # Si es un ID de IMDb o TMDb, no tenemos metadatos propios serializados,
        # dejamos que Stremio use Cinemeta u otros addons de metadatos.
        if id.startswith('tt') or id.startswith('tmdb:'):
            return JSONResponse(
                content={'meta': None},
                status_code=404
            )
            
        # Deserializar item de Balandro
        item = addon.deserialize_item(id)
        
        if not item:
            return JSONResponse(
                content={'meta': None},
                status_code=404
            )
        
        # Convertir a meta completo
        meta = addon.item_to_meta(item, ADDON_ID)
        
        # Agregar campos adicionales si están disponibles
        if hasattr(item, 'infoLabels'):
            info = item.infoLabels
            
            # IMDb rating
            if 'rating' in info and info['rating']:
                meta['imdbRating'] = str(info['rating'])
            
            # Director
            if 'director' in info and info['director']:
                meta['director'] = info['director']
            
            # Cast
            if 'cast' in info and info['cast']:
                meta['cast'] = info['cast']
            
            # Genre
            if 'genre' in info and info['genre']:
                meta['genre'] = [g.strip() for g in info['genre'].split(',')]
        
        return JSONResponse(content={'meta': meta})
    
    except Exception as e:
        print(f"❌ Error en get_meta: {e}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            content={'meta': None},
            status_code=404
        )


# ============================================================================
# Endpoint: Stream
# ============================================================================
@app.get("/stream/{type}/{id}.json")
async def get_streams(type: str, id: str):
    """
    Resuelve un Item a URLs de video finales
    
    Args:
        type: 'movie' o 'series'
        id: ID (formatos: 'tmdb:157336', 'balandro:BASE64_DATA')
    """
    
    streams = []
    
    try:
        # Si es ID de TMDb o IMDb (ej. tt1234567 o tt1234567:1:1), buscar en todos los canales
        if id.startswith('tmdb:') or id.startswith('tt'):
            from tmdb_client import tmdb_client
            
            if id.startswith('tmdb:'):
                print(f"🎬 Búsqueda TMDb ID: {id} ({type})")
                # Extraer TMDb ID
                tmdb_id = id.split(':')[1]
            else:
                # Es un ID de IMDb de Stremio
                print(f"🎬 Búsqueda IMDb ID: {id} ({type})")
                imdb_parts = id.split(':')
                imdb_id_base = imdb_parts[0]  # strip :season:episode if present
                
                # Extraer season/episode si es serie
                if type == 'series' and len(imdb_parts) >= 3:
                    season = imdb_parts[1]
                    episode = imdb_parts[2]
                
                tmdb_id = tmdb_client.get_tmdb_id_from_imdb(imdb_id_base)
                
                if not tmdb_id:
                    print(f"❌ No se pudo resolver IMDb ID {imdb_id_base} a TMDb ID")
                    return JSONResponse(content={'streams': []})
                print(f"  ✓ Resuelto a TMDb ID: {tmdb_id}")
            
            # Obtener metadata de TMDb
            
            if type == 'movie':
                tmdb_data = tmdb_client.get_movie_details(tmdb_id)
            else:
                tmdb_data = tmdb_client.get_tv_details(tmdb_id)
            
            if not tmdb_data:
                return JSONResponse(content={'streams': []})
            
            # Título para buscar
            title = tmdb_data.get('title') or tmdb_data.get('name', '')
            original_title = tmdb_data.get('original_title') or tmdb_data.get('original_name', '')
            year = tmdb_data.get('release_date', '')[:4] if tmdb_data.get('release_date') else None
            
            print(f"  Título ES: {title}")
            if original_title and original_title != title:
                print(f"  Título Original: {original_title}")
            print(f"  Buscando en canales de Balandro...")
            
            # Buscar en canales principales  
            async def search_all_channels():
                all_streams = []
                # Canales prioritarios: rápidos y confiables  
                channels_to_check = [
                    'pelisforte',      # Solicitado por usuario
                    'cinecalidad',     # Muy popular
                    'pelisplushd',     # PelisPlus HD (nombre correcto)
                    'cuevana3re',      # Confiable
                    'hdfull'           # Buena calidad
                ]
                
                for channel_name in channels_to_check:
                    try:
                        print(f"  🔍 Buscando en {channel_name}...")
                        
                        # BUSCAR PRIMERO CON TÍTULO EN ESPAÑOL
                        results = await run_in_threadpool(
                            addon.search_content,
                            title,  # Título español
                            type,
                            channel_name,
                            season=season if 'season' in locals() else None,
                            episode=episode if 'episode' in locals() else None
                        )
                        
                        # SI NO ENCUENTRA Y HAY TÍTULO ORIGINAL DIFERENTE, BUSCAR CON ÉL
                        if not results and original_title and original_title != title:
                            print(f"    ℹ No encontrado con '{title}', probando '{original_title}'...")
                            results = await run_in_threadpool(
                                addon.search_content,
                                original_title,  # Título original (inglés)
                                type,
                                channel_name,
                                season=season if 'season' in locals() else None,
                                episode=episode if 'episode' in locals() else None
                            )
                        
                        if results:
                            # Tomar primer resultado y resolver streams
                            first_result = results[0]
                            
                            # Extraer Item de Balandro
                            item = addon.get_item_from_meta(first_result)
                            
                            if item:
                                print(f"    ✓ Encontrado en {channel_name}, resolviendo streams...")
                                
                                # Resolver URLs
                                channel_streams = await run_in_threadpool(
                                    addon.resolve_video_urls,
                                    item
                                )
                                
                                # Agregar nombre del canal al título
                                for stream in channel_streams:
                                    stream['title'] = f"[{channel_name.upper()}] {stream.get('title', '')}" 
                                
                                all_streams.extend(channel_streams)
                                
                                print(f"    ✓ {len(channel_streams)} streams de {channel_name}")
                            else:
                                print(f"    ⚠ No se pudo extraer Item de {channel_name}")
                        else:
                            print(f"    ℹ No encontrado en {channel_name}")
                    
                    except Exception as e:
                        print(f"    ⚠ Error en {channel_name}: {str(e)[:100]}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                return all_streams
            
            streams = await search_all_channels()
            print(f"✓ Total: {len(streams)} streams encontrados")
        
        else:
            # ID custom de Balandro - deserializar directamente
            item = addon.deserialize_item(id)
            
            if not item:
                return JSONResponse(content={'streams': []})
            
            print(f"🎬 Resolviendo streams para: {getattr(item, 'title', 'Unknown')}")
            
            # Resolver URLs de video en threadpool
            streams = await run_in_threadpool(addon.resolve_video_urls, item)
            
            print(f"✓ {len(streams)} streams encontrados")
    
    except Exception as e:
        print(f"❌ Error en get_streams: {e}")
        import traceback
        traceback.print_exc()
    
    return JSONResponse(content={'streams': streams})


# ============================================================================
# Endpoint: Health Check
# ============================================================================
@app.get("/")
@app.get("/health")
async def health_check():
    """Endpoint de health check para Render"""
    return {
        'status': 'ok',
        'addon': ADDON_NAME,
        'version': '1.0.0',
        'channels': len(AVAILABLE_CHANNELS)
    }


# ============================================================================
# Punto de entrada
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 8000))
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                  STREMIO BALANDRO ADDON                       ║
╠═══════════════════════════════════════════════════════════════╣
║  🚀 Servidor iniciado en: http://0.0.0.0:{port}              ║
║  📡 Manifest URL: http://0.0.0.0:{port}/manifest.json        ║
║  🎬 Canales disponibles: {len(AVAILABLE_CHANNELS)}                                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
