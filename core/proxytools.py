# -*- coding: utf-8 -*-
"""
Simulación del módulo proxytools de Balandro
En serverless no usaremos proxies por ahora
"""

def configurar_proxies_canal(channel, host):
    """Mock function para configurar proxies"""
    print(f"[PROXY] Configuración de proxies no disponible en serverless para {channel}")
    return False

def get_proxy_list():
    """Mock function para obtener lista de proxies"""
    return []
