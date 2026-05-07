from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas import GraphResponse, PathResponse
from backend.services.exceptions import ArtistNotFoundError, EmptyGraphError, PathNotFoundError
from backend.services.graph_service import GraphService


router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/path", response_model=PathResponse)
def get_path(
    source_id: Annotated[int, Query(gt=0)],
    target_id: Annotated[int, Query(gt=0)],
    db: Session = Depends(get_db),
) -> PathResponse:
    try:
        return GraphService(db).shortest_path(source_id, target_id)
    except ArtistNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (EmptyGraphError, PathNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/subgraph", response_model=GraphResponse)
def get_subgraph(
    artist_id: Annotated[int, Query(gt=0)],
    depth: Annotated[int, Query(ge=0, le=3)] = 1,
    db: Session = Depends(get_db),
) -> GraphResponse:
    try:
        return GraphService(db).subgraph(artist_id, depth=depth)
    except ArtistNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
