import importlib.util # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
import json
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")
from app.util.login import get_current_username

router = APIRouter(
    dependencies=[Depends(get_current_username)]
)

@router.get("/sentences")
async def create(request: Request):
    new_lang = (Path.cwd() / 'new_lang')
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / 'examples.py'
        print(path)
        spec = importlib.util.spec_from_file_location("sentences", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sentences = module.sentences
        return templates.TemplateResponse("sentences.html", {"request": request, "sentences": sentences })
    else:
        return templates.TemplateResponse("error_please_create.html", {"request": request })

    
@router.post("/update_sentences")
async def update_sentences(request: Request, sentences:str = Form(...)):
    sentences = json.loads(sentences)
    new_lang = (Path.cwd() / 'new_lang')
    if new_lang.exists():
        if len(list(new_lang.iterdir())) > 0:
            name = list(new_lang.iterdir())[0].name
            examples_file = (Path.cwd() / 'new_lang' / name / 'examples.py')
            examples = examples_file.read_text()
            start = examples.find('sentences = [') + 13
            end = examples.find(']')
            sents = ""
            for sentence in sentences:
                sents += '"'+sentence+'",'
            examples_file.write_text(examples[:start] + sents + examples[end:])
            return sentences 