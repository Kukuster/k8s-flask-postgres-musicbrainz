from Levenshtein import distance

from Songs import Song

def song_title_distance(song: Song, query: str) -> float:
    title: str = song.song_title.lower()
    longer_len = max(len(title), len(query))

    return distance(title, query) / longer_len

def song_title_distance_is_under_threshold(song: Song, query: str) -> bool:
    # query is allowed to be different by 15% of the length of the longer string, plus 1 character
    additive_threshold = 1
    proportional_threshold = 0.15

    title: str = song.song_title.lower()
    longer_len = max(len(title), len(query))

    return song_title_distance(song, query) < (proportional_threshold + additive_threshold/longer_len)

