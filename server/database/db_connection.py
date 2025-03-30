import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Create a connection to the MySQL database
    Returns a connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="root",  # Replace with your MySQL password
            database="artist_management"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """
    Execute a SQL query with parameters
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetchone (bool, optional): Whether to fetch one result
        fetchall (bool, optional): Whether to fetch all results
        
    Returns:
        For INSERT/UPDATE/DELETE: The last row ID
        For SELECT with fetchone=True: A single record as dictionary
        For SELECT with fetchall=True: A list of records as dictionaries
        None if there's an error
    """
    connection = get_connection()
    if connection is None:
        return None
    
    cursor = connection.cursor(dictionary=True)
    result = None
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetchall:
            result = cursor.fetchall()
        elif fetchone:
            result = cursor.fetchone()
        else:
            connection.commit()
            result = cursor.lastrowid
    except Error as e:
        print(f"Error executing query: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
        
    return result