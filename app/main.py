from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import create, texts, corpus, tokenization, sentences, edit_code, lookups
from app.util.login import get_current_username
#from app.auth.routes import router as auth_router
from pathlib import Path


app_dir = Path.cwd()
templates = Jinja2Templates(directory="app/templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

app.include_router(create.router)

app.include_router(texts.router)
app.include_router(corpus.router)
app.include_router(tokenization.router)
app.include_router(sentences.router)
app.include_router(edit_code.router)
app.include_router(lookups.router)

#app.include_router(auth_router, prefix="/auth")


new_lang = (Path.cwd() / 'new_lang')
if not new_lang.exists(): # Directory does not exist the first time the app is used
    new_lang.mkdir(parents=True, exist_ok=True)

@app.get("/")
def root(request: Request,):

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/main")
def main(request: Request, username: str = Depends(get_current_username)):
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/logout")
async def route_logout(request: Request):
    #TODO figure out logout
    return templates.TemplateResponse("login.html", {"request": request})
