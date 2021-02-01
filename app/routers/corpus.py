import srsly
from pathlib import Path
from typing import List, Optional
from fastapi import Request, Form, File, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    dependencies=[Depends(get_current_username)]
)

@router.get("/corpus")
async def read_items(request: Request):
    new_lang = (Path.cwd() / 'new_lang')
    if len(list(new_lang.iterdir())) > 0:
        text_path = list(new_lang.iterdir())[0] / 'texts'
        corpus = ''
        for text in text_path.iterdir():
            corpus += text.read_text()
        print(corpus)
        stats = {'texts':0, "tokens":0}
    return templates.TemplateResponse("corpus.html", {"request": request})
