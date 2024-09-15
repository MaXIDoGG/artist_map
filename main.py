from yandex_music import Client, Artist
import networkx as nx
import matplotlib.pyplot as plt
import re

client = Client().init()

G = nx.Graph()

first_artist_name = input("Введите первого артиста: ").strip()
last_artist_name = input("Введите второго артиста: ").strip()

first_search_result = client.search(first_artist_name)
last_search_result = client.search(last_artist_name)

first_artist = first_search_result.artists.results[0]
last_artist = last_search_result.artists.results[0]
visited_artists = [first_artist.name]

# Очередь для обхода артистов
queue = [first_artist]

# Флаг для остановки поиска
flag = False

# Лимит на количество артистов
max_artists = 1000


def clean_name(name: str) -> str:
    """Очистка имени артиста от символов, вызывающих ошибки"""
    return re.sub(r"[$]", "", name)


# Основной цикл поиска
while queue and len(visited_artists) < max_artists and not flag:
    current_artist = queue.pop(0)
    current_artist_name = clean_name(current_artist.name)

    for track in current_artist.getTracks(page_size=200).tracks:
        if flag:
            break

        # Получаем имена артистов
        artists = track.artists
        if len(artists) < 2:
            continue

        for artist in artists:
            artist_name = clean_name(artist.name)
            if artist_name not in visited_artists:
                G.add_node(artist_name)
                visited_artists.append(artist_name)
                queue.append(artist)

            if artist_name != current_artist_name:
                G.add_edge(current_artist_name, artist_name)

            if artist_name == last_artist.name:
                print(
                    "Кратчайший путь:",
                    nx.shortest_path(G, first_artist.name, last_artist.name),
                )
                flag = True
                break

# Отрисовка графа
nx.draw(G, with_labels=True, font_weight="bold")
plt.show()
