// Estado global de la aplicación
const AppState = {
    songs: [],
    playlists: [],
    currentPlaylist: null,
    currentSong: null,
    currentSongIndex: 0,
    isPlaying: false,
    volume: 0.5,
    audioPlayer: null,
};

// Obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    AppState.audioPlayer = document.getElementById('audio-player');
    AppState.audioPlayer.volume = AppState.volume;
    
    // Event listeners del reproductor de audio
    AppState.audioPlayer.addEventListener('timeupdate', updateProgress);
    AppState.audioPlayer.addEventListener('ended', playNextSong);
    AppState.audioPlayer.addEventListener('loadedmetadata', updateTotalTime);
}

function setupEventListeners() {
    // Download - Solo si los elementos existen (no en modo demostración)
    const downloadBtn = document.getElementById('download-btn');
    const youtubeUrl = document.getElementById('youtube-url');
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadSong);
    }
    
    if (youtubeUrl) {
        youtubeUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') downloadSong();
        });
    }
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Player controls
    document.getElementById('play-pause-btn').addEventListener('click', togglePlayPause);
    document.getElementById('prev-btn').addEventListener('click', playPreviousSong);
    document.getElementById('next-btn').addEventListener('click', playNextSong);
    
    // Volume
    const volumeSlider = document.getElementById('volume-slider');
    volumeSlider.addEventListener('input', (e) => {
        AppState.volume = e.target.value / 100;
        AppState.audioPlayer.volume = AppState.volume;
    });
    
    // Progress - Mejorado para ser completamente funcional
    const progressSlider = document.getElementById('progress-slider');
    
    // Actualizar tiempo al hacer click o arrastrar
    progressSlider.addEventListener('input', (e) => {
        if (AppState.audioPlayer.duration) {
            const time = (e.target.value / 100) * AppState.audioPlayer.duration;
            AppState.audioPlayer.currentTime = time;
            
            // Actualizar visualmente de inmediato
            const progress = e.target.value;
            progressSlider.style.setProperty('--progress', `${progress}%`);
            
            // Actualizar tiempo mostrado
            const minutes = Math.floor(time / 60);
            const seconds = Math.floor(time % 60);
            document.getElementById('current-time').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    });
    
    // También responder a clicks directos
    progressSlider.addEventListener('change', (e) => {
        if (AppState.audioPlayer.duration) {
            const time = (e.target.value / 100) * AppState.audioPlayer.duration;
            AppState.audioPlayer.currentTime = time;
        }
    });
    
    // Playlist actions
    document.getElementById('shuffle-btn').addEventListener('click', shufflePlaylist);
    document.getElementById('create-playlist-btn').addEventListener('click', openPlaylistModal);
    
    // Modal
    document.getElementById('close-modal').addEventListener('click', closePlaylistModal);
    document.getElementById('cancel-playlist').addEventListener('click', closePlaylistModal);
    document.getElementById('save-playlist').addEventListener('click', createPlaylist);
    
    // Search
    document.getElementById('search-library').addEventListener('input', (e) => {
        filterLibrary(e.target.value);
    });
}

async function loadInitialData() {
    await Promise.all([
        loadSongs(),
        loadPlaylists()
    ]);
    
    // Crear playlist por defecto si no hay ninguna
    if (AppState.playlists.length === 0) {
        await createDefaultPlaylist();
    } else {
        // Activar la primera playlist
        const activePlaylist = AppState.playlists.find(p => p.is_active) || AppState.playlists[0];
        await selectPlaylist(activePlaylist.id);
    }
}

// ============ API CALLS ============

async function loadSongs() {
    try {
        const response = await fetch('/api/songs/');
        const data = await response.json();
        AppState.songs = data.songs;
        renderLibrary();
    } catch (error) {
        console.error('Error loading songs:', error);
    }
}

async function loadPlaylists() {
    try {
        const response = await fetch('/api/playlists/');
        const data = await response.json();
        AppState.playlists = data.playlists;
        renderPlaylists();
    } catch (error) {
        console.error('Error loading playlists:', error);
    }
}

