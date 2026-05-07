from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas import ArtistRead
from backend.services.artist_service import ArtistService


router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("/search", response_model=list[ArtistRead])
def search_artists(
    q: Annotated[str, Query(min_length=1, max_length=120)],
    limit: Annotated[int, Query(ge=1, le=25)] = 10,
    db: Session = Depends(get_db),
) -> list[ArtistRead]:
    return ArtistService(db).search(q, limit=limit)
