import httpx

import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import Request, Form, File, UploadFile, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


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
        return templates.TemplateResponse("texts.html", {"request": request})


@router.post("/texts")
async def save_texts(
    request: Request,
    text_url: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    text_area: Optional[str] = Form(None),
):

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
        file_save_path = save_path / f"{current_id()+1}.txt"
        file_save_path.write_text(text)
        # data = [{"text": line} for line in text.split("\n")]
        # file_save_path = str((save_path / f"{current_id()+1}_text.jsonl"))
        # srsly.write_jsonl(file_save_path, data)

    if files:
        for file in files:
            contents = await file.read()
            file_save_path = save_path / f"{current_id()+1}.txt"
            file_save_path.write_text(contents.decode("utf-8"))
        ### Textract for OCR, too complicated and messy, switching to just txt files
        # for file in files:
        #     # Write the UploadFile to disk, this is a trade-off required by textract
        #     p = Path("/tmp") / file.filename
        #     try:
        #         p.write_bytes(file.file.read())
        #         text = textract.process(str(p))
        #         text = text.decode("utf-8")
        #         #data = [{"text": line} for line in text.split("\n")]
        #         file_save_path = (save_path / f"{current_id()+1}.txt")
        #         file_save_path.write_text(text)
        #         #srsly.write_jsonl(file_save_path, data)
        #         p.unlink()

        #    except IsADirectoryError:
        #        pass  # No file selected
    if text_area:
        file_save_path = save_path / f"{current_id()+1}.txt"
        file_save_path.write_text(text_area)
        # data = [{"text": line} for line in text_area.split("\n")]
        # file_save_path = str((save_path / f"{current_id()+1}_text.jsonl"))
        # srsly.write_jsonl(file_save_path, data)

    message = "Text added successfully"
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
        selected_file.unlink()
        return {'message': f"deleted {selected_file.name}" }


@router.get("/texts/stats")
async def get_text_stats():
    pass


@router.get("/tokenized/texts")
async def get_tokenized_texts(request: Request):
    for file in file_save_path.iterdir():
        file_txt = ""
        print(file.name)
        # load lang object
        # tokenize text with obj
        # for token in tokens:
        # if len(token.whitespace_ == 0:
        #   MISC += SpaceAfter=No


# WebAnno TSV
# FORMAT=WebAnno TSV 3.2
# 1-2        4-8        Haag

# Line needs to have 10 tab-separated fields
# # text = Sag, Xaverle, hoscht ebbes oreachts verdwischt?
# 1	Sag	_	_	_	_	_	_	_	SpaceAfter=No
# 2	,	_	_	_	_	_	_	_	_
# 3	Xaverle	_	_	_	_	_	_	_	SpaceAfter=No
# 4	,	_	_	_	_	_	_	_	_
# 5	hoscht	_	_	_	_	_	_	_	_
# 6	ebbes	_	_	_	_	_	_	_	_
# 7	oreachts	_	_	_	_	_	_	_	_
# 8	verdwischt	_	_	_	_	_	_	_	SpaceAfter=No
# 9	?	_	_	_	_	_	_	_	_

# Sentences consist of one or more word lines, and word lines contain the following fields:

# ID: Word index, integer starting at 1 for each new sentence; may be a range for multiword tokens; may be a decimal number for empty nodes (decimal numbers can be lower than 1 but must be greater than 0).
# FORM: Word form or punctuation symbol.
# LEMMA: Lemma or stem of word form.
# UPOS: Universal part-of-speech tag.
# XPOS: Language-specific part-of-speech tag; underscore if not available.
# FEATS: List of morphological features from the universal feature inventory or from a defined language-specific extension; underscore if not available.
# HEAD: Head of the current word, which is either a value of ID or zero (0).
# DEPREL: Universal dependency relation to the HEAD (root iff HEAD = 0) or a defined language-specific subtype of one.
# DEPS: Enhanced dependency graph in the form of a list of head-deprel pairs.
# MISC: Any other annotation.

# Can export Lemma, pos, morph, SpaceAfter=No (token.whitespace_)
