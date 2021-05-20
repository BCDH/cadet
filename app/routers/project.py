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
    2.  template datasheet for your dataset.
    3.  lookups for lemma, pos and entities
    4. serialize your new spaCy language object
    5. a spaCy project file

    Returns:
        FileResponse: project zip file
    """
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    lookups_path = new_lang / lang_name / "lookups"
    for lookup in lookups_path.iterdir():
        key = lookup.stem[lookup.stem.find('_') + 1:]
        if 'lemma' in key:
            lemma_data = srsly.read_json(lookup)
            if isinstance(lemma_data, str):
                return RedirectResponse("/edit_lookup?type=lemma")

        if 'entity' in key:
            entity_data = srsly.read_json(lookup)
            if isinstance(entity_data, str):
                return RedirectResponse("/edit_lookup?type=entity")
        if 'pos' in key:
            pos_data = srsly.read_json(lookup)
            if isinstance(pos_data, str):
                return RedirectResponse("/edit_lookup?type=pos")
    
    #if valid, continue
    texts = get_texts()
    filenames = get_filenames()
    nlp = get_nlp()
    if texts and nlp: 
        docs = [doc for doc in list(nlp.pipe(texts))]
        
        # let each Doc remember the file it came from
        for doc, filename in zip(docs,filenames):
            doc.user_data['filename'] =  filename

        docs = update_tokens_with_lookups(nlp, docs)
        conll = [doc_to_conll(doc) for doc in docs]

        temp_path = Path('/tmp/project_export')
        temp_path.mkdir(parents=True, exist_ok=True)
        for filename, conll in zip(filenames,conll):
            conll_filename = filename.split('.')[0] +'.conll'
            (temp_path / conll_filename).write_text(conll)

        #shutil.make_archive("zipped_sample_directory", "zip", "sample_directory")
        shutil.make_archive(str(temp_path), 'zip', str(temp_path))
        zip_file = str(temp_path).split('/')[-1]+'.zip'
        #save each doc to a file, return single zip file with all CONFIRM, can import directory into INCEpTION

        return FileResponse(f'/tmp/project_export.zip', media_type="application/zip", filename=lang_name + '_'+ zip_file)

def get_filenames() -> List[str]:
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        texts_path = list(new_lang.iterdir())[0] / "texts"
        if not texts_path.exists():
            return None
        filenames = [text.name for text in texts_path.iterdir()]
        return filenames

def get_texts() -> List[str]:
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        texts_path = list(new_lang.iterdir())[0] / "texts"
        if not texts_path.exists():
            return None
        texts = [text.read_text() for text in texts_path.iterdir()]
        return texts

def get_nlp():
    # Load language object as nlp
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    try:
        mod = __import__(f"new_lang.{lang_name}", fromlist=[lang_name.capitalize()])
    except SyntaxError:  # Unable to load __init__ due to syntax error
        # redirect /edit?file_name=examples.py
        message = "[*] SyntaxError, please correct this file to proceed."
        return RedirectResponse(url="/edit?file_name=tokenizer_exceptions.py")
    cls = getattr(mod, lang_name.capitalize())
    nlp = cls()
    return nlp
