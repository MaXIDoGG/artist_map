from graph import YandexMusicGraph
from fastapi import FastAPI
import uvicorn
from urllib.parse import quote_plus

app = FastAPI()
graph = YandexMusicGraph()


@app.get("/")
async def home():
    return {"Hello": "World"}


@app.get("/search_path/")
async def search_path(artist_1: str, artist_2: str):
    return graph.search_collaborations(quote_plus(artist_1), quote_plus(artist_2))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000, log_level="info")
