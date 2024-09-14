import requests
import json

artist_query = input("Введите имя артиста или группы: ")

headers = {"User-Agent": "artist_map/1.0", "Accept": "*/*"}

res = requests.get(
    f"https://musicbrainz.org/ws/2/artist?query={artist_query}&limit=10&fmt=json",
    headers=headers,
)

data = res.json()
# print(json.dumps(data, indent=4))

searching_artists = data["artists"]
# print(json.dumps(searching_artists, indent=4))

i = 1
for artist in searching_artists:
    print(f"{i}. Имя: {artist.get('name')}, Страна: {artist.get('country')}")
    i += 1

choice_artist = int(input("Выберите номер артиста или группы: "))

artist_id = searching_artists[choice_artist - 1]["id"]

res = requests.get(
    f"https://musicbrainz.org/ws/2/recording?artist={artist_id}&inc=artist-credits&limit=100&fmt=json",
    headers=headers,
)

artist_tracks = res.json().get("recordings")
print(json.dumps(artist_tracks, indent=4))
