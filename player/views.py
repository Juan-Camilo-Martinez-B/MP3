from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, F
from .models import Song, Playlist, PlaylistItem, CurrentPlayback
import json
import os
from yt_dlp import YoutubeDL
import re
from pathlib import Path
from django.conf import settings


def index(request):
    """Vista principal del reproductor"""
    return render(request, 'player/index.html')


def get_or_create_playback_state(request):
    """Obtiene o crea el estado de reproducción para la sesión actual"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    playback, created = CurrentPlayback.objects.get_or_create(
        session_key=session_key,
        defaults={'volume': 0.5}
    )
    return playback


# ============ VISTAS DE CANCIONES ============

def songs_list(request):
    """Lista todas las canciones"""
    songs = Song.objects.all()
    songs_data = [{
        'id': song.id,
        'title': song.title,
        'duration': song.duration,
        'duration_formatted': song.duration_formatted,
        'play_count': song.play_count,
        'added_date': song.added_date.strftime('%Y-%m-%d %H:%M'),
        'file_url': song.file_path.url if song.file_path else None,
    } for song in songs]
    
    return JsonResponse({'songs': songs_data})


def song_detail(request, song_id):
    """Detalle de una canción"""
    song = get_object_or_404(Song, id=song_id)
    return JsonResponse({
        'id': song.id,
        'title': song.title,
        'duration': song.duration,
        'duration_formatted': song.duration_formatted,
        'play_count': song.play_count,
        'file_url': song.file_path.url if song.file_path else None,
    })


@csrf_exempt
@require_http_methods(["POST"])
def download_song(request):
    """Descarga una canción de YouTube"""
    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
        
        if not url:
            return JsonResponse({'error': 'URL no proporcionada'}, status=400)
        
        # Validar URL de YouTube
        youtube_patterns = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=',
            r'(https?://)?(www\.)?youtu\.be/',
            r'(https?://)?(www\.)?youtube\.com/playlist\?list='
        ]
        
        if not any(re.search(pattern, url) for pattern in youtube_patterns):
            return JsonResponse({'error': 'URL de YouTube inválida'}, status=400)
        
        # Configurar directorio de descarga
        media_songs_dir = os.path.join(settings.MEDIA_ROOT, 'songs')
        os.makedirs(media_songs_dir, exist_ok=True)
        
        # Opciones de descarga
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(media_songs_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,  # IMPORTANTE: Solo descargar el video, NO la playlist completa
            'ignoreerrors': False,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            song_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Construir ruta del archivo
            original_path = ydl.prepare_filename(info)
            song_path = os.path.splitext(original_path)[0] + '.mp3'
            
            if not os.path.exists(song_path):
                return JsonResponse({'error': 'Error al descargar el archivo'}, status=500)
            
            # Crear entrada en la base de datos
            relative_path = os.path.join('songs', os.path.basename(song_path))
            
            # Verificar si ya existe
            existing_song = Song.objects.filter(title=song_title).first()
            if existing_song:
                return JsonResponse({
                    'message': 'Canción ya existe en la biblioteca',
                    'song': {
                        'id': existing_song.id,
                        'title': existing_song.title,
                        'duration': existing_song.duration,
                        'duration_formatted': existing_song.duration_formatted,
                    }
                })
            
            song = Song.objects.create(
                title=song_title,
                youtube_url=url,
                file_path=relative_path,
                duration=duration
            )
            
            return JsonResponse({
                'message': 'Canción descargada exitosamente',
                'song': {
                    'id': song.id,
                    'title': song.title,
                    'duration': song.duration,
                    'duration_formatted': song.duration_formatted,
                    'file_url': song.file_path.url,
                }
            })
    
    except Exception as e:
        return JsonResponse({'error': f'Error al descargar: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def increment_play_count(request, song_id):
    """Incrementa el contador de reproducciones"""
    song = get_object_or_404(Song, id=song_id)
    song.increment_play_count()
    return JsonResponse({'play_count': song.play_count})


# ============ VISTAS DE PLAYLISTS ============

def playlists_list(request):
    """Lista todas las playlists"""
    playlists = Playlist.objects.all()
    playlists_data = [{
        'id': playlist.id,
        'name': playlist.name,
        'description': playlist.description,
        'is_active': playlist.is_active,
        'song_count': playlist.playlistitem_set.count(),
        'created_date': playlist.created_date.strftime('%Y-%m-%d %H:%M'),
    } for playlist in playlists]
    
    return JsonResponse({'playlists': playlists_data})


def playlist_detail(request, playlist_id):
    """Detalle de una playlist con sus canciones"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    items = playlist.playlistitem_set.all().select_related('song')
    songs_data = [{
        'id': item.song.id,
        'title': item.song.title,
        'duration': item.song.duration,
        'duration_formatted': item.song.duration_formatted,
        'position': item.position,
        'file_url': item.song.file_path.url if item.song.file_path else None,
    } for item in items]
    
    return JsonResponse({
        'id': playlist.id,
        'name': playlist.name,
        'description': playlist.description,
        'is_active': playlist.is_active,
        'songs': songs_data,
    })


