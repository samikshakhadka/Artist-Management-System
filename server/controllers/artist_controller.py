import io
from models.artist_model import Artist
from auth.auth_handler import requires_role, requires_auth

def register_artist_routes(route):
    """Register all artist-related routes with the router"""
    
    @route('/api/artists', methods=['GET'])
    @requires_role(['super_admin', 'artist_manager', 'artist'])
    def get_artists(request):
        """Get all artists with pagination"""
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        search = request.query_params.get('search', '')
        
        if search:
            artists = Artist.search(search, page, per_page)
        else:
            artists = Artist.get_all(page, per_page)
            
        total = Artist.count()
        
        return {
            'status': 200,
            'body': {
                'artists': artists,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }
        }
    
    @route('/api/artists', methods=['POST'])
    @requires_role(['artist_manager'])
    def create_artist(request):
        """Create a new artist"""
        data = request.json_data or request.form_data
        
        # Validate required fields
        if 'name' not in data or not data['name']:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Name is required'}
            }
        
        # Create artist
        artist_id = Artist.create(
            name=data['name'],
            dob=data.get('dob'),
            gender=data.get('gender'),
            address=data.get('address'),
            first_release_year=data.get('first_release_year'),
            no_of_albums_released=data.get('no_of_albums_released', 0)
        )
        
        if not artist_id:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to create artist'}
            }
        
        return {
            'status': 201,
            'body': {
                'success': True,
                'message': 'Artist created successfully',
                'artist_id': artist_id
            }
        }
    
    @route('/api/artists/{id}', methods=['GET'])
    @requires_role(['super_admin', 'artist_manager'])
    def get_artist(request):
        """Get an artist by ID"""
        artist_id = request.path.split('/')[-1]
        
        artist = Artist.get_by_id(artist_id)
        if not artist:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Artist not found'}
            }
        
        return {
            'status': 200,
            'body': {'artist': artist}
        }
    
    @route('/api/artists/{id}', methods=['PUT'])
    @requires_role(['artist_manager'])
    def update_artist(request):
        """Update an artist"""
        artist_id = request.path.split('/')[-1]
        data = request.json_data or request.form_data
        
        # Check if artist exists
        artist = Artist.get_by_id(artist_id)
        if not artist:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Artist not found'}
            }
        
        # Validate name if provided
        if 'name' in data and not data['name']:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Name cannot be empty'}
            }
        
        # Update artist
        result = Artist.update(artist_id, data)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to update artist'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'Artist updated successfully'
            }
        }
    
    @route('/api/artists/{id}', methods=['DELETE'])
    @requires_role(['artist_manager'])
    def delete_artist(request):
        """Delete an artist"""
        artist_id = request.path.split('/')[-1]
        
        # Check if artist exists
        artist = Artist.get_by_id(artist_id)
        if not artist:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Artist not found'}
            }
        
        # Delete artist
        result = Artist.delete(artist_id)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to delete artist'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'Artist deleted successfully'
            }
        }
    
    @route('/api/artists/import', methods=['POST'])
    @requires_role(['artist_manager'])
    def import_artists(request):
        """Import artists from CSV"""
        data = request.form_data
        
        if 'csv_file' not in data:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'CSV file is required'}
            }
        
        # Get file content
        file_content = ''
        if isinstance(data['csv_file'], dict):  # Multipart form data
            file_content = data['csv_file']['value'].decode('utf-8')
        else:  # Plain text
            file_content = data['csv_file']
        
        # Import artists
        result = Artist.import_from_csv(file_content)
        
        if not result['success']:
            return {
                'status': 400,
                'body': {
                    'success': False,
                    'message': f"Failed to import CSV: {result['error']}"
                }
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': f"Successfully imported {result['count']} artists"
            }
        }
    
    @route('/api/artists/export', methods=['GET'])
    @requires_role(['artist_manager'])
    def export_artists(request):
        """Export artists to CSV"""
        csv_content = Artist.export_to_csv()
        
        if not csv_content:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'No artists found'}
            }
        
        return {
            'status': 200,
            'content_type': 'text/csv',
            'body': csv_content,
            'headers': {
                'Content-Disposition': 'attachment; filename=artists.csv'
            }
        }