/**
 * Common utility functions for Artist Management System
 */

/**
 * Format a date string for display
 * @param {string} dateString - Date in string format
 * @returns {string} - Formatted date string or '-' if not provided
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

/**
 * Format gender value for display
 * @param {string} gender - Gender value (m, f, o)
 * @returns {string} - Formatted gender string
 */
function formatGender(gender) {
    if (!gender) return '-';
    
    const genderMap = {
        'm': 'Male',
        'f': 'Female',
        'o': 'Other'
    };
    
    return genderMap[gender] || gender;
}

/**
 * Format role value for display
 * @param {string} role - Role value
 * @returns {string} - Formatted role string
 */
function formatRole(role) {
    if (!role) return '-';
    return role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Format genre value for display
 * @param {string} genre - Genre value
 * @returns {string} - Formatted genre string
 */
function formatGenre(genre) {
    if (!genre) return '-';
    
    const genreMap = {
        'rnb': 'R&B',
        'country': 'Country',
        'classic': 'Classic',
        'jazz': 'Jazz'
    };
    
    return genreMap[genre] || genre;
}

/**
 * Create pagination UI
 * @param {string} type - Pagination type (users, artists, songs)
 * @param {number} totalPages - Total number of pages
 * @param {number} currentPage - Current active page
 * @param {function} loadFunction - Function to call when page changes
 */
function setupPagination(type, totalPages, currentPage, loadFunction) {
    const container = document.getElementById(`${type}-pagination`);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    if (currentPage > 1) {
        const prevButton = document.createElement('button');
        prevButton.className = 'pagination-button';
        prevButton.innerHTML = '&laquo;';
        prevButton.addEventListener('click', () => loadFunction(currentPage - 1));
        container.appendChild(prevButton);
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
                    container.appendChild(ellipsis);
                }
                continue;
            }
            
            if (i > currentPage + 1 && i < totalPages - 1) {
                if (i === currentPage + 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.textContent = '...';
                    container.appendChild(ellipsis);
                }
                continue;
            }
        }
        
        const pageButton = document.createElement('button');
        pageButton.className = 'pagination-button';
        if (i === currentPage) pageButton.classList.add('active');
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            if (i !== currentPage) {
                loadFunction(i);
            }
        });
        container.appendChild(pageButton);
    }
    
    // Next button
    if (currentPage < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.className = 'pagination-button';
        nextButton.innerHTML = '&raquo;';
        nextButton.addEventListener('click', () => loadFunction(currentPage + 1));
        container.appendChild(nextButton);
    }
}

/**
 * Show an error message to the user
 * @param {string} message - Error message to display
 */
function showError(message) {
    alert(message);
}

/**
 * Show a success message to the user
 * @param {string} message - Success message to display
 */
function showSuccess(message) {
    alert(message);
}