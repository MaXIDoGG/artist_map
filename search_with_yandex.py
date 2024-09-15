from yandex_music import Client, search, Artist
import networkx as nx
import matplotlib.pyplot as plt

client = Client().init()

G = nx.Graph()

first_artist_name = input("Введите первого артиста: ").strip()
last_artist_name = input("Введите второго артиста: ").strip()

first_search_result = client.search(first_artist_name)
last_search_result = client.search(last_artist_name)

first_artist = first_search_result.artists.results[0]
last_artist = last_search_result.artists.results[0]
visited_artists = [first_artist.name]

# TODO: Реализовать цикл по очереди (FIFO)
queue = [first_artist]


# def add_tracks_to_graph(G:nx.graph, queue: list, max_n: int = 1000, desired_artist_name: str):
flag = False
while queue and len(visited_artists) < 1000 and not flag:
    current_artist = queue.pop(0)
    for track in current_artist.getTracks(page_size=200).tracks:
        if flag:
            break
        # print(track.title)
        # print(track.artists_name())
        artists = track.artists
        if len(artists) < 2:
            continue
        for artist in artists:
            if artist.name not in visited_artists:
                G.add_node(artist.name)
                visited_artists.append(artist.name)
                queue.append(artist)
            if artist.name != current_artist.name:
                G.add_edge(current_artist.name, artist.name)
            if artist.name == last_artist.name:
                print(nx.shortest_path(G, first_artist.name, last_artist.name))
                flag = True
                break


# add_tracks_to_graph(G=G, queue=queue, desired_artist_name=last_artist.name)
nx.draw(G, with_labels=True, font_weight="bold")
plt.show()
