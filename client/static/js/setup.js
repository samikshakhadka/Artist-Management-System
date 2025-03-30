
function setupModals() {
    // User modal setup
    setupUserModal();
    
    // Artist modal setup
    setupArtistModal();
    
    // Songs modal setup
    setupSongsModal();
    
    // Song modal setup
    setupSongModal();
    
    // Import modal setup
    setupImportModal();
}

// Setup user modal
function setupUserModal() {
    const userModal = document.getElementById('user-modal');
    const userForm = document.getElementById('user-form');
    
    // Add user button
    document.getElementById('add-user-btn').addEventListener('click', createUser);
    
    // Modal close button
    document.getElementById('user-modal-close').addEventListener('click', closeUserModal);
    
    // Form submission
    userForm.addEventListener('submit', saveUser);
    
    // Close when clicking outside the modal
    window.addEventListener('click', function(event) {
        if (event.target === userModal) {
            closeUserModal();
        }
    });
}

// Setup artist modal
function setupArtistModal() {
    const artistModal = document.getElementById('artist-modal');
    const artistForm = document.getElementById('artist-form');
    
    // Add artist button
    document.getElementById('add-artist-btn').addEventListener('click', createArtist);
    
    // Modal close button
    document.getElementById('artist-modal-close').addEventListener('click', closeArtistModal);
    
    // Cancel button
    document.getElementById('artist-cancel-btn').addEventListener('click', closeArtistModal);
    
    // Form submission
    artistForm.addEventListener('submit', saveArtist);
    
    // Close when clicking outside the modal
    window.addEventListener('click', function(event) {
        if (event.target === artistModal) {
            closeArtistModal();
        }
    });
}

// Setup songs modal
function setupSongsModal() {
    const songsModal = document.getElementById('songs-modal');
    
    // Modal close button
    document.getElementById('songs-modal-close').addEventListener('click', closeSongsModal);
    
    // Close button
    document.getElementById('songs-close-btn').addEventListener('click', closeSongsModal);
    
    // Close when clicking outside the modal
    window.addEventListener('click', function(event) {
        if (event.target === songsModal) {
            closeSongsModal();
        }
    });
}

// Setup song modal
function setupSongModal() {
    const songModal = document.getElementById('song-modal');
    const songForm = document.getElementById('song-form');
    
    // Add song button
    document.getElementById('add-song-btn').addEventListener('click', createSong);
    
    // Modal close button
    document.getElementById('song-modal-close').addEventListener('click', closeSongModal);
    
    // Cancel button
    document.getElementById('song-cancel-btn').addEventListener('click', closeSongModal);
    
    // Form submission
    songForm.addEventListener('submit', saveSong);
    
    // Close when clicking outside the modal
    window.addEventListener('click', function(event) {
        if (event.target === songModal) {
            closeSongModal();
        }
    });
}

// Setup import modal
function setupImportModal() {
    const importModal = document.getElementById('import-modal');
    const importForm = document.getElementById('import-form');
    
    // Import button
    document.getElementById('import-artists-btn').addEventListener('click', function() {
        importModal.style.display = 'block';
    });
    
    // Modal close button
    document.getElementById('import-modal-close').addEventListener('click', function() {
        importModal.style.display = 'none';
    });
    
    // Cancel button
    document.getElementById('import-cancel-btn').addEventListener('click', function() {
        importModal.style.display = 'none';
    });
    
    // Form submission
    importForm.addEventListener('submit', importArtistsCSV);
    
    // Close when clicking outside the modal
    window.addEventListener('click', function(event) {
        if (event.target === importModal) {
            importModal.style.display = 'none';
        }
    });
    
    // Export button
    document.getElementById('export-artists-btn').addEventListener('click', exportArtistsCSV);
}