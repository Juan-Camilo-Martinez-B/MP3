# 🚀 Guía Rápida de Inicio

## Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Paso 2: Migrar Base de Datos

```bash
python manage.py migrate
```

## Paso 3: (Opcional) Migrar Canciones Existentes

Si tienes canciones en la carpeta `songs/`:

```bash
python migrate_songs.py
```

## Paso 4: Iniciar Servidor

### Opción A - Usando el script (Windows):
```bash
start.bat
```

### Opción B - Manualmente:
```bash
python manage.py runserver
```

## Paso 5: Abrir en Navegador

```
http://localhost:8000
```

---

## 📋 Comandos Útiles

### Crear Superusuario (acceso al admin)
```bash
python manage.py createsuperuser
```

### Panel de Administración
```
http://localhost:8000/admin
```

### Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

---

## 🎵 Uso Básico

1. **Descargar Canción**: Pega una URL de YouTube en la barra lateral y haz clic en "Descargar"
2. **Ver Biblioteca**: Pestaña "Biblioteca" muestra todas tus canciones
3. **Crear Playlist**: Botón "+" en la sección de Playlists
4. **Agregar a Playlist**: En la biblioteca, haz clic en "➕ Agregar"
5. **Reproducir**: Ve a "Playlist Actual" y haz clic en "▶️ Reproducir"

---

## ⚠️ Solución de Problemas

### FFmpeg no está instalado
Descarga desde: https://ffmpeg.org/download.html

### Canciones no se reproducen
Verifica que los archivos existan en `media/songs/`

### Error de permisos
Ejecuta PowerShell como administrador (Windows)

---

## 📚 Más Información

Consulta el README.md completo para documentación detallada.