async function downloadSong() {
    const urlInput = document.getElementById('youtube-url');
    const url = urlInput.value.trim();
    const statusDiv = document.getElementById('download-status');
    const downloadBtn = document.getElementById('download-btn');
    
    if (!url) {
        showStatus('⚠️ Por favor ingresa una URL de YouTube', 'error');
        return;
    }
    
    // Validación básica de URL
    const isYouTubeUrl = /youtube\.com\/watch\?v=|youtu\.be\//.test(url);
    if (!isYouTubeUrl) {
        showStatus('⚠️ Por favor ingresa una URL válida de YouTube', 'error');
        return;
    }
    
    // Deshabilitar botón y mostrar estado de descarga
    downloadBtn.disabled = true;
    const originalBtnText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Descargando...';
    showStatus('📥 Descargando canción desde YouTube...', 'loading');
    
    try {
        const response = await fetch('/api/songs/download/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Limpiar input
            urlInput.value = '';
            
            // Mostrar mensaje de éxito con el nombre de la canción
            showStatus(`✅ ${data.message}: "${data.song.title}"`, 'success');
            
            // Recargar la biblioteca para mostrar la nueva canción
            await loadSongs();
            
            // Cambiar a la pestaña de biblioteca para mostrar la nueva canción
            switchTab('library');
            
            // Resaltar brevemente la nueva canción
            setTimeout(() => {
                const librarySongs = document.querySelectorAll('#library-songs tr');
                if (librarySongs.length > 0) {
                    // La canción más reciente debería estar al principio
                    const newSongRow = Array.from(librarySongs).find(row => 
                        row.querySelector('.song-title')?.textContent.includes(data.song.title)
                    );
                    if (newSongRow) {
                        newSongRow.style.backgroundColor = 'rgba(29, 185, 84, 0.2)';
                        setTimeout(() => {
                            newSongRow.style.transition = 'background-color 1s ease';
                            newSongRow.style.backgroundColor = '';
                        }, 1000);
                    }
                }
            }, 100);
            
            // Si no hay playlist activa, crear una por defecto
            if (!AppState.currentPlaylist) {
                await createDefaultPlaylist();
            }
        } else {
            showStatus(`❌ ${data.error || 'Error al descargar'}`, 'error');
        }
    } catch (error) {
        showStatus('❌ Error de conexión con el servidor', 'error');
        console.error('Download error:', error);
    } finally {
        // Restaurar botón
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = originalBtnText;
    }
}

async function createDefaultPlaylist() {
    const response = await fetch('/api/playlists/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            name: 'Mi Playlist',
            description: 'Playlist predeterminada',
            is_active: true
        })
    });
    
    if (response.ok) {
        await loadPlaylists();
        const newPlaylist = AppState.playlists[0];
        await selectPlaylist(newPlaylist.id);
    }
}

async function createPlaylist() {
    const name = document.getElementById('playlist-name').value.trim() || 'Nueva Playlist';
    const description = document.getElementById('playlist-description').value.trim();
    
    try {
        const response = await fetch('/api/playlists/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ name, description })
        });
        
        if (response.ok) {
            await loadPlaylists();
            closePlaylistModal();
            document.getElementById('playlist-name').value = '';
            document.getElementById('playlist-description').value = '';
        }
    } catch (error) {
        console.error('Error creating playlist:', error);
    }
}

async function selectPlaylist(playlistId) {
    try {
        const response = await fetch(`/api/playlists/${playlistId}/`);
        const data = await response.json();
        
        AppState.currentPlaylist = data;
        
        // Marcar como activa
        await fetch(`/api/playlists/${playlistId}/set-active/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            }
        });
        
        await loadPlaylists();
        renderPlaylistSongs();
        
        // Actualizar nombre en el header
        document.getElementById('current-playlist-name').textContent = data.name;
    } catch (error) {
        console.error('Error selecting playlist:', error);
    }
}

async function addSongToPlaylist(songId) {
    if (!AppState.currentPlaylist) {
        alert('Por favor selecciona o crea una playlist primero');
        return;
    }
    
    try {
        const response = await fetch(`/api/playlists/${AppState.currentPlaylist.id}/add/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ song_id: songId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            await selectPlaylist(AppState.currentPlaylist.id);
            showStatus('Canción agregada a la playlist', 'success');
        } else {
            showStatus(data.error || 'Error al agregar canción', 'error');
        }
    } catch (error) {
        console.error('Error adding song:', error);
    }
}

