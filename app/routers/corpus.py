import srsly
from spacy.tokens import Doc
from spacy.lang.char_classes import HYPHENS, PUNCT, UNITS, CONCAT_QUOTES

import re
from pathlib import Path
from typing import List, Optional, Set
from fastapi import Request, Form, File, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from collections import Counter, namedtuple
from itertools import chain
from functools import lru_cache
import importlib

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])

Token = namedtuple("Token", ["text", "lemma_", "pos_", "ent_type_","is_stop"])

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
async def update_lemma(word:str,pos:str):
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
            if 'entity' in key:
                ent_data = srsly.read_json(lookup)
            if 'pos' in key:
                pos_data = srsly.read_json(lookup)
        return lemma_data,ent_data,pos_data


@router.get("/corpus")
async def read_items(request: Request):
    
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        lemma_data,ent_data,pos_data = load_lookups()
        STOP_WORDS = load_stopwords()
        text_path = list(new_lang.iterdir())[0] / "texts"
        corpus = ""
        text_count = 0
        token_count = 0
        max_length = 0
        corpus = []
        tokens = []
    
        for text in text_path.iterdir():
            corpus.append(text.read_text())
            if len(text.read_text()) > max_length:
                max_length = len(text.read_text()) + 1
            text_count += 1
        # create doc from corpus with obj, count tokens
        lang_name = list(new_lang.iterdir())[0].name
        try:
            mod = __import__(f"new_lang.{lang_name}", fromlist=[lang_name.capitalize()])
        except SyntaxError:  # Unable to load __init__ due to syntax error
            # redirect /edit?file_name=examples.py
            message = "[*] SyntaxError, please correct this file to proceed."
            return RedirectResponse(url="/edit?file_name=tokenizer_exceptions.py")
        
        ignore = [
            "\n",
            " ",
            "\n\n",
            "\n     ",
            "\n\n\n\n",
        ] #TODO option in the UI to show/hide the following: 
        #    LIST_UNITS = split_chars(_units)
        #     LIST_CURRENCY = split_chars(_currency)
        #     LIST_QUOTES = split_chars(_quotes)
        #     LIST_PUNCT = split_chars(_punct)
        #     LIST_HYPHENS = split_chars(_hyphens)
        #     LIST_ELLIPSES = [r"\.\.+", "…"]
        #     LIST_ICONS = [r"[{i}]".format(i=_other_symbols)]
        
        
        cls = getattr(mod, lang_name.capitalize())
        nlp = cls()
        nlp.max_length = max_length
        for doc in nlp.pipe(corpus):
            token_count += len([t for t in doc])
        
        
            tokens.extend([
                Token(
                    text=t.text,
                    lemma_=lemma_data.get(t.text,''),
                    pos_=pos_data.get(t.text,''),
                    ent_type_= ent_data.get(t.text,''),
                    is_stop= is_stop(t.text, STOP_WORDS)
                )
                for t in doc
                if not t.text in ignore
            ])
        to_json = []
        counter = token_count
        rank = 1
        for i in Counter(tokens).most_common():
            dict_ = i[0]._asdict()
            dict_["count"] = i[1]
            counter = counter - i[1]
            dict_['rank'] = rank
            rank += 1
            dict_["remain"] = counter
            to_json.append(dict_)
        tokens_json = srsly.json_dumps(to_json)
        try:
            sent_count = len([s for s in doc.sents])
        except ValueError:
            sent_count = False
        ent_count = len([e for e in doc.ents])
        stats = {
            "texts": text_count,
            "tokens": token_count,
            "sents": sent_count,
            "ents": ent_count,
            "unique_tokens": len(set([t.text for t in tokens]))
        }
        return templates.TemplateResponse(
            "corpus.html",
            {"request": request, "stats": stats, "tokens_json": tokens_json},
        )
    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )

