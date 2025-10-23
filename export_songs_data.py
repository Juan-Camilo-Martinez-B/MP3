"""
Script para exportar datos de canciones a JSON para importar en producción
"""
import os
import sys
import django
import json

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_player.settings')
django.setup()

from player.models import Song
from django.core import serializers


def export_songs():
    """Exporta las canciones a un archivo JSON"""
    
    print("\n" + "="*60)
    print("EXPORTANDO CANCIONES A JSON")
    print("="*60 + "\n")
    
    songs = Song.objects.all()
    
    if not songs:
        print("[INFO] No hay canciones para exportar")
        return
    
    print(f"Encontradas {songs.count()} canciones\n")
    
    # Serializar a JSON
    data = serializers.serialize('json', songs, indent=2)
    
    # Guardar en archivo
    output_file = 'songs_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(data)
    
    print(f"[OK] Canciones exportadas a: {output_file}")
    print(f"[OK] Total: {songs.count()} canciones")
    
    # Verificar que todas tengan URLs de Cloudinary
    cloudinary_count = 0
    local_count = 0
    
    for song in songs:
        file_path_str = str(song.file_path)
        if file_path_str.startswith('http'):
            cloudinary_count += 1
        else:
            local_count += 1
            print(f"[WARNING] Ruta local encontrada: {song.title} -> {file_path_str}")
    
    print(f"\n[INFO] URLs de Cloudinary: {cloudinary_count}")
    print(f"[INFO] Rutas locales: {local_count}")
    
    if local_count > 0:
        print("\n[WARNING] Algunas canciones tienen rutas locales.")
        print("          Ejecuta 'py upload_to_cloudinary.py' primero.")
    else:
        print("\n[OK] Todas las canciones usan Cloudinary!")
        print("\nPara importar en producción:")
        print("1. Sube 'songs_data.json' a Render")
        print("2. Ejecuta: python manage.py loaddata songs_data.json")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        export_songs()
    except Exception as e:
        print(f"\n[ERROR] Error durante la exportación: {str(e)}")
        import traceback
        traceback.print_exc()

