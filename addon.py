# -*- coding: utf-8 -*-
"""
Addon Module - Lógica de adaptación entre Balandro (Kodi) y Stremio
"""

import base64
import json
import importlib
import sys
from typing import Dict, List, Any, Optional
from urllib.parse import quote, unquote


# ============================================================================
# Serialización Stateless (Base64)
# ============================================================================

def serialize_item(item) -> str:
    """
    Serializa un objeto Item de Balandro a Base64 para usar como ID stateless
    
    Args:
        item: Objeto Item de Balandro
    
    Returns:
        str: ID en formato "balandro:BASE64_DATA"
    """
    try:
        # Extraer solo atributos que existen
        item_dict = {}
        
        # Lista de atributos posibles
        possible_attrs = ['channel', 'action', 'title', 'url', 'thumbnail', 'fanart', 
                         'plot', 'contentType', 'contentTitle', 'contentSerieName', 
                         'contentSeason', 'contentEpisodeNumber', 'server', 'data_url', 'data_lmt']
        
        # NO usar hasattr() porque Item tiene __getattr__ personalizado que lanza KeyError
        for attr in possible_attrs:
            try:
                value = getattr(item, attr)
                if value:  # Solo agregar si tiene valor
                    item_dict[attr] = value
            except (AttributeError, KeyError):
                pass  # Atributo no existe, skip
        
        # Agregar infoLabels si existen
        try:
            if item.infoLabels:
                item_dict['infoLabels'] = dict(item.infoLabels)
        except (AttributeError, KeyError):
            pass
        
        # Serializar a JSON y luego a Base64
        json_str = json.dumps(item_dict, ensure_ascii=True)  # ensure_ascii=True para evitar problemas de encoding
        b64_str = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')
        
        return f"balandro:{b64_str}"
    
    except Exception as e:
        print(f"❌ Error serializando Item: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: usar un ID simple basado en título
        try:
            title_safe = quote(getattr(item, 'title', 'unknown'))
        except:
            title_safe = 'unknown'
        return f"balandro:{title_safe}"


def deserialize_item(item_id: str):
    """
    Deserializa un ID Base64 de vuelta a un objeto Item de Balandro
    
    Args:
        item_id: ID en formato "balandro:BASE64_DATA" o "tmdb:12345"
    
    Returns:
        Item: Objeto Item reconstruido
    """
    from balandro_src.core.item import Item
    
    try:
        # Si es un ID de TMDb, no podemos deserializar directamente
        # El Item debe venir del campo _balandro_item del meta
        if item_id.startswith('tmdb:'):
            print(f"⚠ ID de TMDb detectado: {item_id}")
            print("  Necesitas pasar el meta completo con _balandro_item")
            return None
        
        # Remover prefijo "balandro:"
        if item_id.startswith('balandro:'):
            b64_str = item_id[9:]  # len("balandro:") = 9
        else:
            b64_str = item_id
        
        # Decodificar Base64 y JSON
        json_str = base64.urlsafe_b64decode(b64_str.encode('ascii')).decode('utf-8')
        item_dict = json.loads(json_str)
        
        # Reconstruir Item
        return Item(**item_dict)
    
    except Exception as e:
        print(f"❌ Error deserializando Item ID: {item_id} - {e}")
        return None


def get_item_from_meta(meta: Dict) -> Optional:
    """
    Extrae Item de Balandro desde un meta de Stremio
    
    Args:
        meta: Meta de Stremio que puede contener _balandro_item
    
    Returns:
        Item de Balandro o None
    """
    from balandro_src.core.item import Item
    
    # Si el meta tiene _balandro_item serializado, usarlo
    if '_balandro_item' in meta:
        return deserialize_item(meta['_balandro_item'])
    
    # Si el meta ID es custom de balandro, deserializarlo
    meta_id = meta.get('id', '')
    if meta_id.startswith('balandro:'):
        return deserialize_item(meta_id)
    
    return None


# ============================================================================
# Conversión Item → Stremio Meta
# ============================================================================

def item_to_meta(item, addon_id: str = "community.balandro", use_tmdb: bool = True) -> Dict[str, Any]:
    """
    Convierte un objeto Item de Balandro a formato Meta de Stremio
    
    Args:
        item: Objeto Item de Balandro
        addon_id: ID del addon de Stremio
        use_tmdb: Si True, intenta hacer lookup en TMDb
    
    Returns:
        dict: Objeto meta de Stremio
    """
    from tmdb_client import tmdb_client
    
    # Determinar tipo (movie/series)
    content_type = getattr(item, 'contentType', 'movie')
    stremio_type = 'series' if content_type in ['tvshow', 'season', 'episode'] else 'movie'
    
    # Nombre/Título
    name = getattr(item, 'title', '') or getattr(item, 'contentTitle', '') or 'Sin título'
    
    # Limpiar formato de Kodi (colores, etiquetas)
    name = clean_kodi_formatting(name)
    
    # InfoLabels
    info_labels = {}
    if hasattr(item, 'infoLabels'):
        info_labels = dict(item.infoLabels)
    
    # Año
    year = info_labels.get('year', '')
    if isinstance(year, int):
        year_int = year
        year = str(year)
    elif year and year != '-':
        try:
            year_int = int(year)
        except:
            year_int = None
    else:
        year_int = None
    
    # Intentar match con TMDb si está habilitado
    tmdb_match = None
    if use_tmdb and name and name != 'Sin título':
        try:
            # Limpiar título para mejor match
            clean_title = name.split('(')[0].strip()  # Remover año si está en el título
            
            tmdb_match = tmdb_client.match_content(
                clean_title,
                stremio_type,
                year_int
            )
        except Exception as e:
            print(f"⚠ Error en TMDb lookup para '{name}': {e}")
    
    # Construir meta
    if tmdb_match and tmdb_match.get('tmdb_id'):
        # Usar ID de TMDb
        meta_id = f"tmdb:{tmdb_match['tmdb_id']}"
        
        meta = {
            'id': meta_id,
            'type': stremio_type,
            'name': tmdb_match.get('title', name),
        }
        
        # Usar poster y backdrop de TMDb (mejor calidad)
        if tmdb_match.get('poster'):
            meta['poster'] = tmdb_match['poster']
        
        if tmdb_match.get('backdrop'):
            meta['background'] = tmdb_match['backdrop']
        
        # Descripción de TMDb
        if tmdb_match.get('overview'):
            meta['description'] = tmdb_match['overview']
        
        # Año del release
        if tmdb_match.get('release_date'):
            release_year = tmdb_match['release_date'][:4]
            if release_year:
                meta['year'] = release_year
        
        # Rating de TMDb
        if tmdb_match.get('vote_average'):
            meta['imdbRating'] = str(tmdb_match['vote_average'])
        
        # CRÍTICO: Guardar Item serializado para poder resolver streams después
        # Lo guardamos en un campo personalizado
        meta['_balandro_item'] = serialize_item(item)
        
    else:
        # Fallback: usar ID custom de Balandro
        meta_id = serialize_item(item)
        
        meta = {
            'id': meta_id,
            'type': stremio_type,
            'name': name,
        }
        
        # Poster y background de Balandro
        poster = getattr(item, 'thumbnail', '')
        if poster:
            meta['poster'] = poster
        
        background = getattr(item, 'fanart', poster)
        if background:
            meta['background'] = background
        
        # Descripción
        description = getattr(item, 'plot', '')
        if description:
            meta['description'] = description
        
        # Año
        if year and year != '-':
            meta['year'] = year
    
    return meta


def clean_kodi_formatting(text: str) -> str:
    """
    Limpia formato específico de Kodi (colores [COLOR], etiquetas [B], etc.)
    
    Args:
        text: Texto con formato Kodi
    
    Returns:
        str: Texto limpio
    """
    import re
    
    # Remover tags de color
    text = re.sub(r'\[COLOR[^\]]*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[/COLOR\]', '', text, flags=re.IGNORECASE)
    
    # Remover tags de formato
    text = re.sub(r'\[/?B\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[/?I\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[/?UPPERCASE\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[/?LOWERCASE\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[/?CAPITALIZE\]', '', text, flags=re.IGNORECASE)
    
    # Remover [CR] (line break)
    text = text.replace('[CR]', ' ')
    
    return text.strip()


# ============================================================================
# Carga Dinámica de Canales
# ============================================================================

def load_channel(channel_name: str):
    """
    Carga dinámicamente un módulo de canal de Balandro
    
    Args:
        channel_name: Nombre del canal (ej: 'cinecalidad')
    
    Returns:
        module: Módulo del canal cargado
    """
    try:
        module_name = f'balandro_src.channels.{channel_name}'
        
        # Si ya está cargado, recargarlo para cambios en desarrollo
        if module_name in sys.modules:
            module = sys.modules[module_name]
            importlib.reload(module)
        else:
            module = importlib.import_module(module_name)
        
        return module
    
    except Exception as e:
        print(f"❌ Error cargando canal {channel_name}: {e}")
        return None


# ============================================================================
# Resolución de URLs de Video
# ============================================================================

def resolve_video_urls(item) -> List[Dict[str, Any]]:
    """
    Resuelve un Item a URLs de video usando los resolvers de Balandro
    
    Args:
        item: Objeto Item con información del contenido
    
    Returns:
        list: Lista de streams en formato Stremio
    """
    from balandro_src.core import servertools
    
    streams = []
    
    try:
        # Si el item ya tiene un servidor específico, resolver directamente
        if hasattr(item, 'server') and item.server:
            server = item.server
            video_url = getattr(item, 'url', getattr(item, 'data_url', ''))
            
            if video_url:
                # Intentar resolver con servertools
                try:
                    video_urls = servertools.resolve_video_urls_for_playing(
                        server, video_url
                    )
                    
                    for quality, url in video_urls:
                        stream = {
                            'url': url,
                            'title': f'{server} - {quality}',
                        }
                        
                        # Agregar información de calidad si está disponible
                        if hasattr(item, 'quality'):
                            stream['title'] = f"{item.quality} - {server}"
                        
                        # Agregar idioma si está disponible
                        if hasattr(item, 'language'):
                            stream['title'] += f" [{item.language}]"
                        
                        streams.append(stream)
                
                except Exception as e:
                    print(f"⚠ Error resolviendo {server}: {e}")
        
        # Si no hay servidor específico, intentar obtener findvideos del canal
        else:
            channel_name = getattr(item, 'channel', '')
            if channel_name:
                channel = load_channel(channel_name)
                
                if channel and hasattr(channel, 'findvideos'):
                    # Llamar a findvideos
                    video_items = channel.findvideos(item)
                    
                    # Resolver cada item de video (si hay alguno)
                    if video_items:
                        for video_item in video_items:
                            server = getattr(video_item, 'server', '')
                            video_url = getattr(video_item, 'url', '')
                            
                            if server and video_url:
                                try:
                                    video_urls = servertools.resolve_video_urls_for_playing(
                                        server, video_url
                                    )
                                    
                                    for quality, url in video_urls:
                                        stream = {
                                            'url': url,
                                            'title': f'{server} - {quality}',
                                        }
                                        
                                        if hasattr(video_item, 'language'):
                                            stream['title'] += f" [{video_item.language}]"
                                        
                                        streams.append(stream)
                                
                                except Exception as e:
                                    print(f"⚠ Error resolviendo {server}: {e}")
    
    except Exception as e:
        print(f"❌ Error en resolve_video_urls: {e}")
        import traceback
        traceback.print_exc()
    
    return streams


# ============================================================================
# Búsqueda Global
# ============================================================================

def search_content(query: str, content_type: str = 'movie', channel_name: str = None, 
                   season: str = None, episode: str = None) -> List[Dict[str, Any]]:
    """
    Realiza búsqueda en Balandro
    
    Args:
        query: Término de búsqueda
        content_type: Tipo de contenido ('movie' o 'series')
        channel_name: Canal específico o None para búsqueda global
        season: Número de temporada (opcional)
        episode: Número de episodio (opcional)
    
    Returns:
        list: Lista de metas de Stremio
    """
    metas = []
    
    try:
        if channel_name:
            # Búsqueda en canal específico
            channel = load_channel(channel_name)
            
            if channel and hasattr(channel, 'search'):
                from balandro_src.core.item import Item
                
                # Crear item de búsqueda
                search_item = Item(
                    channel=channel_name,
                    action='search',
                    search_type=content_type,
                    text=query
                )
                
                # Ejecutar búsqueda
                results = channel.search(search_item, query)
                
                # Convertir a metas y añadir info de episodio
                for item in results:
                    if season and episode:
                        item.contentSeason = season
                        item.contentEpisode = episode
                    meta = item_to_meta(item)
                    metas.append(meta)
        
        else:
            # Búsqueda global en múltiples canales
            # Canales populares para buscar
            popular_channels = ['cinecalidad', 'pelisplus', 'cuevana3re']
            
            for ch_name in popular_channels:
                try:
                    channel = load_channel(ch_name)
                    
                    if channel and hasattr(channel, 'search'):
                        from balandro_src.core.item import Item
                        
                        search_item = Item(
                            channel=ch_name,
                            action='search',
                            search_type=content_type,
                            text=query
                        )
                        
                        results = channel.search(search_item, query)
                        
                        for item in results:
                            if season and episode:
                                item.contentSeason = season
                                item.contentEpisode = episode
                            meta = item_to_meta(item)
                            metas.append(meta)
                            
                            # Limitar resultados para no saturar
                            if len(metas) >= 50:
                                break
                    
                    if len(metas) >= 50:
                        break
                
                except Exception as e:
                    print(f"⚠ Error buscando en {ch_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        import traceback
        traceback.print_exc()
    
    return metas
