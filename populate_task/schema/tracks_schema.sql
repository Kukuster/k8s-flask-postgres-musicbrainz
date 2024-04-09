CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mbid UUID NOT NULL,
    track_title VARCHAR(255) NOT NULL,
    release_id INTEGER NOT NULL REFERENCES releases(id),
    artist_id INTEGER NOT NULL REFERENCES artists(id),
    duration VARCHAR(255) NOT NULL, -- `length` is an SQL keyword; format "mm:ss"
    CONSTRAINT PK_id PRIMARY KEY (id),
    CONSTRAINT fk_artist FOREIGN KEY (artist_id) REFERENCES artists(id),
    CONSTRAINT fk_release FOREIGN KEY (release_id) REFERENCES releases(id),
    CONSTRAINT chk_one_track_mbid UNIQUE (mbid),
    CONSTRAINT chk_one_performance UNIQUE (track_title, artist_id),
    CONSTRAINT chk_one_release UNIQUE (track_title, release_id)
);
