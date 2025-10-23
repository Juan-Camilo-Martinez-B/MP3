"""
Script para subir todas las canciones locales a Cloudinary
"""
import os
import sys

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_player.settings')
django.setup()

from player.models import Song
import cloudinary.uploader
from pathlib import Path
from django.conf import settings


def upload_songs_to_cloudinary():
    """Sube todas las canciones con rutas locales a Cloudinary"""
    
    print("\n" + "="*60)
    print("SUBIENDO CANCIONES A CLOUDINARY")
    print("="*60 + "\n")
    
    # Obtener todas las canciones
    songs = Song.objects.all()
    
    if not songs:
        print("[INFO] No hay canciones en la base de datos")
        return
    
    print(f"Encontradas {songs.count()} canciones\n")
    
    uploaded = 0
    skipped = 0
    errors = 0
    
    for song in songs:
        try:
            file_path_str = str(song.file_path)
            
            # Si ya es una URL de Cloudinary, saltar
            if file_path_str.startswith('http'):
                print(f"[SKIP] Ya en Cloudinary: {song.title}")
                skipped += 1
                continue
            
            # Construir ruta completa del archivo local
            local_path = os.path.join(settings.MEDIA_ROOT, file_path_str)
            
            # Verificar si el archivo existe localmente
            if not os.path.exists(local_path):
                print(f"[ERROR] Archivo no encontrado: {song.title} -> {local_path}")
                errors += 1
                continue
            
            print(f"[UPLOAD] Subiendo: {song.title}...")
            
            # Subir directamente a Cloudinary usando su API
            cloudinary_response = cloudinary.uploader.upload(
                local_path,
                resource_type="video",  # MP3 se sube como video en Cloudinary
                folder="songs",
                public_id=os.path.splitext(os.path.basename(local_path))[0],
                overwrite=True
            )
            
            cloudinary_url = cloudinary_response['secure_url']
            
            # Actualizar la base de datos con la URL de Cloudinary
            # Guardamos la URL directamente como string
            song.file_path = cloudinary_url
            song.save()
            
            print(f"[OK] Subida: {song.title}")
            print(f"     URL: {cloudinary_url[:70]}...")
            uploaded += 1
            
        except Exception as e:
            print(f"[ERROR] Error con {song.title}: {str(e)}")
            errors += 1
    
    print(f"\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"[OK] Subidas: {uploaded}")
    print(f"[SKIP] Ya en Cloudinary: {skipped}")
    print(f"[ERROR] Errores: {errors}")
    print("="*60 + "\n")
    
    if uploaded > 0:
        print("* Canciones subidas exitosamente a Cloudinary!")
        print("* Ahora puedes desplegar en Render sin problemas\n")


if __name__ == '__main__':
    try:
        # Verificar que Cloudinary esté configurado
        if not settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'):
            print("[ERROR] Cloudinary no está configurado correctamente")
            print("Verifica las variables de entorno:")
            print("  - CLOUDINARY_CLOUD_NAME")
            print("  - CLOUDINARY_API_KEY")
            print("  - CLOUDINARY_API_SECRET")
            sys.exit(1)
        
        upload_songs_to_cloudinary()
    except Exception as e:
        print(f"\n[ERROR] Error durante la subida: {str(e)}")
        import traceback
        traceback.print_exc()

