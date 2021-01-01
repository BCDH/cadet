import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/edit")
async def read_items(request: Request, file_name:str, username: str = Depends(get_current_username)):
    code = f'hi there! {file_name}'
    new_lang = (Path.cwd() / 'new_lang')
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / file_name
        if path.exists():
            code = path.read_text()
        else:
            code = 'Error, please enter a valid filename'
    return templates.TemplateResponse("edit_code.html", {"request": request, "code":code})

@router.post("/edit")
async def read_items(request: Request, file_name:str, username: str = Depends(get_current_username)):
    code = f'hi there! {file_name}'
    new_lang = (Path.cwd() / 'new_lang')
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / file_name
        if path.exists():
            code = path.read_text()
        else:
            code = 'Error, please enter a valid filename'
    return templates.TemplateResponse("edit_code.html", {"request": request, "code":code})
