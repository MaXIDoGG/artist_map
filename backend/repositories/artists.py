from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from backend.models import Artist


def normalize_artist_name(name: str) -> str:
    return " ".join(name.casefold().strip().split())


class ArtistRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, artist_id: int) -> Artist | None:
        return self.db.get(Artist, artist_id)

    def search(self, query: str, limit: int = 10) -> list[Artist]:
        normalized_query = normalize_artist_name(query)
        if not normalized_query:
            return []

        stmt: Select[tuple[Artist]] = (
            select(Artist)
            .where(Artist.normalized_name.ilike(f"%{normalized_query}%"))
            .order_by(func.length(Artist.name), Artist.name)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def get_or_create_by_name(self, name: str, ym_id: str | None = None, meta: dict | None = None) -> Artist:
        normalized_name = normalize_artist_name(name)
        stmt = select(Artist).where(Artist.normalized_name == normalized_name)
        artist = self.db.scalar(stmt)
        if artist is not None:
            if ym_id and artist.ym_id is None:
                artist.ym_id = ym_id
            return artist

        artist = Artist(
            name=name.strip(),
            normalized_name=normalized_name,
            ym_id=ym_id,
            meta=meta or {},
        )
        self.db.add(artist)
        self.db.flush()
        return artist