@csrf_exempt
@require_http_methods(["POST"])
def playlist_create(request):
    """Crea una nueva playlist"""
    try:
        data = json.loads(request.body)
        name = data.get('name', 'Nueva Playlist')
        description = data.get('description', '')
        
        # Desactivar otras playlists si esta es activa
        is_active = data.get('is_active', False)
        if is_active:
            Playlist.objects.filter(is_active=True).update(is_active=False)
        
        playlist = Playlist.objects.create(
            name=name,
            description=description,
            is_active=is_active
        )
        
        return JsonResponse({
            'message': 'Playlist creada exitosamente',
            'playlist': {
                'id': playlist.id,
                'name': playlist.name,
                'description': playlist.description,
                'is_active': playlist.is_active,
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def playlist_add_song(request, playlist_id):
    """Agrega una canción a una playlist"""
    try:
        data = json.loads(request.body)
        song_id = data.get('song_id')
        position = data.get('position')
        
        playlist = get_object_or_404(Playlist, id=playlist_id)
        song = get_object_or_404(Song, id=song_id)
        
        # Verificar si la canción ya está en la playlist
        if PlaylistItem.objects.filter(playlist=playlist, song=song).exists():
            return JsonResponse({'error': 'La canción ya está en la playlist'}, status=400)
        
        playlist.add_song(song, position)
        
        return JsonResponse({'message': 'Canción agregada a la playlist'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def playlist_remove_song(request, playlist_id):
    """Elimina una canción de una playlist"""
    try:
        data = json.loads(request.body)
        song_id = data.get('song_id')
        
        playlist = get_object_or_404(Playlist, id=playlist_id)
        song = get_object_or_404(Song, id=song_id)
        
        playlist.remove_song(song)
        
        return JsonResponse({'message': 'Canción eliminada de la playlist'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def playlist_shuffle(request, playlist_id):
    """Mezcla las canciones de una playlist"""
    try:
        playlist = get_object_or_404(Playlist, id=playlist_id)
        
        # Verificar que hay canciones para mezclar
        if not playlist.playlistitem_set.exists():
            return JsonResponse({'error': 'La playlist está vacía'}, status=400)
        
        # Mezclar las canciones
        playlist.shuffle()
        
        # Obtener la primera canción de la playlist mezclada
        first_item = playlist.playlistitem_set.order_by('position').first()
        first_song = first_item.song if first_item else None
        
        # Obtener la cantidad de canciones mezcladas
        count = playlist.playlistitem_set.count()
        
        response_data = {
            'message': 'Playlist mezclada exitosamente',
            'count': count
        }
        
        # Incluir información de la primera canción para que el frontend la reproduzca
        if first_song:
            response_data['first_song'] = {
                'id': first_song.id,
                'title': first_song.title,
                'duration': first_song.duration,
                'file_url': first_song.file_path.url if first_song.file_path else None
            }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        import traceback
        print(f"Error en shuffle: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def playlist_reorder(request, playlist_id):
    """Reordena una canción en la playlist"""
    try:
        data = json.loads(request.body)
        song_id = data.get('song_id')
        new_position = data.get('new_position')
        
        playlist = get_object_or_404(Playlist, id=playlist_id)
        item = get_object_or_404(PlaylistItem, playlist=playlist, song_id=song_id)
        
        old_position = item.position
        
        if new_position == old_position:
            return JsonResponse({'message': 'Sin cambios'})
        
        # Remover temporalmente
        item.position = -1
        item.save()
        
        # Ajustar posiciones
        if new_position > old_position:
            # Mover hacia abajo
            PlaylistItem.objects.filter(
                playlist=playlist,
                position__gt=old_position,
                position__lte=new_position
            ).update(position=F('position') - 1)
        else:
            # Mover hacia arriba
            PlaylistItem.objects.filter(
                playlist=playlist,
                position__gte=new_position,
                position__lt=old_position
            ).update(position=F('position') + 1)
        
        # Asignar nueva posición
        item.position = new_position
        item.save()
        
        return JsonResponse({'message': 'Canción reordenada'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def playlist_delete(request, playlist_id):
    """Elimina una playlist"""
    try:
        playlist = get_object_or_404(Playlist, id=playlist_id)
        playlist.delete()
        
        return JsonResponse({'message': 'Playlist eliminada'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def playlist_set_active(request, playlist_id):
    """Establece una playlist como activa"""
    try:
        # Desactivar todas las playlists
        Playlist.objects.filter(is_active=True).update(is_active=False)
        
        # Activar la seleccionada
        playlist = get_object_or_404(Playlist, id=playlist_id)
        playlist.is_active = True
        playlist.save()
        
        return JsonResponse({'message': 'Playlist activada'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============ VISTAS DE ESTADO DE REPRODUCCIÓN ============

def playback_state(request):
    """Obtiene el estado actual de reproducción"""
    playback = get_or_create_playback_state(request)
    
    data = {
        'current_song': {
            'id': playback.current_song.id,
            'title': playback.current_song.title,
            'duration': playback.current_song.duration,
            'file_url': playback.current_song.file_path.url,
        } if playback.current_song else None,
        'current_playlist_id': playback.current_playlist.id if playback.current_playlist else None,
        'current_position': playback.current_position,
        'is_playing': playback.is_playing,
        'volume': playback.volume,
    }
    
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def playback_update(request):
    """Actualiza el estado de reproducción"""
    try:
        data = json.loads(request.body)
        playback = get_or_create_playback_state(request)
        
        if 'song_id' in data:
            playback.current_song_id = data['song_id']
        
        if 'playlist_id' in data:
            playback.current_playlist_id = data['playlist_id']
        
        if 'position' in data:
            playback.current_position = data['position']
        
        if 'is_playing' in data:
            playback.is_playing = data['is_playing']
        
        if 'volume' in data:
            playback.volume = data['volume']
        
        playback.save()
        
        return JsonResponse({'message': 'Estado actualizado'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
