// Check if user is authenticated
async function checkAuth() {
    try {
        const response = await fetch('/api/check-auth', {
            method: 'GET',
            credentials: 'include' // Include cookies
        });
        
        const data = await response.json();
        
        if (data.authenticated) {
            return data.user;
        }
        
        return null;
    } catch (error) {
        console.error('Authentication check failed:', error);
        return null;
    }
}

// Handle login
async function login(email, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include' // Include cookies
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.user;
        }
        
        throw new Error(data.message || 'Login failed');
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
}

// Handle registration
async function register(userData) {
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data;
        }
        
        throw new Error(data.message || 'Registration failed');
    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
}

// Handle logout
async function logout() {
    try {
        await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include' // Include cookies
        });
        
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout failed:', error);
        alert('Logout failed: ' + error.message);
    }
}

// Check if user has specific role
function hasRole(user, roles) {
    if (!user) return false;
    if (!Array.isArray(roles)) roles = [roles];
    return roles.includes(user.role);
}