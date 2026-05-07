from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from backend.models import Artist, ArtistEdge


class GraphRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_artists(self) -> list[Artist]:
        return list(self.db.scalars(select(Artist)))

    def list_edges(self) -> list[ArtistEdge]:
        stmt = select(ArtistEdge).options(
            joinedload(ArtistEdge.source_artist),
            joinedload(ArtistEdge.target_artist),
        )
        return list(self.db.scalars(stmt))

    def get_edges_for_artists(self, artist_ids: set[int]) -> list[ArtistEdge]:
        if not artist_ids:
            return []

        stmt = (
            select(ArtistEdge)
            .options(joinedload(ArtistEdge.source_artist), joinedload(ArtistEdge.target_artist))
            .where(
                ArtistEdge.source_artist_id.in_(artist_ids),
                ArtistEdge.target_artist_id.in_(artist_ids),
            )
        )
        return list(self.db.scalars(stmt))

    def get_neighbor_edges(self, artist_ids: set[int]) -> list[ArtistEdge]:
        if not artist_ids:
            return []

        stmt = (
            select(ArtistEdge)
            .options(joinedload(ArtistEdge.source_artist), joinedload(ArtistEdge.target_artist))
            .where(
                or_(
                    ArtistEdge.source_artist_id.in_(artist_ids),
                    ArtistEdge.target_artist_id.in_(artist_ids),
                )
            )
        )
        return list(self.db.scalars(stmt))
