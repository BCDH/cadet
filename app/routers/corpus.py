import srsly
from spacy.tokens import Doc
from spacy.lang.char_classes import HYPHENS, PUNCT, UNITS, CONCAT_QUOTES

import re
from pathlib import Path
from typing import List, Optional, Set
from fastapi import Request, Form, File, APIRouter, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from collections import Counter, namedtuple
from itertools import chain
from functools import lru_cache
import importlib
from ..util.manage_corpus import make_corpus
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])

Token = namedtuple("Token", ["text", "lemma_", "pos_", "ent_type_","is_stop"])

@router.get("/update_corpus")
async def update_corpus(background_tasks: BackgroundTasks):
    background_tasks.add_task(make_corpus)



###########
# Lemmata #
###########

@router.get("/update_lemma")
async def update_lemma(word:str,lemma:str):
    # load lemma file, needed because we update the file
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    if len(list(new_lang.iterdir())) > 0:
        lookups_path = new_lang / lang_name / "lookups"
        for lookup in lookups_path.iterdir():
            key = lookup.stem[lookup.stem.find('_') + 1:]
            if 'lemma' in key:
                lemma_file = lookup
                lemma_data = srsly.read_json(lookup)

    # remove any accidental spaces 
    word = word.strip()
    lemma = lemma.strip()
    lemma_data[word] = lemma
    srsly.write_json(lemma_file, lemma_data)

###########
# POS #
###########

@router.get("/update_pos")
async def update_pos(word:str,pos:str):
    # load lemma file, needed because we update the file
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    if len(list(new_lang.iterdir())) > 0:
        lookups_path = new_lang / lang_name / "lookups"
        for lookup in lookups_path.iterdir():
            key = lookup.stem[lookup.stem.find('_') + 1:]
            if 'pos' in key:
                pos_file = lookup
                pos_data = srsly.read_json(lookup)

    # remove any accidental spaces 
    word = word.strip()
    pos = pos.strip()
    pos_data[word] = pos
    srsly.write_json(pos_file, pos_data)

###########
# POS #
###########

@router.get("/update_features")
async def update_features(word:str,features:str):
    # load lemma file, needed because we update the file
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    if len(list(new_lang.iterdir())) > 0:
        lookups_path = new_lang / lang_name / "lookups"
        for lookup in lookups_path.iterdir():
            key = lookup.stem[lookup.stem.find('_') + 1:]
            if 'features' in key:
                features_file = lookup
                features_data = srsly.read_json(lookup)

    # remove any accidental spaces 
    word = word.strip()
    features = features.strip()
    features_data[word] = features
    srsly.write_json(features_file, features_data)

##############
# Stop words #
##############
def load_stopwords():
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / "stop_words.py"
        spec = importlib.util.spec_from_file_location("STOP_WORDS", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        STOP_WORDS = module.STOP_WORDS
        return STOP_WORDS


def is_stop(word:str, STOP_WORDS:Set):
    """JavaScript will interpret 'False' as a boolean, so I need to an alternative value"""
    if word in STOP_WORDS:
        return "☑"
    else: 
        return "☐"

@router.get("/add_stopword")
def add_stopword(word:str):
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / "stop_words.py"
        text = path.read_text()
        #Edit only the stopwords string, otherwise we could replace other sections of the file
        start = text.find('"""')
        end = text.find('""".split()')
        stopwords = text[start:end]
        if not word in stopwords:
            stopwords = stopwords + ' ' + word
            text = text[:start] + stopwords + text[end:]
            path.write_text(text)

@router.get("/delete_stopword")
def delete_stopword(word:str):
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        path = list(new_lang.iterdir())[0]
        path = path / "stop_words.py"
        text = path.read_text()
        #Edit only the stopwords string, otherwise we could replace other sections of the file
        start = text.find('"""')
        end = text.find('""".split()')
        stopwords = text[start:end]
        stopwords = re.sub(fr'\b{word}\b', '', stopwords)
        text = text[:start] + stopwords + text[end:]
        path.write_text(text)


###############
# Corpus Page #
###############

@lru_cache
def load_lookups():
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        lang_name = list(new_lang.iterdir())[0].name
        lookups_path = new_lang / lang_name / "lookups"
        for lookup in lookups_path.iterdir():
            key = lookup.stem[lookup.stem.find('_') + 1:]
            if 'lemma' in key:
                lemma_data = srsly.read_json(lookup)
            if 'features' in key:
                features_data = srsly.read_json(lookup)
            if 'pos' in key:
                pos_data = srsly.read_json(lookup)
        return lemma_data,features_data,pos_data


@router.get("/corpus")
async def read_items(request: Request):
    
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        lang_name = list(new_lang.iterdir())[0].name
        corpus_dir = new_lang / lang_name / "corpus_json"
        tokens_json = srsly.read_json((corpus_dir / 'tokens.json'))
        stats = srsly.read_json((corpus_dir / 'stats.json'))
        stats = srsly.json_loads(stats)
        return templates.TemplateResponse(
            "corpus.html",
            {"request": request, "stats": stats, "tokens_json": tokens_json},
        )
    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )

