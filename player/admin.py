from django.contrib import admin
from .models import Song, Playlist, PlaylistItem, CurrentPlayback


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_formatted', 'play_count', 'added_date']
    list_filter = ['added_date']
    search_fields = ['title']
    readonly_fields = ['play_count', 'added_date']


class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 1
    fields = ['song', 'position']
    ordering = ['position']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_date', 'updated_date']
    list_filter = ['is_active', 'created_date']
    search_fields = ['name', 'description']
    inlines = [PlaylistItemInline]


@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'song', 'position', 'added_date']
    list_filter = ['playlist', 'added_date']
    search_fields = ['playlist__name', 'song__title']
    ordering = ['playlist', 'position']


@admin.register(CurrentPlayback)
class CurrentPlaybackAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'current_song', 'is_playing', 'volume', 'last_updated']
    list_filter = ['is_playing', 'last_updated']
    readonly_fields = ['session_key', 'last_updated']
