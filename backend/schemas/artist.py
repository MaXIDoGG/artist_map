from pydantic import BaseModel, ConfigDict


class ArtistRead(BaseModel):
    id: int
    ym_id: str | None
    name: str

    model_config = ConfigDict(from_attributes=True)