async function removeSongFromPlaylist(songId) {
    try {
        await fetch(`/api/playlists/${AppState.currentPlaylist.id}/remove/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ song_id: songId })
        });
        
        await selectPlaylist(AppState.currentPlaylist.id);
        
        // Si la canción que se eliminó era la actual, detener reproducción
        if (AppState.currentSong && AppState.currentSong.id === songId) {
            stopPlayback();
        }
    } catch (error) {
        console.error('Error removing song:', error);
    }
}

async function shufflePlaylist() {
    if (!AppState.currentPlaylist) {
        showStatus('No hay playlist activa', 'error');
        return;
    }
    
    const shuffleBtn = document.getElementById('shuffle-btn');
    const originalText = shuffleBtn.innerHTML;
    
    try {
        // Deshabilitar botón y mostrar feedback
        shuffleBtn.disabled = true;
        shuffleBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mezclando...';
        
        const response = await fetch(`/api/playlists/${AppState.currentPlaylist.id}/shuffle/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al mezclar playlist');
        }
        
        const data = await response.json();
        
        // Recargar la playlist para mostrar el nuevo orden
        await selectPlaylist(AppState.currentPlaylist.id);
        
        // Reproducir automáticamente la primera canción de la playlist mezclada
        if (data.first_song && AppState.currentPlaylist.songs.length > 0) {
            // Iniciar reproducción desde la primera canción (índice 0)
            playSong(0);
        }
        
        // Mostrar mensaje de éxito
        showStatus('✓ Playlist mezclada - reproduciendo desde el inicio', 'success');
        
        // Pequeña animación en la tabla
        const tbody = document.getElementById('playlist-songs');
        tbody.style.opacity = '0.5';
        setTimeout(() => {
            tbody.style.transition = 'opacity 0.3s ease';
            tbody.style.opacity = '1';
        }, 100);
        
    } catch (error) {
        console.error('Error shuffling:', error);
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        // Restaurar botón
        shuffleBtn.disabled = false;
        shuffleBtn.innerHTML = originalText;
    }
}

// ============ PLAYBACK FUNCTIONS ============

