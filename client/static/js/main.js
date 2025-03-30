// Global variable to store current user information
let currentUser = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    checkAuth().then(user => {
        if (!user) {
            // Redirect to login page if not authenticated
            window.location.href = '/login.html';
            return;
        }
        
        // Store user globally
        currentUser = user;
        
        // Set user info in the dashboard header
        document.getElementById('user-name').textContent = `${user.first_name} ${user.last_name}`;
        document.getElementById('user-role').textContent = formatRole(user.role);
        
        // Setup permissions based on user role
        setupRolePermissions(user);
        
        // Load initial data based on active tab
        loadInitialData();
        
        // Set up event listeners
        setupEventListeners();
    });
});

// Format role for display
function formatRole(role) {
    return role.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Setup permissions based on user role
function setupRolePermissions(user) {
    // Show/hide tabs based on user role
    if (!hasRole(user, ['super_admin'])) {
        document.getElementById('tab-users').style.display = 'none';
        document.getElementById('tab-content-users').classList.remove('active');
        document.getElementById('tab-artists').classList.add('active');
        document.getElementById('tab-content-artists').classList.add('active');
    }
    
    // Control permissions for artist actions
    if (!hasRole(user, ['artist_manager'])) {
        const artistButtons = document.querySelectorAll('#add-artist-btn, #import-artists-btn, #export-artists-btn');
        artistButtons.forEach(btn => {
            btn.style.display = 'none';
        });
    }
}

// Load initial data based on active tab
function loadInitialData() {
    // Determine which tab is active
    const activeTab = document.querySelector('.tab-button.active').getAttribute('data-tab');
    
    // Load data for active tab
    if (activeTab === 'users' && hasRole(currentUser, ['super_admin'])) {
        loadUsers();
    } else if (activeTab === 'artists') {
        loadArtists();
    }
}

// Setup all event listeners
function setupEventListeners() {
    // Set up logout button
    document.getElementById('logout-btn').addEventListener('click', function() {
        logout();
    });
    
    // Set up tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Add active class to selected tab
            this.classList.add('active');
            document.getElementById(`tab-content-${tabId}`).classList.add('active');
            
            // Load data for the selected tab
            if (tabId === 'users') {
                loadUsers();
            } else if (tabId === 'artists') {
                loadArtists();
            }
        });
    });
    
    // Setup modals and their event listeners
    setupModals();
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Create pagination UI
function createPagination(type, totalPages, currentPage, callback) {
    const container = document.getElementById(`${type}-pagination`);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Create pagination element
    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    
    // Previous button
    if (currentPage > 1) {
        const prevButton = document.createElement('button');
        prevButton.className = 'pagination-button';
        prevButton.innerHTML = '&laquo;';
        prevButton.addEventListener('click', () => callback(currentPage - 1));
        pagination.appendChild(prevButton);
    }
    
    // Page buttons
    for (let i = 1; i <= totalPages; i++) {
        if (totalPages > 7) {
            // Skip some pages for large pagination
            if (i > 2 && i < currentPage - 1) {
                if (i === 3) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.textContent = '...';
                    pagination.appendChild(ellipsis);
                }
                continue;
            }
            
            if (i > currentPage + 1 && i < totalPages - 1) {
                if (i === currentPage + 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.textContent = '...';
                    pagination.appendChild(ellipsis);
                }
                continue;
            }
        }
        
        const pageButton = document.createElement('button');
        pageButton.className = 'pagination-button' + (i === currentPage ? ' active' : '');
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            if (i !== currentPage) {
                callback(i);
            }
        });
        pagination.appendChild(pageButton);
    }
    
    // Next button
    if (currentPage < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.className = 'pagination-button';
        nextButton.innerHTML = '&raquo;';
        nextButton.addEventListener('click', () => callback(currentPage + 1));
        pagination.appendChild(nextButton);
    }
    
    container.appendChild(pagination);
}

// Show error message
function showError(message) {
    alert(message); // Simple alert for now
}

// Show success message
function showSuccess(message) {
    alert(message); // Simple alert for now
}