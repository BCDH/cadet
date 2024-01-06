import httpx
import json
import csv
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
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        return templates.TemplateResponse("lookups.html", {"request": request})

    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )


@router.post("/upload_lookups")
async def update_lookups(file: UploadFile = File(...), lookup_type: str = Form(...)):
    contents = file.file.read()
    contents = contents.decode("utf-8")

    # load lookups file
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0] / "lookups"
        if lookup_type == "pos":
            json_file = list(path.glob("*upos*"))[0]
        if lookup_type == "lemma":
            json_file = list(path.glob("*lemma*"))[0]
        if lookup_type == "features":
            json_file = list(path.glob("*features*"))[0]
        if json_file.exists():
            lookup = srsly.read_json(json_file)

    # load CSV file
    if file.content_type == "text/csv":
        reader = csv.reader(contents.splitlines())
        for row in reader:
            if row[0] == "key" and row[1] == "value":
                pass
            else:
                lookup[row[0]] = row[1]
        srsly.write_json(json_file, lookup)

    if file.content_type == "application/json":
        data = srsly.json_loads(contents)
        join_dicts = {**lookup, **data}
        srsly.write_json(json_file, join_dicts)


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
        if type == "features":
            json_file = list(path.glob("*features*"))[0]
        if json_file.exists():
            code = json_file.read_text()
            code = srsly.json_loads(code)
            context["code"] = str(code).replace("'", '"')

        else:
            raise HTTPException(status_code=404, detail="File not found")
    return templates.TemplateResponse("edit_json.html", context)


# when code is not valid json, saves to file, but does not load


@router.post("/edit_lookup")
async def update_code(
    request: Request,
):
    data = await request.json()
    type = data["type"]
    code = data["code"]

    # need something here to validate the json, return error and
    # help if not, but never save to disk if not valid (causes so much yuck)
    new_lang = Path.cwd() / "new_lang"

    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0] / "lookups"
        if type == "pos":
            json_file = list(path.glob("*upos*"))[0]
        if type == "lemma":
            json_file = list(path.glob("*lemma*"))[0]
        if type == "features":
            json_file = list(path.glob("*features*"))[0]

        if json_file.exists():
            try:  # assert that code is valid json
                assert json.loads(code)
                json_file.write_text(code)
                return {"message": "200"}
            except Exception as e:
                return {"message": str(e)}

        else:
            raise HTTPException(status_code=404, detail="File not found")

    return templates.TemplateResponse(
        "edit_json.html", {"request": request, "code": code}
    )
