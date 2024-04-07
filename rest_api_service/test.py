from typing import List
import unittest

from flask import json

from db import db, Song, Release, Artist
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

def generate_Song():
    song = Song()
    song.mbid = 'test-song-mbid'
    song.song_title = 'test-song-title'
    song.release_id = 1
    song.artist_id = 1
    song.duration = '03:00'
    return song

def generate_Songs():
    songs: List[Song] = []
    song = Song()
    song.mbid = 'test-song-mbid-1'
    song.song_title = 'test-song-title'
    song.release_id = 1
    song.artist_id = 1
    song.duration = '03:00'
    songs.append(song)

    song = Song()
    song.mbid = 'test-song-mbid-2'
    song.song_title = 'SECOND SONG'
    song.release_id = 1
    song.artist_id = 1
    song.duration = '04:00'
    songs.append(song)

    song = Song()
    song.mbid = 'test-song-mbid-3'
    song.song_title = 'test-s0ng-t1tl3'
    song.release_id = 1
    song.artist_id = 1
    song.duration = '05:00'
    songs.append(song)

    return songs


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig())
        self.client = self.app.test_client()
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with self.app.app_context():
            db.create_all()
            db.session.add(generate_Artist())
            db.session.add(generate_Release())
            for song in generate_Songs():
                db.session.add(song)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


    ### TESTS ###

    def test_search_song_exact_match(self):
        print("test_search_song_exact_match()")
        with self.app.app_context():

            response = self.client.get('/search-song', query_string={
                'q': 'test-song-title'
            })

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 200)
            self.assertEqual(data['mbid'], 'test-song-mbid-1')
            self.assertEqual(data['song_title'], 'test-song-title')
            self.assertEqual(data['release_title'], 'test-release-title')
            self.assertEqual(data['artist_name'], 'test-artist-name')
            self.assertEqual(data['duration'], '03:00')


    def test_search_song_similar(self):
        print("test_search_song_similar()")
        with self.app.app_context():
            # finds a song very similar by title to what's requested
            response = self.client.get('/search-song', query_string={
                'q': 'test-song-t1tle'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 200)
            self.assertEqual(data['mbid'], 'test-song-mbid-1')
            self.assertEqual(data['song_title'], 'test-song-title')
            self.assertEqual(data['release_title'], 'test-release-title')
            self.assertEqual(data['artist_name'], 'test-artist-name')
            self.assertEqual(data['duration'], '03:00')

            # does not find a song that is definitely not present in the test database
            response = self.client.get('/search-song', query_string={
                'q': 'Stare Into Death And Be Still'
            })
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 404)


    def test_search_song_empty_query(self):
        print("test_search_song_empty_query()")
        with self.app.app_context():
            response = self.client.get('/search-song', query_string={
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
