CREATE TABLE IF NOT EXISTS releases (
    id SERIAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    release_title VARCHAR(255) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES artists(id),
    CONSTRAINT PK_release_id PRIMARY KEY (id),
    CONSTRAINT fk_artist FOREIGN KEY (artist_id) REFERENCES artists(id),
    CONSTRAINT chk_one_edition UNIQUE (release_title, artist_id)
);
