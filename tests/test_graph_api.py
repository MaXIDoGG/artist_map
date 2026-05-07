from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from graph_builder.graph_storage import GraphStorage


def seed_sample_graph(db: Session) -> tuple[int, int, int]:
    storage = GraphStorage(db)
    first = storage.upsert_artist("First Artist")
    middle = storage.upsert_artist("Middle Artist")
    last = storage.upsert_artist("Last Artist")
    storage.upsert_edge(first, middle, "Track One")
    storage.upsert_edge(middle, last, "Track Two")
    db.commit()
    return first.id, middle.id, last.id


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_artists(client: TestClient, db_session: Session) -> None:
    seed_sample_graph(db_session)

    response = client.get("/api/v1/artists/search", params={"q": "middle"})

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Middle Artist"


def test_shortest_path(client: TestClient, db_session: Session) -> None:
    first_id, _, last_id = seed_sample_graph(db_session)

    response = client.get(
        "/api/v1/graph/path",
        params={"source_id": first_id, "target_id": last_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["degrees"] == 2
    assert [artist["name"] for artist in body["path"]] == ["First Artist", "Middle Artist", "Last Artist"]


def test_featured_graph(client: TestClient, db_session: Session) -> None:
    seed_sample_graph(db_session)

    response = client.get("/api/v1/graph/featured", params={"depth": 2, "limit": 10, "seed_count": 1})

    assert response.status_code == 200
    body = response.json()
    assert len(body["nodes"]) == 3
    assert len(body["links"]) == 2


def test_missing_artist_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/graph/path", params={"source_id": 1, "target_id": 2})

    assert response.status_code == 404