function playSong(songIndex) {
    if (!AppState.currentPlaylist || !AppState.currentPlaylist.songs.length) {
        return;
    }
    
    const song = AppState.currentPlaylist.songs[songIndex];
    if (!song) return;
    
    AppState.currentSong = song;
    AppState.currentSongIndex = songIndex;
    
    // Actualizar UI del reproductor
    document.getElementById('player-song-title').textContent = song.title;
    document.getElementById('player-song-artist').textContent = 'Reproduciendo ahora';
    
    // Cargar y reproducir
    AppState.audioPlayer.src = song.file_url;
    AppState.audioPlayer.play();
    AppState.isPlaying = true;
    
    // Actualizar botón de play/pause - Ahora usa Font Awesome
    const playIcon = document.getElementById('play-pause-icon');
    playIcon.className = 'fas fa-pause';
    
    // Marcar canción en la lista
    highlightCurrentSong();
    
    // Incrementar contador de reproducciones
    fetch(`/api/songs/${song.id}/play/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    });
}

function togglePlayPause() {
    const playIcon = document.getElementById('play-pause-icon');
    
    if (!AppState.currentSong) {
        // Si no hay canción, reproducir la primera de la playlist
        if (AppState.currentPlaylist && AppState.currentPlaylist.songs.length > 0) {
            playSong(0);
        }
        return;
    }
    
    if (AppState.isPlaying) {
        AppState.audioPlayer.pause();
        AppState.isPlaying = false;
        playIcon.className = 'fas fa-play';
    } else {
        AppState.audioPlayer.play();
        AppState.isPlaying = true;
        playIcon.className = 'fas fa-pause';
    }
}

function playNextSong() {
    if (!AppState.currentPlaylist || !AppState.currentPlaylist.songs.length) return;
    
    const nextIndex = (AppState.currentSongIndex + 1) % AppState.currentPlaylist.songs.length;
    playSong(nextIndex);
}

function playPreviousSong() {
    if (!AppState.currentPlaylist || !AppState.currentPlaylist.songs.length) return;
    
    let prevIndex = AppState.currentSongIndex - 1;
    if (prevIndex < 0) {
        prevIndex = AppState.currentPlaylist.songs.length - 1;
    }
    playSong(prevIndex);
}

function stopPlayback() {
    AppState.audioPlayer.pause();
    AppState.audioPlayer.currentTime = 0;
    AppState.isPlaying = false;
    AppState.currentSong = null;
    
    const playIcon = document.getElementById('play-pause-icon');
    playIcon.className = 'fas fa-play';
    
    document.getElementById('player-song-title').textContent = 'Sin canción';
    document.getElementById('player-song-artist').textContent = 'Selecciona una canción para reproducir';
}

function updateProgress() {
    if (!AppState.audioPlayer.duration) return;
    
    const progress = (AppState.audioPlayer.currentTime / AppState.audioPlayer.duration) * 100;
    const progressSlider = document.getElementById('progress-slider');
    
    // Actualizar valor del slider
    progressSlider.value = progress;
    
    // Actualizar el CSS custom property para el fill visual
    progressSlider.style.setProperty('--progress', `${progress}%`);
    
    // Actualizar tiempo actual
    const minutes = Math.floor(AppState.audioPlayer.currentTime / 60);
    const seconds = Math.floor(AppState.audioPlayer.currentTime % 60);
    document.getElementById('current-time').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function updateTotalTime() {
    const duration = AppState.audioPlayer.duration;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    document.getElementById('total-time').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// ============ UI RENDERING ============

function renderLibrary() {
    const tbody = document.getElementById('library-songs');
    
    if (AppState.songs.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="4">
                    <div class="empty-state-content">
                        <span class="empty-icon">📚</span>
                        <p>No hay canciones en tu biblioteca</p>
                        <p class="empty-hint">Descarga canciones desde YouTube para comenzar</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = AppState.songs.map((song, index) => `
        <tr>
            <td class="song-number">${index + 1}</td>
            <td class="song-title">${song.title}</td>
            <td>${song.duration_formatted}</td>
            <td>
                <div class="song-actions">
                    <button class="action-btn" onclick="playSongFromLibrary(${song.id})">
                        <i class="fas fa-play"></i> Reproducir
                    </button>
                    <button class="action-btn" onclick="addSongToPlaylist(${song.id})">
                        <i class="fas fa-plus"></i> Agregar
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderPlaylistSongs() {
    const tbody = document.getElementById('playlist-songs');
    
    if (!AppState.currentPlaylist || AppState.currentPlaylist.songs.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="4">
                    <div class="empty-state-content">
                        <span class="empty-icon">🎵</span>
                        <p>No hay canciones en la playlist</p>
                        <p class="empty-hint">Agrega canciones desde la biblioteca</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = AppState.currentPlaylist.songs.map((song, index) => `
        <tr data-song-id="${song.id}" ${AppState.currentSong && AppState.currentSong.id === song.id ? 'class="playing"' : ''}>
            <td class="song-number">${index + 1}</td>
            <td class="song-title">${song.title}</td>
            <td>${song.duration_formatted}</td>
            <td>
                <div class="song-actions">
                    <button class="action-btn" onclick="playSong(${index})">
                        <i class="fas fa-play"></i> Reproducir
                    </button>
                    <button class="action-btn danger" onclick="removeSongFromPlaylist(${song.id})">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderPlaylists() {
    const ul = document.getElementById('playlists-list');
    
    if (AppState.playlists.length === 0) {
        ul.innerHTML = '<li style="padding: 10px; color: var(--text-muted);">Sin playlists</li>';
        return;
    }
    
    ul.innerHTML = AppState.playlists.map(playlist => `
        <li class="playlist-item ${playlist.is_active ? 'active' : ''}" onclick="selectPlaylist(${playlist.id})">
            <span class="playlist-name">${playlist.name}</span>
            <span class="playlist-count">${playlist.song_count}</span>
        </li>
    `).join('');
}

function highlightCurrentSong() {
    // Remover highlight anterior
    document.querySelectorAll('#playlist-songs tr.playing').forEach(tr => {
        tr.classList.remove('playing');
    });
    
    // Agregar highlight a la canción actual
    if (AppState.currentSong) {
        const row = document.querySelector(`#playlist-songs tr[data-song-id="${AppState.currentSong.id}"]`);
        if (row) {
            row.classList.add('playing');
        }
    }
}

// ============ UTILITY FUNCTIONS ============

function switchTab(tabName) {
    // Actualizar botones
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Actualizar contenido
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('download-status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type} show`;
    
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.classList.remove('show');
        }, 3000);
    }
}

function openPlaylistModal() {
    document.getElementById('playlist-modal').classList.add('show');
}

function closePlaylistModal() {
    document.getElementById('playlist-modal').classList.remove('show');
}

function filterLibrary(query) {
    const rows = document.querySelectorAll('#library-songs tr');
    const lowerQuery = query.toLowerCase();
    
    rows.forEach(row => {
        const title = row.querySelector('.song-title');
        if (title) {
            const matches = title.textContent.toLowerCase().includes(lowerQuery);
            row.style.display = matches ? '' : 'none';
        }
    });
}

function playSongFromLibrary(songId) {
    // Buscar la canción en la playlist actual
    if (!AppState.currentPlaylist) {
        alert('Por favor selecciona una playlist primero');
        return;
    }
    
    const songIndex = AppState.currentPlaylist.songs.findIndex(s => s.id === songId);
    
    if (songIndex !== -1) {
        playSong(songIndex);
    } else {
        // Si no está en la playlist, agregarla y reproducirla
        addSongToPlaylist(songId).then(() => {
            setTimeout(() => {
                const newIndex = AppState.currentPlaylist.songs.findIndex(s => s.id === songId);
                if (newIndex !== -1) {
                    playSong(newIndex);
                }
            }, 500);
        });
    }
}

// Hacer funciones globales para los onclick en HTML
window.playSong = playSong;
window.playSongFromLibrary = playSongFromLibrary;
window.addSongToPlaylist = addSongToPlaylist;
window.removeSongFromPlaylist = removeSongFromPlaylist;
window.selectPlaylist = selectPlaylist;

