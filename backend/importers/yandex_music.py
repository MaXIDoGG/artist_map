from collections import deque

from sqlalchemy.orm import Session

from backend.core.config import get_settings
from graph_builder.graph_storage import GraphStorage
from graph_builder.ym_client import YMClient


def import_from_yandex_music(db: Session, start_artist_name: str, max_depth: int | None = None) -> dict[str, int]:
    settings = get_settings()
    max_depth = settings.import_max_depth if max_depth is None else max_depth
    client = YMClient()
    storage = GraphStorage(db)

    start = client.search_artist(start_artist_name)
    if start is None:
        return {"artists": 0, "tracks": 0, "edges": 0}

    visited: set[str] = set()
    queue = deque([(start, 0)])
    imported_tracks = 0

    while queue:
        artist, depth = queue.popleft()
        artist_id = str(getattr(artist, "id", artist.name))
        if artist_id in visited or depth > max_depth:
            continue
        visited.add(artist_id)

        current_artist = storage.upsert_artist(
            name=artist.name,
            ym_id=str(getattr(artist, "id", "")) or None,
            meta={"source": "yandex_music"},
        )
        if depth >= max_depth:
            continue

        for track in client.get_artist_tracks(artist):
            track_artists = []
            for track_artist in track.artists:
                saved_artist = storage.upsert_artist(
                    name=track_artist.name,
                    ym_id=str(getattr(track_artist, "id", "")) or None,
                    meta={"source": "yandex_music"},
                )
                track_artists.append(saved_artist)
                next_artist_id = str(getattr(track_artist, "id", track_artist.name))
                if next_artist_id not in visited:
                    queue.append((track_artist, depth + 1))

            if current_artist not in track_artists:
                track_artists.append(current_artist)

            storage.save_collaboration_track(
                title=track.title,
                artists=track_artists,
                ym_id=str(getattr(track, "id", "")) or None,
            )
            imported_tracks += 1

    db.commit()
    return {"artists": len(visited), "tracks": imported_tracks, "edges": 0}
