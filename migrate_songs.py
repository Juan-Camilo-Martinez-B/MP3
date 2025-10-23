"""
Script para migrar canciones existentes a la nueva estructura de Django
"""
import os
import sys
import shutil
import django

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_player.settings')
django.setup()

from player.models import Song


def get_mp3_duration(file_path):
    """Obtiene la duración de un archivo MP3"""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(file_path)
        return audio.info.length
    except:
        # Si no está mutagen instalado, intentar con pygame
        try:
            import pygame
            pygame.mixer.init()
            sound = pygame.mixer.Sound(file_path)
            return sound.get_length()
        except:
            return 0


def migrate_songs():
    """Migra las canciones de la carpeta songs a media/songs y las registra en la BD"""
    
    old_songs_dir = 'songs'
    new_songs_dir = 'media/songs'
    
    if not os.path.exists(old_songs_dir):
        print("[ERROR] No se encontro la carpeta 'songs'")
        return
    
    # Crear directorio de destino
    os.makedirs(new_songs_dir, exist_ok=True)
    
    # Obtener archivos MP3
    mp3_files = [f for f in os.listdir(old_songs_dir) if f.endswith('.mp3')]
    
    if not mp3_files:
        print("[INFO] No se encontraron archivos MP3 en la carpeta 'songs'")
        return
    
    print(f"\n{'='*60}")
    print(f"MIGRACION DE CANCIONES")
    print(f"{'='*60}\n")
    print(f"Encontradas {len(mp3_files)} canciones\n")
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for mp3_file in mp3_files:
        try:
            old_path = os.path.join(old_songs_dir, mp3_file)
            new_path = os.path.join(new_songs_dir, mp3_file)
            
            # Nombre de la canción (sin extensión)
            song_title = os.path.splitext(mp3_file)[0]
            
            # Verificar si ya existe en la BD
            if Song.objects.filter(title=song_title).exists():
                print(f"[SKIP] Ya existe: {song_title}")
                skipped += 1
                continue
            
            # Copiar archivo (no mover, por si acaso)
            if not os.path.exists(new_path):
                shutil.copy2(old_path, new_path)
            
            # Obtener duración del archivo
            duration = get_mp3_duration(new_path)
            
            # Crear registro en la BD
            relative_path = os.path.join('songs', mp3_file)
            song = Song.objects.create(
                title=song_title,
                file_path=relative_path,
                duration=duration
            )
            
            print(f"[OK] Migrado: {song_title}")
            migrated += 1
            
        except Exception as e:
            print(f"[ERROR] Error con {mp3_file}: {str(e)}")
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMEN")
    print(f"{'='*60}")
    print(f"[OK] Migradas: {migrated}")
    print(f"[SKIP] Ya existian: {skipped}")
    print(f"[ERROR] Errores: {errors}")
    print(f"{'='*60}\n")
    
    if migrated > 0:
        print("Migracion completada!")
        print("Las canciones originales se mantuvieron en la carpeta 'songs'")
        print("Puedes eliminar la carpeta 'songs' si lo deseas\n")


if __name__ == '__main__':
    try:
        migrate_songs()
    except Exception as e:
        print(f"\n[ERROR] Error durante la migracion: {str(e)}")
        print("Verifica que Django este configurado correctamente")

