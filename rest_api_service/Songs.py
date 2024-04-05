from typing import Callable, List

from Levenshtein import distance as levenshtein_distance
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    mbid = db.Column(db.String, unique=True, nullable=False)
    song_title = db.Column(db.String, unique=True, nullable=False)
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    duration = db.Column(db.String, nullable=False)

# def init_db(new_db):
#     global db, Song
#     db = new_db
#     class Song(db.Model):
#         __tablename__ = 'songs'

#         id = db.Column(db.Integer, primary_key=True)
#         mbid = db.Column(db.String, unique=True, nullable=False)
#         song_title = db.Column(db.String, unique=True, nullable=False)
#         release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
#         artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
#         duration = db.Column(db.String, nullable=False)

def _song_title_distance(song: Song, query: str) -> float:
    title: str = song.song_title.lower()
    longer_len = max(len(title), len(query))

    return levenshtein_distance(title, query) / longer_len

def _song_title_distance_is_under_threshold(song: Song, query: str) -> bool:
    # query is allowed to be different by 15% of the length of the longer string, plus 1 character
    additive_threshold = 1
    proportional_threshold = 0.15

    title: str = song.song_title.lower()
    longer_len = max(len(title), len(query))

    return _song_title_distance(song, query) < (proportional_threshold + additive_threshold/longer_len)


def search_by_title(Songs: List[Song], query: str):
    """
    Query a song by inexact match with title, returning the best match if it matches well
    """
    query = query.lower()

    distance_from_query: Callable[[Song], float] = lambda song: _song_title_distance(song, query)
    best_match = min(Songs, key=distance_from_query)

    # but is "best match" a good match?
    if _song_title_distance_is_under_threshold(best_match, query):
        return best_match
    else:
        return None

