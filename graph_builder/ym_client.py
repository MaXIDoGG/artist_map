from yandex_music import Client
from yandex_music.search.search import Search
from yandex_music.artist.artist import Artist

from backend.core.config import get_settings


class YMClient:

    def __init__(self):
        settings = get_settings()
        self.client = Client(settings.yandex_music_token).init()

    def search_artist(self, name) -> Artist | None:
        res: Search | None = self.client.search(name)
        if res is not None and res.artists is not None and res.artists.results:
            return res.artists.results[0]
        else:
            return None

    def get_artist_tracks(self, artist):
        page_size = get_settings().import_track_page_size
        page = 0
        tracks = []
        while True:
            batch = artist.getTracks(page=page, page_size=page_size)
            if batch is None or not batch.tracks:
                break
            tracks.extend(batch.tracks)
            if len(batch.tracks) < page_size:
                break
            page += 1
        return tracks