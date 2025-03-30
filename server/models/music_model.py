from database.db_connection import execute_query

class Music:
    def __init__(self, id=None, artist_id=None, title=None, album_name=None,
                 genre=None, created_at=None, updated_at=None):
        self.id = id
        self.artist_id = artist_id
        self.title = title
        self.album_name = album_name
        self.genre = genre
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(artist_id, title, album_name=None, genre=None):
        """Create a new song in the database"""
        query = """
            INSERT INTO music 
            (artist_id, title, album_name, genre) 
            VALUES (%s, %s, %s, %s)
        """
        params = (artist_id, title, album_name, genre)
        return execute_query(query, params)
    
    @staticmethod
    def get_by_id(music_id):
        """Get a song by ID"""
        query = "SELECT * FROM music WHERE id = %s"
        return execute_query(query, (music_id,), fetchone=True)
    
    @staticmethod
    def get_all(page=1, per_page=10):
        """Get all songs with pagination"""
        offset = (page - 1) * per_page
        query = """
            SELECT m.*, a.name as artist_name 
            FROM music m
            JOIN artists a ON m.artist_id = a.id
            LIMIT %s OFFSET %s
        """
        return execute_query(query, (per_page, offset), fetchall=True)
    
    @staticmethod
    def get_by_artist(artist_id, page=1, per_page=10):
        """Get all songs for a specific artist with pagination"""
        offset = (page - 1) * per_page
        query = """
            SELECT m.*, a.name as artist_name 
            FROM music m
            JOIN artists a ON m.artist_id = a.id
            WHERE m.artist_id = %s
            LIMIT %s OFFSET %s
        """
        return execute_query(query, (artist_id, per_page, offset), fetchall=True)
    
    @staticmethod
    def update(music_id, data):
        """Update a song's information"""
        fields = []
        params = []
        
        for key, value in data.items():
            if key != 'id' and value is not None:
                fields.append(f"{key} = %s")
                params.append(value)
        
        params.append(music_id)
        
        query = f"UPDATE music SET {', '.join(fields)} WHERE id = %s"
        return execute_query(query, params)
    
    @staticmethod
    def delete(music_id):
        """Delete a song"""
        query = "DELETE FROM music WHERE id = %s"
        return execute_query(query, (music_id,))
    
    @staticmethod
    def count():
        """Count total number of songs"""
        query = "SELECT COUNT(*) as count FROM music"
        result = execute_query(query, fetchone=True)
        return result['count'] if result else 0
    
    @staticmethod
    def count_by_artist(artist_id):
        """Count number of songs for a specific artist"""
        query = "SELECT COUNT(*) as count FROM music WHERE artist_id = %s"
        result = execute_query(query, (artist_id,), fetchone=True)
        return result['count'] if result else 0
    
    @staticmethod
    def search(search_term, page=1, per_page=10):
        """Search songs by title or album name"""
        offset = (page - 1) * per_page
        query = """
            SELECT m.*, a.name as artist_name 
            FROM music m
            JOIN artists a ON m.artist_id = a.id
            WHERE m.title LIKE %s OR m.album_name LIKE %s
            LIMIT %s OFFSET %s
        """
        search_pattern = f"%{search_term}%"
        return execute_query(query, (search_pattern, search_pattern, per_page, offset), fetchall=True)
    
    @staticmethod
    def get_by_genre(genre, page=1, per_page=10):
        """Get songs by genre with pagination"""
        offset = (page - 1) * per_page
        query = """
            SELECT m.*, a.name as artist_name 
            FROM music m
            JOIN artists a ON m.artist_id = a.id
            WHERE m.genre = %s
            LIMIT %s OFFSET %s
        """
        return execute_query(query, (genre, per_page, offset), fetchall=True)