from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    ym_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    tracks: Mapped[list["ArtistTrack"]] = relationship(
        back_populates="artist",
        cascade="all, delete-orphan",
    )
    outgoing_edges: Mapped[list["ArtistEdge"]] = relationship(
        back_populates="source_artist",
        cascade="all, delete-orphan",
        foreign_keys="ArtistEdge.source_artist_id",
    )
    incoming_edges: Mapped[list["ArtistEdge"]] = relationship(
        back_populates="target_artist",
        cascade="all, delete-orphan",
        foreign_keys="ArtistEdge.target_artist_id",
    )
