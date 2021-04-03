import httpx
import json
import textract
import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import Request, Form, File, UploadFile, APIRouter, Depends, Query
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

@router.get("/lemma_json")
async def datatable_json(request:Request,
    #See https://datatables.net/manual/server-side
    draw:int = None,
    start:int = None,
    length:int = None, #number of entries per page):
    order:int = None,
    columns:str = None
    ):
    search = request.query_params['search[value]']
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0] / "lookups"
        json_file = list(path.glob("*lemma*"))[0]
        lemma_data = srsly.read_json(json_file)

        data = []
        for key, value in lemma_data.items():
            data.append([key,value])
        if search != '':
            data = [d for d in data if search.lower() in d[0].lower() or search.lower() in d[1].lower()]
        data = [[f'<p onclick="edit_word(this)">{key}</p>',f'<p onclick="edit_lemma(this)">{value}</p>'] for key, value in data]
        filtered = len(data)
        return {
            "draw": draw,
            "recordsTotal": len(lemma_data),
            "recordsFiltered": filtered,
            "data":data,
            "result":"ok",
            "error":None
        }