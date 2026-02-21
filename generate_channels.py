# -*- coding: utf-8 -*-
"""
Script para generar all_channels.py con TODOS los canales
"""

import os
import json
from pathlib import Path

balandro_channels = Path("balandro_src/channels")

# Leer todos los archivos .py (canales)
channels_list = []

for py_file in sorted(balandro_channels.glob("*.py")):
    if py_file.stem == "__init__":
        continue
    
    channel_id = py_file.stem
    
    # Intentar leer JSON si existe
    json_file = balandro_channels / f"{channel_id}.json"
    
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            channel_name = data.get('name', channel_id.capitalize())
            categories = data.get('categories', [])
            
            # Determinar tipos
            types = []
            if 'movie' in categories or 'vos' in categories:
                types.append('movie')
            if 'tvshow' in categories or 'anime' in categories or 'dorama' in categories:
                types.append('series')
            
            if not types:
                types = ['movie', 'series']
        
        except:
            channel_name = channel_id.capitalize()
            types = ['movie', 'series']
    else:
        channel_name = channel_id.capitalize()
        types = ['movie', 'series']
    
    channels_list.append({
        'id': channel_id,
        'name': channel_name,
        'types': types
    })

# Escribir archivo Python
with open('all_channels.py', 'w', encoding='utf-8') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('# Lista completa de canales de Balandro\n')
    f.write(f'# Total: {len(channels_list)} canales\n\n')
    f.write('ALL_CHANNELS = [\n')
    
    for ch in channels_list:
        types_str = str(ch['types']).replace("'", '"')
        f.write(f'    {{"id": "{ch["id"]}", "name": "{ch["name"]}", "types": {types_str}}},\n')
    
    f.write(']\n')

print(f"✓ Generado all_channels.py con {len(channels_list)} canales")
