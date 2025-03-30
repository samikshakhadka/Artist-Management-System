
async function loadArtists(page = 1, perPage = 10) {
    // Only super_admin and artist_manager can access artists data
    if (!hasRole(currentUser, ['super_admin', 'artist_manager', 'artist'])) {
        document.querySelector('#artists-table tbody').innerHTML = `
            <tr><td colspan="7" class="text-center">You don't have permission to view artists.</td></tr>
        `;
        return;
    }
    
    // Show loading indication
    document.querySelector('#artists-table tbody').innerHTML = `
        <tr><td colspan="7" class="text-center">Loading artists...</td></tr>
    `;
    
    try {
        const response = await fetch(`/api/artists?page=${page}&per_page=${perPage}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load artists');
        }
        
        const { artists, pagination } = data.body;
        const tbody = document.querySelector('#artists-table tbody');
        
        if (artists.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center">No artists found</td></tr>`;
            return;
        }
        
        // Clear table body
        tbody.innerHTML = '';
        
        // Add artist rows
        artists.forEach(artist => {
            const row = document.createElement('tr');
            
            // Create actions based on user role
            let actionsHtml = `
                <button class="btn-action btn-view" onclick="viewSongs(${artist.id}, '${artist.name}')">
                    <i class="fas fa-music"></i> Songs
                </button>
            `;
            
            // Only artist_manager can edit/delete artists
            if (hasRole(currentUser, ['artist_manager'])) {
                actionsHtml += `
                    <button class="btn-action btn-edit" onclick="editArtist(${artist.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteArtist(${artist.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
            }
            
            row.innerHTML = `
                <td>${artist.id}</td>
                <td>${artist.name}</td>
                <td>${artist.gender === 'm' ? 'Male' : (artist.gender === 'f' ? 'Female' : (artist.gender === 'o' ? 'Other' : '-'))}</td>
                <td>${artist.address || '-'}</td>
                <td>${artist.first_release_year || '-'}</td>
                <td>${artist.no_of_albums_released || '0'}</td>
                <td class="actions-cell">
                    ${actionsHtml}
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Create pagination
        createPagination('artists', pagination.total_pages, pagination.page, loadArtists);
        
    } catch (error) {
        console.error('Error loading artists:', error);
        document.querySelector('#artists-table tbody').innerHTML = `
            <tr><td colspan="7" class="text-center">Error loading artists: ${error.message}</td></tr>
        `;
    }
}

// Create new artist
function createArtist() {
    // Set modal title
    document.getElementById('artist-modal-title').textContent = 'Add New Artist';
    
    // Reset form
    document.getElementById('artist-form').reset();
    document.getElementById('artist-id').value = '';
    
    // Enable all fields
    const formElements = document.querySelectorAll('#artist-form input, #artist-form select, #artist-form textarea');
    formElements.forEach(el => {
        el.disabled = false;
    });
    
    // Reset modal footer
    const modalFooter = document.querySelector('#artist-form .modal-footer');
    modalFooter.innerHTML = `
        <button type="button" class="btn" id="artist-cancel-btn" onclick="closeArtistModal()">Cancel</button>
        <button type="submit" class="btn">Save</button>
    `;
    
    // Show the modal
    document.getElementById('artist-modal').style.display = 'block';
}

// Edit artist
async function editArtist(artistId) {
    try {
        const response = await fetch(`/api/artists/${artistId}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load artist');
        }
        
        const artist = data.body.artist;
        
        // Set modal title
        document.getElementById('artist-modal-title').textContent = 'Edit Artist';
        
        // Populate form with artist data
        document.getElementById('artist-id').value = artist.id;
        document.getElementById('artist-name').value = artist.name;
        document.getElementById('artist-dob').value = artist.dob ? artist.dob.split('T')[0] : '';
        document.getElementById('artist-gender').value = artist.gender || '';
        document.getElementById('artist-address').value = artist.address || '';
        document.getElementById('artist-first-release').value = artist.first_release_year || '';
        document.getElementById('artist-albums').value = artist.no_of_albums_released || '0';
        
        // Enable all fields
        const formElements = document.querySelectorAll('#artist-form input, #artist-form select, #artist-form textarea');
        formElements.forEach(el => {
            el.disabled = false;
        });
        
        // Reset modal footer
        const modalFooter = document.querySelector('#artist-form .modal-footer');
        modalFooter.innerHTML = `
            <button type="button" class="btn" id="artist-cancel-btn" onclick="closeArtistModal()">Cancel</button>
            <button type="submit" class="btn">Save</button>
        `;
        
        // Show the modal
        document.getElementById('artist-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error editing artist:', error);
        showError('Error loading artist: ' + error.message);
    }
}

// Close artist modal
function closeArtistModal() {
    document.getElementById('artist-modal').style.display = 'none';
}

// Save artist (create or update)
async function saveArtist(e) {
    e.preventDefault();
    
    const artistId = document.getElementById('artist-id').value;
    const isUpdate = artistId !== '';
    
    const artistData = {
        name: document.getElementById('artist-name').value,
        dob: document.getElementById('artist-dob').value,
        gender: document.getElementById('artist-gender').value,
        address: document.getElementById('artist-address').value,
        first_release_year: document.getElementById('artist-first-release').value,
        no_of_albums_released: document.getElementById('artist-albums').value || '0'
    };
    
    try {
        const url = isUpdate ? `/api/artists/${artistId}` : '/api/artists';
        const method = isUpdate ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(artistData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `Failed to ${isUpdate ? 'update' : 'create'} artist`);
        }
        
        if (data.body.success) {
            // Close modal
            closeArtistModal();
            
            // Show success message
            showSuccess(`Artist ${isUpdate ? 'updated' : 'created'} successfully`);
            
            // Reload artists list
            loadArtists();
        } else {
            throw new Error(data.body.message || `Failed to ${isUpdate ? 'update' : 'create'} artist`);
        }
    } catch (error) {
        console.error(`Error ${artistId ? 'updating' : 'creating'} artist:`, error);
        showError(error.message);
    }
}

// Delete artist
async function deleteArtist(artistId) {
    // Confirm deletion
    if (!confirm('Are you sure you want to delete this artist? All associated songs will also be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/artists/${artistId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to delete artist');
        }
        
        if (data.body.success) {
            showSuccess('Artist deleted successfully');
            loadArtists(); // Reload artists list
        } else {
            throw new Error(data.body.message || 'Failed to delete artist');
        }
    } catch (error) {
        console.error('Error deleting artist:', error);
        showError('Error deleting artist: ' + error.message);
    }
}

// Import artists from CSV
async function importArtistsCSV(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('csv_file', file);
    
    try {
        const response = await fetch('/api/artists/import', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to import CSV');
        }
        
        if (data.body.success) {
            // Close modal
            document.getElementById('import-modal').style.display = 'none';
            
            // Show success message
            showSuccess(data.body.message || 'Artists imported successfully');
            
            // Reload artists list
            loadArtists();
        } else {
            throw new Error(data.body.message || 'Failed to import CSV');
        }
    } catch (error) {
        console.error('Error importing CSV:', error);
        showError('Error importing CSV: ' + error.message);
    }
}

// Export artists to CSV
async function exportArtistsCSV() {
    try {
        // We'll use directly the href approach, as it will download the file
        window.location.href = '/api/artists/export';
    } catch (error) {
        console.error('Error exporting CSV:', error);
        showError('Error exporting CSV: ' + error.message);
    }
}

// View songs for an artist
async function viewSongs(artistId, artistName) {
    // Set current artist for songs
    window.currentArtistForSongs = { id: artistId, name: artistName };
    document.getElementById('artist-name-for-songs').textContent = artistName;
    
    // Show songs modal
    document.getElementById('songs-modal').style.display = 'block';
    
    // Load songs for the artist
    loadSongs(artistId, 1);
}