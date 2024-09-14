from yandex_music import Client, search, Artist
import networkx as nx
import matplotlib.pyplot as plt

client = Client("token").init()

G = nx.Graph()

search_result = client.search("Pyrokinesis")

first_artist = search_result.artists.results[0]
first_artist_name = first_artist.name
artists = [first_artist_name]


def add_tracks_to_graph(last_artist: Artist):
    for track in last_artist.getTracks(page_size=150).tracks:
        # print(track.title)
        # print(track.artists_name())
        artists_names = track.artists_name()
        if len(artists_names) < 2:
            continue
        for artist in artists_names:
            if artist not in artists:
                G.add_node(artist)
                G.add_edge(last_artist.name, artist)
                artists.append(artist)

    track.artists
