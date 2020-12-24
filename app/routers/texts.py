import httpx
import textract
import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/texts")
async def read_items(request: Request):
    return templates.TemplateResponse("texts.html", {"request": request})


@router.post("/texts")
async def save_texts(
    request: Request,
    text_url: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    text_area: Optional[str] = Form(None),
):

    save_path = Path.cwd() / "data" / "texts"
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
        data = [{"text": line} for line in text.split("\n")]
        file_save_path = str((save_path / f"{current_id()+1}_text.jsonl"))
        srsly.write_jsonl(file_save_path, data)

    if files:

        for file in files:
            # Write the UploadFile to disk, this is a trade-off required by textract
            p = Path("/tmp") / file.filename
            try:
                p.write_bytes(file.file.read())
                text = textract.process(str(p))
                text = text.decode("utf-8")
                data = [{"text": line} for line in text.split("\n")]
                file_save_path = str((save_path / f"{current_id()+1}_text.jsonl"))
                srsly.write_jsonl(file_save_path, data)
                p.unlink()

            except IsADirectoryError:
                pass  # No file selected
    if text_area:
        data = [{"text": line} for line in text_area.split("\n")]
        file_save_path = str((save_path / f"{current_id()+1}_text.jsonl"))
        srsly.write_jsonl(file_save_path, data)

    message = "Text added successfully"
    return templates.TemplateResponse(
        "texts.html", {"request": request, "message": message}
    )


@router.get("/texts/stats")
async def get_text_stats():
    pass
