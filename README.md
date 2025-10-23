# 🎵 MP3 Player - Mejor que Spotify

Un reproductor de música web moderno construido con Django y JavaScript vanilla. Permite descargar canciones de YouTube, crear playlists y reproducir música directamente en el navegador.

## ✨ Características

- 🎼 **Descarga de YouTube**: Descarga canciones directamente desde YouTube usando yt-dlp
- 📋 **Gestión de Playlists**: Crea y administra múltiples playlists
- 🎵 **Reproducción en Navegador**: Reproductor de audio HTML5 completo
- 🔀 **Mezclar Playlist**: Función de shuffle para reproducción aleatoria
- 📚 **Biblioteca Musical**: Organiza todas tus canciones descargadas
- 🎨 **Interfaz Moderna**: Diseño oscuro inspirado en aplicaciones modernas
- 📱 **Responsive**: Funciona en desktop y móviles

## 🚀 Instalación

### Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- FFmpeg (necesario para convertir audio)

#### Instalar FFmpeg

**Windows:**
```bash
# Usando Chocolatey
choco install ffmpeg

# O descarga desde: https://ffmpeg.org/download.html
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Configuración del Proyecto

1. **Clonar el repositorio** (o descomprimirlo)
```bash
cd Mp3
```

2. **Crear entorno virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno** (opcional)
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tu configuración
```

5. **Migrar la base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario** (opcional, para acceder al admin)
```bash
python manage.py createsuperuser
```

7. **Recolectar archivos estáticos**
```bash
python manage.py collectstatic --noinput
```

8. **Iniciar el servidor**
```bash
python manage.py runserver
```

9. **Abrir en el navegador**
```
http://localhost:8000
```

## 📖 Uso

### Descargar Canciones

1. Copia la URL de un video de YouTube
2. Pégala en el campo "YouTube URL" en la barra lateral
3. Haz clic en "Descargar"
4. La canción se agregará automáticamente a tu biblioteca

### Crear Playlists

1. Haz clic en el botón "+" junto a "Playlists"
2. Ingresa un nombre y descripción
3. Haz clic en "Crear"

### Agregar Canciones a Playlist

1. Ve a la pestaña "Biblioteca"
2. Haz clic en "➕ Agregar" en la canción deseada
3. La canción se agregará a la playlist activa

### Reproducir Música

1. Ve a la pestaña "Playlist Actual"
2. Haz clic en "▶️ Reproducir" en cualquier canción
3. Usa los controles en la barra inferior para:
   - Pausar/Reanudar
   - Canción anterior/siguiente
   - Ajustar volumen
   - Buscar en la canción

## 🏗️ Estructura del Proyecto

```
Mp3/
├── music_player/          # Configuración principal de Django
│   ├── settings.py        # Configuración del proyecto
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuración WSGI
├── player/               # Aplicación principal
│   ├── models.py         # Modelos de base de datos
│   ├── views.py          # Vistas y APIs
│   ├── urls.py           # URLs de la aplicación
│   ├── admin.py          # Configuración del admin
│   └── templates/        # Templates HTML
│       └── player/
│           └── index.html
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos
│   └── js/
│       └── app.js        # JavaScript principal
├── media/                # Archivos subidos
│   └── songs/            # Canciones descargadas
├── songs/                # Carpeta legacy (migrar a media/)
├── requirements.txt      # Dependencias Python
├── manage.py            # Utilidad de Django
├── Procfile             # Para despliegue en Heroku
├── runtime.txt          # Versión de Python
└── README.md            # Este archivo
```

## 🔧 Configuración para Producción

### Heroku

1. **Instalar Heroku CLI**
```bash
# Windows
choco install heroku-cli

# Linux/macOS
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Crear aplicación en Heroku**
```bash
heroku login
heroku create tu-music-player
```

3. **Agregar buildpacks**
```bash
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

4. **Configurar variables de entorno**
```bash
heroku config:set SECRET_KEY=tu-clave-secreta-muy-segura
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=tu-music-player.herokuapp.com
```

5. **Desplegar**
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

6. **Migrar base de datos**
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Railway / Render

Similar a Heroku, asegúrate de:
1. Configurar las variables de entorno
2. Instalar FFmpeg en el contenedor
3. Configurar el comando de inicio: `gunicorn music_player.wsgi`

## 🔒 Configuración de Seguridad

Para producción, actualiza `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']
SECRET_KEY = os.getenv('SECRET_KEY')  # Usar variable de entorno

# Configuración de seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
```

## 📝 API Endpoints

### Canciones
- `GET /api/songs/` - Listar todas las canciones
- `GET /api/songs/<id>/` - Detalle de una canción
- `POST /api/songs/download/` - Descargar de YouTube
- `POST /api/songs/<id>/play/` - Incrementar contador

### Playlists
- `GET /api/playlists/` - Listar playlists
- `GET /api/playlists/<id>/` - Detalle de playlist
- `POST /api/playlists/create/` - Crear playlist
- `POST /api/playlists/<id>/add/` - Agregar canción
- `POST /api/playlists/<id>/remove/` - Eliminar canción
- `POST /api/playlists/<id>/shuffle/` - Mezclar playlist
- `POST /api/playlists/<id>/set-active/` - Activar playlist
- `DELETE /api/playlists/<id>/delete/` - Eliminar playlist

## 🐛 Solución de Problemas

### FFmpeg no encontrado
```bash
# Verificar instalación
ffmpeg -version

# Si no está instalado, seguir las instrucciones de instalación arriba
```

### Error al descargar de YouTube
- Verifica que la URL sea válida
- Actualiza yt-dlp: `pip install --upgrade yt-dlp`
- Algunos videos pueden estar bloqueados por región o derechos de autor

### Canciones no se reproducen
- Verifica que los archivos existan en `media/songs/`
- Comprueba que el servidor esté sirviendo archivos media correctamente
- Revisa la consola del navegador para errores

### Estilos no cargan
```bash
python manage.py collectstatic --noinput
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👥 Autor

Desarrollado como proyecto académico para Diseño de Interfaces de Software.

## 🙏 Agradecimientos

- [Django](https://www.djangoproject.com/) - Framework web
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Descargador de YouTube
- [FFmpeg](https://ffmpeg.org/) - Procesamiento de audio
- Inspirado en Spotify y otras aplicaciones modernas de música

## 📞 Soporte

Si encuentras problemas o tienes sugerencias:
1. Revisa la sección de Solución de Problemas
2. Busca en issues existentes
3. Crea un nuevo issue con descripción detallada

---

**Nota**: Este proyecto es solo para uso educativo. Respeta los derechos de autor al descargar contenido de YouTube.

