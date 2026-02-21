# Stremio-Balandro Addon

Addon de Stremio que replica la funcionalidad del popular plugin **Balandro** de Kodi, proporcionando acceso a contenido en español mediante una API REST desplegable en Render.

## 🎯 Características

- ✅ **Integración completa con Balandro**: Usa los mismos canales y resolvers que el plugin de Kodi
- ✅ **Stateless**: IDs serializados en Base64 para compatibilidad total con Stremio
- ✅ **Cloudflare Bypass**: Usa `cloudscraper` para evitar bloqueos
- ✅ **Búsqueda integrada**: Busca contenido directamente desde Stremio
- ✅ **Múltiples canales**: CineCalidad, PelisPlus, Cuevana3 y más
- ✅ **Deploy en Render**: Optimizado para el Free Tier

## 📁 Estructura del Proyecto

```
stremio-balandro/
├── main.py              # Servidor FastAPI con endpoints de Stremio
├── addon.py             # Lógica de adaptación Balandro ↔ Stremio
├── kodi_mock.py         # Mocks de librerías de Kodi
├── patcher.py           # Patches para usar cloudscraper
├── setup_project.py     # Script para copiar archivos de Balandro
├── requirements.txt     # Dependencias Python
├── run.sh              # Script de inicio para Render
├── balandro_src/       # Código fuente de Balandro (se copia automáticamente)
│   ├── channels/       # Canales (cinecalidad, pelisplus, etc.)
│   ├── servers/        # Resolvers de video
│   ├── core/           # Núcleo de Balandro
│   └── lib/            # Librerías auxiliares
└── README.md           # Este archivo
```

## 🚀 Instalación Local

### 1. Ejecutar Setup

```bash
cd c:/Users/admin/Downloads/plugin.video.balandro-4.0.22/stremio-balandro
python setup_project.py
```

Esto copiará automáticamente las carpetas necesarias desde `plugin.video.balandro`.

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar Servidor

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --reload --port 8000
```

### 4. Verificar Funcionamiento

Abre en tu navegador:
- **Health check**: http://localhost:8000/health
- **Manifest**: http://localhost:8000/manifest.json
- **Catálogo de ejemplo**: http://localhost:8000/catalog/movie/cinecalidad-movies.json

## ☁️ Deployment en Render

### Opción 1: Desde Repositorio Git

1. Sube el proyecto a GitHub/GitLab
2. Ve a [Render.com](https://render.com) y crea una cuenta
3. Crear **New Web Service**
4. Conecta tu repositorio
5. Configuración:
   - **Name**: `stremio-balandro`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash run.sh`
6. Click en **Create Web Service**

### Opción 2: Deploy Manual

