from pathlib import Path

import networkx as nx
from sqlalchemy.orm import Session

from graph_builder.graph_storage import GraphStorage


def seed_graphml(db: Session, graphml_path: Path, clear: bool = False) -> dict[str, int]:
    storage = GraphStorage(db)
    if clear:
        storage.clear()

    graph = nx.read_graphml(graphml_path)
    artists_by_name = {
        str(node): storage.upsert_artist(name=str(node), meta={"source": "graphml"})
        for node in graph.nodes
    }

    edge_count = 0
    for source, target, edge_data in graph.edges(data=True):
        source_artist = artists_by_name[str(source)]
        target_artist = artists_by_name[str(target)]
        track_title = edge_data.get("track") or edge_data.get("title") or edge_data.get("track_title")
        if storage.upsert_edge(source_artist, target_artist, track_title=track_title) is not None:
            edge_count += 1

    db.commit()
    return {"artists": len(artists_by_name), "edges": edge_count}
