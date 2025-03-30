from models.music_model import Music
from models.artist_model import Artist
from auth.auth_handler import requires_role, requires_auth

def register_music_routes(route):
    """Register all music-related routes with the router"""
    
    @route('/api/music', methods=['GET'])
    @requires_role(['super_admin', 'artist_manager', 'artist'])
    def get_all_music(request):
        """Get all music with pagination"""
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        search = request.query_params.get('search', '')
        
        if search:
            music_list = Music.search(search, page, per_page)
        else:
            music_list = Music.get_all(page, per_page)
            
        total = Music.count()
        
        return {
            'status': 200,
            'body': {
                'music': music_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }
        }
    
    @route('/api/artists/{artist_id}/music', methods=['GET'])
    @requires_role(['super_admin', 'artist_manager', 'artist'])
    def get_artist_music(request):
        """Get all music for a specific artist with pagination"""
        artist_id = request.path.split('/')[-2]
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        
        # Check if artist exists
        artist = Artist.get_by_id(artist_id)
        if not artist:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Artist not found'}
            }
        
        music_list = Music.get_by_artist(artist_id, page, per_page)
        total = Music.count_by_artist(artist_id)
        
        return {
            'status': 200,
            'body': {
                'artist': artist,
                'music': music_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }
        }
    
    @route('/api/artists/{artist_id}/music', methods=['POST'])
    @requires_role(['artist'])
    def create_music(request):
        """Create a new song for an artist"""
        artist_id = request.path.split('/')[-2]
        data = request.json_data or request.form_data
        
        # Check if artist exists
        artist = Artist.get_by_id(artist_id)
        if not artist:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Artist not found'}
            }
        
        # Validate required fields
        if 'title' not in data or not data['title']:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Title is required'}
            }
        
        # Validate genre if provided
        if 'genre' in data and data['genre']:
            valid_genres = ['rnb', 'country', 'classic', 'jazz']
            if data['genre'] not in valid_genres:
                return {
                    'status': 400,
                    'body': {'success': False, 'message': 'Invalid genre'}
                }
        
        # Create music
        music_id = Music.create(
            artist_id=artist_id,
            title=data['title'],
            album_name=data.get('album_name'),
            genre=data.get('genre')
        )
        
        if not music_id:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to create song'}
            }
        
        # Update artist's album count if album_name is provided and not None
        if data.get('album_name'):
            # This is a simplistic approach - in a real application, you'd check
            # if this is actually a new album name for this artist
            Artist.update(artist_id, {
                'no_of_albums_released': artist['no_of_albums_released'] + 1
            })
        
        return {
            'status': 201,
            'body': {
                'success': True,
                'message': 'Song created successfully',
                'music_id': music_id
            }
        }
    
    @route('/api/music/{id}', methods=['GET'])
    @requires_role(['super_admin', 'artist_manager', 'artist'])
    def get_music(request):
        """Get a song by ID"""
        music_id = request.path.split('/')[-1]
        
        music = Music.get_by_id(music_id)
        if not music:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Song not found'}
            }
        
        return {
            'status': 200,
            'body': {'music': music}
        }
    
    @route('/api/music/{id}', methods=['PUT'])
    @requires_role(['artist'])
    def update_music(request):
        """Update a song"""
        music_id = request.path.split('/')[-1]
        data = request.json_data or request.form_data
        
        # Check if music exists
        music = Music.get_by_id(music_id)
        if not music:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Song not found'}
            }
        
        # Check if the artist is the owner of this song
        if request.user['role'] == 'artist' and str(request.user['id']) != str(music['artist_id']):
            return {
                'status': 403,
                'body': {
                    'success': False,
                    'message': 'You do not have permission to update this song'
                }
            }
        
        # Validate title if provided
        if 'title' in data and not data['title']:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Title cannot be empty'}
            }
        
        # Validate genre if provided
        if 'genre' in data and data['genre']:
            valid_genres = ['rnb', 'country', 'classic', 'jazz']
            if data['genre'] not in valid_genres:
                return {
                    'status': 400,
                    'body': {'success': False, 'message': 'Invalid genre'}
                }
        
        # Update music
        result = Music.update(music_id, data)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to update song'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'Song updated successfully'
            }
        }
    
    @route('/api/music/{id}', methods=['DELETE'])
    @requires_role(['artist'])
    def delete_music(request):
        """Delete a song"""
        music_id = request.path.split('/')[-1]
        
        # Check if music exists
        music = Music.get_by_id(music_id)
        if not music:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'Song not found'}
            }
        
        # Check if the artist is the owner of this song
        if request.user['role'] == 'artist' and str(request.user['id']) != str(music['artist_id']):
            return {
                'status': 403,
                'body': {
                    'success': False,
                    'message': 'You do not have permission to delete this song'
                }
            }
        
        # Delete music
        result = Music.delete(music_id)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to delete song'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'Song deleted successfully'
            }
        }
    
    @route('/api/music/genre/{genre}', methods=['GET'])
    @requires_role(['super_admin', 'artist_manager', 'artist'])
    def get_music_by_genre(request):
        """Get music by genre with pagination"""
        genre = request.path.split('/')[-1]
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        
        # Validate genre
        valid_genres = ['rnb', 'country', 'classic', 'jazz']
        if genre not in valid_genres:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Invalid genre'}
            }
        
        music_list = Music.get_by_genre(genre, page, per_page)
        
        # Count would be more efficient with a dedicated count_by_genre method,
        # but we'll use this approach for simplicity
        total = len(Music.get_by_genre(genre, 1, 1000000))
        
        return {
            'status': 200,
            'body': {
                'genre': genre,
                'music': music_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }
        }