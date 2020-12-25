import httpx
from pathlib import Path
from typing import List, Optional
import spacy
from fastapi import APIRouter
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from app.util.create_util import create_object, clone_object
import json 
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

#Get list of currently support Language objects from spacy.lang
spacy_path = Path(spacy.__file__.replace('__init__.py',''))
spacy_lang = spacy_path / 'lang'
spacy_languages = json.dumps([i.stem for i in spacy_lang.iterdir() if len(i.stem) < 3])

@router.get("/create")
async def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request, "spacy_languages":spacy_languages})


@router.post("/create")
async def create_post(request: Request,
                      lang_name:str= Form(...), 
                      lang_code:str= Form(...), 
                      spacy_language: Optional[str]= Form(None),
                      direction:str = Form(...),
                      has_letters: bool = Form(False),
                      has_case: bool = Form(False)
                      ):
    if spacy_language:
        #clone_object(lang_name,lang_code, spacy_language)
        pass
       
    else:
        create_object(lang_name,lang_code,direction,has_case,has_letters)

        
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
    