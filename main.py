from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/fast_food", response_class=HTMLResponse)
async def fast_food(request: Request):
    return templates.TemplateResponse("fast_food.html", {"request": request})

@app.get("/home_food", response_class=HTMLResponse)
async def home_food(request: Request):
    return templates.TemplateResponse("home_food.html", {"request": request})

@app.get("/desi_food", response_class=HTMLResponse)
async def desi_food(request: Request):
    return templates.TemplateResponse("desi_food.html", {"request": request})
