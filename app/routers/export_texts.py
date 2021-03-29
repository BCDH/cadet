import httpx
import textract
import srsly
from pathlib import Path
from typing import List, Optional

from fastapi import Request, Form, File, UploadFile, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from fastapi.responses import FileResponse

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/export-texts")
async def read_items(request: Request):
    return templates.TemplateResponse("export-texts.html", {"request": request})

@router.get("/download")
async def download():
    
    # # update the doc from seeds and lookups 
    #     #check if under updated seeds
    #     #elif in lookups 
    #     #else add to 
    # text = [a for a in texts if a['filename'] == filename][0]
    text = "hello!"
    temp_file = Path('/tmp/'+ "hello.txt")
    temp_file.write_text(text)
    return FileResponse(temp_file, media_type="text/plain", filename="hello.txt")