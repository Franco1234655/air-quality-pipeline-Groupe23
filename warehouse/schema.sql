-- ==========================================
-- DATA WAREHOUSE
-- QUALITÉ DE L'AIR — OPENWEATHERMAP
-- MODÈLE EN ÉTOILE
-- ==========================================


-- ==========================================
-- DIMENSION : VILLE
-- ==========================================

CREATE TABLE IF NOT EXISTS dim_city (
    city_id SERIAL PRIMARY KEY,

    city_name VARCHAR(100) NOT NULL,

    country VARCHAR(100) NOT NULL,

    latitude DECIMAL(10, 6),

    longitude DECIMAL(10, 6),

    CONSTRAINT unique_city_country
        UNIQUE (
            city_name,
            country
        )
);


-- ==========================================
-- DIMENSION : DATE
-- ==========================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,

    full_date DATE NOT NULL UNIQUE,

    day INTEGER NOT NULL,

    month INTEGER NOT NULL,

    year INTEGER NOT NULL,

    quarter INTEGER NOT NULL
);


-- ==========================================
-- TABLE DE FAITS :
-- MESURES DE QUALITÉ DE L'AIR
-- ==========================================

CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_id BIGSERIAL PRIMARY KEY,

    city_id INTEGER NOT NULL,

    date_id INTEGER NOT NULL,

    measurement_time TIMESTAMPTZ,

    -- Indice OpenWeatherMap :
    -- 1 = Bonne
    -- 2 = Correcte
    -- 3 = Modérée
    -- 4 = Mauvaise
    -- 5 = Très mauvaise

    openweather_aqi INTEGER,

    pm2_5 DECIMAL(12, 4),

    pm10 DECIMAL(12, 4),

    carbon_monoxide DECIMAL(12, 4),

    nitrogen_dioxide DECIMAL(12, 4),

    sulphur_dioxide DECIMAL(12, 4),

    ozone DECIMAL(12, 4),

    ammonia DECIMAL(12, 4),

    air_quality_level VARCHAR(50),

    extracted_at TIMESTAMPTZ,

    CONSTRAINT fk_fact_city
        FOREIGN KEY (city_id)
        REFERENCES dim_city(city_id),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);