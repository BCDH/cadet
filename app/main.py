from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import create, texts, corpus

from pathlib import Path

app_dir = Path.cwd()
templates = Jinja2Templates(directory="app/templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static"), name="static")
app.include_router(create.router)

app.include_router(texts.router)
app.include_router(corpus.router)

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "cadet")
    correct_password = secrets.compare_digest(credentials.password, "NewNLP")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# app.include_router(home.router)
# app.include_router(weather_app.router)

# routers
# load/connect to corpus, get seeds for annotation, create initial ling data
# create language object
# create config.cfg and train
# project.yml
# create model
# load texts and data
#

# 1 Create basic language object
# 2 Create basic model with pipelines
# 3 Create custom model with transformers, pytorch models, and so on


@app.get("/")
def root(request: Request,):

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/main")
def main(request: Request, username: str = Depends(get_current_username)):
    return templates.TemplateResponse("main_page.html", {"request": request})
