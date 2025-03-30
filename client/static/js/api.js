const API = {
    // Base API request function
    request: async function(endpoint, method = 'GET', data = null, headers = {}) {
        showLoading();

        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                credentials: 'include' // Include cookies
            };

            if (data) {
                if (data instanceof FormData) {
                    // If FormData, remove Content-Type to let browser set it with boundary
                    delete options.headers['Content-Type'];
                    options.body = data;
                } else {
                    options.body = JSON.stringify(data);
                }
            }

            const response = await fetch(`/api/${endpoint}`, options);
            
            // Handle file downloads
            if (response.headers.get('Content-Disposition')?.includes('attachment')) {
                const blob = await response.blob();
                const filename = response.headers.get('Content-Disposition')
                    .split('filename=')[1]
                    .replace(/['"]/g, '');
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                hideLoading();
                return { success: true };
            }

            // Parse JSON for regular responses
            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                const jsonData = await response.json();
                hideLoading();
                return jsonData;
            } else {
                const textData = await response.text();
                hideLoading();
                return textData;
            }
        } catch (error) {
            console.error('API request error:', error);
            hideLoading();
            showError('Network error: ' + error.message);
            return { success: false, message: error.message };
        }
    },

    // User endpoints
    users: {
        getAll: (page = 1, perPage = 10) => API.request(`users?page=${page}&per_page=${perPage}`),
        getById: (id) => API.request(`users/${id}`),
        create: (userData) => API.request('users', 'POST', userData),
        update: (id, userData) => API.request(`users/${id}`, 'PUT', userData),
        delete: (id) => API.request(`users/${id}`, 'DELETE'),
        profile: () => API.request('profile'),
        updateProfile: (userData) => API.request('profile', 'PUT', userData)
    },

    // Artist endpoints
    artists: {
        getAll: (page = 1, perPage = 10, search = '') => 
            API.request(`artists?page=${page}&per_page=${perPage}${search ? `&search=${search}` : ''}`),
        getById: (id) => API.request(`artists/${id}`),
        create: (artistData) => API.request('artists', 'POST', artistData),
        update: (id, artistData) => API.request(`artists/${id}`, 'PUT', artistData),
        delete: (id) => API.request(`artists/${id}`, 'DELETE'),
        importCsv: (formData) => API.request('artists/import', 'POST', formData),
        exportCsv: () => API.request('artists/export')
    },

    // Music endpoints
    music: {
        getAll: (page = 1, perPage = 10, search = '') => 
            API.request(`music?page=${page}&per_page=${perPage}${search ? `&search=${search}` : ''}`),
        getByArtist: (artistId, page = 1, perPage = 10) => 
            API.request(`artists/${artistId}/music?page=${page}&per_page=${perPage}`),
        getById: (id) => API.request(`music/${id}`),
        create: (artistId, musicData) => API.request(`artists/${artistId}/music`, 'POST', musicData),
        update: (id, musicData) => API.request(`music/${id}`, 'PUT', musicData),
        delete: (id) => API.request(`music/${id}`, 'DELETE'),
        getByGenre: (genre, page = 1, perPage = 10) => 
            API.request(`music/genre/${genre}?page=${page}&per_page=${perPage}`)
    },

    // Auth endpoints
    auth: {
        login: (credentials) => API.request('login', 'POST', credentials),
        register: (userData) => API.request('register', 'POST', userData),
        logout: () => API.request('logout', 'POST'),
        checkAuth: () => API.request('check-auth')
    }
};