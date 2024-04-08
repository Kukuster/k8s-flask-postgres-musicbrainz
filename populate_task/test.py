import unittest

from musicbrainz_api import MusicBrainzAPI



class TestApp(unittest.TestCase):

    api: MusicBrainzAPI

    def setUp(self):
        self.api = MusicBrainzAPI()
        self.api.start()

    def tearDown(self):
        self.api.stop()


    ### TESTS ###

    def test_search_artist(self):
        artist_name = 'Imagine Dragons'
        artist_search_result = self.api.search_artist(artist_name)

        self.assertIsInstance(artist_search_result, dict)
        self.assertIn("artist-list", artist_search_result)

        try:
            self.assertIsInstance(artist_search_result["artist-list"], list)
            self.assertIsNot(len(artist_search_result["artist-list"]), 0)
            self.assertIn("name", artist_search_result["artist-list"][0])
            self.assertIn("id", artist_search_result["artist-list"][0])

            # Imagine Dragons found
            self.assertEqual(artist_search_result["artist-list"][0]["name"], artist_name)

        except (KeyError, TypeError, ValueError):
            self.fail("unexpected response format from search_artist()")


    def test_get_release_groups(self):
        artist_mbid = '012151a8-0f9a-44c9-997f-ebd68b5389f9'
        release_groups_result = self.api.get_release_groups(artist_mbid)

        self.assertIsInstance(release_groups_result, dict)
        self.assertIn("release-group-list", release_groups_result)

        try:
            self.assertIsInstance(release_groups_result["release-group-list"], list)
            self.assertIsNot(len(release_groups_result["release-group-list"]), 0)
            self.assertIn("id", release_groups_result["release-group-list"][0])
            self.assertIn("title", release_groups_result["release-group-list"][0])
            self.assertIn("type", release_groups_result["release-group-list"][0])
            self.assertIn("first-release-date", release_groups_result["release-group-list"][0])

            # found release group:
            # Imagine Dragons - 2012 - Night Visions
            self.assertEqual(release_groups_result["release-group-list"][0]["title"], "Night Visions")

        except (KeyError, TypeError, ValueError):
            self.fail("unexpected response format from browse_release_groups()")


    def test_get_releases(self):
        release_group_mbid = 'caef5f01-8568-4573-8458-c9e99ff7c734'
        releases_result = self.api.get_releases(release_group_mbid)

        self.assertIsInstance(releases_result, dict)
        self.assertIn("release-list", releases_result)

        try:
            self.assertIsInstance(releases_result["release-list"], list)
            self.assertIsNot(len(releases_result["release-list"]), 0)
            self.assertIn("id", releases_result["release-list"][0])
            self.assertIn("country", releases_result["release-list"][0])
            self.assertIn("release-event-list", releases_result["release-list"][0])
            self.assertIn("label-info-list", releases_result["release-list"][0])

            self.assertIsNot(len(releases_result["release-list"][0]["release-event-list"]), 0)
            self.assertIn("area", releases_result["release-list"][0]["release-event-list"][0])

            self.assertIsNot(len(releases_result["release-list"][0]["label-info-list"]), 0)
            self.assertIn("label", releases_result["release-list"][0]["label-info-list"][0])

        except (KeyError, TypeError, ValueError):
            self.fail("unexpected response format from browse_releases()")


    def test_get_recordings(self):
        recording_mbid = 'bf028638-5789-46dc-8fcf-e9ac1ec8a61f'
        recordings_result = self.api.get_recordings(recording_mbid)

        self.assertIsInstance(recordings_result, dict)
        self.assertIn("recording-list", recordings_result)

        try:
            self.assertIsInstance(recordings_result["recording-list"], list)
            self.assertIsNot(len(recordings_result["recording-list"]), 0)
            self.assertIn("id", recordings_result["recording-list"][0])
            self.assertIn("title", recordings_result["recording-list"][0])
            self.assertIn("length", recordings_result["recording-list"][0])

        except (KeyError, TypeError, ValueError):
            self.fail("unexpected response format from browse_recordings()")



if __name__ == '__main__':
    unittest.main()

