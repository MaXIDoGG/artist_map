import requests
import json
import networkx as nx
import matplotlib.pyplot as plt

artist_query = input("Введите имя артиста или группы: ")

headers = {"User-Agent": "artist_map/1.0", "Accept": "*/*"}


def search_artist_req(artist_name, headers):
    res = requests.get(
        f"https://musicbrainz.org/ws/2/artist?query={artist_name}&limit=10&fmt=json",
        headers=headers,
    )

    return res.json()


data = search_artist_req(artist_query, headers)

searching_artists = data["artists"]
# print(json.dumps(searching_artists, indent=4))

i = 1
for artist in searching_artists:
    print(f"{i}. Имя: {artist.get('name')}, Страна: {artist.get('country')}")
    i += 1

choice_artist = int(input("Выберите номер артиста или группы: "))

artist_id = searching_artists[choice_artist - 1]["id"]
artist_name = searching_artists[choice_artist - 1]["name"]

res = requests.get(
    f"https://musicbrainz.org/ws/2/recording?artist={artist_id}&inc=artist-credits&limit=100&fmt=json",
    headers=headers,
)

first_artist = res.json()
artist_tracks = first_artist.get("recordings")

G = nx.Graph()

G.add_node(artist_name)

for track in artist_tracks:
    track_artists = track.get("artist-credit")
    if len(track_artists) < 2:
        continue
    for a in track_artists:
        another_artist = a.get("artist")
        if another_artist.get("id") == artist_id:
            continue

        G.add_node(another_artist.get("name"), artist_id=another_artist.get("id"))
        G.add_edge(
            artist_name,
            another_artist.get("name"),
            track_title=track.get("title"),
        )


# print(json.dumps(artist_tracks, indent=4))
nx.draw(G, with_labels=True, font_weight="bold")
plt.show()
