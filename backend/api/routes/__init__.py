from fastapi import APIRouter

from backend.api.routes import artists, graph, health


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(artists.router)
api_router.include_router(graph.router)

__all__ = ["api_router"]
