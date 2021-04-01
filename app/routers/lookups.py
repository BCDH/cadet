import httpx
import json
import textract
import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import Request, Form, File, UploadFile, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/lookups")
async def read_items(request: Request):
    return templates.TemplateResponse("lookups.html", {"request": request})


@router.get("/edit_lookup")
async def edit_pos(request: Request, type: str):
    context = {}
    context["request"] = request
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0] / "lookups"
        if type == "pos":
            json_file = list(path.glob("*upos*"))[0]
        if type == "lemma":
            json_file = list(path.glob("*lemma*"))[0]
        if type == "entity":
            json_file = list(path.glob("*entity*"))[0]
        if json_file.exists():
            context["code"] = srsly.read_json(json_file)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    return templates.TemplateResponse("edit_json.html", context)


@router.post("/edit_lookup")
async def update_code(request: Request,):

    data = await request.json()
    type = data["type"]
    code = data["code"]
   
    
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0] / "lookups"
        if type == "pos":
            json_file = list(path.glob("*upos*"))[0]
        if type == "lemma":
            json_file = list(path.glob("*lemma*"))[0]
        if type == "entity":
            json_file = list(path.glob("*entity*"))[0]
        if json_file.exists():
            try:
                code = srsly.json_loads(code)
            except Exception as e:
                return {'message': str(e) }
                
            srsly.write_json(json_file, code)
        #TODO This section needs some work 
        # Need to check that json is valid before save on click of "Save and Back to Lookups" button   
        # Get errors when Check  on JSON is clicked, or get thumbs up 
        else:
            raise HTTPException(status_code=404, detail="File not found")
    return templates.TemplateResponse(
        "edit_json.html", {"request": request, "code": code}
    )
