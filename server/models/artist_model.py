import csv
import io
from database.db_connection import execute_query

class Artist:
    def __init__(self, id=None, name=None, dob=None, gender=None, address=None,
                 first_release_year=None, no_of_albums_released=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.dob = dob
        self.gender = gender
        self.address = address
        self.first_release_year = first_release_year
        self.no_of_albums_released = no_of_albums_released
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(name, dob=None, gender=None, address=None, first_release_year=None, no_of_albums_released=0):
        """Create a new artist in the database"""
        query = """
            INSERT INTO artists 
            (name, dob, gender, address, first_release_year, no_of_albums_released) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, dob, gender, address, first_release_year, no_of_albums_released)
        return execute_query(query, params)
    
    @staticmethod
    def get_by_id(artist_id):
        """Get an artist by ID"""
        query = "SELECT * FROM artists WHERE id = %s"
        return execute_query(query, (artist_id,), fetchone=True)
    
    @staticmethod
    def get_all(page=1, per_page=10):
        """Get all artists with pagination"""
        offset = (page - 1) * per_page
        query = "SELECT * FROM artists LIMIT %s OFFSET %s"
        return execute_query(query, (per_page, offset), fetchall=True)
    
    @staticmethod
    def update(artist_id, data):
        """Update an artist's information"""
        fields = []
        params = []
        
        for key, value in data.items():
            if key != 'id' and value is not None:
                fields.append(f"{key} = %s")
                params.append(value)
        
        params.append(artist_id)
        
        query = f"UPDATE artists SET {', '.join(fields)} WHERE id = %s"
        return execute_query(query, params)
    
    @staticmethod
    def delete(artist_id):
        """Delete an artist"""
        query = "DELETE FROM artists WHERE id = %s"
        return execute_query(query, (artist_id,))
    
    @staticmethod
    def count():
        """Count total number of artists"""
        query = "SELECT COUNT(*) as count FROM artists"
        result = execute_query(query, fetchone=True)
        return result['count'] if result else 0
    
    @staticmethod
    def import_from_csv(csv_content):
        """Import artists from CSV content"""
        created_count = 0
        
        try:
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                # Convert empty strings to None
                for key, value in row.items():
                    if value == '':
                        row[key] = None
                
                # Handle numeric conversions
                if 'no_of_albums_released' in row and row['no_of_albums_released']:
                    row['no_of_albums_released'] = int(row['no_of_albums_released'])
                else:
                    row['no_of_albums_released'] = 0
                
                # Create artist
                Artist.create(
                    name=row.get('name'),
                    dob=row.get('dob'),
                    gender=row.get('gender'),
                    address=row.get('address'),
                    first_release_year=row.get('first_release_year'),
                    no_of_albums_released=row.get('no_of_albums_released')
                )
                created_count += 1
            
            return {'success': True, 'count': created_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def export_to_csv():
        """Export all artists to CSV format"""
        query = "SELECT * FROM artists"
        artists = execute_query(query, fetchall=True)
        
        if not artists:
            return None
        
        output = io.StringIO()
        csv_writer = csv.DictWriter(output, fieldnames=artists[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(artists)
        
        return output.getvalue()
    
    @staticmethod
    def search(search_term, page=1, per_page=10):
        """Search artists by name"""
        offset = (page - 1) * per_page
        query = """
            SELECT * FROM artists 
            WHERE name LIKE %s 
            LIMIT %s OFFSET %s
        """
        search_pattern = f"%{search_term}%"
        return execute_query(query, (search_pattern, per_page, offset), fetchall=True)