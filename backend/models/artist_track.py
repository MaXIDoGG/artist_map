from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class ArtistTrack(Base):
    __tablename__ = "artist_tracks"
    __table_args__ = (UniqueConstraint("artist_id", "track_id", name="uq_artist_tracks_artist_track"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id", ondelete="CASCADE"), index=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), index=True)

    artist: Mapped["Artist"] = relationship(back_populates="tracks")
    track: Mapped["Track"] = relationship(back_populates="artists")
