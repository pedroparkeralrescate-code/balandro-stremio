# -*- coding: utf-8 -*-
"""
Simplified ProxyTools for Balandro-Stremio
Automatic proxy discovery and testing - Serverless optimized
"""
import sys
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

PY3 = sys.version_info[0] >= 3

from core import httptools, scrapertools
from platformcode import config, logger

# Configuración optimizada para serverless
PROXY_CONFIG = {
    'MAX_PROXIES_PER_CHANNEL': 3,      # Solo 3 proxies por canal
    'PROXY_TEST_TIMEOUT': 6,            # 6 segundos por proxy (aumentado)
    'SEARCH_TIMEOUT': 20,               # 20 segundos total para búsqueda (aumentado)
    'DEFAULT_PROVIDERS': [
        'proxyscrape.com',
        'free-proxy-list',
    ],
}

def buscar_proxies_automatico(canal, url='https://www.google.com'):
    """
    Busca proxies automaticamente sin interacción del usuario
    Optimizado para entorno serverless con testing por lotes
    
    Args:
        canal (str): Nombre del canal
        url (str): URL para testear proxies
        
    Returns:
        bool: True si se encontraron proxies válidos
    """
    logger.info('[PROXYTOOLS] Iniciando búsqueda automática de proxies para canal: %s' % canal)
    
    # Intentar primero con proxyscrape (más rápido - API)
    # Pedimos muchos para tener reserva
    proxies = _proxyscrape_com(url, '', '', 200)
    
    if not proxies or len(proxies) < 10:
        # Fallback: free-proxy-list
        logger.info('[PROXYTOOLS] Proxyscrape insuficiente, intentando free-proxy-list')
        proxies_fallback = _free_proxy_list(url, '', '', 100)
        if proxies_fallback:
            proxies = (proxies or []) + proxies_fallback
    
    if not proxies:
        logger.info('[PROXYTOOLS] No se encontraron proxies')
        return False
    
    # Validar formato
    proxies = validar_proxies(proxies)
    logger.info('[PROXYTOOLS] Total candidatos encontrados: %d' % len(proxies))
    
    # Testing por lotes para no gastar tiempo en los primeros si fallan
    selected = []
    batch_size = 20
    max_tested = 100  # Límite duro para no estar eternamente
    total_tested = 0
    
    while len(selected) < PROXY_CONFIG['MAX_PROXIES_PER_CHANNEL'] and total_tested < max_tested and proxies:
        # Extraer lote
        batch = proxies[:batch_size]
        proxies = proxies[batch_size:] # Avanzar lista
        
        if not batch:
            break
            
        logger.info('[PROXYTOOLS] Testeando lote de %d proxies (Total probados: %d)...' % (len(batch), total_tested))
        
        # Testear lote
        results = testear_lista_proxies(url, batch)
        total_tested += len(batch)
        
        # Procesar resultados
        for proxy, info in results:
            if info['ok']:
                logger.info('[PROXYTOOLS] Proxy válido encontrado: %s (Tiempo: %.2fs)' % (proxy, info['time']))
                selected.append(proxy)
                if len(selected) >= PROXY_CONFIG['MAX_PROXIES_PER_CHANNEL']:
                    break
    
    if selected:
        config.set_setting('proxies', ', '.join(selected), canal)
        logger.info('[PROXYTOOLS] Proxies guardados para %s: %s' % (canal, ', '.join(selected)))
        return True
    else:
        logger.info('[PROXYTOOLS] No se encontraron proxies válidos tras probar %d candidatos' % total_tested)
        return False


def validar_proxies(proxies):
    """Valida y filtra lista de proxies por formato IP:PORT"""
    if not proxies:
        return []
    
    if not PY3:
        return list(filter(lambda x: re.match(r'\d+\.\d+\.\d+\.\d+:\d+', str(x)), proxies))
    else:
        pattern = re.compile(r'\d+\.\d+\.\d+\.\d+:\d+', re.DOTALL)
        return pattern.findall(str(proxies))


