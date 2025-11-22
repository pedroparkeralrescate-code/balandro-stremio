# Guía de Despliegue en Render (Recomendado)

Render es una excelente opción gratuita para alojar este addon.

## 1. Preparación

El proyecto ya está configurado para Render con:
- `main.py`: Aplicación Flask
- `requirements.txt`: Dependencias (Flask, Gunicorn)
- `render.yaml`: Configuración de infraestructura

## 2. Crear Repositorio en GitHub

1. Ve a [GitHub](https://github.com/new) y crea un repositorio público llamado `balandro-stremio`.
2. Sube el código (ejecuta esto en tu terminal):

```bash
git remote add origin https://github.com/TU_USUARIO/balandro-stremio.git
git branch -M main
git push -u origin main
```

## 3. Desplegar en Render

1. Ve a [Render Dashboard](https://dashboard.render.com/).
2. Haz clic en **New +** y selecciona **Web Service**.
3. Conecta tu cuenta de GitHub y selecciona el repositorio `balandro-stremio`.
4. Render detectará automáticamente la configuración.
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`
5. Haz clic en **Create Web Service**.

## 4. Finalizar

Render desplegará tu addon y te dará una URL (ej. `https://balandro-stremio.onrender.com`).

1. Copia esa URL.
2. Añade `/manifest.json` al final.
3. Pégala en el buscador de Stremio para instalar.

---

# Opción Alternativa: Vercel

Si prefieres Vercel:

1. Instala Vercel CLI: `npm i -g vercel`
2. Ejecuta `vercel` en la carpeta del proyecto.
3. Sigue las instrucciones en pantalla.
