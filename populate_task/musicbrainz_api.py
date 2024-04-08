from typing import List, TypedDict
from typing_extensions import NotRequired

import musicbrainzngs

from api_rate_counter import ApiRateCounter
from config import MB_USERAGENT_APP_NAME, MB_USERAGENT_APP_VERSION, MB_USERAGENT_APP_CONTACT



SearchArtistResult_artist = TypedDict("SearchArtistResult_artist", {
    "id": str,
    "name": str,
})
SearchArtistResult = TypedDict("SearchArtistResult", {
    "artist-list": List[SearchArtistResult_artist],
})


BrowseReleaseGroupsResult_rg = TypedDict("BrowseReleaseGroupsResult_rg", {
    "id": str,
    "title": str,
    "type": str,
    "first-release-date": str,
})
BrowseReleaseGroupsResult = TypedDict("BrowseReleaseGroupsResult", {
    "release-group-list": List[BrowseReleaseGroupsResult_rg],
})


BrowseReleasesResult_release_event_area = TypedDict("BrowseReleasesResult_release_event_area", {
    "iso-3166-1-code-list": List[str],
})
BrowseReleasesResult_release_event = TypedDict("BrowseReleasesResult_release_event", {
    "area": BrowseReleasesResult_release_event_area,
})
BrowseReleasesResult_release_labelinfo = TypedDict("BrowseReleasesResult_release_labelinfo", {
    "catalog-number": NotRequired[str],
})
BrowseReleasesResult_release = TypedDict("BrowseReleasesResult_release", {
    "id": str,
    "country": str,
    "release-event-list": List[BrowseReleasesResult_release_event],
    "label-info-list": List[BrowseReleasesResult_release_labelinfo],
    "barcode": NotRequired[str],
    "catalog-number": NotRequired[str],
})
BrowseReleasesResult = TypedDict("BrowseReleasesResult", {
    "release-list": List[BrowseReleasesResult_release],
})


BrowseRecordingsResult_recording = TypedDict("BrowseRecordingsResult_recording", {
    "id": str,
    "title": str,
    "length": int,
})
BrowseRecordingsResult = TypedDict("BrowseRecordingsResult", {
    "recording-list": List[BrowseRecordingsResult_recording],
})



class MusicBrainzAPI:

    api_requests: ApiRateCounter

    def __init__(self):
        musicbrainzngs.set_useragent(
            MB_USERAGENT_APP_NAME,
            MB_USERAGENT_APP_VERSION,
            MB_USERAGENT_APP_CONTACT,
        )
        self.api_requests = ApiRateCounter()

    def start(self):
        self.api_requests.start()

    def stop(self):
        self.api_requests.stop()

    def search_artist(self, artist_name: str) -> SearchArtistResult:
        self.api_requests.count()
        return musicbrainzngs.search_artists(artist=artist_name, limit=1) # type:ignore

    def get_release_groups(self, artist_mbid: str) -> BrowseReleaseGroupsResult:
        self.api_requests.count()
        return musicbrainzngs.browse_release_groups(artist=artist_mbid) # type:ignore

    def get_releases(self, release_group_mbid: str) -> BrowseReleasesResult:
        self.api_requests.count()
        # browse_releases provides more data about releases than get_release_group_by_id
        return musicbrainzngs.browse_releases(release_group=release_group_mbid, release_type=["album", "ep", "single"], includes=["labels"]) # type:ignore

    def get_recordings(self, release_mbid: str) -> BrowseRecordingsResult:
        self.api_requests.count()
        return musicbrainzngs.browse_recordings(release=release_mbid) #type:ignore
