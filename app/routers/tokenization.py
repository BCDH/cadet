import json 
import spacy
from pathlib import Path
from fastapi import APIRouter
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from app.util.create_object import create_object
from app.util.clone_object import clone_object
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/tokenization")
async def create(request: Request):
    examples = ['This is one', 'This is two.','This is three']
    return templates.TemplateResponse("tokenizer.html", {"request": request, "examples": examples })