1. Ve a [Render.com](https://render.com)
2. Crear **New Web Service** → **Deploy from GitHub**
3. Sigue los mismos pasos de configuración

### Variables de Entorno (Opcional)

En la sección **Environment** de Render, puedes configurar:

```
PORT=8000  (Render lo configura automáticamente)
```

## 🎬 Usar en Stremio

### 1. Obtener URL del Addon

Después del deploy en Render, copia tu URL (ej: `https://stremio-balandro.onrender.com`)

### 2. Instalar en Stremio

1. Abre **Stremio**
2. Ve a **Addons** (icono de puzzle)
3. En la esquina superior derecha, click en **Install from URL**
4. Pega tu URL + `/manifest.json`:
   ```
   https://stremio-balandro.onrender.com/manifest.json
   ```
5. Click en **Install**

### 3. Usar el Addon

- Ve a **Discover** o **Board**
- Busca contenido o navega los catálogos
- Los streams de Balandro aparecerán automáticamente

## 🔧 Arquitectura Técnica

### Flujo de Datos

```
Stremio Client
    ↓
FastAPI Server (main.py)
    ↓
Adapter (addon.py) ← serializa/deserializa Items
    ↓
Balandro Channels (balandro_src/channels/)
    ↓
Balandro Servers (balandro_src/servers/)
    ↓
cloudscraper (patcher.py) ← evita Cloudflare
    ↓
Video URLs finales
```

### Componentes Clave

#### 1. **Kodi Mocking** (`kodi_mock.py`)
Simula las librerías de Kodi (`xbmc`, `xbmcgui`, `xbmcaddon`, `xbmcplugin`) para que Balandro funcione sin Kodi.

#### 2. **HTTP Patching** (`patcher.py`)
Sobrescribe `httptools.downloadpage()` para usar `cloudscraper` en lugar de `urllib`, evitando bloqueos de Cloudflare.

**CRÍTICO**: Preserva headers personalizados (Referer, User-Agent) que los canales de Balandro necesitan.

#### 3. **Adapter** (`addon.py`)
- **Serialización Stateless**: Convierte `Item` objects a IDs Base64 (`balandro:BASE64_DATA`)
- **Conversión de Formato**: Transforma `Item` de Balandro a `Meta` de Stremio
- **Carga Dinámica**: Importa canales de Balandro on-demand
- **Resolución de Video**: Llama a resolvers de Balandro para obtener URLs finales

#### 4. **FastAPI Server** (`main.py`)
Endpoints implementados:
- `GET /manifest.json` - Metadatos del addon
- `GET /catalog/{type}/{id}.json?search={query}` - Catálogos con búsqueda
- `GET /meta/{type}/{id}.json` - Detalles de un item
- `GET /stream/{type}/{id}.json` - URLs de video

## ⚠️ Limitaciones Conocidas

### Render Free Tier
- ⏰ El servicio se duerme después de 15 minutos de inactividad
- 🐌 Primera request puede tardar 30-60 segundos (cold start)
- 💾 Límites de CPU/memoria pueden afectar scraping intensivo

### Proxy/Cloudflare
- 🛡️ Algunos canales pueden requerir proxies adicionales
- 🌐 IPs de Render pueden estar bloqueadas por ciertos sitios
- ✅ `cloudscraper` mitiga la mayoría de bloqueos básicos

### Stremio
- 🔗 IDs muy largos (Base64) pueden causar problemas en URLs
- 📱 No todos los servers de video funcionan en todas las plataformas de Stremio

## 🐛 Troubleshooting

### El servidor no arranca
```bash
# Verificar imports
python -c "import kodi_mock; import patcher; import addon; import main"

# Verificar dependencias
pip install -r requirements.txt --upgrade
```

### No aparecen streams
- Verifica que el canal funcione en Balandro original
- Revisa logs del servidor para errores de scraping
- Algunos sitios pueden estar caídos temporalmente

### Errores de Cloudflare
- `cloudscraper` debería manejar la mayoría de casos
- Si persiste, el sitio puede requerir proxies reales (no implementado en v1)

### Cold Start lento en Render
- Es normal en Free Tier
- Considera upgrade a plan pago para instancias persistentes

## 🔄 Actualizar Código de Balandro

Si Balandro se actualiza:

```bash
# Re-ejecutar setup
python setup_project.py

# Esto sobrescribirá balandro_src/ con la nueva versión
```

## 📝 Notas de Desarrollo

### Testing Local

```bash
# Ejecutar en modo desarrollo
uvicorn main:app --reload --port 8000

# Probar endpoints
curl http://localhost:8000/manifest.json
curl http://localhost:8000/catalog/movie/cinecalidad-movies.json
```

### Agregar Más Canales

Edita `main.py` y agrega canales a `AVAILABLE_CHANNELS`:

```python
AVAILABLE_CHANNELS = [
    # ... existentes
    {
        'id': 'nuevo_canal',
        'name': 'Nuevo Canal',
        'types': ['movie', 'series']
    },
]
```

### Debugging

Activa logs detallados:

```python
# En main.py
uvicorn.run(..., log_level="debug")
```

## 📄 Licencia

Este proyecto usa código de **Balandro**, que está bajo su propia licencia. Este adaptador es un wrapper que facilita su uso desde Stremio.

## 🙏 Créditos

- **Balandro Team**: Por el excelente plugin de Kodi
- **Stremio**: Por la plataforma de addons
- **cloudscraper**: Por el bypass de Cloudflare

---

**⚠️ Disclaimer**: Este addon es solo para fines educativos. Los usuarios son responsables del contenido al que acceden.
