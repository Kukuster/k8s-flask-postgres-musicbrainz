CREATE TABLE IF NOT EXISTS artists (
    id SERIAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mbid UUID NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    -- genre VARCHAR(255) NOT NULL,
    -- bio TEXT NOT NULL
    CONSTRAINT PK_artist_id PRIMARY KEY (id),
    CONSTRAINT chk_one_artist_mbid UNIQUE (mbid),
    CONSTRAINT chk_one_artist UNIQUE (artist_name)
);
