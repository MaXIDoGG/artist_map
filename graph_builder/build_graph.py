import argparse
from pathlib import Path

import networkx as nx
from sqlalchemy.orm import Session
from yandex_music.artist.artist import Artist

from backend.db.session import SessionLocal
from backend.importers import import_from_yandex_music, seed_graphml
from graph_builder.ym_client import YMClient

MAX_DEPTH = 2

def build_graph(start_artist : str):
    if start_artist is None or start_artist == '':
        return None

    client = YMClient()
    G = nx.Graph()

    start: Artist | None = client.search_artist(start_artist)
    if start is None:
        return None

    visited = {start.name:0}
    queue = [(start,0)]

    while queue:
        artist, depth = queue.pop(0)
        if depth >= MAX_DEPTH:
            continue

        tracks = client.get_artist_tracks(artist)
        for track in tracks:
            artists = track.artists

            for a in artists:
                G.add_node(a.name)

                if a.name != artist.name:
                    G.add_edge(artist.name, a.name)

                if a.name not in visited:
                    visited[a.name] = depth+1
                    queue.append((a, depth+1))

    return G


def seed_database_from_graphml(db: Session, graphml_path: Path, clear: bool = False) -> dict[str, int]:
    return seed_graphml(db, graphml_path=graphml_path, clear=clear)


def import_database_from_yandex(db: Session, start_artist: str, max_depth: int = MAX_DEPTH) -> dict[str, int]:
    return import_from_yandex_music(db, start_artist_name=start_artist, max_depth=max_depth)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build or import the artist collaboration graph.")
    parser.add_argument("--artist", default="Oxxxymiron", help="Start artist for Yandex Music import.")
    parser.add_argument("--depth", type=int, default=MAX_DEPTH, help="Yandex Music traversal depth.")
    parser.add_argument("--graphml", type=Path, help="Seed Postgres from an existing GraphML file.")
    parser.add_argument("--clear", action="store_true", help="Clear database tables before GraphML seed.")
    parser.add_argument("--export-graphml", type=Path, help="Export a fresh GraphML graph instead of writing to DB.")
    args = parser.parse_args()

    if args.export_graphml:
        G = build_graph(args.artist)
        if G is not None:
            nx.write_graphml(G, args.export_graphml)
            print("Graph built:", G.number_of_nodes())
    else:
        with SessionLocal() as db:
            if args.graphml:
                result = seed_database_from_graphml(db, args.graphml, clear=args.clear)
            else:
                result = import_database_from_yandex(db, args.artist, max_depth=args.depth)
            print("Import result:", result)