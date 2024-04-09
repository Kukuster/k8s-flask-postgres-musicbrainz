from typing import Callable, List, Union

from Levenshtein import distance as levenshtein_distance
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EntryNotFoundError(Exception):
    """Raised when an entry with a given ID does not exist in the table, but should"""


class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    mbid = db.Column(db.String, unique=True, nullable=False)
    track_title = db.Column(db.String, unique=True, nullable=False)
    release_id = db.Column(db.Integer, db.ForeignKey('releases.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    duration = db.Column(db.String, nullable=False)

class Release(db.Model):
    __tablename__ = 'releases'

    id = db.Column(db.Integer, primary_key=True)
    mbid = db.Column(db.String, unique=True, nullable=False)
    release_title = db.Column(db.String, unique=True, nullable=False)
    release_type = db.Column(db.String, nullable=False)
    release_date = db.Column(db.String, nullable=False)
    catalog_number = db.Column(db.String, nullable=False)
    barcode = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    mbid = db.Column(db.String, unique=True, nullable=False)
    artist_name = db.Column(db.String, unique=True, nullable=False)



def _track_title_distance(track: Track, query: str) -> float:
    title: str = track.track_title.lower()
    longer_len = max(len(title), len(query))

    return levenshtein_distance(title, query) / longer_len


def _track_title_distance_is_under_threshold(track: Track, query: str) -> bool:
    # query is allowed to be different by 15% of the length of the longer string, plus by 1 character
    additive_threshold = 1
    proportional_threshold = 0.15

    title: str = track.track_title.lower()
    longer_len = max(len(title), len(query))

    return _track_title_distance(track, query) < (proportional_threshold + additive_threshold/longer_len)


def search_by_title(Tracks: List[Track], query: str):
    """
    Query a track by inexact match with title, returning the best match if it matches well
    """
    query = query.lower()

    distance_from_query: Callable[[Track], float] = lambda track: _track_title_distance(track, query)
    best_match = min(Tracks, key=distance_from_query)

    # but is "best match" a good match?
    if _track_title_distance_is_under_threshold(best_match, query):
        return best_match
    else:
        return None


def get_release(release_id: int) -> Release:
    record: Union[Release, None] = db.session.get(Release, release_id) #type:ignore
    if record is None:
        raise EntryNotFoundError(f"Release with id {release_id} not found")
    return record

def get_artist(artist_id: int) -> Artist:
    record: Union[Artist, None] = db.session.get(Artist, artist_id) #type:ignore
    if record is None:
        raise EntryNotFoundError(f"Artist with id {artist_id} not found")
    return record


