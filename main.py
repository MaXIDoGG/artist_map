from graph import YandexMusicGraph
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

graph = YandexMusicGraph()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search_path/")
async def search_path(artist_1: str, artist_2: str):
    print(f"Artist 1: {artist_1}, Artist 2: {artist_2}")
    result = graph.search_collaborations(artist_1, artist_2)
    print(result)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000, log_level="info")
