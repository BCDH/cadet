import spacy
from pathlib import Path
from fastapi import APIRouter
from fastapi import Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

templates = Jinja2Templates(directory="app/templates")
from app.util.login import get_current_username
import importlib.util  # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

router = APIRouter()


@router.get("/tokenization")
async def tokenization(request: Request, login=Depends(get_current_username)):
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / "examples.py"
        spec = importlib.util.spec_from_file_location("sentences", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sentences = module.sentences

        # Load language object as nlp
        lang_name = list(new_lang.iterdir())[0].name
        try:
            mod = __import__(f"new_lang.{lang_name}", fromlist=[lang_name.capitalize()])
        except SyntaxError:  # Unable to load __init__ due to syntax error
            # redirect /edit?file_name=examples.py
            message = "[*] SyntaxError, please correct this file to proceed."
            return RedirectResponse(url="/edit?file_name=tokenizer_exceptions.py")
        cls = getattr(mod, lang_name.capitalize())
        nlp = cls()
        spacy_sentences = []
        for sentence in sentences:
            sent = ""
            doc = nlp(sentence)
            for token in doc:
                sent += f"<span style='margin:5px;' onmouseup='edit_span();' onclick='edit_me(this)' value='{token}' class='token'>{token}</span>&nbsp;"
            spacy_sentences.append(sent)
        return templates.TemplateResponse(
            "tokenization.html", {"request": request, "sentences": spacy_sentences}
        )
    else:
        return templates.TemplateResponse("tokenization.html", {"request": request})


@router.post("/add_tokenization_exception")
async def add_tokenization_exception(
    token1: str = Form(None),
    token2: str = Form(None),
):
    print(token1, token2)
    new_lang = Path.cwd() / "new_lang"
    new_lang_dir = list(new_lang.iterdir())[0]
    exceptions_file = new_lang_dir / "tokenizer_exceptions.py"
    if exceptions_file.exists():
        script = exceptions_file.read_text()
        cursor = script.find("exclusions = [") + 14
        
        if token2: #is split
            addition = f"{{'{token1+token2}':[{{ORTH: '{token1}'}},{{ORTH: '{token2}'}}]}},\n"
        else: # is join
            addition = f"{{'{token1}':[{{ORTH: '{token1}'}}]}},\n"
        new_script = script[:cursor] + addition + script[cursor:]
        exceptions_file.write_text(new_script)
        return RedirectResponse(url="/tokenization", status_code=HTTP_302_FOUND)

    else:
        raise HTTPException(status_code=404, detail="File not found")


# prefix, suffix and infix is a tuple of lists
# the lists contain regular expressions or characters
# many default lists exist and can be imported from lang.char_classes
# there are also default lists in lang.punctuation BASE_TOKENIZER_PREFIXES...
# create object uses BASE defaults, may need to drop them?
# Users will need to import, add and remove elements from these lists


@router.post("/add_tokenization_prefix")
async def add_tokenization_prefix(
    request: Request,
    login=Depends(get_current_username),
    orth: str = Form(None),
    norm: str = Form(None),
    caps_variation: bool = Form(
        None
    ),  # Generate variations of the term with caps, no caps
    exception_type: str = Form(None),  # abbreviation, slang,
):
    pass


@router.post("/add_tokenization_suffix")
async def add_tokenization_suffix(
    request: Request,
    login=Depends(get_current_username),
    char_class: str = Form(None),
    norm: str = Form(None),
    caps_variation: bool = Form(
        None
    ),  # Generate variations of the term with caps, no caps
    exception_type: str = Form(None),  # abbreviation, slang,
):
    pass


@router.post("/add_tokenization_infix")
async def add_tokenization_infix(
    request: Request,
    login=Depends(get_current_username),
    char_class: str = Form(None),
    norm: str = Form(None),
    caps_variation: bool = Form(
        None
    ),  # Generate variations of the term with caps, no caps
    exception_type: str = Form(None),  # abbreviation, slang,
):
    pass


@router.get("/char_class_types")
async def char_class_types():
    char_class_types = "variables listed in spacy.lang.char_classes"
    return char_class_types
