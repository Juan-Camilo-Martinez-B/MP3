"""
Comando de management para cargar datos iniciales de canciones
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from player.models import Song
import os


class Command(BaseCommand):
    help = 'Carga los datos iniciales de canciones si no existen'

    def handle(self, *args, **options):
        # Verificar si ya hay canciones en la base de datos
        song_count = Song.objects.count()
        
        if song_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Ya hay {song_count} canciones en la base de datos. '
                    'No se cargan datos iniciales.'
                )
            )
            return
        
        # Verificar si existe el archivo songs_data.json
        fixture_file = 'songs_data.json'
        if not os.path.exists(fixture_file):
            self.stdout.write(
                self.style.WARNING(
                    f'[WARNING] No se encontro el archivo {fixture_file}. '
                    'Saltando carga de datos iniciales.'
                )
            )
            return
        
        # Cargar los datos
        self.stdout.write('Cargando datos iniciales de canciones...')
        try:
            call_command('loaddata', fixture_file, verbosity=0)
            new_count = Song.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] {new_count} canciones cargadas exitosamente desde Cloudinary!'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'[ERROR] Error al cargar datos: {str(e)}'
                )
            )
            raise

