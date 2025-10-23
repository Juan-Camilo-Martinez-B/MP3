from django.urls import path
from . import views

app_name = 'player'

urlpatterns = [
    # Vista principal
    path('', views.index, name='index'),
    
    # Canciones
    path('api/songs/', views.songs_list, name='songs_list'),
    path('api/songs/<int:song_id>/', views.song_detail, name='song_detail'),
    path('api/songs/download/', views.download_song, name='download_song'),
    path('api/songs/<int:song_id>/play/', views.increment_play_count, name='increment_play_count'),
    
    # Playlists
    path('api/playlists/', views.playlists_list, name='playlists_list'),
    path('api/playlists/create/', views.playlist_create, name='playlist_create'),
    path('api/playlists/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('api/playlists/<int:playlist_id>/add/', views.playlist_add_song, name='playlist_add_song'),
    path('api/playlists/<int:playlist_id>/remove/', views.playlist_remove_song, name='playlist_remove_song'),
    path('api/playlists/<int:playlist_id>/shuffle/', views.playlist_shuffle, name='playlist_shuffle'),
    path('api/playlists/<int:playlist_id>/reorder/', views.playlist_reorder, name='playlist_reorder'),
    path('api/playlists/<int:playlist_id>/delete/', views.playlist_delete, name='playlist_delete'),
    path('api/playlists/<int:playlist_id>/set-active/', views.playlist_set_active, name='playlist_set_active'),
    
    # Estado de reproducción
    path('api/playback/', views.playback_state, name='playback_state'),
    path('api/playback/update/', views.playback_update, name='playback_update'),
]

