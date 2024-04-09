from typing import List
import unittest

from flask import json

from db import db, Track, Release, Artist
from create_app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


def generate_Artist():
    artist = Artist()
    artist.mbid = 'test-artist-mbid'
    artist.artist_name = 'test-artist-name'
    return artist

def generate_Release():
    release = Release()
    release.mbid = 'test-release-mbid'
    release.release_title = 'test-release-title'
    release.release_type = 'test-release-type'
    release.release_date = '2022-01-01'
    release.catalog_number = 'test-catalog-number'
    release.barcode = 'test-barcode'
    release.artist_id = 1
    return release

def generate_Track():
    track = Track()
    track.mbid = 'test-track-mbid'
    track.track_title = 'test-track-title'
    track.release_id = 1
    track.artist_id = 1
    track.duration = '03:00'
    return track

def generate_Tracks():
    tracks: List[Track] = []
    track = Track()
    track.mbid = 'test-track-mbid-1'
    track.track_title = 'test-track-title'
    track.release_id = 1
    track.artist_id = 1
    track.duration = '03:00'
    tracks.append(track)

    track = Track()
    track.mbid = 'test-track-mbid-2'
    track.track_title = 'SECOND TRACK'
    track.release_id = 1
    track.artist_id = 1
    track.duration = '04:00'
    tracks.append(track)

    track = Track()
    track.mbid = 'test-track-mbid-3'
    track.track_title = 'test-tr@ck-t1tl3'
    track.release_id = 1
    track.artist_id = 1
    track.duration = '05:00'
    tracks.append(track)

    return tracks


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig())
        self.client = self.app.test_client()
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with self.app.app_context():
            db.create_all()
            db.session.add(generate_Artist())
            db.session.add(generate_Release())
            for track in generate_Tracks():
                db.session.add(track)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


    ### TESTS ###

    def test_search_track_exact_match(self):
        print("test_search_track_exact_match()")
        with self.app.app_context():

            response = self.client.get('/search-track', query_string={
                'q': 'test-track-title'
            })

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 200)
            self.assertEqual(data['mbid'], 'test-track-mbid-1')
            self.assertEqual(data['track_title'], 'test-track-title')
            self.assertEqual(data['release_title'], 'test-release-title')
            self.assertEqual(data['artist_name'], 'test-artist-name')
            self.assertEqual(data['duration'], '03:00')


    def test_search_track_similar(self):
        print("test_search_track_similar()")
        with self.app.app_context():
            # finds a track very similar by title to what's requested
            response = self.client.get('/search-track', query_string={
                'q': 'test-track-t1tle'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 200)
            self.assertEqual(data['mbid'], 'test-track-mbid-1')
            self.assertEqual(data['track_title'], 'test-track-title')
            self.assertEqual(data['release_title'], 'test-release-title')
            self.assertEqual(data['artist_name'], 'test-artist-name')
            self.assertEqual(data['duration'], '03:00')

            # does not find a track that is definitely not present in the test database
            response = self.client.get('/search-track', query_string={
                'q': 'Stare Into Death And Be Still'
            })
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 404)


    def test_search_track_empty_query(self):
        print("test_search_track_empty_query()")
        with self.app.app_context():
            response = self.client.get('/search-track', query_string={
                'q': ''
            })
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 400)


    def test_are_you_up(self):
        print("test_are_you_up()")

        response = self.client.get('/are-you-up')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')



if __name__ == '__main__':
    unittest.main()
