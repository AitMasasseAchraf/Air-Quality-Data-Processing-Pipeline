-- Create the cities table with a city_id
CREATE TABLE IF NOT EXISTS cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(255),
    lat FLOAT,
    lng FLOAT,
    admin_name VARCHAR(255)
);

-- Create the index_table with a foreign key reference to city_id
CREATE TABLE IF NOT EXISTS index_table (
    index_id INT AUTO_INCREMENT PRIMARY KEY,
    index_type VARCHAR(255),
    index_name VARCHAR(255),
    index_qualification VARCHAR(255),
    index_value FLOAT,
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Create the pollutants table with a foreign key reference to city_id
CREATE TABLE IF NOT EXISTS pollutants (
    pollutant_id INT AUTO_INCREMENT PRIMARY KEY,
    shortcode VARCHAR(255),
    name VARCHAR(255),
    unit VARCHAR(50),
    value FLOAT,
    confidence FLOAT,
    index_qualification VARCHAR(255),
    index_value FLOAT,
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
