import httpx
import json 
import spacy
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.util.create_object import create_object
from app.util.clone_object import clone_object
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

#Get list of currently support Language objects from spacy.lang
spacy_path = Path(spacy.__file__.replace('__init__.py',''))
spacy_lang = spacy_path / 'lang'
spacy_languages = json.dumps([i.stem for i in spacy_lang.iterdir() if len(i.stem) < 3])

@router.get("/create")
async def create(request: Request):
    # Check if a new language exists already, give option to delete if so
    new_lang = (Path.cwd() / 'new_lang')
    if new_lang.exists():
        if len(list(new_lang.iterdir())) > 0:
            name = list(new_lang.iterdir())[0].name
            message = f"<div class='alert alert-warning' role='alert'>Found an existing object for {name}. If you'd like to delete {name} and start over click delete. To continue to edit {name}, click next.</div><a href='/delete_new_lang/{name}' class='read-more'><i style='color:white;'class='icofont-trash'></i> Delete {name}</a><div></div><br><a href='/sentences' class='read-more'>Next<i style='color:white;'class='icofont-long-arrow-right'></i></a>"
            return templates.TemplateResponse("create.html", {"request": request, "spacy_languages":spacy_languages, "message":message})
        else:
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
        lang_name, lang_code = clone_object(lang_name,lang_code, spacy_language)
       
    else:
        lang_name, lang_code = create_object(lang_name,lang_code,direction,has_case,has_letters)

        
    message = f"<div class='alert alert-success' role='alert'>Created a new object for {lang_name} with code {lang_code}<br>To use type <span style='background:white;'>from new_lang.{lang_name} import {lang_name.capitalize()}</span></div><a href='/sentences' class='read-more'>Next<i style='color:white;'class='icofont-long-arrow-right'></i></a>"
    return templates.TemplateResponse("create.html", {"request": request, "message":message})

@router.get("/delete_new_lang/{name}") 
async def delete(name):
    new_lang = (Path.cwd() / 'new_lang' / name)
    shutil.rmtree(new_lang)
    return RedirectResponse(url='/create')


#Select2 endpoint
@router.get("/spacy_languages") #/spacy_languages?term=Russian&_type=query&q=Russian
async def language_options(_type:Optional[str]=None, term:Optional[str]=None, q:Optional[str]=None):
    response = {}
    response['results'] = []
    
    #TODO automatically load most recent languages.json from explosion
    spacy_languages = httpx.get('https://raw.githubusercontent.com/explosion/spaCy/8cc5ed6771010322954c2211b0e1f5a0fd14828a/website/meta/languages.json').json()
    for lang in spacy_languages['languages']:
        if q:
            if q in lang['name']:
                response['results'].append({"id":lang['name'], "text": lang['name']})
        else:
            response['results'].append({"id":lang['name'], "text": lang['name']})
    
    return response
    