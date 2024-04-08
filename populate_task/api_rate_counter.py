from time import sleep, time

class ApiRateCounter:
    api_request_counter: int
    api_requests_start_time: float
    api_requests_end_time: float

    def __init__(self):
        self.api_request_counter = 0

    def count(self):
        sleep(0.05) # https://wiki.musicbrainz.org/MusicBrainz_API/Rate_Limiting
        self.api_request_counter += 1

    def start(self):
        self.api_requests_start_time = time()

    def stop(self):
        api_usage_duration = time() - self.api_requests_start_time
        print(f"MusicBrainz API requests: {self.api_request_counter} in {api_usage_duration:.2f} seconds")

