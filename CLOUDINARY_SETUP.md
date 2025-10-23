# Configuración de Cloudinary

Este proyecto utiliza Cloudinary para almacenar y servir archivos de audio (MP3) tanto en desarrollo local como en producción.

## ¿Por qué Cloudinary?

- **Almacenamiento en la nube**: Los archivos se almacenan en Cloudinary, no en el servidor
- **Funciona en Render**: Render no tiene almacenamiento persistente, por lo que necesitamos un servicio externo
- **Gratis para proyectos pequeños**: El plan gratuito de Cloudinary es suficiente para este proyecto
- **URLs accesibles globalmente**: Las canciones se pueden reproducir desde cualquier lugar

## Configuración

### 1. Variables de Entorno

Asegúrate de tener estas variables en tu `.env` (local) y en Render (producción):

```env
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

### 2. Migrar Canciones Existentes a Cloudinary

Si ya tienes canciones en `media/songs/`, ejecuta:

```bash
# En Windows
py upload_to_cloudinary.py

# En Linux/Mac
python3 upload_to_cloudinary.py
```

Este script:
- Busca todas las canciones con rutas locales en la base de datos
- Las sube a Cloudinary
- Actualiza la base de datos con las URLs de Cloudinary

### 3. Descargas Nuevas

Cuando descargas una canción de YouTube (solo en local):
- El archivo MP3 se descarga temporalmente
- Se sube automáticamente a Cloudinary
- Se guarda la URL de Cloudinary en la base de datos
- El archivo temporal se elimina

## Cómo Funciona

### Desarrollo Local
- `ENABLE_YOUTUBE_DOWNLOAD = True` (porque no hay `DATABASE_URL`)
- Puedes descargar canciones de YouTube
- Las canciones se suben a Cloudinary automáticamente
- Puedes reproducir canciones desde Cloudinary

### Producción (Render)
- `ENABLE_YOUTUBE_DOWNLOAD = False` (porque existe `DATABASE_URL`)
- Las descargas están deshabilitadas (modo demostración)
- Las canciones se reproducen desde Cloudinary
- No hay archivos locales en el servidor

## Verificar que Todo Funciona

1. **Verificar configuración**:
```bash
py -c "from django.conf import settings; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_player.settings'); import django; django.setup(); print('Cloudinary:', settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'))"
```

2. **Verificar canciones en BD**:
```bash
py manage.py shell
>>> from player.models import Song
>>> for song in Song.objects.all()[:3]:
...     print(f"{song.title}: {song.file_path}")
```

Deberías ver URLs que empiezan con `https://res.cloudinary.com/...`

## Solución de Problemas

### Las canciones no se reproducen en Render
1. Verifica que las variables de entorno de Cloudinary estén configuradas en Render
2. Asegúrate de haber ejecutado `upload_to_cloudinary.py` para migrar las canciones
3. Verifica que las URLs en la base de datos sean de Cloudinary (empiecen con `https://`)

### Error al subir a Cloudinary
1. Verifica que las credenciales sean correctas
2. Verifica que tengas espacio disponible en tu cuenta de Cloudinary
3. Revisa los logs para ver el error específico

## Desplegar en Render

### 1. Exportar Datos de Canciones

Antes de desplegar, exporta las canciones a JSON:

```bash
py export_songs_data.py
```

Esto genera `songs_data.json` con todas las canciones y sus URLs de Cloudinary.

### 2. Configurar Variables de Entorno en Render

En el dashboard de Render, configura:

```
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
DATABASE_URL=(se configura automáticamente)
SECRET_KEY=tu_secret_key_segura
ALLOWED_HOSTS=tu-app.onrender.com
DEBUG=False
```

### 3. Desplegar y Cargar Datos

Después del despliegue, desde la terminal de Render:

```bash
python manage.py migrate
python manage.py loaddata songs_data.json
```

O crea un script de inicialización en Render que haga esto automáticamente.

## Notas Importantes

- **Límite del plan gratuito**: 25 GB de almacenamiento y 25 GB de transferencia mensual
- **Backup**: Las canciones están en Cloudinary, no olvides mantener una copia local si son importantes
- **URLs permanentes**: Las URLs de Cloudinary son permanentes mientras no elimines los archivos
- **Base de datos**: El archivo `songs_data.json` contiene los metadatos, las canciones están en Cloudinary

