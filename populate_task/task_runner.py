import requests
import psycopg2
from psycopg2.extras import execute_values
import musicbrainzngs
import json
from typing import Dict, List, Any, Union, Tuple

# Configuration (use environment variables for production)
DB_NAME = "songsdb"
DB_USER = "user12345user"
DB_PASS = "12345pass12345word12345"
DB_HOST = "db-service"
DB_PORT = 5432
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@postgres/{DB_NAME}"
API_URL = "https://api.example.com/data"


APP_DIR = '/app'

#recording_search_result_type = Dict[str, Union[str, List[Dict[str, Any]]]]

class populate_db_task:
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

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

    def create_tables_ifnotexists(self):
        for schema_file in ["artists_schema.sql", "releases_schema.sql", "songs_schema.sql"]:
            with open(f"{APP_DIR}/schema/{schema_file}", "r") as f:
                self.cur.execute(f.read())
        self.conn.commit()

    def disconnect_from_db(self):
        self.cur.close()
        self.conn.close()

    def __init__(self, DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT):
        self.DB_NAME = DB_NAME
        self.DB_USER = DB_USER
        self.DB_PASS = DB_PASS
        self.DB_HOST = DB_HOST
        self.DB_PORT = DB_PORT
        self.connect_to_db()


    def fetch_data(self):
        # response = requests.get(API_URL)
        # data = response.json()
        # return data


        # Configure the musicbrainzngs client
        musicbrainzngs.set_useragent("ExampleApp", "0.1", "http://example.com")

        artist_name = "Imagine Dragons"
        song_name = "Demons"

        # # Search for Imagine Dragons artist ID
        # artist_search_result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        # print(f"{json.dumps(artist_search_result, indent=4)=}")

        # print("")

        recording_search_result = musicbrainzngs.search_recordings(artist=artist_name, recording=song_name, limit=1)
        return recording_search_result


    def process_data(self, recording_search_result):
        # Process data as needed; here, we're assuming it's already in the desired format

        artist_name = recording_search_result["recording-list"][0]["artist-credit"][0]['name']
        song_title = recording_search_result["recording-list"][0]["title"]
        release_title = recording_search_result["recording-list"][0]["release-list"][0]["title"]
        #id = recording_search_result["recording-list"][0]["id"]

        # float constructor has more reliable string parsing,
        #   while int constructor is predictable in taking integer part from float,
        #   and failing with ValueError when given float("NaN"), float("inf"), and float("-inf") 
        #   This way is recommended for converting string from APIs
        duration_ms = int(float(recording_search_result["recording-list"][0]["length"]))
        duration_str = f"{duration_ms // 60000}:{duration_ms % 60000 // 1000}"

        return song_title, artist_name, release_title, duration_str

    def save_entry_to_database(self, song_title, artist_name, release_title, duration_str):
        # # For demonstration purposes, we'll just print the data
        # print(processed_data)

        execute_values(self.cur, "INSERT INTO artists (artist_name) VALUES %s RETURNING id", [(artist_name,)])
        artist_id = self.cur.fetchone()[0] # type:ignore
        execute_values(self.cur, "INSERT INTO releases (release_title, artist_id) VALUES %s RETURNING id", [(release_title, artist_id)])
        release_id = self.cur.fetchone()[0] # type:ignore
        execute_values(self.cur, "INSERT INTO songs (song_title, duration, release_id, artist_id) VALUES %s RETURNING id", [(song_title, duration_str, release_id, artist_id)])
        song_id = self.cur.fetchone()[0] # type:ignore

        print("INSERTED: ", f"{artist_id=}", f"{artist_name=}", f"{release_id=}", f"{release_title=}", f"{song_id=}", f"{song_title=}", f"{duration_str=}")

        # conn = psycopg2.connect(DATABASE_URL)
        # cur = conn.cursor()
        # insert_query = "INSERT INTO records (data) VALUES %s"
        # execute_values(cur, insert_query, [(d,) for d in processed_data])
        # conn.commit()
        # cur.close()
        # conn.close()

    def get_song_from_db_by_name(self, song_title):
        self.cur.execute("SELECT * FROM songs WHERE song_title = %s", (song_title,))
        return self.cur.fetchone()

def main():
    # # Configure the musicbrainzngs client
    # musicbrainzngs.set_useragent("ExampleApp", "0.1", "http://example.com")

    # artist_name = "Imagine Dragons"
    # song_name = "Demons"

    # # Search for Imagine Dragons artist ID
    # artist_search_result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
    # print(f"{json.dumps(artist_search_result, indent=4)=}")

    # print("")

    # recording_search_result = musicbrainzngs.search_recordings(artist=artist_name, recording=song_name, limit=1)
    # print(f"{json.dumps(recording_search_result, indent=4)=}")

    task = populate_db_task(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT)

    data = task.fetch_data()
    song_title, artist_name, release_title, duration_str = task.process_data(data)
    task.save_entry_to_database(song_title, artist_name, release_title, duration_str)
    print("Data fetched and saved to database successfully.")
    print(f"{task.get_song_from_db_by_name(song_title)=}")
    print("hello world from postgres completed!")
    if song_title == "Demons":
        print("Task completed successfully!")


if __name__ == "__main__":
    main()
