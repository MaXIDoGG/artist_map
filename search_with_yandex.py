from yandex_music import Client, search, Artist
import networkx as nx
import matplotlib.pyplot as plt

client = Client("token").init()

G = nx.Graph()

search_result = client.search("Earl Dany-Grey")

first_artist = search_result.artists.results[0]
first_artist_name = first_artist.name
visited_artists = [first_artist_name]

# TODO: Реализовать цикл по очереди (FIFO)
queue = [first_artist]


def add_tracks_to_graph(last_artist: Artist):
    for track in last_artist.getTracks(page_size=200).tracks:
        # print(track.title)
        # print(track.artists_name())
        # TODO: Переделать имена артистов на сущности артистов для удобного поиска в следующих итерациях
        artists_names = track.artists_name()
        if len(artists_names) < 2:
            continue
        for artist in artists_names:
            if artist not in visited_artists:
                G.add_node(artist)
                G.add_edge(last_artist.name, artist)
                visited_artists.append(artist)


add_tracks_to_graph(last_artist=first_artist)
nx.draw(G, with_labels=True, font_weight="bold")
plt.show()
