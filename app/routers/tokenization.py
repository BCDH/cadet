from pathlib import Path
from fastapi import APIRouter
from fastapi import Request, Form, Depends
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")
from app.util.login import get_current_username

router = APIRouter()


@router.get("/tokenization")
async def tokenization(request: Request, login = Depends(get_current_username)):
    print(login)
    return templates.TemplateResponse("tokenization.html", {"request": request, })
