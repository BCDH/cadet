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
    return templates.TemplateResponse("corpus.html", {"request": request})
