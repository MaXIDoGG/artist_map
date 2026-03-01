from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from backend.services.graph_service import GraphService

app = FastAPI()
graph_service = GraphService()

app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/path")
def get_path(a1: str, a2: str):
    return graph_service.shortest_path(a1, a2)

@app.get("/graph")
def get_full_graph():
    return graph_service.get_full_graph()