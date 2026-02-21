# -*- coding: utf-8 -*-
"""
Setup script para crear la estructura del proyecto Stremio-Balandro
Copia los archivos necesarios desde plugin.video.balandro
"""

import os
import shutil
from pathlib import Path

# Rutas
source_dir = Path(r"c:/Users/admin/Downloads/plugin.video.balandro-4.0.22/plugin.video.balandro")
target_dir = Path(r"c:/Users/admin/Downloads/plugin.video.balandro-4.0.22/stremio-balandro")
balandro_src = target_dir / "balandro_src"

# Carpetas a copiar
folders_to_copy = ["channels", "servers", "core", "lib", "platformcode", "modules"]

print("🚀 Iniciando setup del proyecto Stremio-Balandro...")

# Crear carpeta principal
target_dir.mkdir(exist_ok=True)
print(f"✓ Carpeta principal creada: {target_dir}")

# Crear balandro_src
balandro_src.mkdir(exist_ok=True)
print(f"✓ Carpeta balandro_src creada: {balandro_src}")

# Copiar carpetas
for folder in folders_to_copy:
    src = source_dir / folder
    dst = balandro_src / folder
    
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        
        shutil.copytree(src, dst)
        print(f"✓ Copiada carpeta: {folder}")
        
        # Crear __init__.py si no existe
        init_file = dst / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"  ✓ Creado {folder}/__init__.py")
    else:
        print(f"⚠ Carpeta no encontrada (omitiendo): {folder}")

# Crear __init__.py en balandro_src
(balandro_src / "__init__.py").touch()
print(f"✓ Creado balandro_src/__init__.py")

print("\n✅ Setup completado exitosamente!")
print(f"📁 Proyecto creado en: {target_dir}")
print("\n🔧 Próximos pasos:")
print("  1. Revisar archivos generados")
print("  2. Instalar dependencias: pip install -r requirements.txt")
print("  3. Ejecutar servidor: uvicorn main:app --reload")
