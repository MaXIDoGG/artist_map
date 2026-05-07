import networkx as nx
from sqlalchemy.orm import Session

from backend.models import Artist, ArtistEdge
from backend.repositories import ArtistRepository, GraphRepository
from backend.schemas import GraphLink, GraphNode, GraphResponse, PathResponse
from backend.services.exceptions import ArtistNotFoundError, EmptyGraphError, PathNotFoundError


class GraphService:
    def __init__(self, db: Session):
        self.db = db
        self.artists = ArtistRepository(db)
        self.graph = GraphRepository(db)

    def shortest_path(self, source_id: int, target_id: int) -> PathResponse:
        source = self.artists.get(source_id)
        target = self.artists.get(target_id)
        if source is None or target is None:
            raise ArtistNotFoundError("Один из артистов не найден")

        graph = self._build_networkx_graph()
        if graph.number_of_edges() == 0:
            raise EmptyGraphError("Граф артистов пуст")

        try:
            path_ids = nx.shortest_path(graph, source_id, target_id)
        except (nx.NodeNotFound, nx.NetworkXNoPath) as exc:
            raise PathNotFoundError("Связь между артистами не найдена") from exc

        path_artists = self._get_artists_by_ids(path_ids)
        edges = self.graph.get_edges_for_artists(set(path_ids))

        return PathResponse(
            path=path_artists,
            degrees=max(len(path_ids) - 1, 0),
            nodes=[GraphNode(id=artist.id, label=artist.name) for artist in path_artists],
            links=[self._edge_to_link(edge) for edge in edges],
        )

    def subgraph(self, artist_id: int, depth: int = 1) -> GraphResponse:
        artist = self.artists.get(artist_id)
        if artist is None:
            raise ArtistNotFoundError("Артист не найден")
        if depth < 0 or depth > 3:
            raise ValueError("depth должен быть от 0 до 3")

        graph = self._build_networkx_graph()
        if artist_id not in graph:
            return GraphResponse(nodes=[GraphNode(id=artist.id, label=artist.name)], links=[])

        node_ids = {
            node_id
            for node_id, distance in nx.single_source_shortest_path_length(
                graph,
                artist_id,
                cutoff=depth,
            ).items()
            if distance <= depth
        }
        artists = self._get_artists_by_ids(node_ids)
        edges = self.graph.get_edges_for_artists(node_ids)

        return GraphResponse(
            nodes=[GraphNode(id=item.id, label=item.name) for item in artists],
            links=[self._edge_to_link(edge) for edge in edges],
        )

    def featured(self, depth: int = 2, limit: int = 80, seed_count: int = 6) -> GraphResponse:
        if depth < 1 or depth > 2:
            raise ValueError("depth должен быть от 1 до 2")
        if limit < 10 or limit > 150:
            raise ValueError("limit должен быть от 10 до 150")

        edges = self.graph.list_edges()
        if not edges:
            raise EmptyGraphError("Граф артистов пуст")

        graph = self._build_networkx_graph()
        degree_by_artist: dict[int, int] = {}
        for edge in edges:
            degree_by_artist[edge.source_artist_id] = degree_by_artist.get(edge.source_artist_id, 0) + edge.weight
            degree_by_artist[edge.target_artist_id] = degree_by_artist.get(edge.target_artist_id, 0) + edge.weight

        seeds = [
            artist_id
            for artist_id, _degree in sorted(
                degree_by_artist.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:seed_count]
        ]

        node_ids: set[int] = set(seeds)
        frontier = set(seeds)
        for _ in range(depth):
            next_frontier: set[int] = set()
            for artist_id in frontier:
                next_frontier.update(graph.neighbors(artist_id))
            for artist_id in sorted(
                next_frontier - node_ids,
                key=lambda item: degree_by_artist.get(item, 0),
                reverse=True,
            ):
                if len(node_ids) >= limit:
                    break
                node_ids.add(artist_id)
            frontier = next_frontier & node_ids
            if len(node_ids) >= limit:
                break

        artists = self._get_artists_by_ids(node_ids)
        edges = self.graph.get_edges_for_artists(node_ids)

        return GraphResponse(
            nodes=[GraphNode(id=item.id, label=item.name) for item in artists],
            links=[self._edge_to_link(edge) for edge in edges],
        )

    def _build_networkx_graph(self) -> nx.Graph:
        graph = nx.Graph()
        for artist in self.graph.list_artists():
            graph.add_node(artist.id)
        for edge in self.graph.list_edges():
            graph.add_edge(edge.source_artist_id, edge.target_artist_id, weight=edge.weight)
        return graph

    def _get_artists_by_ids(self, artist_ids: list[int] | set[int]) -> list[Artist]:
        artists_by_id = {artist.id: artist for artist in self.graph.list_artists()}
        return [artists_by_id[artist_id] for artist_id in artist_ids if artist_id in artists_by_id]

    @staticmethod
    def _edge_to_link(edge: ArtistEdge) -> GraphLink:
        return GraphLink(
            source=edge.source_artist_id,
            target=edge.target_artist_id,
            weight=edge.weight,
            track_examples=edge.track_examples or [],
        )
