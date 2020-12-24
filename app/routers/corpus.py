import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/corpus")
async def read_items(request: Request):
    return templates.TemplateResponse("corpus.html", {"request": request})
