from collections import deque
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.models import ArtistEdge
from graph_builder.graph_storage import GraphStorage
from graph_builder.ym_client import YMClient


def import_from_yandex_music(
    db: Session,
    start_artist_name: str | Sequence[str],
    max_depth: int | None = None,
    clear: bool = False,
) -> dict[str, int]:
    settings = get_settings()
    max_depth = settings.import_max_depth if max_depth is None else max_depth
    seed_names = [start_artist_name] if isinstance(start_artist_name, str) else list(start_artist_name)
    client = YMClient()
    storage = GraphStorage(db)
    if clear:
        storage.clear()

    queue: deque[tuple[object, int]] = deque()
    visited: set[str] = set()
    queued_depth: dict[str, int] = {}
    imported_tracks = 0
    processed = 0

    def enqueue(artist: object, depth: int) -> None:
        if depth > max_depth:
            return
        artist_key = str(getattr(artist, "id", artist.name))
        if artist_key in visited:
            return
        if artist_key in queued_depth and queued_depth[artist_key] <= depth:
            return
        queued_depth[artist_key] = depth
        queue.append((artist, depth))

    for name in seed_names:
        start = client.search_artist(name)
        if start is not None:
            enqueue(start, 0)

    if not queue:
        return {"artists": 0, "tracks": 0, "edges": 0}

    while queue:
        artist, depth = queue.popleft()
        artist_id = str(getattr(artist, "id", artist.name))
        if artist_id in visited or depth > max_depth:
            continue
        if depth > queued_depth.get(artist_id, depth):
            continue
        visited.add(artist_id)
        processed += 1
        if processed % 50 == 0:
            print(
                f"Processed {processed} artists, queue {len(queue)}, visited {len(visited)}",
                flush=True,
            )
            db.commit()

        current_artist = storage.upsert_artist(
            name=artist.name,
            ym_id=str(getattr(artist, "id", "")) or None,
            meta={"source": "yandex_music"},
        )
        if depth >= max_depth:
            continue

        for track in client.get_artist_tracks(artist):
            track_artists: dict[int, object] = {}
            for track_artist in track.artists:
                saved_artist = storage.upsert_artist(
                    name=track_artist.name,
                    ym_id=str(getattr(track_artist, "id", "")) or None,
                    meta={"source": "yandex_music"},
                )
                track_artists[saved_artist.id] = saved_artist
                enqueue(track_artist, depth + 1)

            track_artists[current_artist.id] = current_artist

            storage.save_collaboration_track(
                title=track.title,
                artists=list(track_artists.values()),
                ym_id=str(getattr(track, "id", "")) or None,
            )
            imported_tracks += 1

    db.commit()
    edge_count = db.scalar(select(func.count()).select_from(ArtistEdge)) or 0
    return {"artists": len(visited), "tracks": imported_tracks, "edges": edge_count}
