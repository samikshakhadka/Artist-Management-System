# Artist Management System

A simple admin panel to manage records of artists with their songs collection. The application implements a Role-Based Access Control (RBAC) system with three user roles: super_admin, artist_manager, and artist.

## Project Structure

```
artist_management/
├── client/                    # Client-side files
│   ├── index.html            # Main dashboard HTML
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── dashboard.html        # Dashboard page
│   └── static/               # Static assets
│       ├── css/
│       │   └── styles.css    # Main stylesheet
│       ├── js/
│       │   ├── api.js        # API interaction functions
│       │   ├── auth.js       # Authentication functions
│       │   ├── artists.js    # Artist management functions
│       │   ├── common.js     # Utility functions
│       │   ├── main.js       # Main dashboard functionality
│       │   ├── music.js      # Music management functions
│       │   ├── setup.js      # Modal setup and event handlers
│       │   └── users.js      # User management functions
│       └── img/              # Images (if any)
│
└── server/                    # Server-side files
    ├── database/
    │   ├── db_connection.py  # Database connection handling
    │   └── queries.py        # SQL queries
    ├── models/               # Database models
    │   ├── user_model.py     # User model with database operations
    │   ├── artist_model.py   # Artist model with database operations
    │   └── music_model.py    # Music model with database operations
    ├── controllers/          # API controllers
    │   ├── controller_init.py # Initializes all controllers
    │   ├── user_controller.py # User related endpoints
    │   ├── artist_controller.py # Artist related endpoints
    │   └── music_controller.py # Music related endpoints
    ├── auth/                 # Authentication handling
    │   └── auth_handler.py   # Login, register, session management
    └── server.py             # Main server file
├── setup.py                  # Initial admin user setup
└── run.py                    # Project runner script
```

## Features

- **User Management**: Create, read, update, and delete users (super_admin only)
- **Artist Management**: Manage artist profiles (super_admin, artist_manager)
- **Song Management**: Each artist can manage their own songs collection
- **CSV Import/Export**: Import and export artist data in CSV format (artist_manager)
- **Role-Based Access Control**: Different permissions based on user roles

## Tech Stack

- Backend: Python with raw SQL queries (no ORM)
- Frontend: HTML, CSS, JavaScript
- Database: MySQL

## Database Schema

```sql
-- User Table
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(500) NOT NULL,
  phone VARCHAR(20),
  dob DATETIME,
  gender ENUM('m', 'f', 'o'),
  address VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  role ENUM('super_admin', 'artist_manager', 'artist') NOT NULL
);

-- Artist Table
CREATE TABLE artists (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  dob DATETIME,
  gender ENUM('m', 'f', 'o'),
  address VARCHAR(255),
  first_release_year YEAR,
  no_of_albums_released INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Music/Song Table
CREATE TABLE music (
  id INT PRIMARY KEY AUTO_INCREMENT,
  artist_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  album_name VARCHAR(255),
  genre ENUM('rnb', 'country', 'classic', 'jazz'),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);
```

## Installation & Setup

1. Clone the repository
2. Set up MySQL database using the provided schema in `database schema/query`
3. Create a Python virtual environment and install dependencies:
```
pip install mysql-connector-python bcrypt
```
4. Run the setup script to create admin user:
```
python setup.py
```

## Running the Project

To start the web server, run:
```
python run.py run project
```

The application will be available at http://localhost:8000

## Default Login

- Email: admin@example.com
- Password: admin123

## User Roles

- **super_admin**: Full access to all features
- **artist_manager**: Manage artists and view their songs
- **artist**: Manage their own songs

For detailed technical documentation, please refer to [technical_documentation.md](technical_documentation.md)

## License

MIT