import networkx as nx
from ym_client import YMClient
from yandex_music.artist.artist import Artist

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


if __name__ == "__main__":
    G = build_graph("Oxxxymiron")
    if G is not None:
        nx.write_graphml(G, "../data/graph.graphml")
        print("Graph built:", G.number_of_nodes())