from sqlalchemy import CheckConstraint, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class ArtistEdge(Base):
    __tablename__ = "artist_edges"
    __table_args__ = (
        UniqueConstraint("source_artist_id", "target_artist_id", name="uq_artist_edges_pair"),
        CheckConstraint("source_artist_id <> target_artist_id", name="no_self_edge"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        index=True,
    )
    target_artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        index=True,
    )
    weight: Mapped[int] = mapped_column(default=1)
    track_examples: Mapped[list[str]] = mapped_column(JSON, default=list)

    source_artist: Mapped["Artist"] = relationship(
        back_populates="outgoing_edges",
        foreign_keys=[source_artist_id],
    )
    target_artist: Mapped["Artist"] = relationship(
        back_populates="incoming_edges",
        foreign_keys=[target_artist_id],
    )
