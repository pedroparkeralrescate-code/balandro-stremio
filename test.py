#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba básico para verificar que los módulos funcionan
"""

import sys
import os

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_platformcode():
    """Test del módulo platformcode"""
    print("=" * 50)
    print("TEST: platformcode")
    print("=" * 50)
    
    try:
        from core import platformcode
        print("✓ platformcode importado correctamente")
        print(f"✓ Config: {platformcode.config.__addon_name}")
        platformcode.logger.info("Test de logger")
        print("✓ Logger funciona")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_core_modules():
    """Test de módulos core"""
    print("\n" + "=" * 50)
    print("TEST: Core modules")
    print("=" * 50)
    
    modules = ['httptools', 'scrapertools', 'servertools', 'item', 'tmdb', 'jsontools']
    success = 0
    
    for module_name in modules:
        try:
            module = __import__(f'core.{module_name}', fromlist=[module_name])
            print(f"✓ {module_name} importado")
            success += 1
        except Exception as e:
            print(f"✗ {module_name} ERROR: {e}")
    
    return success == len(modules)

def test_channel():
    """Test de un channel específico"""
    print("\n" + "=" * 50)
    print("TEST: Channel cuevana3")
    print("=" * 50)
    
    try:
        from channels import cuevana3
        from core.item import Item
        
        print("✓ cuevana3 importado")
        
        # Test search
        item = Item(channel='cuevana3', search_type='movie')
        print("✓ Item creado")
        
        if hasattr(cuevana3, 'search'):
            print("✓ Method search encontrado")
        
        if hasattr(cuevana3, 'findvideos'):
            print("✓ Method findvideos encontrado")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server():
    """Test de un server específico"""
    print("\n" + "=" * 50)
    print("TEST: Server fembed")
    print("=" * 50)
    
    try:
        from servers import fembed
        
        print("✓ fembed importado")
        
        if hasattr(fembed, 'get_video_url'):
            print("✓ Method get_video_url encontrado")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 50)
    print("BALANDRO STREMIO - TESTS")
    print("=" * 50 + "\n")
    
    results = {
        'platformcode': test_platformcode(),
        'core_modules': test_core_modules(),
        'channel': test_channel(),
        'server': test_server()
    }
    
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("=" * 50 + "\n")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
