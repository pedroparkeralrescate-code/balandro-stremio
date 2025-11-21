# Guía de Despliegue en Vercel

## Opción 1: Despliegue con Vercel CLI (Recomendado)

### 1. Instalar Vercel CLI

```bash
npm install -g vercel
```

### 2. Login en Vercel

```bash
vercel login
```

### 3. Desplegar el proyecto

Desde el directorio `balandro-stremio`:

```bash
vercel
```

Sigue las instrucciones:
- Set up and deploy? **Y**
- Which scope? Selecciona tu cuenta
- Link to existing project? **N**
- What's your project's name? `balandro-stremio`
- In which directory is your code located? `./`
- Want to override the settings? **N**

### 4. Obtener la URL

Al finalizar, Vercel te dará una URL como:
```
https://balandro-stremio-xxx.vercel.app
```

### 5. Instalar en Stremio

1. Abre Stremio
2. Ve a **Add-ons**
3. Click en el icono de puzzle (arriba a la derecha)
4. Pega la URL: `https://balandro-stremio-xxx.vercel.app/manifest.json`
5. Click en **Install**

¡Listo! 🎉

---

## Opción 2: Despliegue desde GitHub

### 1. Crear repositorio en GitHub

```bash
cd balandro-stremio
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/balandro-stremio.git
git push -u origin main
```

### 2. Importar en Vercel

1. Ve a https://vercel.com/new
2. Importa tu repositorio de GitHub
3. Configura el proyecto:
   - **Framework Preset**: Other
   - **Build Command**: (dejar vacío)
   - **Output Directory**: (dejar vacío)
4. Click en **Deploy**

### 3. Variables de Entorno (Opcional)

Si quieres configurar API keys de TMDB:

1. En Vercel > Settings > Environment Variables
2. Agregar:
   - `TMDB_API_KEY`: tu API key de TMDB

---

## Testing Local

Para probar localmente antes de desplegar:

```bash
# Instalar Vercel CLI
npm install -g vercel

# Ejecutar en modo development
vercel dev
```

Luego abre: http://localhost:3000/manifest.json

---

## Troubleshooting

### Error: "Module not found"

Asegúrate de que `requirements.txt` esté en la raíz del proyecto y ejecuta:

```bash
vercel --force
```

### Error: "Function timeout"

Los channels pueden tardar mucho. Esto es normal. Stremio mostrará los streams que lleguen antes del timeout.

### No aparecen streams

1. Verifica los logs en Vercel Dashboard
2. Algunos channels pueden estar caídos
3. Prueba con diferentes películas/series

### Modificar channels activos

Edita `api/streams.py` y modifica la lista `PRIORITY_CHANNELS` con los channels que quieras usar.

---

## Mantenimiento

### Actualizar channels

Si Balandro actualiza sus channels:

1. Copia los nuevos archivos .py a `channels/`
2. Ejecuta: `python update_imports.py`
3. Despliega de nuevo: `vercel --prod`

### Ver logs

```bash
vercel logs
```

O desde el dashboard de Vercel: https://vercel.com/dashboard
