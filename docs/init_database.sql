-- Script SQL pour créer la base de données WeatherTrip
-- Pour PostgreSQL

-- Créer la base de données (exécuter cette commande séparément si nécessaire)
-- CREATE DATABASE weathertrip_db;

-- Se connecter à la base de données
\c weathertrip_db

-- Supprimer les tables si elles existent déjà (pour réinitialisation)
DROP TABLE IF EXISTS weather_data CASCADE;
DROP TABLE IF EXISTS destinations CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Table des utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Table des voyages
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX idx_trips_user_id ON trips(user_id);

-- Table des destinations
CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(200) NOT NULL,
    country VARCHAR(100) NOT NULL,
    arrival_date TIMESTAMP,
    departure_date TIMESTAMP,
    latitude FLOAT,
    longitude FLOAT,
    trip_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX idx_destinations_trip_id ON destinations(trip_id);

-- Table des données météo
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER NOT NULL,
    temperature FLOAT,
    feels_like FLOAT,
    temp_min FLOAT,
    temp_max FLOAT,
    humidity INTEGER,
    weather_main VARCHAR(100),
    weather_description VARCHAR(255),
    icon VARCHAR(10),
    wind_speed FLOAT,
    clouds INTEGER,
    forecast_date TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX idx_weather_destination_id ON weather_data(destination_id);
CREATE INDEX idx_weather_fetched_at ON weather_data(fetched_at);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pour mettre à jour updated_at sur la table trips
CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON trips
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insertion de données de test (optionnel)
-- Utilisateur de test
INSERT INTO users (username, email, password_hash) VALUES 
('demo', 'demo@weathertrip.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lU7jN8FeXi4m'); -- mot de passe: demo123

-- Voyage de test
INSERT INTO trips (name, description, start_date, end_date, user_id) VALUES 
('Voyage en Europe', 'Tour des capitales européennes', '2026-06-01', '2026-06-15', 1);

-- Destinations de test
INSERT INTO destinations (city, country, arrival_date, departure_date, trip_id) VALUES 
('Paris', 'France', '2026-06-01', '2026-06-05', 1),
('Londres', 'Royaume-Uni', '2026-06-05', '2026-06-10', 1),
('Berlin', 'Allemagne', '2026-06-10', '2026-06-15', 1);

-- Afficher un résumé
SELECT 'Base de données initialisée avec succès !' as message;
SELECT COUNT(*) as nb_users FROM users;
SELECT COUNT(*) as nb_trips FROM trips;
SELECT COUNT(*) as nb_destinations FROM destinations;
