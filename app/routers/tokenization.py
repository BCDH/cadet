import spacy
from pathlib import Path
from fastapi import APIRouter
from fastapi import Request, Form, Depends
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")
from app.util.login import get_current_username
import importlib.util # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

router = APIRouter()


@router.get("/tokenization")
async def tokenization(request: Request, login = Depends(get_current_username)):
    new_lang = (Path.cwd() / 'new_lang')
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / 'examples.py'
        spec = importlib.util.spec_from_file_location("sentences", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sentences = module.sentences

        # Load language object as nlp
        lang_name = list(new_lang.iterdir())[0].name
        mod = __import__(f'new_lang.{lang_name}', fromlist=[lang_name.capitalize()])
        cls = getattr(mod, lang_name.capitalize())
        nlp = cls()

        spacy_sentences = []
        for sentence in sentences:
            sent = ''
            doc = nlp(sentence)
            for token in doc:
                sent += f"<span class='token'>{token}</span>&nbsp;"
            spacy_sentences.append(sent)
    return templates.TemplateResponse("tokenization.html", {"request": request, "sentences":spacy_sentences })
