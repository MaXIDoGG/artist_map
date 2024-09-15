from yandex_music import Client, Artist
import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import deque

client = Client().init()

G = nx.Graph()

first_artist_name = input("Введите первого артиста: ").strip()
last_artist_name = input("Введите второго артиста: ").strip()

first_search_result = client.search(first_artist_name)
last_search_result = client.search(last_artist_name)

first_artist = first_search_result.artists.results[0]
last_artist = last_search_result.artists.results[0]

# Используем множество для посетившихся артистов
visited_artists = {first_artist.name}

# Используем deque для очереди (быстрее чем список)
queue = deque([first_artist])

# Лимит на количество артистов и глубину поиска
max_artists = 1200
max_depth = 7
depth = {first_artist.name: 0}

# Флаг для остановки поиска
flag = False


def clean_name(name: str) -> str:
    """Очистка имени артиста от символов, вызывающих ошибки"""
    return re.sub(r"[$]", "", name)


# Основной цикл поиска
while queue and len(visited_artists) < max_artists and not flag:
    current_artist = queue.popleft()
    current_artist_name = clean_name(current_artist.name)

    # Если глубина поиска превышает максимальное значение, выходим
    if depth[current_artist_name] >= max_depth:
        continue

    # Получаем треки текущего артиста
    for track in current_artist.getTracks(page_size=70).tracks:
        if flag:
            break

        # Получаем имена артистов
        artists = track.artists
        if len(artists) < 2:
            continue

        for artist in artists:
            artist_name = clean_name(artist.name)

            if artist_name not in visited_artists:
                visited_artists.add(artist_name)
                queue.append(artist)
                G.add_node(artist_name)

                # Обновляем глубину поиска для нового артиста
                depth[artist_name] = depth[current_artist_name] + 1

            # Добавляем ребро между текущим и новым артистом
            if artist_name != current_artist_name:
                G.add_edge(current_artist_name, artist_name)

            # Если нашли целевого артиста, выводим кратчайший путь
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
