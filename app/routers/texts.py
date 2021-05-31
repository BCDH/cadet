import httpx
import spacy
import srsly
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import Request, BackgroundTasks, Form, File, UploadFile, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from ..util.manage_corpus import make_corpus

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])

def add_newlines(text:str):
    """
    Use spaCy's default sentencizer to split docs into sents 
    """
    nlp = spacy.load("xx_ent_wiki_sm")
    nlp.add_pipe('sentencizer')
    doc = nlp(text)
    output = """"""
    for sent in doc.sents:
        output += sent.text + '\n'
    return output

@router.get("/texts")
async def read_items(request: Request):

    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        texts_path = list(new_lang.iterdir())[0] / "texts"
        if not texts_path.exists():
            texts_path.mkdir(parents=True, exist_ok=True)
        texts = [text.name for text in texts_path.iterdir()]
        return templates.TemplateResponse(
            "texts.html", {"request": request, "texts": texts}
        )
    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )



@router.post("/texts")
async def save_texts(
    request: Request,
    background_tasks: BackgroundTasks,
    newlines:str = Form(None),
    text_url: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    text_area: Optional[str] = Form(None),
    
):
    if newlines == 'newline':
        newlines = True
    else: 
        newlines = False 

    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        save_path = list(new_lang.iterdir())[0] / "texts"
        if not save_path.exists():
            save_path.mkdir(parents=True, exist_ok=True)

    # get highest current text id
    def current_id():
        if len(list(save_path.iterdir())) > 0:
            id = max([int((i.stem).split("_")[0]) for i in save_path.iterdir()])
        else:
            id = 0
        return id

    if text_url:
        text = httpx.get(text_url).text
        if newlines:
            text = add_newlines(text)
        filename= text_url.split('/')[-1]
        file_save_path = save_path / filename
        file_save_path.write_text(text)
        # data = [{"text": line} for line in text.split("\n")]
        # file_save_path = str((save_path / f"{current_id()+1}_text.jsonl"))
        # srsly.write_jsonl(file_save_path, data)

    if files:
        for file in files:
            if file.filename:
                contents = await file.read()
                if newlines:
                    contents = add_newlines(contents.decode("utf-8"))
                file_save_path = save_path / file.filename #UploadFile object 
                file_save_path.write_text(contents.decode("utf-8"))
            
    if text_area:
        if newlines:
            text_area = add_newlines(text_area)
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        file_save_path = (save_path / f"{dt_string}-textarea.txt")
        file_save_path.write_text(text_area)
        

    message = "Text added successfully"
    background_tasks.add_task(make_corpus)
    return templates.TemplateResponse(
        "texts.html", {"request": request, "message": message}
    )

@router.get('/delete_text')
async def get_tokenized_texts(text_name:str):

    #Get the path to the file and delete it
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        texts_path = list(new_lang.iterdir())[0] / "texts"
    selected_file = texts_path / text_name
    if selected_file.exists():
        make_corpus()
        selected_file.unlink()
        return {'message': f"deleted {selected_file.name}" }


