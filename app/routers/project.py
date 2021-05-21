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


@router.get("/download_project")
async def download_project():
    """Package all files noted in the template. 
    1. original text files.
    2.  lookups for lemma, pos and entities
    3. serialize your new spaCy language object
    4. a spaCy project file

    Returns:
        FileResponse: project zip file
    """
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    
    # 1 Texts
    texts_path = list(new_lang.iterdir())[0] / "texts"
    texts = [text for text in texts_path.iterdir()]
    
    # 2 lookups 
    lookups_path = new_lang / lang_name / "lookups"
    lookups = [l for l in lookups_path.iterdir()]
            
    # 3 NLP object
    nlp = get_nlp()
    #TODO serialize to_disk() or save folder? does to_disk save examples, exceptions?

    # 4 project.yml

    temp_path = Path('/tmp/project_export')
    temp_path.mkdir(parents=True, exist_ok=True)
    
    # TODO copy files to temp_path


    #shutil.make_archive("zipped_sample_directory", "zip", "sample_directory")
    shutil.make_archive(str(temp_path), 'zip', str(temp_path))
    zip_file = str(temp_path).split('/')[-1]+'.zip'
    #save each doc to a file, return single zip file with all CONFIRM, can import directory into INCEpTION

    return FileResponse(f'/tmp/project_export.zip', media_type="application/zip", filename=lang_name + '_'+ zip_file)


def get_nlp():
    # Load language object as nlp
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    mod = __import__(f"new_lang.{lang_name}", fromlist=[lang_name.capitalize()])
    cls = getattr(mod, lang_name.capitalize())
    nlp = cls()
    return nlp
    
        
    
