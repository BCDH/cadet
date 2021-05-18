import srsly
from pathlib import Path
from typing import List, Optional, Set
from fastapi import Request, Form, File, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from collections import Counter, namedtuple
from itertools import chain
from functools import lru_cache
import importlib

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/project")
async def project(request:Request):
    
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        return templates.TemplateResponse("project.html", {"request": request})
    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )

@router.post("/project")
async def form_post(
    request: Request,
    git_url: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
):
    if git_url:
        pass
    else:
        pass
    print(git_url, username, password)
    message = f"Successfully uploaded files. <a href='{git_url}'>Click here to proceed to GitHub.</a>"
    return templates.TemplateResponse("project.html", {"request": request, "message":message})