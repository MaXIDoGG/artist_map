from yandex_music import Client, search, Artist
import networkx as nx
import matplotlib.pyplot as plt


class YandexMusicGraph:

    def __init__(self, graph_file_name: str = "graph.graphml"):
        self.g: nx.Graph = nx.read_graphml(graph_file_name)
        self.client = Client().init()

    def search_collaborations(self, artist_1, artist_2):
        return nx.shortest_path(self.g, artist_1, artist_2)


def create_graph(first_artist_name: str):
    """Создание графа из Я. Музыки"""
    G = nx.Graph()

    first_search_result = client.search(first_artist_name)
    first_artist = first_search_result.artists.results[0]
    visited_artists = {
        first_artist.name: 0
    }  # Используем словарь для контроля уровня вложенности

    # Максимальная глубина вложенности
    MAX_DEPTH = 3

    # Очередь содержит артиста и его уровень вложенности
    queue = [(first_artist, 0)]

    while queue:
        current_artist, depth = queue.pop(0)
        print(current_artist.name)

        # Если достигли максимальной глубины, не продолжаем
        if depth >= MAX_DEPTH:
            continue

        for track in current_artist.getTracks(page_size=50).tracks:
            artists = track.artists
            if len(artists) < 2:
                continue
            for artist in artists:
                if artist.name not in visited_artists:
                    G.add_node(artist.name)
                    visited_artists[artist.name] = depth + 1
                    queue.append(
                        (artist, depth + 1)
                    )  # Добавляем артиста с увеличенным уровнем вложенности
                if artist.name != current_artist.name:
                    G.add_edge(current_artist.name, artist.name)


# print(G.number_of_nodes())
# nx.write_graphml(G, "graph.graphml")

# nx.draw(G, with_labels=True, font_weight="bold")
# plt.show()
