from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Artist Map"
    environment: Literal["local", "test", "production"] = "local"
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://artist_map:artist_map@localhost:5433/artist_map",
        validation_alias="DATABASE_URL",
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        validation_alias="CORS_ORIGINS",
    )

    yandex_music_token: str | None = Field(default=None, validation_alias="YANDEX_MUSIC_TOKEN")
    import_max_depth: int = Field(default=2, validation_alias="IMPORT_MAX_DEPTH")
    import_track_page_size: int = Field(default=100, validation_alias="IMPORT_TRACK_PAGE_SIZE")
    graph_cache_seconds: int = Field(default=300, validation_alias="GRAPH_CACHE_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
