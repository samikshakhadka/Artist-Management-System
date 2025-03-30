// Load songs for an artist with pagination
async function loadSongs(artistId, page = 1, perPage = 10) {
    // Show loading indication
    document.querySelector('#songs-table tbody').innerHTML = `
        <tr><td colspan="6" class="text-center">Loading songs...</td></tr>
    `;
    
    try {
        const response = await fetch(`/api/artists/${artistId}/music?page=${page}&per_page=${perPage}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load songs');
        }
        
        const { music, pagination } = data.body;
        const tbody = document.querySelector('#songs-table tbody');
        
        if (music.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center">No songs found for this artist</td></tr>`;
            return;
        }
        
        // Clear table body
        tbody.innerHTML = '';
        
        // Show/hide add song button based on role
        document.getElementById('add-song-btn').style.display = 
            hasRole(currentUser, ['artist']) ? 'inline-block' : 'none';
        
        // Add song rows
        music.forEach(song => {
            const row = document.createElement('tr');
            
            // Create actions based on user role
            let actionsHtml = '';
            
            // Only artist can edit/delete songs
            if (hasRole(currentUser, ['artist'])) {
                actionsHtml = `
                    <button class="btn-action btn-edit" onclick="editSong(${song.id}, ${artistId})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteSong(${song.id}, ${artistId})">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
            }
            
            row.innerHTML = `
                <td>${song.id}</td>
                <td>${song.title}</td>
                <td>${song.album_name || '-'}</td>
                <td>${formatGenre(song.genre)}</td>
                <td>${formatDate(song.created_at)}</td>
                <td class="actions-cell">
                    ${actionsHtml}
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Create pagination
        createPagination('songs', pagination.total_pages, pagination.page, 
            (p) => loadSongs(artistId, p, perPage));
        
    } catch (error) {
        console.error('Error loading songs:', error);
        document.querySelector('#songs-table tbody').innerHTML = `
            <tr><td colspan="6" class="text-center">Error loading songs: ${error.message}</td></tr>
        `;
    }
}

// Format genre for display
function formatGenre(genre) {
    switch (genre) {
        case 'rnb': return 'R&B';
        case 'country': return 'Country';
        case 'classic': return 'Classic';
        case 'jazz': return 'Jazz';
        default: return genre || '-';
    }
}

// Create new song
function createSong() {
    // Make sure there's a selected artist
    if (!window.currentArtistForSongs) {
        showError('No artist selected');
        return;
    }
    
    // Set modal title
    document.getElementById('song-modal-title').textContent = 'Add New Song';
    
    // Reset form
    document.getElementById('song-form').reset();
    document.getElementById('song-id').value = '';
    document.getElementById('song-artist-id').value = window.currentArtistForSongs.id;
    
    // Enable all fields
    const formElements = document.querySelectorAll('#song-form input, #song-form select');
    formElements.forEach(el => {
        el.disabled = false;
    });
    
    // Reset modal footer
    const modalFooter = document.querySelector('#song-form .modal-footer');
    modalFooter.innerHTML = `
        <button type="button" class="btn" id="song-cancel-btn" onclick="closeSongModal()">Cancel</button>
        <button type="submit" class="btn">Save</button>
    `;
    
    // Show the modal
    document.getElementById('song-modal').style.display = 'block';
}

// Edit song
async function editSong(songId, artistId) {
    try {
        const response = await fetch(`/api/music/${songId}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load song');
        }
        
        const song = data.body.music;
        
        // Set modal title
        document.getElementById('song-modal-title').textContent = 'Edit Song';
        
        // Populate form with song data
        document.getElementById('song-id').value = song.id;
        document.getElementById('song-artist-id').value = song.artist_id;
        document.getElementById('song-title').value = song.title;
        document.getElementById('song-album').value = song.album_name || '';
        document.getElementById('song-genre').value = song.genre || '';
        
        // Enable all fields
        const formElements = document.querySelectorAll('#song-form input, #song-form select');
        formElements.forEach(el => {
            el.disabled = false;
        });
        
        // Reset modal footer
        const modalFooter = document.querySelector('#song-form .modal-footer');
        modalFooter.innerHTML = `
            <button type="button" class="btn" id="song-cancel-btn" onclick="closeSongModal()">Cancel</button>
            <button type="submit" class="btn">Save</button>
        `;
        
        // Show the modal
        document.getElementById('song-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error editing song:', error);
        showError('Error loading song: ' + error.message);
    }
}

// Close song modal
function closeSongModal() {
    document.getElementById('song-modal').style.display = 'none';
}

// Close songs listing modal
function closeSongsModal() {
    document.getElementById('songs-modal').style.display = 'none';
    window.currentArtistForSongs = null;
}

// Save song (create or update)
async function saveSong(e) {
    e.preventDefault();
    
    const songId = document.getElementById('song-id').value;
    const artistId = document.getElementById('song-artist-id').value;
    const isUpdate = songId !== '';
    
    const songData = {
        title: document.getElementById('song-title').value,
        album_name: document.getElementById('song-album').value,
        genre: document.getElementById('song-genre').value
    };
    
    try {
        const url = isUpdate ? `/api/music/${songId}` : `/api/artists/${artistId}/music`;
        const method = isUpdate ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(songData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `Failed to ${isUpdate ? 'update' : 'create'} song`);
        }
        
        if (data.body.success) {
            // Close modal
            closeSongModal();
            
            // Show success message
            showSuccess(`Song ${isUpdate ? 'updated' : 'created'} successfully`);
            
            // Reload songs list
            loadSongs(artistId);
        } else {
            throw new Error(data.body.message || `Failed to ${isUpdate ? 'update' : 'create'} song`);
        }
    } catch (error) {
        console.error(`Error ${songId ? 'updating' : 'creating'} song:`, error);
        showError(error.message);
    }
}

// Delete song
async function deleteSong(songId, artistId) {
    // Confirm deletion
    if (!confirm('Are you sure you want to delete this song?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/music/${songId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to delete song');
        }
        
        if (data.body.success) {
            showSuccess('Song deleted successfully');
            loadSongs(artistId); // Reload songs list
        } else {
            throw new Error(data.body.message || 'Failed to delete song');
        }
    } catch (error) {
        console.error('Error deleting song:', error);
        showError('Error deleting song: ' + error.message);
    }
}