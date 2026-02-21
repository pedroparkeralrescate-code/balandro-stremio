# -*- coding: utf-8 -*-
"""
Patcher Module - Sobrescribe funciones de Balandro para usar cloudscraper
"""

import cloudscraper
from typing import Optional, Dict, Any
import sys


def apply_patches():
    """
    Aplica monkey patches a las funciones de httptools de Balandro
    para usar cloudscraper en lugar de urllib y evitar bloqueos de Cloudflare
    """
    
    import os
    import sys
    
    # Asegurar que balandro_src esté en el path temporalmente si no lo está
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'balandro_src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        
    # Importar httptools EXACTAMENTE de la misma forma que los canales lo importan
    # para no crear dos instancias del módulo en memoria (core.httptools vs balandro_src.core.httptools)
    try:
        from core import httptools
    except ImportError as e:
        print(f"⚠ Error importando httptools: {e}")
        return
    
    # Guardar funciones originales por si acaso
    original_downloadpage = httptools.downloadpage
    original_downloadpage_proxy = httptools.downloadpage_proxy
    
    # ========================================================================
    # Función parcheada downloadpage
    # ========================================================================
    def patched_downloadpage(url, post=None, headers=None, timeout=None, 
                            follow_redirects=True, cookies=True, 
                            replace_headers=False, add_referer=False, 
                            only_headers=False, bypass_cloudflare=True, 
                            count_retries=0, raise_weberror=True, 
                            use_proxy=None, use_cache=False, cache_duration=36000):
        """
        Versión parcheada de httptools.downloadpage que usa cloudscraper
        Preserva TODOS los headers personalizados que Balandro intenta enviar
        """
        
        # Crear scraper de cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Configurar timeout
        if timeout is None:
            timeout = 30
        
        # Preparar headers
        request_headers = {}
        
        # Headers por defecto
        if not replace_headers:
            request_headers['User-Agent'] = httptools.get_user_agent()
        
        # CRÍTICO: Preservar headers personalizados del caller
        if headers:
            request_headers.update(headers)
        
        # Agregar Referer si se solicita
        if add_referer and 'Referer' not in request_headers:
            request_headers['Referer'] = url
        
        try:
            # Realizar request con cloudscraper
            if post is not None:
                # POST request
                if isinstance(post, dict):
                    response = scraper.post(url, data=post, headers=request_headers, 
                                          timeout=timeout, allow_redirects=follow_redirects)
                else:
                    response = scraper.post(url, data=post, headers=request_headers, 
                                          timeout=timeout, allow_redirects=follow_redirects)
            else:
                # GET request
                response = scraper.get(url, headers=request_headers, timeout=timeout, 
                                      allow_redirects=follow_redirects)
            
            # Verificar status code
            if raise_weberror:
                response.raise_for_status()
            
            # Retornar solo headers si se solicita
            if only_headers:
                # Crear objeto similar al de httptools
                class HeadersResponse:
                    def __init__(self, headers):
                        self.headers = dict(headers)
                        self.data = ''
                
                return HeadersResponse(response.headers)
            
            # Guardar cookies si está habilitado
            if cookies:
                try:
                    # Actualizar cookie jar de httptools
                    for cookie in scraper.cookies:
                        httptools.cj.set_cookie(cookie)
                    httptools.save_cookies()
                except Exception as e:
                    print(f"⚠ Error guardando cookies: {e}")
            
            # Crear objeto de respuesta compatible con httptools
            class CompatResponse:
                def __init__(self, response):
                    # En Python 3, httptools devuelve str, no bytes.
                    # Usamos response.text en lugar de response.content
                    self.data = response.text
                    self.headers = dict(response.headers)
                    self.code = response.status_code
                    self.url = response.url
                    
            print(f"🌍 [PATCHER] URL: {url} | Status: {response.status_code} | Bytes: {len(response.content)}")
            return CompatResponse(response)
            
        except Exception as e:
            print(f"❌ Error en downloadpage: {url} - {e}")
            
            # Si raise_weberror está deshabilitado, retornar respuesta vacía
            if not raise_weberror:
                class EmptyResponse:
                    data = ''
                    headers = {}
                    code = 0
                    url = url
                return EmptyResponse()
            else:
                raise
    
    # ========================================================================
    # Función parcheada downloadpage_proxy
    # ========================================================================
    def patched_downloadpage_proxy(canal, url, post=None, headers=None, timeout=None,
                                   follow_redirects=True, cookies=True, 
                                   replace_headers=False, add_referer=False,
                                   only_headers=False, bypass_cloudflare=True, 
                                   count_retries=0, raise_weberror=True,
                                   use_proxy=None, use_cache=False, cache_duration=36000):
        """
        Versión parcheada de httptools.downloadpage_proxy
        
        NOTA: En Render, normalmente no necesitamos proxies adicionales,
        pero mantenemos la misma signature para compatibilidad.
        Si se necesitan proxies reales, cloudscraper puede configurarse aquí.
        """
        
        # Por ahora, simplemente llamar a la versión sin proxy
        # En producción, aquí se configuraría cloudscraper con proxies si es necesario
        return patched_downloadpage(url, post=post, headers=headers, timeout=timeout,
                                   follow_redirects=follow_redirects, cookies=cookies,
                                   replace_headers=replace_headers, add_referer=add_referer,
                                   only_headers=only_headers, bypass_cloudflare=bypass_cloudflare,
                                   count_retries=count_retries, raise_weberror=raise_weberror,
                                   use_proxy=use_proxy, use_cache=use_cache, 
                                   cache_duration=cache_duration)
    
    # ========================================================================
    # Aplicar patches
    # ========================================================================
    httptools.downloadpage = patched_downloadpage
    httptools.downloadpage_proxy = patched_downloadpage_proxy
    
    print("✓ Patches aplicados a httptools (cloudscraper habilitado)")
    print("  • downloadpage() ahora usa cloudscraper")
    print("  • downloadpage_proxy() ahora usa cloudscraper")
    print("  • Headers personalizados preservados")
