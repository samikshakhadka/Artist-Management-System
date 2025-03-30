CREATE DATABASE IF NOT EXISTS artist_management;
USE artist_management;

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

-- Music/Song Table (renamed from 'songs' to 'music' as per your schema)
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

