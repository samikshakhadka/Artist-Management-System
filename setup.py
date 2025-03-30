import os
import bcrypt
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection using environment variables
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor()

# Get admin credentials from environment variables or use defaults
admin_first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
admin_last_name = os.getenv("ADMIN_LAST_NAME", "User")
admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
admin_role = os.getenv("ADMIN_ROLE", "super_admin")

# Generate hash at runtime
hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

# Insert admin user
cursor.execute("""
    INSERT INTO users (first_name, last_name, email, password, role) 
    VALUES (%s, %s, %s, %s, %s)
""", (admin_first_name, admin_last_name, admin_email, hashed_password.decode('utf-8'), admin_role))

conn.commit()
cursor.close()
conn.close()

print(f"Admin user created successfully with email: {admin_email}")