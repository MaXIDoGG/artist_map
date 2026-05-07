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
        return artist.getTracks(page_size=100).tracks