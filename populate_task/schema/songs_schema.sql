CREATE TABLE IF NOT EXISTS songs (
    id SERIAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mbid UUID NOT NULL,
    song_title VARCHAR(255) NOT NULL,
    release_id INTEGER NOT NULL REFERENCES releases(id),
    artist_id INTEGER NOT NULL REFERENCES artists(id),
    duration VARCHAR(255) NOT NULL, -- `length` is an SQL keyword; format "MM:SS"
    CONSTRAINT PK_id PRIMARY KEY (id),
    CONSTRAINT fk_artist FOREIGN KEY (artist_id) REFERENCES artists(id),
    CONSTRAINT fk_release FOREIGN KEY (release_id) REFERENCES releases(id),
    CONSTRAINT chk_one_song_mbid UNIQUE (mbid),
    CONSTRAINT chk_one_performance UNIQUE (song_title, artist_id),
    CONSTRAINT chk_one_release UNIQUE (song_title, release_id)
);
