from time import sleep, time
import requests
import psycopg2
from psycopg2.extras import execute_values
import musicbrainzngs
import json
from collections import namedtuple
from typing import Dict, List, Any, NamedTuple, Union, Tuple, TypeVar

# Configuration (use environment variables for production)
DB_NAME = "songsdb"
DB_USER = "user12345user"
DB_PASS = "12345pass12345word12345"
DB_HOST = "db-service"
DB_PORT = 5432
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@postgres/{DB_NAME}"
API_URL = "https://api.example.com/data"


APP_DIR = '/app'


T = TypeVar("T")
def flatten_list_of_lists(matrix: List[List[T]]) -> List[T]:
    flat_list = []
    for row in matrix:
        flat_list += row
    return flat_list

release_T = NamedTuple("release_T", [("mbid", str), ("id", int)])


class populate_db_task:
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

    api_request_counter: int
    api_requests_start_time: float
    api_requests_end_time: float


    def count_api_request(self):
        sleep(0.05) # https://wiki.musicbrainz.org/MusicBrainz_API/Rate_Limiting
        self.api_request_counter += 1
    def start_api_usage_stopwatch(self):
        self.api_requests_start_time = time()
    def stop_api_usage_stopwatch(self):
        api_usage_duration = time() - self.api_requests_start_time
        print(f"MusicBrainz API requests: {self.api_request_counter} in {api_usage_duration:.2f} seconds")

    def create_tables_ifnotexists(self):
        for schema_file in ["artists_schema.sql", "releases_schema.sql", "songs_schema.sql"]:
            with open(f"{APP_DIR}/schema/{schema_file}", "r") as f:
                SQL_QUERY = f.read()
                print("EXECUTING QUERY: <<")
                print(SQL_QUERY)
                print(">>")
                print(self.cur.execute(SQL_QUERY))
        self.conn.commit()
        for table in ["artists", "releases", "songs"]:
            print(f"DESCRIBING {table}:")
            print(self.cur.execute(f"Select column_name from information_schema.columns where table_name = '{table}'"))
        sleep(1)


    def connect_to_db(self):
        self.conn = psycopg2.connect(
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT
        )
        self.cur = self.conn.cursor()

        self.create_tables_ifnotexists()

        self.set_useragent("test kuk app", "0.1", "KukusterMOP@gmail.com")

    def disconnect_from_db(self):
        self.cur.close()
        self.conn.close()

    def set_useragent(self, app_name, app_version, app_contact):
        musicbrainzngs.set_useragent(app_name, app_version, app_contact)
        self.api_request_counter = 0

    def __init__(self, DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT):
        self.DB_NAME = DB_NAME
        self.DB_USER = DB_USER
        self.DB_PASS = DB_PASS
        self.DB_HOST = DB_HOST
        self.DB_PORT = DB_PORT
        self.connect_to_db()


    def fetch_artist(self, artist_name: str) -> Union[None, Tuple[int, str]]:
        self.count_api_request()
        artist_search_result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        try:
            mbid: str = artist_search_result["artist-list"][0]["id"]
            name: str = artist_search_result["artist-list"][0]["name"]
            id_: Union[None,int] = self.save_artist_to_database(mbid, name)
            if id_ is None:
                return None
            print(f"Found artist \"{name}\" with mbid '{mbid}'")
            return id_, mbid
        except (IndexError, KeyError):
            print(f"Artist '{artist_name}' not found in MusicBrainz")
            return None

    def fetch_releases(self, artist_id: int, artist_mbid: str) -> List[release_T]:
        self.count_api_request()
        # releases_search_result = musicbrainzngs.browse_releases(artist=artist_mbid, release_type=["album", "ep", "single"])
        release_groups_result = musicbrainzngs.browse_release_groups(artist=artist_mbid)

        selected_releases: List[release_T] = []

        # from each release group, get the first release that is either a US edition, or sold in the US
        # if there's no such release, ignore the entire release group
        for release_group in release_groups_result["release-group-list"]:
            try:
                rg_id: str = release_group["id"]
                rg_title: str = release_group["title"]
                rg_type: str = release_group["type"]
                rg_date: str = release_group["first-release-date"]

                print(f"Release_group: {rg_date} - '{rg_title}' ({rg_type}) [{rg_id=}]")

                # browse_releases provides more data than get_release_group_by_id
                self.count_api_request()
                rg_releases = musicbrainzngs.browse_releases(release_group=rg_id, release_type=["album", "ep", "single"], includes=["labels"])
                releases = rg_releases["release-list"]

                print(f"has {len(releases)} releases. Looping ...")
            except (KeyError, TypeError):
                continue

            release_id: Union[None, int] = None # if no release is found, this will remain None
            release_mbid: Union[None, str] = None

            for release in releases:
                release_mbid = str(release['id'])

                try:
                    is_US_edition = release["country"] == "US"
                except (KeyError, TypeError):
                    continue

                def was_sold_in_US():
                    try:
                        get_area_codes = lambda ev: ev["area"]["iso-3166-1-code-list"]
                        all_area_codes: List[str] = flatten_list_of_lists(map(get_area_codes, release["release-event-list"])) # type:ignore
                    except (KeyError, TypeError):
                        return False
                    return "US" in all_area_codes

                def get_catalognum() -> Union[str, None]:
                    try:
                        for label in release['label-info-list']:
                            if 'catalog-number' in label:
                                return label['catalog-number']
                    except (KeyError, TypeError):
                        return None
                    return None

                def get_barcode() -> Union[str, None]:
                    try:
                        return release['barcode']
                    except (KeyError, TypeError):
                        return None

                if is_US_edition or was_sold_in_US():
                    catalog_number = get_catalognum()
                    barcode = get_barcode()
                    if catalog_number and barcode:
                        print(f"Found suitable release: catalog: {catalog_number}, barcode: {barcode}, mbid: {release_mbid}")
                        release_id = self.save_release_to_database(release_mbid, rg_title, rg_type, rg_date, catalog_number, barcode, artist_id) # type: ignore
                        break


            if release_id is not None:
                assert release_mbid is not None
                selected_releases.append(release_T(release_mbid, release_id))
                # return release_mbid, release_id, artist_id #type: Tuple[str, int, int]


        return selected_releases


    def fetch_songs(self, release_mbid: str, release_id: int, artist_id: int):
        self.count_api_request()
        recordings = musicbrainzngs.browse_recordings(release=release_mbid)
        try:
            recording_list = recordings["recording-list"]
        except (KeyError, TypeError):
            return
        if isinstance(recording_list, list):
            # then `recordings` is not a string
            print(f"Found {len(recording_list)} recordings in release '{release_mbid}'")
            for rec in recording_list:
                try:
                    rec_mbid: str = rec['id']
                    rec_title: str = rec['title']
                    rec_duration = int(rec['length'])
                except (KeyError, TypeError):
                    continue
                rec_duration_str = f"{rec_duration // 60000}:{rec_duration % 60000 // 1000}"
                self.save_song_to_database(rec_mbid, rec_title, rec_duration_str, release_id, artist_id)


    def save_song_to_database(self, mbid: str, song_title: str, duration_str: str, release_id: int, artist_id: int):
        execute_values(self.cur, "INSERT INTO songs (mbid, song_title, duration, release_id, artist_id) VALUES %s ON CONFLICT DO NOTHING RETURNING id ", [(mbid, song_title, duration_str, release_id, artist_id)])
        try:
            song_id: str = self.cur.fetchone()[0] #type:ignore
            return song_id
        except (TypeError, IndexError):
            return None

    def save_release_to_database(self, 
                                 mbid: str,
                                 release_title: str,
                                 release_type: str,
                                 release_date: str,
                                 catalog_number: str,
                                 barcode: str,
                                 artist_id: int
                                 ) -> Union[None,int]:
        execute_values(self.cur, "INSERT INTO releases (mbid, release_title, release_type, release_date, catalog_number, barcode, artist_id) VALUES %s ON CONFLICT DO NOTHING RETURNING id ", [(mbid, release_title, release_type, release_date, catalog_number, barcode, artist_id)])
        try:
            release_id: int = self.cur.fetchone()[0] #type:ignore
            return release_id
        except (TypeError, IndexError):
            return None

    def save_artist_to_database(self, mbid: str, artist_name: str) -> Union[None,int]:
        execute_values(self.cur, "INSERT INTO artists (mbid, artist_name) VALUES %s ON CONFLICT DO NOTHING RETURNING id ", [(mbid, artist_name,)])
        try:
            artist_id: int = self.cur.fetchone()[0] #type:ignore
            return artist_id
        except (TypeError, IndexError):
            return None

    def get_song_from_db_by_name(self, song_title: str) -> int:
        self.cur.execute("SELECT * FROM songs WHERE song_title = %s", (song_title,))
        song_id: int = self.cur.fetchone() #type:ignore
        return song_id

def main():
    task = populate_db_task(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT)

    task.start_api_usage_stopwatch()
    band = 'Imagine Dragons'

    artist = task.fetch_artist(band)
    if artist is None:
        exit(1)
    artist_id, artist_mbid = artist

    releases = task.fetch_releases(artist_id, artist_mbid)
    for rel in releases:
        release_mbid, release_id = rel
        task.fetch_songs(release_mbid, release_id, artist_id)

    task.conn.commit()

    task.stop_api_usage_stopwatch()

    task.disconnect_from_db()

if __name__ == "__main__":
    main()
