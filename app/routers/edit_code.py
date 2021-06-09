import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/edit")
async def edit_code(
    request: Request,
    file_name: str,
    content: Optional[str] = None,
    is_text: Optional[str] = None,
):
    context = {}
    if content:
        context["content"] = content
    context["request"] = request
    if is_text:
        new_lang = Path.cwd() / "new_lang"
        if len(list(new_lang.iterdir())) > 0:
            path = list(new_lang.iterdir())[0] / "texts" / file_name
            if path.exists():
                context["code"] = path.read_text()
            else:
                raise HTTPException(status_code=404, detail="File not found")
    else:
        new_lang = Path.cwd() / "new_lang"
        if len(list(new_lang.iterdir())) > 0:
            path = list(new_lang.iterdir())[0]
            path = path / file_name
            if path.exists():
                context["code"] = path.read_text()
            else:
                raise HTTPException(status_code=404, detail="File not found")
    return templates.TemplateResponse("edit_code.html", context)


@router.post("/edit")
async def update_code(request: Request,):

    data = await request.json()
    type = data["type"]
    code = data["code"]

    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / filename
        if path.exists():
            path.write_text(code)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    return templates.TemplateResponse(
        "edit_code.html", {"request": request, "code": code}
    )
