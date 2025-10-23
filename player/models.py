from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class Song(models.Model):
    """Modelo para las canciones"""
    title = models.CharField(max_length=255, verbose_name="Título")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="URL de YouTube")
    file_path = models.FileField(upload_to='songs/', verbose_name="Archivo MP3")
    duration = models.FloatField(default=0, verbose_name="Duración (segundos)")
    added_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de agregado")
    play_count = models.IntegerField(default=0, verbose_name="Reproducciones")
    
    class Meta:
        verbose_name = "Canción"
        verbose_name_plural = "Canciones"
        ordering = ['-added_date']
    
    def __str__(self):
        return self.title
    
    def increment_play_count(self):
        """Incrementa el contador de reproducciones"""
        self.play_count += 1
        self.save()
    
    @property
    def duration_formatted(self):
        """Retorna la duración en formato MM:SS"""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"


class Playlist(models.Model):
    """Modelo para las playlists"""
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    is_active = models.BooleanField(default=False, verbose_name="Playlist activa")
    
    class Meta:
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"
        ordering = ['-updated_date']
    
    def __str__(self):
        return self.name
    
    def get_songs(self):
        """Retorna las canciones de la playlist ordenadas por posición"""
        return [item.song for item in self.playlistitem_set.all().order_by('position')]
    
    def add_song(self, song, position=None):
        """Agrega una canción a la playlist en una posición específica"""
        if position is None:
            # Si no se especifica posición, agregar al final
            max_position = self.playlistitem_set.aggregate(models.Max('position'))['position__max']
            position = (max_position or 0) + 1
        else:
            # Si se especifica posición, ajustar las demás
            PlaylistItem.objects.filter(
                playlist=self,
                position__gte=position
            ).update(position=models.F('position') + 1)
        
        PlaylistItem.objects.create(
            playlist=self,
            song=song,
            position=position
        )
    
    def remove_song(self, song):
        """Elimina una canción de la playlist"""
        item = self.playlistitem_set.filter(song=song).first()
        if item:
            position = item.position
            item.delete()
            # Reajustar posiciones
            PlaylistItem.objects.filter(
                playlist=self,
                position__gt=position
            ).update(position=models.F('position') - 1)
    
    def shuffle(self):
        """Mezcla aleatoriamente las canciones de la playlist"""
        import random
        from django.db import transaction
        
        items = list(self.playlistitem_set.all())
        if not items:
            return
        
        random.shuffle(items)
        
        # Usar transacción atómica para evitar problemas de constraint
        with transaction.atomic():
            # Primero, asignar posiciones temporales únicas para evitar colisiones
            # Usamos números negativos para garantizar que no colisionan
            for idx, item in enumerate(items):
                item.position = -(idx + 1)
            PlaylistItem.objects.bulk_update(items, ['position'])
            
            # Luego, asignar las posiciones finales
            for idx, item in enumerate(items, start=1):
                item.position = idx
            PlaylistItem.objects.bulk_update(items, ['position'])


class PlaylistItem(models.Model):
    """Modelo para los items de una playlist (relación many-to-many con orden)"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name="Playlist")
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name="Canción")
    position = models.IntegerField(default=0, verbose_name="Posición")
    added_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de agregado")
    
    class Meta:
        verbose_name = "Item de Playlist"
        verbose_name_plural = "Items de Playlist"
        ordering = ['position']
        unique_together = ['playlist', 'position']
    
    def __str__(self):
        return f"{self.playlist.name} - {self.song.title} (pos: {self.position})"


class CurrentPlayback(models.Model):
    """Modelo para guardar el estado actual de reproducción"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    session_key = models.CharField(max_length=40, unique=True, verbose_name="Clave de sesión")
    current_song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Canción actual")
    current_playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Playlist actual")
    current_position = models.IntegerField(default=0, verbose_name="Posición en playlist")
    is_playing = models.BooleanField(default=False, verbose_name="Reproduciendo")
    volume = models.FloatField(default=0.5, verbose_name="Volumen")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Estado de Reproducción"
        verbose_name_plural = "Estados de Reproducción"
    
    def __str__(self):
        return f"Playback - {self.session_key}"
