// Load users with pagination
async function loadUsers(page = 1, perPage = 10) {
    // Only super_admin can access users data
    if (!hasRole(currentUser, ['super_admin'])) {
        document.querySelector('#users-table tbody').innerHTML = `
            <tr><td colspan="7" class="text-center">You don't have permission to view users.</td></tr>
        `;
        return;
    }
    
    // Show loading indication
    document.querySelector('#users-table tbody').innerHTML = `
        <tr><td colspan="7" class="text-center">Loading users...</td></tr>
    `;
    
    try {
        const response = await fetch(`/api/users?page=${page}&per_page=${perPage}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load users');
        }
        
        const { users, pagination } = data.body;
        const tbody = document.querySelector('#users-table tbody');
        
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center">No users found</td></tr>`;
            return;
        }
        
        // Clear table body
        tbody.innerHTML = '';
        
        // Add user rows
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.first_name}</td>
                <td>${user.last_name}</td>
                <td>${user.email}</td>
                <td>${user.phone || '-'}</td>
                <td><span class="user-role">${formatRole(user.role)}</span></td>
                <td class="actions-cell">
                    <button class="btn-action btn-view" onclick="viewUser(${user.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-action btn-edit" onclick="editUser(${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteUser(${user.id})"
                        ${user.id === currentUser.id ? 'disabled' : ''}>
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Create pagination
        createPagination('users', pagination.total_pages, pagination.page, loadUsers);
        
    } catch (error) {
        console.error('Error loading users:', error);
        document.querySelector('#users-table tbody').innerHTML = `
            <tr><td colspan="7" class="text-center">Error loading users: ${error.message}</td></tr>
        `;
    }
}

// View user details
async function viewUser(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load user');
        }
        
        const user = data.body.user;
        
        // Set modal title and content
        document.getElementById('user-modal-title').textContent = 'View User';
        
        // Populate form with user data
        document.getElementById('user-id').value = user.id;
        document.getElementById('user-first-name').value = user.first_name;
        document.getElementById('user-first-name').disabled = true;
        document.getElementById('user-last-name').value = user.last_name;
        document.getElementById('user-last-name').disabled = true;
        document.getElementById('user-email').value = user.email;
        document.getElementById('user-email').disabled = true;
        document.getElementById('user-password').disabled = true;
        document.getElementById('user-phone').value = user.phone || '';
        document.getElementById('user-phone').disabled = true;
        document.getElementById('user-dob').value = user.dob ? user.dob.split('T')[0] : '';
        document.getElementById('user-dob').disabled = true;
        document.getElementById('user-gender').value = user.gender || '';
        document.getElementById('user-gender').disabled = true;
        document.getElementById('user-address').value = user.address || '';
        document.getElementById('user-address').disabled = true;
        document.getElementById('user-role').value = user.role;
        document.getElementById('user-role').disabled = true;
        
        // Hide password field and hint
        document.getElementById('password-hint').style.display = 'none';
        
        // Change buttons in modal footer
        const modalFooter = document.querySelector('#user-form .modal-footer');
        modalFooter.innerHTML = `
            <button type="button" class="btn" onclick="editUser(${user.id})">Edit</button>
            <button type="button" class="btn" onclick="closeUserModal()">Close</button>
        `;
        
        // Show the modal
        document.getElementById('user-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error viewing user:', error);
        showError('Error loading user: ' + error.message);
    }
}

// Edit user
async function editUser(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to load user');
        }
        
        const user = data.body.user;
        
        // Set modal title
        document.getElementById('user-modal-title').textContent = 'Edit User';
        
        // Populate form with user data
        document.getElementById('user-id').value = user.id;
        document.getElementById('user-first-name').value = user.first_name;
        document.getElementById('user-first-name').disabled = false;
        document.getElementById('user-last-name').value = user.last_name;
        document.getElementById('user-last-name').disabled = false;
        document.getElementById('user-email').value = user.email;
        document.getElementById('user-email').disabled = false;
        document.getElementById('user-password').value = '';
        document.getElementById('user-password').disabled = false;
        document.getElementById('user-phone').value = user.phone || '';
        document.getElementById('user-phone').disabled = false;
        document.getElementById('user-dob').value = user.dob ? user.dob.split('T')[0] : '';
        document.getElementById('user-dob').disabled = false;
        document.getElementById('user-gender').value = user.gender || '';
        document.getElementById('user-gender').disabled = false;
        document.getElementById('user-address').value = user.address || '';
        document.getElementById('user-address').disabled = false;
        document.getElementById('user-role').value = user.role;
        document.getElementById('user-role').disabled = false;
        
        // Show password hint
        document.getElementById('password-hint').style.display = 'block';
        
        // Reset modal footer
        const modalFooter = document.querySelector('#user-form .modal-footer');
        modalFooter.innerHTML = `
            <button type="button" class="btn" id="user-cancel-btn" onclick="closeUserModal()">Cancel</button>
            <button type="submit" class="btn">Save</button>
        `;
        
        // Show the modal
        document.getElementById('user-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error editing user:', error);
        showError('Error loading user: ' + error.message);
    }
}

