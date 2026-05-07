from sqlalchemy.orm import Session

from backend.models import Artist
from backend.repositories import ArtistRepository


class ArtistService:
    def __init__(self, db: Session):
        self.repository = ArtistRepository(db)

    def search(self, query: str, limit: int = 10) -> list[Artist]:
        return self.repository.search(query, limit=limit)
