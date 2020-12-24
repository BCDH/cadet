import httpx
from pathlib import Path
from typing import List, Optional
import spacy
from fastapi import APIRouter
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/create")
async def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@router.post("/create")
async def create_post(request: Request,
                      lang_name:str= Form(...), 
                      lang_code:str= Form(...), 
                      spacy_language: Optional[str]= Form(None)
                      ):
    if spacy_language:
        clone_object(lang_name,lang_code, spacy_language)
    else:
        create_object(lang_name,lang_code)
    message = f"Created a new object for {lang_name} with code {lang_code}"
    return templates.TemplateResponse("create.html", {"request": request, "message":message})

#Select2 endpoint
@router.get("/spacy_languages") #/spacy_languages?term=Russian&_type=query&q=Russian
async def language_options(_type:Optional[str]=None, term:Optional[str]=None, q:Optional[str]=None):
    response = {}
    response['results'] = []
    
    spacy_languages = httpx.get('https://raw.githubusercontent.com/explosion/spaCy/8cc5ed6771010322954c2211b0e1f5a0fd14828a/website/meta/languages.json').json()
    for lang in spacy_languages['languages']:
        if q:
            if q in lang['name']:
                response['results'].append({"id":lang['name'], "text": lang['name']})
        else:
            response['results'].append({"id":lang['name'], "text": lang['name']})
    
    return response
    