// Create new user
function createUser() {
    // Set modal title
    document.getElementById('user-modal-title').textContent = 'Add New User';
    
    // Reset form
    document.getElementById('user-form').reset();
    document.getElementById('user-id').value = '';
    
    // Enable all fields
    const formElements = document.querySelectorAll('#user-form input, #user-form select, #user-form textarea');
    formElements.forEach(el => {
        el.disabled = false;
    });
    
    // Hide password hint
    document.getElementById('password-hint').style.display = 'none';
    
    // Set default role if it's needed
    if (document.getElementById('user-role')) {
        document.getElementById('user-role').value = 'artist'; // Default role
    }
    
    // Reset modal footer
    const modalFooter = document.querySelector('#user-form .modal-footer');
    modalFooter.innerHTML = `
        <button type="button" class="btn" id="user-cancel-btn" onclick="closeUserModal()">Cancel</button>
        <button type="submit" class="btn">Save</button>
    `;
    
    // Show the modal
    document.getElementById('user-modal').style.display = 'block';
}

// Close user modal
function closeUserModal() {
    document.getElementById('user-modal').style.display = 'none';
}

// Save user (create or update)
async function saveUser(e) {
    e.preventDefault();
    
    const userId = document.getElementById('user-id').value;
    const isUpdate = userId !== '';
    
    // Get form values
    const firstName = document.getElementById('user-first-name').value;
    const lastName = document.getElementById('user-last-name').value;
    const email = document.getElementById('user-email').value;
    const password = document.getElementById('user-password').value;
    const phone = document.getElementById('user-phone').value;
    const dob = document.getElementById('user-dob').value;
    const gender = document.getElementById('user-gender').value;
    const address = document.getElementById('user-address').value;
    const role = document.getElementById('user-role').value;
    
    // Validate required fields
    if (!firstName || !lastName || !email || !role) {
        showError('First name, last name, email, and role are required fields');
        return;
    }
    
    if (!isUpdate && !password) {
        // Password is required for new users
        showError('Password is required for new users');
        return;
    }
    
    // Create user data object
    const userData = {
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone || '',
        dob: dob || '',
        gender: gender || '',
        address: address || '',
        role: role
    };
    
    // Add password only if provided
    if (password) {
        userData.password = password;
    }
    
    try {
        const url = isUpdate ? `/api/users/${userId}` : '/api/users';
        const method = isUpdate ? 'PUT' : 'POST';
        
        console.log('Sending user data:', userData); // Debug log
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `Failed to ${isUpdate ? 'update' : 'create'} user`);
        }
        
        if (data.body && data.body.success) {
            // Close modal
            closeUserModal();
            
            // Show success message
            showSuccess(`User ${isUpdate ? 'updated' : 'created'} successfully`);
            
            // Reload users list
            loadUsers();
        } else {
            throw new Error(data.message || data.body?.message || `Failed to ${isUpdate ? 'update' : 'create'} user`);
        }
    } catch (error) {
        console.error(`Error ${userId ? 'updating' : 'creating'} user:`, error);
        showError(error.message);
    }
}

// Delete user
async function deleteUser(userId) {
    // Prevent deleting current user
    if (userId === currentUser.id) {
        showError('You cannot delete your own account');
        return;
    }
    
    // Confirm deletion
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to delete user');
        }
        
        if (data.body.success) {
            showSuccess('User deleted successfully');
            loadUsers(); // Reload users list
        } else {
            throw new Error(data.body.message || 'Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showError('Error deleting user: ' + error.message);
    }
}

// Format role for display
function formatRole(role) {
    return role.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Initialize user management
function initUserManagement() {
    // Add user form submission handler
    const userForm = document.getElementById('user-form');
    if (userForm) {
        userForm.addEventListener('submit', saveUser);
    }
    
    // Add user button click handler
    const addUserBtn = document.getElementById('add-user-btn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', createUser);
    }
    
    // Add event listeners for all user buttons if they exist
    document.querySelectorAll('.btn-view[onclick^="viewUser"]').forEach(btn => {
        const userId = btn.getAttribute('onclick').match(/\d+/)[0];
        btn.addEventListener('click', () => viewUser(userId));
    });
    
    document.querySelectorAll('.btn-edit[onclick^="editUser"]').forEach(btn => {
        const userId = btn.getAttribute('onclick').match(/\d+/)[0];
        btn.addEventListener('click', () => editUser(userId));
    });
    
    document.querySelectorAll('.btn-delete[onclick^="deleteUser"]').forEach(btn => {
        const userId = btn.getAttribute('onclick').match(/\d+/)[0];
        btn.addEventListener('click', () => deleteUser(userId));
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // This will be called by main.js when the dashboard is loaded
    if (typeof initUserFormHandlers === 'function') {
        initUserFormHandlers();
    }
    
    // Initialize user management if we're on a page with users table
    if (document.getElementById('users-table')) {
        initUserManagement();
    }
});

// Export functions for use in other scripts
if (typeof window !== 'undefined') {
    window.userManagement = {
        loadUsers,
        viewUser,
        editUser,
        createUser,
        closeUserModal,
        saveUser,
        deleteUser,
        formatRole,
        initUserManagement
    };
}