def testear_lista_proxies(url, proxies):
    """
    Testea lista de proxies en paralelo con timeout
    
    Args:
        url (str): URL para testear
        proxies (list): Lista de proxies en formato IP:PORT
        
    Returns:
        list: Lista de tuplas (proxy, info_dict) ordenadas por velocidad
    """
    logger.info('[PROXYTOOLS] Testeando %d proxies...' % len(proxies))
    
    results = []
    
    # Testear en paralelo con ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_proxy = {
            executor.submit(_test_single_proxy, proxy, url): proxy 
            for proxy in proxies
        }
        
        for future in as_completed(future_to_proxy, timeout=PROXY_CONFIG['SEARCH_TIMEOUT']):
            proxy = future_to_proxy[future]
            try:
                info = future.result()
                results.append((proxy, info))
            except Exception as e:
                logger.info('[PROXYTOOLS] Error testeando proxy %s: %s' % (proxy, str(e)))
                results.append((proxy, {'ok': False, 'time': 999, 'code': 'error', 'len': 0}))
    
    # Ordenar por velocidad (proxies válidos primero, luego por tiempo)
    results.sort(key=lambda x: (not x[1]['ok'], x[1]['time']))
    
    return results


def _test_single_proxy(proxy, url):
    """
    Testea un solo proxy
    
    Args:
        proxy (str): Proxy en formato IP:PORT
        url (str): URL para testear
        
    Returns:
        dict: Información del test {ok, time, code, len}
    """
    start_time = time.time()
    use_proxy = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
    
    try:
        resp = httptools.downloadpage(
            url, 
            use_proxy=use_proxy, 
            timeout=PROXY_CONFIG['PROXY_TEST_TIMEOUT'],
            raise_weberror=False,
            only_headers=True  # Solo headers para ser más rápido
        )
        
        elapsed = time.time() - start_time
        
        # Validar respuesta
        ok = (
            resp.sucess and 
            isinstance(resp.code, int) and 
            200 <= resp.code < 400
        )
        
        return {
            'ok': ok,
            'time': elapsed,
            'code': resp.code,
            'len': len(resp.data) if hasattr(resp, 'data') else 0
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'ok': False,
            'time': elapsed,
            'code': str(e)[:50],
            'len': 0
        }


# ============================================================================
# PROXY PROVIDERS - Solo los más rápidos
# ============================================================================

def _proxyscrape_com(url, tipo_proxy, pais_proxy, max_proxies):
    """
    Busca proxies en ProxyScrape.com (API - MUY RÁPIDO)
    API: https://proxyscrape.com/api-documentation
    """
    logger.info('[PROXYTOOLS] Buscando en proxyscrape.com')
    
    try:
        # API: https://proxyscrape.com/api-documentation
        url_provider = 'https://api.proxyscrape.com/?request=displayproxies'
        url_provider += '&proxytype=' + ('https' if url.startswith('https') else 'http')
        url_provider += '&ssl=all'
        if tipo_proxy: 
            url_provider += '&anonymity=' + tipo_proxy
        if pais_proxy: 
            url_provider += '&country=' + pais_proxy
        
        resp = httptools.downloadpage(
            url_provider, 
            timeout=5,
            raise_weberror=False
        )
        
        if resp.sucess:
            proxies = resp.data.split()
            logger.info('[PROXYTOOLS] Proxyscrape: %d proxies encontrados' % len(proxies))
            return proxies
        else:
            logger.info('[PROXYTOOLS] Proxyscrape falló: %s' % resp.code)
            return []
            
    except Exception as e:
        logger.info('[PROXYTOOLS] Error en proxyscrape: %s' % str(e))
        return []


def _free_proxy_list(url, tipo_proxy, pais_proxy, max_proxies):
    """Busca proxies en free-proxy-list.net"""
    logger.info('[PROXYTOOLS] Buscando en free-proxy-list.net')
    
    try:
        url_provider = 'https://free-proxy-list.net'
        resp = httptools.downloadpage(
            url_provider,
            timeout=5,
            raise_weberror=False
        )
        
        if not resp.sucess:
            logger.info('[PROXYTOOLS] Free-proxy-list falló: %s' % resp.code)
            return []
        
        proxies = []
        block = scrapertools.find_single_match(resp.data, 'Updated at(.*?)</textarea>')
        
        if block:
            enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')
            for prox in enlaces:
                if prox and '-' not in prox:
                    proxies.append(prox.strip())
        
        logger.info('[PROXYTOOLS] Free-proxy-list: %d proxies encontrados' % len(proxies))
        return proxies
        
    except Exception as e:
        logger.info('[PROXYTOOLS] Error en free-proxy-list: %s' % str(e))
        return []


# ============================================================================
# FUNCIONES ADICIONALES (pueden agregarse más proveedores si es necesario)
# ============================================================================

def limpiar_proxies_canal(canal):
    """Elimina proxies guardados de un canal"""
    config.set_setting('proxies', '', canal)
    logger.info('[PROXYTOOLS] Proxies eliminados para canal: %s' % canal)
