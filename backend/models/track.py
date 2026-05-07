from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    ym_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    artists: Mapped[list["ArtistTrack"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
    )
