from itertools import combinations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Artist, ArtistEdge, ArtistTrack, Track
from backend.repositories import ArtistRepository


class GraphStorage:
    def __init__(self, db: Session):
        self.db = db
        self.artists = ArtistRepository(db)

    def clear(self) -> None:
        self.db.query(ArtistEdge).delete()
        self.db.query(ArtistTrack).delete()
        self.db.query(Track).delete()
        self.db.query(Artist).delete()
        self.db.flush()

    def upsert_artist(self, name: str, ym_id: str | None = None, meta: dict | None = None) -> Artist:
        return self.artists.get_or_create_by_name(name=name, ym_id=ym_id, meta=meta)

    def upsert_track(self, title: str, ym_id: str | None = None, meta: dict | None = None) -> Track:
        stmt = select(Track).where(Track.ym_id == ym_id) if ym_id else select(Track).where(Track.title == title)
        track = self.db.scalar(stmt)
        if track is not None:
            return track

        track = Track(title=title, ym_id=ym_id, meta=meta or {})
        self.db.add(track)
        self.db.flush()
        return track

    def attach_artist_to_track(self, artist: Artist, track: Track) -> None:
        stmt = select(ArtistTrack).where(
            ArtistTrack.artist_id == artist.id,
            ArtistTrack.track_id == track.id,
        )
        if self.db.scalar(stmt) is None:
            self.db.add(ArtistTrack(artist_id=artist.id, track_id=track.id))

    def upsert_edge(self, artist_a: Artist, artist_b: Artist, track_title: str | None = None) -> ArtistEdge | None:
        if artist_a.id == artist_b.id:
            return None

        source_id, target_id = sorted([artist_a.id, artist_b.id])
        stmt = select(ArtistEdge).where(
            ArtistEdge.source_artist_id == source_id,
            ArtistEdge.target_artist_id == target_id,
        )
        edge = self.db.scalar(stmt)
        if edge is None:
            edge = ArtistEdge(
                source_artist_id=source_id,
                target_artist_id=target_id,
                weight=0,
                track_examples=[],
            )
            self.db.add(edge)
            self.db.flush()

        edge.weight += 1
        if track_title and track_title not in edge.track_examples and len(edge.track_examples) < 5:
            edge.track_examples = [*edge.track_examples, track_title]
        return edge

    def save_collaboration_track(self, title: str, artists: list[Artist], ym_id: str | None = None) -> Track:
        track = self.upsert_track(title=title, ym_id=ym_id)
        for artist in artists:
            self.attach_artist_to_track(artist, track)
        for artist_a, artist_b in combinations(artists, 2):
            self.upsert_edge(artist_a, artist_b, track_title=title)
        self.db.flush()
        return track
