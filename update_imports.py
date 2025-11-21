#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar imports en todos los archivos de channels y servers
Convierte los imports de Kodi a nuestro adaptador
"""

import os
import re
import glob

def update_imports_in_file(filepath):
    """Actualiza los imports en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # Reemplazar imports de platformcode
        if 'from platformcode import' in content:
            # No hacer nada, ya funciona con nuestro adaptador
            pass
        
        # Reemplazar imports de core que pueden faltar
        replacements = [
            # Añadir sys.path si no existe
            (r'^(# -\*- coding: utf-8 -\*-\s*\n)', 
             r'\1\nimport sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n'),
        ]
        
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                modified = True
        
        # Guardar solo si se modificó
        if modified and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")
        return False

def main():
    """Procesa todos los archivos de channels y servers"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Procesar channels
    channels_dir = os.path.join(base_dir, 'channels')
    channel_files = glob.glob(os.path.join(channels_dir, '*.py'))
    
    print(f"Procesando {len(channel_files)} channels...")
    updated = 0
    for filepath in channel_files:
        if '__init__' in filepath:
            continue
        if update_imports_in_file(filepath):
            updated += 1
            print(f"  ✓ {os.path.basename(filepath)}")
    
    print(f"\nChannels actualizados: {updated}/{len(channel_files)}")
    
    # Procesar servers
    servers_dir = os.path.join(base_dir, 'servers')
    server_files = glob.glob(os.path.join(servers_dir, '*.py'))
    
    print(f"\nProcesando {len(server_files)} servers...")
    updated = 0
    for filepath in server_files:
        if '__init__' in filepath:
            continue
        if update_imports_in_file(filepath):
            updated += 1
            print(f"  ✓ {os.path.basename(filepath)}")
    
    print(f"\nServers actualizados: {updated}/{len(server_files)}")
    
    print("\n✅ Proceso completado!")

if __name__ == '__main__':
    main()
