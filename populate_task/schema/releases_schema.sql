CREATE TABLE IF NOT EXISTS releases (
    id SERIAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mbid UUID NOT NULL,
    release_title VARCHAR(255) NOT NULL,
    release_type VARCHAR(255) NOT NULL,
    release_date VARCHAR(11) NOT NULL, -- format: YYYY-MM-DD
    catalog_number VARCHAR(255) NOT NULL,
    barcode VARCHAR(255) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES artists(id),
    CONSTRAINT PK_release_id PRIMARY KEY (id),
    CONSTRAINT fk_artist FOREIGN KEY (artist_id) REFERENCES artists(id),
    CONSTRAINT chk_one_release_mbid UNIQUE (mbid),
    CONSTRAINT chk_one_edition UNIQUE (release_title, artist_id),
    CONSTRAINT chk_one_catalog_number UNIQUE (catalog_number),
    CONSTRAINT chk_one_barcode UNIQUE (barcode)
);
