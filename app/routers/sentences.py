import importlib.util  # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
import json
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from fastapi import Request, Form
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
from app.util.login import get_current_username

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/sentences")
async def create(request: Request):
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / "examples.py"
        spec = importlib.util.spec_from_file_location("sentences", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sentences = module.sentences
        
        #ltr or rtl
        nlp = get_nlp()
        writing_system = nlp.vocab.writing_system['direction']

        return templates.TemplateResponse(
            "sentences.html", {"request": request, "sentences": sentences, "writing_system":writing_system}
        )
    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )


@router.post("/update_sentences")
async def update_sentences(request: Request, sentences: str = Form(...)):
    sentences = json.loads(sentences)
    new_lang = Path.cwd() / "new_lang"
    if new_lang.exists():
        if len(list(new_lang.iterdir())) > 0:
            name = list(new_lang.iterdir())[0].name
            examples_file = Path.cwd() / "new_lang" / name / "examples.py"
            examples = examples_file.read_text()
            start = examples.find("sentences = [") + 13
            end = examples.find("]")
            sents = ""
            for sentence in sentences:
                sentence = sentence.replace('&amp;nbsp','').replace('&nbsp;','').replace('\n','') #bug from the template
                sents += '"""' + sentence + '""",'
            examples_file.write_text(examples[:start] + sents + examples[end:])
            return sentences

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
