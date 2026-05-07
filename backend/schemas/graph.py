from pydantic import BaseModel, Field

from backend.schemas.artist import ArtistRead


class GraphNode(BaseModel):
    id: int
    label: str


class GraphLink(BaseModel):
    source: int
    target: int
    weight: int = 1
    track_examples: list[str] = Field(default_factory=list)


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


class PathResponse(GraphResponse):
    path: list[ArtistRead]
    degrees: int


class MessageResponse(BaseModel):
    detail: str
