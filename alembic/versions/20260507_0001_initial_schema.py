"""initial schema

Revision ID: 20260507_0001
Revises:
Create Date: 2026-05-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260507_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "artists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ym_id", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artists")),
    )
    op.create_index(op.f("ix_artists_name"), "artists", ["name"], unique=False)
    op.create_index(op.f("ix_artists_normalized_name"), "artists", ["normalized_name"], unique=False)
    op.create_index(op.f("ix_artists_ym_id"), "artists", ["ym_id"], unique=True)

    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ym_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tracks")),
    )
    op.create_index(op.f("ix_tracks_title"), "tracks", ["title"], unique=False)
    op.create_index(op.f("ix_tracks_ym_id"), "tracks", ["ym_id"], unique=True)

    op.create_table(
        "artist_edges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_artist_id", sa.Integer(), nullable=False),
        sa.Column("target_artist_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("track_examples", sa.JSON(), nullable=False),
        sa.CheckConstraint("source_artist_id <> target_artist_id", name=op.f("ck_artist_edges_no_self_edge")),
        sa.ForeignKeyConstraint(
            ["source_artist_id"],
            ["artists.id"],
            name=op.f("fk_artist_edges_source_artist_id_artists"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_artist_id"],
            ["artists.id"],
            name=op.f("fk_artist_edges_target_artist_id_artists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artist_edges")),
        sa.UniqueConstraint("source_artist_id", "target_artist_id", name="uq_artist_edges_pair"),
    )
    op.create_index(op.f("ix_artist_edges_source_artist_id"), "artist_edges", ["source_artist_id"], unique=False)
    op.create_index(op.f("ix_artist_edges_target_artist_id"), "artist_edges", ["target_artist_id"], unique=False)

    op.create_table(
        "artist_tracks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("artist_id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            name=op.f("fk_artist_tracks_artist_id_artists"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["tracks.id"],
            name=op.f("fk_artist_tracks_track_id_tracks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artist_tracks")),
        sa.UniqueConstraint("artist_id", "track_id", name="uq_artist_tracks_artist_track"),
    )
    op.create_index(op.f("ix_artist_tracks_artist_id"), "artist_tracks", ["artist_id"], unique=False)
    op.create_index(op.f("ix_artist_tracks_track_id"), "artist_tracks", ["track_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_artist_tracks_track_id"), table_name="artist_tracks")
    op.drop_index(op.f("ix_artist_tracks_artist_id"), table_name="artist_tracks")
    op.drop_table("artist_tracks")
    op.drop_index(op.f("ix_artist_edges_target_artist_id"), table_name="artist_edges")
    op.drop_index(op.f("ix_artist_edges_source_artist_id"), table_name="artist_edges")
    op.drop_table("artist_edges")
    op.drop_index(op.f("ix_tracks_ym_id"), table_name="tracks")
    op.drop_index(op.f("ix_tracks_title"), table_name="tracks")
    op.drop_table("tracks")
    op.drop_index(op.f("ix_artists_ym_id"), table_name="artists")
    op.drop_index(op.f("ix_artists_normalized_name"), table_name="artists")
    op.drop_index(op.f("ix_artists_name"), table_name="artists")
    op.drop_table("artists")
